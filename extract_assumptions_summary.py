"""
Extract comprehensive summary of assumptions from Excel file
"""
import pandas as pd
import numpy as np

print("="*80)
print("COMPREHENSIVE ASSUMPTION SUMMARY")
print("="*80)
print()

# ============================================================================
# FUEL PRICES
# ============================================================================
df_fuel = pd.read_excel('assumption.xlsx', sheet_name='fuel_price', header=0)

print("1. FUEL PRICE TRAJECTORIES")
print("="*80)
print()

# Hydrogen prices (USD/kg)
h2_row = df_fuel.iloc[0]
print("Hydrogen (USD/kg):")
years = [2025, 2030, 2035, 2040, 2045, 2050]
for year in years:
    print(f"  {year}: ${h2_row[year]:.2f}")
print()

# Electricity prices (USD/MWh)
elec_row = df_fuel.iloc[1]
print("Electricity (USD/MWh):")
for year in years:
    print(f"  {year}: ${elec_row[year]:.2f}")
print()

# Check for KRW values (if needed for internal calculations)
print("KRW values (if applicable):")
for i in range(4, min(12, len(df_fuel))):
    label = df_fuel.iloc[i, 0]
    if pd.notna(label) and isinstance(label, str) and 'Hydrogen' in label:
        val_2025 = df_fuel.iloc[i, 1]
        if pd.notna(val_2025):
            print(f"  {label}: {val_2025:,.0f} KRW (2025)")
    elif pd.notna(label) and isinstance(label, str) and 'Electricity' in label:
        val_2025 = df_fuel.iloc[i, 1]
        if pd.notna(val_2025):
            print(f"  {label}: {val_2025:,.0f} KRW (2025)")
print()

# ============================================================================
# TECHNOLOGY PARAMETERS
# ============================================================================
df_tech = pd.read_excel('assumption.xlsx', sheet_name='tech_cost', header=0)

print("="*80)
print("2. TECHNOLOGY PARAMETERS")
print("="*80)
print()

# NCC-전기로 (NCC-Electricity)
print("NCC-전기로 (NCC-Electricity)")
print("-" * 80)
print()

print("A. Energy Consumption (MWh/ton C2H4):")
ncc_elec_energy = df_tech[(df_tech['구분'] == 'NCC-전기로') & (df_tech['Unnamed: 4'] == 'MWh/ton C₂H₄')]
for idx, row in ncc_elec_energy.iterrows():
    source = row['출처 (논문/보고서)'][:40] if len(row['출처 (논문/보고서)']) > 40 else row['출처 (논문/보고서)']
    author = row.get('저자', 'N/A')
    year = row.get('연도', 'N/A')
    value = row['Unnamed: 5']
    print(f"  • {source:40s} ({author}, {year}): {value}")
print()

print("Recommended range: 5.0-7.0 MWh/ton (moderate estimate, commercial scale)")
print("Conservative: 7.0 MWh/ton (proven technology)")
print("Optimistic: 5.0 MWh/ton (advanced plasma/electric heating)")
print()

print("B. CAPEX (USD/t-C2H4/yr):")
ncc_elec_capex = df_tech[(df_tech['구분'] == 'NCC-전기로') & (df_tech['Unnamed: 4'] == 'CAPEX (USD/t-C2H4/yr)')]
for idx, row in ncc_elec_capex.iterrows():
    author = row.get('저자', 'N/A')
    year = row.get('연도', 'N/A')
    value = row['Unnamed: 5']
    print(f"  • {author:30s} ({year}): {value}")
print()

print("Recommended: $1,500/t-C2H4/yr (large-scale commercial, Toribio-Ramirez 2025)")
print()

# NCC-수소 (NCC-H2)
print("="*80)
print("NCC-수소 (NCC-H2)")
print("-" * 80)
print()

print("A. H2 Consumption (kg H2/ton C2H4):")
ncc_h2_energy = df_tech[(df_tech['구분'] == 'NCC-수소') & (df_tech['Unnamed: 4'] == 'H₂ Consumption')]
for idx, row in ncc_h2_energy.iterrows():
    source = row['출처 (논문/보고서)'][:40] if len(row['출처 (논문/보고서)']) > 40 else row['출처 (논문/보고서)']
    author = row.get('저자', 'N/A')
    year = row.get('연도', 'N/A')
    value = row['Unnamed: 5']
    print(f"  • {source:40s} ({author}, {year})")
    print(f"    {value}")
    print()

print("Recommended range: 200-230 kg H2/ton C2H4")
print("Conservative: 230 kg H2/ton (energy balance approach)")
print("Moderate: 200 kg H2/ton (Lummus 2023, commercial estimate)")
print()

print("B. CAPEX (USD/t-C2H4/yr):")
# NCC-수소 CAPEX from rows 11-12
for idx in [11, 12]:
    if idx < len(df_tech):
        row = df_tech.iloc[idx]
        if pd.notna(row.get('Unnamed: 5')) and 'CAPEX' in str(row.get('Unnamed: 4', '')):
            author = row.get('저자', 'N/A')
            year = row.get('연도', 'N/A')
            source = row.get('출처 (논문/보고서)', 'N/A')
            value = row['Unnamed: 5']
            # Check if this is H2-related
            if 'Thunder' in source or '플라즈마' in source:
                print(f"  • {author:30s} ({year}): {value}")
                print(f"    ({source})")
print()

print("Recommended: $1,700/t-C2H4/yr (Thunder Said Energy 2023, H2-fueled furnace)")
print()

# ============================================================================
# SUMMARY RECOMMENDATIONS
# ============================================================================
print("="*80)
print("3. RECOMMENDED VALUES FOR MODEL")
print("="*80)
print()

print("NCC-전기로 (Main Scenario):")
print("  • Energy consumption: 5.0-6.0 MWh/ton C2H4 (moderate, commercial)")
print("  • CAPEX: $1,500/t-C2H4/yr")
print("  • OPEX: 4% of CAPEX annually")
print("  • Lifetime: 25 years")
print("  • Available from: 2030")
print()

print("NCC-수소 (Reference Scenario):")
print("  • H2 consumption: 200-230 kg/ton C2H4")
print("  • CAPEX: $1,700/t-C2H4/yr")
print("  • OPEX: 4% of CAPEX annually")
print("  • Lifetime: 25 years")
print("  • Available from: 2030")
print()

print("Fuel Prices (trajectory as extracted):")
print("  • Hydrogen: $6.73/kg (2025) → $2.63/kg (2050)")
print("  • Electricity: $129.29/MWh (2025) → $191.38/MWh (2050)")
print()

print("="*80)
print("Next step: Update data/technology_parameters.csv with these values")
print("="*80)
