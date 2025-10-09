#!/usr/bin/env python3
"""
MODULE 1: BASELINE ANALYSIS
Korean Petrochemical Industry - 2025 Baseline with 50-year facility projections

Outputs:
1. Baseline emissions breakdown (2025)
2. Annual BAU trajectory (2025-2075) with natural facility retirement
3. Energy source transitions over time
4. Emissions by product, facility, company, region
5. CSV + PNG for each analysis

Author: Petrochemical MACC Model v2.0
Date: October 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

class BaselineAnalyzer:
    """Analyze baseline emissions and BAU trajectory with facility retirement"""

    def __init__(self, excel_path):
        """Initialize with data from Excel"""
        self.excel_path = excel_path
        self.output_dir = Path('step_01_baseline_analysis/outputs')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("MODULE 1: BASELINE ANALYSIS")
        print("="*80)

        # Load data
        print("\n loading data...")
        self.df_ci = pd.read_excel(excel_path, sheet_name='CI_Corrected')
        self.df_ci2 = pd.read_excel(excel_path, sheet_name='CI2_Corrected')
        self.df_source = pd.read_excel(excel_path, sheet_name='source_Original')
        self.df_grid_trajectory = pd.read_excel(excel_path, sheet_name='Korea_Grid_Emission_Trajectory')

        print(f"   ✓ Loaded {len(self.df_source)} facilities")
        print(f"   ✓ Loaded {len(self.df_ci)} product/process combinations")

        # Facility operational lifetime
        self.facility_lifetime_years = 50

    def calculate_2025_baseline(self):
        """Calculate detailed 2025 baseline emissions"""
        print("\n📊 Calculating 2025 baseline emissions...")

        # Get emission factors
        ef_dict = {
            'naphtha': self.df_ci2['Naphtha_Thermal_tCO2_per_GJ'].iloc[0],
            'electricity': self.df_ci2['Electricity_tCO2_per_kWh'].iloc[0],
            'lng': self.df_ci2['LNG_tCO2_per_GJ'].iloc[0],
            'fuel_gas': self.df_ci2['Fuel_Gas_Mix_tCO2_per_GJ'].iloc[0],
            'byproduct_gas': self.df_ci2['Byproduct_Gas_tCO2_per_GJ'].iloc[0],
            'lpg_propane': self.df_ci2['LPG_Propane_tCO2_per_GJ'].iloc[0],
            'lpg_butane': self.df_ci2['LPG_Butane_tCO2_per_GJ'].iloc[0],
            'fuel_oil': self.df_ci2['Fuel_Oil_tCO2_per_GJ'].iloc[0],
            'diesel': self.df_ci2['Diesel_tCO2_per_GJ'].iloc[0],
        }

        # Calculate emissions for each facility
        facility_emissions = []

        for idx, source_row in self.df_source.iterrows():
            product = source_row['products']
            process = source_row['process']
            company = source_row['company']
            location = source_row['location']
            year_built = source_row['year']
            capacity_kt = source_row['capacity_1000_t']
            capacity_t = capacity_kt * 1000

            # Find matching CI data
            ci_row = self.df_ci[self.df_ci['Product'] == product]
            if len(ci_row) == 0:
                continue
            ci_row = ci_row.iloc[0]

            # Calculate emissions by fuel type (tonnes CO2)
            emissions = {}
            emissions['naphtha'] = capacity_t * ci_row.get('Naphtha_Thermal_GJ_per_t', 0) * ef_dict['naphtha']
            emissions['electricity'] = capacity_t * ci_row.get('Electricity_kWh_per_t', 0) * ef_dict['electricity']
            emissions['lng'] = capacity_t * ci_row.get('LNG_GJ_per_t', 0) * ef_dict['lng']
            emissions['fuel_gas'] = capacity_t * ci_row.get('Fuel_Gas_Mix_GJ_per_t', 0) * ef_dict['fuel_gas']
            emissions['byproduct_gas'] = capacity_t * ci_row.get('Byproduct_Gas_GJ_per_t', 0) * ef_dict['byproduct_gas']
            emissions['lpg'] = (capacity_t * ci_row.get('LPG_Propane_GJ_per_t', 0) * ef_dict['lpg_propane'] +
                              capacity_t * ci_row.get('LPG_Butane_GJ_per_t', 0) * ef_dict['lpg_butane'])
            emissions['fuel_oil'] = capacity_t * ci_row.get('Fuel_Oil_GJ_per_t', 0) * ef_dict['fuel_oil']
            emissions['diesel'] = capacity_t * ci_row.get('Diesel_GJ_per_t', 0) * ef_dict['diesel']

            total_emissions_t = sum(emissions.values())

            facility_emissions.append({
                'product': product,
                'process': process,
                'company': company,
                'location': location,
                'year_built': year_built,
                'retirement_year': year_built + self.facility_lifetime_years,
                'capacity_kt': capacity_kt,
                'emissions_naphtha_kt': emissions['naphtha'] / 1000,
                'emissions_electricity_kt': emissions['electricity'] / 1000,
                'emissions_lng_kt': emissions['lng'] / 1000,
                'emissions_fuel_gas_kt': emissions['fuel_gas'] / 1000,
                'emissions_byproduct_gas_kt': emissions['byproduct_gas'] / 1000,
                'emissions_lpg_kt': emissions['lpg'] / 1000,
                'emissions_fuel_oil_kt': emissions['fuel_oil'] / 1000,
                'emissions_diesel_kt': emissions['diesel'] / 1000,
                'total_emissions_kt': total_emissions_t / 1000,
                'active_2025': True  # All active in baseline
            })

        self.df_facilities = pd.DataFrame(facility_emissions)

        # Summary statistics
        total_emissions_mt = self.df_facilities['total_emissions_kt'].sum() / 1000

        print(f"\n   ✓ Baseline 2025: {total_emissions_mt:.2f} MtCO2")
        print(f"   ✓ Facilities: {len(self.df_facilities)}")
        print(f"   ✓ Total capacity: {self.df_facilities['capacity_kt'].sum():,.0f} kt/year")

        # Save baseline
        baseline_file = self.output_dir / 'baseline_2025_detailed.csv'
        self.df_facilities.to_csv(baseline_file, index=False)
        print(f"   ✓ Saved: {baseline_file}")

        return self.df_facilities

    def project_bau_trajectory(self):
        """Project BAU emissions 2025-2075 with natural facility retirement"""
        print("\n📈 Projecting BAU trajectory with facility retirement...")

        years = range(2025, 2076)  # 2025-2075 (50 years)
        trajectory = []

        for year in years:
            # Filter facilities that are still operational
            active_facilities = self.df_facilities[
                (self.df_facilities['year_built'] <= year) &
                (self.df_facilities['retirement_year'] > year)
            ].copy()

            # Get grid emission factor for this year
            grid_ef = self._get_grid_ef(year)
            baseline_grid_ef = self.df_ci2['Electricity_tCO2_per_kWh'].iloc[0]

            # Adjust electricity emissions based on grid decarbonization
            electricity_scaling = grid_ef / baseline_grid_ef

            # Calculate total emissions
            emissions_by_fuel = {
                'naphtha': active_facilities['emissions_naphtha_kt'].sum(),
                'electricity': active_facilities['emissions_electricity_kt'].sum() * electricity_scaling,
                'lng': active_facilities['emissions_lng_kt'].sum(),
                'fuel_gas': active_facilities['emissions_fuel_gas_kt'].sum(),
                'byproduct_gas': active_facilities['emissions_byproduct_gas_kt'].sum(),
                'lpg': active_facilities['emissions_lpg_kt'].sum(),
                'fuel_oil': active_facilities['emissions_fuel_oil_kt'].sum(),
                'diesel': active_facilities['emissions_diesel_kt'].sum(),
            }

            total_emissions = sum(emissions_by_fuel.values())

            trajectory.append({
                'year': year,
                'total_emissions_mt': total_emissions / 1000,
                'naphtha_mt': emissions_by_fuel['naphtha'] / 1000,
                'electricity_mt': emissions_by_fuel['electricity'] / 1000,
                'lng_mt': emissions_by_fuel['lng'] / 1000,
                'fuel_gas_mt': emissions_by_fuel['fuel_gas'] / 1000,
                'other_fuels_mt': (emissions_by_fuel['byproduct_gas'] + emissions_by_fuel['lpg'] +
                                   emissions_by_fuel['fuel_oil'] + emissions_by_fuel['diesel']) / 1000,
                'active_facilities': len(active_facilities),
                'active_capacity_kt': active_facilities['capacity_kt'].sum(),
                'grid_emission_factor': grid_ef
            })

        self.df_trajectory = pd.DataFrame(trajectory)

        print(f"   ✓ Projected {len(years)} years")
        print(f"   ✓ 2025 emissions: {self.df_trajectory[self.df_trajectory['year']==2025]['total_emissions_mt'].iloc[0]:.2f} MtCO2")
        print(f"   ✓ 2050 emissions: {self.df_trajectory[self.df_trajectory['year']==2050]['total_emissions_mt'].iloc[0]:.2f} MtCO2")
        print(f"   ✓ 2075 emissions: {self.df_trajectory[self.df_trajectory['year']==2075]['total_emissions_mt'].iloc[0]:.2f} MtCO2")

        # Save trajectory
        trajectory_file = self.output_dir / 'bau_trajectory_2025_2075.csv'
        self.df_trajectory.to_csv(trajectory_file, index=False)
        print(f"   ✓ Saved: {trajectory_file}")

        return self.df_trajectory

    def _get_grid_ef(self, year):
        """Get interpolated grid emission factor for any year"""
        if year <= 2025:
            return self.df_grid_trajectory[self.df_grid_trajectory['Year']==2025]['Electricity_tCO2_per_kWh'].iloc[0]
        elif year >= 2050:
            return self.df_grid_trajectory[self.df_grid_trajectory['Year']==2050]['Electricity_tCO2_per_kWh'].iloc[0]
        else:
            # Linear interpolation
            return np.interp(year,
                           self.df_grid_trajectory['Year'],
                           self.df_grid_trajectory['Electricity_tCO2_per_kWh'])

    def analyze_by_category(self):
        """Analyze emissions by product, company, location"""
        print("\n📊 Analyzing by category...")

        # By product
        by_product = self.df_facilities.groupby('product').agg({
            'total_emissions_kt': 'sum',
            'capacity_kt': 'sum',
            'product': 'count'
        }).rename(columns={'product': 'num_facilities'})
        by_product = by_product.sort_values('total_emissions_kt', ascending=False)
        by_product['emissions_mt'] = by_product['total_emissions_kt'] / 1000
        by_product['share_%'] = 100 * by_product['emissions_mt'] / by_product['emissions_mt'].sum()

        # By company
        by_company = self.df_facilities.groupby('company').agg({
            'total_emissions_kt': 'sum',
            'capacity_kt': 'sum',
            'company': 'count'
        }).rename(columns={'company': 'num_facilities'})
        by_company = by_company.sort_values('total_emissions_kt', ascending=False)
        by_company['emissions_mt'] = by_company['total_emissions_kt'] / 1000
        by_company['share_%'] = 100 * by_company['emissions_mt'] / by_company['emissions_mt'].sum()

        # By location
        by_location = self.df_facilities.groupby('location').agg({
            'total_emissions_kt': 'sum',
            'capacity_kt': 'sum',
            'location': 'count'
        }).rename(columns={'location': 'num_facilities'})
        by_location = by_location.sort_values('total_emissions_kt', ascending=False)
        by_location['emissions_mt'] = by_location['total_emissions_kt'] / 1000
        by_location['share_%'] = 100 * by_location['emissions_mt'] / by_location['emissions_mt'].sum()

        # Save
        by_product.to_csv(self.output_dir / 'emissions_by_product.csv')
        by_company.to_csv(self.output_dir / 'emissions_by_company.csv')
        by_location.to_csv(self.output_dir / 'emissions_by_location.csv')

        print(f"   ✓ Top 5 products by emissions:")
        for idx, row in by_product.head(5).iterrows():
            print(f"      {idx}: {row['emissions_mt']:.2f} MtCO2 ({row['share_%']:.1f}%)")

        return by_product, by_company, by_location

    def create_visualizations(self):
        """Create all PNG visualizations"""
        print("\n🎨 Creating visualizations...")

        # 1. BAU Trajectory with fuel breakdown
        self._plot_bau_trajectory()

        # 2. Baseline 2025 breakdown
        self._plot_baseline_breakdown()

        # 3. Energy source transition
        self._plot_energy_transition()

        # 4. Facility retirement schedule
        self._plot_facility_retirement()

        print("   ✓ All visualizations saved")

    def _plot_bau_trajectory(self):
        """Plot BAU emissions trajectory with stacked fuel types"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        # Total emissions
        ax1.plot(self.df_trajectory['year'], self.df_trajectory['total_emissions_mt'],
                linewidth=2.5, color='darkred', label='Total BAU Emissions')
        ax1.fill_between(self.df_trajectory['year'], 0, self.df_trajectory['total_emissions_mt'],
                         alpha=0.2, color='darkred')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Emissions (MtCO2/year)')
        ax1.set_title('Business-as-Usual Emissions Trajectory (2025-2075)\nWith Natural Facility Retirement (50-year lifetime)',
                     fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Stacked by fuel type
        fuels = ['naphtha_mt', 'electricity_mt', 'lng_mt', 'fuel_gas_mt', 'other_fuels_mt']
        labels = ['Naphtha', 'Electricity', 'LNG', 'Fuel Gas', 'Other Fuels']
        colors = ['#8B4513', '#FFD700', '#4169E1', '#32CD32', '#808080']

        ax2.stackplot(self.df_trajectory['year'],
                     *[self.df_trajectory[f] for f in fuels],
                     labels=labels, colors=colors, alpha=0.8)
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Emissions (MtCO2/year)')
        ax2.set_title('Emissions by Fuel Type', fontsize=12, fontweight='bold')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'bau_trajectory_annual.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ bau_trajectory_annual.png")

    def _plot_baseline_breakdown(self):
        """Plot 2025 baseline breakdown by fuel type"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Pie chart
        baseline_2025 = self.df_trajectory[self.df_trajectory['year']==2025].iloc[0]
        fuel_emissions = [
            baseline_2025['naphtha_mt'],
            baseline_2025['electricity_mt'],
            baseline_2025['lng_mt'],
            baseline_2025['fuel_gas_mt'],
            baseline_2025['other_fuels_mt']
        ]
        labels = ['Naphtha', 'Electricity', 'LNG', 'Fuel Gas', 'Other Fuels']
        colors = ['#8B4513', '#FFD700', '#4169E1', '#32CD32', '#808080']

        ax1.pie(fuel_emissions, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 11})
        ax1.set_title('2025 Baseline Emissions by Fuel Type\nTotal: {:.2f} MtCO2'.format(baseline_2025['total_emissions_mt']),
                     fontsize=12, fontweight='bold')

        # Bar chart
        ax2.bar(labels, fuel_emissions, color=colors, alpha=0.7, edgecolor='black')
        ax2.set_ylabel('Emissions (MtCO2/year)')
        ax2.set_title('2025 Baseline Emissions', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        # Add values on bars
        for i, v in enumerate(fuel_emissions):
            ax2.text(i, v + 0.5, f'{v:.1f}', ha='center', fontweight='bold')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'baseline_2025_breakdown.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ baseline_2025_breakdown.png")

    def _plot_energy_transition(self):
        """Plot energy source transition over time"""
        fig, ax = plt.subplots(figsize=(14, 8))

        # Calculate percentages
        df_pct = self.df_trajectory.copy()
        for fuel in ['naphtha_mt', 'electricity_mt', 'lng_mt', 'fuel_gas_mt', 'other_fuels_mt']:
            df_pct[fuel + '_pct'] = 100 * df_pct[fuel] / df_pct['total_emissions_mt']

        # Plot
        fuels = ['naphtha_mt_pct', 'electricity_mt_pct', 'lng_mt_pct', 'fuel_gas_mt_pct', 'other_fuels_mt_pct']
        labels = ['Naphtha', 'Electricity (Grid)', 'LNG', 'Fuel Gas', 'Other Fuels']
        colors = ['#8B4513', '#FFD700', '#4169E1', '#32CD32', '#808080']

        ax.stackplot(df_pct['year'], *[df_pct[f] for f in fuels],
                    labels=labels, colors=colors, alpha=0.8)

        ax.set_xlabel('Year')
        ax.set_ylabel('Share of Total Emissions (%)')
        ax.set_title('Energy Source Transition in BAU Scenario (2025-2075)\nBased on Grid Decarbonization Only',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'energy_source_transition.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ energy_source_transition.png")

    def _plot_facility_retirement(self):
        """Plot facility retirement schedule"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        # Number of active facilities over time
        ax1.plot(self.df_trajectory['year'], self.df_trajectory['active_facilities'],
                linewidth=2.5, color='steelblue', marker='o', markersize=2)
        ax1.fill_between(self.df_trajectory['year'], 0, self.df_trajectory['active_facilities'],
                        alpha=0.2, color='steelblue')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Number of Active Facilities')
        ax1.set_title('Facility Retirement Schedule (50-year operational lifetime)',
                     fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Active capacity over time
        ax2.plot(self.df_trajectory['year'], self.df_trajectory['active_capacity_kt']/1000,
                linewidth=2.5, color='darkgreen', marker='o', markersize=2)
        ax2.fill_between(self.df_trajectory['year'], 0, self.df_trajectory['active_capacity_kt']/1000,
                        alpha=0.2, color='darkgreen')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Active Capacity (Mt/year)')
        ax2.set_title('Production Capacity Over Time', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'facility_retirement_schedule.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ facility_retirement_schedule.png")

    def run_complete_analysis(self):
        """Run all baseline analyses"""
        print("\n" + "="*80)
        print("RUNNING COMPLETE BASELINE ANALYSIS")
        print("="*80)

        # 1. Calculate baseline
        self.calculate_2025_baseline()

        # 2. Project BAU trajectory
        self.project_bau_trajectory()

        # 3. Analyze by category
        self.analyze_by_category()

        # 4. Create visualizations
        self.create_visualizations()

        print("\n" + "="*80)
        print("✓ MODULE 1 COMPLETE")
        print("="*80)
        print(f"\nOutputs saved to: {self.output_dir}")
        print("\nGenerated files:")
        for f in sorted(self.output_dir.glob('*')):
            print(f"   - {f.name}")


if __name__ == '__main__':
    # Run analysis
    analyzer = BaselineAnalyzer('data_sources/Korean_Petrochemical_MACC_Model_English.xlsx')
    analyzer.run_complete_analysis()

    print("\n🎉 Baseline analysis complete!")
