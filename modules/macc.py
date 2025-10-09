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
        print("\n📁 Loading data...")
        loader = DataLoader(data_dir)

        self.df_baseline = pd.read_csv(self.baseline_dir / 'baseline_2025_detailed.csv')
        self.df_tech_params = loader.load_technology_params()
        self.df_h2_prices = loader.load_h2_prices()
        self.df_re_prices = loader.load_re_prices()
        self.df_hp_applicability = loader.load_heat_pump_applicability()
        self.df_fuel_prices = pd.read_csv(self.data_dir / 'fuel_price_trajectory.csv')

        print(f"   ✓ Loaded baseline: {len(self.df_baseline)} facilities")
        print(f"   ✓ Loaded {len(self.df_tech_params)} technologies")

        # Initialize calculators
        self.tech_cost_calc = TechnologyCostCalculator(self.df_tech_params)
        self.price_calc = PriceCalculator(self.df_h2_prices, self.df_re_prices, self.df_fuel_prices)

        # Constants
        self.discount_rate = 0.08
        self.ef_naphtha = 0.0149  # tCO2/GJ

    def calculate_macc_annual(self, years=range(2025, 2051)):
        """Calculate MACC for all technologies and years"""
        print(f"\n📊 Calculating dynamic MACC ({min(years)}-{max(years)})...")

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

        df_macc = pd.DataFrame(macc_data)

        print(f"   ✓ Calculated {len(df_macc)} technology-year combinations")

        self.df_macc = df_macc
        return df_macc

    def _calculate_heat_pump_macc(self, year, h2_price, re_price, naphtha_price):
        """Calculate heat pump MACC"""
        tech_costs = self.tech_cost_calc.get_technology_costs('Heat_Pump', year)

        # Abatement potential
        potential_mt = 0
        for _, row in self.df_hp_applicability.iterrows():
            product_group = row['product_group']
            applicability = row['applicability_pct'] / 100

            # Get emissions for this product group
            group_emissions = self.df_baseline[
                self.df_baseline['product_group'] == product_group
            ]['emissions_naphtha_kt'].sum() / 1000  # MtCO2

            potential_mt += group_emissions * applicability

        # Costs
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        crf = self.price_calc.calculate_capital_recovery_factor(self.discount_rate, lifetime)
        capex_ann = capex_musd_per_mtco2 * crf * 1e6  # $/tCO2

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
        """Calculate NCC-H2 MACC"""
        tech_costs = self.tech_cost_calc.get_technology_costs('NCC-H2', year)

        # Abatement potential (NCC emissions only)
        ncc_emissions = self.df_baseline[
            self.df_baseline['product'].apply(is_ncc_facility)
        ]['emissions_naphtha_kt'].sum() / 1000  # MtCO2

        # Costs
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        crf = self.price_calc.calculate_capital_recovery_factor(self.discount_rate, lifetime)
        capex_ann = capex_musd_per_mtco2 * crf * 1e6

        opex_ann = capex_ann * (tech_costs['opex_pct_capex'] / 100)

        # Fuel cost differential (H2 vs naphtha)
        # 1 GJ naphtha = 0.033 kg H2 (energy equivalent, roughly 120 MJ/kg)
        gj_per_tco2 = 1 / self.ef_naphtha
        kg_h2_per_tco2 = gj_per_tco2 / 120 * 1000  # Rough conversion
        h2_cost_per_tco2 = kg_h2_per_tco2 * h2_price
        naphtha_cost_per_tco2 = gj_per_tco2 * naphtha_price
        fuel_cost_diff = h2_cost_per_tco2 - naphtha_cost_per_tco2

        total_cost = capex_ann + opex_ann + fuel_cost_diff

        return {
            'year': year,
            'technology': 'NCC-H2',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': ncc_emissions,
            'capex_ann_usd_per_tco2': capex_ann,
            'opex_ann_usd_per_tco2': opex_ann,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff,
            'total_cost_usd_per_tco2': total_cost,
            're_price_usd_per_mwh': np.nan,
            'h2_price_usd_per_kg': h2_price,
        }

    def _calculate_ncc_electricity_macc(self, year, re_price, naphtha_price):
        """Calculate NCC-Electricity MACC"""
        tech_costs = self.tech_cost_calc.get_technology_costs('NCC-Electricity', year)

        # Abatement potential
        ncc_emissions = self.df_baseline[
            self.df_baseline['product'].apply(is_ncc_facility)
        ]['emissions_naphtha_kt'].sum() / 1000

        # Costs
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        crf = self.price_calc.calculate_capital_recovery_factor(self.discount_rate, lifetime)
        capex_ann = capex_musd_per_mtco2 * crf * 1e6

        opex_ann = capex_ann * (tech_costs['opex_pct_capex'] / 100)

        # Fuel cost differential (RE electricity vs naphtha)
        gj_per_tco2 = 1 / self.ef_naphtha
        electricity_cost_per_tco2 = (re_price / 3.6) * gj_per_tco2  # 1 GJ = 277.8 kWh
        naphtha_cost_per_tco2 = gj_per_tco2 * naphtha_price
        fuel_cost_diff = electricity_cost_per_tco2 - naphtha_cost_per_tco2

        total_cost = capex_ann + opex_ann + fuel_cost_diff

        return {
            'year': year,
            'technology': 'NCC-Electricity',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': ncc_emissions,
            'capex_ann_usd_per_tco2': capex_ann,
            'opex_ann_usd_per_tco2': opex_ann,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff,
            'total_cost_usd_per_tco2': total_cost,
            're_price_usd_per_mwh': re_price,
            'h2_price_usd_per_kg': np.nan,
        }

    def create_visualizations(self):
        """Create MACC curve visualizations"""
        print("\n🎨 Creating visualizations...")

        # MACC curves for key years
        key_years = [2025, 2030, 2040, 2050]

        for year in key_years:
            df_year = self.df_macc[
                (self.df_macc['year'] == year) &
                (self.df_macc['available'] == True)
            ].sort_values('total_cost_usd_per_tco2')

            if len(df_year) == 0:
                continue

            fig, ax = plt.subplots(figsize=(14, 8))

            # Create MACC bars
            x_pos = 0
            colors = {'Heat_Pump': '#2ECC71', 'NCC-H2': '#3498DB', 'NCC-Electricity': '#E74C3C'}

            for _, row in df_year.iterrows():
                width = row['abatement_potential_mtco2']
                height = row['total_cost_usd_per_tco2']
                color = colors.get(row['technology'], 'gray')

                ax.bar(x_pos + width/2, height, width=width, color=color,
                      edgecolor='black', linewidth=1, alpha=0.8,
                      label=row['technology'] if x_pos == 0 or row['technology'] not in [t['technology'] for t in df_year.iloc[:df_year.index.get_loc(row.name)].to_dict('records')] else "")

                x_pos += width

            ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
            ax.set_xlabel('Cumulative Abatement Potential (MtCO2/year)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Marginal Abatement Cost ($/tCO2)', fontsize=12, fontweight='bold')
            ax.set_title(f'Dynamic MACC Curve - {year}', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')

            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), loc='upper left')

            save_plot(fig, self.output_dir / f'macc_curve_{year}.png')

        # Cost evolution
        fig, ax = plt.subplots(figsize=(14, 8))
        for tech in ['Heat_Pump', 'NCC-H2', 'NCC-Electricity']:
            df_tech = self.df_macc[self.df_macc['technology'] == tech]
            ax.plot(df_tech['year'], df_tech['total_cost_usd_per_tco2'],
                   linewidth=2.5, label=tech, marker='o', markersize=4)

        ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Cost ($/tCO2)', fontsize=12, fontweight='bold')
        ax.set_title('Technology Cost Evolution (2025-2050)', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        save_plot(fig, self.output_dir / 'cost_evolution_annual.png')

    def save_outputs(self):
        """Save outputs"""
        print("\n💾 Saving outputs...")
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
        print("✓ MODULE 2 COMPLETE")
        print("="*80)
        print(f"\nOutputs saved to: {self.output_dir}")

        return {'macc': self.df_macc}
