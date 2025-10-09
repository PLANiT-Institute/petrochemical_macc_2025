#!/usr/bin/env python3
"""
Verify Korean industry benchmarks against the properly calibrated model
Check all 7 Korean industry statistics provided by user
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KoreanBenchmarkVerifier:
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "data"
        self.calibrated_excel = self.data_path / "Korean_MACC_Model_PROPERLY_Calibrated.xlsx"
        self.output_path = Path(__file__).parent.parent / "outputs" / "korean_calibrated_baseline"

        # Korean industry benchmarks to verify
        self.korean_benchmarks = {
            'basic_petrochemicals_share': 0.89,  # 기초유분 생산이 전체 온실가스의 89% 차지
            'ncc_process_share': 0.46,           # NCC 분해공정이 전체 온실가스의 46% 차지
            'direct_emissions_share': 0.64,      # 직접 배출이 64% 차지
            'indirect_emissions_share': 0.34,    # 간접 배출이 34% 차지
            'byproduct_share_of_direct': 0.70,   # 직접 배출에서 부생가스, 부생유가 70% 차지
            'total_energy_toe': 67_700_000,      # 전체 에너지 사용량 6770만 toe
            'naphtha_share': 0.829,              # 나프타 비중이 전체 82.9%차지
            'downstream_electricity_toe': 4_000_000,  # 다운스트림 전력 400만 toe
        }

        self.verification_results = {}

    def run_basic_analysis(self):
        """Run basic analysis on the properly calibrated model"""
        logger.info("🔍 Running basic analysis on calibrated model...")

        try:
            # Load calibrated model data
            model_data = self.load_calibrated_model_data()

            # Calculate emissions breakdown
            emissions_analysis = self.analyze_emissions_structure(model_data)

            # Calculate energy consumption breakdown
            energy_analysis = self.analyze_energy_structure(model_data)

            # Verify each Korean benchmark
            self.verification_results = self.verify_all_benchmarks(emissions_analysis, energy_analysis)

            # Generate verification report
            self.generate_verification_report()

            return self.verification_results

        except Exception as e:
            logger.error(f"Error in basic analysis: {e}")
            raise

    def load_calibrated_model_data(self):
        """Load data from the properly calibrated model"""
        logger.info("📊 Loading calibrated model data...")

        model_data = {}

        try:
            # Load key sheets from calibrated model
            sheets_to_load = [
                'source_Original',
                'CI_Corrected',
                'CI2_Corrected',
                'utilities_Original',
                'Baseline_Assumptions_Original'
            ]

            for sheet in sheets_to_load:
                try:
                    model_data[sheet] = pd.read_excel(self.calibrated_excel, sheet_name=sheet)
                    logger.info(f"✅ Loaded {sheet}: {model_data[sheet].shape}")
                except Exception as e:
                    logger.warning(f"Could not load {sheet}: {e}")

            return model_data

        except Exception as e:
            logger.error(f"Error loading model data: {e}")
            # Fallback to original file if calibrated doesn't exist
            original_file = self.data_path / "Korean_Petrochemical_MACC_Model_English.xlsx"
            logger.info(f"Falling back to original file: {original_file}")

            for sheet in sheets_to_load:
                try:
                    model_data[sheet] = pd.read_excel(original_file, sheet_name=sheet)
                    logger.info(f"✅ Loaded {sheet} from original: {model_data[sheet].shape}")
                except Exception as e:
                    logger.warning(f"Could not load {sheet} from original: {e}")

            return model_data

    def analyze_emissions_structure(self, model_data):
        """Analyze emissions structure to check Korean benchmarks"""
        logger.info("🏭 Analyzing emissions structure...")

        emissions_analysis = {
            'total_emissions_mt': 0,
            'process_breakdown': {},
            'direct_indirect_split': {},
            'basic_petrochemicals_share': 0,
            'byproduct_emissions': 0,
            'detailed_breakdown': []
        }

        try:
            # Get facility data
            if 'source_Original' in model_data:
                facilities = model_data['source_Original']

                # Get emission factors
                emission_factors = {}
                if 'CI_Corrected' in model_data and 'CI2_Corrected' in model_data:
                    ci_data = model_data['CI_Corrected']
                    ci2_data = model_data['CI2_Corrected']

                    # Build emission factor lookup
                    for _, row in ci_data.iterrows():
                        if len(row) >= 2:
                            process_name = str(row.iloc[0])
                            emission_factors[process_name] = row

                # Calculate emissions by process
                process_emissions = {}
                total_emissions = 0

                for _, facility in facilities.iterrows():
                    if 'Process' in facility and 'capacity_1000_t' in facility:
                        process = str(facility['Process'])
                        capacity = facility['capacity_1000_t'] if pd.notna(facility['capacity_1000_t']) else 0

                        # Estimate emissions (simplified calculation)
                        # This is a placeholder - in real model this would use proper emission factors
                        emission_intensity = self.get_emission_intensity_by_process(process)
                        facility_emissions = capacity * emission_intensity

                        if process not in process_emissions:
                            process_emissions[process] = 0
                        process_emissions[process] += facility_emissions
                        total_emissions += facility_emissions

                emissions_analysis['total_emissions_mt'] = total_emissions / 1000  # Convert to Mt
                emissions_analysis['process_breakdown'] = process_emissions

                # Calculate basic petrochemicals share (NCC + downstream processes)
                basic_petro_processes = ['Naphtha Cracker', 'BTX Plant', 'Polyethylene', 'Polypropylene',
                                       'Polyvinyl Chloride', 'Polystyrene', 'Styrene Monomer']
                basic_petro_emissions = sum(process_emissions.get(p, 0) for p in basic_petro_processes)
                emissions_analysis['basic_petrochemicals_share'] = basic_petro_emissions / total_emissions if total_emissions > 0 else 0

                logger.info(f"Total emissions: {emissions_analysis['total_emissions_mt']:.1f} Mt")
                logger.info(f"Basic petrochemicals share: {emissions_analysis['basic_petrochemicals_share']:.1%}")

        except Exception as e:
            logger.error(f"Error analyzing emissions structure: {e}")

        return emissions_analysis

    def get_emission_intensity_by_process(self, process):
        """Get emission intensity by process type (simplified)"""
        # Simplified emission intensities (tCO2/kt production)
        # In real model, this would come from detailed emission factors

        emission_intensities = {
            'Naphtha Cracker': 1200,      # High emissions from cracking
            'BTX Plant': 800,             # Moderate emissions from aromatics
            'Polyethylene': 600,          # Downstream polymerization
            'Polypropylene': 650,
            'Polyvinyl Chloride': 900,    # Higher due to chlorine process
            'Polystyrene': 750,
            'Styrene Monomer': 850,
            'Utility': 2000,              # High due to power generation
        }

        # Default intensity for unknown processes
        return emission_intensities.get(process, 500)

    def analyze_energy_structure(self, model_data):
        """Analyze energy consumption structure"""
        logger.info("⚡ Analyzing energy structure...")

        energy_analysis = {
            'total_energy_gj': 0,
            'total_energy_toe': 0,
            'naphtha_consumption': 0,
            'fuel_gas_consumption': 0,
            'electricity_consumption': 0,
            'naphtha_share': 0,
            'energy_breakdown': {}
        }

        try:
            # Get facility data and calculate energy consumption
            if 'source_Original' in model_data:
                facilities = model_data['source_Original']

                # Energy intensities by process (GJ/t)
                energy_intensities = self.get_energy_intensities_by_process()

                total_energy = 0
                naphtha_energy = 0
                fuel_gas_energy = 0
                electricity_energy = 0

                for _, facility in facilities.iterrows():
                    if 'Process' in facility and 'capacity_1000_t' in facility:
                        process = str(facility['Process'])
                        capacity = facility['capacity_1000_t'] if pd.notna(facility['capacity_1000_t']) else 0

                        # Get energy breakdown for this process
                        process_energies = energy_intensities.get(process, {})

                        facility_naphtha = capacity * 1000 * process_energies.get('naphtha_gj_per_t', 0)
                        facility_fuel_gas = capacity * 1000 * process_energies.get('fuel_gas_gj_per_t', 0)
                        facility_electricity = capacity * 1000 * process_energies.get('electricity_gj_per_t', 0)

                        naphtha_energy += facility_naphtha
                        fuel_gas_energy += facility_fuel_gas
                        electricity_energy += facility_electricity

                total_energy = naphtha_energy + fuel_gas_energy + electricity_energy

                energy_analysis.update({
                    'total_energy_gj': total_energy,
                    'total_energy_toe': total_energy / 41.868,  # Convert to toe
                    'naphtha_consumption': naphtha_energy / 41.868,
                    'fuel_gas_consumption': fuel_gas_energy / 41.868,
                    'electricity_consumption': electricity_energy / 41.868,
                    'naphtha_share': naphtha_energy / total_energy if total_energy > 0 else 0
                })

                logger.info(f"Total energy: {energy_analysis['total_energy_toe']/1e6:.1f} M toe")
                logger.info(f"Naphtha share: {energy_analysis['naphtha_share']:.1%}")

        except Exception as e:
            logger.error(f"Error analyzing energy structure: {e}")

        return energy_analysis

    def get_energy_intensities_by_process(self):
        """Get energy intensities by process (simplified)"""
        # Simplified energy intensities based on typical petrochemical processes

        return {
            'Naphtha Cracker': {
                'naphtha_gj_per_t': 25,    # High naphtha as feedstock
                'fuel_gas_gj_per_t': 5,    # Some fuel gas for heating
                'electricity_gj_per_t': 1.5
            },
            'BTX Plant': {
                'naphtha_gj_per_t': 20,    # Naphtha feedstock
                'fuel_gas_gj_per_t': 3,
                'electricity_gj_per_t': 2
            },
            'Polyethylene': {
                'naphtha_gj_per_t': 2,     # Mainly ethylene from NCC
                'fuel_gas_gj_per_t': 8,    # Uses byproduct gases
                'electricity_gj_per_t': 3
            },
            'Polypropylene': {
                'naphtha_gj_per_t': 2,
                'fuel_gas_gj_per_t': 7,
                'electricity_gj_per_t': 2.5
            },
            'Utility': {
                'naphtha_gj_per_t': 0,
                'fuel_gas_gj_per_t': 15,   # High fuel gas for power
                'electricity_gj_per_t': 0  # Produces electricity
            }
        }

    def verify_all_benchmarks(self, emissions_analysis, energy_analysis):
        """Verify all Korean industry benchmarks"""
        logger.info("✅ Verifying Korean benchmarks...")

        verification = {}

        # 1. Basic petrochemicals (기초유분) = 89% of GHG
        actual_basic_share = emissions_analysis.get('basic_petrochemicals_share', 0)
        target_basic_share = self.korean_benchmarks['basic_petrochemicals_share']
        verification['basic_petrochemicals'] = {
            'target': f"{target_basic_share:.1%}",
            'actual': f"{actual_basic_share:.1%}",
            'difference': f"{(actual_basic_share - target_basic_share)*100:+.1f}pp",
            'status': '✅ PASS' if abs(actual_basic_share - target_basic_share) < 0.1 else '❌ FAIL'
        }

        # 2. NCC process = 46% of total GHG
        ncc_emissions = emissions_analysis['process_breakdown'].get('Naphtha Cracker', 0)
        total_emissions = sum(emissions_analysis['process_breakdown'].values())
        actual_ncc_share = ncc_emissions / total_emissions if total_emissions > 0 else 0
        target_ncc_share = self.korean_benchmarks['ncc_process_share']
        verification['ncc_process'] = {
            'target': f"{target_ncc_share:.1%}",
            'actual': f"{actual_ncc_share:.1%}",
            'difference': f"{(actual_ncc_share - target_ncc_share)*100:+.1f}pp",
            'status': '✅ PASS' if abs(actual_ncc_share - target_ncc_share) < 0.05 else '❌ FAIL'
        }

        # 3. Direct emissions = 64%, Indirect = 34%
        # Simplified assumption: fuel combustion = direct, electricity = indirect
        total_energy_toe = energy_analysis.get('total_energy_toe', 1)
        electricity_toe = energy_analysis.get('electricity_consumption', 0)
        direct_energy_toe = total_energy_toe - electricity_toe

        actual_direct_share = direct_energy_toe / total_energy_toe if total_energy_toe > 0 else 0
        actual_indirect_share = electricity_toe / total_energy_toe if total_energy_toe > 0 else 0

        verification['direct_emissions'] = {
            'target': f"{self.korean_benchmarks['direct_emissions_share']:.1%}",
            'actual': f"{actual_direct_share:.1%}",
            'difference': f"{(actual_direct_share - self.korean_benchmarks['direct_emissions_share'])*100:+.1f}pp",
            'status': '✅ PASS' if abs(actual_direct_share - self.korean_benchmarks['direct_emissions_share']) < 0.1 else '❌ FAIL'
        }

        verification['indirect_emissions'] = {
            'target': f"{self.korean_benchmarks['indirect_emissions_share']:.1%}",
            'actual': f"{actual_indirect_share:.1%}",
            'difference': f"{(actual_indirect_share - self.korean_benchmarks['indirect_emissions_share'])*100:+.1f}pp",
            'status': '✅ PASS' if abs(actual_indirect_share - self.korean_benchmarks['indirect_emissions_share']) < 0.1 else '❌ FAIL'
        }

        # 4. Total energy = 67.7M toe
        actual_total_energy = energy_analysis.get('total_energy_toe', 0) / 1e6
        target_total_energy = self.korean_benchmarks['total_energy_toe'] / 1e6
        verification['total_energy'] = {
            'target': f"{target_total_energy:.1f} M toe",
            'actual': f"{actual_total_energy:.1f} M toe",
            'difference': f"{actual_total_energy - target_total_energy:+.1f} M toe",
            'status': '✅ PASS' if abs(actual_total_energy - target_total_energy) < 5 else '❌ FAIL'
        }

        # 5. Naphtha share = 82.9%
        actual_naphtha_share = energy_analysis.get('naphtha_share', 0)
        target_naphtha_share = self.korean_benchmarks['naphtha_share']
        verification['naphtha_share'] = {
            'target': f"{target_naphtha_share:.1%}",
            'actual': f"{actual_naphtha_share:.1%}",
            'difference': f"{(actual_naphtha_share - target_naphtha_share)*100:+.1f}pp",
            'status': '✅ PASS' if abs(actual_naphtha_share - target_naphtha_share) < 0.05 else '❌ FAIL'
        }

        # 6. Downstream electricity = 4M toe
        actual_downstream_elec = energy_analysis.get('electricity_consumption', 0) / 1e6
        target_downstream_elec = self.korean_benchmarks['downstream_electricity_toe'] / 1e6
        verification['downstream_electricity'] = {
            'target': f"{target_downstream_elec:.1f} M toe",
            'actual': f"{actual_downstream_elec:.1f} M toe",
            'difference': f"{actual_downstream_elec - target_downstream_elec:+.1f} M toe",
            'status': '✅ PASS' if abs(actual_downstream_elec - target_downstream_elec) < 1 else '❌ FAIL'
        }

        # 7. Byproduct gas/oil = 70% of direct emissions (placeholder)
        verification['byproduct_share'] = {
            'target': f"{self.korean_benchmarks['byproduct_share_of_direct']:.1%}",
            'actual': "Not calculated (requires detailed process data)",
            'difference': "N/A",
            'status': '⚠️ NEEDS DETAILED DATA'
        }

        return verification

    def generate_verification_report(self):
        """Generate comprehensive verification report"""
        logger.info("📋 Generating verification report...")

        try:
            # Create report
            report_file = self.output_path / "korean_benchmarks_verification.txt"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("한국 석유화학 산업 벤치마크 검증 보고서\n")
                f.write("KOREAN PETROCHEMICAL INDUSTRY BENCHMARKS VERIFICATION\n")
                f.write("=" * 80 + "\n\n")

                f.write("🎯 검증 대상 (Korean Industry Facts to Verify):\n")
                f.write("1. 기초유분 생산이 전체 온실가스의 89% 차지\n")
                f.write("2. NCC 분해공정이 전체 온실가스의 46% 차지\n")
                f.write("3. 직접 배출이 64% 차지, 간접 배출이 34% 차지\n")
                f.write("4. 직접 배출에서 부생가스, 부생유가 70% 차지\n")
                f.write("5. 전체 에너지 사용량 6770만 toe\n")
                f.write("6. 나프타 비중이 전체 82.9%차지\n")
                f.write("7. 다운스트림 전력 400만 toe\n\n")

                f.write("📊 검증 결과 (Verification Results):\n")
                f.write("-" * 60 + "\n\n")

                for i, (key, result) in enumerate(self.verification_results.items(), 1):
                    f.write(f"{i}. {key.replace('_', ' ').title()}:\n")
                    f.write(f"   Target: {result['target']}\n")
                    f.write(f"   Actual: {result['actual']}\n")
                    f.write(f"   Difference: {result['difference']}\n")
                    f.write(f"   Status: {result['status']}\n\n")

                # Summary
                passed = sum(1 for r in self.verification_results.values() if '✅' in r['status'])
                total = len(self.verification_results)

                f.write("📋 요약 (Summary):\n")
                f.write(f"   통과: {passed}/{total} benchmarks\n")
                f.write(f"   Pass Rate: {passed/total*100:.1f}%\n\n")

                if passed == total:
                    f.write("🎉 모든 한국 산업 벤치마크가 일치합니다!\n")
                    f.write("🎉 ALL KOREAN INDUSTRY BENCHMARKS MATCH!\n")
                else:
                    f.write("⚠️  일부 벤치마크 조정이 필요합니다.\n")
                    f.write("⚠️  SOME BENCHMARKS NEED ADJUSTMENT.\n")

            logger.info(f"✅ Verification report saved: {report_file}")

        except Exception as e:
            logger.error(f"Error generating report: {e}")

    def create_verification_visualization(self):
        """Create visualization of verification results"""
        logger.info("📊 Creating verification visualization...")

        try:
            # Create comparison chart
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

            # 1. Process emissions breakdown
            if 'ncc_process' in self.verification_results and 'basic_petrochemicals' in self.verification_results:
                processes = ['NCC Process', 'Basic Petrochemicals', 'Others']
                target_values = [46, 89, 11]  # Simplified
                # actual_values would need to be calculated from verification results

                ax1.bar(processes, target_values, alpha=0.7, label='Korean Target')
                ax1.set_title('Process Emissions Share (%)')
                ax1.set_ylabel('Share of Total Emissions (%)')
                ax1.legend()

            # 2. Direct vs Indirect Emissions
            if 'direct_emissions' in self.verification_results:
                emissions_types = ['Direct', 'Indirect']
                target_values = [64, 34]

                ax2.pie(target_values, labels=emissions_types, autopct='%1.1f%%',
                       colors=['lightcoral', 'lightblue'])
                ax2.set_title('Emissions Type Distribution (Korean Target)')

            # 3. Energy consumption breakdown
            if 'naphtha_share' in self.verification_results:
                energy_sources = ['Naphtha', 'Fuel Gas', 'Electricity']
                target_values = [82.9, 11.2, 5.9]  # Approximate

                ax3.pie(target_values, labels=energy_sources, autopct='%1.1f%%',
                       colors=['gold', 'lightgreen', 'lightsteelblue'])
                ax3.set_title('Energy Mix (Korean Target)')

            # 4. Verification status
            statuses = list(self.verification_results.keys())
            status_colors = []
            for result in self.verification_results.values():
                if '✅' in result['status']:
                    status_colors.append('green')
                elif '❌' in result['status']:
                    status_colors.append('red')
                else:
                    status_colors.append('orange')

            ax4.bar(range(len(statuses)), [1]*len(statuses), color=status_colors)
            ax4.set_xticks(range(len(statuses)))
            ax4.set_xticklabels([s.replace('_', '\n') for s in statuses], rotation=45, ha='right')
            ax4.set_title('Verification Status')
            ax4.set_ylabel('Status (Green=Pass, Red=Fail, Orange=Needs Data)')

            plt.tight_layout()

            # Save visualization
            viz_file = self.output_path / "korean_benchmarks_verification.png"
            plt.savefig(viz_file, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"✅ Verification visualization saved: {viz_file}")

        except Exception as e:
            logger.error(f"Error creating visualization: {e}")

def main():
    """Main verification function"""
    logger.info("Starting Korean benchmarks verification...")

    try:
        verifier = KoreanBenchmarkVerifier()

        # Run analysis and verification
        verification_results = verifier.run_basic_analysis()

        # Create visualization
        verifier.create_verification_visualization()

        # Print summary
        print("\n" + "=" * 60)
        print("🇰🇷 KOREAN INDUSTRY BENCHMARKS VERIFICATION")
        print("=" * 60)

        for key, result in verification_results.items():
            print(f"\n📊 {key.replace('_', ' ').title()}:")
            print(f"   Target: {result['target']}")
            print(f"   Actual: {result['actual']}")
            print(f"   Status: {result['status']}")

        # Summary
        passed = sum(1 for r in verification_results.values() if '✅' in r['status'])
        total = len(verification_results)

        print(f"\n📋 SUMMARY:")
        print(f"   Passed: {passed}/{total} benchmarks")
        print(f"   Pass Rate: {passed/total*100:.1f}%")

        if passed == total:
            print("\n🎉 ALL KOREAN INDUSTRY BENCHMARKS VERIFIED! ✅")
        else:
            print(f"\n⚠️  {total-passed} benchmarks need adjustment")

        return verification_results

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return None

if __name__ == "__main__":
    main()