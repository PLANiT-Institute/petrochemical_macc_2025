#!/usr/bin/env python3
"""
Test the optimization model with the new Korean petrochemical MACC database
"""

import sys
import os
sys.path.append('archive/legacy_model')

from data_io import read_excel, baseline_total_mt, targets_map, build_timeseries, parse_links
from model_pyomo import build_model, solve_model

def test_macc_optimization():
    """Test MACC optimization with Korean petrochemical data"""
    
    print("=== Testing Korean Petrochemical MACC Optimization ===")
    
    # Load optimization-ready data
    excel_file = "data/korean_petrochemical_macc_optimization.xlsx"
    sheets = read_excel(excel_file)
    
    print(f"Loaded sheets: {list(sheets.keys())}")
    
    # Get baseline emissions
    baseline_mt = baseline_total_mt(sheets)
    print(f"Baseline emissions: {baseline_mt:.1f} Mt CO₂")
    
    # Get emission targets
    years_all, tmap = targets_map(sheets, None)
    print(f"Target years: {years_all}")
    print(f"Targets: {tmap}")
    
    # Build technology timeseries
    tech_ids, params = build_timeseries(sheets, years_all[:3], ramp_default=0.05)  # Test with first 3 years
    print(f"Technologies: {len(tech_ids)}")
    print(f"Sample technologies: {tech_ids[:5]}")
    
    # Parse technology links
    groups, depends = parse_links(sheets)
    print(f"Mutual exclusivity groups: {len(groups)}")
    print(f"Coupling dependencies: {len(depends)}")
    
    # Build optimization model
    print("\nBuilding optimization model...")
    years_test = years_all[:3]  # Test with 2025-2027
    m = build_model(years_test, baseline_mt, tmap, tech_ids, params, groups, depends,
                    allow_slack=True, slack_penalty=1e12, discount_rate=0.07)
    
    # Print model summary
    print(f"Model variables: {len(m.build)} build, {len(m.share)} share, {len(m.abate)} abate")
    print(f"Model constraints: Stock, Start, Ramp, Cap, Abat, Target + {len(m.Groups)} groups + {len(m.Couplings)} couplings")
    
    # Solve model
    print("\nSolving optimization model...")
    try:
        solver_used, results = solve_model(m, solver="auto")
        print(f"Solver: {solver_used}")
        print(f"Status: {results.solver.termination_condition}")
        
        # Extract key results
        print("\n=== OPTIMIZATION RESULTS ===")
        for year in years_test:
            total_abatement = sum(m.abate[i,year].value or 0 for i in tech_ids) / 1e6  # Mt CO2
            required_abatement = m.req[year].value / 1e6  # Mt CO2
            shortfall = m.shortfall[year].value / 1e6 if hasattr(m, 'shortfall') else 0  # Mt CO2
            
            print(f"Year {year}:")
            print(f"  Required abatement: {required_abatement:.1f} Mt CO₂")
            print(f"  Achieved abatement: {total_abatement:.1f} Mt CO₂")
            print(f"  Shortfall: {shortfall:.1f} Mt CO₂")
            
            # Top deployed technologies
            deployments = [(i, m.share[i,year].value or 0) for i in tech_ids]
            deployments.sort(key=lambda x: x[1], reverse=True)
            
            print(f"  Top 5 deployed technologies:")
            for tech_id, share in deployments[:5]:
                if share > 0.01:  # Only show significant deployments
                    abatement = m.abate[tech_id,year].value or 0
                    print(f"    {tech_id}: {share:.3f} share, {abatement/1000:.1f} kt CO₂")
        
        print("\nOptimization test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Optimization failed: {e}")
        return False

if __name__ == "__main__":
    test_macc_optimization()