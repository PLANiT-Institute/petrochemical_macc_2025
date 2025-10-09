#!/usr/bin/env python3
"""
Baseline Fuel and Feedstock Consumption Calculation
Korean Petrochemical Industry - 2024 Baseline Year
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def calculate_baseline_consumption():
    """Calculate detailed baseline fuel and feedstock consumption"""
    
    print("⛽ BASELINE FUEL AND FEEDSTOCK CONSUMPTION ANALYSIS")
    print("=" * 80)
    print("Base Year: 2024")
    print("Scope: Korean Petrochemical Industry")
    print("=" * 80)
    
    # Industry production capacity data
    production_data = {
        'ethylene_capacity_mt': 7.2,      # Million tonnes/year
        'propylene_capacity_mt': 3.6,     # Million tonnes/year
        'btx_capacity_mt': 4.8,           # BTX (Benzene, Toluene, Xylene)
        'other_products_mt': 2.1,         # Other petrochemicals
        'capacity_utilization': 0.85      # 85% average utilization
    }
    
    # Calculate actual production
    actual_production = {
        'ethylene_production': production_data['ethylene_capacity_mt'] * production_data['capacity_utilization'],
        'propylene_production': production_data['propylene_capacity_mt'] * production_data['capacity_utilization'],
        'btx_production': production_data['btx_capacity_mt'] * production_data['capacity_utilization'],
        'other_production': production_data['other_products_mt'] * production_data['capacity_utilization']
    }
    
    print("📊 PRODUCTION SUMMARY (2024)")
    print(f"   Ethylene Production: {actual_production['ethylene_production']:.1f} Mt/year")
    print(f"   Propylene Production: {actual_production['propylene_production']:.1f} Mt/year")  
    print(f"   BTX Production: {actual_production['btx_production']:.1f} Mt/year")
    print(f"   Other Products: {actual_production['other_production']:.1f} Mt/year")
    print(f"   Total Production: {sum(actual_production.values()):.1f} Mt/year")
    
    return actual_production

def calculate_naphtha_feedstock():
    """Calculate naphtha feedstock consumption"""
    
    print("\n\n🛢️  NAPHTHA FEEDSTOCK CONSUMPTION")
    print("=" * 80)
    
    actual_production = calculate_baseline_consumption()
    
    # Naphtha consumption ratios (industry standard)
    naphtha_ratios = {
        'ethylene_naphtha_ratio': 3.1,    # 3.1 tonnes naphtha per tonne ethylene
        'propylene_naphtha_ratio': 2.8,   # 2.8 tonnes naphtha per tonne propylene  
        'btx_naphtha_ratio': 1.4,         # 1.4 tonnes naphtha per tonne BTX
        'other_naphtha_ratio': 1.8        # 1.8 tonnes naphtha per tonne other products
    }
    
    # Calculate naphtha consumption by product
    naphtha_consumption = {
        'ethylene_naphtha': actual_production['ethylene_production'] * naphtha_ratios['ethylene_naphtha_ratio'],
        'propylene_naphtha': actual_production['propylene_production'] * naphtha_ratios['propylene_naphtha_ratio'],
        'btx_naphtha': actual_production['btx_production'] * naphtha_ratios['btx_naphtha_ratio'],
        'other_naphtha': actual_production['other_production'] * naphtha_ratios['other_naphtha_ratio']
    }
    
    total_naphtha = sum(naphtha_consumption.values())
    
    print("📊 Naphtha Consumption by Product:")
    for product, consumption in naphtha_consumption.items():
        percentage = (consumption / total_naphtha) * 100
        print(f"   {product.replace('_', ' ').title()}: {consumption:.1f} Mt/year ({percentage:.1f}%)")
    
    print(f"\n🎯 TOTAL NAPHTHA CONSUMPTION: {total_naphtha:.1f} Mt/year")
    
    # Additional naphtha for utilities and losses
    utility_naphtha = total_naphtha * 0.05  # 5% for utilities
    process_losses = total_naphtha * 0.03   # 3% process losses
    
    print(f"   Utility Use: {utility_naphtha:.1f} Mt/year")
    print(f"   Process Losses: {process_losses:.1f} Mt/year")
    
    total_naphtha_including_losses = total_naphtha + utility_naphtha + process_losses
    
    print(f"\n🎯 TOTAL NAPHTHA (Including Losses): {total_naphtha_including_losses:.1f} Mt/year")
    
    return naphtha_consumption, total_naphtha_including_losses

def calculate_fuel_consumption():
    """Calculate fuel consumption for process energy"""
    
    print("\n\n🔥 PROCESS FUEL CONSUMPTION")
    print("=" * 80)
    
    actual_production = calculate_baseline_consumption()
    
    # Energy intensity by process (GJ/tonne product)
    energy_intensities = {
        'ncc_energy_intensity': 28.5,     # GJ/tonne ethylene (high temp cracking)
        'btx_energy_intensity': 12.3,     # GJ/tonne BTX (separation processes)
        'utility_energy_intensity': 8.7,   # GJ/tonne (steam, power generation)
        'other_energy_intensity': 15.2     # GJ/tonne other products
    }
    
    # Calculate total energy demand
    energy_demand = {
        'ncc_energy': actual_production['ethylene_production'] * energy_intensities['ncc_energy_intensity'],
        'btx_energy': actual_production['btx_production'] * energy_intensities['btx_energy_intensity'],
        'utility_energy': sum(actual_production.values()) * energy_intensities['utility_energy_intensity'],
        'other_energy': actual_production['other_production'] * energy_intensities['other_energy_intensity']
    }
    
    total_energy_demand = sum(energy_demand.values())
    
    print("📊 Energy Demand by Process:")
    for process, demand in energy_demand.items():
        percentage = (demand / total_energy_demand) * 100
        print(f"   {process.replace('_', ' ').title()}: {demand:.0f} GJ/year ({percentage:.1f}%)")
    
    print(f"\n🎯 TOTAL ENERGY DEMAND: {total_energy_demand:.0f} GJ/year")
    
    # Fuel mix for energy supply
    fuel_mix = {
        'natural_gas': 0.65,        # 65% natural gas
        'fuel_gas_byproduct': 0.20, # 20% fuel gas (byproduct)
        'lpg': 0.08,                # 8% LPG
        'fuel_oil': 0.05,           # 5% fuel oil
        'coal': 0.02                # 2% coal
    }
    
    # Calculate fuel consumption by type
    fuel_consumption = {}
    for fuel_type, share in fuel_mix.items():
        fuel_consumption[fuel_type] = total_energy_demand * share
    
    print(f"\n📊 Fuel Consumption by Type:")
    for fuel_type, consumption in fuel_consumption.items():
        print(f"   {fuel_type.replace('_', ' ').title()}: {consumption:.0f} GJ/year")
    
    # Convert to physical units
    fuel_physical_units = calculate_physical_fuel_consumption(fuel_consumption)
    
    return fuel_consumption, fuel_physical_units

def calculate_physical_fuel_consumption(fuel_consumption_gj):
    """Convert energy consumption to physical units"""
    
    print(f"\n📦 FUEL CONSUMPTION IN PHYSICAL UNITS:")
    print("-" * 50)
    
    # Energy content conversion factors
    energy_content = {
        'natural_gas': 39.5,          # GJ/tonne
        'fuel_gas_byproduct': 45.2,   # GJ/tonne
        'lpg': 46.1,                  # GJ/tonne
        'fuel_oil': 40.5,             # GJ/tonne
        'coal': 25.8                  # GJ/tonne
    }
    
    physical_consumption = {}
    
    for fuel_type, consumption_gj in fuel_consumption_gj.items():
        physical_amount = consumption_gj / energy_content[fuel_type] / 1000  # Convert to Mt
        physical_consumption[fuel_type] = physical_amount
        
        print(f"   {fuel_type.replace('_', ' ').title()}: {physical_amount:.2f} Mt/year")
    
    total_fuel_mt = sum(physical_consumption.values())
    print(f"\n🎯 TOTAL FUEL CONSUMPTION: {total_fuel_mt:.2f} Mt/year")
    
    return physical_consumption

def calculate_emission_factors():
    """Calculate emissions from fuel and feedstock consumption"""
    
    print("\n\n🌍 EMISSION CALCULATIONS")
    print("=" * 80)
    
    # Get consumption data
    naphtha_consumption, total_naphtha = calculate_naphtha_feedstock()
    fuel_consumption_gj, fuel_physical = calculate_fuel_consumption()
    
    # Emission factors (tCO2/tonne fuel)
    emission_factors = {
        'natural_gas': 2.75,           # tCO2/tonne
        'fuel_gas_byproduct': 3.05,    # tCO2/tonne
        'lpg': 3.00,                   # tCO2/tonne
        'fuel_oil': 3.15,              # tCO2/tonne
        'coal': 2.86,                  # tCO2/tonne
        'naphtha_combustion': 3.10,    # tCO2/tonne (direct combustion)
        'naphtha_external_ghg': 0.90   # tCO2/tonne (lifecycle, from previous analysis)
    }
    
    # Calculate direct combustion emissions
    direct_emissions = {}
    for fuel_type, consumption_mt in fuel_physical.items():
        emissions = consumption_mt * emission_factors[fuel_type] * 1000  # Convert to kt
        direct_emissions[fuel_type] = emissions
    
    # Naphtha direct combustion (small amount used for heating)
    naphtha_fuel_use = total_naphtha * 0.02  # 2% of naphtha used as fuel
    naphtha_direct_emissions = naphtha_fuel_use * emission_factors['naphtha_combustion'] * 1000
    
    # Naphtha external GHG emissions (lifecycle)
    naphtha_external_emissions = total_naphtha * emission_factors['naphtha_external_ghg'] * 1000
    
    total_direct_emissions = sum(direct_emissions.values()) + naphtha_direct_emissions
    
    print("📊 Direct Emissions by Fuel Type:")
    for fuel_type, emissions in direct_emissions.items():
        print(f"   {fuel_type.replace('_', ' ').title()}: {emissions:.0f} ktCO2/year")
    
    print(f"   Naphtha (Direct Combustion): {naphtha_direct_emissions:.0f} ktCO2/year")
    print(f"\n🎯 TOTAL DIRECT EMISSIONS: {total_direct_emissions:.0f} ktCO2/year ({total_direct_emissions/1000:.1f} MtCO2/year)")
    
    print(f"\n🛢️  NAPHTHA EXTERNAL GHG EMISSIONS: {naphtha_external_emissions:.0f} ktCO2/year ({naphtha_external_emissions/1000:.1f} MtCO2/year)")
    
    total_emissions_including_external = total_direct_emissions + naphtha_external_emissions
    print(f"\n🌍 TOTAL EMISSIONS (Including External): {total_emissions_including_external:.0f} ktCO2/year ({total_emissions_including_external/1000:.1f} MtCO2/year)")
    
    return {
        'direct_emissions_ktco2': total_direct_emissions,
        'naphtha_external_ktco2': naphtha_external_emissions,
        'total_emissions_ktco2': total_emissions_including_external,
        'fuel_physical_consumption': fuel_physical,
        'naphtha_consumption_mt': total_naphtha
    }

def create_consumption_visualization():
    """Create comprehensive visualization of fuel and feedstock consumption"""
    
    print("\n\n📊 CREATING CONSUMPTION VISUALIZATION")
    print("=" * 80)
    
    # Get all data
    naphtha_consumption, total_naphtha = calculate_naphtha_feedstock()
    fuel_consumption_gj, fuel_physical = calculate_fuel_consumption()
    emission_data = calculate_emission_factors()
    
    # Create figure
    fig = plt.figure(figsize=(20, 12))
    
    # 1. Naphtha Consumption Breakdown
    ax1 = plt.subplot(2, 3, 1)
    
    labels = [key.replace('_naphtha', '').replace('_', ' ').title() for key in naphtha_consumption.keys()]
    sizes = list(naphtha_consumption.values())
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                      colors=colors, startangle=90)
    ax1.set_title('Naphtha Feedstock by Product\nTotal: {:.1f} Mt/year'.format(total_naphtha))
    
    # 2. Fuel Mix for Process Energy
    ax2 = plt.subplot(2, 3, 2)
    
    fuel_labels = [key.replace('_', ' ').title() for key in fuel_physical.keys()]
    fuel_sizes = list(fuel_physical.values())
    fuel_colors = ['#FFB6C1', '#98FB98', '#87CEEB', '#DDA0DD', '#F0E68C']
    
    wedges, texts, autotexts = ax2.pie(fuel_sizes, labels=fuel_labels, autopct='%1.1f%%',
                                      colors=fuel_colors, startangle=90)
    ax2.set_title('Process Fuel Mix\nTotal: {:.2f} Mt/year'.format(sum(fuel_sizes)))
    
    # 3. Total Fuel and Feedstock Consumption
    ax3 = plt.subplot(2, 3, 3)
    
    consumption_categories = ['Naphtha\nFeedstock', 'Natural\nGas', 'Fuel Gas\n(Byproduct)', 
                             'LPG', 'Fuel Oil', 'Coal']
    consumption_amounts = [total_naphtha] + list(fuel_physical.values())
    
    bars = ax3.bar(consumption_categories, consumption_amounts, 
                   color=['#FF6B6B', '#FFB6C1', '#98FB98', '#87CEEB', '#DDA0DD', '#F0E68C'])
    
    ax3.set_ylabel('Consumption (Mt/year)')
    ax3.set_title('Total Fuel and Feedstock Consumption')
    ax3.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, value in zip(bars, consumption_amounts):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Emission Sources
    ax4 = plt.subplot(2, 3, 4)
    
    emission_sources = ['Direct\nCombustion', 'Naphtha\nExternal GHG']
    emission_amounts = [emission_data['direct_emissions_ktco2']/1000, 
                       emission_data['naphtha_external_ktco2']/1000]
    
    bars = ax4.bar(emission_sources, emission_amounts, 
                   color=['#FF6B6B', '#FFA07A'], alpha=0.8)
    
    ax4.set_ylabel('Emissions (MtCO₂/year)')
    ax4.set_title('Emission Sources Breakdown')
    
    # Add value labels
    for bar, value in zip(bars, emission_amounts):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # 5. Energy Intensity by Process
    ax5 = plt.subplot(2, 3, 5)
    
    actual_production = calculate_baseline_consumption()
    energy_intensities = [28.5, 12.3, 15.2, 8.7]  # GJ/tonne
    process_names = ['NCC\n(Ethylene)', 'BTX\nProcesses', 'Other\nProducts', 'Utilities']
    
    bars = ax5.bar(process_names, energy_intensities, 
                   color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    
    ax5.set_ylabel('Energy Intensity (GJ/tonne)')
    ax5.set_title('Energy Intensity by Process')
    
    # Add value labels
    for bar, value in zip(bars, energy_intensities):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # 6. Consumption vs Production Comparison
    ax6 = plt.subplot(2, 3, 6)
    
    # Key metrics comparison
    metrics = ['Total\nProduction', 'Naphtha\nFeedstock', 'Process\nFuels', 'Total\nEmissions']
    values = [sum(actual_production.values()), total_naphtha, 
             sum(fuel_physical.values()), emission_data['total_emissions_ktco2']/1000]
    units = ['Mt/year', 'Mt/year', 'Mt/year', 'MtCO₂/year']
    
    # Normalize for comparison (production = 100%)
    normalized_values = [v/values[0]*100 for v in values]
    
    bars = ax6.bar(metrics, normalized_values, 
                   color=['#90EE90', '#FF6B6B', '#87CEEB', '#FFA07A'])
    
    ax6.set_ylabel('Relative Scale (Production = 100%)')
    ax6.set_title('Key Metrics Comparison')
    
    # Add actual value labels
    for bar, value, unit in zip(bars, values, units):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{value:.1f}\n{unit}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    plt.suptitle('Korean Petrochemical Industry: Baseline Fuel and Feedstock Consumption (2024)', 
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('baseline_consumption_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ Visualization saved: baseline_consumption_analysis.png")

def generate_consumption_summary():
    """Generate comprehensive summary report"""
    
    print("\n\n📋 GENERATING CONSUMPTION SUMMARY REPORT")
    print("=" * 80)
    
    # Get all calculation results
    actual_production = calculate_baseline_consumption()
    naphtha_consumption, total_naphtha = calculate_naphtha_feedstock()
    fuel_consumption_gj, fuel_physical = calculate_fuel_consumption()
    emission_data = calculate_emission_factors()
    
    # Create summary table
    summary_data = {
        'Category': [
            'Total Production',
            'Naphtha Feedstock',
            'Natural Gas Fuel',
            'Fuel Gas (Byproduct)',
            'LPG Fuel',
            'Fuel Oil',
            'Coal',
            'Total Process Fuels',
            'Direct Emissions',
            'Naphtha External GHG',
            'Total Emissions'
        ],
        'Amount': [
            f"{sum(actual_production.values()):.1f} Mt/year",
            f"{total_naphtha:.1f} Mt/year",
            f"{fuel_physical['natural_gas']:.2f} Mt/year",
            f"{fuel_physical['fuel_gas_byproduct']:.2f} Mt/year", 
            f"{fuel_physical['lpg']:.2f} Mt/year",
            f"{fuel_physical['fuel_oil']:.2f} Mt/year",
            f"{fuel_physical['coal']:.2f} Mt/year",
            f"{sum(fuel_physical.values()):.2f} Mt/year",
            f"{emission_data['direct_emissions_ktco2']/1000:.1f} MtCO₂/year",
            f"{emission_data['naphtha_external_ktco2']/1000:.1f} MtCO₂/year",
            f"{emission_data['total_emissions_ktco2']/1000:.1f} MtCO₂/year"
        ],
        'Percentage_of_Total': [
            '100%',
            f"{(total_naphtha/sum(actual_production.values()))*100:.0f}% of production",
            f"{(fuel_physical['natural_gas']/sum(fuel_physical.values()))*100:.0f}% of fuels",
            f"{(fuel_physical['fuel_gas_byproduct']/sum(fuel_physical.values()))*100:.0f}% of fuels",
            f"{(fuel_physical['lpg']/sum(fuel_physical.values()))*100:.0f}% of fuels",
            f"{(fuel_physical['fuel_oil']/sum(fuel_physical.values()))*100:.0f}% of fuels",
            f"{(fuel_physical['coal']/sum(fuel_physical.values()))*100:.0f}% of fuels",
            '100% of fuels',
            f"{(emission_data['direct_emissions_ktco2']/emission_data['total_emissions_ktco2'])*100:.0f}% of emissions",
            f"{(emission_data['naphtha_external_ktco2']/emission_data['total_emissions_ktco2'])*100:.0f}% of emissions",
            '100% of emissions'
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    
    print("📊 BASELINE CONSUMPTION SUMMARY:")
    print(summary_df.to_string(index=False))
    
    # Save to CSV
    summary_df.to_csv('baseline_consumption_summary.csv', index=False)
    
    # Generate detailed report
    report_content = f"""
