#!/usr/bin/env python3
from modules.financial import FinancialAnalyzer

if __name__ == '__main__':
    analyzer = FinancialAnalyzer()
    results = analyzer.run_complete_analysis()
    print("\n🎉 Financial analysis complete!")
