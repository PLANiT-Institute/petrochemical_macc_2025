"""
Debug Corrected Model - Simplified Version
==========================================

Simplified version to identify why all options are being filtered out.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def debug_corrected_model():
    """Debug the corrected model step by step"""
    
    print("DEBUGGING CORRECTED MODEL")
    print("=" * 50)
    
    # Load data
    excel_data = pd.read_excel("data/Korea_Petrochemical_MACC_Database.xlsx", sheet_name=None)
    
    facilities_df = excel_data['RegionalFacilities']
    consumption_df = excel_data['FacilityBaselineConsumption_202']
    technologies_df = excel_data['AlternativeTechnologies']
    costs_df = excel_data['AlternativeCosts']
    ef_df = excel_data['EmissionFactors_TimeSeries']
    
    print(f"Loaded data successfully")
    
    # Test for 2030
    target_year = 2030
    
    # Get emission factors for 2030 (should have low-carbon naphtha)
    ef_2030 = ef_df[ef_df['Year'] == target_year].iloc[0]
    print(f"\\n2030 Emission Factors:")
    print(f"  NG: {ef_2030['Natural_Gas_tCO2_per_GJ']:.4f} tCO2/GJ")
    print(f"  Electricity: {ef_2030['Electricity_tCO2_per_GJ']:.4f} tCO2/GJ")
    print(f"  Naphtha: {ef_2030['Naphtha_tCO2_per_t']:.4f} tCO2/t (should be 0.219 if low-carbon)")
    
    # Check if we have low-carbon naphtha
    if ef_2030['Naphtha_tCO2_per_t'] <= 0.25:
        print("  ✅ Low-carbon naphtha detected!")
    else:
        print("  ❌ Still using conventional naphtha - need to fix this")
        return
    
    # Calculate one example manually
    print(f"\\nMANUAL CALCULATION EXAMPLE:")
    print("-" * 40)
    
    # Get Yeosu NCC baseline
    yeosu_ncc = consumption_df[
        (consumption_df['FacilityID'].str.contains('F001|F002|F003|F004')) &
        (consumption_df['ProcessType'] == 'NCC')
    ]
    
    if len(yeosu_ncc) > 0:
        # Average NCC consumption in Yeosu
        total_capacity = yeosu_ncc['Activity_kt_product'].sum()
        avg_ng = (yeosu_ncc['NaturalGas_GJ_per_t'] * yeosu_ncc['Activity_kt_product']).sum() / total_capacity
        avg_elec = (yeosu_ncc['Electricity_GJ_per_t'] * yeosu_ncc['Activity_kt_product']).sum() / total_capacity
        avg_naphtha = (yeosu_ncc.get('Naphtha_t_per_t', 0) * yeosu_ncc['Activity_kt_product']).sum() / total_capacity
        
        # Baseline emissions
        baseline_emissions = (
            avg_ng * ef_2030['Natural_Gas_tCO2_per_GJ'] +
            avg_elec * ef_2030['Electricity_tCO2_per_GJ'] +
            avg_naphtha * ef_2030['Naphtha_tCO2_per_t']
        )
        
        print(f"Yeosu NCC Baseline:")
        print(f"  Capacity: {total_capacity:,.0f} kt/year")
        print(f"  NG: {avg_ng:.2f} GJ/t → {avg_ng * ef_2030['Natural_Gas_tCO2_per_GJ']:.3f} tCO2/t")
        print(f"  Elec: {avg_elec:.2f} GJ/t → {avg_elec * ef_2030['Electricity_tCO2_per_GJ']:.3f} tCO2/t")
        print(f"  Naphtha: {avg_naphtha:.2f} t/t → {avg_naphtha * ef_2030['Naphtha_tCO2_per_t']:.3f} tCO2/t")
        print(f"  Total: {baseline_emissions:.3f} tCO2/t")
        
        # Test heat pump alternative
        heat_pump = technologies_df[
            (technologies_df['TechGroup'] == 'NCC') & 
            (technologies_df['TechnologyCategory'] == 'Heat pump')
        ].iloc[0]
        
        alt_emissions = (
            heat_pump['NaturalGas_GJ_per_t'] * ef_2030['Natural_Gas_tCO2_per_GJ'] +
            heat_pump['Electricity_GJ_per_t'] * ef_2030['Electricity_tCO2_per_GJ'] +
            heat_pump.get('Naphtha_t_per_t', 0) * ef_2030['Naphtha_tCO2_per_t']
        )
        
        abatement_per_t = baseline_emissions - alt_emissions
        total_abatement = total_capacity * abatement_per_t / 1000  # ktCO2/year
        
        print(f"\\nHeat Pump Alternative:")
        print(f"  NG: {heat_pump['NaturalGas_GJ_per_t']:.2f} GJ/t")
        print(f"  Elec: {heat_pump['Electricity_GJ_per_t']:.2f} GJ/t") 
        print(f"  Emissions: {alt_emissions:.3f} tCO2/t")
        print(f"  Abatement: {abatement_per_t:.3f} tCO2/t")
        print(f"  Total potential: {total_abatement:.1f} ktCO2/year")
        
        # Calculate costs
        heat_pump_cost = costs_df[costs_df['TechID'] == heat_pump['TechID']].iloc[0]
        
        capex_per_kt = heat_pump_cost['CAPEX_Million_USD_per_kt_capacity']
        total_capex = total_capacity * capex_per_kt
        
        # Annualized
        lifetime = heat_pump['Lifetime_years']
        crf = 0.05 / (1 - (1 + 0.05) ** -lifetime)
        annual_capex = total_capex * crf
        
        # OPEX
        opex_delta = heat_pump_cost['OPEX_Delta_USD_per_t']
        annual_opex_delta = total_capacity * 1000 * opex_delta / 1e6
        
        total_annual_cost = annual_capex + annual_opex_delta
        
        lcoa = total_annual_cost * 1e6 / (total_abatement * 1000) if total_abatement > 0 else float('inf')
        
        print(f"\\nCost Analysis:")
        print(f"  CAPEX: ${capex_per_kt:.0f}M per kt → ${total_capex:.1f}M total")
        print(f"  Annual CAPEX: ${annual_capex:.1f}M/year")
        print(f"  OPEX delta: ${opex_delta:+.0f}/t → ${annual_opex_delta:+.1f}M/year")
        print(f"  Total annual cost: ${total_annual_cost:.1f}M/year")
        print(f"  LCOA: ${lcoa:.0f}/tCO2")
        
        if lcoa < 25000:
            print(f"  ✅ Cost-effective option!")
        else:
            print(f"  ❌ Too expensive (>${lcoa:.0f}/tCO2 vs $25,000/tCO2 limit)")
            
        # Show impact of low-carbon naphtha
        conventional_naphtha_ef = 0.730  # Original
        if avg_naphtha > 0:
            feedstock_benefit = avg_naphtha * (conventional_naphtha_ef - ef_2030['Naphtha_tCO2_per_t'])
            feedstock_total = total_capacity * feedstock_benefit / 1000
            print(f"\\nFeedstock Switching Benefit:")
            print(f"  Naphtha reduction: {feedstock_benefit:.3f} tCO2/t")
            print(f"  Total benefit: {feedstock_total:.1f} ktCO2/year")
            print(f"  Combined abatement: {total_abatement + feedstock_total:.1f} ktCO2/year")

def fix_emission_factors():
    """Fix emission factors to include low-carbon naphtha"""
    
    print("\\nFIXING EMISSION FACTORS")
    print("-" * 40)
    
    excel_path = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    excel_data = pd.read_excel(excel_path, sheet_name=None)
    
    ef_df = excel_data['EmissionFactors_TimeSeries'].copy()
    
    # Update naphtha emission factor from 2030
    baseline_naphtha = 0.730
    low_carbon_naphtha = baseline_naphtha * 0.3  # 70% reduction
    
    updated_count = 0
    for idx, row in ef_df.iterrows():
        if row['Year'] >= 2030:
            ef_df.loc[idx, 'Naphtha_tCO2_per_t'] = low_carbon_naphtha
            updated_count += 1
    
    print(f"Updated {updated_count} records with low-carbon naphtha factor: {low_carbon_naphtha:.3f} tCO2/t")
    
    # Save back
    all_sheets = excel_data.copy()
    all_sheets['EmissionFactors_TimeSeries'] = ef_df
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print("✅ Emission factors updated and saved")

if __name__ == "__main__":
    # First fix the emission factors
    fix_emission_factors()
    
    # Then debug
    debug_corrected_model()