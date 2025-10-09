#!/usr/bin/env python3
"""
MODULE 2: DYNAMIC MACC ANALYSIS
Korean Petrochemical Industry - Marginal Abatement Cost Curves

Features:
- Dynamic MACC calculation based on:
  * Technology capex/opex (from database)
  * Fuel prices (H2, RE electricity) over time
  * Baseline emissions avoided
- Annual MACCs for each year 2025-2050
- Technology-specific abatement potential
- CSV + PNG outputs

Author: Petrochemical MACC Model v2.0
Date: October 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

class MACCAnalyzer:
    """Dynamic Marginal Abatement Cost Curve analysis"""

    def __init__(self, excel_path):
        """Initialize with data from Excel"""
        self.excel_path = excel_path
        self.output_dir = Path('step_02_macc_analysis/outputs')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("MODULE 2: DYNAMIC MACC ANALYSIS")
        print("="*80)

        # Load data
        print("\n📁 Loading data...")
        self.df_baseline = pd.read_csv('step_01_baseline_analysis/outputs/baseline_2025_detailed.csv')
        self.df_tech_costs = pd.read_excel(excel_path, sheet_name='Technology_Costs_All')
        self.df_h2_prices = pd.read_excel(excel_path, sheet_name='H2_Price_Trajectory')
        self.df_re_prices = pd.read_excel(excel_path, sheet_name='RE_Price_Trajectory')
        self.df_hp_applicability = pd.read_excel(excel_path, sheet_name='Heat_Pump_Applicability')
        self.df_ci = pd.read_excel(excel_path, sheet_name='CI_Corrected')
        self.df_source = pd.read_excel(excel_path, sheet_name='source_Original')

        print(f"   ✓ Loaded baseline emissions: {self.df_baseline['total_emissions_kt'].sum()/1000:.2f} MtCO2")
        print(f"   ✓ Loaded {len(self.df_tech_costs)} technology cost entries")

        # Discount rate for annualization
        self.discount_rate = 0.08  # 8%
        self.tech_lifetime = 20  # years

        # Product grouping for heat pump applicability
        self.product_groups = {
            'Olefins': ['Ethylene', 'Propylene', 'Butadiene', 'C-H'],
            'Aromatics': ['Benzene', 'Toluene', 'Xylene', 'O-X', 'M-X', 'P-X'],
            'Polymers': ['HDPE', 'LDPE', 'L-LDPE', 'PP', 'PS', 'PVC', 'EPS', 'ABS'],
            'Intermediates': ['EG', 'TPA', 'EDC', 'VCM', 'SM'],
            'Rubber': ['SBR', 'S-SBR', 'BR', 'NBR', 'EPDM'],
            'Specialty': ['Acetic Acid', 'Phenol', 'Acetone', 'TDI', 'MDI']
        }

    def calculate_annual_macc(self, year):
        """Calculate MACC for a specific year"""

        # Get technology costs for this year
        tech_costs_year = self._interpolate_tech_costs(year)

        # Get fuel prices for this year
        h2_price = self._interpolate_h2_price(year)
        re_price = self._interpolate_re_price(year)

        # Calculate abatement cost for each technology
        macc_data = []

        # 1. Heat Pumps
        hp_result = self._calculate_heat_pump_macc(year, tech_costs_year, re_price)
        if hp_result:
            macc_data.append(hp_result)

        # 2. NCC-H2
        ncc_h2_result = self._calculate_ncc_h2_macc(year, tech_costs_year, h2_price)
        if ncc_h2_result:
            macc_data.append(ncc_h2_result)

        # 3. NCC-Electricity
        ncc_elec_result = self._calculate_ncc_electricity_macc(year, tech_costs_year, re_price)
        if ncc_elec_result:
            macc_data.append(ncc_elec_result)

        # Note: Biomass/bio-naphtha removed per user request
        # Only 3 technologies: Heat Pumps, NCC-H2, NCC-Electricity

        return pd.DataFrame(macc_data)

    def _calculate_heat_pump_macc(self, year, tech_costs, re_price_mwh):
        """Calculate MACC for industrial heat pumps"""

        # Get heat pump costs
        hp_costs = tech_costs[tech_costs['Technology'] == 'Heat_Pump']
        if len(hp_costs) == 0:
            return None
        hp_costs = hp_costs.iloc[0]

        # Annualized capex
        crf = self.discount_rate / (1 - (1 + self.discount_rate)**(-self.tech_lifetime))
        annual_capex_per_tco2 = hp_costs['Capex_USD_per_tCO2_abated'] * crf

        # Fixed opex
        annual_opex_per_tco2 = hp_costs['Opex_Fixed_USD_per_tCO2_per_year']

        # Variable cost (electricity for heat pump vs baseline fossil fuel)
        # Heat pump COP = 4.0, baseline naphtha at 0.0149 tCO2/GJ
        # For every GJ of heat needed:
        # - Baseline: burn naphtha → cost = naphtha_price/GJ
        # - Heat pump: use elec/COP → cost = electricity_price/COP per GJ thermal
        cop = 4.0
        naphtha_cost_per_gj = 15.0  # $/GJ for naphtha
        electricity_cost_per_gj_thermal = (re_price_mwh / 3.6) / cop  # $/GJ thermal output

        # Per tCO2 abated: need to replace ~67 GJ of naphtha
        gj_per_tco2 = 1 / 0.0149  # ~67 GJ per tCO2 at 0.0149 tCO2/GJ

        # Fuel cost differential = (new fuel cost - old fuel cost) per tCO2
        fuel_cost_diff = (electricity_cost_per_gj_thermal - naphtha_cost_per_gj) * gj_per_tco2

        # Total abatement cost
        total_cost = annual_capex_per_tco2 + annual_opex_per_tco2 + fuel_cost_diff

        # Abatement potential - calculate from facilities
        # Heat pumps can replace 10-60% of thermal energy depending on product
        total_abatement_kt = 0

        for _, facility in self.df_baseline.iterrows():
            product = facility['product']

            # Find product group
            hp_applicable_pct = 0
            for group, products in self.product_groups.items():
                if product in products:
                    # Get applicability from database
                    hp_row = self.df_hp_applicability[
                        self.df_hp_applicability['Product_Group'].str.contains(group.split('(')[0].strip(), na=False)
                    ]
                    if len(hp_row) > 0:
                        hp_applicable_pct = hp_row.iloc[0]['Heat_Pump_Applicable_%'] / 100
                    break

            if hp_applicable_pct > 0:
                # Heat pump can replace this fraction of thermal energy
                facility_thermal_emissions = facility['emissions_naphtha_kt']
                abatement = facility_thermal_emissions * hp_applicable_pct * (hp_costs['Emission_Reduction_%'] / 100)
                total_abatement_kt += abatement

        if total_abatement_kt < 0.01:  # Minimum threshold
            return None

        return {
            'technology': 'Heat_Pump',
            'year': year,
            'capex_ann_usd_per_tco2': annual_capex_per_tco2,
            'opex_usd_per_tco2': annual_opex_per_tco2,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff,
            'total_cost_usd_per_tco2': total_cost,
            'abatement_potential_mtco2': total_abatement_kt / 1000,
            'trl': hp_costs.get('TRL_2025', 9),
            'available': year >= hp_costs.get('Commercial_Availability', 2025)
        }

    def _calculate_ncc_h2_macc(self, year, tech_costs, h2_price_kg):
        """Calculate MACC for NCC-H2 (hydrogen crackers)"""

        # Get NCC-H2 costs
        ncc_h2 = tech_costs[tech_costs['Technology'] == 'NCC-H2']
        if len(ncc_h2) == 0:
            return None
        ncc_h2 = ncc_h2.iloc[0]

        # Annualized capex
        crf = self.discount_rate / (1 - (1 + self.discount_rate)**(-self.tech_lifetime))
        annual_capex_per_tco2 = ncc_h2['Capex_USD_per_tCO2_abated'] * crf

        # Fixed opex
        annual_opex_per_tco2 = ncc_h2['Opex_Fixed_USD_per_tCO2_per_year']

        # Fuel cost differential: H2 vs naphtha
        # H2: 1.25 kg H2 per kg naphtha replaced (energy basis)
        # Naphtha cost: ~$600/tonne = $0.60/kg
        # For 1 tCO2 abated at 0.0149 tCO2/GJ:
        naphtha_cost_per_kg = 0.60
        gj_per_tco2 = 1 / 0.0149
        kg_naphtha_per_tco2 = gj_per_tco2 / 43.5  # naphtha heating value

        h2_needed_kg = kg_naphtha_per_tco2 * 1.25
        fuel_cost_diff = h2_needed_kg * h2_price_kg - kg_naphtha_per_tco2 * naphtha_cost_per_kg

        # Total cost
        total_cost = annual_capex_per_tco2 + annual_opex_per_tco2 + fuel_cost_diff

        # Abatement potential - all naphtha cracker emissions
        cracker_products = ['Ethylene', 'Propylene', 'Butadiene', 'C-H']
        total_abatement_kt = 0

        for product in cracker_products:
            product_emissions = self.df_baseline[self.df_baseline['product'] == product]['emissions_naphtha_kt'].sum()
            total_abatement_kt += product_emissions * (ncc_h2['Emission_Reduction_%'] / 100)

        if total_abatement_kt < 0.01:
            return None

        return {
            'technology': 'NCC-H2',
            'year': year,
            'capex_ann_usd_per_tco2': annual_capex_per_tco2,
            'opex_usd_per_tco2': annual_opex_per_tco2,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff,
            'total_cost_usd_per_tco2': total_cost,
            'abatement_potential_mtco2': total_abatement_kt / 1000,
            'trl': ncc_h2.get('TRL_2025', 7),
            'available': year >= ncc_h2.get('Commercial_Availability', 2028)
        }

    def _calculate_ncc_electricity_macc(self, year, tech_costs, re_price_mwh):
        """Calculate MACC for NCC-Electricity (electric crackers)"""

        # Get NCC-Electricity costs
        ncc_elec = tech_costs[tech_costs['Technology'] == 'NCC-Electricity']
        if len(ncc_elec) == 0:
            return None
        ncc_elec = ncc_elec.iloc[0]

        # Annualized capex
        crf = self.discount_rate / (1 - (1 + self.discount_rate)**(-self.tech_lifetime))
        annual_capex_per_tco2 = ncc_elec['Capex_USD_per_tCO2_abated'] * crf

        # Fixed opex
        annual_opex_per_tco2 = ncc_elec['Opex_Fixed_USD_per_tCO2_per_year']

        # Fuel cost: electricity vs naphtha
        # Electric cracker: ~6500 kWh/t ethylene (direct heating)
        # Per tCO2 abated:
        gj_per_tco2 = 1 / 0.0149
        kg_naphtha_per_tco2 = gj_per_tco2 / 43.5
        kwh_per_tco2 = 6500 * (kg_naphtha_per_tco2 / 1000)  # Scale by naphtha

        naphtha_cost_per_kg = 0.60
        electricity_cost = (kwh_per_tco2 / 1000) * re_price_mwh
        naphtha_cost = kg_naphtha_per_tco2 * naphtha_cost_per_kg

        fuel_cost_diff = electricity_cost - naphtha_cost

        # Total cost
        total_cost = annual_capex_per_tco2 + annual_opex_per_tco2 + fuel_cost_diff

        # Abatement potential - same as NCC-H2
        cracker_products = ['Ethylene', 'Propylene', 'Butadiene', 'C-H']
        total_abatement_kt = 0

        for product in cracker_products:
            product_emissions = self.df_baseline[self.df_baseline['product'] == product]['emissions_naphtha_kt'].sum()
            total_abatement_kt += product_emissions * (ncc_elec['Emission_Reduction_%'] / 100)

        if total_abatement_kt < 0.01:
            return None

        return {
            'technology': 'NCC-Electricity',
            'year': year,
            'capex_ann_usd_per_tco2': annual_capex_per_tco2,
            'opex_usd_per_tco2': annual_opex_per_tco2,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff,
            'total_cost_usd_per_tco2': total_cost,
            'abatement_potential_mtco2': total_abatement_kt / 1000,
            'trl': ncc_elec.get('TRL_2025', 5),
            'available': year >= ncc_elec.get('Commercial_Availability', 2033)
        }

    def _calculate_bio_switching_macc(self, year, tech_costs):
        """Calculate MACC for bio-naphtha fuel switching"""

        # Get bio-switching costs
        bio = tech_costs[tech_costs['Technology'] == 'Fuel_Switching_Biomass']
        if len(bio) == 0:
            return None
        bio = bio.iloc[0]

        # Annualized capex (minimal - just infrastructure)
        crf = self.discount_rate / (1 - (1 + self.discount_rate)**(-self.tech_lifetime))
        annual_capex_per_tco2 = bio['Capex_USD_per_tCO2_abated'] * crf

        # Fixed opex
        annual_opex_per_tco2 = bio['Opex_Fixed_USD_per_tCO2_per_year']

        # Fuel cost premium: bio-naphtha vs fossil naphtha
        bio_premium_per_kg = 0.30  # $0.30/kg premium for bio-naphtha
        gj_per_tco2 = 1 / 0.0149
        kg_naphtha_per_tco2 = gj_per_tco2 / 43.5

        fuel_cost_diff = kg_naphtha_per_tco2 * bio_premium_per_kg

        # Total cost
        total_cost = annual_capex_per_tco2 + annual_opex_per_tco2 + fuel_cost_diff

        # Abatement potential - all naphtha thermal emissions
        total_abatement_kt = self.df_baseline['emissions_naphtha_kt'].sum() * (bio['Emission_Reduction_%'] / 100)

        if total_abatement_kt < 0.01:
            return None

        return {
            'technology': 'Fuel_Switching_Biomass',
            'year': year,
            'capex_ann_usd_per_tco2': annual_capex_per_tco2,
            'opex_usd_per_tco2': annual_opex_per_tco2,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff,
            'total_cost_usd_per_tco2': total_cost,
            'abatement_potential_mtco2': total_abatement_kt / 1000,
            'trl': bio.get('TRL_2025', 8),
            'available': year >= bio.get('Commercial_Availability', 2025)
        }

    def _interpolate_tech_costs(self, year):
        """Interpolate technology costs for any year"""
        available_years = sorted(self.df_tech_costs['Year'].unique())

        if year <= available_years[0]:
            return self.df_tech_costs[self.df_tech_costs['Year'] == available_years[0]].copy()
        elif year >= available_years[-1]:
            return self.df_tech_costs[self.df_tech_costs['Year'] == available_years[-1]].copy()
        else:
            # Linear interpolation
            technologies = self.df_tech_costs['Technology'].unique()
            interpolated = []

            for tech in technologies:
                tech_data = self.df_tech_costs[self.df_tech_costs['Technology'] == tech].sort_values('Year')

                capex = np.interp(year, tech_data['Year'], tech_data['Capex_USD_per_tCO2_abated'])
                opex = np.interp(year, tech_data['Year'], tech_data['Opex_Fixed_USD_per_tCO2_per_year'])

                interpolated.append({
                    'Technology': tech,
                    'Year': year,
                    'Capex_USD_per_tCO2_abated': capex,
                    'Opex_Fixed_USD_per_tCO2_per_year': opex,
                    'Emission_Reduction_%': tech_data.iloc[0]['Emission_Reduction_%'],
                    'TRL_2025': tech_data.iloc[0].get('TRL_2025', 7),
                    'Commercial_Availability': tech_data.iloc[0].get('Commercial_Availability', 2025)
                })

            return pd.DataFrame(interpolated)

    def _interpolate_h2_price(self, year):
        """Get interpolated H2 price for any year"""
        return np.interp(year,
                        self.df_h2_prices['Year'],
                        self.df_h2_prices['Green_H2_USD_per_kg'])

    def _interpolate_re_price(self, year):
        """Get interpolated RE electricity price for any year"""
        return np.interp(year,
                        self.df_re_prices['Year'],
                        self.df_re_prices['Average_RE_LCOE_USD_per_MWh'])

    def generate_annual_maccs(self):
        """Generate MACC for every year 2025-2050"""
        print("\n📊 Generating annual MACC curves (2025-2050)...")

        all_maccs = []

        for year in range(2025, 2051):
            macc_year = self.calculate_annual_macc(year)
            if macc_year is not None and len(macc_year) > 0:
                all_maccs.append(macc_year)

        self.df_all_maccs = pd.concat(all_maccs, ignore_index=True)

        # Save
        output_file = self.output_dir / 'macc_annual_2025_2050.csv'
        self.df_all_maccs.to_csv(output_file, index=False)

        print(f"   ✓ Generated MACCs for {len(range(2025, 2051))} years")
        print(f"   ✓ Saved: {output_file}")

        return self.df_all_maccs

    def create_macc_visualizations(self):
        """Create MACC curve visualizations"""
        print("\n🎨 Creating MACC visualizations...")

        # Select key years for detailed MACC curves
        key_years = [2025, 2030, 2040, 2050]

        for year in key_years:
            self._plot_macc_curve(year)

        # Plot cost evolution over time
        self._plot_cost_evolution()

        # Plot abatement potential over time
        self._plot_abatement_potential()

        print("   ✓ All MACC visualizations created")

    def _plot_macc_curve(self, year):
        """Plot MACC curve for a specific year"""
        macc_year = self.df_all_maccs[self.df_all_maccs['year'] == year].copy()

        if len(macc_year) == 0:
            return

        # Sort by cost
        macc_year = macc_year.sort_values('total_cost_usd_per_tco2')

        # Calculate cumulative abatement
        macc_year['cumulative_abatement_mtco2'] = macc_year['abatement_potential_mtco2'].cumsum()

        # Plot
        fig, ax = plt.subplots(figsize=(14, 8))

        colors = {'Heat_Pump': '#2ECC71', 'NCC-H2': '#3498DB',
                 'NCC-Electricity': '#E74C3C', 'Fuel_Switching_Biomass': '#F39C12'}

        x_prev = 0
        for idx, row in macc_year.iterrows():
            color = colors.get(row['technology'], '#95A5A6')
            width = row['abatement_potential_mtco2']
            height = row['total_cost_usd_per_tco2']

            # Draw bar
            ax.bar(x_prev + width/2, height, width=width,
                  color=color, edgecolor='black', linewidth=1.5,
                  label=row['technology'], alpha=0.8)

            # Add cost breakdown annotation
            if row['available']:
                ax.text(x_prev + width/2, height + 5,
                       f"${height:.0f}/tCO2",
                       ha='center', fontsize=8, fontweight='bold')
            else:
                # Not yet available - show dashed
                ax.bar(x_prev + width/2, height, width=width,
                      fill=False, edgecolor=color, linewidth=2,
                      linestyle='--', alpha=0.5)
                ax.text(x_prev + width/2, height/2,
                       'Not\nAvailable',
                       ha='center', va='center', fontsize=8, style='italic')

            x_prev += width

        ax.set_xlabel('Cumulative Abatement Potential (MtCO2/year)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Abatement Cost (USD/tCO2)', fontsize=12, fontweight='bold')
        ax.set_title(f'Marginal Abatement Cost Curve - {year}\nDynamic Costs Based on Technology & Fuel Prices',
                    fontsize=14, fontweight='bold')

        # Remove duplicate labels
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper left')

        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

        plt.tight_layout()
        plt.savefig(self.output_dir / f'macc_curve_{year}.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"   ✓ macc_curve_{year}.png")

    def _plot_cost_evolution(self):
        """Plot how abatement costs evolve over time for each technology"""
        fig, ax = plt.subplots(figsize=(14, 8))

        technologies = self.df_all_maccs['technology'].unique()
        colors = {'Heat_Pump': '#2ECC71', 'NCC-H2': '#3498DB',
                 'NCC-Electricity': '#E74C3C', 'Fuel_Switching_Biomass': '#F39C12'}

        for tech in technologies:
            tech_data = self.df_all_maccs[self.df_all_maccs['technology'] == tech].sort_values('year')
            ax.plot(tech_data['year'], tech_data['total_cost_usd_per_tco2'],
                   marker='o', linewidth=2.5, label=tech, color=colors.get(tech, '#95A5A6'))

        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Abatement Cost (USD/tCO2)', fontsize=12, fontweight='bold')
        ax.set_title('Technology Abatement Cost Evolution (2025-2050)\nDynamic Costs: Capex + Opex + Fuel Cost Differential',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'cost_evolution_annual.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ cost_evolution_annual.png")

    def _plot_abatement_potential(self):
        """Plot total abatement potential over time"""
        fig, ax = plt.subplots(figsize=(14, 8))

        # Get total potential by year
        potential_by_year = self.df_all_maccs.groupby('year')['abatement_potential_mtco2'].sum().reset_index()

        # Also show by technology (stacked)
        pivot_data = self.df_all_maccs.pivot_table(
            index='year',
            columns='technology',
            values='abatement_potential_mtco2',
            aggfunc='sum',
            fill_value=0
        )

        colors = {'Heat_Pump': '#2ECC71', 'NCC-H2': '#3498DB',
                 'NCC-Electricity': '#E74C3C', 'Fuel_Switching_Biomass': '#F39C12'}

        pivot_data.plot(kind='area', stacked=True, ax=ax,
                       color=[colors.get(col, '#95A5A6') for col in pivot_data.columns],
                       alpha=0.8)

        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Abatement Potential (MtCO2/year)', fontsize=12, fontweight='bold')
        ax.set_title('Total Abatement Potential by Technology (2025-2050)',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'abatement_potential_annual.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ abatement_potential_annual.png")

    def run_complete_analysis(self):
        """Run complete MACC analysis"""
        print("\n" + "="*80)
        print("RUNNING COMPLETE MACC ANALYSIS")
        print("="*80)

        # Generate annual MACCs
        self.generate_annual_maccs()

        # Create visualizations
        self.create_macc_visualizations()

        print("\n" + "="*80)
        print("✓ MODULE 2 COMPLETE")
        print("="*80)
        print(f"\nOutputs saved to: {self.output_dir}")
        print("\nGenerated files:")
        for f in sorted(self.output_dir.glob('*')):
            print(f"   - {f.name}")


if __name__ == '__main__':
    # Run analysis
    analyzer = MACCAnalyzer('data_sources/Korean_Petrochemical_MACC_Model_English.xlsx')
    analyzer.run_complete_analysis()

    print("\n🎉 Dynamic MACC analysis complete!")
