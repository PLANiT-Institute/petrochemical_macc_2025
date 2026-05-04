"""
MODULE 3: COST OPTIMIZATION (VERSION 2 - CORRECTED)
Find least-cost technology deployment pathways

CRITICAL FIX:
- NCC-H2 and NCC-Electricity are now mutually exclusive
- A facility can choose H2 OR Electricity, never both
- Technology selection based on cost-effectiveness
- Once selected, irreversibility applies (capital lock-in)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from .utils import save_csv_output, save_plot, is_ncc_facility

class CostOptimizerV2:
    """Cost optimization under emission constraints (CORRECTED VERSION)

    Supports two types of constraints:
    1. Annual emission path: yearly targets from CSV
    2. Carbon budget: total cumulative emissions limit

    KEY CORRECTION:
    - NCC-H2 and NCC-Electricity are mutually exclusive alternatives
    - Model selects the cheaper option each year
    - Once selected, choice persists (irreversibility)
    """

    def __init__(self, baseline_output='outputs/module_01', macc_output='outputs/module_02',
                 output_dir='outputs/module_03', scenario_file='data/emission_scenarios_clean.csv',
                 force_ncc_technology=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.force_ncc_technology = force_ncc_technology  # 'NCC-H2', 'NCC-Electricity', or None

        print("="*80)
        print("MODULE 3: COST OPTIMIZATION")
        print("="*80)

        self.df_baseline = pd.read_csv(Path(baseline_output) / 'baseline_2025_detailed.csv')
        self.df_bau = pd.read_csv(Path(baseline_output) / 'bau_trajectory_2025_2050.csv')
        self.df_macc = pd.read_csv(Path(macc_output) / 'macc_annual_2025_2050.csv')

        # Load emission scenarios
        try:
            self.df_scenarios = pd.read_csv(scenario_file)
            print(f"\n📁 Loaded emission scenarios from: {scenario_file}")

            # Parse scenarios
            self.scenarios = self._parse_scenarios(self.df_scenarios)
            print(f"   ✓ Found {len(self.scenarios)} scenarios:")
            for name, config in self.scenarios.items():
                if config['type'] == 'annual_path':
                    print(f"      - {name}: Annual path (2025: {config['path'][2025]:.1f} Mt → 2050: {config['path'][2050]:.1f} Mt)")
                else:
                    print(f"      - {name}: Carbon budget ({config['budget']:.0f} MtCO2 total)")
        except FileNotFoundError:
            print(f"\n⚠️  Scenario file not found: {scenario_file}")
            print("   Using default Linear scenario")
            self.scenarios = {
                'Linear_Default': {'type': 'annual_path', 'path': self._create_linear_path(52, 2)}
            }

    def _parse_scenarios(self, df_scenarios):
        """Parse scenarios from CSV"""
        scenarios = {}

        for scenario_name in df_scenarios['scenario_name'].unique():
            df_sc = df_scenarios[df_scenarios['scenario_name'] == scenario_name]
            constraint_type = df_sc['constraint_type'].iloc[0]

            if constraint_type == 'annual_path':
                # Build year -> target dictionary
                path = {}
                for _, row in df_sc.iterrows():
                    if pd.notna(row['year']):
                        path[int(row['year'])] = row['target_mt']
                scenarios[scenario_name] = {'type': 'annual_path', 'path': path}

            elif constraint_type == 'carbon_budget':
                # Total cumulative budget
                budget = df_sc['target_mt'].iloc[0]
                scenarios[scenario_name] = {'type': 'carbon_budget', 'budget': budget}

        return scenarios

    def _create_linear_path(self, start, end):
        """Create linear emission path"""
        path = {}
        for year in range(2025, 2051):
            progress = (year - 2025) / 25
            path[year] = start + (end - start) * progress
        return path

    def optimize_scenario(self, scenario_name):
        """Optimize for a scenario"""
        print(f"\n�� Optimizing: {scenario_name}")

        scenario_config = self.scenarios[scenario_name]
        years = range(2025, 2051)

        if scenario_config['type'] == 'annual_path':
            return self._optimize_annual_path(scenario_name, scenario_config['path'])
        elif scenario_config['type'] == 'carbon_budget':
            return self._optimize_carbon_budget(scenario_name, scenario_config['budget'])

    def _optimize_annual_path(self, scenario_name, emission_path):
        """Optimize with annual emission targets

        KEY CONSTRAINT: Technology irreversibility
        - Once a technology is deployed, it cannot be reversed
        - Each year's deployment must be >= previous year's deployment
        - This prevents the emission trajectory from oscillating

        CRITICAL FIX:
        - NCC-H2 and NCC-Electricity are mutually exclusive
        - Model selects the cheaper option
        - Once selected, choice persists (irreversibility + capital lock-in)
        """
        years = range(2025, 2051)
        deployment = []

        # Track cumulative investment
        cumulative_capex_musd = 0

        # Track deployed capacity (irreversible - can only increase)
        deployed_capacity = {'Heat_Pump': 0, 'NCC-H2': 0, 'NCC-Electricity': 0, 'RE_PPA': 0, 'RDH': 0}

        # NEW: Track NCC technology choice (mutually exclusive)
        # Once chosen (H2 or Electricity), this persists for all future years
        # Can be forced via initialization parameter (for scenario analysis)
        ncc_choice = self.force_ncc_technology  # 'NCC-H2', 'NCC-Electricity', or None for auto-select

        if ncc_choice:
            print(f"   🔒 NCC Technology FORCED: {ncc_choice}")

        # Interpolate missing years in emission path
        years_with_targets = sorted([y for y in emission_path.keys()])
        interpolated_path = {}
        for year in years:
            if year in emission_path:
                interpolated_path[year] = emission_path[year]
            else:
                # Linear interpolation
                # Find surrounding years
                before = [y for y in years_with_targets if y < year]
                after = [y for y in years_with_targets if y > year]

                if before and after:
                    y1 = before[-1]
                    y2 = after[0]
                    t1 = emission_path[y1]
                    t2 = emission_path[y2]
                    # Linear interpolation
                    interpolated_path[year] = t1 + (t2 - t1) * (year - y1) / (y2 - y1)
                elif after:
                    # Before first target, use first target
                    interpolated_path[year] = emission_path[after[0]]
                elif before:
                    # After last target, use last target
                    interpolated_path[year] = emission_path[before[-1]]
                else:
                    # No targets at all, use BAU
                    bau = self.df_bau[self.df_bau['year'] == year]['total_emissions_mt'].iloc[0]
                    interpolated_path[year] = bau

        # Enforce non-increasing emission targets to prohibit rebounds
        previous_target = None
        for year in years:
            if previous_target is not None:
                interpolated_path[year] = min(interpolated_path[year], previous_target)
            previous_target = interpolated_path[year]

        for year in years:
            bau = self.df_bau[self.df_bau['year'] == year]['total_emissions_mt'].iloc[0]
            target = interpolated_path[year]
            required = max(0, bau - target)

            # Get available technologies sorted by cost
            tech_year_all = self.df_macc[
                (self.df_macc['year'] == year) & (self.df_macc['available'] == True)
            ].sort_values('total_cost_usd_per_tco2')

            # CRITICAL FIX: Determine NCC technology choice (mutually exclusive)
            if ncc_choice is None:
                # First time deploying NCC technology - choose cheaper option
                ncc_h2 = tech_year_all[tech_year_all['technology'] == 'NCC-H2']
                ncc_elec = tech_year_all[tech_year_all['technology'] == 'NCC-Electricity']

                if not ncc_h2.empty and not ncc_elec.empty:
                    # Both available - choose cheaper
                    h2_cost = ncc_h2.iloc[0]['total_cost_usd_per_tco2']
                    elec_cost = ncc_elec.iloc[0]['total_cost_usd_per_tco2']
                    ncc_choice = 'NCC-H2' if h2_cost < elec_cost else 'NCC-Electricity'
                    print(f"   Year {year}: Selecting {ncc_choice} (${h2_cost:.0f} vs ${elec_cost:.0f} per tCO2)")
                elif not ncc_h2.empty:
                    ncc_choice = 'NCC-H2'
                    print(f"   Year {year}: Selecting NCC-H2 (only option available)")
                elif not ncc_elec.empty:
                    ncc_choice = 'NCC-Electricity'
                    print(f"   Year {year}: Selecting NCC-Electricity (only option available)")

            # Filter technologies: exclude non-selected NCC option
            tech_year = tech_year_all[
                ~((tech_year_all['technology'].isin(['NCC-H2', 'NCC-Electricity'])) &
                  (tech_year_all['technology'] != ncc_choice))
            ].copy()

            # Deploy technologies in cost order
            # Start from previous year's deployment (irreversibility)
            deployed = deployed_capacity.copy()
            remaining = max(0, required - sum(deployed.values()))

            for _, tech in tech_year.iterrows():
                if remaining <= 0:
                    break
                # Can only ADD capacity, not remove
                additional_deploy = min(remaining, tech['abatement_potential_mtco2'] - deployed[tech['technology']])
                if additional_deploy > 0:
                    # Calculate CAPEX for NEW deployment only
                    capex_per_tco2 = tech['capex_ann_usd_per_tco2']  # Annualized CAPEX
                    # Convert to total CAPEX: multiply by lifetime (assume 20 years)
                    lifetime = 20
                    total_capex_usd = additional_deploy * 1e6 * capex_per_tco2 * lifetime  # MtCO2 * tCO2/Mt * USD/tCO2 * years
                    cumulative_capex_musd += total_capex_usd / 1e6  # Convert to million USD

                    deployed[tech['technology']] += additional_deploy
                    remaining -= additional_deploy

            # Update capacity tracker for next year
            deployed_capacity = deployed.copy()

            # Calculate H2 consumption for NCC-H2 deployment
            # Get H2 consumption from MACC data for current year
            macc_year = self.df_macc[self.df_macc['year'] == year]
            try:
                macc_ncc_h2 = macc_year[macc_year['technology'] == 'NCC-H2'].iloc[0]
                # H2 consumption per ton ethylene from MACC data
                h2_ton_per_ton_ethylene = macc_ncc_h2['h2_consumption_ton_per_ton_ethylene']
                baseline_tco2_per_ton_ethylene = macc_ncc_h2['baseline_combustion_emissions_tco2_per_ton']
            except (IndexError, KeyError):
                # 2024-12-08: Fallback if MACC data missing for specific year
                h2_ton_per_ton_ethylene = 0.2 # Default assumption
                baseline_tco2_per_ton_ethylene = 1.9 # Default assumption
                if deployed['NCC-H2'] > 0:
                     print(f"   ⚠️  Warning: Missing NCC-H2 MACC data for {year}, using defaults")

            # Convert: deployed MtCO2 → Mt ethylene → kt H2
            # 1 MtCO2 abated = (1e6 tCO2) / (baseline_tco2_per_ton_ethylene) = tons ethylene
            # tons ethylene * h2_ton_per_ton_ethylene = tons H2 → / 1000 = kt H2
            h2_consumption_kt = deployed['NCC-H2'] * (1e6 / baseline_tco2_per_ton_ethylene) * h2_ton_per_ton_ethylene / 1000  # kt H2

            # Calculate electricity consumption increase
            # NCC-Electricity: ~10 MWh per ton ethylene (from literature)
            # Heat Pump: Displaces naphtha with electricity at COP=4, so 1/4 of heat energy as electricity
            # RE_PPA: No additional consumption, just switches source

            # For NCC-Electricity: assume 1.9 tCO2/ton ethylene baseline emission
            # So each MtCO2 abated = ~0.53 Mt ethylene produced
            # At 10 MWh/ton ethylene = 5.3 TWh per MtCO2 abated
            mwh_per_tco2_ncc_elec = 5300  # MWh per tCO2 abated

            # For Heat Pump: Replace 1 GJ thermal with 0.25 GJ electricity (COP=4)
            # 1 tCO2 from naphtha = 67 GJ thermal = 16.75 GJ electricity = 4.65 MWh
            mwh_per_tco2_heat_pump = 4.65  # MWh per tCO2 abated

            # deployed is in MtCO2, convert to tCO2 (*1e6), then MWh to TWh (/1e6) = no conversion needed
            electricity_consumption_increase_twh = (
                deployed['NCC-Electricity'] * mwh_per_tco2_ncc_elec / 1e3 +  # MtCO2 * MWh/tCO2 / 1000 = TWh
                deployed['Heat_Pump'] * mwh_per_tco2_heat_pump / 1e3  # MtCO2 * MWh/tCO2 / 1000 = TWh
            )

            deployment.append({
                'year': year,
                'target_mt': target,
                'bau_mt': bau,
                'heat_pump_mt': deployed['Heat_Pump'],
                'ncc_h2_mt': deployed['NCC-H2'],
                'ncc_elec_mt': deployed['NCC-Electricity'],
                're_ppa_mt': deployed['RE_PPA'],
                'rdh_mt': deployed['RDH'],  # RDH for BTX facilities
                'h2_consumption_kt': h2_consumption_kt,
                'electricity_consumption_increase_twh': electricity_consumption_increase_twh,
                'total_deployed_mt': sum(deployed.values()),
                'actual_emissions_mt': bau - sum(deployed.values()),
                'shortfall_mt': max(0, bau - sum(deployed.values()) - target),
                'cumulative_capex_musd': cumulative_capex_musd,
            })

        return pd.DataFrame(deployment)

    def _optimize_carbon_budget(self, scenario_name, total_budget):
        """Optimize with total carbon budget constraint

        This uses a simple greedy approach:
        1. Deploy cheapest technologies first across all years
        2. Continue until cumulative emissions = budget
        3. Technology irreversibility: once deployed, cannot be reversed
        """
        years = range(2025, 2051)
        print(f"   Total carbon budget: {total_budget:.0f} MtCO2 (2025-2050)")

        # Calculate BAU cumulative
        bau_cumulative = self.df_bau['total_emissions_mt'].sum()
        print(f"   BAU cumulative: {bau_cumulative:.0f} MtCO2")
        print(f"   Required reduction: {bau_cumulative - total_budget:.0f} MtCO2")

        # Build cost-effectiveness ranking across all years
        tech_options = []
        for year in years:
            bau = self.df_bau[self.df_bau['year'] == year]['total_emissions_mt'].iloc[0]
            tech_year = self.df_macc[
                (self.df_macc['year'] == year) & (self.df_macc['available'] == True)
            ]
            for _, tech in tech_year.iterrows():
                tech_options.append({
                    'year': year,
                    'technology': tech['technology'],
                    'cost': tech['total_cost_usd_per_tco2'],
                    'potential': tech['abatement_potential_mtco2'],
                    'capex_ann_usd_per_tco2': tech['capex_ann_usd_per_tco2'],
                })

        # Sort by cost
        tech_options_df = pd.DataFrame(tech_options).sort_values('cost')

        # Deploy technologies until budget constraint met
        # NEW: Track deployed capacity (irreversible)
        deployed_capacity = {'Heat_Pump': 0, 'NCC-H2': 0, 'NCC-Electricity': 0, 'RE_PPA': 0, 'RDH': 0}
        deployment_dict = {year: {'Heat_Pump': 0, 'NCC-H2': 0, 'NCC-Electricity': 0, 'RE_PPA': 0, 'RDH': 0}
                          for year in years}

        cumulative = 0
        bau_cumulative_so_far = 0
        cumulative_capex_musd = 0

        for year in years:
            bau = self.df_bau[self.df_bau['year'] == year]['total_emissions_mt'].iloc[0]
            bau_cumulative_so_far += bau

            # Start from previous year's deployment (irreversibility)
            deployment_dict[year] = deployed_capacity.copy()

            # How much room left in budget?
            budget_remaining = total_budget - cumulative
            required_this_year = max(0, bau - sum(deployment_dict[year].values()))

            # Deploy technologies for this year
            for _, tech in tech_options_df[tech_options_df['year'] == year].iterrows():
                if cumulative >= total_budget:
                    break
                # Can only ADD capacity
                current_deploy = deployment_dict[year][tech['technology']]
                max_additional = min(tech['potential'] - current_deploy, required_this_year)

                if max_additional > 0:
                    # Calculate CAPEX for new deployment
                    lifetime = 20
                    total_capex_usd = max_additional * 1e6 * tech['capex_ann_usd_per_tco2'] * lifetime
                    cumulative_capex_musd += total_capex_usd / 1e6

                    deployment_dict[year][tech['technology']] += max_additional
                    required_this_year -= max_additional

            # Update capacity tracker for next year
            deployed_capacity = deployment_dict[year].copy()

            actual_emission = bau - sum(deployment_dict[year].values())
            cumulative += actual_emission

        # Convert to dataframe
        deployment = []
        cumulative = 0
        cumulative_capex_calc = 0  # Recalculate for consistency
        prev_deployment = {'Heat_Pump': 0, 'NCC-H2': 0, 'NCC-Electricity': 0, 'RE_PPA': 0, 'RDH': 0}

        for year in years:
            bau = self.df_bau[self.df_bau['year'] == year]['total_emissions_mt'].iloc[0]
            actual = bau - sum(deployment_dict[year].values())
            cumulative += actual

            # Calculate CAPEX for new deployment this year
            tech_year = self.df_macc[(self.df_macc['year'] == year) & (self.df_macc['available'] == True)]
            for tech_name in ['Heat_Pump', 'NCC-H2', 'NCC-Electricity', 'RE_PPA', 'RDH']:
                new_capacity = deployment_dict[year][tech_name] - prev_deployment[tech_name]
                if new_capacity > 0:
                    tech_data = tech_year[tech_year['technology'] == tech_name]
                    if not tech_data.empty:
                        capex_ann = tech_data.iloc[0]['capex_ann_usd_per_tco2']
                        lifetime = 20
                        cumulative_capex_calc += new_capacity * 1e6 * capex_ann * lifetime / 1e6

            # Calculate H2 consumption from MACC data
            macc_year = self.df_macc[self.df_macc['year'] == year]
            try:
                macc_ncc_h2 = macc_year[macc_year['technology'] == 'NCC-H2'].iloc[0]
                h2_ton_per_ton_ethylene = macc_ncc_h2['h2_consumption_ton_per_ton_ethylene']
                baseline_tco2_per_ton_ethylene = macc_ncc_h2['baseline_combustion_emissions_tco2_per_ton']
            except (IndexError, KeyError):
                h2_ton_per_ton_ethylene = 0.2
                baseline_tco2_per_ton_ethylene = 1.9
                if deployment_dict[year]['NCC-H2'] > 0:
                     print(f"   ⚠️  Warning: Missing NCC-H2 MACC data for {year}, using defaults")
            h2_consumption_kt = deployment_dict[year]['NCC-H2'] * (1e6 / baseline_tco2_per_ton_ethylene) * h2_ton_per_ton_ethylene / 1000

            # Calculate electricity consumption increase
            mwh_per_tco2_ncc_elec = 5300
            mwh_per_tco2_heat_pump = 4.65
            electricity_consumption_increase_twh = (
                deployment_dict[year]['NCC-Electricity'] * mwh_per_tco2_ncc_elec / 1e3 +  # MtCO2 * MWh/tCO2 / 1000 = TWh
                deployment_dict[year]['Heat_Pump'] * mwh_per_tco2_heat_pump / 1e3  # MtCO2 * MWh/tCO2 / 1000 = TWh
            )

            deployment.append({
                'year': year,
                'target_mt': None,  # No annual target, only budget
                'bau_mt': bau,
                'heat_pump_mt': deployment_dict[year]['Heat_Pump'],
                'ncc_h2_mt': deployment_dict[year]['NCC-H2'],
                'ncc_elec_mt': deployment_dict[year]['NCC-Electricity'],
                're_ppa_mt': deployment_dict[year]['RE_PPA'],
                'rdh_mt': deployment_dict[year]['RDH'],  # RDH for BTX facilities
                'h2_consumption_kt': h2_consumption_kt,
                'electricity_consumption_increase_twh': electricity_consumption_increase_twh,
                'total_deployed_mt': sum(deployment_dict[year].values()),
                'actual_emissions_mt': actual,
                'cumulative_emissions_mt': cumulative,
                'budget_remaining_mt': total_budget - cumulative,
                'cumulative_capex_musd': cumulative_capex_calc,
            })

            prev_deployment = deployment_dict[year].copy()

        print(f"   Final cumulative: {cumulative:.0f} MtCO2")
        print(f"   Budget compliance: {(cumulative/total_budget)*100:.1f}%")

        return pd.DataFrame(deployment)

    def create_visualizations(self, results):
        """Create visualizations"""
        print("\n🎨 Creating visualizations...")

        for scenario, df in results.items():
            # Deployment stack plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

            # Top: Technology deployment (include RDH if present)
            rdh_data = df['rdh_mt'] if 'rdh_mt' in df.columns else [0] * len(df)
            ax1.stackplot(df['year'], df['heat_pump_mt'], df['ncc_h2_mt'], df['ncc_elec_mt'], df['re_ppa_mt'], rdh_data,
                        labels=['Heat Pump', 'NCC-H2', 'NCC-Electricity', 'RE PPA', 'RDH'],
                        colors=['#2ECC71', '#3498DB', '#E74C3C', '#F39C12', '#9B59B6'], alpha=0.8)
            ax1.set_ylabel('Abatement (MtCO2/year)', fontweight='bold')
            ax1.set_title(f'Technology Deployment: {scenario}', fontweight='bold', fontsize=14)
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3)

            # Bottom: Emissions trajectory
            ax2.plot(df['year'], df['bau_mt'], label='BAU', color='gray', linestyle='--', linewidth=2)
            ax2.plot(df['year'], df['actual_emissions_mt'], label='Actual with deployment',
                    color='green', linewidth=2.5)
            if 'target_mt' in df.columns and df['target_mt'].notna().any():
                ax2.plot(df['year'], df['target_mt'], label='Target', color='red',
                        linestyle=':', linewidth=2)
            ax2.set_xlabel('Year', fontweight='bold')
            ax2.set_ylabel('Emissions (MtCO2/year)', fontweight='bold')
            ax2.set_title('Emission Trajectory', fontweight='bold')
            ax2.legend(loc='upper right')
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            save_plot(fig, self.output_dir / f'deployment_{scenario.lower().replace(" ", "_")}.png')

            # For carbon budget scenarios, create cumulative plot
            if 'cumulative_emissions_mt' in df.columns:
                fig, ax = plt.subplots(figsize=(14, 8))
                ax.plot(df['year'], df['cumulative_emissions_mt'], linewidth=2.5, color='navy')
                if 'budget_remaining_mt' in df.columns:
                    budget_total = df['cumulative_emissions_mt'].iloc[-1] + df['budget_remaining_mt'].iloc[-1]
                    ax.axhline(budget_total, color='red', linestyle='--', linewidth=2,
                             label=f'Budget: {budget_total:.0f} MtCO2')
                ax.set_xlabel('Year', fontweight='bold')
                ax.set_ylabel('Cumulative Emissions (MtCO2)', fontweight='bold')
                ax.set_title(f'Carbon Budget Compliance: {scenario}', fontweight='bold', fontsize=14)
                ax.legend()
                ax.grid(True, alpha=0.3)
                save_plot(fig, self.output_dir / f'budget_{scenario.lower().replace(" ", "_")}.png')

    def create_facility_level_allocation(self, scenario_name, deployment_df):
        """
        Allocate technologies to specific facilities (CORRECTED VERSION)

        Shows which of the 248 facilities get which technology mix

        CRITICAL FIX:
        - NCC-H2 and NCC-Electricity are mutually exclusive
        - Only ONE of them can be allocated to NCC facilities
        - This prevents >100% abatement and negative emissions
        """
        print(f"\n📍 Creating facility-level allocation for {scenario_name}...")

        # Get 2050 deployment (final state)
        deploy_2050 = deployment_df[deployment_df['year'] == 2050].iloc[0]

        # Load baseline facility data
        df_facilities = self.df_baseline.copy()

        # Initialize technology allocation columns
        df_facilities['tech_heat_pump_pct'] = 0.0
        df_facilities['tech_ncc_h2_pct'] = 0.0
        df_facilities['tech_ncc_elec_pct'] = 0.0
        df_facilities['tech_re_ppa_pct'] = 0.0
        df_facilities['abatement_mt'] = 0.0

        # Identify NCC facilities
        from .utils import is_ncc_facility
        df_facilities['is_ncc'] = df_facilities['product'].apply(is_ncc_facility)

        # Allocate Heat Pump (NON-NCC facilities only, proportional to ALL fossil fuel emissions)
        if deploy_2050['heat_pump_mt'] > 0:
            # Heat pump applies to NON-NCC facilities, replaces ALL fossil fuels (not just naphtha)
            # Calculate total fossil fuel emissions for non-NCC facilities
            df_facilities['fossil_fuel_emissions_kt'] = (
                df_facilities['emissions_naphtha_kt'] +
                df_facilities['emissions_lng_kt'] +
                df_facilities['emissions_fuel_gas_kt'] +
                df_facilities['emissions_lpg_kt'] +
                df_facilities['emissions_fuel_oil_kt'] +
                df_facilities['emissions_diesel_kt']
            )

            non_ncc_fossil_emissions = df_facilities[~df_facilities['is_ncc']]['fossil_fuel_emissions_kt'].sum() / 1000

            if non_ncc_fossil_emissions > 0:
                # Allocate proportionally to non-NCC fossil fuel emissions
                df_facilities['hp_abatement_mt'] = 0.0
                df_facilities.loc[~df_facilities['is_ncc'], 'hp_abatement_mt'] = (
                    df_facilities.loc[~df_facilities['is_ncc'], 'fossil_fuel_emissions_kt'] / 1000 /
                    non_ncc_fossil_emissions * deploy_2050['heat_pump_mt']
                )
                # Calculate percentage (based on fossil fuels, not total emissions)
                df_facilities['tech_heat_pump_pct'] = 0.0
                mask = (df_facilities['fossil_fuel_emissions_kt'] > 0) & (~df_facilities['is_ncc'])
                df_facilities.loc[mask, 'tech_heat_pump_pct'] = (
                    df_facilities.loc[mask, 'hp_abatement_mt'] / (df_facilities.loc[mask, 'fossil_fuel_emissions_kt'] / 1000) * 100
                )
                df_facilities['abatement_mt'] += df_facilities['hp_abatement_mt']

        # CRITICAL: Allocate ONLY ONE NCC technology (mutually exclusive)
        # Determine which NCC technology was deployed
        ncc_deployed = None
        if deploy_2050['ncc_h2_mt'] > 0:
            ncc_deployed = 'NCC-H2'
        elif deploy_2050['ncc_elec_mt'] > 0:
            ncc_deployed = 'NCC-Electricity'

        if ncc_deployed == 'NCC-H2':
            # Allocate NCC-H2 to NCC facilities only
            ncc_emissions = df_facilities[df_facilities['is_ncc']]['emissions_naphtha_kt'].sum() / 1000

            if ncc_emissions > 0:
                df_facilities['ncc_h2_abatement_mt'] = 0.0
                df_facilities.loc[df_facilities['is_ncc'], 'ncc_h2_abatement_mt'] = (
                    df_facilities.loc[df_facilities['is_ncc'], 'emissions_naphtha_kt'] / 1000 /
                    ncc_emissions * deploy_2050['ncc_h2_mt']
                )
                # Calculate percentage
                mask = (df_facilities['emissions_naphtha_kt'] > 0) & (df_facilities['is_ncc'])
                df_facilities.loc[mask, 'tech_ncc_h2_pct'] = (
                    df_facilities.loc[mask, 'ncc_h2_abatement_mt'] / (df_facilities.loc[mask, 'emissions_naphtha_kt'] / 1000) * 100
                )
                df_facilities['abatement_mt'] += df_facilities['ncc_h2_abatement_mt']
                print(f"   Allocated NCC-H2: {deploy_2050['ncc_h2_mt']:.2f} Mt to NCC facilities")

        elif ncc_deployed == 'NCC-Electricity':
            # Allocate NCC-Electricity to NCC facilities only
            ncc_emissions = df_facilities[df_facilities['is_ncc']]['emissions_naphtha_kt'].sum() / 1000

            if ncc_emissions > 0:
                df_facilities['ncc_elec_abatement_mt'] = 0.0
                df_facilities.loc[df_facilities['is_ncc'], 'ncc_elec_abatement_mt'] = (
                    df_facilities.loc[df_facilities['is_ncc'], 'emissions_naphtha_kt'] / 1000 /
                    ncc_emissions * deploy_2050['ncc_elec_mt']
                )
                # Calculate percentage
                mask = (df_facilities['emissions_naphtha_kt'] > 0) & (df_facilities['is_ncc'])
                df_facilities.loc[mask, 'tech_ncc_elec_pct'] = (
                    df_facilities.loc[mask, 'ncc_elec_abatement_mt'] / (df_facilities.loc[mask, 'emissions_naphtha_kt'] / 1000) * 100
                )
                df_facilities['abatement_mt'] += df_facilities['ncc_elec_abatement_mt']
                print(f"   Allocated NCC-Electricity: {deploy_2050['ncc_elec_mt']:.2f} Mt to NCC facilities")

        # Allocate Renewable Electricity (all facilities EXCEPT those with NCC-Electricity)
        # CRITICAL FIX: NCC-Electricity already uses 100% RE, so exclude those facilities
        if deploy_2050['re_ppa_mt'] > 0:
            # Determine which facilities are eligible for RE
            # If NCC-Electricity is deployed, exclude NCC facilities (they already use RE)
            # Otherwise, all facilities with electricity consumption can switch to RE

            if ncc_deployed == 'NCC-Electricity':
                # Exclude NCC facilities (they already use 100% RE via NCC-Electricity)
                re_eligible = ~df_facilities['is_ncc']
                print(f"   RE allocation: Excluding NCC facilities (already using RE via NCC-Electricity)")
            else:
                # All facilities can switch grid electricity to RE
                re_eligible = df_facilities['emissions_electricity_kt'] > 0
                print(f"   RE allocation: All facilities with electricity consumption")

            # Calculate total eligible electricity emissions
            eligible_elec_emissions = df_facilities[re_eligible]['emissions_electricity_kt'].sum() / 1000

            if eligible_elec_emissions > 0:
                df_facilities['re_ppa_abatement_mt'] = 0.0
                df_facilities.loc[re_eligible, 're_ppa_abatement_mt'] = (
                    df_facilities.loc[re_eligible, 'emissions_electricity_kt'] / 1000 / eligible_elec_emissions * deploy_2050['re_ppa_mt']
                )
                df_facilities['tech_re_ppa_pct'] = (
                    df_facilities['re_ppa_abatement_mt'] / (df_facilities['emissions_electricity_kt'] / 1000) * 100
                ).fillna(0)
                df_facilities['abatement_mt'] += df_facilities['re_ppa_abatement_mt']
                print(f"   Allocated Renewable Electricity: {deploy_2050['re_ppa_mt']:.2f} Mt to {re_eligible.sum()} eligible facilities")

        # Add facility ID
        df_facilities['facility_id'] = range(1, len(df_facilities) + 1)

        # Select relevant columns
        output_cols = [
            'facility_id', 'company', 'location', 'product', 'process',
            'total_emissions_kt', 'tech_heat_pump_pct', 'tech_ncc_h2_pct',
            'tech_ncc_elec_pct', 'tech_re_ppa_pct', 'abatement_mt'
        ]

        df_allocation = df_facilities[output_cols].copy()
        df_allocation['emissions_2050_kt'] = (
            df_allocation['total_emissions_kt'] - df_allocation['abatement_mt'] * 1000
        )

        # VALIDATION: Check for negative emissions or >100% abatement
        negative_emissions = df_allocation[df_allocation['emissions_2050_kt'] < 0]
        if len(negative_emissions) > 0:
            print(f"   ⚠️  WARNING: {len(negative_emissions)} facilities have NEGATIVE emissions!")
            print(f"   This indicates double-counting error in allocation logic.")
            # Clip to zero
            df_allocation.loc[df_allocation['emissions_2050_kt'] < 0, 'emissions_2050_kt'] = 0

        # Calculate total abatement percentage
        total_baseline = df_allocation['total_emissions_kt'].sum()
        total_abatement = df_allocation['abatement_mt'].sum() * 1000
        abatement_pct = (total_abatement / total_baseline) * 100

        print(f"   ✓ Allocated technologies to {len(df_allocation)} facilities")
        print(f"   ✓ {(df_allocation['abatement_mt'] > 0).sum()} facilities have technology deployment")
        print(f"   ✓ Total abatement: {df_allocation['abatement_mt'].sum():.2f} Mt ({abatement_pct:.1f}% of baseline)")
        print(f"   ✓ Final emissions: {df_allocation['emissions_2050_kt'].sum():.0f} kt")

        # Save output
        filename = f'{scenario_name.lower()}_facility_allocation_2050.csv'
        save_csv_output(df_allocation, self.output_dir / filename)

        return df_allocation

    def run_complete_analysis(self):
        """Run complete optimization"""
        print("\n" + "="*80)
        print("RUNNING COST OPTIMIZATION")
        print("="*80)

        results = {}
        for scenario in self.scenarios:
            df = self.optimize_scenario(scenario)
            results[scenario] = df
            filename = scenario.lower().replace(' ', '_').replace('-', '_')
            save_csv_output(df, self.output_dir / f'{filename}_deployment.csv')

        self.create_visualizations(results)

        # Create comparison summary
        self._create_scenario_comparison(results)

        # Create facility-level allocations for each scenario
        print("\n📍 Creating facility-level technology allocations...")
        for scenario_name, deployment_df in results.items():
            self.create_facility_level_allocation(scenario_name, deployment_df)

        # Create regional energy transition analysis
        print("\n📍 Creating regional energy transition analysis...")
        self._create_regional_analysis(results)

        print("\n✓ MODULE 3 COMPLETE")
        print(f"Outputs saved to: {self.output_dir}")
        return results

    def _create_scenario_comparison(self, results):
        """Create scenario comparison summary"""
        comparison = []

        for scenario_name, df in results.items():
            if 'cumulative_emissions_mt' in df.columns:
                cumulative_2050 = df.iloc[-1]['cumulative_emissions_mt']
            else:
                cumulative_2050 = df['actual_emissions_mt'].sum()

            comparison.append({
                'scenario': scenario_name,
                'emissions_2030_mt': df[df['year'] == 2030]['actual_emissions_mt'].iloc[0],
                'emissions_2050_mt': df[df['year'] == 2050]['actual_emissions_mt'].iloc[0],
                'cumulative_2025_2050_mt': cumulative_2050,
                'total_heat_pump_2050_mt': df[df['year'] == 2050]['heat_pump_mt'].iloc[0],
                'total_ncc_h2_2050_mt': df[df['year'] == 2050]['ncc_h2_mt'].iloc[0],
                'total_ncc_elec_2050_mt': df[df['year'] == 2050]['ncc_elec_mt'].iloc[0],
                'total_re_ppa_2050_mt': df[df['year'] == 2050]['re_ppa_mt'].iloc[0],
                'reduction_2030_pct': ((52 - df[df['year'] == 2030]['actual_emissions_mt'].iloc[0]) / 52) * 100,
                'reduction_2050_pct': ((52 - df[df['year'] == 2050]['actual_emissions_mt'].iloc[0]) / 52) * 100,
            })

        df_comparison = pd.DataFrame(comparison)
        save_csv_output(df_comparison, self.output_dir / 'scenario_comparison.csv')

    def _create_regional_analysis(self, results):
        """Create regional energy transition analysis for all scenarios"""
        try:
            from .regional_energy_tracker import RegionalEnergyTracker

            tracker = RegionalEnergyTracker(
                baseline_dir='data',
                output_dir=self.output_dir / 'regional_analysis'
            )

            # Create baseline regional summary
            regional_baseline = tracker.create_regional_baseline()
            save_csv_output(regional_baseline, self.output_dir / 'regional_baseline.csv',
                           "Baseline emissions and energy by region")
        except (ImportError, ModuleNotFoundError):
            print("   (skipping regional analysis - regional_energy_tracker not available)")
            return

        # For each scenario, create regional deployment tracking
        for scenario_name, df_deployment in results.items():
            print(f"   - Analyzing {scenario_name} regional deployment...")

            # Extract technology deployment by reading facility allocation
            try:
                df_facility = pd.read_csv(
                    self.output_dir / f'{scenario_name.lower()}_facility_allocation_2050.csv'
                )

                # Aggregate by region
                df_regional = self._aggregate_regional_deployment(df_facility, tracker)

                # Save regional deployment
                save_csv_output(
                    df_regional,
                    self.output_dir / f'{scenario_name}_regional_deployment.csv',
                    f"Regional technology deployment for {scenario_name}"
                )

                # Skip energy consumption change (complex time-series analysis)
                # For now, just save regional deployment summary
                pass

            except FileNotFoundError:
                print(f"   ⚠️ Facility allocation not found for {scenario_name}")
                continue

        print("   ✓ Regional analysis complete")

    def _aggregate_regional_deployment(self, df_facility, tracker):
        """Aggregate facility-level deployment to regional level (2050 snapshot)"""

        # df_facility already has location column
        df = df_facility.copy()

        # Aggregate by location
        regional_summary = []

        for location in df['location'].unique():
            df_region = df[df['location'] == location]

            summary = {
                'location': location,
                'year': 2050,  # Snapshot year
                'num_facilities': len(df_region),
                'total_baseline_emissions_kt': df_region['total_emissions_kt'].sum(),
                'total_abatement_mt': df_region['abatement_mt'].sum(),
                'total_emissions_2050_kt': df_region['emissions_2050_kt'].sum(),
            }

            # Add technology penetration rates
            tech_cols = [c for c in df.columns if c.startswith('tech_') and c.endswith('_pct')]
            for col in tech_cols:
                tech_name = col.replace('tech_', '').replace('_pct', '')
                # Average penetration rate across facilities
                summary[f'{tech_name}_avg_pct'] = df_region[col].mean()
                # Number of facilities using this tech
                summary[f'{tech_name}_num_facilities'] = (df_region[col] > 0).sum()

            regional_summary.append(summary)

        return pd.DataFrame(regional_summary)

    def create_annual_regional_analysis(self, scenario_name, deployment_df):
        """
        Create annual regional analysis for Cost and Electricity (NEW REQUIREMENT)
        Iterates 2025-2050 to allocate technologies to facilities each year
        and aggregates by location.
        """
        print(f"\\n📍 Creating annual regional analysis for {scenario_name}...")
        
        regional_results = []
        years = range(2025, 2051)
        
        # Pre-calculate non-NCC fossil emissions for weighting heat pump
        df_facilities = self.df_baseline.copy()
        
        # Identify NCC facilities
        df_facilities['is_ncc'] = df_facilities['product'].apply(is_ncc_facility)
        
        # Generate facility_id if missing
        if 'facility_id' not in df_facilities.columns:
            df_facilities['facility_id'] = df_facilities.index
            
        df_facilities['fossil_fuel_emissions_kt'] = (
            df_facilities['emissions_naphtha_kt'] +
            df_facilities['emissions_lng_kt'] +
            df_facilities['emissions_fuel_gas_kt'] + 
            df_facilities['emissions_lpg_kt'] +
            df_facilities['emissions_fuel_oil_kt'] +
            df_facilities['emissions_diesel_kt']
        )
        non_ncc_fossil_emissions = df_facilities[~df_facilities['is_ncc']]['fossil_fuel_emissions_kt'].sum() / 1000
        ncc_emissions = df_facilities[df_facilities['is_ncc']]['emissions_naphtha_kt'].sum() / 1000
        
        # Calculate total electricity consumption for RE weighting
        if 'emissions_electricity_kt' in df_facilities.columns:
            df_facilities['electricity_emissions_kt'] = df_facilities['emissions_electricity_kt']
        else:
            # Fallback if column missing (should be there from baseline)
            df_facilities['electricity_emissions_kt'] = 0
            
        # Parameters
        lifetime = 20 # years for CAPEX amortization
        
        # Track previous deployment to calculate new CAPEX investment flow
        # Initialize with 0 for all facilities and technologies
        prev_deployment = {}
        for idx, row in df_facilities.iterrows():
            prev_deployment[row['facility_id']] = {'Heat_Pump': 0, 'NCC-H2': 0, 'NCC-Electricity': 0, 'RE_PPA': 0}
            
        for year in years:
            year_data = deployment_df[deployment_df['year'] == year]
            if year_data.empty:
                continue
            deploy_year = year_data.iloc[0]
            
            # Get costs for this year
            macc_year = self.df_macc[self.df_macc['year'] == year]
            
            # --- ALLOCATION LOGIC ---
            # We must re-calculate the cumulative deployment for this year for each facility
            
            current_deployment_by_fac = {}
            for idx, row in df_facilities.iterrows():
                current_deployment_by_fac[row['facility_id']] = {'Heat_Pump': 0, 'NCC-H2': 0, 'NCC-Electricity': 0, 'RE_PPA': 0}
            
            # 1. Heat Pump
            if deploy_year['heat_pump_mt'] > 0 and non_ncc_fossil_emissions > 0:
                 rate = deploy_year['heat_pump_mt'] / non_ncc_fossil_emissions
                 mask = (~df_facilities['is_ncc'])
                 for idx, row in df_facilities[mask].iterrows():
                     abated = (row['fossil_fuel_emissions_kt'] / 1000) * rate
                     current_deployment_by_fac[row['facility_id']]['Heat_Pump'] = abated

            # 2. NCC Tech
            ncc_tech = None
            deploy_amt = 0
            if deploy_year['ncc_h2_mt'] > 0:
                ncc_tech = 'NCC-H2'
                deploy_amt = deploy_year['ncc_h2_mt']
            elif deploy_year['ncc_elec_mt'] > 0:
                ncc_tech = 'NCC-Electricity'
                deploy_amt = deploy_year['ncc_elec_mt']
                
            if ncc_tech and ncc_emissions > 0:
                rate = deploy_amt / ncc_emissions
                mask = (df_facilities['is_ncc'])
                for idx, row in df_facilities[mask].iterrows():
                    abated = (row['emissions_naphtha_kt'] / 1000) * rate
                    current_deployment_by_fac[row['facility_id']][ncc_tech] = abated
            
            # 3. RE PPA
            if deploy_year['re_ppa_mt'] > 0:
                if ncc_tech == 'NCC-Electricity':
                    eligible_mask = (~df_facilities['is_ncc']) & (df_facilities['electricity_emissions_kt'] > 0)
                else:
                    eligible_mask = (df_facilities['electricity_emissions_kt'] > 0)
                
                eligible_emissions = df_facilities[eligible_mask]['electricity_emissions_kt'].sum() / 1000
                
                if eligible_emissions > 0:
                    rate = deploy_year['re_ppa_mt'] / eligible_emissions
                    for idx, row in df_facilities[eligible_mask].iterrows():
                        abated = (row['electricity_emissions_kt'] / 1000) * rate
                        current_deployment_by_fac[row['facility_id']]['RE_PPA'] = abated

            # --- CALCULATE METRICS PER FACILITY ---
            
            row_data = [] 
            
            for idx, row in df_facilities.iterrows():
                fac_id = row['facility_id']
                loc = row['location']
                
                # Calculate Electricity Demand (TWh)
                # Base electricity estimate (approximate from 2025 emissions)
                # Grid EF 2025 ~ 0.436 tCO2/MWh
                grid_ef_2025 = 0.436
                base_emissions_t = row['electricity_emissions_kt'] * 1000
                base_mwh = base_emissions_t / grid_ef_2025 if base_emissions_t > 0 else 0
                    
                # Increase from tech
                increase_mwh = (
                    current_deployment_by_fac[fac_id]['NCC-Electricity'] * 1e6 * 5.3 + 
                    current_deployment_by_fac[fac_id]['Heat_Pump'] * 1e6 * 4.65
                )
                
                total_elec_twh = (base_mwh + increase_mwh) / 1e6
                
                capex_investment_usd = 0
                total_annual_cost_usd = 0
                
                for tech in ['Heat_Pump', 'NCC-H2', 'NCC-Electricity', 'RE_PPA']:
                    amt = current_deployment_by_fac[fac_id][tech]
                    prev_amt = prev_deployment[fac_id][tech]
                    delta = max(0, amt - prev_amt) # New capacity
                    
                    try:
                        t_data = macc_year[macc_year['technology'] == tech]
                        if not t_data.empty:
                            t_data = t_data.iloc[0]
                            unit_capex_ann = t_data['capex_ann_usd_per_tco2']
                            unit_opex = t_data['opex_ann_usd_per_tco2']
                            unit_fuel = t_data['fuel_cost_diff_usd_per_tco2']
                            
                            # CAPEX Investment (Full cost upfront)
                            if delta > 0:
                                capex_investment_usd += delta * 1e6 * unit_capex_ann * lifetime
                                
                            # Annual Cost
                            total_annual_cost_usd += amt * 1e6 * (unit_capex_ann + unit_opex + unit_fuel)
                    except (IndexError, KeyError):
                        pass
                        
                # Update prev deployment for next loop
                for tech in ['Heat_Pump', 'NCC-H2', 'NCC-Electricity', 'RE_PPA']:
                    prev_deployment[fac_id][tech] = current_deployment_by_fac[fac_id][tech]
                    
                row_data.append({
                    'location': loc,
                    'capex_investment_musd': capex_investment_usd / 1e6,
                    'total_annual_cost_musd': total_annual_cost_usd / 1e6,
                    'electricity_demand_twh': total_elec_twh
                })
                
            # Aggregate by region
            df_year_sim = pd.DataFrame(row_data)
            agg = df_year_sim.groupby('location').sum().reset_index()
            agg['year'] = year
            agg['scenario'] = scenario_name
            regional_results.append(agg)
            
        # Combine all years
        final_df = pd.concat(regional_results, ignore_index=True)
        final_df.to_csv(self.output_dir / 'regional_annual_analysis.csv', index=False)
        print(f"   ✓ Saved regional analysis: regional_annual_analysis.csv")
        return final_df
