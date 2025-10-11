"""
MODULE 2: DYNAMIC MACC ANALYSIS
Calculate Marginal Abatement Cost Curves dynamically
NO pre-calculated costs from Excel - all computed in Python
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
    Dynamic MACC Analysis
    - Calculate technology costs from capex + opex + fuel differentials
    - Track technology availability by year
    - Annual MACC curves 2025-2050
    """

    def __init__(self, baseline_output='outputs/module_01', data_dir='data',
                 output_dir='outputs/module_02'):
        self.baseline_dir = Path(baseline_output)
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("MODULE 2: DYNAMIC MACC ANALYSIS")
        print("="*80)

        # Load data
        print("\nLoading Loading data...")
        loader = DataLoader(data_dir)

        self.df_baseline = pd.read_csv(self.baseline_dir / 'baseline_2025_detailed.csv')
        self.df_tech_params = loader.load_technology_params()
        self.df_h2_prices = loader.load_h2_prices()
        self.df_re_prices = loader.load_re_prices()
        self.df_hp_applicability = loader.load_heat_pump_applicability()
        self.df_fuel_prices = pd.read_csv(self.data_dir / 'fuel_price_trajectory.csv')
        self.df_grid_emission = pd.read_csv(self.data_dir / 'grid_emission_trajectory.csv')
        self.df_ncc_lcoe = pd.read_csv(self.data_dir / 'ncc_lcoe_trajectory.csv')

        print(f"   - Loaded baseline: {len(self.df_baseline)} facilities")
        print(f"   - Loaded {len(self.df_tech_params)} technologies")
        print(f"   - Loaded LCOE trajectory for NCC technologies")

        # Initialize calculators
        self.tech_cost_calc = TechnologyCostCalculator(self.df_tech_params)
        self.price_calc = PriceCalculator(self.df_h2_prices, self.df_re_prices, self.df_fuel_prices)

        # Constants
        self.discount_rate = 0.08
        self.ef_naphtha = 0.0149  # tCO2/GJ

    def calculate_macc_annual(self, years=range(2025, 2051)):
        """Calculate MACC for all technologies and years"""
        print(f"\nCalculating Calculating dynamic MACC ({min(years)}-{max(years)})...")

        macc_data = []

        for year in years:
            # Get prices for this year
            h2_price = self.price_calc.get_h2_price(year)  # $/kg
            re_price = self.price_calc.get_re_price(year)  # $/MWh
            naphtha_price = self.df_fuel_prices[self.df_fuel_prices['year'] == year]['naphtha_usd_per_gj'].iloc[0]

            # 1. HEAT PUMPS
            hp_macc = self._calculate_heat_pump_macc(year, h2_price, re_price, naphtha_price)
            macc_data.append(hp_macc)

            # 2. NCC-H2
            ncc_h2_macc = self._calculate_ncc_h2_macc(year, h2_price, naphtha_price)
            macc_data.append(ncc_h2_macc)

            # 3. NCC-Electricity
            ncc_elec_macc = self._calculate_ncc_electricity_macc(year, re_price, naphtha_price)
            macc_data.append(ncc_elec_macc)

            # 4. RE PPA (NCC facilities only)
            grid_ef = self.df_grid_emission[self.df_grid_emission['year'] == year]['grid_ef_tco2_per_mwh'].iloc[0]
            re_ppa_macc = self._calculate_re_ppa_macc(year, re_price, grid_ef)
            macc_data.append(re_ppa_macc)

        df_macc = pd.DataFrame(macc_data)

        print(f"   - Calculated {len(df_macc)} technology-year combinations")

        self.df_macc = df_macc
        return df_macc

    def _calculate_heat_pump_macc(self, year, h2_price, re_price, naphtha_price):
        """Calculate heat pump MACC"""
        tech_costs = self.tech_cost_calc.get_technology_costs('Heat_Pump', year)

        # Abatement potential
        # Heat pumps can replace ALL fossil fuel combustion (naphtha, LNG, fuel gas, etc)
        # NOT electricity emissions (those are grid-based)
        potential_mt = 0
        for _, row in self.df_hp_applicability.iterrows():
            product_group = row['product_group']
            applicability = row['applicability_pct'] / 100

            # Get ALL fossil fuel combustion emissions for this product group
            df_group = self.df_baseline[self.df_baseline['product_group'] == product_group]
            fossil_emissions = (
                df_group['emissions_naphtha_kt'].sum() +
                df_group['emissions_lng_kt'].sum() +
                df_group['emissions_fuel_gas_kt'].sum() +
                df_group['emissions_lpg_kt'].sum() +
                df_group['emissions_fuel_oil_kt'].sum() +
                df_group['emissions_diesel_kt'].sum()
            ) / 1000  # MtCO2

            potential_mt += fossil_emissions * applicability

        # Costs
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        crf = self.price_calc.calculate_capital_recovery_factor(self.discount_rate, lifetime)
        capex_ann = capex_musd_per_mtco2 * crf  # MUSD/MtCO2 * CRF = USD/tCO2 (Million cancels)

        opex_ann = capex_ann * (tech_costs['opex_pct_capex'] / 100)

        # Fuel cost differential (heat pump vs naphtha)
        cop = tech_costs['cop']
        re_price_per_gj_thermal = (re_price / 3.6) / cop  # $/GJ thermal output
        gj_per_tco2 = 1 / self.ef_naphtha
        fuel_cost_diff = (re_price_per_gj_thermal - naphtha_price) * gj_per_tco2

        total_cost = capex_ann + opex_ann + fuel_cost_diff

        return {
            'year': year,
            'technology': 'Heat_Pump',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': potential_mt,
            'capex_ann_usd_per_tco2': capex_ann,
            'opex_ann_usd_per_tco2': opex_ann,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff,
            'total_cost_usd_per_tco2': total_cost,
            're_price_usd_per_mwh': re_price,
            'h2_price_usd_per_kg': h2_price,
        }

    def _calculate_ncc_h2_macc(self, year, h2_price, naphtha_price):
        """
        Calculate NCC-H2 MACC using LCOE-based methodology

        This method uses Levelized Cost of Ethylene (LCOE) premium approach
        instead of traditional CAPEX+OPEX+Fuel methodology, as NCC-H2
        represents a fundamental process transformation, not just fuel switching.

        Reference: MACC_METHODOLOGY_ACADEMIC.md Section 2.4.2
        """
        tech_costs = self.tech_cost_calc.get_technology_costs('NCC-H2', year)

        # Abatement potential (NCC emissions only)
        # NOTE: This represents the MAXIMUM potential if ALL naphtha crackers adopt H2
        # In reality, this is mutually exclusive with NCC-Electricity
        # The optimizer will choose between H2 and Electricity based on cost
        ncc_emissions = self.df_baseline[
            self.df_baseline['product'].apply(is_ncc_facility)
        ]['emissions_naphtha_kt'].sum() / 1000  # MtCO2

        # Get LCOE data for this year
        lcoe_data = self.df_ncc_lcoe[self.df_ncc_lcoe['year'] == year].iloc[0]

        # LCOE Premium Method
        lcoe_baseline = lcoe_data['baseline_steam_cracker_usd_per_ton']  # $/ton ethylene
        lcoe_h2 = lcoe_data['ncc_h2_usd_per_ton']  # $/ton ethylene
        lcoe_premium = lcoe_h2 - lcoe_baseline

        # Emission intensities
        emission_intensity_baseline = lcoe_data['baseline_emission_intensity_tco2_per_ton']  # tCO2/ton ethylene
        emission_intensity_h2 = lcoe_data['ncc_h2_emission_intensity_tco2_per_ton']  # tCO2/ton ethylene
        abatement_per_ton_ethylene = emission_intensity_baseline - emission_intensity_h2

        # Calculate MACC cost
        if abatement_per_ton_ethylene > 0:
            macc_cost = lcoe_premium / abatement_per_ton_ethylene  # $/tCO2
        else:
            macc_cost = 1e9  # Very high if no abatement

        # For transparency, show components (even though not used in total calculation)
        # These are estimates for reporting purposes only
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        crf = self.price_calc.calculate_capital_recovery_factor(self.discount_rate, lifetime)
        capex_ann_estimate = capex_musd_per_mtco2 * crf
        opex_ann_estimate = capex_ann_estimate * (tech_costs['opex_pct_capex'] / 100)

        return {
            'year': year,
            'technology': 'NCC-H2',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': ncc_emissions,
            'capex_ann_usd_per_tco2': capex_ann_estimate,  # Estimate only
            'opex_ann_usd_per_tco2': opex_ann_estimate,  # Estimate only
            'fuel_cost_diff_usd_per_tco2': 0.0,  # Not applicable (LCOE method)
            'total_cost_usd_per_tco2': macc_cost,  # LCOE-based
            're_price_usd_per_mwh': np.nan,
            'h2_price_usd_per_kg': h2_price,
            'lcoe_baseline_usd_per_ton': lcoe_baseline,
            'lcoe_technology_usd_per_ton': lcoe_h2,
            'lcoe_premium_usd_per_ton': lcoe_premium,
            'emission_intensity_baseline': emission_intensity_baseline,
            'emission_intensity_technology': emission_intensity_h2,
            'methodology': 'LCOE-based'
        }

    def _calculate_ncc_electricity_macc(self, year, re_price, naphtha_price):
        """
        Calculate NCC-Electricity MACC using LCOE-based methodology

        This method uses Levelized Cost of Ethylene (LCOE) premium approach
        instead of traditional CAPEX+OPEX+Fuel methodology, as electric crackers
        represent a fundamental process transformation with complete redesign.

        Reference: MACC_METHODOLOGY_ACADEMIC.md Section 2.4.1
        """
        tech_costs = self.tech_cost_calc.get_technology_costs('NCC-Electricity', year)

        # Abatement potential
        ncc_emissions = self.df_baseline[
            self.df_baseline['product'].apply(is_ncc_facility)
        ]['emissions_naphtha_kt'].sum() / 1000

        # Get LCOE data for this year
        lcoe_data = self.df_ncc_lcoe[self.df_ncc_lcoe['year'] == year].iloc[0]

        # LCOE Premium Method
        lcoe_baseline = lcoe_data['baseline_steam_cracker_usd_per_ton']  # $/ton ethylene
        lcoe_elec = lcoe_data['ncc_electricity_usd_per_ton']  # $/ton ethylene
        lcoe_premium = lcoe_elec - lcoe_baseline

        # Emission intensities
        emission_intensity_baseline = lcoe_data['baseline_emission_intensity_tco2_per_ton']  # tCO2/ton ethylene
        emission_intensity_elec = lcoe_data['ncc_electricity_emission_intensity_tco2_per_ton']  # tCO2/ton ethylene
        abatement_per_ton_ethylene = emission_intensity_baseline - emission_intensity_elec

        # Calculate MACC cost
        if abatement_per_ton_ethylene > 0:
            macc_cost = lcoe_premium / abatement_per_ton_ethylene  # $/tCO2
        else:
            macc_cost = 1e9  # Very high if no abatement

        # For transparency, show components (even though not used in total calculation)
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        crf = self.price_calc.calculate_capital_recovery_factor(self.discount_rate, lifetime)
        capex_ann_estimate = capex_musd_per_mtco2 * crf
        opex_ann_estimate = capex_ann_estimate * (tech_costs['opex_pct_capex'] / 100)

        return {
            'year': year,
            'technology': 'NCC-Electricity',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': ncc_emissions,
            'capex_ann_usd_per_tco2': capex_ann_estimate,  # Estimate only
            'opex_ann_usd_per_tco2': opex_ann_estimate,  # Estimate only
            'fuel_cost_diff_usd_per_tco2': 0.0,  # Not applicable (LCOE method)
            'total_cost_usd_per_tco2': macc_cost,  # LCOE-based
            're_price_usd_per_mwh': re_price,
            'h2_price_usd_per_kg': np.nan,
            'lcoe_baseline_usd_per_ton': lcoe_baseline,
            'lcoe_technology_usd_per_ton': lcoe_elec,
            'lcoe_premium_usd_per_ton': lcoe_premium,
            'emission_intensity_baseline': emission_intensity_baseline,
            'emission_intensity_technology': emission_intensity_elec,
            'methodology': 'LCOE-based'
        }

    def _calculate_re_ppa_macc(self, year, re_price, grid_ef):
        """Calculate RE PPA MACC (NCC facilities only)

        RE PPA = Renewable Power Purchase Agreement
        Simply switching from grid electricity to RE electricity for NCC facilities
        No infrastructure needed - just procurement contract

        User specified: "RE is only applied to NCC"
        """
        tech_costs = self.tech_cost_calc.get_technology_costs('Renewable_Energy', year)

        # Get grid electricity price (convert from $/kWh to $/MWh)
        grid_price_per_kwh = self.df_fuel_prices[
            self.df_fuel_prices['year'] == year
        ]['electricity_usd_per_kwh'].iloc[0]
        grid_price = grid_price_per_kwh * 1000  # $/MWh

        # Filter NCC facilities only (user constraint)
        ncc_facilities = self.df_baseline[
            self.df_baseline['product'].apply(is_ncc_facility)
        ]

        # Calculate total electricity emissions for NCC facilities
        total_elec_emissions_mt = ncc_facilities['emissions_electricity_kt'].sum() / 1000  # MtCO2

        # Emission factors
        re_ef = 0.05  # tCO2/MWh (lifecycle emissions for renewable energy)
        grid_ef_tco2_per_mwh = grid_ef  # tCO2/MWh (from trajectory)

        # Abatement per MWh
        abatement_per_mwh = grid_ef_tco2_per_mwh - re_ef

        # Abatement potential: all NCC electricity could switch to RE
        abatement_potential_mt = total_elec_emissions_mt * (1 - re_ef / grid_ef_tco2_per_mwh)

        # Cost per MWh difference
        price_diff_per_mwh = re_price - grid_price

        # Cost per tCO2 abated
        if abatement_per_mwh > 0:
            cost_per_tco2 = price_diff_per_mwh / abatement_per_mwh
        else:
            cost_per_tco2 = 1e9  # Very high if no abatement

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
            'grid_ef_tco2_per_mwh': grid_ef_tco2_per_mwh,
        }

    def create_visualizations(self):
        """Create MACC curve visualizations"""
        print("\nCreating Creating visualizations...")

        # MACC curves for key years
        key_years = [2025, 2030, 2040, 2050]

        for year in key_years:
            df_year = self.df_macc[
                (self.df_macc['year'] == year) &
                (self.df_macc['available'] == True)
            ].sort_values('total_cost_usd_per_tco2')

            if len(df_year) == 0:
                continue

            fig, ax = plt.subplots(figsize=(12, 7))

            # Sort by cost for proper MACC ordering
            df_year_sorted = df_year.sort_values('total_cost_usd_per_tco2')

            # Create MACC bars - Publication quality
            x_pos = 0
            colors = {'Heat_Pump': '#2ECC71', 'NCC-H2': '#3498DB', 'NCC-Electricity': '#E74C3C', 'RE_PPA': '#F39C12'}
            tech_labels = {
                'Heat_Pump': 'Heat Pump',
                'RE_PPA': 'RE PPA',
                'NCC-Electricity': 'NCC-Electricity (LCOE)',
                'NCC-H2': 'NCC-H2 (LCOE)'
            }

            legend_entries = []

            for _, row in df_year_sorted.iterrows():
                width = row['abatement_potential_mtco2']
                height = row['total_cost_usd_per_tco2']
                color = colors.get(row['technology'], 'gray')
                label = tech_labels.get(row['technology'], row['technology'])

                # Add to legend only once per technology
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

            # Labels and formatting
            ax.set_xlabel('Cumulative Abatement Potential (MtCO2/year)', fontsize=13, fontweight='bold')
            ax.set_ylabel('Marginal Abatement Cost ($/tCO2)', fontsize=13, fontweight='bold')
            ax.set_title(f'Marginal Abatement Cost Curve - {year}', fontsize=15, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y', linestyle='--')

            # Legend positioning
            ax.legend(loc='best', fontsize=10, framealpha=0.95, edgecolor='black')

            # Add subtle background shading
            y_min, y_max = ax.get_ylim()
            if y_min < 0:
                ax.axhspan(y_min, 0, alpha=0.08, color='green', zorder=0)
                ax.text(x_pos * 0.98, min(-20, y_min * 0.95), 'Cost-Saving',
                       fontsize=9, ha='right', va='bottom', style='italic', color='darkgreen')
            if y_max > 0:
                ax.axhspan(0, y_max, alpha=0.05, color='red', zorder=0)

            save_plot(fig, self.output_dir / f'macc_curve_{year}.png')

        # Cost evolution - Publication quality
        fig, ax = plt.subplots(figsize=(12, 7))

        # Technology colors and markers for clarity
        tech_styles = {
            'Heat_Pump': {'color': '#2ECC71', 'marker': 'o', 'label': 'Heat Pump'},
            'RE_PPA': {'color': '#F39C12', 'marker': 's', 'label': 'RE PPA'},
            'NCC-Electricity': {'color': '#E74C3C', 'marker': '^', 'label': 'NCC-Electricity (LCOE)'},
            'NCC-H2': {'color': '#3498DB', 'marker': 'D', 'label': 'NCC-H2 (LCOE)'}
        }

        for tech in ['Heat_Pump', 'RE_PPA', 'NCC-Electricity', 'NCC-H2']:
            df_tech = self.df_macc[self.df_macc['technology'] == tech]
            style = tech_styles[tech]
            ax.plot(df_tech['year'], df_tech['total_cost_usd_per_tco2'],
                   linewidth=2.5, color=style['color'], marker=style['marker'],
                   markersize=6, label=style['label'], alpha=0.9)

        ax.axhline(y=0, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label='Cost Parity')
        ax.set_xlabel('Year', fontsize=13, fontweight='bold')
        ax.set_ylabel('Marginal Abatement Cost ($/tCO2)', fontsize=13, fontweight='bold')
        ax.set_title('Technology Cost Trajectories (2025-2050)', fontsize=15, fontweight='bold')
        ax.legend(loc='best', fontsize=10, framealpha=0.95)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(2024, 2051)

        # Add shaded region for negative costs (profitable)
        ax.fill_between([2024, 2051], -1000, 0, alpha=0.1, color='green', label='_nolegend_')
        ax.text(2048, -50, 'Cost-Saving\nRegion', fontsize=10, ha='right', va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='green'))

        save_plot(fig, self.output_dir / 'cost_evolution_annual.png')

    def save_outputs(self):
        """Save outputs"""
        print("\nSaving Saving outputs...")
        save_csv_output(self.df_macc, self.output_dir / 'macc_annual_2025_2050.csv',
                       f"({len(self.df_macc)} tech-year combinations)")

    def run_complete_analysis(self):
        """Run complete MACC analysis"""
        print("\n" + "="*80)
        print("RUNNING COMPLETE MACC ANALYSIS")
        print("="*80)

        self.calculate_macc_annual()
        self.create_visualizations()
        self.save_outputs()

        print("\n" + "="*80)
        print("- MODULE 2 COMPLETE")
        print("="*80)
        print(f"\nOutputs saved to: {self.output_dir}")

        return {'macc': self.df_macc}