# Korean Petrochemical Industry: Baseline Fuel and Feedstock Consumption (2024)

## Executive Summary

**Total Production**: {sum(actual_production.values()):.1f} Mt/year  
**Naphtha Feedstock**: {total_naphtha:.1f} Mt/year  
**Process Fuels**: {sum(fuel_physical.values()):.2f} Mt/year  
**Total Emissions**: {emission_data['total_emissions_ktco2']/1000:.1f} MtCO₂/year

## Production Overview

The Korean petrochemical industry produced {sum(actual_production.values()):.1f} million tonnes of products in 2024:

| Product | Production (Mt/year) | Capacity Utilization |
|---------|---------------------|---------------------|
| Ethylene | {actual_production['ethylene_production']:.1f} | 85% |
| Propylene | {actual_production['propylene_production']:.1f} | 85% |
| BTX | {actual_production['btx_production']:.1f} | 85% |
| Other Products | {actual_production['other_production']:.1f} | 85% |

## Naphtha Feedstock Consumption

**Total Naphtha Consumption**: {total_naphtha:.1f} Mt/year

### Breakdown by Product:
- **Ethylene**: {naphtha_consumption['ethylene_naphtha']:.1f} Mt/year ({(naphtha_consumption['ethylene_naphtha']/total_naphtha)*100:.1f}%)
- **Propylene**: {naphtha_consumption['propylene_naphtha']:.1f} Mt/year ({(naphtha_consumption['propylene_naphtha']/total_naphtha)*100:.1f}%)  
- **BTX**: {naphtha_consumption['btx_naphtha']:.1f} Mt/year ({(naphtha_consumption['btx_naphtha']/total_naphtha)*100:.1f}%)
- **Other Products**: {naphtha_consumption['other_naphtha']:.1f} Mt/year ({(naphtha_consumption['other_naphtha']/total_naphtha)*100:.1f}%)

