#!/usr/bin/env python3
"""
Create enhanced MACC database with realistic technology constraints and renewable energy
"""

import pandas as pd
import numpy as np
from pathlib import Path

def create_enhanced_macc_database():
    """Create enhanced MACC database with improved technology portfolio"""
    
    print("🔧 CREATING ENHANCED MACC DATABASE")
    print("="*60)
    
    # Load current database
    current_macc = pd.read_excel('data/korean_petrochemical_macc_optimization.xlsx', sheet_name='MACC_Template')
    current_tech = pd.read_excel('data/korean_petrochemical_macc_optimization.xlsx', sheet_name='TechOptions')
    
    # Load facility data for emissions calculation
    facility_data = pd.read_csv("outputs/facility_emissions_korea_scale_52mt_final.csv")
    
    print("✓ Loaded current database")
    
    # Calculate process-specific emissions for EE constraint calculation
    process_emissions = facility_data.groupby('process')['annual_emissions_kt_co2'].sum()
    total_emissions_mt = process_emissions.sum() / 1000  # Convert to Mt
    
    print(f"✓ Total baseline emissions: {total_emissions_mt:.1f} Mt CO₂")
    
    # Define process-specific EE constraints
    ee_constraints = {
        'Naphtha Cracker': {
            'max_penetration': 0.10,
            'emissions_kt': process_emissions.get('Naphtha Cracker', 0),
            'rationale': 'High-temperature processes, thermodynamic constraints'
        },
        'BTX Plant': {
            'max_penetration': 0.20,
            'emissions_kt': process_emissions.get('BTX Plant', 0),
            'rationale': 'Moderate heat recovery potential'
        },
        'Utility': {
            'max_penetration': 0.35,
            'emissions_kt': process_emissions.get('Utility', 0),
            'rationale': 'High efficiency potential in utilities'
        }
    }
    
    # Calculate weighted average EE potential
    total_ee_potential_kt = 0
    for process, constraint in ee_constraints.items():
        potential = constraint['emissions_kt'] * constraint['max_penetration']
        total_ee_potential_kt += potential
        print(f"  • {process}: {constraint['max_penetration']:.0%} × {constraint['emissions_kt']:.0f} kt = {potential:.0f} kt CO₂")
    
    realistic_ee_potential_mt = total_ee_potential_kt / 1000
    realistic_ee_penetration = realistic_ee_potential_mt / total_emissions_mt
    
    print(f"✓ Realistic EE potential: {realistic_ee_potential_mt:.1f} Mt CO₂ ({realistic_ee_penetration:.1%})")
    
    # Create enhanced technology list
    enhanced_technologies = []
    
    # 1. Update existing EE technology with realistic constraints
    ee_original = current_macc[current_macc['TechID'] == 'EE_001'].iloc[0]
    enhanced_technologies.append({
        'TechID': 'EE_001',
        'TechName': 'Energy Efficiency Package (Process-Constrained)',
        'Cost_USD_per_tCO2': -69,  # Keep original cost
        'Abatement_Potential_MtCO2_per_year': realistic_ee_potential_mt,
        'TRL': 9,
        'Commercial_Year': 2025,
        'Product': 'All_Products',
        'ProcessType': 'Efficiency',
        'EnergyCarrier': 'Mixed',
        'MaxPenetration': realistic_ee_penetration,
        'RampUpSharePerYear': 0.15,
        'StartYear_Commercial': 2025,
        'Notes': 'Process-specific constraints: NCC 10%, BTX 20%, Utilities 35%'
    })
    
    # 2. Split EE into process-specific technologies for better modeling
    ee_by_process = [
        {
            'TechID': 'EE_NCC',
            'TechName': 'Naphtha Cracker Energy Efficiency',
            'Cost_USD_per_tCO2': -50,  # Lower savings due to constraints
            'Abatement_Potential_MtCO2_per_year': ee_constraints['Naphtha Cracker']['emissions_kt'] / 1000,
            'TRL': 9,
            'Commercial_Year': 2025,
            'Product': 'Ethylene',  # Representative product
            'ProcessType': 'Efficiency',
            'EnergyCarrier': 'Mixed',
            'MaxPenetration': 0.10,
            'RampUpSharePerYear': 0.10,  # Slower ramp-up
            'StartYear_Commercial': 2025,
            'Notes': 'Limited by high-temperature process constraints'
        },
        {
            'TechID': 'EE_BTX',
            'TechName': 'BTX Plant Energy Efficiency',
            'Cost_USD_per_tCO2': -65,
            'Abatement_Potential_MtCO2_per_year': ee_constraints['BTX Plant']['emissions_kt'] / 1000,
            'TRL': 9,
            'Commercial_Year': 2025,
            'Product': '벤젠',  # Representative product
            'ProcessType': 'Efficiency',
            'EnergyCarrier': 'Mixed',
            'MaxPenetration': 0.20,
            'RampUpSharePerYear': 0.12,
            'StartYear_Commercial': 2025,
            'Notes': 'Moderate heat recovery potential'
        },
        {
            'TechID': 'EE_UTL',
            'TechName': 'Utility System Energy Efficiency',
            'Cost_USD_per_tCO2': -85,  # Highest savings in utilities
            'Abatement_Potential_MtCO2_per_year': ee_constraints['Utility']['emissions_kt'] / 1000,
            'TRL': 9,
            'Commercial_Year': 2025,
            'Product': 'All_Products',
            'ProcessType': 'Efficiency',
            'EnergyCarrier': 'Mixed',
            'MaxPenetration': 0.35,
            'RampUpSharePerYear': 0.20,  # Faster implementation
            'StartYear_Commercial': 2025,
            'Notes': 'High potential in steam systems, motors, cogeneration'
        }
    ]
    
    # 3. Add new renewable energy technologies
    renewable_technologies = [
        {
            'TechID': 'RE_001',
            'TechName': 'Solar Thermal for Process Heat',
            'Cost_USD_per_tCO2': 100,
            'Abatement_Potential_MtCO2_per_year': 3.5,  # Low-medium temp applications
            'TRL': 8,
            'Commercial_Year': 2026,
            'Product': 'All_Products',
            'ProcessType': 'Renewable',
            'EnergyCarrier': 'Solar',
            'MaxPenetration': 0.25,
            'RampUpSharePerYear': 0.08,
            'StartYear_Commercial': 2026,
            'Notes': 'For temperatures 80-250°C: polymerization, separation, drying'
        },
        {
            'TechID': 'RE_002',
            'TechName': 'Industrial Solar PV Systems',
            'Cost_USD_per_tCO2': 55,
            'Abatement_Potential_MtCO2_per_year': 8.5,  # Electricity demand
            'TRL': 9,
            'Commercial_Year': 2025,
            'Product': 'All_Products',
            'ProcessType': 'Renewable',
            'EnergyCarrier': 'Solar',
            'MaxPenetration': 0.40,
            'RampUpSharePerYear': 0.12,
            'StartYear_Commercial': 2025,
            'Notes': 'On-site solar electricity generation'
        },
        {
            'TechID': 'RE_003',
            'TechName': 'Wind Power Purchase Agreements',
            'Cost_USD_per_tCO2': 40,
            'Abatement_Potential_MtCO2_per_year': 12.0,  # Large electricity demand
            'TRL': 9,
            'Commercial_Year': 2025,
            'Product': 'All_Products',
            'ProcessType': 'Renewable',
            'EnergyCarrier': 'Wind',
            'MaxPenetration': 0.60,
            'RampUpSharePerYear': 0.15,
            'StartYear_Commercial': 2025,
            'Notes': 'Long-term renewable electricity contracts'
        },
        {
            'TechID': 'HP_002',
            'TechName': 'High-Temperature Heat Pumps',
            'Cost_USD_per_tCO2': 175,
            'Abatement_Potential_MtCO2_per_year': 4.2,  # Medium temp applications
            'TRL': 7,
            'Commercial_Year': 2028,
            'Product': 'All_Products',
            'ProcessType': 'Electrification',
            'EnergyCarrier': 'Electricity',
            'MaxPenetration': 0.30,
            'RampUpSharePerYear': 0.10,
            'StartYear_Commercial': 2028,
            'Notes': 'Heat pumps for 120-200°C: distillation, evaporation'
        },
        {
            'TechID': 'ES_001',
            'TechName': 'Battery Energy Storage Systems',
            'Cost_USD_per_tCO2': 140,
            'Abatement_Potential_MtCO2_per_year': 2.8,  # Load balancing
            'TRL': 8,
            'Commercial_Year': 2027,
            'Product': 'All_Products',
            'ProcessType': 'Infrastructure',
            'EnergyCarrier': 'Electricity',
            'MaxPenetration': 0.20,
            'RampUpSharePerYear': 0.08,
            'StartYear_Commercial': 2027,
            'Notes': 'Grid stabilization and renewable integration'
        }
    ]
    
    # 4. Keep existing product-specific technologies (validated)
    existing_product_techs = current_tech[
        ~current_tech['TechID'].isin(['EE_001', 'HP_001'])
    ].copy()
    
    # 5. Update heat pump technology
    hp_enhanced = {
        'TechID': 'HP_001',
        'TechName': 'Low-Medium Temperature Heat Pumps',
        'Cost_USD_per_tCO2': 10,  # Keep original cost
        'Abatement_Potential_MtCO2_per_year': 6.5,  # Slightly reduced from original
        'TRL': 8,
        'Commercial_Year': 2025,
        'Product': 'All_Products',
        'ProcessType': 'Electrification',
        'EnergyCarrier': 'Electricity',
        'MaxPenetration': 0.50,  # Reduced from 0.6
        'RampUpSharePerYear': 0.12,
        'StartYear_Commercial': 2025,
        'Notes': 'Heat pumps for temperatures up to 120°C'
    }
    
    # Combine all technologies
    all_enhanced_techs = []
    
    # Add process-specific EE
    all_enhanced_techs.extend(ee_by_process)
    
    # Add renewable technologies
    all_enhanced_techs.extend(renewable_technologies)
    
    # Add updated heat pump
    all_enhanced_techs.append(hp_enhanced)
    
    # Add existing product-specific technologies with original MACC data
    for _, tech in existing_product_techs.iterrows():
        macc_data = current_macc[current_macc['TechID'] == tech['TechID']].iloc[0]
        
        enhanced_tech = {
            'TechID': tech['TechID'],
            'TechName': tech['TechName'],
            'Cost_USD_per_tCO2': macc_data['Cost_USD_per_tCO2'],
            'Abatement_Potential_MtCO2_per_year': macc_data['Abatement_Potential_MtCO2_per_year'],
            'TRL': macc_data['TRL'],
            'Commercial_Year': macc_data['Commercial_Year'],
            'Product': tech['Product'],
            'ProcessType': tech['ProcessType'],
            'EnergyCarrier': tech['EnergyCarrier'],
            'MaxPenetration': tech['MaxPenetration'],
            'RampUpSharePerYear': tech['RampUpSharePerYear'],
            'StartYear_Commercial': tech['StartYear_Commercial'],
            'Notes': f"Original technology: {tech.get('Notes', 'Product-specific solution')}"
        }
        all_enhanced_techs.append(enhanced_tech)
    
    # Create enhanced DataFrames
    enhanced_macc_df = pd.DataFrame(all_enhanced_techs)
    enhanced_tech_df = enhanced_macc_df.copy()
    
    # Create separate MACC_Template and TechOptions sheets
    macc_columns = ['TechID', 'TechName', 'Cost_USD_per_tCO2', 'Abatement_Potential_MtCO2_per_year', 
                   'TRL', 'Commercial_Year', 'Notes']
    tech_columns = ['TechID', 'TechName', 'Product', 'ProcessType', 'EnergyCarrier', 
                   'MaxPenetration', 'RampUpSharePerYear', 'StartYear_Commercial', 'Notes']
    
    enhanced_macc_template = enhanced_macc_df[macc_columns].copy()
    enhanced_tech_options = enhanced_tech_df[tech_columns].copy()
    
    # Add cumulative abatement for MACC template
    enhanced_macc_template = enhanced_macc_template.sort_values('Cost_USD_per_tCO2')
    enhanced_macc_template['Cumulative_Abatement_MtCO2_per_year'] = enhanced_macc_template['Abatement_Potential_MtCO2_per_year'].cumsum()
    
    # Save enhanced database
    output_file = 'data/korean_petrochemical_macc_enhanced.xlsx'
    
    # Load other sheets from original file
    original_sheets = {}
    with pd.ExcelFile('data/korean_petrochemical_macc_optimization.xlsx') as xls:
        for sheet_name in xls.sheet_names:
            if sheet_name not in ['MACC_Template', 'TechOptions']:
                original_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Write enhanced database
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Write enhanced sheets
        enhanced_macc_template.to_excel(writer, sheet_name='MACC_Template', index=False)
        enhanced_tech_options.to_excel(writer, sheet_name='TechOptions', index=False)
        
        # Copy other sheets
        for sheet_name, df in original_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"✓ Enhanced database saved: {output_file}")
    print(f"✓ Technologies: {len(enhanced_macc_template)} (vs {len(current_macc)} original)")
    
    # Print summary
    print(f"\n📊 ENHANCED TECHNOLOGY SUMMARY:")
    print(f"="*60)
    
    tech_categories = enhanced_tech_options.groupby('ProcessType').agg({
        'TechID': 'count',
        'Product': lambda x: len(x.unique())
    })
    tech_categories.columns = ['Technology_Count', 'Product_Coverage']
    
    print(tech_categories)
    
    # Print cost range analysis
    print(f"\n💰 COST ANALYSIS:")
    cost_stats = enhanced_macc_template['Cost_USD_per_tCO2'].describe()
    print(f"  • Cost range: ${cost_stats['min']:.0f} to ${cost_stats['max']:.0f} per tCO₂")
    print(f"  • Median cost: ${cost_stats['50%']:.0f} per tCO₂")
    print(f"  • Negative cost options: {(enhanced_macc_template['Cost_USD_per_tCO2'] < 0).sum()}")
    
    # Print abatement potential
    print(f"\n🎯 ABATEMENT POTENTIAL:")
    total_abatement = enhanced_macc_template['Abatement_Potential_MtCO2_per_year'].sum()
    print(f"  • Total technical potential: {total_abatement:.1f} Mt CO₂/year")
    print(f"  • Baseline emissions: {total_emissions_mt:.1f} Mt CO₂")
    print(f"  • Coverage: {total_abatement/total_emissions_mt:.1%}")
    
    return enhanced_macc_template, enhanced_tech_options, output_file

if __name__ == "__main__":
    macc_template, tech_options, output_file = create_enhanced_macc_database()
    print(f"\n✅ ENHANCED MACC DATABASE CREATION COMPLETE")
    print(f"📁 File: {output_file}")