"""
MODULE 3: COST OPTIMIZATION
Find least-cost technology deployment pathways
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from .utils import save_csv_output, save_plot, is_ncc_facility

class CostOptimizer:
    """Cost optimization under emission constraints

    Supports two types of constraints:
    1. Annual emission path: yearly targets from CSV
    2. Carbon budget: total cumulative emissions limit
    """

    def __init__(self, baseline_output='outputs/module_01', macc_output='outputs/module_02',
                 output_dir='outputs/module_03', scenario_file='data/emission_scenarios_template.csv'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

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
        """Optimize with annual emission targets"""
        years = range(2025, 2051)
        deployment = []

        for year in years:
            bau = self.df_bau[self.df_bau['year'] == year]['total_emissions_mt'].iloc[0]
            target = emission_path.get(year, bau)  # Use BAU if no target specified
            required = max(0, bau - target)

            # Get available technologies sorted by cost
            tech_year = self.df_macc[
                (self.df_macc['year'] == year) & (self.df_macc['available'] == True)
            ].sort_values('total_cost_usd_per_tco2')

            # Deploy technologies in cost order
            deployed = {'Heat_Pump': 0, 'NCC-H2': 0, 'NCC-Electricity': 0}
            remaining = required

            for _, tech in tech_year.iterrows():
                if remaining <= 0:
                    break
                deploy = min(remaining, tech['abatement_potential_mtco2'])
                deployed[tech['technology']] += deploy
                remaining -= deploy

            deployment.append({
                'year': year,
                'target_mt': target,
                'bau_mt': bau,
                'heat_pump_mt': deployed['Heat_Pump'],
                'ncc_h2_mt': deployed['NCC-H2'],
                'ncc_elec_mt': deployed['NCC-Electricity'],
                'total_deployed_mt': sum(deployed.values()),
                'actual_emissions_mt': bau - sum(deployed.values()),
                'shortfall_mt': max(0, bau - sum(deployed.values()) - target),
            })

        return pd.DataFrame(deployment)

    def _optimize_carbon_budget(self, scenario_name, total_budget):
        """Optimize with total carbon budget constraint

        This uses a simple greedy approach:
        1. Deploy cheapest technologies first across all years
        2. Continue until cumulative emissions = budget
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
                })

        # Sort by cost
        tech_options_df = pd.DataFrame(tech_options).sort_values('cost')

        # Deploy technologies until budget constraint met
        deployment_dict = {year: {'Heat_Pump': 0, 'NCC-H2': 0, 'NCC-Electricity': 0}
                          for year in years}

        cumulative = 0
        bau_cumulative_so_far = 0

        for year in years:
            bau = self.df_bau[self.df_bau['year'] == year]['total_emissions_mt'].iloc[0]
            bau_cumulative_so_far += bau

            # How much room left in budget?
            budget_remaining = total_budget - cumulative
            required_this_year = bau - budget_remaining / (2051 - year)  # Spread remaining budget

            # Deploy technologies for this year
            for _, tech in tech_options_df[tech_options_df['year'] == year].iterrows():
                if cumulative >= total_budget:
                    break
                deploy = min(tech['potential'], bau - sum(deployment_dict[year].values()))
                if deploy > 0:
                    deployment_dict[year][tech['technology']] += deploy

            actual_emission = bau - sum(deployment_dict[year].values())
            cumulative += actual_emission

        # Convert to dataframe
        deployment = []
        cumulative = 0
        for year in years:
            bau = self.df_bau[self.df_bau['year'] == year]['total_emissions_mt'].iloc[0]
            actual = bau - sum(deployment_dict[year].values())
            cumulative += actual

            deployment.append({
                'year': year,
                'target_mt': None,  # No annual target, only budget
                'bau_mt': bau,
                'heat_pump_mt': deployment_dict[year]['Heat_Pump'],
                'ncc_h2_mt': deployment_dict[year]['NCC-H2'],
                'ncc_elec_mt': deployment_dict[year]['NCC-Electricity'],
                'total_deployed_mt': sum(deployment_dict[year].values()),
                'actual_emissions_mt': actual,
                'cumulative_emissions_mt': cumulative,
                'budget_remaining_mt': total_budget - cumulative,
            })

        print(f"   Final cumulative: {cumulative:.0f} MtCO2")
        print(f"   Budget compliance: {(cumulative/total_budget)*100:.1f}%")

        return pd.DataFrame(deployment)

    def create_visualizations(self, results):
        """Create visualizations"""
        print("\n🎨 Creating visualizations...")

        for scenario, df in results.items():
            # Deployment stack plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

            # Top: Technology deployment
            ax1.stackplot(df['year'], df['heat_pump_mt'], df['ncc_h2_mt'], df['ncc_elec_mt'],
                        labels=['Heat Pump', 'NCC-H2', 'NCC-Electricity'],
                        colors=['#2ECC71', '#3498DB', '#E74C3C'], alpha=0.8)
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
                'reduction_2030_pct': ((52 - df[df['year'] == 2030]['actual_emissions_mt'].iloc[0]) / 52) * 100,
                'reduction_2050_pct': ((52 - df[df['year'] == 2050]['actual_emissions_mt'].iloc[0]) / 52) * 100,
            })

        df_comparison = pd.DataFrame(comparison)
        save_csv_output(df_comparison, self.output_dir / 'scenario_comparison.csv')
        print(f"   ✓ Saved: scenario_comparison.csv")
