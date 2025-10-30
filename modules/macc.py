"""
MODULE 2: ENERGY-BASED MACC ANALYSIS
Calculate Marginal Abatement Cost Curves with explicit energy consumption tracking
REDESIGNED: 2025-10-16 - Replaced LCOE approach with energy-based methodology
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from .utils import (DataLoader, TechnologyCostCalculator, PriceCalculator,
                    save_csv_output, save_plot, is_ncc_facility, identify_product_group)


class MACCAnalyzer:
    """
    Energy-Based MACC Analysis

    Key Principle:
        MACC = CAPEX_annual + OPEX_annual + Fuel_Cost_Differential

    Where Fuel_Cost_Differential explicitly tracks:
        - Energy replacement (fossil → H2/electricity)
        - Price differentials
        - Emission reductions

    CRITICAL: Naphtha feedstock cost is FIXED (not included in differential)
    """

    def __init__(self, baseline_output='outputs/module_01', data_dir='data',
                 output_dir='outputs/module_02'):
        self.baseline_dir = Path(baseline_output)
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("MODULE 2: ENERGY-BASED MACC ANALYSIS")
        print("="*80)

        # Load data
        print("\nLoading data...")
        loader = DataLoader(self.data_dir)

        self.df_baseline = pd.read_csv(self.baseline_dir / 'baseline_2025_detailed.csv')
        self.df_tech_params = loader.load_technology_params()
        self.df_h2_prices = loader.load_h2_prices()
        self.df_re_prices = loader.load_re_prices()
        self.df_grid_prices = loader.load_grid_prices()
        self.df_hp_applicability = loader.load_heat_pump_applicability()
        self.df_fuel_prices = pd.read_csv(self.data_dir / 'fuel_price_trajectory.csv')
        self.df_grid_emission = pd.read_csv(self.data_dir / 'grid_emission_trajectory.csv')

        # Load demand growth trajectory
        try:
            self.df_demand_growth = pd.read_csv(self.data_dir / 'demand_growth_trajectory.csv')
            print(f"   - Loaded demand growth trajectory")
        except FileNotFoundError:
            print("   - No demand growth file, assuming zero growth")
            self.df_demand_growth = pd.DataFrame({
                'year': range(2025, 2051),
                'cumulative_capacity_multiplier': [1.0] * 26
            })

        print(f"   - Loaded baseline: {len(self.df_baseline)} facilities")
        print(f"   - Loaded {len(self.df_tech_params)} technologies")

        # Initialize calculators
        self.tech_cost_calc = TechnologyCostCalculator(self.df_tech_params)
        self.price_calc = PriceCalculator(self.df_h2_prices, self.df_re_prices, self.df_fuel_prices)

        # Load emission factors from data file
        self.df_emission_factors = pd.read_csv(self.data_dir / 'emission_factors.csv')
        ef_dict = self.df_emission_factors.set_index('fuel')

        # Get emission factors
        self.ef_naphtha = ef_dict.loc['Naphtha', 'tCO2_per_GJ']
        self.ef_h2_green = ef_dict.loc['H2', 'tCO2_per_kg']  # Green H2 = 0.0

    def calculate_macc_annual(self, years=range(2025, 2051)):
        """Calculate MACC for all technologies and years"""
        print(f"\nCalculating dynamic MACC ({min(years)}-{max(years)})...")

        macc_data = []

        for year in years:
            # Get prices for this year
            h2_price = self.price_calc.get_h2_price(year)  # $/kg
            re_price = self.price_calc.get_re_price(year)  # $/MWh
            naphtha_price = self.df_fuel_prices[self.df_fuel_prices['year'] == year]['naphtha_usd_per_gj'].iloc[0]

            # Get GRID electricity price and emission factor (Korean grid)
            grid_price = self.df_grid_prices[self.df_grid_prices['year'] == year]['grid_price_usd_per_mwh'].iloc[0]
            grid_ef = self.df_grid_emission[self.df_grid_emission['year'] == year]['grid_ef_tco2_per_mwh'].iloc[0]

            # 1. HEAT PUMPS (uses GRID electricity)
            hp_macc = self._calculate_heat_pump_macc(year, h2_price, re_price, naphtha_price, grid_price)
            macc_data.append(hp_macc)

            # 2. NCC-H2
            ncc_h2_macc = self._calculate_ncc_h2_macc(year, h2_price, naphtha_price)
            macc_data.append(ncc_h2_macc)

            # 3. NCC-Electricity (uses RENEWABLE electricity - RE_PPA)
            ncc_elec_macc = self._calculate_ncc_electricity_macc(year, re_price, naphtha_price)
            macc_data.append(ncc_elec_macc)

            # 4. RE Switching (converting grid electricity to RE)
            re_ppa_macc = self._calculate_re_ppa_macc(year, re_price, grid_price, grid_ef)
            macc_data.append(re_ppa_macc)

        df_macc = pd.DataFrame(macc_data)

        print(f"   - Calculated {len(df_macc)} technology-year combinations")

        self.df_macc = df_macc
        return df_macc

    def _calculate_heat_pump_macc(self, year, h2_price, re_price, naphtha_price, elec_price):
        """
        Calculate Heat Pump MACC with explicit energy conversion

        Energy Conversion:
            Before: Fossil fuel combustion (naphtha, LNG, fuel gas, etc.)
            After:  Electricity = Fossil_fuel_GJ / COP / 3.6 [MWh]

        Cost:
            MACC = CAPEX_annual + OPEX_annual + Fuel_Diff
            Fuel_Diff = (Electricity_cost - Fossil_fuel_cost) / tCO2_abated
        """
        tech_costs = self.tech_cost_calc.get_technology_costs('Heat_Pump', year)
        cop = tech_costs['cop']

        # Get capacity multiplier for this year (demand growth)
        capacity_multiplier = self.df_demand_growth[
            self.df_demand_growth['year'] == year
        ]['cumulative_capacity_multiplier'].iloc[0]

        # Abatement potential
        # Heat pumps replace ALL fossil fuel combustion (NOT electricity)
        potential_mt = 0
        total_fossil_fuel_gj = 0  # For fuel cost calculation

        for _, row in self.df_hp_applicability.iterrows():
            product_group = row['product_group']
            applicability = row['applicability_pct'] / 100

            # Get fossil fuel combustion emissions for NON-NCC facilities only
            # NCC facilities get NCC-H2 and NCC-Electricity, not Heat Pump
            df_group = self.df_baseline[
                (self.df_baseline['product_group'] == product_group) &
                (self.df_baseline['process'] != 'Naphtha Cracker')
            ]

            fossil_emissions_kt = (
                df_group['emissions_naphtha_kt'].sum() +
                df_group['emissions_lng_kt'].sum() +
                df_group['emissions_fuel_gas_kt'].sum() +
                df_group['emissions_lpg_kt'].sum() +
                df_group['emissions_fuel_oil_kt'].sum() +
                df_group['emissions_diesel_kt'].sum()
            )

            # Calculate total fossil fuel energy (GJ) from emissions
            # Assuming average EF for fossil fuels ≈ 0.0149 tCO2/GJ
            fossil_fuel_gj = (fossil_emissions_kt * 1000) / self.ef_naphtha

            potential_mt += (fossil_emissions_kt / 1000) * applicability
            total_fossil_fuel_gj += fossil_fuel_gj * applicability

        # Scale by demand growth
        potential_mt *= capacity_multiplier
        total_fossil_fuel_gj *= capacity_multiplier

        # Energy conversion
        electricity_mwh_required = total_fossil_fuel_gj / cop / 3.6  # MWh

        # Emissions after heat pump (using RE electricity)
        re_ef = 0.05  # tCO2/MWh (lifecycle emissions for renewable energy)
        emissions_after_mt = (electricity_mwh_required * re_ef) / 1e6  # MtCO2

        # Actual abatement (considering RE emissions)
        abatement_mt = potential_mt - emissions_after_mt

        # Costs per MtCO2 abated (Simple annualization: NO discount rate)
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        capex_ann = capex_musd_per_mtco2 / lifetime  # Simple: CAPEX / lifetime
        opex_ann = capex_musd_per_mtco2 * (tech_costs['opex_pct_capex'] / 100)  # OPEX as % of CAPEX

        # Fuel cost: RE electricity cost only (no fossil fuel savings counted)
        electricity_cost_total = electricity_mwh_required * re_price
        fuel_cost_diff_total = electricity_cost_total  # Pure RE electricity cost

        if abatement_mt > 0:
            fuel_cost_diff_per_tco2 = fuel_cost_diff_total / (abatement_mt * 1e6)
        else:
            fuel_cost_diff_per_tco2 = 1e9

        total_cost = capex_ann + opex_ann + fuel_cost_diff_per_tco2

        return {
            'year': year,
            'technology': 'Heat_Pump',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': abatement_mt,
            'capex_ann_usd_per_tco2': capex_ann,
            'opex_ann_usd_per_tco2': opex_ann,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff_per_tco2,
            'total_cost_usd_per_tco2': total_cost,
            're_price_usd_per_mwh': re_price,
            'h2_price_usd_per_kg': h2_price,
            'electricity_consumption_mwh': electricity_mwh_required,
            'fossil_fuel_replaced_gj': total_fossil_fuel_gj,
            'methodology': 'Energy-based'
        }

    def _calculate_ncc_h2_macc(self, year, h2_price, naphtha_price):
        """
        Calculate NCC-H2 MACC with H2 as energy source

        Process Change:
            Before: Naphtha cracking with LNG/Fuel Gas combustion (11.23 GJ/ton ethylene)
            After:  Naphtha cracking with H2 (0.20 ton H2/ton ethylene)

        CRITICAL:
            - Naphtha feedstock (105 GJ) continues unchanged - still purchased!
            - LNG/Fuel Gas combustion (11.23 GJ) is ELIMINATED
            - H2 provides energy instead
            - NO fuel cost saving (naphtha not used as fuel before)

        Cost:
            MACC = CAPEX_annual + OPEX_annual + H2_cost / tCO2_abated
        """
        tech_costs = self.tech_cost_calc.get_technology_costs('NCC-H2', year)
        h2_ton_per_ton_ethylene = tech_costs['h2_ton_per_ton_ethylene']

        # Get capacity multiplier
        capacity_multiplier = self.df_demand_growth[
            self.df_demand_growth['year'] == year
        ]['cumulative_capacity_multiplier'].iloc[0]

        # Get total ethylene production (kt/year)
        ncc_facilities = self.df_baseline[self.df_baseline['product'].apply(is_ncc_facility)]
        ethylene_production_kt = ncc_facilities[ncc_facilities['product'] == 'Ethylene']['capacity_kt'].sum()
        ethylene_production_kt *= capacity_multiplier

        # Emissions calculation (per ton ethylene)
        # Calculate from baseline data (average of ethylene NCC facilities)
        ethylene_ncc = ncc_facilities[ncc_facilities['product'] == 'Ethylene']
        if len(ethylene_ncc) > 0:
            # Calculate weighted average emissions per ton
            total_emissions_kt = ethylene_ncc['total_emissions_kt'].sum()
            total_capacity_kt = ethylene_ncc['capacity_kt'].sum()
            emission_baseline_per_ton = (total_emissions_kt / total_capacity_kt) * 1000  # tCO2/ton
        else:
            # Fallback to typical value for ethylene
            emission_baseline_per_ton = 1.74  # tCO2/ton (typical for NCC)

        # After NCC-H2: Naphtha becomes FEEDSTOCK only (no combustion), H2 provides energy
        emission_h2_per_ton = self.ef_h2_green  # tCO2/ton ethylene (green H2)
        abatement_per_ton = emission_baseline_per_ton - emission_h2_per_ton

        # Total abatement potential
        abatement_mt = (ethylene_production_kt * 1000 * abatement_per_ton) / 1e6  # MtCO2

        # Costs
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        capex_ann = capex_musd_per_mtco2 / lifetime  # Simple: CAPEX / lifetime
        opex_ann = capex_musd_per_mtco2 * (tech_costs['opex_pct_capex'] / 100)  # OPEX as % of CAPEX

        # Fuel cost: H2 cost only (no fossil fuel savings)
        h2_fuel_cost_per_ton = h2_ton_per_ton_ethylene * 1000 * h2_price  # $/ton ethylene

        if abatement_per_ton > 0:
            fuel_cost_diff_per_tco2 = h2_fuel_cost_per_ton / abatement_per_ton  # $/tCO2
        else:
            fuel_cost_diff_per_tco2 = 0

        total_cost = capex_ann + opex_ann + fuel_cost_diff_per_tco2

        return {
            'year': year,
            'technology': 'NCC-H2',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': abatement_mt,
            'capex_ann_usd_per_tco2': capex_ann,
            'opex_ann_usd_per_tco2': opex_ann,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff_per_tco2,
            'total_cost_usd_per_tco2': total_cost,
            're_price_usd_per_mwh': np.nan,
            'h2_price_usd_per_kg': h2_price,
            'h2_consumption_ton_per_ton_ethylene': h2_ton_per_ton_ethylene,
            'baseline_combustion_emissions_tco2_per_ton': emission_baseline_per_ton,
            'ethylene_production_kt': ethylene_production_kt,
            'h2_fuel_cost_per_ton_ethylene': h2_fuel_cost_per_ton,
            'methodology': 'Energy-based'
        }

    def _calculate_ncc_electricity_macc(self, year, re_price, naphtha_price):
        """
        Calculate NCC-Electricity MACC using RENEWABLE electricity (RE_PPA)

        Process Change:
            Before: Naphtha cracking with LNG/Fuel Gas combustion (~11 GJ/ton ethylene)
            After:  Naphtha cracking with RENEWABLE electricity (5.0 MWh/ton ethylene)

        CRITICAL:
            - Naphtha feedstock (105 GJ) continues unchanged - still purchased!
            - LNG/Fuel Gas combustion (~11 GJ) is ELIMINATED
            - RENEWABLE electricity provides energy (RE_PPA pricing)
            - Renewable electricity has ZERO emissions (no EF penalty)
            - NO fuel cost saving (naphtha not used as fuel before)

        Cost:
            MACC = CAPEX_annual + OPEX_annual + RE_electricity_cost / tCO2_abated

        Emissions:
            Baseline: Fossil fuel combustion emissions
            After: ZERO emissions (renewable electricity)
            Abatement: Baseline emissions (100% abatement)
        """
        tech_costs = self.tech_cost_calc.get_technology_costs('NCC-Electricity', year)
        elec_mwh_per_ton = tech_costs['elec_mwh_per_ton_ethylene']

        # Get capacity multiplier
        capacity_multiplier = self.df_demand_growth[
            self.df_demand_growth['year'] == year
        ]['cumulative_capacity_multiplier'].iloc[0]

        # Get total ethylene production
        ncc_facilities = self.df_baseline[self.df_baseline['product'].apply(is_ncc_facility)]
        ethylene_production_kt = ncc_facilities[ncc_facilities['product'] == 'Ethylene']['capacity_kt'].sum()
        ethylene_production_kt *= capacity_multiplier

        # Emissions calculation (per ton ethylene)
        # Calculate from baseline data (average of ethylene NCC facilities)
        ethylene_ncc = ncc_facilities[ncc_facilities['product'] == 'Ethylene']
        if len(ethylene_ncc) > 0:
            # Calculate weighted average emissions per ton
            total_emissions_kt = ethylene_ncc['total_emissions_kt'].sum()
            total_capacity_kt = ethylene_ncc['capacity_kt'].sum()
            emission_baseline_per_ton = (total_emissions_kt / total_capacity_kt) * 1000  # tCO2/ton
        else:
            # Fallback to typical value for ethylene
            emission_baseline_per_ton = 1.74  # tCO2/ton (typical for NCC)

        # After NCC-Electricity: Uses RENEWABLE electricity (ZERO emissions)
        emission_elec_per_ton = 0.0  # tCO2/ton ethylene (renewable = zero emissions)

        abatement_per_ton = emission_baseline_per_ton  # 100% abatement (baseline - 0)

        # Total abatement potential
        abatement_mt = (ethylene_production_kt * 1000 * abatement_per_ton) / 1e6  # MtCO2

        # Costs
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        capex_ann = capex_musd_per_mtco2 / lifetime  # Simple: CAPEX / lifetime
        opex_ann = capex_musd_per_mtco2 * (tech_costs['opex_pct_capex'] / 100)  # OPEX as % of CAPEX

        # Fuel cost: RENEWABLE electricity cost only (no fossil fuel savings)
        electricity_cost_per_ton = elec_mwh_per_ton * re_price  # $/ton ethylene

        if abatement_per_ton > 0:
            fuel_cost_diff_per_tco2 = electricity_cost_per_ton / abatement_per_ton  # $/tCO2
        else:
            fuel_cost_diff_per_tco2 = 0

        total_cost = capex_ann + opex_ann + fuel_cost_diff_per_tco2

        return {
            'year': year,
            'technology': 'NCC-Electricity',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': abatement_mt,
            'capex_ann_usd_per_tco2': capex_ann,
            'opex_ann_usd_per_tco2': opex_ann,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff_per_tco2,
            'total_cost_usd_per_tco2': total_cost,
            're_price_usd_per_mwh': re_price,
            'h2_price_usd_per_kg': np.nan,
            'electricity_consumption_mwh_per_ton_ethylene': elec_mwh_per_ton,
            'baseline_combustion_emissions_tco2_per_ton': emission_baseline_per_ton,
            'ethylene_production_kt': ethylene_production_kt,
            'electricity_cost_per_ton_ethylene': electricity_cost_per_ton,
            'grid_ef_tco2_per_mwh': 0.0,
            'grid_price_usd_per_mwh': np.nan,
            'methodology': 'Energy-based'
        }

    def _calculate_re_ppa_macc(self, year, re_price, grid_price, grid_ef):
        """
        Calculate RE PPA MACC (NCC facilities only)

        RE PPA = Renewable Power Purchase Agreement
        Simply switching from grid electricity to RE electricity for NCC facilities
        No infrastructure needed - just procurement contract
        No energy consumption change - just price differential

        User specified: "RE is only applied to NCC"

        Cost:
            MACC = Price_Diff / Abatement_per_MWh
            (CAPEX = 0, OPEX = 0)
        """
        tech_costs = self.tech_cost_calc.get_technology_costs('RE_PPA', year)

        # Get capacity multiplier
        capacity_multiplier = self.df_demand_growth[
            self.df_demand_growth['year'] == year
        ]['cumulative_capacity_multiplier'].iloc[0]

        # Filter NCC facilities only (user constraint)
        ncc_facilities = self.df_baseline[
            self.df_baseline['product'].apply(is_ncc_facility)
        ]

        # Calculate total electricity emissions for NCC facilities
        total_elec_emissions_mt = ncc_facilities['emissions_electricity_kt'].sum() / 1000  # MtCO2
        total_elec_emissions_mt *= capacity_multiplier

        # Emission factors
        re_ef = 0.05  # tCO2/MWh (lifecycle emissions for renewable energy)

        # Abatement per MWh
        abatement_per_mwh = grid_ef - re_ef

        # Abatement potential: all NCC electricity could switch to RE
        abatement_potential_mt = total_elec_emissions_mt * (1 - re_ef / grid_ef)

        # Cost: Price differential between RE and Grid (Option A - Switching)
        # When switching from Grid to RE:
        #   - Stop paying Grid price
        #   - Start paying RE price
        #   - Net cost = (RE price - Grid price) × electricity
        #   - This can be NEGATIVE if RE is cheaper than Grid!
        total_elec_mwh = total_elec_emissions_mt * 1e6 / grid_ef  # MWh (from emissions back to energy)
        price_diff = re_price - grid_price  # Can be negative!
        total_cost_diff = total_elec_mwh * price_diff  # Total incremental cost (can be negative!)

        if abatement_potential_mt > 0:
            cost_per_tco2 = total_cost_diff / (abatement_potential_mt * 1e6)  # $/tCO2 (can be negative!)
        else:
            cost_per_tco2 = 1e9

        return {
            'year': year,
            'technology': 'RE_PPA',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': abatement_potential_mt,
            'capex_ann_usd_per_tco2': 0,  # No capital investment for PPA
            'opex_ann_usd_per_tco2': 0,   # Operating cost included in PPA price
            'fuel_cost_diff_usd_per_tco2': cost_per_tco2,
            'total_cost_usd_per_tco2': cost_per_tco2,
            're_price_usd_per_mwh': re_price,
            'h2_price_usd_per_kg': np.nan,
            'grid_price_usd_per_mwh': grid_price,
            'grid_ef_tco2_per_mwh': grid_ef,
            'methodology': 'Energy-based'
        }

    def create_visualizations(self):
        """Create MACC curve visualizations"""
        print("\nCreating visualizations...")

        # MACC curves for key years
        key_years = [2025, 2030, 2040, 2050]

        for year in key_years:
            df_year = self.df_macc[
                (self.df_macc['year'] == year) &
                (self.df_macc['available'] == True) &
                (self.df_macc['technology'] != 'Heat_Pump')  # Exclude Heat Pump from visualization
            ].sort_values('total_cost_usd_per_tco2')

            if len(df_year) == 0:
                continue

            fig, ax = plt.subplots(figsize=(12, 7))

            # Sort by cost for proper MACC ordering
            df_year_sorted = df_year.sort_values('total_cost_usd_per_tco2')

            # Create MACC bars
            x_pos = 0
            colors = {'Heat_Pump': '#2ECC71', 'NCC-H2': '#3498DB', 'NCC-Electricity': '#E74C3C', 'RE_PPA': '#F39C12'}
            tech_labels = {
                'Heat_Pump': 'Heat Pump',
                'RE_PPA': 'RE PPA',
                'NCC-Electricity': 'NCC-Electricity',
                'NCC-H2': 'NCC-H2'
            }

            legend_entries = []

            for _, row in df_year_sorted.iterrows():
                width = row['abatement_potential_mtco2']
                height = row['total_cost_usd_per_tco2']
                color = colors.get(row['technology'], 'gray')
                label = tech_labels.get(row['technology'], row['technology'])

                if label not in legend_entries:
                    ax.bar(x_pos + width/2, height, width=width, color=color,
                          edgecolor='black', linewidth=1.2, alpha=0.85, label=label)
                    legend_entries.append(label)
                else:
                    ax.bar(x_pos + width/2, height, width=width, color=color,
                          edgecolor='black', linewidth=1.2, alpha=0.85)

                x_pos += width

            # Zero line
            ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5, alpha=0.8, zorder=10)

            # Labels
            ax.set_xlabel('Cumulative Abatement Potential (MtCO2/year)', fontsize=13, fontweight='bold')
            ax.set_ylabel('Marginal Abatement Cost ($/tCO2)', fontsize=13, fontweight='bold')
            ax.set_title(f'MACC Curve - {year} (Energy-Based)', fontsize=15, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y', linestyle='--')
            ax.legend(loc='best', fontsize=10, framealpha=0.95, edgecolor='black')

            save_plot(fig, self.output_dir / f'macc_curve_{year}.png')

        # Cost evolution
        fig, ax = plt.subplots(figsize=(12, 7))

        tech_styles = {
            'Heat_Pump': {'color': '#2ECC71', 'marker': 'o', 'label': 'Heat Pump'},
            'RE_PPA': {'color': '#F39C12', 'marker': 's', 'label': 'RE PPA'},
            'NCC-Electricity': {'color': '#E74C3C', 'marker': '^', 'label': 'NCC-Electricity'},
            'NCC-H2': {'color': '#3498DB', 'marker': 'D', 'label': 'NCC-H2'}
        }

        # Exclude Heat Pump from cost evolution plot
        for tech in ['RE_PPA', 'NCC-Electricity', 'NCC-H2']:
            df_tech = self.df_macc[self.df_macc['technology'] == tech]
            style = tech_styles[tech]
            ax.plot(df_tech['year'], df_tech['total_cost_usd_per_tco2'],
                   linewidth=2.5, color=style['color'], marker=style['marker'],
                   markersize=6, label=style['label'], alpha=0.9)

        ax.axhline(y=0, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label='Cost Parity')
        ax.set_xlabel('Year', fontsize=13, fontweight='bold')
        ax.set_ylabel('Marginal Abatement Cost ($/tCO2)', fontsize=13, fontweight='bold')
        ax.set_title('Technology Cost Trajectories (2025-2050) - Energy-Based', fontsize=15, fontweight='bold')
        ax.legend(loc='best', fontsize=10, framealpha=0.95)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(2024, 2051)

        save_plot(fig, self.output_dir / 'cost_evolution_annual.png')

    def save_outputs(self):
        """Save outputs"""
        print("\nSaving outputs...")
        save_csv_output(self.df_macc, self.output_dir / 'macc_annual_2025_2050.csv',
                       f"({len(self.df_macc)} tech-year combinations)")

        # Add alternative cost units (if available)
        try:
            from .regional_energy_tracker import create_cost_conversion_table
            df_cost_conversion = create_cost_conversion_table(self.df_macc)
            save_csv_output(df_cost_conversion, self.output_dir / 'macc_cost_units_comparison.csv',
                           "Multiple cost units for easier interpretation")
        except (ImportError, ModuleNotFoundError):
            print("   (skipping cost conversion table - regional_energy_tracker not available)")

    def run_complete_analysis(self):
        """Run complete MACC analysis"""
        print("\n" + "="*80)
        print("RUNNING COMPLETE MACC ANALYSIS (ENERGY-BASED)")
        print("="*80)

        self.calculate_macc_annual()
        self.create_visualizations()
        self.save_outputs()

        print("\n" + "="*80)
        print("MODULE 2 COMPLETE")
        print("="*80)
        print(f"\nOutputs saved to: {self.output_dir}")
        print("\nKey changes from LCOE approach:")
        print("  - Explicit CAPEX, OPEX, Fuel Cost tracking")
        print("  - H2 consumption: 0.8 ton/ton ethylene")
        print("  - Electricity consumption: 13 MWh/ton ethylene")
        print("  - Naphtha feedstock cost: FIXED (not in differential)")

        return {'macc': self.df_macc}
