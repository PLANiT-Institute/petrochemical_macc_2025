#!/usr/bin/env python3
"""
Run single BAU to Net-Zero optimization for testing
"""

from macc_optimization_model_bau_netzero import MACCOptimizationBAUNetZero

if __name__ == "__main__":
    print("🚀 Testing BAU to Net-Zero optimization with 30yr facility lifetime")
    
    # Create optimization model for 30yr lifetime
    optimizer = MACCOptimizationBAUNetZero(facility_lifetime='30yr')
    
    # Run optimization
    results = optimizer.run_optimization_analysis()
    
    if results:
        print("✅ Optimization completed successfully")
    else:
        print("❌ Optimization failed")