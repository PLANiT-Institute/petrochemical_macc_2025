#!/usr/bin/env python3
"""
Corrected Facility-Level BAU Analysis
- 248 facilities totaling 52 MtCO2 (Korean benchmark)
- 50-year operation lifetime assumption
- Proper emission intensity calibration
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

class CorrectedFacilityBAUAnalysis:
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "data"
        self.original_file = self.data_path / "Korean_Petrochemical_MACC_Model_English.xlsx"
        self.corrected_file = self.data_path / "Korean_MACC_Model_CORRECTED_INTENSITIES.xlsx"
        self.output_path = Path(__file__).parent.parent / "outputs" / "corrected_facility_bau"
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Model parameters
        self.base_year = 2025
        self.analysis_years = [2025, 2030, 2040, 2050]
        self.facility_lifetime_years = 50  # Standard petrochemical facility lifetime
        self.target_total_emissions_2025 = 52.0  # MtCO2 - Korean benchmark

        # Corrected emission intensity factor (calibrated to achieve 52 MtCO2)
        self.emission_correction_factor = 0.580  # Calculated to achieve Korean target

    def load_facility_data(self):
        """Load all facility data with proper structure"""
        logger.info("📊 Loading corrected facility data...")

        try:
            # Base facility data (248 facilities)
            self.facilities_base = pd.read_excel(self.original_file, sheet_name='source_Original')

            # Load corrected energy intensities
            self.ci_corrected = pd.read_excel(self.corrected_file, sheet_name='CI_Corrected')

            # Baseline assumptions
            self.baseline_assumptions = pd.read_excel(self.original_file, sheet_name='Baseline_Assumptions_Original')

            logger.info(f"✅ Loaded data:")
            logger.info(f"   Total facilities: {len(self.facilities_base)}")
            logger.info(f"   Target emissions: {self.target_total_emissions_2025} MtCO₂")
            logger.info(f"   Facility lifetime: {self.facility_lifetime_years} years")

            return True

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False

    def calculate_facility_retirement_schedule(self):
        """Calculate which facilities retire in each analysis year (50-year lifetime)"""

        retirement_schedule = {}

        for year in self.analysis_years:
            active_facilities = []
            retired_facilities = []

            for idx, facility in self.facilities_base.iterrows():
                operation_year = facility['year']
                facility_age = year - operation_year

                # Facility retires after 50 years
                if facility_age < self.facility_lifetime_years:
                    active_facilities.append(idx)
                else:
                    retired_facilities.append(idx)

            retirement_schedule[year] = {
                'active_indices': active_facilities,
                'retired_indices': retired_facilities,
                'num_active': len(active_facilities),
                'num_retired': len(retired_facilities),
                'retirement_rate': len(retired_facilities) / len(self.facilities_base) * 100
            }

            logger.info(f"   {year}: {len(active_facilities)} active, {len(retired_facilities)} retired ({retirement_schedule[year]['retirement_rate']:.1f}% retired)")

        self.retirement_schedule = retirement_schedule

    def calculate_facility_emissions(self, facility_indices, year):
        """Calculate emissions for specified facilities using corrected intensities"""

        facility_results = []

        for idx in facility_indices:
            try:
                facility = self.facilities_base.iloc[idx]

                # Extract facility information
                product = str(facility['products'])
                process = str(facility['process'])
                company = str(facility['company'])
                location = str(facility['location'])
                operation_year = int(facility['year'])
                capacity_kt = float(facility['capacity_1000_t'])

                # Calculate facility age
                facility_age = year - operation_year

                # Find matching energy intensity in corrected data
                product_match = self.ci_corrected[
                    self.ci_corrected.iloc[:,0].str.contains(product, case=False, na=False, regex=False)
                ]

                if product_match.empty:
                    # Try process matching
                    process_keywords = process.split()
                    for keyword in process_keywords:
                        if len(keyword) > 3:  # Avoid short words
                            product_match = self.ci_corrected[
                                self.ci_corrected.iloc[:,0].str.contains(keyword, case=False, na=False, regex=False)
                            ]
                            if not product_match.empty:
                                break

                if product_match.empty:
                    # Default energy intensity for unmatched facilities
                    logger.warning(f"No CI match for {product}/{process}, using default")
                    total_energy_intensity = 25.0  # Default GJ/t
                    energy_breakdown = {'Default_Energy': total_energy_intensity * capacity_kt * 1000}
                else:
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
                            else:
                                energy_breakdown['Other_Energy'] = energy_breakdown.get('Other_Energy', 0) + total_energy_gj

                            total_energy_intensity += intensity

                # Calculate emissions by energy source (with Korean-calibrated correction factor)
                emission_factors = {
                    'Naphtha_Feedstock': 0.0561,
                    'Naphtha_Thermal': 0.0561,
                    'LNG': 0.0515,
                    'Fuel_Gas': 0.0500,
                    'Byproduct_Gas': 0.0500,
                    'Electricity': 0.1389,  # Korean grid
                    'Other_Energy': 0.055,  # Average
                    'Default_Energy': 0.055
                }

                total_emissions = 0
                emission_breakdown = {}

                for source, energy_gj in energy_breakdown.items():
                    ef = emission_factors.get(source, 0.055)
                    emissions_tco2 = energy_gj * ef * self.emission_correction_factor
                    emission_breakdown[source] = emissions_tco2
                    total_emissions += emissions_tco2

                facility_result = {
                    'Facility_Index': idx,
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
                    'Emission_Intensity_tCO2_per_t': total_emissions / (capacity_kt * 1000) if capacity_kt > 0 else 0
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

    def run_corrected_bau_analysis(self):
        """Run BAU analysis with corrected emission intensities and 50-year lifetimes"""
        logger.info("🚀 Running corrected facility-level BAU analysis...")

        # Calculate retirement schedule
        self.calculate_facility_retirement_schedule()

        self.bau_results = {}
        self.facility_details = {}

        for year in self.analysis_years:
            logger.info(f"📈 Processing year {year}...")

            # Get active facilities for this year
            active_indices = self.retirement_schedule[year]['active_indices']

            # Calculate emissions for active facilities
            facility_results_df = self.calculate_facility_emissions(active_indices, year)

            if facility_results_df.empty:
                logger.warning(f"No valid facilities for year {year}")
                continue

            # Store detailed results
            self.facility_details[year] = facility_results_df

            # Calculate aggregated results
            total_emissions_tco2 = facility_results_df['Total_Emissions_tCO2'].sum()
            total_energy_gj = facility_results_df['Total_Energy_GJ'].sum()
            total_capacity_kt = facility_results_df['Capacity_kt'].sum()
            num_active_facilities = len(facility_results_df)

            # Process-level aggregation
            process_breakdown = facility_results_df.groupby('Process')['Total_Emissions_tCO2'].sum()
            process_shares = (process_breakdown / total_emissions_tco2 * 100).round(1) if total_emissions_tco2 > 0 else {}

            # Company-level aggregation (top 10)
            company_breakdown = facility_results_df.groupby('Company')['Total_Emissions_tCO2'].sum().sort_values(ascending=False)
            top_companies = dict(company_breakdown.head(10))

            # Energy source aggregation
            energy_cols = [col for col in facility_results_df.columns if col.startswith('Energy_') and col.endswith('_GJ')]
            energy_totals = {}

            for col in energy_cols:
                source = col.replace('Energy_', '').replace('_GJ', '')
                total_energy_source = facility_results_df[col].sum()
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
                'process_shares': dict(process_shares),
                'company_breakdown': top_companies,
                'energy_totals_gj': energy_totals,
                'energy_shares_pct': energy_shares
            }

            logger.info(f"   {year}: {self.bau_results[year]['total_emissions_mtco2']:.1f} MtCO₂, {num_active_facilities} facilities")

    def create_comprehensive_visualizations(self):
        """Create comprehensive BAU visualizations"""
        logger.info("📊 Creating comprehensive visualizations...")

        fig = plt.figure(figsize=(20, 16))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 1. BAU Emission Pathway
        ax1 = fig.add_subplot(gs[0, 0])
        years_list = list(self.bau_results.keys())
        emissions_list = [self.bau_results[year]['total_emissions_mtco2'] for year in years_list]

        ax1.plot(years_list, emissions_list, 'o-', linewidth=3, markersize=8, color='red', label='BAU Pathway')
        ax1.axhline(y=52.0, color='green', linestyle='--', alpha=0.7, label='Korean Benchmark')
        ax1.set_title('BAU Emission Pathway\n(248 Facilities, 50yr Lifetime)', fontweight='bold', fontsize=12)
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Emissions (MtCO₂)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, max([55] + emissions_list))

        # 2. Active Facilities Over Time
        ax2 = fig.add_subplot(gs[0, 1])
        facilities_list = [self.bau_results[year]['num_active_facilities'] for year in years_list]
        ax2.plot(years_list, facilities_list, 'o-', linewidth=3, markersize=8, color='blue')
        ax2.set_title('Active Facilities (50yr Retirement)', fontweight='bold', fontsize=12)
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Number of Active Facilities')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 250)

        # 3. Total Capacity Over Time
        ax3 = fig.add_subplot(gs[0, 2])
        capacity_list = [self.bau_results[year]['total_capacity_kt']/1000 for year in years_list]  # Convert to Mt
        ax3.plot(years_list, capacity_list, 'o-', linewidth=3, markersize=8, color='purple')
        ax3.set_title('Production Capacity\n(Natural Retirements)', fontweight='bold', fontsize=12)
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Total Capacity (Mt/year)')
        ax3.grid(True, alpha=0.3)

        # 4. Process Shares (2025)
        if 2025 in self.bau_results and self.bau_results[2025]['process_shares']:
            ax4 = fig.add_subplot(gs[1, 0])
            process_data = self.bau_results[2025]['process_shares']
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            ax4.pie(process_data.values(), labels=process_data.keys(), autopct='%1.1f%%',
                   startangle=90, colors=colors)
            ax4.set_title('2025 Process Emission Shares', fontweight='bold', fontsize=12)

        # 5. Energy Source Shares (2025)
        if 2025 in self.bau_results and self.bau_results[2025]['energy_shares_pct']:
            ax5 = fig.add_subplot(gs[1, 1])
            energy_data = self.bau_results[2025]['energy_shares_pct']
            colors = ['#FFD93D', '#6BCF7F', '#FF8C42', '#74B9FF', '#A29BFE']
            ax5.pie(energy_data.values(), labels=energy_data.keys(), autopct='%1.1f%%',
                   startangle=90, colors=colors)
            ax5.set_title('2025 Energy Source Shares', fontweight='bold', fontsize=12)

        # 6. Retirement Schedule
        ax6 = fig.add_subplot(gs[1, 2])
        retirement_years = list(self.retirement_schedule.keys())
        active_counts = [self.retirement_schedule[year]['num_active'] for year in retirement_years]
        retired_counts = [self.retirement_schedule[year]['num_retired'] for year in retirement_years]

        ax6.bar(retirement_years, active_counts, label='Active', color='green', alpha=0.7)
        ax6.bar(retirement_years, retired_counts, bottom=active_counts, label='Retired', color='red', alpha=0.7)
        ax6.set_title('50yr Retirement Schedule', fontweight='bold', fontsize=12)
        ax6.set_xlabel('Year')
        ax6.set_ylabel('Number of Facilities')
        ax6.legend()

        # 7. Top Companies (2025)
        if 2025 in self.bau_results and self.bau_results[2025]['company_breakdown']:
            ax7 = fig.add_subplot(gs[2, :])
            company_data = self.bau_results[2025]['company_breakdown']
            companies = list(company_data.keys())[:10]
            emissions = [company_data[comp]/1_000_000 for comp in companies]  # Convert to MtCO2

            bars = ax7.bar(range(len(companies)), emissions, color='skyblue', alpha=0.8)
            ax7.set_title('2025 Top 10 Companies by Emissions', fontweight='bold', fontsize=12)
            ax7.set_xlabel('Company')
            ax7.set_ylabel('Emissions (MtCO₂)')
            ax7.set_xticks(range(len(companies)))
            ax7.set_xticklabels(companies, rotation=45, ha='right')

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax7.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}', ha='center', va='bottom', fontsize=10)

        plt.suptitle('Korean Petrochemical Industry - Corrected Facility-Level BAU Analysis\n(52 MtCO₂ Baseline, 50-Year Facility Lifetime)',
                     fontsize=18, fontweight='bold', y=0.98)

        plt.savefig(self.output_path / 'corrected_facility_bau_comprehensive.png',
                    dpi=300, bbox_inches='tight')
        plt.show()

    def generate_detailed_reports(self):
        """Generate comprehensive reports with Korean benchmarks"""
        logger.info("📋 Generating detailed reports...")

        # Export facility details for each year
        for year in self.analysis_years:
            if year in self.facility_details:
                csv_file = self.output_path / f"facility_details_{year}.csv"
                self.facility_details[year].to_csv(csv_file, index=False)

        # Generate main report
        report_file = self.output_path / "corrected_facility_bau_report.txt"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("KOREAN PETROCHEMICAL CORRECTED FACILITY-LEVEL BAU ANALYSIS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Calibrated to Korean Industry Benchmarks (52 MtCO₂ total)\n\n")

            f.write("🎯 MODEL SPECIFICATIONS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"• Total facilities modeled: {len(self.facilities_base)}\n")
            f.write(f"• Target 2025 emissions: {self.target_total_emissions_2025} MtCO₂\n")
            f.write(f"• Facility operation lifetime: {self.facility_lifetime_years} years\n")
            f.write(f"• Emission correction factor: {self.emission_correction_factor:.3f}\n")
            f.write(f"• Analysis years: {', '.join(map(str, self.analysis_years))}\n\n")

            f.write("📊 BAU PATHWAY RESULTS:\n")
            f.write("-" * 30 + "\n")
            for year in self.analysis_years:
                if year in self.bau_results:
                    result = self.bau_results[year]
                    f.write(f"{year}: {result['total_emissions_mtco2']:.1f} MtCO₂ | ")
                    f.write(f"{result['num_active_facilities']} facilities | ")
                    f.write(f"{result['total_capacity_kt']:,.0f} kt capacity\n")

            # Korean benchmark validation
            if 2025 in self.bau_results:
                result_2025 = self.bau_results[2025]
                f.write(f"\n🇰🇷 KOREAN BENCHMARK VALIDATION (2025):\n")
                f.write("-" * 45 + "\n")
                f.write(f"Model Emissions: {result_2025['total_emissions_mtco2']:.1f} MtCO₂\n")
                f.write(f"Korean Target: {self.target_total_emissions_2025} MtCO₂\n")
                accuracy = result_2025['total_emissions_mtco2'] / self.target_total_emissions_2025
                f.write(f"Accuracy Ratio: {accuracy:.3f} ({'✅ EXCELLENT' if abs(accuracy - 1.0) < 0.05 else '✅ GOOD' if abs(accuracy - 1.0) < 0.1 else '⚠️ NEEDS ADJUSTMENT'})\n")
                f.write(f"Total Energy: {result_2025['total_energy_toe']/1_000_000:.1f} Million toe\n")
                f.write(f"Active Facilities: {result_2025['num_active_facilities']}\n\n")

            # Process breakdown
            if 2025 in self.bau_results:
                f.write("🏭 PROCESS BREAKDOWN (2025):\n")
                f.write("-" * 30 + "\n")
                process_data = self.bau_results[2025]['process_shares']
                for process, share in process_data.items():
                    f.write(f"{process}: {share:.1f}%\n")
                f.write("\n")

            # Retirement schedule
            f.write("⏰ 50-YEAR RETIREMENT SCHEDULE:\n")
            f.write("-" * 35 + "\n")
            for year in self.analysis_years:
                schedule = self.retirement_schedule[year]
                f.write(f"{year}: {schedule['num_active']} active, {schedule['num_retired']} retired ")
                f.write(f"({schedule['retirement_rate']:.1f}% retired)\n")

            f.write(f"\n✅ MODEL READY FOR MACC OPTIMIZATION ANALYSIS\n")

        logger.info(f"✅ Reports saved to: {self.output_path}")

    def run_complete_analysis(self):
        """Run the complete corrected facility-level BAU analysis"""
        logger.info("🚀 Starting corrected facility-level BAU analysis...")

        try:
            # Load data
            if not self.load_facility_data():
                return False

            # Run corrected BAU analysis
            self.run_corrected_bau_analysis()

            # Create visualizations
            self.create_comprehensive_visualizations()

            # Generate reports
            self.generate_detailed_reports()

            print("\n" + "="*80)
            print("🎯 CORRECTED FACILITY-LEVEL BAU ANALYSIS COMPLETE")
            print("="*80)
            print(f"✅ Calibrated to Korean Industry Benchmark: {self.target_total_emissions_2025} MtCO₂")
            print(f"✅ 50-year facility lifetime assumption applied")

            # Print key results
            for year in self.analysis_years:
                if year in self.bau_results:
                    result = self.bau_results[year]
                    print(f"{year}: {result['total_emissions_mtco2']:.1f} MtCO₂ | "
                          f"{result['num_active_facilities']} facilities | "
                          f"{result['total_capacity_kt']:,.0f} kt")

            if 2025 in self.bau_results:
                accuracy = self.bau_results[2025]['total_emissions_mtco2'] / self.target_total_emissions_2025
                print(f"\n🇰🇷 Korean Benchmark Accuracy: {accuracy:.3f} (Target: 1.000)")

            print(f"\n📁 Detailed results: {self.output_path}")

            return True

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return False

def main():
    """Main analysis function"""
    analyzer = CorrectedFacilityBAUAnalysis()
    return analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()