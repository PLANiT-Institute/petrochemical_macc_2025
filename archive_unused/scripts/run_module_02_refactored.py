"""
MODULE 2: MACC Analysis (Refactored - Data-Driven)
All assumptions loaded from data files - NO HARDCODED VALUES
"""

from modules.data_manager import DataManager
from modules import macc
import sys

if __name__ == '__main__':
    print("\n" + "="*80)
    print("MODULE 2: ENERGY-BASED MACC ANALYSIS (DATA-DRIVEN VERSION)")
    print("="*80)

    # Load all data
    dm = DataManager('data')

    # Run MACC analysis
    analyzer = macc.MACCAnalyzer(
        baseline_output='outputs/module_01',
        data_dir='data',
        output_dir='outputs/module_02_refactored'
    )

    # Calculate MACC
    results = analyzer.run_complete_analysis()

    print("\n" + "="*80)
    print("MODULE 2 COMPLETE (DATA-DRIVEN)")
    print("="*80)
    print(f"\nOutputs saved to: outputs/module_02_refactored")
    print("\n🎉 MACC analysis complete!")
