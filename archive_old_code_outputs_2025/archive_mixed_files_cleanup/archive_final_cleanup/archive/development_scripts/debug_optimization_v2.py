"""
Debug Optimization Issues - After Tech Fix
==========================================

Debug why optimization still finds no viable options after fixing alternative technologies.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def debug_optimization_after_fix():
    """Debug optimization issues after technology fix"""
    
    data_file = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    
    with pd.ExcelFile(data_file) as xls:
        facilities_df = pd.read_excel(xls, sheet_name='RegionalFacilities')
        consumption_df = pd.read_excel(xls, sheet_name='FacilityBaselineConsumption_2023')
        technologies_df = pd.read_excel(xls, sheet_name='AlternativeTechnologies')
        costs_df = pd.read_excel(xls, sheet_name='AlternativeCosts')
        emission_factors_ts_df = pd.read_excel(xls, sheet_name='EmissionFactors_TimeSeries')
        fuel_costs_ts_df = pd.read_excel(xls, sheet_name='FuelCosts_TimeSeries')
    
    print("DEBUGGING OPTIMIZATION AFTER TECH FIX")
    print("=" * 50)
    
    # Test for 2030
    target_year = 2030
    ef_year = emission_factors_ts_df[emission_factors_ts_df['Year'] == target_year].iloc[0]
    fc_year = fuel_costs_ts_df[fuel_costs_ts_df['Year'] == target_year].iloc[0]
    
    # Merge technology and cost data
    tech_costs = technologies_df.merge(costs_df, on='TechID', how='left')
    
    print(f"\n1. TECHNOLOGY FILTERING FOR {target_year}:")
    print("-" * 30)
    
    total_techs = len(tech_costs)
    commercial_filter = tech_costs['CommercialYear'] <= target_year
    commercial_techs = len(tech_costs[commercial_filter])
    
    print(f"Total technologies: {total_techs}")
    print(f"Commercially available by {target_year}: {commercial_techs}")
    
    # Check TRL filtering
    for _, facility in facilities_df.iterrows():
        facility_readiness = facility['TechnicalReadiness_Level']
        applicable_techs = tech_costs[
            (tech_costs['CommercialYear'] <= target_year) &
            (tech_costs['TechnicalReadiness'] >= facility_readiness)
        ]
        print(f"  {facility['FacilityID']} (TRL≥{facility_readiness}): {len(applicable_techs)} technologies")
    
    print(f"\n2. DETAILED ABATEMENT CALCULATION:")
    print("-" * 30)
    
    # Test multiple facility-technology combinations
    viable_count = 0
    total_combinations = 0
    
    for _, facility in facilities_df.iterrows():
        facility_id = facility['FacilityID']
        facility_consumption = consumption_df[consumption_df['FacilityID'] == facility_id]
        
        for _, process_row in facility_consumption.iterrows():
            process_type = process_row['ProcessType']
            capacity = process_row['Activity_kt_product']
            
            applicable_techs = tech_costs[
                (tech_costs['TechGroup'] == process_type) &
                (tech_costs['CommercialYear'] <= target_year) &
                (tech_costs['TechnicalReadiness'] >= facility['TechnicalReadiness_Level'])
            ]
            
            for _, tech in applicable_techs.iterrows():
                total_combinations += 1
                
                # Calculate baseline emissions
                baseline_ng = capacity * process_row['NaturalGas_GJ_per_t'] * 1000 * ef_year['Natural_Gas_tCO2_per_GJ'] / 1000
                baseline_elec = capacity * process_row['Electricity_GJ_per_t'] * 1000 * ef_year['Electricity_tCO2_per_GJ'] / 1000
                baseline_total = baseline_ng + baseline_elec
                
                # Calculate alternative emissions
                alt_ng = capacity * tech['NaturalGas_GJ_per_t'] * 1000 * ef_year['Natural_Gas_tCO2_per_GJ'] / 1000
                alt_elec = capacity * tech['Electricity_GJ_per_t'] * 1000 * ef_year['Electricity_tCO2_per_GJ'] / 1000
                alt_h2 = capacity * tech['Hydrogen_GJ_per_t'] * 1000 * ef_year['Green_Hydrogen_tCO2_per_GJ'] / 1000
                alt_total = alt_ng + alt_elec + alt_h2
                
                abatement_potential = baseline_total - alt_total
                
                if abatement_potential > 0:
                    # Calculate costs
                    capex_per_kt = tech['CAPEX_Million_USD_per_kt_capacity']
                    total_capex = capex_per_kt * capacity
                    regional_multiplier = facility['Labor_Cost_Index'] / 100
                    adjusted_capex = total_capex * regional_multiplier
                    
                    lifetime = tech['Lifetime_years']
                    discount_rate = 0.08
                    annuity_factor = discount_rate / (1 - (1 + discount_rate) ** (-lifetime))
                    annual_capex = adjusted_capex * 1000000 * annuity_factor
                    
                    annual_opex_delta = tech['OPEX_Delta_USD_per_t'] * capacity * 1000
                    
                    # Simplified fuel cost
                    fuel_cost_delta = 0
                    if 'Electric' in tech['TechnologyCategory']:
                        elec_consumption_delta = capacity * (tech['Electricity_GJ_per_t'] - process_row['Electricity_GJ_per_t']) * 1000
                        fuel_cost_delta = elec_consumption_delta * fc_year['Electricity_USD_per_GJ']
                    elif 'H2' in tech['TechnologyCategory']:
                        h2_consumption = capacity * tech['Hydrogen_GJ_per_t'] * 1000
                        fuel_cost_delta = h2_consumption * fc_year['Green_Hydrogen_USD_per_GJ']
                    
                    maintenance_cost = adjusted_capex * 1000000 * (tech['MaintenanceCost_Pct'] / 100)
                    total_annual_cost = annual_capex + annual_opex_delta + fuel_cost_delta + maintenance_cost
                    
                    lcoa = total_annual_cost / (abatement_potential * 1000) if abatement_potential > 0 else np.inf
                    
                    # Check viability filters
                    abatement_positive = abatement_potential > 0
                    cost_reasonable = 0 < lcoa < 10000
                    
                    if abatement_positive and cost_reasonable:
                        viable_count += 1
                        
                        if viable_count <= 5:  # Show first few viable options
                            print(f"\n  Viable Option {viable_count}:")
                            print(f"    {facility_id}-{process_type}-{tech['TechID']}")
                            print(f"    Abatement: {abatement_potential:.1f} ktCO2/year")
                            print(f"    LCOA: ${lcoa:.0f}/tCO2")
                            print(f"    Annual cost: ${total_annual_cost:,.0f}")
                    
                    elif abatement_positive and not cost_reasonable:
                        if total_combinations <= 10:  # Show first few for debugging
                            print(f"\n  High Cost Option:")
                            print(f"    {facility_id}-{process_type}-{tech['TechID']}")
                            print(f"    Abatement: {abatement_potential:.1f} ktCO2/year")
                            print(f"    LCOA: ${lcoa:.0f}/tCO2 (TOO HIGH)")
    
    print(f"\n3. SUMMARY:")
    print("-" * 30)
    print(f"Total facility-technology combinations: {total_combinations}")
    print(f"Viable options (positive abatement, reasonable cost): {viable_count}")
    
    if viable_count == 0:
        print(f"\n❌ ISSUE: All options either have no abatement or costs > $10,000/tCO2")
        print(f"Recommendations:")
        print(f"  1. Lower cost threshold from $10,000/tCO2 to $20,000/tCO2")
        print(f"  2. Review CAPEX assumptions (might be too high)")
        print(f"  3. Check if learning curves should be applied")
    else:
        print(f"\n✅ Found {viable_count} viable options! Optimization should work.")

def main():
    debug_optimization_after_fix()

if __name__ == "__main__":
    main()