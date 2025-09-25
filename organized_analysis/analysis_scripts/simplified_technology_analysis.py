#!/usr/bin/env python3
"""
Simplified Technology Analysis for Korean Petrochemical Industry
Focus: Realistic technology constraints, NCC facilities, reduced renewable overestimation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def create_realistic_technology_matrix():
    """Create simplified, realistic technology adoption matrix"""
    
    print("🎯 CREATING REALISTIC TECHNOLOGY MATRIX")
    print("=" * 80)
    
    # Simplified technology categories (removing overestimated waste technologies)
    technologies = {
        'Energy_Efficiency': {
            'description': 'Process optimization and efficiency improvements',
            'ncc_max': 0.10,  # Very limited for high-temp processes
            'btx_max': 0.20,  # Moderate for BTX plants
            'utility_max': 0.35,  # Higher for utility systems
            'cost_range': [50, 200],  # USD/tCO2
            'maturity': 'High'
        },
        'Hydrogen_Integration': {
            'description': 'Green hydrogen for high-temperature processes',
            'ncc_max': 0.80,  # High potential for NCC furnaces
            'btx_max': 0.30,  # Limited application in BTX
            'utility_max': 0.60,  # Good for utility boilers
            'cost_range': [200, 500],  # USD/tCO2
            'maturity': 'Medium'
        },
        'Electrification': {
            'description': 'Electric heating and process equipment',
            'ncc_max': 0.25,  # Limited by temperature requirements
            'btx_max': 0.50,  # Good for moderate temperatures
            'utility_max': 0.70,  # High for utilities
            'cost_range': [100, 300],  # USD/tCO2
            'maturity': 'High'
        },
        'Renewable_Energy': {
            'description': 'Solar/wind for electricity needs only',
            'ncc_max': 0.15,  # Only for electricity, not thermal
            'btx_max': 0.60,  # Good for electricity needs
            'utility_max': 0.80,  # High for power generation
            'cost_range': [80, 150],  # USD/tCO2
            'maturity': 'High'
        },
        'Heat_Recovery': {
            'description': 'Waste heat recovery systems',
            'ncc_max': 0.40,  # Good potential for high-temp processes
            'btx_max': 0.35,  # Moderate potential
            'utility_max': 0.30,  # Some potential
            'cost_range': [30, 120],  # USD/tCO2
            'maturity': 'High'
        }
    }
    
    # Create technology matrix DataFrame
    processes = ['NCC', 'BTX Plant', 'Utility']
    tech_names = list(technologies.keys())
    
    max_penetration = []
    cost_mid = []
    
    for tech in tech_names:
        tech_data = technologies[tech]
        max_penetration.append([
            tech_data['ncc_max'],
            tech_data['btx_max'], 
            tech_data['utility_max']
        ])
        cost_mid.append(np.mean(tech_data['cost_range']))
    
    # Create penetration matrix
    penetration_matrix = np.array(max_penetration)
    
    # Create DataFrame for analysis
    tech_df = pd.DataFrame({
        'Technology': tech_names,
        'NCC_Max': penetration_matrix[:, 0],
        'BTX_Max': penetration_matrix[:, 1],
        'Utility_Max': penetration_matrix[:, 2],
        'Cost_USD_tCO2': cost_mid,
        'Description': [technologies[tech]['description'] for tech in tech_names],
        'Maturity': [technologies[tech]['maturity'] for tech in tech_names]
    })
    
    print("📊 Simplified Technology Matrix:")
    print(tech_df.round(2))
    
    return tech_df, penetration_matrix, technologies

def analyze_ncc_focus():
    """Detailed analysis focusing on NCC facilities"""
    
    print("\n\n🏭 NCC FACILITY FOCUS ANALYSIS")
    print("=" * 80)
    
    # NCC-specific analysis based on high-temperature requirements
    ncc_analysis = {
        'Process_Temperature': '800-900°C',
        'Primary_Energy_Sources': ['Natural Gas', 'Fuel Gas', 'LPG'],
        'Current_Challenges': [
            'High temperature requirements limit technology options',
            'Energy-intensive cracking processes',
            'Limited electrification potential due to temperature',
            'Heavy reliance on fossil fuel feedstock'
        ],
        'Realistic_Technologies': {
            'Hydrogen_Integration': {
                'application': 'Furnace fuel replacement',
                'max_penetration': 0.80,
                'timeline': '2030-2040',
                'key_barriers': ['Cost', 'Infrastructure', 'Supply']
            },
            'Energy_Efficiency': {
                'application': 'Process optimization, heat integration',
                'max_penetration': 0.10,
                'timeline': '2025-2030',
                'key_barriers': ['Technical limits', 'Process constraints']
            },
            'Electrification': {
                'application': 'Auxiliary systems, utilities',
                'max_penetration': 0.25,
                'timeline': '2025-2035',
                'key_barriers': ['Temperature limits', 'Power requirements']
            },
            'Heat_Recovery': {
                'application': 'Waste heat utilization',
                'max_penetration': 0.40,
                'timeline': '2025-2030',
                'key_barriers': ['Integration complexity', 'Capital cost']
            }
        }
    }
    
    print("🌡️  Process Characteristics:")
    print(f"   Temperature: {ncc_analysis['Process_Temperature']}")
    print(f"   Primary Energy: {', '.join(ncc_analysis['Primary_Energy_Sources'])}")
    
    print("\n⚠️  Current Challenges:")
    for challenge in ncc_analysis['Current_Challenges']:
        print(f"   • {challenge}")
    
    print("\n🎯 Realistic Technology Options for NCC:")
    for tech, details in ncc_analysis['Realistic_Technologies'].items():
        print(f"\n   {tech}:")
        print(f"      Application: {details['application']}")
        print(f"      Max Penetration: {details['max_penetration']:.1%}")
        print(f"      Timeline: {details['timeline']}")
        print(f"      Barriers: {', '.join(details['key_barriers'])}")
    
    return ncc_analysis

def create_upstream_downstream_connections():
    """Create visualization of technology interconnections"""
    
    print("\n\n🔗 TECHNOLOGY INTERCONNECTION ANALYSIS")
    print("=" * 80)
    
    # Define technology connections (upstream -> downstream)
    connections = {
        'Renewable_Energy': {
            'enables': ['Electrification', 'Hydrogen_Integration'],
            'competes_with': [],
            'synergies': ['Energy_Storage', 'Grid_Integration']
        },
        'Hydrogen_Integration': {
            'enables': ['High_Temp_Process_Conversion'],
            'competes_with': ['Natural_Gas_Combustion'],
            'synergies': ['Renewable_Energy', 'Electrification']
        },
        'Electrification': {
            'enables': ['Process_Modernization'],
            'competes_with': ['Thermal_Processes'],
            'synergies': ['Renewable_Energy', 'Energy_Efficiency']
        },
        'Energy_Efficiency': {
            'enables': ['Reduced_Energy_Demand'],
            'competes_with': [],
            'synergies': ['All_Technologies']
        },
        'Heat_Recovery': {
            'enables': ['Process_Integration'],
            'competes_with': [],
            'synergies': ['Energy_Efficiency', 'Hydrogen_Integration']
        }
    }
    
    # Process-specific connection impacts
    process_impacts = {
        'NCC': {
            'primary_pathway': 'Renewable_Energy -> Hydrogen_Integration -> Process_Conversion',
            'secondary_pathway': 'Energy_Efficiency + Heat_Recovery -> Optimization',
            'limitations': 'Limited renewable thermal due to temperature requirements'
        },
        'BTX_Plant': {
            'primary_pathway': 'Renewable_Energy -> Electrification -> Process_Modernization',
            'secondary_pathway': 'Hydrogen_Integration -> Selected_Processes',
            'limitations': 'Moderate temperature processes allow more options'
        },
        'Utility': {
            'primary_pathway': 'Renewable_Energy -> Full_Electrification',
            'secondary_pathway': 'Hydrogen_Integration -> Backup_Systems',
            'limitations': 'Minimal technical constraints'
        }
    }
    
    print("🔗 Technology Interconnections:")
    for tech, conn in connections.items():
        print(f"\n   {tech}:")
        if conn['enables']:
            print(f"      Enables: {', '.join(conn['enables'])}")
        if conn['competes_with']:
            print(f"      Competes with: {', '.join(conn['competes_with'])}")
        if conn['synergies']:
            print(f"      Synergies: {', '.join(conn['synergies'])}")
    
    print(f"\n🏭 Process-Specific Impact Pathways:")
    for process, impact in process_impacts.items():
        print(f"\n   {process}:")
        print(f"      Primary: {impact['primary_pathway']}")
        print(f"      Secondary: {impact['secondary_pathway']}")
        print(f"      Limitations: {impact['limitations']}")
    
    return connections, process_impacts

def create_technology_connection_visualization():
    """Create visual representation of technology interconnections"""
    
    print("\n\n📊 CREATING TECHNOLOGY CONNECTION VISUALIZATION")
    print("=" * 80)
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Simplified Technology Analysis: Korean Petrochemical Industry', fontsize=16, fontweight='bold')
    
    # 1. Technology Penetration by Process
    tech_df, penetration_matrix, technologies = create_realistic_technology_matrix()
    
    im1 = ax1.imshow(penetration_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    ax1.set_xticks(range(3))
    ax1.set_xticklabels(['NCC', 'BTX Plant', 'Utility'])
    ax1.set_yticks(range(len(tech_df)))
    ax1.set_yticklabels(tech_df['Technology'])
    ax1.set_title('Maximum Technology Penetration by Process')
    
    # Add values to heatmap
    for i in range(len(tech_df)):
        for j in range(3):
            ax1.text(j, i, f'{penetration_matrix[i,j]:.0%}', 
                    ha='center', va='center', fontweight='bold')
    
    plt.colorbar(im1, ax=ax1, label='Max Penetration')
    
    # 2. Cost vs Penetration Analysis
    penetration_cols = ['NCC_Max', 'BTX_Max', 'Utility_Max']
    process_names = ['NCC', 'BTX Plant', 'Utility']
    for i, (col, process) in enumerate(zip(penetration_cols, process_names)):
        ax2.scatter(tech_df['Cost_USD_tCO2'], tech_df[col], 
                   s=100, alpha=0.7, label=process)
    
    ax2.set_xlabel('Cost (USD/tCO2)')
    ax2.set_ylabel('Maximum Penetration')
    ax2.set_title('Technology Cost vs Penetration Potential')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. NCC-Focused Analysis
    ncc_data = tech_df[['Technology', 'NCC_Max', 'Cost_USD_tCO2']].sort_values('NCC_Max', ascending=True)
    
    bars = ax3.barh(ncc_data['Technology'], ncc_data['NCC_Max'], 
                   color=['red' if x < 0.3 else 'orange' if x < 0.6 else 'green' 
                         for x in ncc_data['NCC_Max']])
    ax3.set_xlabel('Maximum Penetration for NCC')
    ax3.set_title('Technology Potential for NCC Facilities')
    ax3.set_xlim(0, 1)
    
    # Add percentage labels
    for i, (bar, val) in enumerate(zip(bars, ncc_data['NCC_Max'])):
        ax3.text(val + 0.01, i, f'{val:.0%}', va='center')
    
    # 4. Technology Timeline and Maturity
    timeline_data = {
        'Energy_Efficiency': {'start': 2025, 'peak': 2030, 'maturity': 'High'},
        'Renewable_Energy': {'start': 2025, 'peak': 2035, 'maturity': 'High'},
        'Heat_Recovery': {'start': 2025, 'peak': 2030, 'maturity': 'High'},
        'Electrification': {'start': 2025, 'peak': 2035, 'maturity': 'High'},
        'Hydrogen_Integration': {'start': 2030, 'peak': 2040, 'maturity': 'Medium'}
    }
    
    colors = {'High': 'green', 'Medium': 'orange', 'Low': 'red'}
    
    for i, (tech, data) in enumerate(timeline_data.items()):
        ax4.barh(i, data['peak'] - data['start'], left=data['start'], 
                color=colors[data['maturity']], alpha=0.7, label=data['maturity'])
        ax4.text(data['start'] + (data['peak'] - data['start'])/2, i, tech, 
                ha='center', va='center', fontsize=9, fontweight='bold')
    
    ax4.set_xlim(2020, 2050)
    ax4.set_xlabel('Year')
    ax4.set_title('Technology Deployment Timeline')
    ax4.set_yticks([])
    
    # Add legend for maturity levels
    handles = [plt.Rectangle((0,0),1,1, color=colors[level], alpha=0.7) 
              for level in ['High', 'Medium']]
    ax4.legend(handles, ['High Maturity', 'Medium Maturity'], loc='upper right')
    
    plt.tight_layout()
    plt.savefig('../outputs/simplified_technology_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ Visualization saved: simplified_technology_analysis.png")

def main():
    """Main analysis function"""
    
    print("🎯 SIMPLIFIED TECHNOLOGY ANALYSIS")
    print("=" * 80)
    print("Focus: Realistic constraints, NCC facilities, reduced overestimation")
    print("=" * 80)
    
    # Run analyses
    tech_df, penetration_matrix, technologies = create_realistic_technology_matrix()
    ncc_analysis = analyze_ncc_focus()
    connections, process_impacts = create_upstream_downstream_connections()
    create_technology_connection_visualization()
    
    # Summary findings
    print("\n\n📋 KEY FINDINGS:")
    print("=" * 50)
    print("✅ Technology overestimation addressed - removed unrealistic waste technologies")
    print("✅ NCC constraints properly modeled - limited to high-temp compatible technologies")
    print("✅ Renewable energy adoption limited to appropriate applications")
    print("✅ Technology interconnections identified for system optimization")
    print("✅ Realistic penetration limits based on process constraints")
    
    print("\n🎯 NEXT STEPS:")
    print("• Analyze naphtha emission factors and external GHG impacts")
    print("• Model bio-naphtha reduction as exogenous variable")
    print("• Create detailed upstream-downstream connection graphs")

if __name__ == "__main__":
    main()