#!/usr/bin/env python3
"""
Proper Facility-Level BAU Analysis with Natural Shutdowns and Retirements
Using all Excel sheets as intended for the MACC model
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FacilityLevelBAUAnalysis:
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "data"
        self.original_file = self.data_path / "Korean_Petrochemical_MACC_Model_English.xlsx"
        self.corrected_file = self.data_path / "Korean_MACC_Model_CORRECTED_INTENSITIES.xlsx"
        self.output_path = Path(__file__).parent.parent / "outputs" / "facility_level_bau"
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Model years
        self.years = [2025, 2030, 2040, 2050]

        # Energy intensity correction factor (from previous analysis)
        self.correction_factor = 63.3 / 261.5  # 0.242

    def load_all_facility_data(self):
        """Load all facility-related data from Excel sheets"""
        logger.info("📊 Loading comprehensive facility data...")

        try:
            # Base facility data
            self.facilities_base = pd.read_excel(self.original_file, sheet_name='source_Original')

            # Facility projections for each year
            self.facility_projections = {}
            for year in [2030, 2040, 2050]:
                sheet_name = f'Facility_Projections_{year}'
                self.facility_projections[year] = pd.read_excel(self.original_file, sheet_name=sheet_name)

            # Retirement summary
            self.retirement_summary = pd.read_excel(self.original_file, sheet_name='Retirement_Summary')

            # Load corrected energy intensities
            self.ci_corrected = pd.read_excel(self.corrected_file, sheet_name='CI_Corrected')

            # Baseline assumptions
            self.baseline_assumptions = pd.read_excel(self.original_file, sheet_name='Baseline_Assumptions_Original')

            logger.info(f"✅ Loaded facility data:")
            logger.info(f"   Base facilities: {self.facilities_base.shape[0]} facilities")
            logger.info(f"   Retirement data: {self.retirement_summary.shape[0]} time points")
            logger.info(f"   Energy intensities: {self.ci_corrected.shape[0]} products")

            return True

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False

    def calculate_facility_emissions(self, facility_data, year):
        """Calculate emissions for each facility using corrected intensities"""

        facility_results = []

        for idx, facility in facility_data.iterrows():
            try:
                # Extract facility information
                product = str(facility['products'])
                process = str(facility['process'])
                company = str(facility['company'])
                location = str(facility['location'])
                operation_year = int(facility['year'])
                capacity_kt = float(facility['capacity_1000_t'])

                # Check if facility is retired (for projection years)
                is_retired = False
                if 'retired' in facility and facility['retired']:
                    is_retired = True
                    continue  # Skip retired facilities

                # Find matching energy intensity
                product_match = self.ci_corrected[
                    self.ci_corrected.iloc[:,0].str.contains(product, case=False, na=False)
                ]

                if product_match.empty:
                    # Try process matching
                    product_match = self.ci_corrected[
                        self.ci_corrected.iloc[:,0].str.contains(process, case=False, na=False)
                    ]

                if product_match.empty:
                    logger.warning(f"No CI match for {product}/{process}")
                    continue

                ci_row = product_match.iloc[0]

                # Calculate energy consumption by source
                energy_breakdown = {}
                total_energy_intensity = 0

                for col_idx, col_name in enumerate(self.ci_corrected.columns):
                    col_str = str(col_name).lower()
                    if 'gj_per_t' in col_str and pd.notna(ci_row.iloc[col_idx]):
                        intensity = float(ci_row.iloc[col_idx])
                        total_energy_gj = intensity * capacity_kt * 1000  # Convert kt to t

                        # Categorize energy source
                        if 'naphtha_feedstock' in col_str:
                            energy_breakdown['Naphtha_Feedstock'] = total_energy_gj
                        elif 'naphtha_thermal' in col_str:
                            energy_breakdown['Naphtha_Thermal'] = total_energy_gj
                        elif 'lng' in col_str:
                            energy_breakdown['LNG'] = total_energy_gj
                        elif 'fuel_gas' in col_str:
                            energy_breakdown['Fuel_Gas'] = total_energy_gj
                        elif 'byproduct_gas' in col_str:
                            energy_breakdown['Byproduct_Gas'] = total_energy_gj
                        elif 'electricity' in col_str:
                            energy_breakdown['Electricity'] = total_energy_gj
                        elif 'lpg' in col_str:
                            energy_breakdown['LPG'] = total_energy_gj
                        elif 'fuel_oil' in col_str:
                            energy_breakdown['Fuel_Oil'] = total_energy_gj

                        total_energy_intensity += intensity

                # Calculate emissions by energy source (with correction factor)
                emission_factors = {
                    'Naphtha_Feedstock': 0.0561,
                    'Naphtha_Thermal': 0.0561,
                    'LNG': 0.0515,
                    'Fuel_Gas': 0.0500,
                    'Byproduct_Gas': 0.0500,
                    'Electricity': 0.1389,  # Korean grid
                    'LPG': 0.0631,
                    'Fuel_Oil': 0.0774
                }

                total_emissions = 0
                emission_breakdown = {}

                for source, energy_gj in energy_breakdown.items():
                    ef = emission_factors.get(source, 0.055)  # Default factor
                    emissions_tco2 = energy_gj * ef * self.correction_factor  # Apply correction
                    emission_breakdown[source] = emissions_tco2
                    total_emissions += emissions_tco2

                # Calculate facility age
                facility_age = year - operation_year

                facility_result = {
                    'Year': year,
                    'Product': product,
                    'Process': process,
                    'Company': company,
                    'Location': location,
                    'Operation_Year': operation_year,
                    'Age': facility_age,
                    'Capacity_kt': capacity_kt,
                    'Total_Emissions_tCO2': total_emissions,
                    'Total_Energy_GJ': sum(energy_breakdown.values()),
                    'Energy_Intensity_GJ_per_t': total_energy_intensity,
                    'Emission_Intensity_tCO2_per_t': total_emissions / (capacity_kt * 1000) if capacity_kt > 0 else 0,
                    'Is_Retired': is_retired
                }

                # Add energy and emission breakdowns
                for source, energy in energy_breakdown.items():
                    facility_result[f'Energy_{source}_GJ'] = energy

                for source, emissions in emission_breakdown.items():
                    facility_result[f'Emissions_{source}_tCO2'] = emissions

                facility_results.append(facility_result)

            except Exception as e:
                logger.warning(f"Error processing facility {idx}: {e}")
                continue

        return pd.DataFrame(facility_results)

    def run_bau_analysis(self):
        """Run complete facility-level BAU analysis with retirements"""
        logger.info("🚀 Running facility-level BAU analysis...")

        self.bau_results = {}
        self.facility_details = {}

        for year in self.years:
            logger.info(f"📈 Processing year {year}...")

            # Get appropriate facility data
            if year == 2025:
                # Use base data (no retirements yet)
                facility_data = self.facilities_base.copy()
            elif year in self.facility_projections:
                # Use projection data with retirements
                facility_data = self.facility_projections[year].copy()
            else:
                # Interpolate or use closest available data
                facility_data = self.facilities_base.copy()

            # Calculate emissions for all active facilities
            facility_results_df = self.calculate_facility_emissions(facility_data, year)

            if facility_results_df.empty:
                logger.warning(f"No valid facilities for year {year}")
                continue

            # Store detailed results
            self.facility_details[year] = facility_results_df

            # Calculate aggregated results
            active_facilities = facility_results_df[~facility_results_df['Is_Retired']]

            total_emissions_tco2 = active_facilities['Total_Emissions_tCO2'].sum()
            total_energy_gj = active_facilities['Total_Energy_GJ'].sum()
            total_capacity_kt = active_facilities['Capacity_kt'].sum()
            num_active_facilities = len(active_facilities)

            # Process-level aggregation
            process_breakdown = active_facilities.groupby('Process')['Total_Emissions_tCO2'].sum()
            process_breakdown = (process_breakdown / total_emissions_tco2 * 100).round(1) if total_emissions_tco2 > 0 else {}

            # Company-level aggregation
            company_breakdown = active_facilities.groupby('Company')['Total_Emissions_tCO2'].sum().sort_values(ascending=False)
            top_companies = company_breakdown.head(10)

            # Energy source aggregation
            energy_cols = [col for col in active_facilities.columns if col.startswith('Energy_') and col.endswith('_GJ')]
            energy_totals = {}

            for col in energy_cols:
                source = col.replace('Energy_', '').replace('_GJ', '')
                total_energy_source = active_facilities[col].sum()
                if total_energy_source > 0:
                    energy_totals[source] = total_energy_source

            # Calculate energy shares
            total_energy_all_sources = sum(energy_totals.values())
            energy_shares = {k: v/total_energy_all_sources*100 for k, v in energy_totals.items()} if total_energy_all_sources > 0 else {}

            self.bau_results[year] = {
                'total_emissions_mtco2': total_emissions_tco2 / 1_000_000,
                'total_energy_gj': total_energy_gj,
                'total_energy_toe': total_energy_gj / 41.868,
                'total_capacity_kt': total_capacity_kt,
                'num_active_facilities': num_active_facilities,
                'process_breakdown': dict(process_breakdown),
                'company_breakdown': dict(top_companies),
                'energy_totals_gj': energy_totals,
                'energy_shares_pct': energy_shares
            }

            logger.info(f"   {year}: {self.bau_results[year]['total_emissions_mtco2']:.1f} MtCO₂, {num_active_facilities} active facilities")

    def create_comprehensive_visualizations(self):
        """Create comprehensive facility-level visualizations"""
        logger.info("📊 Creating comprehensive visualizations...")

        # Set style
        plt.style.use('default')
        fig = plt.figure(figsize=(20, 16))

        # Create 6-panel visualization
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 1. BAU Emission Pathway
        ax1 = fig.add_subplot(gs[0, 0])
        years_list = list(self.bau_results.keys())
        emissions_list = [self.bau_results[year]['total_emissions_mtco2'] for year in years_list]

        ax1.plot(years_list, emissions_list, 'o-', linewidth=3, markersize=8, color='red', label='BAU Pathway')
        ax1.axhline(y=52.0, color='green', linestyle='--', alpha=0.7, label='Korean Target')
        ax1.set_title('BAU Emission Pathway\n(Facility-Level with Retirements)', fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Emissions (MtCO₂)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Active Facilities Over Time
        ax2 = fig.add_subplot(gs[0, 1])
        facilities_list = [self.bau_results[year]['num_active_facilities'] for year in years_list]
        ax2.plot(years_list, facilities_list, 'o-', linewidth=3, markersize=8, color='blue')
        ax2.set_title('Active Facilities Over Time\n(Natural Shutdowns)', fontweight='bold')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Number of Active Facilities')
        ax2.grid(True, alpha=0.3)

        # 3. Capacity Over Time
        ax3 = fig.add_subplot(gs[0, 2])
        capacity_list = [self.bau_results[year]['total_capacity_kt'] for year in years_list]
        ax3.plot(years_list, capacity_list, 'o-', linewidth=3, markersize=8, color='purple')
        ax3.set_title('Total Capacity Over Time\n(Accounting for Retirements)', fontweight='bold')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Total Capacity (kt)')
        ax3.grid(True, alpha=0.3)

        # 4. Process Breakdown (2025)
        if 2025 in self.bau_results:
            ax4 = fig.add_subplot(gs[1, 0])
            process_data = self.bau_results[2025]['process_breakdown']
            if process_data:
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
                ax4.pie(process_data.values(), labels=process_data.keys(), autopct='%1.1f%%',
                       startangle=90, colors=colors)
                ax4.set_title('2025 Emission Shares by Process', fontweight='bold')

        # 5. Energy Source Shares (2025)
        if 2025 in self.bau_results:
            ax5 = fig.add_subplot(gs[1, 1])
            energy_data = self.bau_results[2025]['energy_shares_pct']
            if energy_data:
                colors = ['#FFD93D', '#6BCF7F', '#FF8C42', '#74B9FF', '#A29BFE']
                ax5.pie(energy_data.values(), labels=energy_data.keys(), autopct='%1.1f%%',
                       startangle=90, colors=colors)
                ax5.set_title('2025 Energy Shares by Source', fontweight='bold')

        # 6. Retirement Impact
        ax6 = fig.add_subplot(gs[1, 2])
        retirement_years = [2030, 2040, 2050]
        retirement_data = self.retirement_summary.set_index('year')

        if not retirement_data.empty:
            active_fac = [retirement_data.loc[year, 'active_facilities'] for year in retirement_years]
            retired_fac = [retirement_data.loc[year, 'retired_facilities'] for year in retirement_years]

            ax6.bar(retirement_years, active_fac, label='Active', color='green', alpha=0.7)
            ax6.bar(retirement_years, retired_fac, bottom=active_fac, label='Retired', color='red', alpha=0.7)
            ax6.set_title('Facility Retirement Schedule', fontweight='bold')
            ax6.set_xlabel('Year')
            ax6.set_ylabel('Number of Facilities')
            ax6.legend()

        # 7. Top Companies (2025)
        if 2025 in self.bau_results:
            ax7 = fig.add_subplot(gs[2, :])
            company_data = self.bau_results[2025]['company_breakdown']
            if company_data:
                companies = list(company_data.keys())[:10]  # Top 10
                emissions = [company_data[comp]/1_000_000 for comp in companies]  # Convert to MtCO2

                bars = ax7.bar(range(len(companies)), emissions, color='skyblue')
                ax7.set_title('2025 Top Companies by Emissions', fontweight='bold')
                ax7.set_xlabel('Company')
                ax7.set_ylabel('Emissions (MtCO₂)')
                ax7.set_xticks(range(len(companies)))
                ax7.set_xticklabels(companies, rotation=45, ha='right')

                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax7.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}', ha='center', va='bottom')

        plt.suptitle('Korean Petrochemical Industry - Facility-Level BAU Analysis',
                     fontsize=18, fontweight='bold', y=0.98)

        plt.savefig(self.output_path / 'facility_level_bau_comprehensive.png',
                    dpi=300, bbox_inches='tight')
        plt.show()

    def generate_detailed_reports(self):
        """Generate comprehensive facility-level reports"""
        logger.info("📋 Generating detailed reports...")

        # Export facility-level data for each year
        for year in self.years:
            if year in self.facility_details:
                csv_file = self.output_path / f"facility_details_{year}.csv"
                self.facility_details[year].to_csv(csv_file, index=False)

        # Generate summary report
        report_file = self.output_path / "facility_level_bau_report.txt"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("KOREAN PETROCHEMICAL FACILITY-LEVEL BAU ANALYSIS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Analysis Level: Individual Facility with Natural Retirements\n\n")

            f.write("🎯 MODEL SPECIFICATIONS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"• Energy intensity correction factor: {self.correction_factor:.3f}\n")
            f.write(f"• Analysis years: {', '.join(map(str, self.years))}\n")
            f.write(f"• Total facilities modeled: {self.facilities_base.shape[0]}\n")
            f.write(f"• Natural retirement modeling: Yes\n\n")

            f.write("📊 BAU PATHWAY RESULTS:\n")
            f.write("-" * 30 + "\n")
            for year in self.years:
                if year in self.bau_results:
                    result = self.bau_results[year]
                    f.write(f"{year}: {result['total_emissions_mtco2']:.1f} MtCO₂ | ")
                    f.write(f"{result['num_active_facilities']} facilities | ")
                    f.write(f"{result['total_capacity_kt']:,.0f} kt capacity\n")

            # Korean benchmark comparison
            if 2025 in self.bau_results:
                result_2025 = self.bau_results[2025]
                f.write(f"\n🇰🇷 KOREAN BENCHMARK ALIGNMENT (2025):\n")
                f.write("-" * 40 + "\n")
                f.write(f"Model Emissions: {result_2025['total_emissions_mtco2']:.1f} MtCO₂\n")
                f.write(f"Korean Target: 52.0 MtCO₂\n")
                f.write(f"Accuracy Ratio: {result_2025['total_emissions_mtco2']/52.0:.2f}\n")
                f.write(f"Total Energy: {result_2025['total_energy_toe']/1_000_000:.1f} Million toe\n")
                f.write(f"Active Facilities: {result_2025['num_active_facilities']}\n\n")

            # Process breakdown
            if 2025 in self.bau_results:
                f.write("🏭 PROCESS BREAKDOWN (2025):\n")
                f.write("-" * 30 + "\n")
                process_data = self.bau_results[2025]['process_breakdown']
                for process, share in process_data.items():
                    f.write(f"{process}: {share:.1f}%\n")
                f.write("\n")

            # Retirement impact
            f.write("⏰ RETIREMENT IMPACT:\n")
            f.write("-" * 25 + "\n")
            for idx, row in self.retirement_summary.iterrows():
                year = int(row['year'])
                active = int(row['active_facilities'])
                retired = int(row['retired_facilities'])
                retirement_rate = row['retirement_rate_pct']
                f.write(f"{year}: {active} active, {retired} retired ({retirement_rate:.1f}% retired)\n")

        logger.info(f"✅ Reports saved to: {self.output_path}")

    def run_complete_analysis(self):
        """Run the complete facility-level BAU analysis"""
        logger.info("🚀 Starting complete facility-level BAU analysis...")

        try:
            # Load data
            if not self.load_all_facility_data():
                return False

            # Run BAU analysis
            self.run_bau_analysis()

            # Create visualizations
            self.create_comprehensive_visualizations()

            # Generate reports
            self.generate_detailed_reports()

            print("\n" + "="*80)
            print("🎯 FACILITY-LEVEL BAU ANALYSIS COMPLETE")
            print("="*80)

            # Print key results
            for year in self.years:
                if year in self.bau_results:
                    result = self.bau_results[year]
                    print(f"{year}: {result['total_emissions_mtco2']:.1f} MtCO₂ | "
                          f"{result['num_active_facilities']} facilities | "
                          f"{result['total_capacity_kt']:,.0f} kt")

            if 2025 in self.bau_results:
                accuracy = self.bau_results[2025]['total_emissions_mtco2'] / 52.0
                print(f"\n🇰🇷 Korean Alignment (2025): {accuracy:.2f}")

            print(f"\n📁 Detailed results: {self.output_path}")

            return True

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return False

def main():
    """Main analysis function"""
    analyzer = FacilityLevelBAUAnalysis()
    return analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()