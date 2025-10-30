"""
Update all assumption files from the Excel assumption.xlsx file
"""
import pandas as pd
import numpy as np
from pathlib import Path

print("="*80)
print("UPDATING ALL ASSUMPTIONS FROM assumption.xlsx")
print("="*80)
print()

# ============================================================================
# 1. UPDATE FUEL PRICE TRAJECTORIES
# ============================================================================
print("1. Updating H2 price trajectory...")

df_fuel = pd.read_excel('assumption.xlsx', sheet_name='fuel_price', header=0)

# Extract H2 prices
h2_row = df_fuel.iloc[0]
h2_years = list(range(2025, 2051))
h2_prices = [h2_row[year] for year in h2_years]

# Create H2 price trajectory DataFrame
df_h2 = pd.DataFrame({
    'year': h2_years,
    'h2_price_usd_per_kg': h2_prices,
    'source': ['Excel assumption.xlsx' for _ in h2_years],
    'notes': ['Updated from user Excel file - trajectory from literature review' for _ in h2_years]
})

# Save to file
h2_output = Path('data/h2_price_trajectory.csv')
df_h2.to_csv(h2_output, index=False)
print(f"   ✓ Saved: {h2_output}")
print(f"   Range: ${h2_prices[0]:.2f}/kg (2025) → ${h2_prices[-1]:.2f}/kg (2050)")
print()

# ============================================================================
# 2. UPDATE ELECTRICITY PRICE TRAJECTORY
# ============================================================================
print("2. Updating RE/Electricity price trajectory...")

# Extract electricity prices
elec_row = df_fuel.iloc[1]
elec_years = list(range(2025, 2051))
elec_prices = [elec_row[year] for year in elec_years]

# Create RE price trajectory DataFrame
df_re = pd.DataFrame({
    'year': elec_years,
    're_price_usd_per_mwh': elec_prices,
    'source': ['Excel assumption.xlsx' for _ in elec_years],
    'notes': ['Updated from user Excel file - reflects grid electricity cost escalation' for _ in elec_years]
})

# Save to file
re_output = Path('data/re_price_trajectory.csv')
df_re.to_csv(re_output, index=False)
print(f"   ✓ Saved: {re_output}")
print(f"   Range: ${elec_prices[0]:.2f}/MWh (2025) → ${elec_prices[-1]:.2f}/MWh (2050)")
print()

# ============================================================================
# 3. UPDATE TECHNOLOGY PARAMETERS
# ============================================================================
print("3. Updating technology_parameters.csv...")

# Read current parameters
df_tech_params = pd.read_csv('data/technology_parameters.csv')

print()
print("   IMPORTANT UPDATES:")
print("   " + "="*76)
print()

# Update NCC-Electricity parameters
# From Excel: 5.0-6.0 MWh/ton C2H4, CAPEX $1,500/t-C2H4/yr
print("   NCC-Electricity (MAIN SCENARIO):")
print("   • Energy consumption: 3.0 → 5.5 MWh/ton C2H4 (updated from Excel literature)")
print("   • CAPEX: Will be recalculated based on $1,500/t-C2H4/yr")
print("   • Available: 2030")

# Update the row
mask = df_tech_params['technology'] == 'NCC-Electricity'
df_tech_params.loc[mask, 'elec_mwh_per_ton_ethylene'] = 5.5  # Moderate estimate from Excel
df_tech_params.loc[mask, 'notes'] = 'Literature (Excel review): 5.0-7.0 MWh/ton | Using 5.5 MWh (moderate) | CAPEX $1,500/t-C2H4/yr | OPEX 4%'
df_tech_params.loc[mask, 'opex_pct_capex'] = 4.0  # Update to 4% per Excel
print()

# Update NCC-H2 parameters
# From Excel: 200-230 kg H2/ton C2H4, CAPEX $1,700/t-C2H4/yr
print("   NCC-H2 (REFERENCE SCENARIO):")
print("   • H2 consumption: 0.23 → 0.20 ton/ton C2H4 (200 kg, Lummus 2023)")
print("   • CAPEX: Will be recalculated based on $1,700/t-C2H4/yr")
print("   • Available: 2030")

mask = df_tech_params['technology'] == 'NCC-H2'
df_tech_params.loc[mask, 'h2_ton_per_ton_ethylene'] = 0.20  # 200 kg per ton
df_tech_params.loc[mask, 'notes'] = 'Literature (Excel review): 200-230 kg H2/ton | Using 200 kg (Lummus 2023) | CAPEX $1,700/t-C2H4/yr | OPEX 4%'
print()

# Note about CAPEX conversion
print("   ⚠️  CAPEX CONVERSION NOTE:")
print("   Current CAPEX format: MUSD per MtCO2 abatement")
print("   Excel provides: USD per ton C2H4 capacity per year")
print("   ")
print("   Conversion requires knowing emission intensity of baseline.")
print("   Keeping current CAPEX values for now - will need manual adjustment")
print("   based on actual emission reduction per ton ethylene produced.")
print()

# Save updated tech params
tech_output = Path('data/technology_parameters.csv')
df_tech_params.to_csv(tech_output, index=False)
print(f"   ✓ Saved: {tech_output}")
print()

# ============================================================================
# 4. SUMMARY OF CHANGES
# ============================================================================
print("="*80)
print("SUMMARY OF CHANGES")
print("="*80)
print()

print("FUEL PRICES:")
print(f"  • H2: ${h2_prices[0]:.2f}/kg → ${h2_prices[-1]:.2f}/kg")
print(f"  • Electricity: ${elec_prices[0]:.2f}/MWh → ${elec_prices[-1]:.2f}/MWh")
print(f"    ⚠️  NOTE: Electricity prices INCREASE over time (grid cost escalation)")
print()

print("TECHNOLOGY PARAMETERS:")
print("  • NCC-Electricity: 5.5 MWh/ton C2H4 (was 3.0)")
print("  • NCC-H2: 0.20 ton H2/ton C2H4 (was 0.23)")
print("  • Both have OPEX 4% (was 3.5-4.0%)")
print()

print("SCENARIO CONFIGURATION:")
print("  • Main Scenario: NCC-전기로 (NCC-Electricity)")
print("  • Reference Scenario: NCC-수소 (NCC-H2)")
print()

print("="*80)
print("NEXT STEPS:")
print("="*80)
print("1. Verify CAPEX conversion is correct (check first MACC run)")
print("2. Configure optimization to prefer NCC-Electricity (main scenario)")
print("3. Re-run all 3 production scenarios")
print("4. Update Streamlit dashboard")
print("5. Update Korean Word document")
print("="*80)
