#!/usr/bin/env python3
"""
Run Module 2: Dynamic MACC Analysis
Simple runner - all logic is in modules/macc.py
"""

from modules.macc import MACCAnalyzer

if __name__ == '__main__':
    # Create analyzer
    analyzer = MACCAnalyzer(
        baseline_output='outputs/module_01',
        data_dir='data',
        output_dir='outputs/module_02'
    )

    # Run complete analysis
    results = analyzer.run_complete_analysis()

    print("\n🎉 MACC analysis complete!")
