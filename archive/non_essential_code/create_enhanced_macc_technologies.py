#!/usr/bin/env python3
"""
Create enhanced alternative technologies sheet for comprehensive MACC analysis
Based on existing alter sheet + comprehensive decarbonization knowledge
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def create_enhanced_technologies():
    """Create comprehensive alternative technologies database"""
    
    # Load existing data for reference
    facilities_df = pd.read_excel('data/petro_data_v1.0_final.xlsx', sheet_name='source')
    facilities_df['capacity_numeric'] = pd.to_numeric(facilities_df['capacity_1000_t'], errors='coerce').fillna(0)
    
    # Calculate production capacity by product
    production_capacity = facilities_df[facilities_df['capacity_numeric'] > 0].groupby('products')['capacity_numeric'].sum()
    
    print("Creating enhanced MACC technologies database...")
    
    # Enhanced alternative technologies based on industry knowledge
    technologies = [
        # ETHYLENE TECHNOLOGIES
        {
            'TechID': 'ETH_001',
            'Product': 'Ethylene',
            'Technology': 'Electric Steam Cracking',
            'Energy_carrier': 'Electricity',
            'Process_energy_GJ_per_t_product': 16.3,
            'Electricity_MWh_per_t_product': 4.5,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 2200,
            'OPEX_delta_USD_per_t': 50,
            'TRL': 7,  # Demo stage
            'Commercial_year': 2027,
            'Max_penetration': 0.8,
            'Ramp_rate_per_year': 0.05,
            'Abatement_tCO2_per_t': 1.8,  # vs baseline naphtha cracking
            'Source_note': 'Electric heating replaces fuel gas in cracker furnace'
        },
        {
            'TechID': 'ETH_002', 
            'Product': 'Ethylene',
            'Technology': 'Green H2 Steam Cracking',
            'Energy_carrier': 'Hydrogen',
            'Process_energy_GJ_per_t_product': 16.3,
            'Electricity_MWh_per_t_product': 0.5,
            'Hydrogen_kg_per_t_product': 300,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 2400,
            'OPEX_delta_USD_per_t': 80,
            'TRL': 6,  # Pilot
            'Commercial_year': 2030,
            'Max_penetration': 0.7,
            'Ramp_rate_per_year': 0.04,
            'Abatement_tCO2_per_t': 1.9,
            'Source_note': 'Hydrogen combustion replaces natural gas in furnaces'
        },
        {
            'TechID': 'ETH_003',
            'Product': 'Ethylene', 
            'Technology': 'Bio-ethylene (Ethanol dehydration)',
            'Energy_carrier': 'Biomass',
            'Process_energy_GJ_per_t_product': 8.0,
            'Electricity_MWh_per_t_product': 0.8,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 1250,
            'OPEX_delta_USD_per_t': 200,
            'TRL': 9,  # Commercial
            'Commercial_year': 2025,
            'Max_penetration': 0.15,  # Limited by biomass availability
            'Ramp_rate_per_year': 0.02,
            'Abatement_tCO2_per_t': 2.1,  # Near zero emissions
            'Source_note': 'Sustainable ethanol feedstock'
        },
        {
            'TechID': 'ETH_004',
            'Product': 'Ethylene',
            'Technology': 'Methanol-to-Olefins (MTO)',
            'Energy_carrier': 'Natural Gas',
            'Process_energy_GJ_per_t_product': 5.0,
            'Electricity_MWh_per_t_product': 1.4,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 28.0,
            'CAPEX_USD_per_tpa': 1000,
            'OPEX_delta_USD_per_t': -50,  # Lower operating costs
            'TRL': 9,  # Commercial
            'Commercial_year': 2025,
            'Max_penetration': 0.6,
            'Ramp_rate_per_year': 0.08,
            'Abatement_tCO2_per_t': 0.8,  # Moderate improvement
            'Source_note': 'Alternative route via methanol'
        },
        
        # PROPYLENE TECHNOLOGIES
        {
            'TechID': 'PROP_001',
            'Product': 'Propylene',
            'Technology': 'Electric Propane Dehydrogenation (ePDH)',
            'Energy_carrier': 'Electricity',
            'Process_energy_GJ_per_t_product': 2.5,
            'Electricity_MWh_per_t_product': 2.8,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 1800,
            'OPEX_delta_USD_per_t': 40,
            'TRL': 6,  # Pilot
            'Commercial_year': 2028,
            'Max_penetration': 0.7,
            'Ramp_rate_per_year': 0.05,
            'Abatement_tCO2_per_t': 1.5,
            'Source_note': 'Electric heating for endothermic PDH reaction'
        },
        {
            'TechID': 'PROP_002',
            'Product': 'Propylene',
            'Technology': 'Bio-propylene (Renewable propane)',
            'Energy_carrier': 'Biomass',
            'Process_energy_GJ_per_t_product': 3.0,
            'Electricity_MWh_per_t_product': 0.6,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 1900,
            'OPEX_delta_USD_per_t': 180,
            'TRL': 7,  # Demo
            'Commercial_year': 2029,
            'Max_penetration': 0.2,  # Limited feedstock
            'Ramp_rate_per_year': 0.03,
            'Abatement_tCO2_per_t': 1.8,
            'Source_note': 'Renewable propane feedstock'
        },
        
        # AROMATICS TECHNOLOGIES
        {
            'TechID': 'BTX_001',
            'Product': '벤젠',
            'Technology': 'Electric Reforming',
            'Energy_carrier': 'Electricity',
            'Process_energy_GJ_per_t_product': 3.2,
            'Electricity_MWh_per_t_product': 3.5,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 2500,
            'OPEX_delta_USD_per_t': 60,
            'TRL': 5,  # Lab scale
            'Commercial_year': 2032,
            'Max_penetration': 0.6,
            'Ramp_rate_per_year': 0.04,
            'Abatement_tCO2_per_t': 1.2,
            'Source_note': 'Electric heating for reforming reactions'
        },
        {
            'TechID': 'BTX_002',
            'Product': '벤젠',
            'Technology': 'Bio-aromatics (Lignin)',
            'Energy_carrier': 'Biomass',
            'Process_energy_GJ_per_t_product': 8.5,
            'Electricity_MWh_per_t_product': 1.2,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 3200,
            'OPEX_delta_USD_per_t': 250,
            'TRL': 4,  # Research
            'Commercial_year': 2035,
            'Max_penetration': 0.25,
            'Ramp_rate_per_year': 0.02,
            'Abatement_tCO2_per_t': 1.6,
            'Source_note': 'Lignin-to-aromatics conversion'
        },
        
        # POLYMER TECHNOLOGIES
        {
            'TechID': 'PE_001',
            'Product': 'HDPE',
            'Technology': 'Advanced Catalyst (Lower Temperature)',
            'Energy_carrier': 'Natural Gas',
            'Process_energy_GJ_per_t_product': 0.8,
            'Electricity_MWh_per_t_product': 0.25,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 600,
            'OPEX_delta_USD_per_t': 10,
            'TRL': 8,  # Near commercial
            'Commercial_year': 2026,
            'Max_penetration': 0.9,
            'Ramp_rate_per_year': 0.1,
            'Abatement_tCO2_per_t': 0.3,
            'Source_note': 'Lower temperature polymerization'
        },
        {
            'TechID': 'PE_002',
            'Product': 'LDPE',
            'Technology': 'Heat Integration & Recovery',
            'Energy_carrier': 'Natural Gas',
            'Process_energy_GJ_per_t_product': 1.0,
            'Electricity_MWh_per_t_product': 0.3,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 400,
            'OPEX_delta_USD_per_t': -5,
            'TRL': 9,  # Commercial
            'Commercial_year': 2025,
            'Max_penetration': 0.8,
            'Ramp_rate_per_year': 0.15,
            'Abatement_tCO2_per_t': 0.4,
            'Source_note': 'Heat recovery and process integration'
        },
        {
            'TechID': 'PP_001',
            'Product': 'PP',
            'Technology': 'Electric Heating Polymerization',
            'Energy_carrier': 'Electricity',
            'Process_energy_GJ_per_t_product': 0.5,
            'Electricity_MWh_per_t_product': 1.8,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 800,
            'OPEX_delta_USD_per_t': 25,
            'TRL': 6,  # Pilot
            'Commercial_year': 2029,
            'Max_penetration': 0.7,
            'Ramp_rate_per_year': 0.06,
            'Abatement_tCO2_per_t': 0.8,
            'Source_note': 'Electric heating replaces steam'
        },
        
        # SPECIALTY CHEMICALS
        {
            'TechID': 'PX_001',
            'Product': 'P-X',
            'Technology': 'Bio-based p-Xylene',
            'Energy_carrier': 'Biomass',
            'Process_energy_GJ_per_t_product': 5.0,
            'Electricity_MWh_per_t_product': 0.8,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 2800,
            'OPEX_delta_USD_per_t': 300,
            'TRL': 4,  # Research
            'Commercial_year': 2037,
            'Max_penetration': 0.3,
            'Ramp_rate_per_year': 0.02,
            'Abatement_tCO2_per_t': 1.4,
            'Source_note': 'Biosynthetic p-xylene pathway'
        },
        {
            'TechID': 'TPA_001',
            'Product': 'TPA',
            'Technology': 'Process Intensification',
            'Energy_carrier': 'Natural Gas',
            'Process_energy_GJ_per_t_product': 2.5,
            'Electricity_MWh_per_t_product': 0.15,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 500,
            'OPEX_delta_USD_per_t': 0,
            'TRL': 8,  # Near commercial
            'Commercial_year': 2027,
            'Max_penetration': 0.8,
            'Ramp_rate_per_year': 0.12,
            'Abatement_tCO2_per_t': 0.6,
            'Source_note': 'Intensified oxidation process'
        },
        
        # CROSS-CUTTING TECHNOLOGIES
        {
            'TechID': 'CCS_001',
            'Product': 'All_Products',
            'Technology': 'Carbon Capture & Storage',
            'Energy_carrier': 'Electricity',
            'Process_energy_GJ_per_t_product': 0.5,
            'Electricity_MWh_per_t_product': 0.4,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 200,  # Per tonne of product capacity
            'OPEX_delta_USD_per_t': 30,  # Per tonne of product
            'TRL': 7,  # Demo
            'Commercial_year': 2028,
            'Max_penetration': 0.9,
            'Ramp_rate_per_year': 0.08,
            'Abatement_tCO2_per_t': 0.85,  # 85% of process emissions
            'Source_note': 'Post-combustion CO2 capture'
        },
        {
            'TechID': 'H2_001',
            'Product': 'All_Products',
            'Technology': 'Green Hydrogen Boilers',
            'Energy_carrier': 'Hydrogen',
            'Process_energy_GJ_per_t_product': 0.0,
            'Electricity_MWh_per_t_product': 0.1,
            'Hydrogen_kg_per_t_product': 50,  # Per tonne product
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 150,
            'OPEX_delta_USD_per_t': 25,
            'TRL': 6,  # Pilot
            'Commercial_year': 2030,
            'Max_penetration': 0.8,
            'Ramp_rate_per_year': 0.06,
            'Abatement_tCO2_per_t': 0.4,  # Replaces NG boilers
            'Source_note': 'H2 combustion for process heating'
        },
        {
            'TechID': 'EE_001',
            'Product': 'All_Products',
            'Technology': 'Energy Efficiency Package',
            'Energy_carrier': 'Mixed',
            'Process_energy_GJ_per_t_product': -1.0,  # Energy savings
            'Electricity_MWh_per_t_product': -0.2,
            'Hydrogen_kg_per_t_product': 0,
            'Feedstock_energy_GJ_per_t': 0,
            'CAPEX_USD_per_tpa': 300,
            'OPEX_delta_USD_per_t': -10,  # Cost savings
            'TRL': 9,  # Commercial
            'Commercial_year': 2025,
            'Max_penetration': 0.95,
            'Ramp_rate_per_year': 0.2,
            'Abatement_tCO2_per_t': 0.3,
            'Source_note': 'Heat integration, motor efficiency, controls'
        }
    ]
    
    return pd.DataFrame(technologies)

def calculate_macc_metrics(tech_df, baseline_emissions, production_capacity):
    """Calculate MACC metrics for each technology"""
    
    print("Calculating MACC metrics...")
    
    # Energy prices (2025 estimates, USD)
    energy_prices = {
        'electricity': 0.12,  # USD/kWh (Korean industrial)
        'natural_gas': 15.0,  # USD/GJ
        'hydrogen': 3.0,      # USD/kg (green H2 target)
        'biomass': 8.0        # USD/GJ
    }
    
    # Calculate costs and abatement for each technology
    macc_results = []
    
    for _, tech in tech_df.iterrows():
        # Get baseline emissions for this product
        product = tech['Product']
        if product == 'All_Products':
            # Cross-cutting technology - use weighted average
            baseline_ei = 0.7  # tCO2/t average
            total_capacity = production_capacity.sum()
            applicable_capacity = total_capacity
        else:
            # Product-specific technology
            baseline_ei = baseline_emissions.get(product, 1.0)  # tCO2/t
            applicable_capacity = production_capacity.get(product, 0)
        
        if applicable_capacity == 0:
            continue
            
        # Calculate annual energy costs
        electricity_cost = (tech['Electricity_MWh_per_t_product'] or 0) * 1000 * energy_prices['electricity']  # USD/t
        gas_cost = (tech['Process_energy_GJ_per_t_product'] or 0) * energy_prices['natural_gas']  # USD/t
        hydrogen_cost = (tech['Hydrogen_kg_per_t_product'] or 0) * energy_prices['hydrogen']  # USD/t
        
        # Total annual cost per tonne product
        annual_energy_cost = electricity_cost + gas_cost + hydrogen_cost
        annual_opex = tech['OPEX_delta_USD_per_t']
        
        # Annualized CAPEX (assuming 20-year lifetime, 7% discount rate)
        capex_factor = 0.094  # Annuity factor
        annual_capex = tech['CAPEX_USD_per_tpa'] * capex_factor
        
        # Total annual cost per tonne
        total_annual_cost = annual_capex + annual_opex + annual_energy_cost
        
        # Abatement potential
        abatement_per_tonne = tech['Abatement_tCO2_per_t']
        max_penetration = tech['Max_penetration']
        
        # Total abatement potential (ktCO2/year)
        total_abatement_potential = applicable_capacity * max_penetration * abatement_per_tonne
        
        # Abatement cost (USD/tCO2)
        if abatement_per_tonne > 0:
            abatement_cost = total_annual_cost / abatement_per_tonne
        else:
            abatement_cost = 0
        
        macc_results.append({
            'TechID': tech['TechID'],
            'Product': product,
            'Technology': tech['Technology'],
            'TRL': tech['TRL'],
            'Commercial_year': tech['Commercial_year'],
            'Abatement_cost_USD_per_tCO2': abatement_cost,
            'Abatement_potential_ktCO2_per_year': total_abatement_potential,
            'Max_penetration': max_penetration,
            'Applicable_capacity_kt': applicable_capacity,
            'Annual_cost_USD_per_t': total_annual_cost,
            'CAPEX_USD_per_tpa': tech['CAPEX_USD_per_tpa'],
            'Ready_for_deployment': tech['TRL'] >= 7 and tech['Commercial_year'] <= 2030
        })
    
    return pd.DataFrame(macc_results)

def create_macc_curve(macc_df, output_dir="outputs"):
    """Create MACC curve visualization"""
    
    print("Creating MACC curve...")
    
    # Filter to deployable technologies (TRL >= 6, commercial by 2035)
    deployable = macc_df[
        (macc_df['TRL'] >= 6) & 
        (macc_df['Commercial_year'] <= 2035) &
        (macc_df['Abatement_potential_ktCO2_per_year'] > 0)
    ].copy()
    
    # Sort by abatement cost
    deployable = deployable.sort_values('Abatement_cost_USD_per_tCO2')
    
    # Calculate cumulative abatement
    deployable['Cumulative_abatement_MtCO2'] = deployable['Abatement_potential_ktCO2_per_year'].cumsum() / 1000
    
    # Create MACC curve
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot bars
    cumulative = 0
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(deployable)))
    
    for i, (_, row) in enumerate(deployable.iterrows()):
        width = row['Abatement_potential_ktCO2_per_year'] / 1000  # MtCO2/year
        height = row['Abatement_cost_USD_per_tCO2']
        
        # Color based on cost
        if height < 0:
            color = 'green'
        elif height < 50:
            color = 'lightgreen'
        elif height < 100:
            color = 'yellow'
        elif height < 200:
            color = 'orange'
        else:
            color = 'red'
        
        ax.bar(cumulative + width/2, height, width=width, 
               color=color, alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # Add technology labels for significant options
        if width > 1 or height < 50:  # Large potential or low cost
            ax.text(cumulative + width/2, height + 5, 
                   row['TechID'], rotation=45, ha='center', va='bottom', fontsize=8)
        
        cumulative += width
    
    # Formatting
    ax.set_xlabel('Cumulative Abatement Potential (Mt CO₂/year)', fontsize=12)
    ax.set_ylabel('Abatement Cost (USD/t CO₂)', fontsize=12)
    ax.set_title('Korean Petrochemical Industry - MACC Curve\n(Technologies Available by 2035)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    # Add cost ranges legend
    legend_elements = [
        plt.Rectangle((0,0),1,1, facecolor='green', alpha=0.7, label='Negative cost (profitable)'),
        plt.Rectangle((0,0),1,1, facecolor='lightgreen', alpha=0.7, label='Low cost (<$50/tCO₂)'),
        plt.Rectangle((0,0),1,1, facecolor='yellow', alpha=0.7, label='Medium cost ($50-100/tCO₂)'),
        plt.Rectangle((0,0),1,1, facecolor='orange', alpha=0.7, label='High cost ($100-200/tCO₂)'),
        plt.Rectangle((0,0),1,1, facecolor='red', alpha=0.7, label='Very high cost (>$200/tCO₂)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    # Add summary statistics
    total_potential = deployable['Abatement_potential_ktCO2_per_year'].sum() / 1000
    negative_cost = deployable[deployable['Abatement_cost_USD_per_tCO2'] < 0]['Abatement_potential_ktCO2_per_year'].sum() / 1000
    low_cost = deployable[deployable['Abatement_cost_USD_per_tCO2'] < 50]['Abatement_potential_ktCO2_per_year'].sum() / 1000
    
    textstr = f'Total Potential: {total_potential:.1f} Mt CO₂/year\\nProfitable: {negative_cost:.1f} Mt CO₂/year\\nLow Cost (<$50): {low_cost:.1f} Mt CO₂/year'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/korean_petrochemical_macc_curve.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"MACC curve saved to {output_dir}/korean_petrochemical_macc_curve.png")
    
    return deployable

def save_enhanced_alter_sheet():
    """Save enhanced alternative technologies to Excel"""
    
    # Load production capacity data
    facilities_df = pd.read_excel('data/petro_data_v1.0_final.xlsx', sheet_name='source')
    facilities_df['capacity_numeric'] = pd.to_numeric(facilities_df['capacity_1000_t'], errors='coerce').fillna(0)
    production_capacity = facilities_df[facilities_df['capacity_numeric'] > 0].groupby('products')['capacity_numeric'].sum()
    
    # Estimate baseline emission intensities from our final data
    emissions_df = pd.read_csv('outputs/facility_emissions_final.csv')
    baseline_emissions = emissions_df.groupby('product').apply(
        lambda x: (x['annual_emissions_kt_co2'].sum() * 1000) / (x['capacity_kt'].sum() * 1000)
    ).to_dict()
    
    # Create enhanced technologies
    tech_df = create_enhanced_technologies()
    
    # Calculate MACC metrics
    macc_df = calculate_macc_metrics(tech_df, baseline_emissions, production_capacity)
    
    # Load original Excel file and add enhanced sheets
    original_file = "data/petro_data_v1.0_final.xlsx"
    
    with pd.ExcelFile(original_file) as xls:
        all_sheets = {}
        for sheet_name in xls.sheet_names:
            if sheet_name not in ['alter']:
                all_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Add enhanced alternative technologies
    all_sheets['alter'] = tech_df
    all_sheets['macc_analysis'] = macc_df
    
    # Save enhanced file
    output_file = "data/petro_data_v1.0_enhanced.xlsx"
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"Enhanced technologies saved to {output_file}")
    
    # Create MACC curve
    Path("outputs").mkdir(exist_ok=True)
    deployable_tech = create_macc_curve(macc_df)
    
    # Save MACC results
    macc_df.to_csv("outputs/macc_analysis.csv", index=False)
    deployable_tech.to_csv("outputs/macc_deployable_technologies.csv", index=False)
    
    # Print summary
    print(f"\n=== MACC ANALYSIS SUMMARY ===")
    print(f"Total technologies: {len(tech_df)}")
    print(f"Deployable by 2035: {len(deployable_tech)}")
    print(f"Total abatement potential: {deployable_tech['Abatement_potential_ktCO2_per_year'].sum()/1000:.1f} Mt CO₂/year")
    print(f"Average abatement cost: ${deployable_tech['Abatement_cost_USD_per_tCO2'].mean():.0f}/t CO₂")
    
    return output_file

if __name__ == "__main__":
    save_enhanced_alter_sheet()