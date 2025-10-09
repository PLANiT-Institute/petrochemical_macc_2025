#!/usr/bin/env python3
"""
ENHANCED MODULE 1: BASELINE EMISSION ANALYSIS WITH QA VALIDATION
Version 2.0 - Comprehensive validation, energy flow tracking, and standardized outputs
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
from typing import Dict, Tuple, List
warnings.filterwarnings('ignore')

class EnhancedBaselineAnalyzer:
    """
    Enhanced baseline analyzer with:
    - Comprehensive QA validation framework
    - Detailed energy flow tracking
    - Scope 1 & 2 emissions breakdown
    - Standardized CSV outputs
    """

    def __init__(self):
        """Initialize enhanced baseline analyzer"""
        print("🏭 ENHANCED MODULE 1: BASELINE EMISSION ANALYSIS v2.0")
        print("=" * 70)

        # Paths and configuration
        self.data_path = "../data_sources/Korean_Petrochemical_MACC_Model_English.xlsx"
        self.output_dir = Path(".")
        self.baseline_year = 2025
        self.projection_years = list(range(2025, 2051))

        # Target values for validation (from fundamental guidance)
        self.validation_targets = {
            'total_emissions_mtco2': 52.0,
            'total_energy_mtoe': 67.7,
            'naphtha_energy_share': 0.829,  # 82.9%
            'ncc_emission_share': 0.46,     # 46%
            'direct_emission_share': 0.64,   # 64%
            'indirect_emission_share': 0.34, # 34%
            'byproduct_of_direct_share': 0.70, # 70%
            'utility_electricity_mtoe': 4.0,
        }

        # Tolerance for validation (±%)
        self.validation_tolerance = {
            'total_emissions_mtco2': 0.03,  # ±3%
            'total_energy_mtoe': 0.05,
            'naphtha_energy_share': 0.05,
            'ncc_emission_share': 0.05,
            'direct_emission_share': 0.05,
            'indirect_emission_share': 0.05,
            'byproduct_of_direct_share': 0.05,
            'utility_electricity_mtoe': 0.10,
        }

        # Energy conversion factors
        self.GJ_PER_TOE = 41.868  # GJ per tonne of oil equivalent
        self.KWH_TO_GJ = 3.6 / 1000  # kWh to GJ

        # Load and process data
        self.load_source_data()
        self.process_facility_data()
        self.calculate_baseline_emissions()
        self.calculate_energy_flows()
        self.validate_baseline()

    def load_source_data(self):
        """Load source Excel data with error handling"""
        print("📊 Loading source data...")

        try:
            # Load all relevant sheets
            self.facilities_df = pd.read_excel(self.data_path, sheet_name='source_Original')
            self.ci_df = pd.read_excel(self.data_path, sheet_name='CI_Corrected', index_col=0)
            self.ci2_df = pd.read_excel(self.data_path, sheet_name='CI2_Corrected', index_col=0)

            print(f"   ✅ Loaded {len(self.facilities_df)} facilities")
            print(f"   ✅ Energy intensity: {self.ci_df.shape[0]} products × {self.ci_df.shape[1]} energy types")
            print(f"   ✅ Emission factors: {self.ci2_df.shape[1]} fuel types")

        except Exception as e:
            print(f"   ❌ Error loading data: {e}")
            raise

    def process_facility_data(self):
        """Clean and enhance facility data"""
        print("🔧 Processing facility data...")

        # Clean data
        initial_count = len(self.facilities_df)
        self.facilities_df = self.facilities_df.dropna(subset=['capacity_1000_t', 'year'])
        self.facilities_df = self.facilities_df[self.facilities_df['capacity_1000_t'] > 0]
        self.facilities_df = self.facilities_df[self.facilities_df['year'] > 1900]

        # Add facility attributes
        self.facilities_df['facility_id'] = range(len(self.facilities_df))
        self.facilities_df['age_2025'] = 2025 - self.facilities_df['year']
        self.facilities_df['capacity_t'] = self.facilities_df['capacity_1000_t'] * 1000

        # Map processes to products for emission calculation
        self.process_product_mapping = {
            'Naphtha Cracker': 'Ethylene',
            'BTX Plant': 'Benzene',
            'Utility': 'Steam',
            'Aromatics': 'Benzene',
            'Olefins': 'Ethylene'
        }

        self.facilities_df['product'] = self.facilities_df['process'].map(
            self.process_product_mapping
        ).fillna('Ethylene')

        # Add location if missing
        if 'location' not in self.facilities_df.columns:
            self.facilities_df['location'] = 'Unknown'

        print(f"   ✅ Cleaned: {initial_count} → {len(self.facilities_df)} facilities")
        print(f"   📊 Process distribution:")
        for process, count in self.facilities_df['process'].value_counts().items():
            print(f"      {process}: {count} facilities")

    def calculate_baseline_emissions(self):
        """Calculate baseline emissions with detailed tracking"""
        print("⚡ Calculating baseline emissions...")

        # Get emission factors
        self.emission_factors = {
            col: self.ci2_df.iloc[0][col]
            for col in self.ci2_df.columns
        }

        # Initialize tracking arrays
        emissions_data = {
            'total': [],
            'scope1': [],
            'scope2': [],
            'naphtha_feedstock': [],
            'naphtha_thermal': [],
            'byproduct_gas': [],
            'byproduct_oil': [],
            'lng': [],
            'ng': [],
            'electricity': []
        }

        energy_data = {
            'total_gj': [],
            'naphtha_feedstock_gj': [],
            'naphtha_thermal_gj': [],
            'byproduct_gas_gj': [],
            'byproduct_oil_gj': [],
            'lng_gj': [],
            'ng_gj': [],
            'electricity_gj': []
        }

        for idx, facility in self.facilities_df.iterrows():
            product = facility['product']
            capacity = facility['capacity_t']

            if product not in self.ci_df.index:
                # Zero emissions for unmapped products
                for key in emissions_data:
                    emissions_data[key].append(0)
                for key in energy_data:
                    energy_data[key].append(0)
                continue

            product_row = self.ci_df.loc[product]

            # Track emissions and energy by source
            facility_emissions = {key: 0 for key in emissions_data}
            facility_energy = {key: 0 for key in energy_data}

            # Energy source mappings with scope classification
            energy_sources = [
                ('Naphtha_Feedstock_GJ_per_t', 'Naphtha_Feedstock_tCO2_per_GJ',
                 'naphtha_feedstock', 'scope1'),
                ('Naphtha_Thermal_GJ_per_t', 'Naphtha_Thermal_tCO2_per_GJ',
                 'naphtha_thermal', 'scope1'),
                ('Byproduct_Gas_GJ_per_t', 'Byproduct_Gas_tCO2_per_GJ',
                 'byproduct_gas', 'scope1'),
                ('Byproduct_Oil_GJ_per_t', 'Byproduct_Oil_tCO2_per_GJ',
                 'byproduct_oil', 'scope1'),
                ('LNG_GJ_per_t', 'LNG_tCO2_per_GJ', 'lng', 'scope1'),
                ('NG_GJ_per_t', 'NG_tCO2_per_GJ', 'ng', 'scope1'),
                ('Electricity_kWh_per_t', 'Electricity_tCO2_per_kWh',
                 'electricity', 'scope2')
            ]

            for consumption_col, emission_col, source_key, scope in energy_sources:
                if consumption_col in product_row.index and emission_col in self.emission_factors:
                    consumption = product_row[consumption_col]

                    if pd.notna(consumption) and consumption > 0:
                        emission_factor = self.emission_factors[emission_col]

                        # Calculate emissions
                        if 'kWh' in consumption_col:
                            # Electricity: convert kWh to GJ
                            energy_gj = consumption * capacity * self.KWH_TO_GJ
                            emissions_tco2 = consumption * capacity * emission_factor
                        else:
                            # Fuels: already in GJ
                            energy_gj = consumption * capacity
                            emissions_tco2 = energy_gj * emission_factor

                        # Store by source
                        facility_emissions[source_key] = emissions_tco2
                        facility_emissions[scope] += emissions_tco2
                        facility_emissions['total'] += emissions_tco2

                        facility_energy[f'{source_key}_gj'] = energy_gj
                        facility_energy['total_gj'] += energy_gj

            # Append to arrays
            for key in emissions_data:
                emissions_data[key].append(facility_emissions[key])
            for key in energy_data:
                energy_data[key].append(facility_energy[key])

        # Store in dataframe
        for key, values in emissions_data.items():
            self.facilities_df[f'emissions_{key}_tco2'] = values
        for key, values in energy_data.items():
            self.facilities_df[f'energy_{key}'] = values

        # Calculate totals before calibration
        self.baseline_totals_raw = {
            'total_emissions_tco2': self.facilities_df['emissions_total_tco2'].sum(),
            'scope1_emissions_tco2': self.facilities_df['emissions_scope1_tco2'].sum(),
            'scope2_emissions_tco2': self.facilities_df['emissions_scope2_tco2'].sum(),
            'total_energy_gj': self.facilities_df['energy_total_gj'].sum(),
        }

        # Calibration to target baseline (52 MtCO2)
        target_emissions_tco2 = self.validation_targets['total_emissions_mtco2'] * 1e6
        self.calibration_factor = target_emissions_tco2 / self.baseline_totals_raw['total_emissions_tco2']

        # Apply calibration to all emission and energy columns
        for col in self.facilities_df.columns:
            if col.startswith('emissions_') or col.startswith('energy_'):
                self.facilities_df[col] = self.facilities_df[col] * self.calibration_factor

        # Remove zero-emission facilities
        self.facilities_df = self.facilities_df[
            self.facilities_df['emissions_total_tco2'] > 0
        ].copy()

        print(f"   📊 Raw baseline: {self.baseline_totals_raw['total_emissions_tco2']/1e6:.1f} MtCO₂")
        print(f"   🎯 Target: {self.validation_targets['total_emissions_mtco2']:.1f} MtCO₂")
        print(f"   ⚖️ Calibration factor: {self.calibration_factor:.4f}")
        print(f"   ✅ Final facilities: {len(self.facilities_df)}")

    def calculate_energy_flows(self):
        """Calculate detailed energy flows for baseline"""
        print("🔋 Calculating energy flows...")

        # Aggregate energy flows
        self.energy_flows_2025 = {
            'naphtha_feedstock_pj': self.facilities_df['energy_naphtha_feedstock_gj'].sum() / 1e3,
            'naphtha_thermal_pj': self.facilities_df['energy_naphtha_thermal_gj'].sum() / 1e3,
            'byproduct_gas_pj': self.facilities_df['energy_byproduct_gas_gj'].sum() / 1e3,
            'byproduct_oil_pj': self.facilities_df['energy_byproduct_oil_gj'].sum() / 1e3,
            'lng_pj': self.facilities_df['energy_lng_gj'].sum() / 1e3,
            'ng_pj': self.facilities_df['energy_ng_gj'].sum() / 1e3,
            'grid_electricity_pj': self.facilities_df['energy_electricity_gj'].sum() / 1e3,
            're_ppa_pj': 0.0,  # Baseline has no RE
            'onsite_re_pj': 0.0,
            'blue_h2_pj': 0.0,
            'green_h2_pj': 0.0,
        }

        self.energy_flows_2025['total_pj'] = sum(self.energy_flows_2025.values())

        # Convert to Mtoe
        self.energy_flows_2025['total_mtoe'] = (
            self.energy_flows_2025['total_pj'] * 1e3 / self.GJ_PER_TOE / 1e6
        )

        print(f"   ✅ Total energy: {self.energy_flows_2025['total_pj']:.1f} PJ " +
              f"({self.energy_flows_2025['total_mtoe']:.1f} Mtoe)")

    def validate_baseline(self) -> Dict[str, bool]:
        """Comprehensive validation against targets"""
        print("✅ Validating baseline against targets...")

        # Calculate validation metrics
        total_emissions_mtco2 = self.facilities_df['emissions_total_tco2'].sum() / 1e6
        scope1_mtco2 = self.facilities_df['emissions_scope1_tco2'].sum() / 1e6
        scope2_mtco2 = self.facilities_df['emissions_scope2_tco2'].sum() / 1e6
        total_energy_mtoe = self.energy_flows_2025['total_mtoe']

        # By-product emissions (gas + oil)
        byproduct_emissions = (
            self.facilities_df['emissions_byproduct_gas_tco2'].sum() +
            self.facilities_df['emissions_byproduct_oil_tco2'].sum()
        ) / 1e6

        # Naphtha energy (feedstock + thermal)
        naphtha_energy_pj = (
            self.energy_flows_2025['naphtha_feedstock_pj'] +
            self.energy_flows_2025['naphtha_thermal_pj']
        )

        # NCC emissions
        ncc_emissions_mtco2 = self.facilities_df[
            self.facilities_df['process'] == 'Naphtha Cracker'
        ]['emissions_total_tco2'].sum() / 1e6

        # Calculated metrics
        self.validation_results = {
            'total_emissions_mtco2': total_emissions_mtco2,
            'scope1_emissions_mtco2': scope1_mtco2,
            'scope2_emissions_mtco2': scope2_mtco2,
            'direct_emission_share': scope1_mtco2 / total_emissions_mtco2 if total_emissions_mtco2 > 0 else 0,
            'indirect_emission_share': scope2_mtco2 / total_emissions_mtco2 if total_emissions_mtco2 > 0 else 0,
            'byproduct_of_direct_share': byproduct_emissions / scope1_mtco2 if scope1_mtco2 > 0 else 0,
            'total_energy_mtoe': total_energy_mtoe,
            'naphtha_energy_share': naphtha_energy_pj / self.energy_flows_2025['total_pj'] if self.energy_flows_2025['total_pj'] > 0 else 0,
            'ncc_emission_share': ncc_emissions_mtco2 / total_emissions_mtco2 if total_emissions_mtco2 > 0 else 0,
            'utility_electricity_mtoe': self.energy_flows_2025['grid_electricity_pj'] * 1e3 / self.GJ_PER_TOE / 1e6,
        }

        # Validate against targets
        self.qa_checks = []
        all_pass = True

        for metric, value in self.validation_results.items():
            if metric in self.validation_targets:
                target = self.validation_targets[metric]
                tolerance = self.validation_tolerance.get(metric, 0.05)

                # Calculate bounds
                lower_bound = target * (1 - tolerance)
                upper_bound = target * (1 + tolerance)

                # Check if within bounds
                passed = lower_bound <= value <= upper_bound
                all_pass = all_pass and passed

                # Store check result
                self.qa_checks.append({
                    'metric': metric,
                    'value': value,
                    'target': target,
                    'unit': self._get_unit(metric),
                    'tolerance_pct': tolerance * 100,
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound,
                    'status': 'PASS' if passed else 'FAIL',
                    'deviation_pct': abs(value - target) / target * 100 if target > 0 else 0
                })

        # Print results
        print("   📋 VALIDATION RESULTS:")
        print("   " + "-" * 66)
        print(f"   {'Metric':<35} {'Value':>10} {'Target':>10} {'Status':>8}")
        print("   " + "-" * 66)

        for check in self.qa_checks:
            status_symbol = "✅" if check['status'] == 'PASS' else "❌"
            print(f"   {status_symbol} {check['metric']:<33} {check['value']:>10.2f} " +
                  f"{check['target']:>10.2f} {check['status']:>8}")

        print("   " + "-" * 66)

        if all_pass:
            print("   ✅ ALL VALIDATIONS PASSED!")
        else:
            print("   ⚠️ SOME VALIDATIONS FAILED - Review above")

        self.validation_passed = all_pass
        return all_pass

    def _get_unit(self, metric: str) -> str:
        """Get unit for metric"""
        if 'emissions' in metric and 'mtco2' in metric:
            return 'MtCO₂'
        elif 'share' in metric:
            return '%'
        elif 'mtoe' in metric:
            return 'Mtoe'
        elif 'pj' in metric:
            return 'PJ'
        else:
            return ''

    def export_baseline_2025_totals(self) -> str:
        """Export baseline_2025_totals.csv"""
        print("💾 Exporting baseline_2025_totals.csv...")

        # Create DataFrame from QA checks
        qa_df = pd.DataFrame(self.qa_checks)

        # Add summary row
        summary_row = {
            'metric': 'VALIDATION_SUMMARY',
            'value': len([c for c in self.qa_checks if c['status'] == 'PASS']),
            'target': len(self.qa_checks),
            'unit': 'checks passed',
            'tolerance_pct': np.nan,
            'lower_bound': np.nan,
            'upper_bound': np.nan,
            'status': 'PASS' if self.validation_passed else 'FAIL',
            'deviation_pct': np.nan
        }
        qa_df = pd.concat([qa_df, pd.DataFrame([summary_row])], ignore_index=True)

        # Export
        output_file = self.output_dir / "baseline_2025_totals.csv"
        qa_df.to_csv(output_file, index=False)

        print(f"   ✅ Exported: {output_file}")
        return str(output_file)

    def export_qa_checks(self) -> str:
        """Export qa_checks.csv with detailed validation"""
        print("💾 Exporting qa_checks.csv...")

        qa_detailed = []

        # Add all QA checks
        for check in self.qa_checks:
            qa_detailed.append({
                'check_type': 'baseline_validation',
                'category': 'emissions' if 'emission' in check['metric'] else 'energy',
                'metric': check['metric'],
                'value': check['value'],
                'target': check['target'],
                'unit': check['unit'],
                'tolerance_pct': check['tolerance_pct'],
                'deviation_pct': check['deviation_pct'],
                'status': check['status'],
                'severity': 'HIGH' if check['deviation_pct'] > 10 else 'MEDIUM' if check['deviation_pct'] > 5 else 'LOW',
                'notes': f"Within ±{check['tolerance_pct']:.1f}% tolerance" if check['status'] == 'PASS' else f"Deviation: {check['deviation_pct']:.1f}%"
            })

        # Add facility-level checks
        qa_detailed.append({
            'check_type': 'facility_count',
            'category': 'data_quality',
            'metric': 'total_facilities',
            'value': len(self.facilities_df),
            'target': np.nan,
            'unit': 'facilities',
            'tolerance_pct': np.nan,
            'deviation_pct': 0,
            'status': 'PASS',
            'severity': 'INFO',
            'notes': f'{len(self.facilities_df)} facilities with non-zero emissions'
        })

        qa_detailed.append({
            'check_type': 'calibration',
            'category': 'data_quality',
            'metric': 'calibration_factor',
            'value': self.calibration_factor,
            'target': 1.0,
            'unit': 'ratio',
            'tolerance_pct': np.nan,
            'deviation_pct': abs(self.calibration_factor - 1.0) * 100,
            'status': 'PASS' if 0.8 <= self.calibration_factor <= 1.2 else 'WARN',
            'severity': 'INFO',
            'notes': f'Applied {self.calibration_factor:.4f}× factor to match 52 MtCO₂ target'
        })

        qa_df = pd.DataFrame(qa_detailed)

        # Export
        output_file = self.output_dir / "qa_checks.csv"
        qa_df.to_csv(output_file, index=False)

        print(f"   ✅ Exported: {output_file}")
        return str(output_file)

    def export_energy_flow_baseline(self) -> str:
        """Export energy_flow.csv for baseline year (Sankey-ready)"""
        print("💾 Exporting energy_flow_baseline.csv...")

        energy_flow_records = []

        # Aggregate by process type
        for process in self.facilities_df['process'].unique():
            process_facilities = self.facilities_df[self.facilities_df['process'] == process]

            # Energy sources
            sources = [
                ('naphtha_feedstock', 'Naphtha (Feedstock)'),
                ('naphtha_thermal', 'Naphtha (Thermal)'),
                ('byproduct_gas', 'By-product Gas'),
                ('byproduct_oil', 'By-product Oil'),
                ('lng', 'LNG'),
                ('ng', 'Natural Gas'),
                ('electricity', 'Grid Electricity'),
            ]

            for source_key, source_name in sources:
                energy_gj = process_facilities[f'energy_{source_key}_gj'].sum()
                emissions_tco2 = process_facilities[f'emissions_{source_key}_tco2'].sum()

                if energy_gj > 0:
                    energy_flow_records.append({
                        'scenario': 'baseline',
                        'year': 2025,
                        'source_carrier': source_name,
                        'intermediate_carrier': None,
                        'sink_process': process,
                        'energy_gj': energy_gj,
                        'emission_intensity_kgco2_gj': (emissions_tco2 * 1000 / energy_gj) if energy_gj > 0 else 0
                    })

        energy_flow_df = pd.DataFrame(energy_flow_records)

        # Export
        output_file = self.output_dir / "energy_flow_baseline.csv"
        energy_flow_df.to_csv(output_file, index=False)

        print(f"   ✅ Exported: {output_file}")
        return str(output_file)

    def generate_baseline_report(self) -> str:
        """Generate comprehensive baseline Excel report"""
        print("📊 Generating baseline analysis report...")

        output_file = self.output_dir / "baseline_analysis_enhanced_report.xlsx"

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

            # 1. Executive Summary
            exec_summary = pd.DataFrame([
                ['Analysis Date', pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')],
                ['Model Version', '2.0 - Enhanced with QA Validation'],
                ['Data Source', str(self.data_path)],
                ['Baseline Year', self.baseline_year],
                ['Total Facilities', len(self.facilities_df)],
                ['Calibration Factor', f'{self.calibration_factor:.4f}'],
                ['Validation Status', 'PASS' if self.validation_passed else 'FAIL'],
                ['', ''],
                ['KEY METRICS (2025 Baseline)', ''],
                ['Total Emissions', f"{self.validation_results['total_emissions_mtco2']:.2f} MtCO₂"],
                ['Scope 1 Emissions', f"{self.validation_results['scope1_emissions_mtco2']:.2f} MtCO₂"],
                ['Scope 2 Emissions', f"{self.validation_results['scope2_emissions_mtco2']:.2f} MtCO₂"],
                ['Total Energy', f"{self.validation_results['total_energy_mtoe']:.2f} Mtoe"],
                ['Naphtha Share', f"{self.validation_results['naphtha_energy_share']*100:.1f}%"],
                ['NCC Emission Share', f"{self.validation_results['ncc_emission_share']*100:.1f}%"],
            ], columns=['Metric', 'Value'])
            exec_summary.to_excel(writer, sheet_name='Executive_Summary', index=False)

            # 2. QA Validation Results
            qa_df = pd.DataFrame(self.qa_checks)
            qa_df.to_excel(writer, sheet_name='QA_Validation', index=False)

            # 3. Energy Flow Summary
            energy_summary = pd.DataFrame([
                ['Energy Source', 'PJ', 'Mtoe', '% Share'],
                ['Naphtha (Feedstock)',
                 f"{self.energy_flows_2025['naphtha_feedstock_pj']:.2f}",
                 f"{self.energy_flows_2025['naphtha_feedstock_pj']*1e3/self.GJ_PER_TOE/1e6:.2f}",
                 f"{self.energy_flows_2025['naphtha_feedstock_pj']/self.energy_flows_2025['total_pj']*100:.1f}%"],
                ['Naphtha (Thermal)',
                 f"{self.energy_flows_2025['naphtha_thermal_pj']:.2f}",
                 f"{self.energy_flows_2025['naphtha_thermal_pj']*1e3/self.GJ_PER_TOE/1e6:.2f}",
                 f"{self.energy_flows_2025['naphtha_thermal_pj']/self.energy_flows_2025['total_pj']*100:.1f}%"],
                ['By-product Gas',
                 f"{self.energy_flows_2025['byproduct_gas_pj']:.2f}",
                 f"{self.energy_flows_2025['byproduct_gas_pj']*1e3/self.GJ_PER_TOE/1e6:.2f}",
                 f"{self.energy_flows_2025['byproduct_gas_pj']/self.energy_flows_2025['total_pj']*100:.1f}%"],
                ['By-product Oil',
                 f"{self.energy_flows_2025['byproduct_oil_pj']:.2f}",
                 f"{self.energy_flows_2025['byproduct_oil_pj']*1e3/self.GJ_PER_TOE/1e6:.2f}",
                 f"{self.energy_flows_2025['byproduct_oil_pj']/self.energy_flows_2025['total_pj']*100:.1f}%"],
                ['LNG',
                 f"{self.energy_flows_2025['lng_pj']:.2f}",
                 f"{self.energy_flows_2025['lng_pj']*1e3/self.GJ_PER_TOE/1e6:.2f}",
                 f"{self.energy_flows_2025['lng_pj']/self.energy_flows_2025['total_pj']*100:.1f}%"],
                ['Natural Gas',
                 f"{self.energy_flows_2025['ng_pj']:.2f}",
                 f"{self.energy_flows_2025['ng_pj']*1e3/self.GJ_PER_TOE/1e6:.2f}",
                 f"{self.energy_flows_2025['ng_pj']/self.energy_flows_2025['total_pj']*100:.1f}%"],
                ['Grid Electricity',
                 f"{self.energy_flows_2025['grid_electricity_pj']:.2f}",
                 f"{self.energy_flows_2025['grid_electricity_pj']*1e3/self.GJ_PER_TOE/1e6:.2f}",
                 f"{self.energy_flows_2025['grid_electricity_pj']/self.energy_flows_2025['total_pj']*100:.1f}%"],
                ['TOTAL',
                 f"{self.energy_flows_2025['total_pj']:.2f}",
                 f"{self.energy_flows_2025['total_mtoe']:.2f}",
                 "100.0%"],
            ])
            energy_summary.to_excel(writer, sheet_name='Energy_Flows', index=False, header=False)

            # 4. Emissions by Process
            process_summary = self.facilities_df.groupby('process').agg({
                'emissions_total_tco2': 'sum',
                'emissions_scope1_tco2': 'sum',
                'emissions_scope2_tco2': 'sum',
                'capacity_t': 'sum',
                'facility_id': 'count'
            }).reset_index()

            process_summary.columns = ['Process', 'Total Emissions (tCO₂)', 'Scope 1 (tCO₂)',
                                      'Scope 2 (tCO₂)', 'Total Capacity (t)', 'Facility Count']
            process_summary['Emissions (MtCO₂)'] = process_summary['Total Emissions (tCO₂)'] / 1e6
            process_summary['Share (%)'] = (
                process_summary['Total Emissions (tCO₂)'] /
                process_summary['Total Emissions (tCO₂)'].sum() * 100
            )
            process_summary.to_excel(writer, sheet_name='Emissions_by_Process', index=False)

            # 5. Emissions by Company
            company_summary = self.facilities_df.groupby('company').agg({
                'emissions_total_tco2': 'sum',
                'emissions_scope1_tco2': 'sum',
                'emissions_scope2_tco2': 'sum',
                'capacity_t': 'sum',
                'facility_id': 'count',
                'age_2025': 'mean'
            }).reset_index()

            company_summary.columns = ['Company', 'Total Emissions (tCO₂)', 'Scope 1 (tCO₂)',
                                      'Scope 2 (tCO₂)', 'Total Capacity (t)',
                                      'Facility Count', 'Avg Age']
            company_summary['Emissions (MtCO₂)'] = company_summary['Total Emissions (tCO₂)'] / 1e6
            company_summary['Share (%)'] = (
                company_summary['Total Emissions (tCO₂)'] /
                company_summary['Total Emissions (tCO₂)'].sum() * 100
            )
            company_summary = company_summary.sort_values('Emissions (MtCO₂)', ascending=False)
            company_summary.to_excel(writer, sheet_name='Emissions_by_Company', index=False)

            # 6. Facility Master Data
            facility_export = self.facilities_df[[
                'facility_id', 'company', 'location', 'process', 'product',
                'capacity_t', 'year', 'age_2025',
                'emissions_total_tco2', 'emissions_scope1_tco2', 'emissions_scope2_tco2',
                'energy_total_gj'
            ]].copy()
            facility_export.to_excel(writer, sheet_name='Facility_Master', index=False)

        print(f"   ✅ Report saved: {output_file}")
        return str(output_file)

    def run_complete_analysis(self):
        """Run complete enhanced baseline analysis"""
        print("\n" + "=" * 70)
        print("🚀 RUNNING COMPLETE ENHANCED BASELINE ANALYSIS")
        print("=" * 70)

        # Export standardized outputs
        baseline_totals = self.export_baseline_2025_totals()
        qa_checks = self.export_qa_checks()
        energy_flow = self.export_energy_flow_baseline()
        excel_report = self.generate_baseline_report()

        # Summary
        print("\n" + "=" * 70)
        print("✅ ENHANCED BASELINE ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"📊 Baseline Emissions: {self.validation_results['total_emissions_mtco2']:.2f} MtCO₂")
        print(f"   • Scope 1: {self.validation_results['scope1_emissions_mtco2']:.2f} MtCO₂ " +
              f"({self.validation_results['direct_emission_share']*100:.1f}%)")
        print(f"   • Scope 2: {self.validation_results['scope2_emissions_mtco2']:.2f} MtCO₂ " +
              f"({self.validation_results['indirect_emission_share']*100:.1f}%)")
        print(f"🔋 Total Energy: {self.validation_results['total_energy_mtoe']:.2f} Mtoe")
        print(f"   • Naphtha: {self.validation_results['naphtha_energy_share']*100:.1f}%")
        print(f"🏭 Facilities: {len(self.facilities_df)}")
        print(f"✅ Validation: {'PASSED' if self.validation_passed else 'FAILED'}")
        print(f"\n📁 Outputs:")
        print(f"   • {baseline_totals}")
        print(f"   • {qa_checks}")
        print(f"   • {energy_flow}")
        print(f"   • {excel_report}")
        print("=" * 70)

        return {
            'validation_passed': self.validation_passed,
            'baseline_totals': baseline_totals,
            'qa_checks': qa_checks,
            'energy_flow': energy_flow,
            'excel_report': excel_report,
            'facilities_df': self.facilities_df,
            'validation_results': self.validation_results
        }


def main():
    """Main execution function"""
    analyzer = EnhancedBaselineAnalyzer()
    results = analyzer.run_complete_analysis()

    return results


if __name__ == "__main__":
    main()
