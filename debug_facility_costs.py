#!/usr/bin/env python3
"""
Debug Facility-Level Costs
==========================

Check individual facility costs to identify the pricing issue.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def debug_facility_costs():
    """Debug facility-level costs for realistic values"""
    
    print("DEBUGGING FACILITY-LEVEL COSTS")
    print("=" * 50)
    
    # Load data
    excel_data = pd.read_excel("data/Korea_Petrochemical_MACC_Database.xlsx", sheet_name=None)
    
    facilities_df = excel_data['RegionalFacilities']
    consumption_df = excel_data['FacilityBaselineConsumption_202']
    technologies_df = excel_data['AlternativeTechnologies']
    costs_df = excel_data['AlternativeCosts']
    ef_df = excel_data['EmissionFactors_TimeSeries']
    
    # Get 2030 emission factors
    ef_2030 = ef_df[ef_df['Year'] == 2030].iloc[0]
    
    print(f"2030 Emission Factors:")
    print(f"  NG: {ef_2030['Natural_Gas_tCO2_per_GJ']:.4f} tCO2/GJ")
    print(f"  Electricity: {ef_2030['Electricity_tCO2_per_GJ']:.4f} tCO2/GJ")
    print(f"  Naphtha: {ef_2030['Naphtha_tCO2_per_t']:.4f} tCO2/t")
    
    print(f"\nINDIVIDUAL FACILITY ANALYSIS:")
    print("-" * 50)
    
    # Look at each facility individually
    for _, facility in facilities_df.iterrows():
        facility_id = facility['FacilityID']
        region = facility['Region']
        company = facility['Company']
        
        facility_consumption = consumption_df[consumption_df['FacilityID'] == facility_id]
        
        if len(facility_consumption) > 0:
            print(f"\n{facility_id} ({company} - {region})")
            
            for _, process in facility_consumption.iterrows():
                process_type = process['ProcessType']
                capacity = process['Activity_kt_product']
                
                print(f"  {process_type}: {capacity:,.0f} kt/year")
                
                # Calculate baseline emissions
                ng = process['NaturalGas_GJ_per_t']
                elec = process['Electricity_GJ_per_t']
                naphtha = process.get('Naphtha_t_per_t', 0)
                
                baseline_emissions_per_t = (
                    ng * ef_2030['Natural_Gas_tCO2_per_GJ'] +
                    elec * ef_2030['Electricity_tCO2_per_GJ'] +
                    naphtha * ef_2030['Naphtha_tCO2_per_t']
                )
                
                print(f"    Baseline: {baseline_emissions_per_t:.3f} tCO2/t")
                
                # Test heat pump for this facility
                heat_pump = technologies_df[
                    (technologies_df['TechGroup'] == process_type) & 
                    (technologies_df['TechnologyCategory'] == 'Heat pump')
                ]
                
                if len(heat_pump) > 0:
                    tech = heat_pump.iloc[0]
                    tech_cost = costs_df[costs_df['TechID'] == tech['TechID']].iloc[0]
                    
                    # Alternative emissions
                    alt_emissions = (
                        tech['NaturalGas_GJ_per_t'] * ef_2030['Natural_Gas_tCO2_per_GJ'] +
                        tech['Electricity_GJ_per_t'] * ef_2030['Electricity_tCO2_per_GJ'] +
                        tech.get('Naphtha_t_per_t', 0) * ef_2030['Naphtha_tCO2_per_t']
                    )
                    
                    abatement_per_t = baseline_emissions_per_t - alt_emissions
                    total_abatement = capacity * abatement_per_t / 1000  # ktCO2/year
                    
                    # Cost calculation
                    capex_per_kt = tech_cost['CAPEX_Million_USD_per_kt_capacity']
                    total_capex = capacity * capex_per_kt  # Million USD
                    
                    # Annualized cost
                    lifetime = tech['Lifetime_years']
                    crf = 0.05 / (1 - (1 + 0.05) ** -lifetime)
                    annual_capex = total_capex * crf
                    
                    # OPEX
                    opex_delta = tech_cost['OPEX_Delta_USD_per_t']
                    annual_opex_delta = capacity * 1000 * opex_delta / 1e6  # Million USD/year
                    
                    total_annual_cost = annual_capex + annual_opex_delta
                    
                    # LCOA calculation
                    if total_abatement > 0:
                        lcoa = total_annual_cost * 1e6 / (total_abatement * 1000)  # USD/tCO2
                    else:
                        lcoa = float('inf')
                    
                    print(f"    Heat pump option:")
                    print(f"      Alternative emissions: {alt_emissions:.3f} tCO2/t")
                    print(f"      Abatement: {abatement_per_t:.3f} tCO2/t")
                    print(f"      Total abatement: {total_abatement:.1f} ktCO2/year")
                    print(f"      CAPEX: ${capex_per_kt:.0f}M/kt × {capacity:,.0f}kt = ${total_capex:,.0f}M")
                    print(f"      Annual CAPEX: ${annual_capex:.1f}M/year")
                    print(f"      OPEX delta: ${opex_delta:+.0f}/t → ${annual_opex_delta:+.1f}M/year")
                    print(f"      Total annual cost: ${total_annual_cost:.1f}M/year")
                    print(f"      LCOA: ${lcoa:,.0f}/tCO2")
                    
                    if lcoa < 25000:
                        print(f"      ✅ COST-EFFECTIVE")
                    else:
                        print(f"      ❌ TOO EXPENSIVE")
                        
                        # Check what makes it expensive
                        if total_capex > 1000:  # > $1B
                            print(f"        → High total CAPEX: ${total_capex:,.0f}M")
                        if annual_capex > 100:  # > $100M/year
                            print(f"        → High annual CAPEX: ${annual_capex:.1f}M/year") 
                        if abs(annual_opex_delta) > 50:  # > $50M/year
                            print(f"        → High OPEX impact: ${annual_opex_delta:+.1f}M/year")
                        if total_abatement < 10:  # < 10 ktCO2/year
                            print(f"        → Low abatement: {total_abatement:.1f} ktCO2/year")

def check_cost_reasonableness():
    """Check if costs are in reasonable ranges"""
    
    print(f"\nCOST REASONABLENESS CHECK")
    print("-" * 30)
    
    excel_data = pd.read_excel("data/Korea_Petrochemical_MACC_Database.xlsx", sheet_name=None)
    costs_df = excel_data['AlternativeCosts']
    
    print("CAPEX per kt capacity (Million USD):")
    print(costs_df['CAPEX_Million_USD_per_kt_capacity'].describe())
    
    print(f"\nOPEX Delta per tonne (USD):")
    print(costs_df['OPEX_Delta_USD_per_t'].describe())
    
    # Industry comparison
    print(f"\nINDUSTRY COMPARISON:")
    print(f"  Typical petrochemical plant: 100-500 kt/year capacity")
    print(f"  Heat pump retrofit: $50-150M per kt capacity")
    print(f"  Our data range: ${costs_df['CAPEX_Million_USD_per_kt_capacity'].min():.0f}-{costs_df['CAPEX_Million_USD_per_kt_capacity'].max():.0f}M per kt")
    
    # Check if our facilities are too large
    consumption_df = excel_data['FacilityBaselineConsumption_202']
    print(f"\nFACILITY SIZE ANALYSIS:")
    print(f"  Capacity range: {consumption_df['Activity_kt_product'].min():.0f}-{consumption_df['Activity_kt_product'].max():.0f} kt/year")
    print(f"  Average capacity: {consumption_df['Activity_kt_product'].mean():.0f} kt/year")
    print(f"  Large facilities (>1000 kt): {len(consumption_df[consumption_df['Activity_kt_product'] > 1000])}")

if __name__ == "__main__":
    debug_facility_costs()
    check_cost_reasonableness()