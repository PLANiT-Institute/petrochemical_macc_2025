#!/usr/bin/env python3
"""
Create optimization-ready technology database compatible with legacy MACC optimization
"""

import pandas as pd
import numpy as np

def create_macc_template_sheet():
    """Create MACC_Template sheet compatible with legacy optimization model"""
    
    # Load enhanced technologies and MACC analysis
    tech_df = pd.read_excel('data/petro_data_v1.0_enhanced.xlsx', sheet_name='alter')
    macc_df = pd.read_csv('outputs/macc_analysis.csv')
    
    print("Creating MACC_Template sheet for optimization...")
    
    # Time horizon for optimization
    years = list(range(2025, 2051))
    
    # Create MACC template entries
    macc_template = []
    
    for _, tech in tech_df.iterrows():
        tech_id = tech['TechID']
        
        # Get MACC metrics
        macc_row = macc_df[macc_df['TechID'] == tech_id].iloc[0] if len(macc_df[macc_df['TechID'] == tech_id]) > 0 else None
        
        if macc_row is None:
            continue
            
        # Calculate ramp-up trajectory
        commercial_year = int(tech['Commercial_year'])
        max_penetration = tech['Max_penetration']
        ramp_rate = tech['Ramp_rate_per_year']
        
        # Activity volume (applicable capacity)
        activity_volume = macc_row['Applicable_capacity_kt'] * 1000  # Convert to tonnes
        
        # Abatement per unit activity
        abatement_per_t = tech['Abatement_tCO2_per_t']
        
        # Cost components (all in KRW, convert from USD using 1300 KRW/USD)
        usd_to_krw = 1300
        capex_krw = tech['CAPEX_USD_per_tpa'] * usd_to_krw
        opex_krw = tech['OPEX_delta_USD_per_t'] * usd_to_krw
        
        # Energy costs need to be calculated based on Korean energy prices
        # Electricity: ~150 KRW/kWh, Natural gas: ~20,000 KRW/GJ, H2: ~4,000 KRW/kg
        electricity_cost = (tech['Electricity_MWh_per_t_product'] or 0) * 1000 * 150  # KRW/t
        gas_cost = (tech['Process_energy_GJ_per_t_product'] or 0) * 20000  # KRW/t
        h2_cost = (tech['Hydrogen_kg_per_t_product'] or 0) * 4000  # KRW/t
        
        var_opex_krw = opex_krw + electricity_cost + gas_cost + h2_cost
        
        # Create time series data
        for year in years:
            # Adoption capacity constraint
            if year < commercial_year:
                max_adoption = 0.0
            else:
                years_since_commercial = year - commercial_year
                max_adoption = min(max_penetration, ramp_rate * years_since_commercial)
            
            # Technology learning (CAPEX reduction over time)
            learning_rate = 0.02  # 2% per year cost reduction
            years_from_2025 = max(0, year - 2025)
            capex_adj = capex_krw * (1 - learning_rate) ** years_from_2025
            
            macc_template.append({
                'TechID': tech_id,
                'Year': year,
                'Ref_Year': year,
                'Eligible_Activity_Volume': activity_volume,
                'Max_Adoption_Share': max_adoption,
                'Abatement_tCO2_per_activity': abatement_per_t,
                'Cost_CAPEX_KRW_per_unit': capex_adj,
                'Cost_FixedOPEX_KRW_per_unit_per_yr': 0,  # Included in variable
                'Cost_VarOPEX_KRW_per_activity': var_opex_krw,
                'Lifetime_years': 20,  # Standard assumption
                'StartYear_Commercial': commercial_year,
                'Technology_Name': tech['Technology'],
                'Product': tech['Product'],
                'TRL': tech['TRL'],
                'Energy_Carrier': tech['Energy_carrier']
            })
    
    return pd.DataFrame(macc_template)

def create_tech_options_sheet():
    """Create TechOptions sheet with technology metadata"""
    
    tech_df = pd.read_excel('data/petro_data_v1.0_enhanced.xlsx', sheet_name='alter')
    
    tech_options = []
    
    for _, tech in tech_df.iterrows():
        tech_options.append({
            'TechID': tech['TechID'],
            'TechName': tech['Technology'],
            'Product': tech['Product'],
            'ProcessType': 'Alternative',
            'EnergyCarrier': tech['Energy_carrier'],
            'Lifetime_years': 20,
            'StartYear_Commercial': tech['Commercial_year'],
            'RampUpSharePerYear': tech['Ramp_rate_per_year'],
            'MaxPenetration': tech['Max_penetration'],
            'TRL': tech['TRL'],
            'CarbonIntensity_tCO2_per_t': -tech['Abatement_tCO2_per_t'],  # Negative because it's abatement
            'CAPEX_Million_KRW_per_kt': tech['CAPEX_USD_per_tpa'] * 1.3,  # Convert USD to KRW
            'Notes': tech['Source_note']
        })
    
    return pd.DataFrame(tech_options)

def create_emissions_target_sheet():
    """Create emissions target sheet for Korean petrochemical sector"""
    
    # Based on Korean Green New Deal and carbon neutrality targets
    targets = [
        {'Year': 2025, 'Target_MtCO2e': 48.0, 'Source': 'Baseline projection'},
        {'Year': 2030, 'Target_MtCO2e': 35.0, 'Source': 'NDC target (30% reduction)'},
        {'Year': 2035, 'Target_MtCO2e': 25.0, 'Source': 'Interim target'},
        {'Year': 2040, 'Target_MtCO2e': 15.0, 'Source': 'Deep decarbonization'},
        {'Year': 2045, 'Target_MtCO2e': 7.5, 'Source': 'Near zero'},
        {'Year': 2050, 'Target_MtCO2e': 2.5, 'Source': 'Net zero (residual)'}
    ]
    
    return pd.DataFrame(targets)

