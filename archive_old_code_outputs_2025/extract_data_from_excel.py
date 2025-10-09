#!/usr/bin/env python3
"""
Extract data from Excel and convert to clean CSV files
This script extracts only the RAW INPUT DATA, not calculated values
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
excel_file = 'petrochemical_cost_optimization_model/data_sources/Korean_Petrochemical_MACC_Model_English.xlsx'
output_dir = Path('data')
output_dir.mkdir(exist_ok=True)

print("="*80)
print("EXTRACTING DATA FROM EXCEL TO CSV")
print("="*80)

# 1. Facility Database - Extract from CI_Corrected
print("\n1. Extracting facility database...")
df_ci = pd.read_excel(excel_file, sheet_name='CI_Corrected')

# Create facility database with essential info only
facilities = []
for idx, row in df_ci.iterrows():
    facilities.append({
        'product': row.get('Product', f'Product_{idx}'),
        'process': row.get('Process', 'Standard'),
        'company': row.get('Company', 'Unknown'),
        'location': row.get('Location', 'Korea'),
        'capacity_kt': row.get('Capacity_kt', 1000),
        'year_built': row.get('Year_Built', 2000),
    })

df_facilities = pd.DataFrame(facilities)
df_facilities.to_csv(output_dir / 'facility_database.csv', index=False)
print(f"   ✓ Saved {len(df_facilities)} facilities")

# 2. Energy Intensities - From CI_Corrected
print("\n2. Extracting energy intensities...")
energy_cols = [
    'Naphtha_GJ_per_tonne',
    'Electricity_kWh_per_tonne',
    'LNG_GJ_per_tonne',
    'Fuel_Gas_GJ_per_tonne',
    'Byproduct_Gas_GJ_per_tonne',
    'LPG_GJ_per_tonne',
    'Fuel_Oil_GJ_per_tonne',
    'Diesel_GJ_per_tonne'
]

intensities = []
for idx, row in df_ci.iterrows():
    intensity_data = {'product': row.get('Product', f'Product_{idx}')}
    for col in energy_cols:
        intensity_data[col] = row.get(col, 0)
    intensities.append(intensity_data)

df_intensities = pd.DataFrame(intensities)
df_intensities.to_csv(output_dir / 'energy_intensities.csv', index=False)
print(f"   ✓ Saved energy intensities for {len(df_intensities)} products")

# 3. Emission Factors - Fixed values (user-specified)
print("\n3. Creating emission factors...")
emission_factors = pd.DataFrame([
    {'fuel': 'Naphtha', 'tCO2_per_GJ': 0.0149, 'source': 'User-specified'},
    {'fuel': 'Electricity', 'tCO2_per_kWh': 0.0045, 'source': 'Baseline grid 2025'},
    {'fuel': 'LNG', 'tCO2_per_GJ': 0.0149, 'source': 'User-specified (same as naphtha)'},
    {'fuel': 'Fuel_Gas', 'tCO2_per_GJ': 0.0149, 'source': 'User-specified'},
    {'fuel': 'Byproduct_Gas', 'tCO2_per_GJ': 0.0149, 'source': 'User-specified'},
    {'fuel': 'LPG', 'tCO2_per_GJ': 0.0149, 'source': 'User-specified'},
    {'fuel': 'Fuel_Oil', 'tCO2_per_GJ': 0.0149, 'source': 'User-specified'},
    {'fuel': 'Diesel', 'tCO2_per_GJ': 0.0149, 'source': 'User-specified'},
    {'fuel': 'H2', 'tCO2_per_kg': 0.0, 'source': 'Green H2 (zero emissions)'},
])
emission_factors.to_csv(output_dir / 'emission_factors.csv', index=False)
print(f"   ✓ Saved emission factors for {len(emission_factors)} fuels")

# 4. Price Trajectories
print("\n4. Extracting price trajectories...")

# H2 prices
try:
    df_h2 = pd.read_excel(excel_file, sheet_name='H2_Price_Trajectory')
    df_h2.to_csv(output_dir / 'h2_price_trajectory.csv', index=False)
    print(f"   ✓ Saved H2 price trajectory")
except:
    # Create default if not found
    h2_prices = pd.DataFrame({
        'year': range(2025, 2051),
        'h2_price_usd_per_kg': np.linspace(6.0, 1.2, 26)
    })
    h2_prices.to_csv(output_dir / 'h2_price_trajectory.csv', index=False)
    print(f"   ✓ Created default H2 price trajectory")

# RE prices
try:
    df_re = pd.read_excel(excel_file, sheet_name='RE_Price_Trajectory')
    df_re.to_csv(output_dir / 're_price_trajectory.csv', index=False)
    print(f"   ✓ Saved RE price trajectory")
except:
    # Create default if not found
    re_prices = pd.DataFrame({
        'year': range(2025, 2051),
        're_price_usd_per_mwh': np.linspace(58, 32, 26)
    })
    re_prices.to_csv(output_dir / 're_price_trajectory.csv', index=False)
    print(f"   ✓ Created default RE price trajectory")

# Grid emission trajectory
try:
    df_grid = pd.read_excel(excel_file, sheet_name='Korea_Grid_Emission_Trajectory')
    df_grid.to_csv(output_dir / 'grid_emission_trajectory.csv', index=False)
    print(f"   ✓ Saved grid emission trajectory")
except:
    # Create default
    grid_emissions = pd.DataFrame({
        'year': range(2025, 2076),
        'grid_ef_tco2_per_mwh': np.linspace(0.45, 0.05, 51)
    })
    grid_emissions.to_csv(output_dir / 'grid_emission_trajectory.csv', index=False)
    print(f"   ✓ Created default grid emission trajectory")

# 5. Technology Parameters
print("\n5. Creating technology parameters...")
technology_params = pd.DataFrame([
    {
        'technology': 'Heat_Pump',
        'applies_to': 'All processes <165°C',
        'cop': 4.0,
        'trl': 9,
        'available_year': 2025,
        'capex_2025_musd_per_mtco2': 150,
        'capex_2030_musd_per_mtco2': 120,
        'capex_2040_musd_per_mtco2': 90,
        'capex_2050_musd_per_mtco2': 75,
        'opex_pct_capex': 3.0,
        'lifetime_years': 20,
    },
    {
        'technology': 'NCC-H2',
        'applies_to': 'Naphtha crackers only',
        'cop': None,
        'trl': 7,
        'available_year': 2030,
        'capex_2025_musd_per_mtco2': 300,
        'capex_2030_musd_per_mtco2': 250,
        'capex_2040_musd_per_mtco2': 180,
        'capex_2050_musd_per_mtco2': 150,
        'opex_pct_capex': 2.5,
        'lifetime_years': 25,
    },
    {
        'technology': 'NCC-Electricity',
        'applies_to': 'Naphtha crackers only',
        'cop': None,
        'trl': 6,
        'available_year': 2030,
        'capex_2025_musd_per_mtco2': 350,
        'capex_2030_musd_per_mtco2': 300,
        'capex_2040_musd_per_mtco2': 220,
        'capex_2050_musd_per_mtco2': 180,
        'opex_pct_capex': 2.0,
        'lifetime_years': 25,
    },
])
technology_params.to_csv(output_dir / 'technology_parameters.csv', index=False)
print(f"   ✓ Saved technology parameters for {len(technology_params)} technologies")

# 6. Heat Pump Applicability by Product
print("\n6. Creating heat pump applicability...")
try:
    df_hp = pd.read_excel(excel_file, sheet_name='Heat_Pump_Applicability')
    df_hp.to_csv(output_dir / 'heat_pump_applicability.csv', index=False)
    print(f"   ✓ Saved heat pump applicability")
except:
    # Create default
    hp_applicability = pd.DataFrame([
        {'product_group': 'Olefins', 'applicability_pct': 10, 'temperature_c': 850},
        {'product_group': 'Aromatics', 'applicability_pct': 60, 'temperature_c': 140},
        {'product_group': 'Polymers', 'applicability_pct': 45, 'temperature_c': 180},
        {'product_group': 'Intermediates', 'applicability_pct': 50, 'temperature_c': 150},
        {'product_group': 'Other', 'applicability_pct': 35, 'temperature_c': 200},
    ])
    hp_applicability.to_csv(output_dir / 'heat_pump_applicability.csv', index=False)
    print(f"   ✓ Created default heat pump applicability")

# 7. Baseline fuel costs
print("\n7. Creating baseline fuel costs...")
fuel_costs = pd.DataFrame([
    {'fuel': 'Naphtha', 'cost_2025_usd_per_gj': 15.0},
    {'fuel': 'LNG', 'cost_2025_usd_per_gj': 12.0},
    {'fuel': 'Fuel_Gas', 'cost_2025_usd_per_gj': 10.0},
    {'fuel': 'Byproduct_Gas', 'cost_2025_usd_per_gj': 5.0},
    {'fuel': 'LPG', 'cost_2025_usd_per_gj': 14.0},
    {'fuel': 'Fuel_Oil', 'cost_2025_usd_per_gj': 13.0},
    {'fuel': 'Diesel', 'cost_2025_usd_per_gj': 16.0},
    {'fuel': 'Electricity', 'cost_2025_usd_per_kwh': 0.10},
])
fuel_costs.to_csv(output_dir / 'fuel_costs_baseline.csv', index=False)
print(f"   ✓ Saved baseline fuel costs")

print("\n" + "="*80)
print("✓ DATA EXTRACTION COMPLETE")
print("="*80)
print(f"\nAll data saved to: {output_dir.absolute()}")
print("\nExtracted files:")
for f in sorted(output_dir.glob('*.csv')):
    print(f"   - {f.name}")
