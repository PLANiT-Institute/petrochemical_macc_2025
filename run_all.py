#!/usr/bin/env python3
"""
Run complete analysis - all 4 modules
"""

from modules.baseline import BaselineAnalyzer
from modules.macc import MACCAnalyzer
from modules.optimization import CostOptimizer
from modules.financial import FinancialAnalyzer

if __name__ == '__main__':
    print("\n" + "="*80)
    print("KOREAN PETROCHEMICAL MACC MODEL - COMPLETE ANALYSIS")
    print("="*80)

    # Module 1: Baseline
    print("\n[1/4] Running Baseline Analysis...")
    baseline = BaselineAnalyzer()
    baseline.run_complete_analysis()

    # Module 2: MACC
    print("\n[2/4] Running MACC Analysis...")
    macc = MACCAnalyzer()
    macc.run_complete_analysis()

    # Module 3: Optimization
    print("\n[3/4] Running Cost Optimization...")
    optimizer = CostOptimizer()
    optimizer.run_complete_analysis()

    # Module 4: Financial
    print("\n[4/4] Running Financial Analysis...")
    financial = FinancialAnalyzer()
    financial.run_complete_analysis()

    print("\n" + "="*80)
    print("✓ COMPLETE ANALYSIS FINISHED")
    print("="*80)
    print("\nAll outputs saved to: outputs/")
    print("  - outputs/module_01/ (Baseline)")
    print("  - outputs/module_02/ (MACC)")
    print("  - outputs/module_03/ (Optimization)")
    print("  - outputs/module_04/ (Financial)")
