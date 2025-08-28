"""
Debug Optimization Issues
========================

This script analyzes why the optimization is not finding viable technology options.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def load_and_analyze():
    """Load data and analyze why no viable options exist"""
    
    data_file = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    
    with pd.ExcelFile(data_file) as xls:
        facilities_df = pd.read_excel(xls, sheet_name='RegionalFacilities')
        consumption_df = pd.read_excel(xls, sheet_name='FacilityBaselineConsumption_2023')
        technologies_df = pd.read_excel(xls, sheet_name='AlternativeTechnologies')
        costs_df = pd.read_excel(xls, sheet_name='AlternativeCosts')
        emission_factors_ts_df = pd.read_excel(xls, sheet_name='EmissionFactors_TimeSeries')
        fuel_costs_ts_df = pd.read_excel(xls, sheet_name='FuelCosts_TimeSeries')
    
    print("DEBUGGING OPTIMIZATION ISSUES")
    print("=" * 50)
    
    # 1. Check technology data
    print("\n1. ALTERNATIVE TECHNOLOGIES ANALYSIS:")
    print("-" * 30)
    
    tech_costs = technologies_df.merge(costs_df, on='TechID', how='left')
    print(f"Total technologies: {len(tech_costs)}")
    print(f"Technology categories: {tech_costs['TechnologyCategory'].unique()}")
    print(f"Process types: {tech_costs['TechGroup'].unique()}")
    
    print(f"\nCommercial years range: {tech_costs['CommercialYear'].min()}-{tech_costs['CommercialYear'].max()}")
    print(f"TRL range: {tech_costs['TechnicalReadiness'].min()}-{tech_costs['TechnicalReadiness'].max()}")
    
    # 2. Check consumption profiles
    print(f"\n2. CONSUMPTION PROFILE COMPARISON:")
    print("-" * 30)
    
    # Check baseline vs alternative consumption
    for process in ['NCC', 'BTX', 'C4']:
        print(f"\n{process} Process:")
        
        # Baseline average
        baseline_process = consumption_df[consumption_df['ProcessType'] == process]
        if len(baseline_process) > 0:
            baseline_avg = baseline_process[['NaturalGas_GJ_per_t', 'Electricity_GJ_per_t', 'FuelOil_GJ_per_t']].mean()
            print(f"  Baseline avg: NG={baseline_avg['NaturalGas_GJ_per_t']:.1f}, Elec={baseline_avg['Electricity_GJ_per_t']:.1f}, FO={baseline_avg['FuelOil_GJ_per_t']:.1f} GJ/t")
        
        # Alternative technologies
        alt_techs = tech_costs[tech_costs['TechGroup'] == process]
        if len(alt_techs) > 0:
            alt_avg = alt_techs[['NaturalGas_GJ_per_t', 'Electricity_GJ_per_t', 'FuelOil_GJ_per_t', 'Hydrogen_GJ_per_t']].mean()
            print(f"  Alt tech avg: NG={alt_avg['NaturalGas_GJ_per_t']:.1f}, Elec={alt_avg['Electricity_GJ_per_t']:.1f}, FO={alt_avg['FuelOil_GJ_per_t']:.1f}, H2={alt_avg['Hydrogen_GJ_per_t']:.1f} GJ/t")
    
    # 3. Check emission factors
    print(f"\n3. EMISSION FACTORS ANALYSIS:")
    print("-" * 30)
    
    ef_2030 = emission_factors_ts_df[emission_factors_ts_df['Year'] == 2030].iloc[0]
    print(f"2030 Emission Factors:")
    print(f"  Natural Gas: {ef_2030['Natural_Gas_tCO2_per_GJ']:.3f} tCO2/GJ")
    print(f"  Electricity: {ef_2030['Electricity_tCO2_per_GJ']:.3f} tCO2/GJ") 
    print(f"  Green H2: {ef_2030['Green_Hydrogen_tCO2_per_GJ']:.3f} tCO2/GJ")
    
    # 4. Calculate sample abatement potential
    print(f"\n4. SAMPLE ABATEMENT CALCULATION:")
    print("-" * 30)
    
    # Take first NCC facility and first applicable technology
    sample_facility = consumption_df[consumption_df['ProcessType'] == 'NCC'].iloc[0]
    sample_tech = tech_costs[tech_costs['TechGroup'] == 'NCC'].iloc[0]
    
    print(f"Sample facility: {sample_facility['FacilityID']} - {sample_facility['Company']}")
    print(f"Sample technology: {sample_tech['TechID']} - {sample_tech['TechnologyCategory']}")
    
    capacity = sample_facility['Activity_kt_product']
    
    # Baseline emissions
    baseline_ng = capacity * sample_facility['NaturalGas_GJ_per_t'] * 1000 * ef_2030['Natural_Gas_tCO2_per_GJ'] / 1000
    baseline_elec = capacity * sample_facility['Electricity_GJ_per_t'] * 1000 * ef_2030['Electricity_tCO2_per_GJ'] / 1000
    baseline_total = baseline_ng + baseline_elec
    
    print(f"Baseline emissions: {baseline_total:.1f} ktCO2/year")
    
    # Alternative emissions
    alt_ng = capacity * sample_tech['NaturalGas_GJ_per_t'] * 1000 * ef_2030['Natural_Gas_tCO2_per_GJ'] / 1000
    alt_elec = capacity * sample_tech['Electricity_GJ_per_t'] * 1000 * ef_2030['Electricity_tCO2_per_GJ'] / 1000
    alt_h2 = capacity * sample_tech['Hydrogen_GJ_per_t'] * 1000 * ef_2030['Green_Hydrogen_tCO2_per_GJ'] / 1000
    alt_total = alt_ng + alt_elec + alt_h2
    
    print(f"Alternative emissions: {alt_total:.1f} ktCO2/year")
    print(f"Abatement potential: {baseline_total - alt_total:.1f} ktCO2/year")
    
    if baseline_total - alt_total <= 0:
        print("❌ ISSUE: Alternative technology has higher or equal emissions!")
        print("   This explains why no viable options are found.")
        
        # Check fuel switching impact
        print(f"\n   Fuel consumption comparison:")
        print(f"   Baseline: NG={sample_facility['NaturalGas_GJ_per_t']:.1f}, Elec={sample_facility['Electricity_GJ_per_t']:.1f} GJ/t")
        print(f"   Alternative: NG={sample_tech['NaturalGas_GJ_per_t']:.1f}, Elec={sample_tech['Electricity_GJ_per_t']:.1f}, H2={sample_tech['Hydrogen_GJ_per_t']:.1f} GJ/t")
    
    # 5. Cost analysis
    print(f"\n5. COST ANALYSIS:")
    print("-" * 30)
    
    print(f"CAPEX range: ${tech_costs['CAPEX_Million_USD_per_kt_capacity'].min():.1f} - ${tech_costs['CAPEX_Million_USD_per_kt_capacity'].max():.1f} M$/kt")
    print(f"OPEX delta range: ${tech_costs['OPEX_Delta_USD_per_t'].min():.1f} - ${tech_costs['OPEX_Delta_USD_per_t'].max():.1f} $/t")
    
    # Simple LCOA calculation
    sample_capex = sample_tech['CAPEX_Million_USD_per_kt_capacity'] * capacity * 1000000
    annual_capex = sample_capex * 0.1  # Simplified 10% annualization
    annual_opex = sample_tech['OPEX_Delta_USD_per_t'] * capacity * 1000
    
    abatement = max(0.01, baseline_total - alt_total)  # Avoid division by zero
    lcoa = (annual_capex + annual_opex) / (abatement * 1000)  # per tonne CO2
    
    print(f"Sample LCOA: ${lcoa:.0f} per tCO2")
    
    # 6. Recommendations
    print(f"\n6. RECOMMENDATIONS:")
    print("-" * 30)
    
    if baseline_total - alt_total <= 0:
        print("❌ PRIMARY ISSUE: Alternative technologies show no emission reduction benefit")
        print("   Solutions:")
        print("   1. Review alternative technology consumption profiles")
        print("   2. Ensure green hydrogen has zero emission factor") 
        print("   3. Check if electric technologies benefit from grid decarbonization")
        print("   4. Add process emission reductions (not just fuel switching)")
    
    if lcoa > 5000:
        print("❌ SECONDARY ISSUE: Very high costs")
        print("   Solutions:")
        print("   1. Review CAPEX assumptions")
        print("   2. Check technology lifetime assumptions")
        print("   3. Consider learning curves and cost reductions")

def main():
    load_and_analyze()

if __name__ == "__main__":
    main()