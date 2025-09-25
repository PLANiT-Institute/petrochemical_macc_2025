#!/usr/bin/env python3
"""
Upstream-Downstream Technology Connection Analysis
Focus: Clear visualization of interconnected technology pathways
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyBboxPatch
import seaborn as sns

def create_technology_network_graph():
    """Create detailed network graph of technology interconnections"""
    
    print("🔗 CREATING TECHNOLOGY NETWORK GRAPH")
    print("=" * 80)
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Define technology nodes with categories
    technologies = {
        # Energy Sources (Upstream)
        'Grid_Electricity': {'category': 'Energy_Source', 'level': 1, 'color': '#FFB6C1'},
        'Natural_Gas': {'category': 'Energy_Source', 'level': 1, 'color': '#FFB6C1'},
        'Renewable_Solar': {'category': 'Energy_Source', 'level': 1, 'color': '#90EE90'},
        'Renewable_Wind': {'category': 'Energy_Source', 'level': 1, 'color': '#90EE90'},
        
        # Energy Conversion (Mid-stream)
        'Green_Hydrogen': {'category': 'Energy_Conversion', 'level': 2, 'color': '#87CEEB'},
        'Heat_Pump': {'category': 'Energy_Conversion', 'level': 2, 'color': '#87CEEB'},
        'Electric_Heating': {'category': 'Energy_Conversion', 'level': 2, 'color': '#87CEEB'},
        'Energy_Storage': {'category': 'Energy_Conversion', 'level': 2, 'color': '#87CEEB'},
        
        # Process Technologies (Downstream)
        'NCC_Furnace': {'category': 'Process_NCC', 'level': 3, 'color': '#F0E68C'},
        'BTX_Heating': {'category': 'Process_BTX', 'level': 3, 'color': '#DDA0DD'},
        'Utility_Boiler': {'category': 'Process_Utility', 'level': 3, 'color': '#98FB98'},
        'Heat_Recovery': {'category': 'Process_Efficiency', 'level': 3, 'color': '#FFA07A'},
        
        # End Applications
        'Ethylene_Production': {'category': 'End_Product', 'level': 4, 'color': '#F5DEB3'},
        'BTX_Separation': {'category': 'End_Product', 'level': 4, 'color': '#F5DEB3'},
        'Steam_Generation': {'category': 'End_Product', 'level': 4, 'color': '#F5DEB3'}
    }
    
    # Add nodes to graph
    for tech, attrs in technologies.items():
        G.add_node(tech, **attrs)
    
    # Define connections (upstream -> downstream)
    connections = [
        # Energy sources to conversion
        ('Grid_Electricity', 'Green_Hydrogen', {'weight': 0.3, 'type': 'electrolysis'}),
        ('Renewable_Solar', 'Green_Hydrogen', {'weight': 0.8, 'type': 'electrolysis'}),
        ('Renewable_Wind', 'Green_Hydrogen', {'weight': 0.8, 'type': 'electrolysis'}),
        ('Grid_Electricity', 'Electric_Heating', {'weight': 0.9, 'type': 'direct'}),
        ('Renewable_Solar', 'Electric_Heating', {'weight': 0.9, 'type': 'direct'}),
        ('Grid_Electricity', 'Heat_Pump', {'weight': 0.8, 'type': 'direct'}),
        ('Renewable_Solar', 'Energy_Storage', {'weight': 0.7, 'type': 'storage'}),
        
        # Energy conversion to processes
        ('Green_Hydrogen', 'NCC_Furnace', {'weight': 0.8, 'type': 'fuel_replacement'}),
        ('Green_Hydrogen', 'Utility_Boiler', {'weight': 0.6, 'type': 'fuel_replacement'}),
        ('Electric_Heating', 'BTX_Heating', {'weight': 0.7, 'type': 'process_heat'}),
        ('Electric_Heating', 'Utility_Boiler', {'weight': 0.8, 'type': 'process_heat'}),
        ('Heat_Pump', 'BTX_Heating', {'weight': 0.5, 'type': 'low_temp_heat'}),
        ('Natural_Gas', 'NCC_Furnace', {'weight': 0.9, 'type': 'baseline_fuel'}),
        ('Natural_Gas', 'Utility_Boiler', {'weight': 0.9, 'type': 'baseline_fuel'}),
        
        # Process to end products
        ('NCC_Furnace', 'Ethylene_Production', {'weight': 0.9, 'type': 'cracking'}),
        ('BTX_Heating', 'BTX_Separation', {'weight': 0.8, 'type': 'separation'}),
        ('Utility_Boiler', 'Steam_Generation', {'weight': 0.9, 'type': 'steam'}),
        
        # Heat recovery connections
        ('NCC_Furnace', 'Heat_Recovery', {'weight': 0.6, 'type': 'waste_heat'}),
        ('BTX_Heating', 'Heat_Recovery', {'weight': 0.4, 'type': 'waste_heat'}),
        ('Heat_Recovery', 'Steam_Generation', {'weight': 0.7, 'type': 'recovered_heat'})
    ]
    
    # Add edges to graph
    G.add_edges_from([(u, v, attrs) for u, v, attrs in connections])
    
    return G, technologies, connections

def visualize_technology_network():
    """Create comprehensive visualization of technology network"""
    
    G, technologies, connections = create_technology_network_graph()
    
    print("📊 Creating network visualization...")
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 12))
    
    # Main network graph
    ax1 = plt.subplot(2, 2, (1, 2))
    
    # Position nodes by level (left to right flow)
    pos = {}
    level_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    level_spacing = {1: 1.5, 2: 1.2, 3: 1.0, 4: 1.5}
    
    for node, attrs in technologies.items():
        level = attrs['level']
        x = level * 3  # Horizontal spacing
        y = level_counts[level] * level_spacing[level] - (len([n for n, a in technologies.items() if a['level'] == level]) * level_spacing[level] / 2)
        pos[node] = (x, y)
        level_counts[level] += 1
    
    # Draw nodes
    for level in range(1, 5):
        level_nodes = [node for node, attrs in technologies.items() if attrs['level'] == level]
        node_colors = [technologies[node]['color'] for node in level_nodes]
        nx.draw_networkx_nodes(G, pos, nodelist=level_nodes, node_color=node_colors, 
                              node_size=2000, alpha=0.8, ax=ax1)
    
    # Draw edges with different styles for different connection types
    edge_styles = {
        'electrolysis': {'color': 'blue', 'style': '-', 'width': 2},
        'direct': {'color': 'green', 'style': '-', 'width': 2},
        'fuel_replacement': {'color': 'red', 'style': '--', 'width': 3},
        'process_heat': {'color': 'orange', 'style': '-', 'width': 2},
        'baseline_fuel': {'color': 'gray', 'style': ':', 'width': 1},
        'waste_heat': {'color': 'purple', 'style': '-.', 'width': 2}
    }
    
    for edge_type, style in edge_styles.items():
        edge_list = [(u, v) for u, v, attrs in G.edges(data=True) if attrs.get('type') == edge_type]
        if edge_list:
            nx.draw_networkx_edges(G, pos, edgelist=edge_list, 
                                 edge_color=style['color'], style=style['style'], 
                                 width=style['width'], alpha=0.7, ax=ax1)
    
    # Add labels
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax1)
    
    ax1.set_title('Technology Network: Upstream-Downstream Connections', fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    # Add level labels
    level_labels = ['Energy Sources', 'Energy Conversion', 'Process Technologies', 'End Products']
    for i, label in enumerate(level_labels):
        ax1.text((i+1)*3, -6, label, ha='center', fontsize=12, fontweight='bold')
    
    # Process-specific analysis
    ax2 = plt.subplot(2, 2, 3)
    
    # Technology compatibility matrix
    processes = ['NCC', 'BTX Plant', 'Utility']
    tech_types = ['Renewable\nEnergy', 'Hydrogen\nIntegration', 'Electrification', 'Heat\nRecovery', 'Energy\nEfficiency']
    
    # Compatibility scores (0-3: Not applicable, Low, Medium, High)
    compatibility = np.array([
        [1, 3, 2, 3, 1],  # NCC: Low RE, High H2, Med Elec, High Heat Recovery, Low EE
        [3, 2, 3, 2, 2],  # BTX: High RE, Med H2, High Elec, Med Heat Recovery, Med EE
        [3, 2, 3, 2, 3]   # Utility: High RE, Med H2, High Elec, Med Heat Recovery, High EE
    ])
    
    im = ax2.imshow(compatibility, cmap='RdYlGn', aspect='auto', vmin=0, vmax=3)
    ax2.set_xticks(range(len(tech_types)))
    ax2.set_xticklabels(tech_types, rotation=45, ha='right')
    ax2.set_yticks(range(len(processes)))
    ax2.set_yticklabels(processes)
    ax2.set_title('Technology Compatibility by Process')
    
    # Add compatibility scores
    for i in range(len(processes)):
        for j in range(len(tech_types)):
            score_labels = ['N/A', 'Low', 'Med', 'High']
            ax2.text(j, i, score_labels[compatibility[i,j]], 
                    ha='center', va='center', fontweight='bold')
    
    plt.colorbar(im, ax=ax2, label='Compatibility', ticks=[0,1,2,3], 
                format=plt.FuncFormatter(lambda x, p: ['N/A', 'Low', 'Med', 'High'][int(x)]))
    
    # Technology change impacts
    ax3 = plt.subplot(2, 2, 4)
    
    # Simulate technology adoption impacts
    years = np.arange(2025, 2051, 5)
    
    # NCC emission reduction pathway (conservative due to constraints)
    ncc_baseline = 100
    ncc_reduction = np.array([0, 5, 15, 30, 50, 65])  # Conservative hydrogen adoption
    
    # BTX emission reduction pathway (more aggressive)
    btx_baseline = 100
    btx_reduction = np.array([0, 10, 25, 45, 65, 80])  # Better electrification potential
    
    # Utility emission reduction pathway (most aggressive)
    utility_baseline = 100
    utility_reduction = np.array([0, 15, 35, 60, 80, 90])  # Full renewable potential
    
    ax3.plot(years, ncc_baseline - ncc_reduction, 'o-', color='red', linewidth=2, label='NCC (Conservative)')
    ax3.plot(years, btx_baseline - btx_reduction, 's-', color='blue', linewidth=2, label='BTX (Moderate)')
    ax3.plot(years, utility_baseline - utility_reduction, '^-', color='green', linewidth=2, label='Utility (Aggressive)')
    
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Relative Emissions (%)')
    ax3.set_title('Technology-Driven Emission Reduction Pathways')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 105)
    
    plt.tight_layout()
    plt.savefig('technology_network_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ Technology network visualization saved: technology_network_analysis.png")

def analyze_connection_impacts():
    """Analyze how technology connections change system behavior"""
    
    print("\n\n🔍 ANALYZING TECHNOLOGY CONNECTION IMPACTS")
    print("=" * 80)
    
    # Define impact scenarios
    scenarios = {
        'Isolated_Technologies': {
            'description': 'Technologies deployed independently',
            'renewable_effectiveness': 0.6,
            'hydrogen_cost_reduction': 0.0,
            'system_efficiency': 0.7,
            'implementation_risk': 0.8
        },
        'Synergistic_Deployment': {
            'description': 'Technologies deployed with interconnections',
            'renewable_effectiveness': 0.9,
            'hydrogen_cost_reduction': 0.3,
            'system_efficiency': 0.9,
            'implementation_risk': 0.4
        },
        'Optimized_Integration': {
            'description': 'Fully integrated technology system',
            'renewable_effectiveness': 0.95,
            'hydrogen_cost_reduction': 0.5,
            'system_efficiency': 0.95,
            'implementation_risk': 0.3
        }
    }
    
    print("📊 Impact Analysis by Deployment Scenario:")
    for scenario, data in scenarios.items():
        print(f"\n🎯 {scenario}:")
        print(f"   Description: {data['description']}")
        print(f"   Renewable Effectiveness: {data['renewable_effectiveness']:.0%}")
        print(f"   Hydrogen Cost Reduction: {data['hydrogen_cost_reduction']:.0%}")
        print(f"   System Efficiency: {data['system_efficiency']:.0%}")
        print(f"   Implementation Risk: {data['implementation_risk']:.0%}")
    
    # Calculate combined impact scores
    print(f"\n📈 Combined Impact Scores:")
    for scenario, data in scenarios.items():
        combined_score = (data['renewable_effectiveness'] * 0.3 + 
                         (1-data['implementation_risk']) * 0.3 + 
                         data['system_efficiency'] * 0.4)
        print(f"   {scenario}: {combined_score:.2f}")
    
    return scenarios

def main():
    """Main analysis function"""
    
    print("🔗 UPSTREAM-DOWNSTREAM TECHNOLOGY CONNECTION ANALYSIS")
    print("=" * 80)
    
    # Create network graph
    G, technologies, connections = create_technology_network_graph()
    
    print(f"📊 Network Statistics:")
    print(f"   Nodes: {G.number_of_nodes()}")
    print(f"   Edges: {G.number_of_edges()}")
    print(f"   Technology Categories: {len(set(attr['category'] for attr in technologies.values()))}")
    
    # Analyze network properties
    print(f"\n🔍 Network Analysis:")
    print(f"   Most connected node: {max(G.degree(), key=lambda x: x[1])}")
    print(f"   Average path length: {nx.average_shortest_path_length(G):.2f}")
    
    # Create visualizations
    visualize_technology_network()
    
    # Analyze connection impacts
    scenarios = analyze_connection_impacts()
    
    print(f"\n\n📋 KEY INSIGHTS:")
    print("=" * 50)
    print("✅ Technology interconnections significantly impact deployment effectiveness")
    print("✅ NCC processes require specialized high-temperature technology pathways")
    print("✅ Renewable energy enables hydrogen production for high-temp applications")
    print("✅ Heat recovery creates synergies across all process types")
    print("✅ Integrated deployment reduces costs and risks compared to isolated approaches")

if __name__ == "__main__":
    main()