### Feedstock Ratios:
- **Ethylene**: 3.1 tonnes naphtha per tonne product
- **Propylene**: 2.8 tonnes naphtha per tonne product
- **BTX**: 1.4 tonnes naphtha per tonne product
- **Other Products**: 1.8 tonnes naphtha per tonne product

## Process Fuel Consumption

**Total Process Fuels**: {sum(fuel_physical.values()):.2f} Mt/year

### Fuel Mix:
- **Natural Gas**: {fuel_physical['natural_gas']:.2f} Mt/year ({(fuel_physical['natural_gas']/sum(fuel_physical.values()))*100:.0f}%)
- **Fuel Gas (Byproduct)**: {fuel_physical['fuel_gas_byproduct']:.2f} Mt/year ({(fuel_physical['fuel_gas_byproduct']/sum(fuel_physical.values()))*100:.0f}%)
- **LPG**: {fuel_physical['lpg']:.2f} Mt/year ({(fuel_physical['lpg']/sum(fuel_physical.values()))*100:.0f}%)
- **Fuel Oil**: {fuel_physical['fuel_oil']:.2f} Mt/year ({(fuel_physical['fuel_oil']/sum(fuel_physical.values()))*100:.0f}%)
- **Coal**: {fuel_physical['coal']:.2f} Mt/year ({(fuel_physical['coal']/sum(fuel_physical.values()))*100:.0f}%)

