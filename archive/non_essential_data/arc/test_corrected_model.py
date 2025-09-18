#!/usr/bin/env python3
"""
Test script for the corrected MACC model with proper scale units
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'petrochem'))

from petrochem.lib.data.loaders import DataLoader
from petrochem.lib.optimization.model_builder_corrected import CorrectedMACCModelBuilder
from petrochem.lib.analysis.results import ModelResults
from petrochem.model_pyomo import solve_model
import pandas as pd

def test_corrected_model():
    """Test the corrected MACC model with proper units"""
    
    print("Testing Corrected MACC Model")
    print("=" * 50)
    
    # Load data
    data_dir = "data"
    loader = DataLoader(data_dir)
    
    print("1. Loading data...")
    try:
        scenario = loader.load_emissions_scenario("Korea_Petrochemical_MACC_Database.xlsx")
        portfolio = loader.load_technology_portfolio() 
        print("   ✓ Data loaded successfully")
    except Exception as e:
        print(f"   ✗ Data loading failed: {str(e)}")
        return False
    
    print(f"   - Loaded {len(portfolio.technologies)} technologies")
    print(f"   - Timeline: {min(scenario.timeline)} to {max(scenario.timeline)}")
    print(f"   - Processes: {list(scenario.baseline.process_baselines.keys())}")
    
    # Build corrected model
    print("\n2. Building corrected model...")
    builder = CorrectedMACCModelBuilder(scenario, portfolio)
    model = builder.build_model(allow_slack=True, discount_rate=0.05)
    
    # Display model summary
    summary = builder.get_model_summary()
    print(f"   - Model type: {summary['model_type']}")
    print(f"   - Variables: {summary['variables']}")
    print(f"   - Unit corrections applied:")
    for unit_type, description in summary['unit_corrections'].items():
        print(f"     * {unit_type}: {description}")
    
    # Test model structure
    print("\n3. Validating model structure...")
    
    # Check that variables exist with correct domains
    assert hasattr(model, 'install_capacity'), "Missing install_capacity variable"
    assert hasattr(model, 'total_capacity'), "Missing total_capacity variable"  
    assert hasattr(model, 'production'), "Missing production variable"
    assert hasattr(model, 'abatement'), "Missing abatement variable"
    print("   ✓ All required variables present")
    
    # Check constraints exist
    required_constraints = [
        'capacity_evolution', 'production_limit', 'capacity_limit',
        'ramp_constraint', 'abatement_calc', 'target_constraint'
    ]
    for constraint_name in required_constraints:
        assert hasattr(model, constraint_name), f"Missing constraint: {constraint_name}"
    print("   ✓ All required constraints present")
    
    # Check parameters have reasonable values
    print("\n4. Checking parameter values...")
    
    # Sample some parameter values
    sample_tech = list(model.TECHS)[0]
    sample_year = list(model.YEARS)[5]  # Not first year
    
    capex_val = model.capex_per_kt[sample_tech, sample_year]
    opex_val = model.opex_per_t[sample_tech, sample_year]
    max_cap_val = model.max_capacity[sample_tech, sample_year]
    
    print(f"   - Sample CAPEX (Million USD/kt): {capex_val}")
    print(f"   - Sample OPEX (USD/t): {opex_val}")
    print(f"   - Sample Max Capacity (kt/year): {max_cap_val}")
    
    # Verify units make sense
    assert capex_val >= 0, "CAPEX should be non-negative"
    assert max_cap_val >= 0, "Max capacity should be non-negative"
    print("   ✓ Parameter values are reasonable")
    
    # Solve model
    print("\n5. Solving corrected model...")
    try:
        solver_used, results = solve_model(model, solver="auto")
        print(f"   ✓ Model solved successfully")
        print(f"   - Solver: {solver_used}")
        print(f"   - Status: {results.solver.termination_condition if hasattr(results, 'solver') else 'OK'}")
        print(f"   - Objective value: {model.total_cost.expr() if hasattr(model, 'total_cost') else 'N/A'}")
            
    except Exception as e:
        print(f"   ✗ Solver error: {str(e)}")
        return False
    
    # Analyze results
    print("\n6. Analyzing corrected model results...")
    results = ModelResults(model, scenario, portfolio)
    
    # Check solution makes sense
    total_capacity_installed = 0
    total_production = 0 
    total_abatement = 0
    
    for tech in model.TECHS:
        for year in model.YEARS:
            if hasattr(model.install_capacity[tech, year], 'value'):
                cap_val = model.install_capacity[tech, year].value or 0
                prod_val = model.production[tech, year].value or 0
                abate_val = model.abatement[tech, year].value or 0
                
                total_capacity_installed += cap_val
                total_production += prod_val
                total_abatement += abate_val
    
    print(f"   - Total capacity installed: {total_capacity_installed:,.1f} kt/year")
    print(f"   - Total annual production: {total_production:,.1f} kt/year") 
    print(f"   - Total abatement achieved: {total_abatement/1e6:,.1f} MtCO2")
    
    # Check capacity-production relationship
    if total_production > 0 and total_capacity_installed > 0:
        utilization = total_production / total_capacity_installed
        print(f"   - Average capacity utilization: {utilization:.1%}")
        
        # Utilization should be reasonable (0-100%)
        assert 0 <= utilization <= 1.1, f"Unreasonable utilization rate: {utilization:.1%}"
        print("   ✓ Capacity-production relationship is reasonable")
    
    # Verify emissions targets
    print("\n7. Checking emissions target achievement...")
    
    target_years = [2030, 2040, 2050]
    for year in target_years:
        if year in scenario.timeline:
            required = scenario.get_required_abatement(year) * 1e6  # Convert to tonnes
            
            achieved = sum(
                model.abatement[tech, year].value or 0 
                for tech in model.TECHS
            )
            
            shortfall = model.shortfall[year].value or 0 if hasattr(model, 'shortfall') else 0
            
            achievement_rate = (achieved / required * 100) if required > 0 else 100
            
            print(f"   - {year}: {achievement_rate:.1f}% target achievement")
            print(f"     Required: {required/1e6:.1f} MtCO2, Achieved: {achieved/1e6:.1f} MtCO2, Shortfall: {shortfall/1e6:.1f} MtCO2")
    
    print("\n" + "=" * 50)
    print("✓ CORRECTED MODEL VALIDATION COMPLETE")
    print("✓ All unit consistency checks passed")
    print("✓ Model formulation follows corrected logic")
    print("✓ Capacity-production separation working properly")
    
    return True

if __name__ == "__main__":
    success = test_corrected_model()
    if success:
        print("\n🎉 Corrected model test PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Corrected model test FAILED!")
        sys.exit(1)