#!/usr/bin/env python3
"""
Deep analysis of each Excel sheet's purpose and logic before Korean calibration
Understanding the model structure and dependencies is crucial for proper calibration
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelSheetLogicAnalyzer:
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "data"
        self.excel_file = self.data_path / "Korean_Petrochemical_MACC_Model_English.xlsx"
        self.output_path = Path(__file__).parent.parent / "outputs" / "korean_calibrated_baseline"

        # Korean benchmarks for reference
        self.korean_benchmarks = {
            'total_energy_toe': 67_700_000,  # 67.7 million toe
            'naphtha_share': 0.829,          # 82.9%
            'ncc_ghg_share': 0.46,           # 46% of GHG from NCC
            'direct_emission_share': 0.64,   # 64% direct emissions
            'indirect_emission_share': 0.34, # 34% indirect emissions
        }

    def analyze_all_sheets(self):
        """Analyze purpose and logic of each sheet"""
        logger.info("🔍 Deep analysis of Excel sheet logic...")

        try:
            # Load all sheets
            excel_data = pd.read_excel(self.excel_file, sheet_name=None)

            analysis_results = {}

            for sheet_name, df in excel_data.items():
                logger.info(f"Analyzing sheet: {sheet_name}")
                sheet_analysis = self.analyze_sheet_purpose(sheet_name, df)
                analysis_results[sheet_name] = sheet_analysis

            # Determine calibration strategy
            calibration_strategy = self.determine_calibration_strategy(analysis_results)

            # Save analysis
            self.save_analysis_results(analysis_results, calibration_strategy)

            return analysis_results, calibration_strategy

        except Exception as e:
            logger.error(f"Error analyzing sheets: {e}")
            raise

    def analyze_sheet_purpose(self, sheet_name, df):
        """Analyze the purpose and logic of a specific sheet"""

        analysis = {
            'sheet_name': sheet_name,
            'dimensions': df.shape,
            'column_types': {},
            'data_patterns': {},
            'likely_purpose': '',
            'calibration_approach': '',
            'dependencies': [],
            'should_modify': False,
            'modification_type': 'none'
        }

        # Analyze column patterns
        for col in df.columns:
            col_str = str(col).lower()

            # Categorize column types
            if any(term in col_str for term in ['capacity', 'production', 'volume', 'throughput']):
                analysis['column_types']['capacity_data'] = analysis['column_types'].get('capacity_data', []) + [col]

            elif any(term in col_str for term in ['emission', 'co2', 'ghg']):
                if any(term in col_str for term in ['factor', 'intensity', 'per_t', 'per_gj']):
                    analysis['column_types']['emission_factors'] = analysis['column_types'].get('emission_factors', []) + [col]
                else:
                    analysis['column_types']['emission_totals'] = analysis['column_types'].get('emission_totals', []) + [col]

            elif any(term in col_str for term in ['energy', 'fuel', 'naphtha', 'electricity']):
                if any(term in col_str for term in ['per_t', 'per_gj', 'intensity', 'factor']):
                    analysis['column_types']['energy_intensities'] = analysis['column_types'].get('energy_intensities', []) + [col]
                else:
                    analysis['column_types']['energy_consumption'] = analysis['column_types'].get('energy_consumption', []) + [col]

            elif any(term in col_str for term in ['cost', 'capex', 'opex', 'usd']):
                analysis['column_types']['economic_data'] = analysis['column_types'].get('economic_data', []) + [col]

            elif any(term in col_str for term in ['tech', 'alternative', 'abatement']):
                analysis['column_types']['technology_data'] = analysis['column_types'].get('technology_data', []) + [col]

        # Determine sheet purpose based on name and content
        analysis['likely_purpose'] = self.determine_sheet_purpose(sheet_name, analysis['column_types'])

        # Determine calibration approach
        analysis['calibration_approach'] = self.determine_sheet_calibration_approach(
            sheet_name, analysis['likely_purpose'], analysis['column_types']
        )

        return analysis

    def determine_sheet_purpose(self, sheet_name, column_types):
        """Determine the likely purpose of a sheet based on name and columns"""

        name_lower = sheet_name.lower()

        # Base data sheets
        if any(term in name_lower for term in ['ci_corrected', 'ci2_corrected']):
            return 'emission_factors_base_data'
        elif 'source_original' in name_lower:
            return 'facility_capacity_base_data'
        elif 'utilities_original' in name_lower:
            return 'utility_process_base_data'
        elif 'baseline_assumptions' in name_lower:
            return 'baseline_parameters'

        # Template sheets
        elif 'macc_template' in name_lower:
            return 'macc_calculation_template'
        elif 'techoptions' in name_lower:
            return 'technology_options_template'

        # Time-based projections
        elif any(year in name_lower for year in ['2030', '2040', '2050']):
            if 'facility_projections' in name_lower:
                return 'facility_capacity_projection'
            elif 'macc_' in name_lower:
                return 'macc_results_by_year'
            else:
                return 'temporal_scenario'

        # Results and analysis
        elif 'summary' in name_lower:
            return 'results_summary'
        elif 'comparison' in name_lower:
            return 'comparative_analysis'
        elif 'retirement' in name_lower:
            return 'facility_retirement_schedule'
        elif 'availability' in name_lower:
            return 'technology_availability'
        elif 'master' in name_lower:
            return 'master_technology_database'

        # Specific analysis
        elif 'naphtha_emission' in name_lower:
            return 'naphtha_emission_breakdown'
        elif 'emissions_target' in name_lower:
            return 'emission_targets'
        elif 'techlinks' in name_lower:
            return 'technology_linkages'

        else:
            return 'unknown_purpose'

    def determine_sheet_calibration_approach(self, sheet_name, purpose, column_types):
        """Determine how to calibrate each sheet based on its purpose"""

        # Base data sheets - these should be calibrated
        if purpose == 'facility_capacity_base_data':
            return 'calibrate_capacity_to_match_korean_totals'
        elif purpose == 'baseline_parameters':
            return 'calibrate_baseline_assumptions'

        # Factor/intensity sheets - these should NOT be calibrated (physical constants)
        elif purpose == 'emission_factors_base_data':
            return 'do_not_modify_emission_factors'
        elif purpose == 'utility_process_base_data':
            return 'do_not_modify_process_intensities'

        # Templates - should not be modified directly
        elif 'template' in purpose:
            return 'do_not_modify_templates'

        # Results and calculations - should be recalculated, not modified
        elif any(term in purpose for term in ['results', 'macc_results', 'summary']):
            return 'recalculate_from_base_data'

        # Projections - may need scaling if based on base year
        elif 'projection' in purpose:
            return 'scale_proportionally_from_base_year'

        # Technology data - costs and performance should not change
        elif any(term in purpose for term in ['technology', 'master']):
            return 'do_not_modify_technology_costs'

        # Targets - may need adjustment to Korean policy
        elif 'target' in purpose:
            return 'adjust_to_korean_policy_targets'

        else:
            return 'analyze_dependencies_first'

    def determine_calibration_strategy(self, analysis_results):
        """Determine overall calibration strategy based on sheet analysis"""

        strategy = {
            'phase_1_base_data': [],      # Sheets to calibrate first
            'phase_2_recalculate': [],    # Sheets to recalculate after phase 1
            'phase_3_verify': [],         # Sheets to verify final results
            'do_not_modify': [],          # Sheets that should never be modified
            'korean_benchmarks_target': self.korean_benchmarks,
            'calibration_sequence': []
        }

        for sheet_name, analysis in analysis_results.items():
            approach = analysis['calibration_approach']

            if 'calibrate' in approach and 'base_data' in analysis['likely_purpose']:
                strategy['phase_1_base_data'].append({
                    'sheet': sheet_name,
                    'approach': approach,
                    'purpose': analysis['likely_purpose']
                })

            elif 'recalculate' in approach:
                strategy['phase_2_recalculate'].append({
                    'sheet': sheet_name,
                    'approach': approach,
                    'purpose': analysis['likely_purpose']
                })

            elif 'do_not_modify' in approach:
                strategy['do_not_modify'].append({
                    'sheet': sheet_name,
                    'reason': approach,
                    'purpose': analysis['likely_purpose']
                })

            elif any(term in approach for term in ['verify', 'summary', 'results']):
                strategy['phase_3_verify'].append({
                    'sheet': sheet_name,
                    'approach': approach,
                    'purpose': analysis['likely_purpose']
                })

        # Define calibration sequence
        strategy['calibration_sequence'] = [
            "1. Calibrate base facility capacities (source_Original sheet)",
            "2. Update baseline assumptions to Korean benchmarks",
            "3. Recalculate all derived values (emissions, energy consumption)",
            "4. Verify results match Korean industry statistics",
            "5. Do NOT modify emission factors or technology costs"
        ]

        return strategy

    def save_analysis_results(self, analysis_results, calibration_strategy):
        """Save detailed analysis results"""

        try:
            # Create detailed analysis report
            report_file = self.output_path / "excel_sheet_logic_analysis.txt"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            with open(report_file, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("EXCEL SHEET LOGIC ANALYSIS FOR KOREAN CALIBRATION\n")
                f.write("=" * 80 + "\n\n")

                f.write("🎯 KOREAN INDUSTRY BENCHMARKS TO ACHIEVE:\n")
                for key, value in self.korean_benchmarks.items():
                    f.write(f"   {key}: {value}\n")
                f.write("\n")

                f.write("📊 SHEET-BY-SHEET ANALYSIS:\n")
                f.write("-" * 50 + "\n")

                for sheet_name, analysis in analysis_results.items():
                    f.write(f"\n🔍 SHEET: {sheet_name}\n")
                    f.write(f"   Purpose: {analysis['likely_purpose']}\n")
                    f.write(f"   Dimensions: {analysis['dimensions']}\n")
                    f.write(f"   Calibration Approach: {analysis['calibration_approach']}\n")

                    if analysis['column_types']:
                        f.write("   Column Types:\n")
                        for col_type, cols in analysis['column_types'].items():
                            f.write(f"     {col_type}: {len(cols)} columns\n")
                    f.write("\n")

                f.write("🚀 RECOMMENDED CALIBRATION STRATEGY:\n")
                f.write("-" * 50 + "\n")

                f.write("\n📋 CALIBRATION SEQUENCE:\n")
                for i, step in enumerate(calibration_strategy['calibration_sequence'], 1):
                    f.write(f"{step}\n")

                f.write(f"\n✅ PHASE 1 - BASE DATA CALIBRATION ({len(calibration_strategy['phase_1_base_data'])} sheets):\n")
                for item in calibration_strategy['phase_1_base_data']:
                    f.write(f"   {item['sheet']}: {item['approach']}\n")

                f.write(f"\n🔄 PHASE 2 - RECALCULATE ({len(calibration_strategy['phase_2_recalculate'])} sheets):\n")
                for item in calibration_strategy['phase_2_recalculate']:
                    f.write(f"   {item['sheet']}: {item['approach']}\n")

                f.write(f"\n🚫 DO NOT MODIFY ({len(calibration_strategy['do_not_modify'])} sheets):\n")
                for item in calibration_strategy['do_not_modify']:
                    f.write(f"   {item['sheet']}: {item['reason']}\n")

                f.write(f"\n✔️  PHASE 3 - VERIFICATION ({len(calibration_strategy['phase_3_verify'])} sheets):\n")
                for item in calibration_strategy['phase_3_verify']:
                    f.write(f"   {item['sheet']}: {item['approach']}\n")

            # Save as JSON for programmatic use
            import json
            json_file = self.output_path / "excel_sheet_analysis.json"

            analysis_data = {
                'sheet_analysis': analysis_results,
                'calibration_strategy': calibration_strategy,
                'korean_benchmarks': self.korean_benchmarks
            }

            with open(json_file, 'w') as f:
                json.dump(analysis_data, f, indent=2, default=str)

            logger.info(f"✅ Analysis saved: {report_file}")
            logger.info(f"📄 JSON data: {json_file}")

        except Exception as e:
            logger.error(f"Error saving analysis: {e}")

def main():
    """Main analysis function"""
    logger.info("Starting deep Excel sheet logic analysis...")

    try:
        analyzer = ExcelSheetLogicAnalyzer()
        analysis_results, calibration_strategy = analyzer.analyze_all_sheets()

        print("\n" + "=" * 60)
        print("🧠 EXCEL SHEET LOGIC ANALYSIS COMPLETE")
        print("=" * 60)

        print(f"\n📊 Analyzed {len(analysis_results)} sheets")
        print(f"✅ Phase 1 (Base Data): {len(calibration_strategy['phase_1_base_data'])} sheets")
        print(f"🔄 Phase 2 (Recalculate): {len(calibration_strategy['phase_2_recalculate'])} sheets")
        print(f"🚫 Do Not Modify: {len(calibration_strategy['do_not_modify'])} sheets")

        print("\n🎯 KEY INSIGHT:")
        print("Korean calibration should modify BASE CAPACITY data, not emission factors!")
        print("Let the model recalculate emissions from calibrated inputs.")

        print("\n📋 NEXT STEPS:")
        for step in calibration_strategy['calibration_sequence']:
            print(f"   {step}")

        return analysis_results, calibration_strategy

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return None, None

if __name__ == "__main__":
    main()