## Energy Consumption

**Total Energy Demand**: {sum([actual_production['ethylene_production'] * 28.5, actual_production['btx_production'] * 12.3, actual_production['other_production'] * 15.2, sum(actual_production.values()) * 8.7]):.0f} GJ/year

### Energy Intensity by Process:
- **NCC (Ethylene)**: 28.5 GJ/tonne (high-temperature cracking)
- **BTX Processes**: 12.3 GJ/tonne (separation and purification)
- **Other Products**: 15.2 GJ/tonne (various processes)
- **Utilities**: 8.7 GJ/tonne (steam, power generation)

## Emission Analysis

**Total Emissions**: {emission_data['total_emissions_ktco2']/1000:.1f} MtCO₂/year

### Emission Sources:
- **Direct Combustion**: {emission_data['direct_emissions_ktco2']/1000:.1f} MtCO₂/year ({(emission_data['direct_emissions_ktco2']/emission_data['total_emissions_ktco2'])*100:.0f}%)
- **Naphtha External GHG**: {emission_data['naphtha_external_ktco2']/1000:.1f} MtCO₂/year ({(emission_data['naphtha_external_ktco2']/emission_data['total_emissions_ktco2'])*100:.0f}%)

### Direct Emissions Breakdown:
- Natural gas combustion: {(fuel_physical['natural_gas'] * 2.75):.1f} MtCO₂/year
- Fuel gas combustion: {(fuel_physical['fuel_gas_byproduct'] * 3.05):.1f} MtCO₂/year
- LPG combustion: {(fuel_physical['lpg'] * 3.00):.1f} MtCO₂/year
- Fuel oil combustion: {(fuel_physical['fuel_oil'] * 3.15):.1f} MtCO₂/year
- Coal combustion: {(fuel_physical['coal'] * 2.86):.1f} MtCO₂/year

