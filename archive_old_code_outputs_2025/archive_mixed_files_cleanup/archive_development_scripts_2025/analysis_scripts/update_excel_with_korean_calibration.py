#!/usr/bin/env python3
"""
Update Excel file with Korean industry calibrated baseline data
Matches the Korean industry statistics provided by user:
- Total energy: 67.7 million toe
- Naphtha share: 82.9%
- NCC process: 46% of GHG
- Direct/indirect emissions: 64%/34%
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from openpyxl import load_workbook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelKoreanCalibrationUpdater:
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "data"
        self.excel_file = self.data_path / "Korean_Petrochemical_MACC_Model_English.xlsx"
        self.output_path = Path(__file__).parent.parent / "outputs" / "korean_calibrated_baseline"

        # Korean industry benchmarks
        self.korean_benchmarks = {
            'total_energy_toe': 67_700_000,  # 67.7 million toe
            'total_energy_gj': 67_700_000 * 41.868,  # Convert to GJ
            'naphtha_share': 0.829,  # 82.9% naphtha share
            'fuel_gas_share': 0.111,  # ~11.1% fuel gas
            'electricity_share': 0.059,  # ~5.9% electricity (4M toe / 67.7M toe)
            'ncc_ghg_share': 0.46,   # 46% of GHG from NCC
            'btx_ghg_share': 0.32,   # ~32% from BTX (estimated)
            'utility_ghg_share': 0.18,  # ~18% from utilities (estimated)
            'direct_emission_share': 0.64,   # 64% direct emissions
            'indirect_emission_share': 0.34, # 34% indirect emissions
            'total_ghg_target': 261.5,  # Target total emissions MtCO2e
        }

        # Load calibrated values from our analysis
        self.load_calibrated_data()

    def load_calibrated_data(self):
        """Load the calibrated data from our Korean analysis output"""
        try:
            # Load energy consumption data
            energy_file = self.output_path / "korean_calibrated_energy_consumption.csv"
            if energy_file.exists():
                self.energy_data = pd.read_csv(energy_file)
                logger.info(f"Loaded energy calibration data: {len(self.energy_data)} rows")

            # Load process analysis data
            process_file = self.output_path / "korean_calibrated_process_analysis.csv"
            if process_file.exists():
                self.process_data = pd.read_csv(process_file)
                logger.info(f"Loaded process calibration data: {len(self.process_data)} rows")

        except Exception as e:
            logger.warning(f"Could not load calibrated data: {e}. Will calculate from benchmarks.")
            self.calculate_calibrated_values()

    def calculate_calibrated_values(self):
        """Calculate calibrated values based on Korean benchmarks"""
        # Energy consumption breakdown
        total_gj = self.korean_benchmarks['total_energy_gj']

        self.energy_calibration = {
            'Naphtha': {
                'gj': total_gj * self.korean_benchmarks['naphtha_share'],
                'toe': self.korean_benchmarks['total_energy_toe'] * self.korean_benchmarks['naphtha_share']
            },
            'Fuel_Gas': {
                'gj': total_gj * self.korean_benchmarks['fuel_gas_share'],
                'toe': self.korean_benchmarks['total_energy_toe'] * self.korean_benchmarks['fuel_gas_share']
            },
            'Electricity': {
                'gj': total_gj * self.korean_benchmarks['electricity_share'],
                'toe': self.korean_benchmarks['total_energy_toe'] * self.korean_benchmarks['electricity_share']
            }
        }

        # Process emissions breakdown
        total_ghg = self.korean_benchmarks['total_ghg_target']

        self.process_calibration = {
            'Naphtha Cracker': {
                'emissions_mt': total_ghg * self.korean_benchmarks['ncc_ghg_share'],
                'share': self.korean_benchmarks['ncc_ghg_share']
            },
            'BTX Plant': {
                'emissions_mt': total_ghg * self.korean_benchmarks['btx_ghg_share'],
                'share': self.korean_benchmarks['btx_ghg_share']
            },
            'Utility': {
                'emissions_mt': total_ghg * self.korean_benchmarks['utility_ghg_share'],
                'share': self.korean_benchmarks['utility_ghg_share']
            }
        }

    def update_excel_file(self):
        """Update the Excel file with Korean calibrated data"""
        logger.info(f"Updating Excel file: {self.excel_file}")

        try:
            # Read all sheets
            excel_data = pd.read_excel(self.excel_file, sheet_name=None)
            sheet_names = list(excel_data.keys())
            logger.info(f"Found sheets: {sheet_names}")

            # Update relevant sheets
            updated_sheets = {}

            for sheet_name, df in excel_data.items():
                logger.info(f"Processing sheet: {sheet_name}")
                updated_df = self.calibrate_sheet_data(df, sheet_name)
                updated_sheets[sheet_name] = updated_df

            # Write updated Excel file
            output_file = self.data_path / "Korean_Petrochemical_MACC_Model_English_Calibrated.xlsx"
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                for sheet_name, df in updated_sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            logger.info(f"Updated Excel file saved: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error updating Excel file: {e}")
            raise

    def calibrate_sheet_data(self, df, sheet_name):
        """Calibrate data in a specific sheet based on Korean benchmarks"""
        df_copy = df.copy()

        try:
            # Check for energy consumption columns
            energy_columns = [col for col in df.columns if any(term in col.lower()
                            for term in ['energy', 'consumption', 'naphtha', 'fuel', 'electricity'])]

            if energy_columns:
                logger.info(f"Found energy columns in {sheet_name}: {energy_columns}")
                df_copy = self.update_energy_consumption(df_copy, energy_columns)

            # Check for emission columns
            emission_columns = [col for col in df.columns if any(term in col.lower()
                              for term in ['emission', 'co2', 'ghg'])]

            if emission_columns:
                logger.info(f"Found emission columns in {sheet_name}: {emission_columns}")
                df_copy = self.update_emissions(df_copy, emission_columns)

            # Check for process-specific data
            if 'process' in df.columns or any('process' in str(col).lower() for col in df.columns):
                logger.info(f"Found process data in {sheet_name}")
                df_copy = self.update_process_data(df_copy)

        except Exception as e:
            logger.warning(f"Error calibrating sheet {sheet_name}: {e}")
            return df_copy

        return df_copy

    def update_energy_consumption(self, df, energy_columns):
        """Update energy consumption values based on Korean calibration"""
        if not hasattr(self, 'energy_calibration'):
            self.calculate_calibrated_values()

        for idx, row in df.iterrows():
            # Look for naphtha consumption
            for col in energy_columns:
                if 'naphtha' in col.lower():
                    # Scale existing values to match Korean benchmark
                    if pd.notna(row[col]) and row[col] > 0:
                        scaling_factor = (self.energy_calibration['Naphtha']['gj'] /
                                        df[col].sum() if df[col].sum() > 0 else 1)
                        df.loc[idx, col] = row[col] * scaling_factor

                elif 'fuel' in col.lower() or 'gas' in col.lower():
                    # Scale fuel gas consumption
                    if pd.notna(row[col]) and row[col] > 0:
                        scaling_factor = (self.energy_calibration['Fuel_Gas']['gj'] /
                                        df[col].sum() if df[col].sum() > 0 else 1)
                        df.loc[idx, col] = row[col] * scaling_factor

                elif 'electricity' in col.lower() or 'electric' in col.lower():
                    # Scale electricity consumption
                    if pd.notna(row[col]) and row[col] > 0:
                        scaling_factor = (self.energy_calibration['Electricity']['gj'] /
                                        df[col].sum() if df[col].sum() > 0 else 1)
                        df.loc[idx, col] = row[col] * scaling_factor

        return df

    def update_emissions(self, df, emission_columns):
        """Update emission values based on Korean calibration"""
        if not hasattr(self, 'process_calibration'):
            self.calculate_calibrated_values()

        # Scale total emissions to match Korean benchmark
        total_target = self.korean_benchmarks['total_ghg_target'] * 1_000_000  # Convert to tCO2

        for col in emission_columns:
            if df[col].sum() > 0:
                scaling_factor = total_target / df[col].sum()
                df[col] = df[col] * scaling_factor

        return df

    def update_process_data(self, df):
        """Update process-specific data based on Korean benchmarks"""
        if not hasattr(self, 'process_calibration'):
            self.calculate_calibrated_values()

        # Look for process column
        process_col = None
        for col in df.columns:
            if 'process' in str(col).lower() or any(proc in str(col).lower()
                                                   for proc in ['naphtha', 'btx', 'utility']):
                process_col = col
                break

        if process_col:
            for idx, row in df.iterrows():
                process_name = str(row[process_col]).lower()

                # Match to our calibrated processes
                if 'naphtha' in process_name or 'ncc' in process_name:
                    # Apply NCC calibration
                    self.apply_process_scaling(df, idx, 'Naphtha Cracker')
                elif 'btx' in process_name:
                    # Apply BTX calibration
                    self.apply_process_scaling(df, idx, 'BTX Plant')
                elif 'utility' in process_name:
                    # Apply Utility calibration
                    self.apply_process_scaling(df, idx, 'Utility')

        return df

    def apply_process_scaling(self, df, row_idx, process_type):
        """Apply scaling factors for specific process types"""
        if process_type not in self.process_calibration:
            return

        target_share = self.process_calibration[process_type]['share']

        # Scale emission-related columns
        emission_cols = [col for col in df.columns if any(term in str(col).lower()
                        for term in ['emission', 'co2', 'ghg'])]

        for col in emission_cols:
            if pd.notna(df.loc[row_idx, col]) and df.loc[row_idx, col] > 0:
                # Scale to match target share
                total_emissions = df[col].sum()
                if total_emissions > 0:
                    target_value = total_emissions * target_share
                    current_share = df.loc[row_idx, col] / total_emissions
                    if current_share > 0:
                        scaling_factor = target_share / current_share
                        df.loc[row_idx, col] = df.loc[row_idx, col] * scaling_factor

    def create_calibration_summary(self, updated_file):
        """Create a summary of the calibration changes"""
        summary = {
            'Korean Industry Benchmarks Applied': self.korean_benchmarks,
            'Energy Calibration': getattr(self, 'energy_calibration', {}),
            'Process Calibration': getattr(self, 'process_calibration', {}),
            'Updated File': str(updated_file),
            'Calibration Status': 'Success'
        }

        # Save summary
        summary_file = self.output_path / "excel_calibration_summary.json"
        summary_file.parent.mkdir(parents=True, exist_ok=True)

        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info(f"Calibration summary saved: {summary_file}")
        return summary

def main():
    """Main execution function"""
    logger.info("Starting Excel Korean calibration update...")

    try:
        updater = ExcelKoreanCalibrationUpdater()
        updated_file = updater.update_excel_file()
        summary = updater.create_calibration_summary(updated_file)

        print("✅ Excel file updated with Korean industry calibrated data!")
        print(f"📁 Updated file: {updated_file}")
        print("\n📊 Korean Industry Benchmarks Applied:")
        for key, value in updater.korean_benchmarks.items():
            print(f"   {key}: {value}")

        return updated_file, summary

    except Exception as e:
        logger.error(f"Failed to update Excel file: {e}")
        raise

if __name__ == "__main__":
    main()