#!/usr/bin/env python3
"""
Analyze petrochemical processes and technology applicability
"""

import pandas as pd

def analyze_petrochemical_processes():
    """Analyze petrochemical processes for technology applicability"""
    
    print("🔬 PETROCHEMICAL PROCESS ANALYSIS")
    print("="*60)
    
    # Load facility data to understand process types
    facility_data = pd.read_csv("outputs/facility_emissions_korea_scale_52mt_final.csv")
    
    # Analyze by process type
    process_analysis = facility_data.groupby(['process', 'product']).agg({
        'annual_emissions_kt_co2': 'sum',
        'capacity_kt': 'sum',
        'emission_intensity_t_co2_per_t': 'mean',
        'facility_id': 'count'
    }).reset_index()
    
    process_analysis.columns = ['Process', 'Product', 'Total_Emissions_kt', 'Total_Capacity_kt', 
                               'Avg_Intensity', 'Facility_Count']
    
    print("\n📊 PROCESS-PRODUCT BREAKDOWN:")
    print(process_analysis.round(2))
    
    # Analyze energy efficiency applicability
    print("\n⚡ ENERGY EFFICIENCY APPLICABILITY ANALYSIS:")
    print("="*60)
    
    # NCC (Naphtha Cracker) - high temperature, energy-intensive
    ncc_processes = process_analysis[process_analysis['Process'] == 'Naphtha Cracker']
    print(f"\n🔥 NAPHTHA CRACKER COMPLEXES:")
    print(f"  • Products: {', '.join(ncc_processes['Product'].tolist())}")
    print(f"  • Total Emissions: {ncc_processes['Total_Emissions_kt'].sum():.1f} kt CO₂")
    print(f"  • Avg Intensity: {ncc_processes['Avg_Intensity'].mean():.2f} t CO₂/t")
    print(f"  • Energy Efficiency Applicability: LIMITED")
    print(f"    - High-temperature processes (>800°C)")
    print(f"    - Fundamental thermodynamic constraints")
    print(f"    - Heat integration already optimized in modern plants")
    print(f"    - Max EE potential: 5-10% (vs 20-30% in other processes)")
    
    # BTX (Aromatics) - catalytic reforming, moderate EE potential
    btx_processes = process_analysis[process_analysis['Process'] == 'BTX Plant']
    print(f"\n🧪 BTX PLANTS:")
    print(f"  • Products: {', '.join(btx_processes['Product'].tolist())}")
    print(f"  • Total Emissions: {btx_processes['Total_Emissions_kt'].sum():.1f} kt CO₂")
    print(f"  • Avg Intensity: {btx_processes['Avg_Intensity'].mean():.2f} t CO₂/t")
    print(f"  • Energy Efficiency Applicability: MODERATE")
    print(f"    - Catalytic processes with heat recovery potential")
    print(f"    - Process optimization opportunities")
    print(f"    - Max EE potential: 15-25%")
    
    # Utilities - highest EE potential
    utility_processes = process_analysis[process_analysis['Process'] == 'Utility']
    print(f"\n⚙️  UTILITIES:")
    print(f"  • Products: {', '.join(utility_processes['Product'].tolist())}")
    print(f"  • Total Emissions: {utility_processes['Total_Emissions_kt'].sum():.1f} kt CO₂")
    print(f"  • Avg Intensity: {utility_processes['Avg_Intensity'].mean():.2f} t CO₂/t")
    print(f"  • Energy Efficiency Applicability: HIGH")
    print(f"    - Steam systems, power generation")
    print(f"    - Motor efficiency, VFDs")
    print(f"    - Heat recovery, cogeneration")
    print(f"    - Max EE potential: 20-40%")
    
    # Calculate appropriate EE potentials
    ee_potential_by_process = {
        'Naphtha Cracker': 0.10,  # 10% max due to thermodynamic constraints
        'BTX Plant': 0.20,        # 20% moderate potential
        'Utility': 0.35          # 35% high potential for utilities
    }
    
    print(f"\n📋 RECOMMENDED EE CONSTRAINTS:")
    print(f"="*60)
    
    total_weighted_potential = 0
    total_emissions = 0
    
    for process, max_ee in ee_potential_by_process.items():
        process_data = process_analysis[process_analysis['Process'] == process]
        process_emissions = process_data['Total_Emissions_kt'].sum()
        process_potential = process_emissions * max_ee
        
        total_weighted_potential += process_potential
        total_emissions += process_emissions
        
        print(f"  • {process}: {max_ee:.0%} max EE penetration")
        print(f"    - Emissions: {process_emissions:.1f} kt CO₂")
        print(f"    - EE Potential: {process_potential:.1f} kt CO₂")
    
    overall_ee_potential = total_weighted_potential / total_emissions
    print(f"\n  📊 OVERALL EE POTENTIAL: {overall_ee_potential:.1%}")
    print(f"  📊 CURRENT MODEL ASSUMES: 95% (UNREALISTIC)")
    print(f"  📊 RECOMMENDED LIMIT: {overall_ee_potential:.1%}")
    
    return process_analysis, ee_potential_by_process, overall_ee_potential

