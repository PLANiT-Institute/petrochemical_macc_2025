import pandas as pd
import matplotlib.pyplot as plt

# User Provided Data (Baseline 2017) - Units: 1,000 TOE
# (User gave values in TOE. "3,592,000 TOE" -> 3592 kTOE)
user_data_ktoe = {
    'LPG': 3592,
    'LNG': 1372,
    'Electricity': 3929
}

# Emission Factors (tCO2e / TOE)
# Estimates derived to match diagram or standard IPCC
# Electricity: User 3929 kTOE -> ~15.9 Mt CO2 (from Diagram Indirect) => EF ~ 4.05
# LPG: Standard ~2.64 (63.1 kg/GJ)
# LNG: Standard ~2.35 (56.1 kg/GJ)
# Fuel Gas / Byproduct Gas: Assume similar to Byproduct/Fuel Gas ~ 2.6
EF_TOE = {
    'LPG': 2.64,
    'LNG': 2.35,
    'Electricity': 4.05, 
    'Fuel_Gas': 2.6, 
    'Byproduct_Gas': 2.6,
    'Naphtha': 0, # Feedstock assumed sequestered
    'Others': 2.5
}

# Load CSV to determine Splits (NCC vs Non-NCC) and Gas Volumes
file_path = 'data/energy_intensities.csv'
df = pd.read_csv(file_path)

# Normalize Process Names for Splitting
# "Naphtha Cracker" is NCC. Everything else is Non-NCC.
df['Sector'] = df['process'].apply(lambda x: 'NCC' if 'Naphtha Cracker' in str(x) else 'Non-NCC')

# Calculate Ratios from CSV
# We need to know: Of the total Industry use of X, what % is NCC?
# We calculate the 'Theoretical Total' from CSV first.

kWh_to_GJ = 0.0036
TOE_to_GJ = 41.868

csv_totals = {
    'LPG': 0.0,
    'LNG': 0.0,
    'Electricity': 0.0,
    'Fuel_Gas': 0.0,
    'Byproduct_Gas': 0.0
}
csv_ncc_totals = {k: 0.0 for k in csv_totals}

for index, row in df.iterrows():
    cap_kt = row['capacity_kt']
    is_ncc = (row['Sector'] == 'NCC')
    
    # helper
    def add_val(energy_type, val_per_tonne_gj):
        total_gj = val_per_tonne_gj * cap_kt * 1000
        total_ktoe = total_gj / TOE_to_GJ / 1000
        csv_totals[energy_type] += total_ktoe
        if is_ncc:
            csv_ncc_totals[energy_type] += total_ktoe

    # LPG
    add_val('LPG', row.get('LPG_GJ_per_tonne', 0))
    # LNG
    add_val('LNG', row.get('LNG_GJ_per_tonne', 0))
    # Fuel Gas
    add_val('Fuel_Gas', row.get('Fuel_Gas_GJ_per_tonne', 0))
    # Byproduct Gas
    add_val('Byproduct_Gas', row.get('Byproduct_Gas_GJ_per_tonne', 0))
    
    # Electricity (converted from kWh)
    elec_kwh = row.get('Electricity_kWh_per_tonne', 0)
    elec_gj = elec_kwh * kWh_to_GJ
    add_val('Electricity', elec_gj)

# Calculate Splits (NCC Share)
splits = {}
for k in csv_totals:
    if csv_totals[k] > 0:
        splits[k] = csv_ncc_totals[k] / csv_totals[k]
    else:
        # Default fallback if CSV has 0. NCCs are usually the main consumers of Gas/LPG.
        splits[k] = 0.9 if k in ['Fuel_Gas', 'Byproduct_Gas', 'LPG'] else 0.5

print("Calculated Sector Splits (NCC Share):")
for k, v in splits.items():
    print(f"  {k}: {v:.2%}")