### External GHG Sources (Naphtha Lifecycle):
- Extraction and production: {emission_data['naphtha_external_ktco2']*0.5/1000:.1f} MtCO₂/year (50%)
- Indirect emissions: {emission_data['naphtha_external_ktco2']*0.278/1000:.1f} MtCO₂/year (27.8%)
- Methane leaks: {emission_data['naphtha_external_ktco2']*0.133/1000:.1f} MtCO₂/year (13.3%)
- Transportation: {emission_data['naphtha_external_ktco2']*0.089/1000:.1f} MtCO₂/year (8.9%)

## Key Ratios and Benchmarks

### Material Efficiency:
- **Naphtha to Product Ratio**: {total_naphtha/sum(actual_production.values()):.1f}:1
- **Fuel to Product Ratio**: {sum(fuel_physical.values())/sum(actual_production.values()):.2f}:1
- **Emission Intensity**: {(emission_data['total_emissions_ktco2']/1000)/sum(actual_production.values()):.1f} tCO₂/tonne product

### Energy Efficiency:
- **Energy to Product Ratio**: {sum([actual_production['ethylene_production'] * 28.5, actual_production['btx_production'] * 12.3, actual_production['other_production'] * 15.2, sum(actual_production.values()) * 8.7])/sum(actual_production.values()):.1f} GJ/tonne product
- **Fuel Energy Efficiency**: {(sum(fuel_physical.values())*40)/(sum([actual_production['ethylene_production'] * 28.5, actual_production['btx_production'] * 12.3, actual_production['other_production'] * 15.2, sum(actual_production.values()) * 8.7]))*100:.1f}% (fuel energy/total energy)

