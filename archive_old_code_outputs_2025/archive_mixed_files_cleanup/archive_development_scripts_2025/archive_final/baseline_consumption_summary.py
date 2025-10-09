#!/usr/bin/env python3
"""
Simplified Baseline Fuel and Feedstock Consumption Summary
Korean Petrochemical Industry - 2024 Baseline Year
"""

import pandas as pd
import numpy as np

def calculate_baseline_summary():
    """Calculate baseline fuel and feedstock consumption summary"""
    
    print("⛽ KOREAN PETROCHEMICAL BASELINE CONSUMPTION (2024)")
    print("=" * 80)
    
    # Industry production data (2024)
    production = {
        'ethylene': 6.1,          # Mt/year
        'propylene': 3.1,         # Mt/year  
        'btx': 4.1,               # Mt/year
        'other_products': 1.8     # Mt/year
    }
    
    total_production = sum(production.values())
    
    print("📊 PRODUCTION SUMMARY:")
    print(f"   Total Production: {total_production:.1f} Mt/year")
    for product, amount in production.items():
        print(f"   {product.replace('_', ' ').title()}: {amount:.1f} Mt/year")
    
    # Naphtha feedstock consumption
    naphtha_ratios = {
        'ethylene': 3.1,          # tonnes naphtha per tonne ethylene
        'propylene': 2.8,         # tonnes naphtha per tonne propylene
        'btx': 1.4,               # tonnes naphtha per tonne BTX
        'other_products': 1.8     # tonnes naphtha per tonne other
    }
    
    naphtha_consumption = {}
    for product, prod_amount in production.items():
        naphtha_consumption[product] = prod_amount * naphtha_ratios[product]
    
    total_naphtha = sum(naphtha_consumption.values())
    
    # Add utility use and losses
    utility_naphtha = total_naphtha * 0.05  # 5%
    process_losses = total_naphtha * 0.03   # 3%
    total_naphtha_with_losses = total_naphtha + utility_naphtha + process_losses
    
    print(f"\n🛢️  NAPHTHA FEEDSTOCK CONSUMPTION:")
    print(f"   Core Products: {total_naphtha:.1f} Mt/year")
    print(f"   Utility Use: {utility_naphtha:.1f} Mt/year")
    print(f"   Process Losses: {process_losses:.1f} Mt/year")
    print(f"   TOTAL NAPHTHA: {total_naphtha_with_losses:.1f} Mt/year")
    
    # Process fuel consumption
    energy_demand_pj = {
        'ncc': production['ethylene'] * 28.5 / 1000,      # PJ/year (28.5 GJ/tonne)
        'btx': production['btx'] * 12.3 / 1000,           # PJ/year (12.3 GJ/tonne)
        'other': production['other_products'] * 15.2 / 1000, # PJ/year
        'utilities': total_production * 8.7 / 1000        # PJ/year
    }
    
    total_energy_pj = sum(energy_demand_pj.values())
    
    # Fuel mix shares
    fuel_shares = {
        'natural_gas': 0.65,
        'fuel_gas': 0.20,
        'lpg': 0.08,
        'fuel_oil': 0.05,
        'coal': 0.02
    }
    
    # Calculate fuel consumption in physical units
    fuel_consumption_mt = {
        'natural_gas': (total_energy_pj * fuel_shares['natural_gas'] * 1000) / 39.5,  # Mt/year
        'fuel_gas': (total_energy_pj * fuel_shares['fuel_gas'] * 1000) / 45.2,        # Mt/year
        'lpg': (total_energy_pj * fuel_shares['lpg'] * 1000) / 46.1,                  # Mt/year
        'fuel_oil': (total_energy_pj * fuel_shares['fuel_oil'] * 1000) / 40.5,        # Mt/year
        'coal': (total_energy_pj * fuel_shares['coal'] * 1000) / 25.8                 # Mt/year
    }
    
    total_fuel_mt = sum(fuel_consumption_mt.values())
    
    print(f"\n🔥 PROCESS FUEL CONSUMPTION:")
    print(f"   Total Energy Demand: {total_energy_pj:.1f} PJ/year")
    print(f"   Total Fuel Consumption: {total_fuel_mt:.2f} Mt/year")
    for fuel, amount in fuel_consumption_mt.items():
        percentage = (amount / total_fuel_mt) * 100
        print(f"   {fuel.replace('_', ' ').title()}: {amount:.2f} Mt/year ({percentage:.0f}%)")
    
    # Emission calculations
    emission_factors = {
        'natural_gas': 2.75,      # tCO2/tonne
        'fuel_gas': 3.05,         # tCO2/tonne
        'lpg': 3.00,              # tCO2/tonne
        'fuel_oil': 3.15,         # tCO2/tonne
        'coal': 2.86,             # tCO2/tonne
        'naphtha_external': 0.90  # tCO2/tonne (lifecycle)
    }
    
    # Direct emissions from fuel combustion
    direct_emissions_mt = 0
    for fuel, consumption in fuel_consumption_mt.items():
        emissions = consumption * emission_factors[fuel]
        direct_emissions_mt += emissions
    
    # Naphtha external GHG emissions
    naphtha_external_emissions_mt = total_naphtha_with_losses * emission_factors['naphtha_external']
    
    total_emissions_mt = direct_emissions_mt + naphtha_external_emissions_mt
    
    print(f"\n🌍 EMISSION SUMMARY:")
    print(f"   Direct Combustion Emissions: {direct_emissions_mt:.1f} MtCO2/year")
    print(f"   Naphtha External GHG: {naphtha_external_emissions_mt:.1f} MtCO2/year")
    print(f"   TOTAL EMISSIONS: {total_emissions_mt:.1f} MtCO2/year")
    
    # Summary ratios
    print(f"\n📈 KEY RATIOS:")
    print(f"   Naphtha/Production Ratio: {total_naphtha_with_losses/total_production:.1f}:1")
    print(f"   Fuel/Production Ratio: {total_fuel_mt/total_production:.2f}:1")
    print(f"   Emission Intensity: {total_emissions_mt/total_production:.1f} tCO2/tonne product")
    print(f"   Energy Intensity: {total_energy_pj/total_production*1000:.0f} GJ/tonne product")
    
    # Create summary table
    summary_data = {
        'Category': [
            'Total Production',
            'Naphtha Feedstock',
            'Process Fuels',
            'Total Energy Demand',
            'Direct Emissions',
            'Naphtha External GHG',
            'Total Emissions'
        ],
        'Amount': [
            f"{total_production:.1f} Mt/year",
            f"{total_naphtha_with_losses:.1f} Mt/year",
            f"{total_fuel_mt:.2f} Mt/year", 
            f"{total_energy_pj:.1f} PJ/year",
            f"{direct_emissions_mt:.1f} MtCO2/year",
            f"{naphtha_external_emissions_mt:.1f} MtCO2/year",
            f"{total_emissions_mt:.1f} MtCO2/year"
        ],
        'Notes': [
            'Ethylene, Propylene, BTX, Other',
            'Including utility use and losses',
            'Natural gas, fuel gas, LPG, fuel oil, coal',
            'All processes and utilities',
            'From fuel combustion',
            'Naphtha lifecycle emissions',
            'Scope 1 + External GHG'
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    print(f"\n📋 CONSUMPTION SUMMARY TABLE:")
    print(summary_df.to_string(index=False))
    
    # Save to CSV
    summary_df.to_csv('baseline_consumption_summary.csv', index=False)
    
    return {
        'production': production,
        'total_production': total_production,
        'naphtha_consumption': total_naphtha_with_losses,
        'fuel_consumption': total_fuel_mt,
        'energy_demand': total_energy_pj,
        'total_emissions': total_emissions_mt,
        'direct_emissions': direct_emissions_mt,
        'naphtha_external_emissions': naphtha_external_emissions_mt
    }

def main():
    """Main execution"""
    
    print("🏭 KOREAN PETROCHEMICAL INDUSTRY")
    print("BASELINE CONSUMPTION ANALYSIS (2024)")
    print("=" * 80)
    
    results = calculate_baseline_summary()
    
    print(f"\n✅ ANALYSIS COMPLETE")
    print(f"📊 Summary saved: baseline_consumption_summary.csv")
    
    print(f"\n🎯 KEY FINDINGS:")
    print(f"   • Production: {results['total_production']:.1f} Mt/year")
    print(f"   • Naphtha: {results['naphtha_consumption']:.1f} Mt/year")
    print(f"   • Fuels: {results['fuel_consumption']:.2f} Mt/year")
    print(f"   • Emissions: {results['total_emissions']:.1f} MtCO2/year")

if __name__ == "__main__":
    main()