def create_baseline_assumptions_sheet():
    """Create baseline assumptions sheet"""
    
    # Read current emission data
    emissions_df = pd.read_csv('outputs/facility_emissions_final.csv')
    total_emissions_2023 = emissions_df['annual_emissions_kt_co2'].sum() / 1000  # Mt CO2
    
    assumptions = [
        {'Parameter': 'Total_Scope1plus2_MtCO2e_2023', 'Value': total_emissions_2023, 'Unit': 'MtCO2e', 'Source': 'Facility-level calculation'},
        {'Parameter': 'Discount_Rate', 'Value': 0.07, 'Unit': 'fraction', 'Source': 'Korean WACC assumption'},
        {'Parameter': 'Base_Year', 'Value': 2025, 'Unit': 'year', 'Source': 'Model start year'},
        {'Parameter': 'End_Year', 'Value': 2050, 'Unit': 'year', 'Source': 'Carbon neutrality target'},
        {'Parameter': 'Carbon_Price_2030', 'Value': 30000, 'Unit': 'KRW/tCO2', 'Source': 'K-ETS projection'},
        {'Parameter': 'Carbon_Price_2050', 'Value': 150000, 'Unit': 'KRW/tCO2', 'Source': 'High carbon price scenario'},
    ]
    
    return pd.DataFrame(assumptions)

def create_tech_links_sheet():
    """Create technology links sheet for mutual exclusivity and coupling"""
    
    # Define technology relationships
    links = [
        # Ethylene technologies are mutually exclusive within each facility
        {'PrimaryTech': 'ETH_001', 'SecondaryTech': 'ETH_002', 'RuleType': 'MutuallyExclusive', 'Description': 'Electric vs H2 cracking'},
        {'PrimaryTech': 'ETH_001', 'SecondaryTech': 'ETH_003', 'RuleType': 'MutuallyExclusive', 'Description': 'Electric vs bio-ethylene'},
        {'PrimaryTech': 'ETH_001', 'SecondaryTech': 'ETH_004', 'RuleType': 'MutuallyExclusive', 'Description': 'Electric vs MTO'},
        {'PrimaryTech': 'ETH_002', 'SecondaryTech': 'ETH_003', 'RuleType': 'MutuallyExclusive', 'Description': 'H2 vs bio-ethylene'},
        {'PrimaryTech': 'ETH_002', 'SecondaryTech': 'ETH_004', 'RuleType': 'MutuallyExclusive', 'Description': 'H2 vs MTO'},
        {'PrimaryTech': 'ETH_003', 'SecondaryTech': 'ETH_004', 'RuleType': 'MutuallyExclusive', 'Description': 'Bio vs MTO'},
        
        # Propylene technologies are mutually exclusive
        {'PrimaryTech': 'PROP_001', 'SecondaryTech': 'PROP_002', 'RuleType': 'MutuallyExclusive', 'Description': 'Electric vs bio-propylene'},
        
        # Cross-cutting technologies have coupling requirements
        {'PrimaryTech': 'H2_001', 'SecondaryTech': 'ETH_002', 'RuleType': 'Coupling', 'Description': 'H2 infrastructure needed for H2 cracking'},
    ]
    
    return pd.DataFrame(links)

def save_optimization_ready_database():
    """Save complete optimization-ready database"""
    
    print("Creating optimization-ready database...")
    
    # Create all sheets
    macc_template = create_macc_template_sheet()
    tech_options = create_tech_options_sheet()
    emissions_target = create_emissions_target_sheet()
    baseline_assumptions = create_baseline_assumptions_sheet()
    tech_links = create_tech_links_sheet()
    
    # Load existing sheets from enhanced file
    with pd.ExcelFile('data/petro_data_v1.0_enhanced.xlsx') as xls:
        existing_sheets = {}
        for sheet_name in ['source', 'CI', 'CI2', 'utilities']:
            if sheet_name in xls.sheet_names:
                existing_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Combine all sheets
    all_sheets = {
        **existing_sheets,
        'MACC_Template': macc_template,
        'TechOptions': tech_options,
        'Emissions_Target': emissions_target,
        'Baseline_Assumptions': baseline_assumptions,
        'TechLinks': tech_links
    }
    
    # Save optimization-ready file
    output_file = "data/korean_petrochemical_macc_optimization.xlsx"
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"Optimization-ready database saved to {output_file}")
    
    # Print summary
    print(f"\n=== OPTIMIZATION DATABASE SUMMARY ===")
    print(f"Technologies: {len(tech_options)}")
    print(f"MACC entries: {len(macc_template)}")
    print(f"Time horizon: 2025-2050")
    print(f"Emission targets: {len(emissions_target)} milestones")
    print(f"Technology links: {len(tech_links)} relationships")
    
    # Show sample of key technologies
    print(f"\nKey Technologies by Abatement Potential:")
    sample_tech = tech_options.merge(
        macc_template.groupby('TechID')['Eligible_Activity_Volume'].first(), 
        left_on='TechID', right_index=True
    )
    sample_tech['Potential_MtCO2'] = (sample_tech['Eligible_Activity_Volume'] * 
                                    sample_tech['MaxPenetration'] * 
                                    abs(sample_tech['CarbonIntensity_tCO2_per_t']) / 1e6)
    
    top_5 = sample_tech.nlargest(5, 'Potential_MtCO2')[['TechID', 'TechName', 'Product', 'Potential_MtCO2', 'StartYear_Commercial']]
    print(top_5.to_string(index=False))
    
    return output_file

if __name__ == "__main__":
    save_optimization_ready_database()