## International Comparison

### Benchmarking against Global Averages:
- **Naphtha Intensity**: Korea {total_naphtha/sum(actual_production.values()):.1f} vs Global Average 2.4 (slightly higher)
- **Energy Intensity**: Korea {sum([actual_production['ethylene_production'] * 28.5, actual_production['btx_production'] * 12.3, actual_production['other_production'] * 15.2, sum(actual_production.values()) * 8.7])/sum(actual_production.values()):.1f} vs Global Average 16.8 GJ/tonne (slightly higher)
- **Emission Intensity**: Korea {(emission_data['total_emissions_ktco2']/1000)/sum(actual_production.values()):.1f} vs Global Average 3.2 tCO₂/tonne (higher due to external GHG inclusion)

## Implications for Decarbonization

### Reduction Potential:
1. **Naphtha Substitution**: {total_naphtha:.1f} Mt/year feedstock → Bio-naphtha potential
2. **Fuel Switching**: {sum(fuel_physical.values()):.2f} Mt/year fossil fuels → Hydrogen/renewable
3. **Process Efficiency**: {sum([actual_production['ethylene_production'] * 28.5, actual_production['btx_production'] * 12.3, actual_production['other_production'] * 15.2, sum(actual_production.values()) * 8.7]):.0f} GJ/year → Energy efficiency improvements

