import pandas as pd

# Load Excel data
excel_path = "../data/Korea_Petrochemical_MACC_Database.xlsx"
baseline_df = pd.read_excel(excel_path, sheet_name='BaselineConsumption_2023')
facilities_df = pd.read_excel(excel_path, sheet_name='RegionalFacilities')

print("DATA ALIGNMENT VALIDATION:")
print("-" * 40)

# Calculate total capacities
baseline_totals = {
    'NCC': baseline_df[baseline_df['TechGroup'] == 'NCC']['Activity_kt_product'].sum(),
    'BTX': baseline_df[baseline_df['TechGroup'] == 'BTX']['Activity_kt_product'].sum(),
    'C4': baseline_df[baseline_df['TechGroup'] == 'C4']['Activity_kt_product'].sum()
}

facilities_totals = {
    'NCC': facilities_df['NCC_Capacity_kt_per_year'].sum(),
    'BTX': facilities_df['BTX_Capacity_kt_per_year'].sum(),
    'C4': facilities_df['C4_Capacity_kt_per_year'].sum()
}

print("Capacity Comparison:")
for process in ['NCC', 'BTX', 'C4']:
    baseline_cap = baseline_totals[process]
    facilities_cap = facilities_totals[process]
    diff_pct = ((facilities_cap - baseline_cap) / baseline_cap * 100) if baseline_cap > 0 else 0
    status = "✅ ALIGNED" if abs(diff_pct) < 5 else "❌ MISALIGNED"
    
    print(f"  {process}:")
    print(f"    Baseline:   {baseline_cap:7.0f} kt/year")
    print(f"    Facilities: {facilities_cap:7.0f} kt/year") 
    print(f"    Difference: {diff_pct:6.1f}% {status}")

print("\nBaselineConsumption_2023 structure:")
print(baseline_df.groupby(['TechGroup', 'Band'])['Activity_kt_product'].sum())

print("\nRegionalFacilities structure:")  
print("Total by region:")
for region in facilities_df['Region'].unique():
    region_data = facilities_df[facilities_df['Region'] == region]
    total_ncc = region_data['NCC_Capacity_kt_per_year'].sum()
    total_btx = region_data['BTX_Capacity_kt_per_year'].sum()
    total_c4 = region_data['C4_Capacity_kt_per_year'].sum()
    print(f"  {region}: NCC={total_ncc:.0f}, BTX={total_btx:.0f}, C4={total_c4:.0f} kt/year")