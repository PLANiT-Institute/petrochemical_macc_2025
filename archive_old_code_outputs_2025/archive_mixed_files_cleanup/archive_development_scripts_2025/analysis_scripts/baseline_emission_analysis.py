#!/usr/bin/env python3
"""
Baseline Emission Analysis for Korean Petrochemical Industry MACC Model

This is Part 1 of the comprehensive MACC analysis:
1. BASIC ANALYSIS (this module):
   - Baseline emission source analysis
   - Business-as-usual (BAU) emission projections
   - Current energy mix and emission patterns

2. OPTIMIZATION MODEL (separate module):
   - Technology deployment scenarios
   - Cost-optimal pathways
   - Policy scenario analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class BaselineEmissionAnalysis:
    def __init__(self, data_path="../data/Korean_Petrochemical_MACC_Model_English.xlsx"):
        """Initialize baseline emission analysis"""
        self.data_path = data_path
        self.output_dir = Path("../outputs/baseline_analysis")
        self.output_dir.mkdir(exist_ok=True)

        print("🏭 KOREAN PETROCHEMICAL BASELINE EMISSION ANALYSIS")
        print("=" * 80)
        print("📊 Part 1: Business-as-Usual (BAU) Analysis")
        print("🎯 Foundation for MACC Optimization Model")
        print()

    def load_baseline_data(self):
        """Load all baseline data from Excel"""
        print("📁 Loading baseline data...")

        self.source_df = pd.read_excel(self.data_path, sheet_name='source_Original')
        self.ci_df = pd.read_excel(self.data_path, sheet_name='CI_Corrected')
        self.utilities_df = pd.read_excel(self.data_path, sheet_name='utilities_Original')

        print(f"✅ Facilities: {len(self.source_df)} records")
        print(f"✅ Carbon Intensity: {len(self.ci_df)} records")
        print(f"✅ Utilities: {len(self.utilities_df)} records")

        return self

    def calculate_baseline_emissions(self):
        """Calculate baseline emissions by energy source"""
        print("\n💨 Calculating baseline emissions...")

        # Merge source data with carbon intensity
        self.merged_df = self.source_df.merge(
            self.ci_df,
            left_on=['products', 'process'],
            right_on=['Product', 'Process'],
            how='left'
        )

        # Energy sources and emission factors
        self.energy_sources = {
            'Naphtha_Feedstock': {'intensity_col': 'Naphtha_Feedstock_GJ_per_t', 'ef': 70.5},
            'Naphtha_Thermal': {'intensity_col': 'Naphtha_Thermal_GJ_per_t', 'ef': 70.5},
            'LNG': {'intensity_col': 'LNG_GJ_per_t', 'ef': 56.1},
            'LPG_Propane': {'intensity_col': 'LPG_Propane_GJ_per_t', 'ef': 63.1},
            'LPG_Butane': {'intensity_col': 'LPG_Butane_GJ_per_t', 'ef': 64.2},
            'Fuel_Gas_Mix': {'intensity_col': 'Fuel_Gas_Mix_GJ_per_t', 'ef': 60.0},
            'Electricity': {'intensity_col': 'Electricity_kWh_per_t', 'ef': 466.0}
        }

        # Convert capacity to tonnes
        self.merged_df['capacity_t'] = self.merged_df['capacity_1000_t'] * 1000

        # Calculate energy consumption and emissions for each energy source
        self.energy_consumption_gj = {}  # Store total energy consumption in GJ

        for source, config in self.energy_sources.items():
            intensity_col = config['intensity_col']
            ef = config['ef']

            if intensity_col in self.merged_df.columns:
                if source == 'Electricity':
                    # Convert kWh to GJ (1 kWh = 0.0036 GJ)
                    energy_gj = self.merged_df[intensity_col] * self.merged_df['capacity_t'] * 0.0036
                else:
                    energy_gj = self.merged_df[intensity_col] * self.merged_df['capacity_t']

                # Store energy consumption in GJ
                self.energy_consumption_gj[source] = energy_gj.sum()

                # Calculate emissions (kg CO2)
                self.merged_df[f'{source}_emissions_t_CO2'] = (energy_gj * ef) / 1000
            else:
                self.energy_consumption_gj[source] = 0

        # Aggregate by major energy categories
        self.energy_categories = {
            'Naphtha': ['Naphtha_Feedstock_emissions_t_CO2', 'Naphtha_Thermal_emissions_t_CO2'],
            'LPG': ['LPG_Propane_emissions_t_CO2', 'LPG_Butane_emissions_t_CO2'],
            'Natural_Gas': ['LNG_emissions_t_CO2', 'Fuel_Gas_Mix_emissions_t_CO2'],
            'Electricity': ['Electricity_emissions_t_CO2']
        }

        # Corresponding energy consumption categories
        self.energy_consumption_categories = {
            'Naphtha': ['Naphtha_Feedstock', 'Naphtha_Thermal'],
            'LPG': ['LPG_Propane', 'LPG_Butane'],
            'Natural_Gas': ['LNG', 'Fuel_Gas_Mix'],
            'Electricity': ['Electricity']
        }

        # Calculate total energy consumption by category (GJ)
        self.baseline_energy_gj = {}
        for category, sources in self.energy_consumption_categories.items():
            category_consumption = sum(self.energy_consumption_gj.get(source, 0) for source in sources)
            self.baseline_energy_gj[category] = category_consumption

        # Convert GJ to toe (1 toe = 41.868 GJ)
        self.baseline_energy_toe = {
            category: energy_gj / 41.868
            for category, energy_gj in self.baseline_energy_gj.items()
        }

        # Calculate emissions
        self.baseline_emissions = {}
        for category, columns in self.energy_categories.items():
            available_cols = [col for col in columns if col in self.merged_df.columns]
            if available_cols:
                self.baseline_emissions[category] = self.merged_df[available_cols].sum(axis=1).sum()
            else:
                self.baseline_emissions[category] = 0

        # Calculate totals
        self.total_baseline_emissions = sum(self.baseline_emissions.values())
        self.total_energy_gj = sum(self.baseline_energy_gj.values())
        self.total_energy_toe = sum(self.baseline_energy_toe.values())

        print(f"✅ Total baseline emissions: {self.total_baseline_emissions/1e6:.1f} MtCO₂e/year")
        print(f"✅ Total energy consumption: {self.total_energy_gj/1e9:.1f} billion GJ/year")
        print(f"✅ Total energy consumption: {self.total_energy_toe/1e6:.1f} million toe/year")

        return self

    def create_bau_projections(self, years=[2025, 2030, 2040, 2050]):
        """Create Business-as-Usual emission projections"""
        print(f"\n📈 Creating BAU projections for {years}...")

        # BAU assumptions (annual growth rates)
        bau_assumptions = {
            'capacity_growth': 0.02,  # 2% annual capacity growth
            'efficiency_improvement': -0.005,  # 0.5% annual efficiency improvement
            'electricity_decarbonization': -0.02  # 2% annual grid decarbonization
        }

        self.bau_projections = {}
        base_year = 2023

        for year in years:
            years_from_base = year - base_year

            # Capacity growth factor
            capacity_factor = (1 + bau_assumptions['capacity_growth']) ** years_from_base

            # Efficiency improvement factor
            efficiency_factor = (1 + bau_assumptions['efficiency_improvement']) ** years_from_base

            # Grid decarbonization factor (electricity only)
            grid_factor = (1 + bau_assumptions['electricity_decarbonization']) ** years_from_base

            year_emissions = {}
            for category, base_emissions in self.baseline_emissions.items():
                if category == 'Electricity':
                    # Apply all factors to electricity
                    year_emissions[category] = base_emissions * capacity_factor * efficiency_factor * grid_factor
                else:
                    # Apply capacity and efficiency factors to other sources
                    year_emissions[category] = base_emissions * capacity_factor * efficiency_factor

            self.bau_projections[year] = year_emissions

        return self

    def analyze_by_sectors(self):
        """Analyze emissions by process sectors and companies"""
        print("\n🏭 Analyzing by sectors and companies...")

        # Process sector analysis
        emission_cols = [col for col in self.merged_df.columns if 'emissions_t_CO2' in col]

        self.process_analysis = self.merged_df.groupby('process').agg({
            'capacity_1000_t': 'sum',
            'company': 'nunique',
            **{col: 'sum' for col in emission_cols}
        }).fillna(0)

        self.process_analysis['total_emissions_MtCO2'] = self.process_analysis[emission_cols].sum(axis=1) / 1e6
        self.process_analysis['emission_intensity_tCO2_per_t'] = (
            self.process_analysis[emission_cols].sum(axis=1) /
            (self.process_analysis['capacity_1000_t'] * 1000)
        )

        # Company analysis
        self.company_analysis = self.merged_df.groupby('company').agg({
            'capacity_1000_t': 'sum',
            'process': 'nunique',
            **{col: 'sum' for col in emission_cols}
        }).fillna(0)

        self.company_analysis['total_emissions_MtCO2'] = self.company_analysis[emission_cols].sum(axis=1) / 1e6
        self.company_analysis = self.company_analysis.sort_values('total_emissions_MtCO2', ascending=False)

        return self

    def create_baseline_visualizations(self):
        """Create comprehensive baseline visualizations"""
        print("\n📊 Creating baseline visualizations...")

        # Set up the figure with additional space for energy consumption
        fig = plt.figure(figsize=(24, 16))
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)

        fig.suptitle('Korean Petrochemical Industry - Baseline Emission Analysis (2023)',
                    fontsize=20, fontweight='bold', y=0.98)

        # Colors for consistency
        energy_colors = {'Naphtha': '#FF6B6B', 'Natural_Gas': '#4ECDC4', 'Electricity': '#45B7D1', 'LPG': '#FFA07A'}
        process_colors = {'BTX Plant': '#FF9999', 'Naphtha Cracker': '#66B2FF', 'Utility': '#99FF99'}

        # 1. Energy Source Breakdown - Emissions (Pie Chart)
        ax1 = fig.add_subplot(gs[0, :2])
        energy_sources = list(self.baseline_emissions.keys())
        emission_values = list(self.baseline_emissions.values())
        colors1 = [energy_colors.get(source, '#CCCCCC') for source in energy_sources]

        wedges, texts, autotexts = ax1.pie(emission_values, labels=energy_sources, autopct='%1.1f%%',
                                          colors=colors1, startangle=90, textprops={'fontsize': 12})
        ax1.set_title(f'Baseline Emissions by Energy Source\nTotal: {self.total_baseline_emissions/1e6:.1f} MtCO₂e/year',
                     fontsize=14, fontweight='bold', pad=20)

        # 2. Energy Consumption by Source (Pie Chart)
        ax2 = fig.add_subplot(gs[0, 2])
        energy_consumption_values = [self.baseline_energy_gj[source] for source in energy_sources]

        wedges2, texts2, autotexts2 = ax2.pie(energy_consumption_values, labels=energy_sources, autopct='%1.1f%%',
                                              colors=colors1, startangle=90, textprops={'fontsize': 10})
        ax2.set_title(f'Energy Consumption by Source\nTotal: {self.total_energy_gj/1e9:.1f} billion GJ/year\n({self.total_energy_toe/1e6:.1f} million toe/year)',
                     fontsize=12, fontweight='bold', pad=15)

        # 3. BAU Projections (Line Chart)
        ax3 = fig.add_subplot(gs[0, 3])
        years = list(self.bau_projections.keys())

        for energy_source in energy_sources:
            values = [self.bau_projections[year][energy_source]/1e6 for year in years]
            ax3.plot(years, values, marker='o', linewidth=2.5, markersize=6,
                    color=energy_colors.get(energy_source, '#CCCCCC'), label=energy_source)

        ax3.set_title('BAU Emission Projections', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Emissions (MtCO₂e/year)')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3)

        # 4. Process Sector Analysis (Bar Chart)
        ax4 = fig.add_subplot(gs[1, 0])
        process_names = self.process_analysis.index
        process_emissions = self.process_analysis['total_emissions_MtCO2']
        colors3 = [process_colors.get(process, '#CCCCCC') for process in process_names]

        bars = ax4.bar(process_names, process_emissions, color=colors3)
        ax4.set_title('Emissions by Process Type', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Emissions (MtCO₂e/year)')
        ax4.tick_params(axis='x', rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars, process_emissions):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{value:.1f}', ha='center', va='bottom', fontsize=10)

        # 5. Emission Intensity by Process (Bar Chart)
        ax5 = fig.add_subplot(gs[1, 1])
        intensities = self.process_analysis['emission_intensity_tCO2_per_t']

        bars = ax5.bar(process_names, intensities, color=colors3)
        ax5.set_title('Emission Intensity by Process', fontsize=14, fontweight='bold')
        ax5.set_ylabel('tCO₂e per tonne product')
        ax5.tick_params(axis='x', rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars, intensities):
            ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.2f}', ha='center', va='bottom', fontsize=10)

        # 6. Top Companies by Emissions (Horizontal Bar)
        ax6 = fig.add_subplot(gs[1, 2:])
        top_companies = self.company_analysis.head(10)

        bars = ax6.barh(range(len(top_companies)), top_companies['total_emissions_MtCO2'],
                       color='lightblue')
        ax6.set_title('Top 10 Companies by Emissions', fontsize=14, fontweight='bold')
        ax6.set_xlabel('Emissions (MtCO₂e/year)')
        ax6.set_yticks(range(len(top_companies)))
        ax6.set_yticklabels(top_companies.index, fontsize=9)

        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, top_companies['total_emissions_MtCO2'])):
            ax6.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{value:.1f}', ha='left', va='center', fontsize=8)

        # 7. Energy Mix by Process (Stacked Bar)
        ax7 = fig.add_subplot(gs[2, :])

        # Calculate energy mix for each process
        process_energy = {}
        for process in self.merged_df['process'].unique():
            process_data = self.merged_df[self.merged_df['process'] == process]
            energy_totals = {}

            for category, columns in self.energy_categories.items():
                available_cols = [col for col in columns if col in process_data.columns]
                if available_cols:
                    energy_totals[category] = process_data[available_cols].sum().sum() / 1e6
                else:
                    energy_totals[category] = 0

            process_energy[process] = energy_totals

        # Convert to DataFrame for plotting
        process_energy_df = pd.DataFrame(process_energy).fillna(0)

        # Create stacked bar chart
        bottom = np.zeros(len(process_energy_df.columns))

        for energy_source in process_energy_df.index:
            color = energy_colors.get(energy_source, '#CCCCCC')
            ax7.bar(process_energy_df.columns, process_energy_df.loc[energy_source],
                   bottom=bottom, label=energy_source, color=color)
            bottom += process_energy_df.loc[energy_source]

        ax7.set_title('Energy Source Mix by Process Type', fontsize=14, fontweight='bold')
        ax7.set_ylabel('Emissions (MtCO₂e/year)')
        ax7.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax7.tick_params(axis='x', rotation=45)

        # Save the comprehensive visualization
        baseline_viz_path = self.output_dir / "baseline_emission_analysis.png"
        plt.savefig(baseline_viz_path, dpi=300, bbox_inches='tight')
        print(f"✅ Baseline visualization saved: {baseline_viz_path}")

        plt.show()
        return baseline_viz_path

    def save_baseline_reports(self):
        """Save detailed baseline analysis reports"""
        print("\n📋 Saving baseline reports...")

        # 1. Energy source baseline report with consumption data
        baseline_summary = pd.DataFrame({
            'Energy_Source': list(self.baseline_emissions.keys()),
            'Annual_Emissions_tCO2': list(self.baseline_emissions.values()),
            'Emissions_MtCO2': [v/1e6 for v in self.baseline_emissions.values()],
            'Emission_Share_Percent': [(v/self.total_baseline_emissions)*100 for v in self.baseline_emissions.values()],
            'Energy_Consumption_GJ': [self.baseline_energy_gj[k] for k in self.baseline_emissions.keys()],
            'Energy_Consumption_Million_GJ': [self.baseline_energy_gj[k]/1e6 for k in self.baseline_emissions.keys()],
            'Energy_Consumption_toe': [self.baseline_energy_toe[k] for k in self.baseline_emissions.keys()],
            'Energy_Consumption_Million_toe': [self.baseline_energy_toe[k]/1e6 for k in self.baseline_emissions.keys()],
            'Energy_Share_Percent': [(self.baseline_energy_gj[k]/self.total_energy_gj)*100 for k in self.baseline_emissions.keys()],
            'Energy_Intensity_GJ_per_tCO2': [
                (self.baseline_energy_gj[k]/self.baseline_emissions[k]) if self.baseline_emissions[k] > 0 else 0
                for k in self.baseline_emissions.keys()
            ]
        })

        baseline_path = self.output_dir / "baseline_emissions_by_source.csv"
        baseline_summary.to_csv(baseline_path, index=False)

        # 2. BAU projections report
        bau_df = pd.DataFrame(self.bau_projections).T / 1e6  # Convert to MtCO2
        bau_df.index.name = 'Year'
        bau_df['Total'] = bau_df.sum(axis=1)

        bau_path = self.output_dir / "bau_emission_projections.csv"
        bau_df.to_csv(bau_path)

        # 3. Process analysis report
        process_path = self.output_dir / "baseline_emissions_by_process.csv"
        self.process_analysis.to_csv(process_path)

        # 4. Company analysis report
        company_path = self.output_dir / "baseline_emissions_by_company.csv"
        self.company_analysis.to_csv(company_path)

        print(f"✅ Reports saved to: {self.output_dir}")
        return {
            'baseline': baseline_path,
            'bau_projections': bau_path,
            'process_analysis': process_path,
            'company_analysis': company_path
        }

    def print_summary(self):
        """Print executive summary of baseline analysis"""
        print(f"\n{'='*80}")
        print("🎯 BASELINE EMISSION ANALYSIS SUMMARY")
        print(f"{'='*80}")

        print(f"\n📊 TOTAL BASELINE EMISSIONS (2023): {self.total_baseline_emissions/1e6:.1f} MtCO₂e/year")
        print(f"⚡ TOTAL ENERGY CONSUMPTION (2023): {self.total_energy_gj/1e9:.1f} billion GJ/year")
        print(f"🛢️ TOTAL ENERGY CONSUMPTION (2023): {self.total_energy_toe/1e6:.1f} million toe/year")
        print(f"📈 Industry Capacity: {self.merged_df['capacity_1000_t'].sum():,.0f} kt/year")
        print(f"🏭 Total Facilities: {len(self.merged_df)} facilities")
        print(f"🏢 Total Companies: {self.merged_df['company'].nunique()} companies")

        print(f"\n⚡ ENERGY SOURCE BREAKDOWN (Emissions & Consumption):")
        for source in self.baseline_emissions.keys():
            emissions = self.baseline_emissions[source]
            energy_gj = self.baseline_energy_gj[source]
            energy_toe = self.baseline_energy_toe[source]
            emission_share = (emissions / self.total_baseline_emissions) * 100
            energy_share = (energy_gj / self.total_energy_gj) * 100
            print(f"   {source:12}: {emissions/1e6:6.2f} MtCO₂e ({emission_share:5.1f}%) | "
                  f"{energy_gj/1e6:6.0f} million GJ ({energy_share:5.1f}%) | "
                  f"{energy_toe/1e6:5.2f} million toe")

        print(f"\n🏭 PROCESS TYPE BREAKDOWN:")
        for process, data in self.process_analysis.iterrows():
            print(f"   {process:15}: {data['total_emissions_MtCO2']:6.1f} MtCO₂e, "
                  f"{data['capacity_1000_t']:6.0f} kt capacity, "
                  f"{data['emission_intensity_tCO2_per_t']:.2f} tCO₂e/t")

        print(f"\n📈 BAU PROJECTION (2050): {sum(self.bau_projections[2050].values())/1e6:.1f} MtCO₂e/year")

        print(f"\n🎯 KEY INSIGHTS:")
        print(f"   • Naphtha dominates emissions ({(self.baseline_emissions['Naphtha']/self.total_baseline_emissions)*100:.1f}% of total)")
        print(f"   • {self.process_analysis['total_emissions_MtCO2'].idxmax()} is the highest-emitting process type")
        print(f"   • {self.company_analysis.index[0]} is the largest emitter among companies")
        print(f"   • Average emission intensity: {(self.total_baseline_emissions/(self.merged_df['capacity_1000_t'].sum()*1000)):.2f} tCO₂e/t product")

    def run_full_analysis(self):
        """Run the complete baseline emission analysis"""
        print("🚀 Starting comprehensive baseline analysis...")

        # Execute all analysis steps
        self.load_baseline_data()
        self.calculate_baseline_emissions()
        self.create_bau_projections()
        self.analyze_by_sectors()

        # Create visualizations and reports
        viz_path = self.create_baseline_visualizations()
        report_paths = self.save_baseline_reports()

        # Print summary
        self.print_summary()

        print(f"\n✅ BASELINE ANALYSIS COMPLETE!")
        print(f"📊 Main visualization: {viz_path}")
        print(f"📋 Reports directory: {self.output_dir}")
        print(f"\n🔄 Ready for Phase 2: MACC Optimization Model")

        return {
            'visualization': viz_path,
            'reports': report_paths,
            'baseline_emissions': self.baseline_emissions,
            'bau_projections': self.bau_projections,
            'total_emissions': self.total_baseline_emissions
        }

if __name__ == "__main__":
    # Run the complete baseline analysis
    baseline_analysis = BaselineEmissionAnalysis()
    results = baseline_analysis.run_full_analysis()