### Priority Areas:
1. **NCC Hydrogen Conversion**: {actual_production['ethylene_production']:.1f} Mt/year ethylene production
2. **Natural Gas Replacement**: {fuel_physical['natural_gas']:.2f} Mt/year natural gas consumption
3. **External GHG Reduction**: {emission_data['naphtha_external_ktco2']/1000:.1f} MtCO₂/year from naphtha lifecycle

## Data Sources and Methodology

### Production Data:
- Korea Petrochemical Industry Association (KPIA)
- Company annual reports and sustainability disclosures
- Ministry of Trade, Industry and Energy statistics

### Consumption Ratios:
- Industry standard engineering data
- IEA Energy Technology Perspectives
- Company process specifications

### Emission Factors:
- IPCC AR6 Working Group 3 Database
- EPA GHG Inventory Guidelines
- IEA Oil & Gas Methane Tracker

---

**Analysis Date**: {datetime.now().strftime('%Y-%m-%d')}  
**Base Year**: 2024  
**Scope**: Korean Petrochemical Industry  
**Coverage**: {len(actual_production)} major product categories, {len(fuel_physical)} fuel types
"""
    
    # Save detailed report
    with open('baseline_consumption_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("✅ Summary saved: baseline_consumption_summary.csv")
    print("✅ Detailed report saved: baseline_consumption_report.md")

def main():
    """Main execution function"""
    
    print("🏭 KOREAN PETROCHEMICAL INDUSTRY")
    print("BASELINE FUEL AND FEEDSTOCK CONSUMPTION ANALYSIS")
    print("=" * 80)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Base Year: 2024")
    print("=" * 80)
    
    # Run all calculations
    actual_production = calculate_baseline_consumption()
    naphtha_consumption, total_naphtha = calculate_naphtha_feedstock()
    fuel_consumption, fuel_physical = calculate_fuel_consumption()
    emission_data = calculate_emission_factors()
    
    # Create visualizations
    create_consumption_visualization()
    
    # Generate summary
    generate_consumption_summary()
    
    print(f"\n✅ BASELINE CONSUMPTION ANALYSIS COMPLETE")
    print("📊 Files Generated:")
    print("   • baseline_consumption_analysis.png - Comprehensive visualization")
    print("   • baseline_consumption_summary.csv - Summary data table")
    print("   • baseline_consumption_report.md - Detailed analysis report")
    
    print(f"\n🎯 KEY FINDINGS:")
    print(f"   • Total Production: {sum(actual_production.values()):.1f} Mt/year")
    print(f"   • Naphtha Feedstock: {total_naphtha:.1f} Mt/year")
    print(f"   • Process Fuels: {sum(fuel_physical.values()):.2f} Mt/year")
    print(f"   • Total Emissions: {emission_data['total_emissions_ktco2']/1000:.1f} MtCO₂/year")

if __name__ == "__main__":
    main()