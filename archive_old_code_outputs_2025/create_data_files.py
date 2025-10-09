#!/usr/bin/env python3
"""
Create all data files from Excel with REAL facility data
Uses source_Original sheet with actual company ownership
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
excel_file = 'petrochemical_cost_optimization_model/data_sources/Korean_Petrochemical_MACC_Model_English.xlsx'
data_dir = Path('data')
data_dir.mkdir(exist_ok=True)

print("="*80)
print("CREATING DATA FILES - USING REAL FACILITY DATA")
print("="*80)

# 1. Read REAL facilities from source_Original
print("\n1. Reading REAL facility data from source_Original...")
df_facilities_raw = pd.read_excel(excel_file, sheet_name='source_Original')

# Rename columns to match our schema
df_facilities = df_facilities_raw.rename(columns={
    'products': 'product',
    'capacity_1000_t': 'capacity_kt',
    'year': 'year_built'
}).copy()

# Select relevant columns
df_facilities = df_facilities[['product', 'process', 'company', 'location', 'capacity_kt', 'year_built']].copy()

print(f"   ✓ Loaded {len(df_facilities)} REAL facilities")
print(f"   ✓ Companies: {df_facilities['company'].nunique()} unique companies")
print(f"   ✓ Locations: {df_facilities['location'].nunique()} unique locations")
print(f"   ✓ Products: {df_facilities['product'].nunique()} unique products")
print(f"   ✓ Capacity range: {df_facilities['capacity_kt'].min():.0f} - {df_facilities['capacity_kt'].max():.0f} kt/year")
print(f"   ✓ Year built range: {df_facilities['year_built'].min()} - {df_facilities['year_built'].max()}")

# 2. Read energy intensities from CI_Corrected
print("\n2. Reading energy intensities from CI_Corrected...")
df_ci = pd.read_excel(excel_file, sheet_name='CI_Corrected')

# Rename columns for consistency
df_ci = df_ci.rename(columns={
    'LNG_GJ_per_t': 'LNG_GJ_per_tonne',
    'Byproduct_Gas_GJ_per_t': 'Byproduct_Gas_GJ_per_tonne',
    'LPG_Propane_GJ_per_t': 'LPG_GJ_per_tonne',
    'Fuel_Gas_Mix_GJ_per_t': 'Fuel_Gas_GJ_per_tonne',
    'Fuel_Oil_GJ_per_t': 'Fuel_Oil_GJ_per_tonne',
    'Diesel_GJ_per_t': 'Diesel_GJ_per_tonne',
    'Electricity_kWh_per_t': 'Electricity_kWh_per_tonne',
    'Naphtha_Thermal_GJ_per_t': 'Naphtha_GJ_per_tonne',
})

# Select relevant columns
intensity_cols = ['Product', 'Process', 'Naphtha_GJ_per_tonne', 'Electricity_kWh_per_tonne',
                 'LNG_GJ_per_tonne', 'Fuel_Gas_GJ_per_tonne', 'Byproduct_Gas_GJ_per_tonne',
                 'LPG_GJ_per_tonne', 'Fuel_Oil_GJ_per_tonne', 'Diesel_GJ_per_tonne']

df_intensities = df_ci[intensity_cols].copy()
df_intensities = df_intensities.fillna(0)
df_intensities = df_intensities.rename(columns={'Product': 'product', 'Process': 'process'})

print(f"   ✓ Loaded {len(df_intensities)} product intensities")

# 3. Match facilities with energy intensities
print("\n3. Matching facilities with energy intensities...")

# Create facility intensities by merging on product
df_facility_intensities = df_facilities.merge(
    df_intensities,
    on='product',
    how='left',
    suffixes=('', '_intensity')
)

# For facilities without exact match, try to find similar product
missing_intensities = df_facility_intensities[df_facility_intensities['Naphtha_GJ_per_tonne'].isna()]
if len(missing_intensities) > 0:
    print(f"   ⚠ {len(missing_intensities)} facilities missing intensity data")
    print(f"   ℹ Products without matches: {missing_intensities['product'].unique()}")

    # Fill with zero for now (or could use average)
    df_facility_intensities = df_facility_intensities.fillna(0)

# Remove duplicate process column
if 'process_intensity' in df_facility_intensities.columns:
    df_facility_intensities = df_facility_intensities.drop(columns=['process_intensity'])

print(f"   ✓ Matched {len(df_facility_intensities)} facilities with intensities")

# 4. Calculate baseline emissions and scale if needed
print("\n4. Calculating baseline emissions...")

ef_fossil = 0.0149  # tCO2/GJ
ef_electricity = 0.0045  # tCO2/kWh

total_emissions = 0
facility_emissions = []

for i in range(len(df_facilities)):
    fac = df_facilities.iloc[i]
    intensity = df_facility_intensities.iloc[i]

    capacity = fac['capacity_kt']

    # Calculate emissions (kt CO2)
    emissions = 0
    emissions += intensity['Naphtha_GJ_per_tonne'] * capacity * ef_fossil
    emissions += intensity['Electricity_kWh_per_tonne'] * capacity * ef_electricity
    emissions += intensity['LNG_GJ_per_tonne'] * capacity * ef_fossil
    emissions += intensity['Fuel_Gas_GJ_per_tonne'] * capacity * ef_fossil
    emissions += intensity['Byproduct_Gas_GJ_per_tonne'] * capacity * ef_fossil
    emissions += intensity['LPG_GJ_per_tonne'] * capacity * ef_fossil
    emissions += intensity['Fuel_Oil_GJ_per_tonne'] * capacity * ef_fossil
    emissions += intensity['Diesel_GJ_per_tonne'] * capacity * ef_fossil

    facility_emissions.append(emissions)
    total_emissions += emissions

print(f"   ✓ Total baseline emissions (pre-scaling): {total_emissions/1000:.2f} MtCO2")

# Scale intensities to hit 52 MtCO2 target
target_emissions = 52000  # kt CO2
scale_factor = target_emissions / total_emissions
print(f"   ℹ Scaling intensities by {scale_factor:.4f} to reach 52 MtCO2")

for col in ['Naphtha_GJ_per_tonne', 'Electricity_kWh_per_tonne', 'LNG_GJ_per_tonne',
            'Fuel_Gas_GJ_per_tonne', 'Byproduct_Gas_GJ_per_tonne', 'LPG_GJ_per_tonne',
            'Fuel_Oil_GJ_per_tonne', 'Diesel_GJ_per_tonne']:
    df_facility_intensities[col] = df_facility_intensities[col] * scale_factor

# Verify
total_emissions_scaled = 0
for i in range(len(df_facilities)):
    fac = df_facilities.iloc[i]
    intensity = df_facility_intensities.iloc[i]
    capacity = fac['capacity_kt']

    emissions = 0
    emissions += intensity['Naphtha_GJ_per_tonne'] * capacity * ef_fossil
    emissions += intensity['Electricity_kWh_per_tonne'] * capacity * ef_electricity
    emissions += intensity['LNG_GJ_per_tonne'] * capacity * ef_fossil
    emissions += intensity['Fuel_Gas_GJ_per_tonne'] * capacity * ef_fossil
    emissions += intensity['Byproduct_Gas_GJ_per_tonne'] * capacity * ef_fossil
    emissions += intensity['LPG_GJ_per_tonne'] * capacity * ef_fossil
    emissions += intensity['Fuel_Oil_GJ_per_tonne'] * capacity * ef_fossil
    emissions += intensity['Diesel_GJ_per_tonne'] * capacity * ef_fossil

    total_emissions_scaled += emissions

print(f"   ✓ Total baseline emissions (post-scaling): {total_emissions_scaled/1000:.2f} MtCO2")

# 5. Save facility database and intensities
print("\n5. Saving facility data...")
df_facilities.to_csv(data_dir / 'facility_database.csv', index=False)
df_facility_intensities.to_csv(data_dir / 'energy_intensities.csv', index=False)
print(f"   ✓ Saved facility_database.csv")
print(f"   ✓ Saved energy_intensities.csv")

# 6. Emission factors
print("\n6. Creating emission factors...")
emission_factors = pd.DataFrame([
    {'fuel': 'Naphtha', 'tCO2_per_GJ': 0.0149, 'tCO2_per_kWh': np.nan, 'tCO2_per_kg': np.nan},
    {'fuel': 'Electricity', 'tCO2_per_GJ': np.nan, 'tCO2_per_kWh': 0.0045, 'tCO2_per_kg': np.nan},
    {'fuel': 'LNG', 'tCO2_per_GJ': 0.0149, 'tCO2_per_kWh': np.nan, 'tCO2_per_kg': np.nan},
    {'fuel': 'Fuel_Gas', 'tCO2_per_GJ': 0.0149, 'tCO2_per_kWh': np.nan, 'tCO2_per_kg': np.nan},
    {'fuel': 'Byproduct_Gas', 'tCO2_per_GJ': 0.0149, 'tCO2_per_kWh': np.nan, 'tCO2_per_kg': np.nan},
    {'fuel': 'LPG', 'tCO2_per_GJ': 0.0149, 'tCO2_per_kWh': np.nan, 'tCO2_per_kg': np.nan},
    {'fuel': 'Fuel_Oil', 'tCO2_per_GJ': 0.0149, 'tCO2_per_kWh': np.nan, 'tCO2_per_kg': np.nan},
    {'fuel': 'Diesel', 'tCO2_per_GJ': 0.0149, 'tCO2_per_kWh': np.nan, 'tCO2_per_kg': np.nan},
    {'fuel': 'H2', 'tCO2_per_GJ': np.nan, 'tCO2_per_kWh': np.nan, 'tCO2_per_kg': 0.0},
])
emission_factors.to_csv(data_dir / 'emission_factors.csv', index=False)
print(f"   ✓ Saved emission factors")

# 7. Price trajectories
print("\n7. Creating price trajectories...")

# H2 prices
h2_prices = pd.DataFrame({
    'year': range(2025, 2051),
    'h2_price_usd_per_kg': np.linspace(6.0, 1.2, 26)
})
h2_prices.to_csv(data_dir / 'h2_price_trajectory.csv', index=False)

# RE prices
re_prices = pd.DataFrame({
    'year': range(2025, 2051),
    're_price_usd_per_mwh': np.linspace(58, 32, 26)
})
re_prices.to_csv(data_dir / 're_price_trajectory.csv', index=False)

# Grid emissions
grid_emissions = pd.DataFrame({
    'year': range(2025, 2076),
    'grid_ef_tco2_per_mwh': np.linspace(0.45, 0.05, 51)
})
grid_emissions.to_csv(data_dir / 'grid_emission_trajectory.csv', index=False)

# Fossil fuel prices (constant in real terms - assume inflation-adjusted)
fuel_prices = pd.DataFrame({
    'year': range(2025, 2051),
    'naphtha_usd_per_gj': [15.0] * 26,
    'lng_usd_per_gj': [12.0] * 26,
    'fuel_gas_usd_per_gj': [10.0] * 26,
    'lpg_usd_per_gj': [14.0] * 26,
    'fuel_oil_usd_per_gj': [13.0] * 26,
    'diesel_usd_per_gj': [16.0] * 26,
    'electricity_usd_per_kwh': [0.10] * 26,
})
fuel_prices.to_csv(data_dir / 'fuel_price_trajectory.csv', index=False)

print(f"   ✓ Saved price trajectories")

# 8. Technology parameters
print("\n8. Creating technology parameters...")
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
        'cop': np.nan,
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
        'cop': np.nan,
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
technology_params.to_csv(data_dir / 'technology_parameters.csv', index=False)
print(f"   ✓ Saved technology parameters")

# 9. Heat pump applicability
print("\n9. Creating heat pump applicability...")
hp_applicability = pd.DataFrame([
    {'product_group': 'Olefins', 'applicability_pct': 10, 'max_temperature_c': 850},
    {'product_group': 'Aromatics', 'applicability_pct': 60, 'max_temperature_c': 140},
    {'product_group': 'Polymers', 'applicability_pct': 45, 'max_temperature_c': 180},
    {'product_group': 'Intermediates', 'applicability_pct': 50, 'max_temperature_c': 150},
    {'product_group': 'Other', 'applicability_pct': 35, 'max_temperature_c': 200},
])
hp_applicability.to_csv(data_dir / 'heat_pump_applicability.csv', index=False)
print(f"   ✓ Saved heat pump applicability")

print("\n" + "="*80)
print("✓ DATA FILES CREATED WITH REAL FACILITY DATA")
print("="*80)
print(f"\nAll data saved to: {data_dir.absolute()}")
print("\nFiles created:")
for f in sorted(data_dir.glob('*.csv')):
    print(f"   - {f.name}")

# 10. Show company summary
print("\n" + "="*80)
print("COMPANY OWNERSHIP SUMMARY (REAL DATA)")
print("="*80)

company_summary = df_facilities.groupby('company').agg({
    'product': 'count',
    'capacity_kt': 'sum'
}).rename(columns={'product': 'n_facilities', 'capacity_kt': 'total_capacity_kt'})

# Count NCC facilities (Ethylene/Propylene from Naphtha Cracker)
ncc_facilities = df_facilities[
    (df_facilities['product'].isin(['Ethylene', 'Propylene'])) &
    (df_facilities['process'] == 'Naphtha Cracker')
].groupby('company').size()

company_summary['n_ncc_facilities'] = ncc_facilities.fillna(0).astype(int)
company_summary = company_summary.sort_values('n_facilities', ascending=False)

print("\nTop 15 companies by number of facilities:")
print(company_summary.head(15).to_string())

print("\n" + "="*80)
print("NCC FACILITIES OWNERSHIP (ETHYLENE + PROPYLENE)")
print("="*80)

ncc_only = df_facilities[
    (df_facilities['product'].isin(['Ethylene', 'Propylene'])) &
    (df_facilities['process'] == 'Naphtha Cracker')
]

ncc_company_summary = ncc_only.groupby('company').agg({
    'product': 'count',
    'capacity_kt': 'sum'
}).rename(columns={'product': 'n_ncc_facilities', 'capacity_kt': 'ncc_capacity_kt'})
ncc_company_summary = ncc_company_summary.sort_values('ncc_capacity_kt', ascending=False)

print("\nNCC facilities by company:")
print(ncc_company_summary.to_string())