def identify_missing_technologies():
    """Identify missing renewable energy and advanced technologies"""
    
    print(f"\n🔋 MISSING RENEWABLE ENERGY TECHNOLOGIES:")
    print(f"="*60)
    
    missing_technologies = {
        'RE_001': {
            'name': 'Solar Thermal for Process Heat',
            'description': 'Solar collectors for low-medium temperature heating',
            'temperature_range': '80-250°C',
            'applicable_processes': ['Polymerization', 'Separation', 'Drying'],
            'cost_range': '50-150 USD/tCO₂',
            'trl': 8,
            'max_penetration': 0.25
        },
        'RE_002': {
            'name': 'Industrial Solar PV Systems',
            'description': 'On-site solar electricity generation',
            'applicable_processes': ['All (electricity demand)'],
            'cost_range': '30-80 USD/tCO₂',
            'trl': 9,
            'max_penetration': 0.40
        },
        'RE_003': {
            'name': 'Wind Power Purchase Agreements',
            'description': 'Long-term renewable electricity contracts',
            'applicable_processes': ['All (electricity demand)'],
            'cost_range': '20-60 USD/tCO₂',
            'trl': 9,
            'max_penetration': 0.60
        },
        'HP_002': {
            'name': 'High-Temperature Heat Pumps',
            'description': 'Heat pumps for temperatures up to 200°C',
            'temperature_range': '120-200°C',
            'applicable_processes': ['Distillation', 'Evaporation', 'Drying'],
            'cost_range': '100-250 USD/tCO₂',
            'trl': 7,
            'max_penetration': 0.30
        },
        'ES_001': {
            'name': 'Battery Energy Storage Systems',
            'description': 'Grid stabilization and renewable integration',
            'applicable_processes': ['All (load balancing)'],
            'cost_range': '80-200 USD/tCO₂',
            'trl': 8,
            'max_penetration': 0.20
        }
    }
    
    for tech_id, tech_info in missing_technologies.items():
        print(f"\n  {tech_id}: {tech_info['name']}")
        print(f"    - Description: {tech_info['description']}")
        print(f"    - Cost Range: {tech_info['cost_range']}")
        print(f"    - TRL: {tech_info['trl']}")
        print(f"    - Max Penetration: {tech_info['max_penetration']:.0%}")
        if 'temperature_range' in tech_info:
            print(f"    - Temperature Range: {tech_info['temperature_range']}")
        print(f"    - Applicable to: {', '.join(tech_info['applicable_processes'])}")
    
    return missing_technologies

if __name__ == "__main__":
    process_analysis, ee_constraints, overall_ee = analyze_petrochemical_processes()
    missing_techs = identify_missing_technologies()
    
    print(f"\n✅ ANALYSIS COMPLETE")
    print(f"📊 Process-specific EE constraints identified")
    print(f"🔋 {len(missing_techs)} additional renewable technologies recommended")