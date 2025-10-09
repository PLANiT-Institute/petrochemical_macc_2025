"""
Test Optimization with Debug Output
==================================

This script replicates the exact optimization logic with debug output.
"""

from run_optimization_model_v3_facility_based import *

def test_optimization_with_debug():
    """Test optimization with detailed debugging"""
    
    # Load data exactly like the main script
    facilities_df, consumption_df, technologies_df, costs_df, emission_factors_ts_df, fuel_costs_ts_df, targets_df = load_facility_based_data()
    
    target_year = 2030
    print(f"\nTEST OPTIMIZATION DEBUG FOR {target_year}")
    print("=" * 50)
    
    # Get year-specific factors exactly like the main function
    ef_year = emission_factors_ts_df[emission_factors_ts_df['Year'] == target_year].iloc[0]
    fc_year = fuel_costs_ts_df[fuel_costs_ts_df['Year'] == target_year].iloc[0]
    
    print(f"Emission factors for {target_year}:")
    print(f"  NG: {ef_year['Natural_Gas_tCO2_per_GJ']:.3f}, Elec: {ef_year['Electricity_tCO2_per_GJ']:.3f}, H2: {ef_year['Green_Hydrogen_tCO2_per_GJ']:.3f}")
    
    # Merge technology and cost data exactly like main function
    tech_costs = technologies_df.merge(costs_df, on='TechID', how='left')
    
    deployment_options = []
    
    # Test first facility only for debugging
    facility = facilities_df.iloc[0]  # F001
    facility_id = facility['FacilityID']
    
    print(f"\nTesting facility: {facility_id} - {facility['Company']}")
    print(f"TRL requirement: {facility['TechnicalReadiness_Level']}")
    
    # Get baseline consumption for this facility
    facility_consumption = consumption_df[consumption_df['FacilityID'] == facility_id]
    print(f"Process records: {len(facility_consumption)}")
    
    for _, process_row in facility_consumption.iterrows():
        process_type = process_row['ProcessType']
        capacity = process_row['Activity_kt_product']
        
        print(f"\n  Process: {process_type}, Capacity: {capacity} kt/year")
        
        # Get applicable technologies
        applicable_techs = tech_costs[
            (tech_costs['TechGroup'] == process_type) &
            (tech_costs['CommercialYear'] <= target_year) &
            (tech_costs['TechnicalReadiness'] >= facility['TechnicalReadiness_Level'])
        ]
        
        print(f"  Applicable technologies: {len(applicable_techs)}")
        
        # Calculate baseline emissions
        baseline_emissions = calculate_process_baseline_emissions(process_row, ef_year)
        print(f"  Baseline emissions: {baseline_emissions:.1f} ktCO2/year")
        
        for _, tech in applicable_techs.iterrows():
            print(f"\n    Testing tech: {tech['TechID']} - {tech['TechnologyCategory']}")
            
            # Calculate alternative emissions
            alt_emissions = calculate_alternative_emissions(tech, capacity, ef_year)
            print(f"      Alt emissions: {alt_emissions:.1f} ktCO2/year")
            
            # Calculate abatement
            abatement_potential = baseline_emissions - alt_emissions
            print(f"      Abatement: {abatement_potential:.1f} ktCO2/year")
            
            if abatement_potential <= 0:
                print(f"      ❌ No abatement - FILTERED OUT")
                continue
            
            # Calculate costs
            try:
                costs_result = calculate_technology_costs(tech, capacity, fc_year, facility)
                annual_cost = costs_result['AnnualCost_USD']
                lcoa = annual_cost / (abatement_potential * 1000)
                
                print(f"      Annual cost: ${annual_cost:,.0f}")
                print(f"      LCOA: ${lcoa:.0f}/tCO2")
                
                if 0 < lcoa < 25000:
                    print(f"      ✅ VIABLE OPTION!")
                    deployment_options.append({
                        'FacilityID': facility_id,
                        'ProcessType': process_type,
                        'TechID': tech['TechID'],
                        'AbatementPotential_ktCO2': abatement_potential,
                        'LCOA_USD_per_tCO2': lcoa,
                        'AnnualCost_USD': annual_cost
                    })
                else:
                    print(f"      ❌ Too expensive - FILTERED OUT")
                    
            except Exception as e:
                print(f"      ❌ Cost calculation error: {e}")
    
    print(f"\nTOTAL VIABLE OPTIONS FOUND: {len(deployment_options)}")
    
    if len(deployment_options) > 0:
        print(f"\nViable options summary:")
        for i, option in enumerate(deployment_options[:5]):  # Show first 5
            print(f"  {i+1}. {option['FacilityID']}-{option['ProcessType']}-{option['TechID']}")
            print(f"     Abatement: {option['AbatementPotential_ktCO2']:.1f} ktCO2, LCOA: ${option['LCOA_USD_per_tCO2']:.0f}/tCO2")

if __name__ == "__main__":
    test_optimization_with_debug()