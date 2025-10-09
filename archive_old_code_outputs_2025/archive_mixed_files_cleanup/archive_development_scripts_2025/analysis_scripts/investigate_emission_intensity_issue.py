#!/usr/bin/env python3
"""
Investigate why total emissions are 261.5 MtCO2 instead of expected ~52 MtCO2
Check emission intensities and energy intensities against industry benchmarks
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmissionIntensityInvestigator:
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "data"
        self.excel_file = self.data_path / "Korean_Petrochemical_MACC_Model_English.xlsx"
        self.output_path = Path(__file__).parent.parent / "outputs" / "emission_intensity_investigation"

        # Korean industry benchmarks for comparison
        self.korean_industry_facts = {
            'total_emissions_mt': 52.0,  # Actual Korean petrochemical emissions ~52 Mt
            'total_energy_toe': 67.7e6,  # 67.7 million toe
            'naphtha_share': 0.829,      # 82.9%
        }

        # Typical industry emission intensities (research-based)
        self.typical_intensities = {
            'naphtha_cracker': {
                'energy_gj_per_t': 30-35,      # Typical range for steam cracking
                'emissions_tco2_per_t': 1.5-2.5, # Typical range for ethylene production
                'description': 'Steam cracking of naphtha to produce ethylene/propylene'
            },
            'btx_plant': {
                'energy_gj_per_t': 15-25,      # Reforming and separation
                'emissions_tco2_per_t': 0.8-1.5, # BTX production
                'description': 'Catalytic reforming and aromatics extraction'
            },
            'polyethylene': {
                'energy_gj_per_t': 20-28,      # Polymerization
                'emissions_tco2_per_t': 1.0-1.8, # PE production
                'description': 'Ethylene polymerization'
            },
            'polypropylene': {
                'energy_gj_per_t': 18-25,      # Polymerization
                'emissions_tco2_per_t': 1.2-2.0, # PP production
                'description': 'Propylene polymerization'
            }
        }

    def investigate_intensity_discrepancy(self):
        """Investigate why emissions are ~5x higher than expected"""
        logger.info("🔍 Investigating emission intensity discrepancy...")

        try:
            # Load model data
            model_data = self.load_model_data()

            # Analyze current intensities in model
            current_intensities = self.analyze_current_intensities(model_data)

            # Compare with industry benchmarks
            comparison = self.compare_with_benchmarks(current_intensities)

            # Calculate corrected emission factors
            corrected_factors = self.calculate_corrected_factors()

            # Generate investigation report
            self.generate_investigation_report(current_intensities, comparison, corrected_factors)

            return current_intensities, comparison, corrected_factors

        except Exception as e:
            logger.error(f"Investigation failed: {e}")
            raise

    def load_model_data(self):
        """Load relevant model data for analysis"""
        logger.info("📊 Loading model data...")

        model_data = {}

        try:
            # Load key sheets
            sheets = ['source_Original', 'CI_Corrected', 'CI2_Corrected', 'utilities_Original']

            for sheet in sheets:
                try:
                    model_data[sheet] = pd.read_excel(self.excel_file, sheet_name=sheet)
                    logger.info(f"✅ Loaded {sheet}: {model_data[sheet].shape}")
                except Exception as e:
                    logger.warning(f"Could not load {sheet}: {e}")

            return model_data

        except Exception as e:
            logger.error(f"Error loading model data: {e}")
            raise

    def analyze_current_intensities(self, model_data):
        """Analyze current emission and energy intensities in the model"""
        logger.info("🔬 Analyzing current intensities...")

        intensities = {
            'facilities': [],
            'emission_factors': {},
            'energy_intensities': {},
            'summary_stats': {}
        }

        try:
            # Analyze facility-level data
            if 'source_Original' in model_data:
                facilities = model_data['source_Original']

                for _, facility in facilities.iterrows():
                    facility_analysis = {
                        'company': facility.get('Company', 'Unknown'),
                        'process': facility.get('Process', 'Unknown'),
                        'capacity_kt': facility.get('capacity_1000_t', 0),
                        'location': facility.get('Location', 'Unknown')
                    }
                    intensities['facilities'].append(facility_analysis)

                # Calculate aggregate stats by process
                if 'Process' in facilities.columns and 'capacity_1000_t' in facilities.columns:
                    process_stats = facilities.groupby('Process')['capacity_1000_t'].agg(['sum', 'count', 'mean'])
                    intensities['facility_stats'] = process_stats

            # Analyze CI data (Carbon Intensity factors)
            if 'CI_Corrected' in model_data:
                ci_data = model_data['CI_Corrected']

                # Extract emission intensities by process
                for _, row in ci_data.iterrows():
                    if len(row) > 0:
                        process_name = str(row.iloc[0])

                        # Look for energy consumption columns
                        energy_cols = [col for col in ci_data.columns if any(term in str(col).lower()
                                     for term in ['gj_per_t', 'energy', 'fuel', 'naphtha', 'electricity'])]

                        if energy_cols:
                            process_energy = {}
                            for col in energy_cols:
                                if pd.notna(row[col]):
                                    process_energy[col] = row[col]

                            if process_energy:
                                intensities['energy_intensities'][process_name] = process_energy

            # Analyze CI2 data (Emission factors)
            if 'CI2_Corrected' in model_data:
                ci2_data = model_data['CI2_Corrected']

                for _, row in ci2_data.iterrows():
                    if len(row) > 0:
                        factor_name = str(row.iloc[0])

                        # Look for emission factor columns
                        emission_cols = [col for col in ci2_data.columns if any(term in str(col).lower()
                                       for term in ['tco2', 'emission', 'factor'])]

                        if emission_cols:
                            factor_values = {}
                            for col in emission_cols:
                                if pd.notna(row[col]):
                                    factor_values[col] = row[col]

                            if factor_values:
                                intensities['emission_factors'][factor_name] = factor_values

            logger.info(f"Found {len(intensities['facilities'])} facilities")
            logger.info(f"Found {len(intensities['energy_intensities'])} energy intensity profiles")
            logger.info(f"Found {len(intensities['emission_factors'])} emission factors")

            return intensities

        except Exception as e:
            logger.error(f"Error analyzing intensities: {e}")
            return intensities

    def compare_with_benchmarks(self, current_intensities):
        """Compare current model intensities with industry benchmarks"""
        logger.info("📏 Comparing with industry benchmarks...")

        comparison = {
            'process_comparisons': {},
            'overall_assessment': {},
            'identified_issues': []
        }

        try:
            # Compare energy intensities
            for process, energy_data in current_intensities['energy_intensities'].items():
                process_lower = process.lower()

                # Match to typical intensities
                matched_benchmark = None
                for benchmark_name, benchmark_data in self.typical_intensities.items():
                    if any(term in process_lower for term in benchmark_name.split('_')):
                        matched_benchmark = benchmark_name
                        break

                if matched_benchmark:
                    benchmark = self.typical_intensities[matched_benchmark]

                    # Calculate total energy from model
                    total_model_energy = 0
                    for col, value in energy_data.items():
                        if 'gj_per_t' in col.lower():
                            total_model_energy += value

                    # Compare with benchmark range
                    benchmark_min = benchmark['energy_gj_per_t'].split('-')[0] if isinstance(benchmark['energy_gj_per_t'], str) else benchmark['energy_gj_per_t']
                    benchmark_max = benchmark['energy_gj_per_t'].split('-')[1] if isinstance(benchmark['energy_gj_per_t'], str) else benchmark['energy_gj_per_t']

                    try:
                        benchmark_min = float(str(benchmark_min).replace(')', '').replace('(', ''))
                        benchmark_max = float(str(benchmark_max).replace(')', '').replace('(', ''))

                        comparison['process_comparisons'][process] = {
                            'model_energy_intensity': total_model_energy,
                            'benchmark_range': f"{benchmark_min}-{benchmark_max}",
                            'ratio_to_benchmark': total_model_energy / ((benchmark_min + benchmark_max) / 2),
                            'assessment': 'HIGH' if total_model_energy > benchmark_max * 1.5 else
                                        'NORMAL' if benchmark_min <= total_model_energy <= benchmark_max * 1.2 else
                                        'REVIEW_NEEDED'
                        }

                        if total_model_energy > benchmark_max * 1.5:
                            comparison['identified_issues'].append(
                                f"{process}: Energy intensity {total_model_energy:.1f} GJ/t is {total_model_energy/((benchmark_min+benchmark_max)/2):.1f}x typical range"
                            )

                    except (ValueError, TypeError) as e:
                        logger.warning(f"Could not parse benchmark for {process}: {e}")

            # Calculate overall emission intensity
            if current_intensities.get('facilities'):
                total_capacity = sum(f['capacity_kt'] for f in current_intensities['facilities'])

                # From our analysis, total emissions = 261.5 Mt, total capacity ≈ 100,066 kt
                if total_capacity > 0:
                    avg_emission_intensity = 261.5 * 1000 / total_capacity  # tCO2/t

                    comparison['overall_assessment'] = {
                        'total_emissions_mt': 261.5,
                        'total_capacity_kt': total_capacity,
                        'avg_intensity_tco2_per_t': avg_emission_intensity,
                        'target_emissions_mt': self.korean_industry_facts['total_emissions_mt'],
                        'intensity_multiplier': 261.5 / self.korean_industry_facts['total_emissions_mt'],
                        'assessment': f"Emissions are {261.5/52:.1f}x higher than Korean industry reality"
                    }

                    comparison['identified_issues'].append(
                        f"MAJOR ISSUE: Total emissions {261.5:.1f} Mt vs expected {self.korean_industry_facts['total_emissions_mt']:.1f} Mt"
                    )
                    comparison['identified_issues'].append(
                        f"Average emission intensity {avg_emission_intensity:.2f} tCO2/t seems too high for petrochemical industry"
                    )

            return comparison

        except Exception as e:
            logger.error(f"Error in benchmark comparison: {e}")
            return comparison

    def calculate_corrected_factors(self):
        """Calculate corrected emission factors to match Korean industry totals"""
        logger.info("🎯 Calculating corrected emission factors...")

        corrected_factors = {
            'scaling_factor': 1.0,
            'corrected_intensities': {},
            'rationale': []
        }

        try:
            # Calculate required scaling factor
            current_total = 261.5  # Mt
            target_total = self.korean_industry_facts['total_emissions_mt']  # 52 Mt

            scaling_factor = target_total / current_total
            corrected_factors['scaling_factor'] = scaling_factor

            corrected_factors['rationale'] = [
                f"Current model total: {current_total:.1f} MtCO2",
                f"Korean industry target: {target_total:.1f} MtCO2",
                f"Required scaling factor: {scaling_factor:.3f}",
                "This suggests emission factors in model are ~5x too high",
                "Possible causes: Double counting, wrong units, inflated factors"
            ]

            # Suggest corrected intensities for main processes
            typical_corrected = {
                'Naphtha Cracker': {
                    'current_estimated': 11.91,  # From previous analysis
                    'corrected': 11.91 * scaling_factor,
                    'industry_typical': '1.5-2.5 tCO2/t ethylene'
                },
                'BTX Plant': {
                    'current_estimated': 4.96,   # From previous analysis
                    'corrected': 4.96 * scaling_factor,
                    'industry_typical': '0.8-1.5 tCO2/t aromatics'
                }
            }

            corrected_factors['corrected_intensities'] = typical_corrected

            return corrected_factors

        except Exception as e:
            logger.error(f"Error calculating corrections: {e}")
            return corrected_factors

    def generate_investigation_report(self, current_intensities, comparison, corrected_factors):
        """Generate comprehensive investigation report"""
        logger.info("📋 Generating investigation report...")

        try:
            self.output_path.mkdir(parents=True, exist_ok=True)

            report_file = self.output_path / "emission_intensity_investigation_report.txt"

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("KOREAN PETROCHEMICAL EMISSION INTENSITY INVESTIGATION\n")
                f.write("=" * 80 + "\n\n")

                f.write("🚨 PROBLEM IDENTIFIED:\n")
                f.write(f"   Model emissions: 261.5 MtCO₂\n")
                f.write(f"   Korean reality: ~{self.korean_industry_facts['total_emissions_mt']} MtCO₂\n")
                f.write(f"   Discrepancy: {261.5/52:.1f}x higher than expected\n\n")

                f.write("🔍 ROOT CAUSE ANALYSIS:\n")
                f.write("-" * 50 + "\n")

                # Issues identified
                if comparison.get('identified_issues'):
                    f.write("Issues Found:\n")
                    for i, issue in enumerate(comparison['identified_issues'], 1):
                        f.write(f"{i}. {issue}\n")
                    f.write("\n")

                # Process comparisons
                if comparison.get('process_comparisons'):
                    f.write("Process Intensity Analysis:\n")
                    for process, data in comparison['process_comparisons'].items():
                        f.write(f"   {process}:\n")
                        f.write(f"     Model: {data['model_energy_intensity']:.1f} GJ/t\n")
                        f.write(f"     Benchmark: {data['benchmark_range']} GJ/t\n")
                        f.write(f"     Ratio: {data['ratio_to_benchmark']:.1f}x\n")
                        f.write(f"     Status: {data['assessment']}\n\n")

                # Overall assessment
                if comparison.get('overall_assessment'):
                    oa = comparison['overall_assessment']
                    f.write("Overall Assessment:\n")
                    f.write(f"   Avg emission intensity: {oa['avg_intensity_tco2_per_t']:.2f} tCO₂/t\n")
                    f.write(f"   Total capacity: {oa['total_capacity_kt']:,.0f} kt\n")
                    f.write(f"   Intensity multiplier: {oa['intensity_multiplier']:.1f}x\n")
                    f.write(f"   Assessment: {oa['assessment']}\n\n")

                f.write("🎯 RECOMMENDED CORRECTIONS:\n")
                f.write("-" * 50 + "\n")
                for rationale in corrected_factors['rationale']:
                    f.write(f"• {rationale}\n")

                f.write(f"\n📊 CORRECTED INTENSITIES:\n")
                if corrected_factors.get('corrected_intensities'):
                    for process, data in corrected_factors['corrected_intensities'].items():
                        f.write(f"   {process}:\n")
                        f.write(f"     Current: {data['current_estimated']:.2f} tCO₂/t\n")
                        f.write(f"     Corrected: {data['corrected']:.2f} tCO₂/t\n")
                        f.write(f"     Industry typical: {data['industry_typical']}\n\n")

                f.write("🔧 NEXT STEPS:\n")
                f.write("-" * 30 + "\n")
                f.write("1. Review emission factor sources in CI_Corrected and CI2_Corrected sheets\n")
                f.write("2. Check for unit conversion errors (kt vs t, GJ vs MJ, etc.)\n")
                f.write("3. Verify against Korean petrochemical plant data\n")
                f.write("4. Apply scaling factor or recalibrate base emission factors\n")
                f.write("5. Validate against 52 MtCO₂ Korean industry total\n")

            logger.info(f"✅ Investigation report saved: {report_file}")

        except Exception as e:
            logger.error(f"Error generating report: {e}")

def main():
    """Main investigation function"""
    logger.info("🚨 Starting emission intensity investigation...")

    try:
        investigator = EmissionIntensityInvestigator()
        current_intensities, comparison, corrected_factors = investigator.investigate_intensity_discrepancy()

        print("\n" + "=" * 60)
        print("🚨 EMISSION INTENSITY INVESTIGATION RESULTS")
        print("=" * 60)

        print(f"\n📊 PROBLEM SUMMARY:")
        print(f"   Model Total: 261.5 MtCO₂")
        print(f"   Korean Reality: ~52 MtCO₂")
        print(f"   Discrepancy: {261.5/52:.1f}x higher")

        print(f"\n🎯 ROOT CAUSE:")
        print(f"   Emission intensities appear ~5x too high")
        print(f"   Required scaling factor: {corrected_factors['scaling_factor']:.3f}")

        print(f"\n🔧 RECOMMENDED ACTION:")
        print(f"   Scale down all emission factors by {corrected_factors['scaling_factor']:.3f}")
        print(f"   OR investigate source data for errors")

        return current_intensities, comparison, corrected_factors

    except Exception as e:
        logger.error(f"Investigation failed: {e}")
        return None, None, None

if __name__ == "__main__":
    main()