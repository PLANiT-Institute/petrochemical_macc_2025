import pandas as pd

file_path = 'data/energy_intensities.csv'
df = pd.read_csv(file_path)

# Conversion factors
kWh_to_GJ = 0.0036

# Energy columns
# Identify columns that end with _per_tonne, excluding the non-numeric metadata if any matched (none do)
energy_cols = [c for c in df.columns if 'per_tonne' in c]
print("Energy columns found:", energy_cols)


# Aggregate totals by fuel type
fuel_totals_gj = {}

for col in energy_cols:
    fuel_name = col.replace('_GJ_per_tonne', '').replace('_per_tonne', '')
    if col == 'Electricity_kWh_per_tonne':
        fuel_name = 'Electricity'
        
    fuel_totals_gj[fuel_name] = 0.0

total_global_gj = 0.0

for index, row in df.iterrows():
    capacity_t = row['capacity_kt'] * 1000
    
    for col in energy_cols:
        fuel_name = col.replace('_GJ_per_tonne', '').replace('_per_tonne', '')
        if col == 'Electricity_kWh_per_tonne':
            fuel_name = 'Electricity'
            # Convert kWh/t to GJ/t
            intensity_gj = row[col] * kWh_to_GJ
        else:
            intensity_gj = row[col]
            
        consumption_gj = intensity_gj * capacity_t
        fuel_totals_gj[fuel_name] += consumption_gj
        total_global_gj += consumption_gj


# Create summary table
summary_data = []
TOE_CONVERSION_FACTOR = 41.868  # 1 TOE = 41.868 GJ

for fuel, amount_gj in fuel_totals_gj.items():
    share = (amount_gj / total_global_gj) * 100
    # Convert GJ to 1,000 TOE
    # 1000 TOE = (GJ / 41.868) / 1000 = GJ / 41868
    amount_1000_toe = amount_gj / (TOE_CONVERSION_FACTOR * 1000)
    
    summary_data.append({
        'Fuel Type': fuel,
        'Consumption (1,000 TOE)': amount_1000_toe,
        'Share (%)': share
    })

summary_df = pd.DataFrame(summary_data)
summary_df = summary_df.sort_values('Share (%)', ascending=False)

print("\nEnergy Consumption Share by Fuel Type:")
print(summary_df.to_markdown(index=False, floatfmt=".2f"))

