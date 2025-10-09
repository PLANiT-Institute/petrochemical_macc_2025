#!/usr/bin/env python3
from modules.optimization import CostOptimizer

if __name__ == '__main__':
    optimizer = CostOptimizer()
    results = optimizer.run_complete_analysis()
    print("\n🎉 Optimization complete!")