# --- Baseline (2017) Calculation ---
# Rules: 
# 1. LPG, LNG, Electricity: Use User Data * Split
# 2. Fuel Gas, Byproduct Gas: Use CSV Data * Scaling Factor?
#    Problem: CSV totals for Fuel Gas might be based on 2023 capacity.
#    Let's Calibrate Fuel Gas to fill the gap to ~45.9 Mt?
#    Or just use CSV raw.
#    Let's use CSV raw for Gas volumes (assuming intensities are constant) and check total.
#    If total is weird, we'll note it.
#    Wait, User LPG is 3.6M, CSV LPG is 0.
#    So split for LPG derived from CSV (0/0) is undefined. 
#    Manual Override: NCCs consume most LPG for cracking/heating. Assume 95% NCC for LPG.
#    LNG: Assume CSV split is valid.
#    Electricity: Assume CSV split is valid.

splits['LPG'] = 0.95 # Override due to missing data in CSV

baseline_emissions = {
    'NCC_Direct': 0.0,
    'NCC_Indirect': 0.0,
    'NonNCC_Direct': 0.0,
    'NonNCC_Indirect': 0.0
}

def calc_emission(fuel, volume_ktoe, is_direct):
    ef = EF_TOE.get(fuel, 2.5)
    e_mt = volume_ktoe * ef / 1000 # kTOE * t/TOE = kt. /1000 = Mt
    
    ncc_share = splits.get(fuel, 0.5)
    
    ncc_amt = e_mt * ncc_share
    non_ncc_amt = e_mt * (1 - ncc_share)
    
    if is_direct:
        baseline_emissions['NCC_Direct'] += ncc_amt
        baseline_emissions['NonNCC_Direct'] += non_ncc_amt
    else:
        baseline_emissions['NCC_Indirect'] += ncc_amt
        baseline_emissions['NonNCC_Indirect'] += non_ncc_amt
        
    return e_mt

# Calculate
print("\n--- Baseline Numbers (User Data + CSV Gas) ---")
calc_emission('LPG', user_data_ktoe['LPG'], True)
calc_emission('LNG', user_data_ktoe['LNG'], True)
calc_emission('Electricity', user_data_ktoe['Electricity'], False)

# For Fuel Gas / Byproduct Gas: Use CSV quantities directly
# (Assuming CSV reflects a "Standard Year" close enough, or scaling is needed)
# My CSV Fuel Gas ~ 4500 kTOE.
calc_emission('Fuel_Gas', csv_totals['Fuel_Gas'], True)
calc_emission('Byproduct_Gas', csv_totals['Byproduct_Gas'], True)

base_total = sum(baseline_emissions.values())
print(f"Total Baseline Emissions: {base_total:.2f} Mt")
print("Breakdown:", baseline_emissions)

# --- 2024 Estimation ---
# Growth Factor 1.10
growth_ratio = 1.10
estim_2024 = {k: v * growth_ratio for k, v in baseline_emissions.items()}
estim_2024_total = base_total * growth_ratio

print(f"\n--- 2024 Estimated Emissions (Ratio {growth_ratio}) ---")
print(f"Total: {estim_2024_total:.2f} Mt")
print("Breakdown:", estim_2024)

# --- Generate Logic for 2024 Energy Use ---
print(f"\n--- 2024 Energy Use Estimation (1,000 TOE) ---")
for fuel, val in user_data_ktoe.items():
    print(f"  {fuel}: {val * growth_ratio:,.0f}")
    
# --- Plotting ---
labels = ['NCC Direct', 'NCC Indirect', 'Non-NCC Direct', 'Non-NCC Indirect']
colors = ['#5bc0de', '#5cb85c', '#f0ad4e', '#d9534f'] # approx colors from image (Blue, Green, Orange, Red)
sizes_base = [baseline_emissions['NCC_Direct'], baseline_emissions['NCC_Indirect'], 
              baseline_emissions['NonNCC_Direct'], baseline_emissions['NonNCC_Indirect']]

fig, ax = plt.subplots(figsize=(8, 6))
patches, texts, autotexts = ax.pie(sizes_base, labels=labels, autopct='%1.1f', startangle=90, colors=colors)
ax.axis('equal')  
plt.title(f'Petrochemical GHG Emissions (Baseline)\nTotal: {base_total:.1f} Mt')

# Make text readable
for t in texts: t.set_fontsize(10)
for t in autotexts: t.set_fontsize(10)

plt.savefig('baseline_emissions_plot.png')
print("Plot saved to baseline_emissions_plot.png")
