"""
Analyze and extract assumption data from Excel file
"""
import pandas as pd

# Read fuel_price sheet
df_fuel = pd.read_excel('assumption.xlsx', sheet_name='fuel_price', header=0)

print('='*80)
print('FUEL PRICES (Cleaned)')
print('='*80)
print()

# Get hydrogen prices (first row) - use integer column names
h2_row = df_fuel.iloc[0]
print('Hydrogen (USD/kg):')
print(f'  2025: ${h2_row[2025]:.2f}')
print(f'  2030: ${h2_row[2030]:.2f}')
print(f'  2040: ${h2_row[2040]:.2f}')
print(f'  2050: ${h2_row[2050]:.2f}')
print()

# Get electricity prices (second row)
elec_row = df_fuel.iloc[1]
print('Electricity (USD/MWh):')
print(f'  2025: ${elec_row[2025]:.2f}')
print(f'  2030: ${elec_row[2030]:.2f}')
print(f'  2035: ${elec_row[2035]:.2f}')
print(f'  2040: ${elec_row[2040]:.2f}')
print(f'  2050: ${elec_row[2050]:.2f}')
print()

# Check for KRW values
print('='*80)
print('Checking for KRW values:')
print('='*80)
for i in range(len(df_fuel)):
    label = df_fuel.iloc[i, 0]
    if pd.notna(label) and isinstance(label, str):
        val_2025 = df_fuel.iloc[i, 1]
        if pd.notna(val_2025) and val_2025 > 1000:  # Likely KRW
            print(f'{label}: {val_2025:,.0f} (2025)')
print()

# Read tech_cost sheet
df_tech = pd.read_excel('assumption.xlsx', sheet_name='tech_cost', header=0)

print('='*80)
print('TECHNOLOGY COST PARAMETERS')
print('='*80)
print()

# Extract NCC-전기로 parameters
print('NCC-전기로 (NCC-Electricity):')
ncc_elec = df_tech[df_tech['구분'] == 'NCC-전기로']
print(f'  Number of references: {len(ncc_elec)}')
if len(ncc_elec) > 0:
    print('  Energy consumption ranges:')
    for idx, row in ncc_elec.iterrows():
        if pd.notna(row.get('Unnamed: 5')):
            print(f'    - {row["출처 (논문/보고서)"][:50]:50s}: {row["Unnamed: 5"]}')
print()

# Extract NCC-수소 parameters
print('NCC-수소 (NCC-H2):')
ncc_h2 = df_tech[df_tech['구분'] == 'NCC-수소']
print(f'  Number of references: {len(ncc_h2)}')
if len(ncc_h2) > 0:
    print('  H2 consumption ranges:')
    for idx, row in ncc_h2.iterrows():
        if pd.notna(row.get('Unnamed: 5')):
            print(f'    - {row["출처 (논문/보고서)"][:50]:50s}: {row["Unnamed: 5"]}')
print()

# Look for CAPEX values
print('='*80)
print('CAPEX ESTIMATES')
print('='*80)
print()

# NCC-전기로 CAPEX
ncc_elec_capex = df_tech[(df_tech['구분'] == 'NCC-전기로') & (df_tech['Unnamed: 4'] == 'CAPEX (USD/t-C2H4/yr)')]
print('NCC-전기로 CAPEX (USD/t-C2H4/yr):')
for idx, row in ncc_elec_capex.iterrows():
    if pd.notna(row.get('Unnamed: 5')):
        print(f'  - {row["저자"]:30s} ({row["연도"]}): {row["Unnamed: 5"]}')
print()

# NCC-수소 CAPEX
ncc_h2_capex = df_tech[(df_tech['구분'].str.contains('NCC', na=False)) & (df_tech['Unnamed: 4'] == 'CAPEX (USD/t-C2H4/yr)')]
print('NCC-수소 CAPEX (USD/t-C2H4/yr):')
for idx, row in ncc_h2_capex.iterrows():
    if pd.notna(row.get('Unnamed: 5')) and '수소' not in str(row['구분']):
        continue
    if pd.notna(row.get('Unnamed: 5')):
        author = row.get('저자', 'N/A')
        year = row.get('연도', 'N/A')
        print(f'  - {author:30s} ({year}): {row["Unnamed: 5"]}')
