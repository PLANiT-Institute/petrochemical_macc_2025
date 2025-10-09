#!/usr/bin/env python3
"""
Run Module 1: Baseline Analysis
Simple runner - all logic is in modules/baseline.py
"""

from modules.baseline import BaselineAnalyzer

if __name__ == '__main__':
    # Create analyzer
    analyzer = BaselineAnalyzer(data_dir='data', output_dir='outputs/module_01')

    # Run complete analysis
    results = analyzer.run_complete_analysis()

    print("\n🎉 Baseline analysis complete!")
