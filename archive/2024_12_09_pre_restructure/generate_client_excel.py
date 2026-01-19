"""
Generate Comprehensive Excel Report for Client
==============================================
Korea Petrochemical Net Zero Pathway Analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SCENARIOS_DIR = DATA_DIR / "scenarios"
REPORTS_DIR = BASE_DIR / "reports"

REPORTS_DIR.mkdir(exist_ok=True)

# Scenario info
SCENARIOS = {
    'shaheen_ncc_h2': {'name': 'Shaheen + NCC-H2', 'production': 'Shaheen (Growth)', 'tech': 'NCC-H2'},
    'shaheen_ncc_electricity': {'name': 'Shaheen + NCC-Elec', 'production': 'Shaheen (Growth)', 'tech': 'NCC-Electricity'},
    'restructure_25pct_ncc_h2': {'name': 'Restructure 25% + NCC-H2', 'production': 'Restructure 25%', 'tech': 'NCC-H2'},
    'restructure_25pct_ncc_electricity': {'name': 'Restructure 25% + NCC-Elec', 'production': 'Restructure 25%', 'tech': 'NCC-Electricity'},
    'restructure_40pct_ncc_h2': {'name': 'Restructure 40% + NCC-H2', 'production': 'Restructure 40%', 'tech': 'NCC-H2'},
    'restructure_40pct_ncc_electricity': {'name': 'Restructure 40% + NCC-Elec', 'production': 'Restructure 40%', 'tech': 'NCC-Electricity'},
}

print("=" * 80)
print("GENERATING CLIENT EXCEL REPORT")
print("=" * 80)

# Load all data
print("\n1. Loading data...")

# Assumptions
tech_params = pd.read_csv(DATA_DIR / "technology_parameters.csv")
h2_prices = pd.read_csv(DATA_DIR / "h2_price_trajectory.csv")
re_prices = pd.read_csv(DATA_DIR / "re_price_trajectory.csv")
grid_ef = pd.read_csv(DATA_DIR / "grid_emission_trajectory.csv")
facilities = pd.read_csv(DATA_DIR / "facility_database_with_regions.csv")

# Scenario data
scenario_data = {}
for sid in SCENARIOS.keys():
    path = SCENARIOS_DIR / f"{sid}.csv"
    if path.exists():
        scenario_data[sid] = pd.read_csv(path)
        print(f"   Loaded: {sid}")

# Create Excel writer
output_file = REPORTS_DIR / f"Korea_Petrochemical_NetZero_Analysis_{datetime.now().strftime('%Y%m%d')}.xlsx"
writer = pd.ExcelWriter(output_file, engine='openpyxl')

print(f"\n2. Creating Excel file: {output_file.name}")

# ============================================================================
# Sheet 1: Executive Summary
# ============================================================================
print("   Creating: Executive Summary...")

summary_data = []
for sid, info in SCENARIOS.items():
    if sid in scenario_data:
        df = scenario_data[sid]
        df_2025 = df[df['year'] == 2025]
        df_2050 = df[df['year'] == 2050]

        summary_data.append({
            'Scenario': info['name'],
            'Production Pathway': info['production'],
            'NCC Technology': info['tech'],
            'Facilities (2050)': int(df_2050['n_facilities'].sum() / len(df_2050['region'].unique())),
            'BAU Emissions 2025 (kt)': round(df_2025['bau_emissions_kt'].sum(), 0),
            'BAU Emissions 2050 (kt)': round(df_2050['bau_emissions_kt'].sum(), 0),
            'Net Emissions 2050 (kt)': round(df_2050['actual_emissions_kt'].sum(), 0),
            'Total Abatement 2050 (kt)': round(df_2050['total_abatement_kt'].sum(), 0),
            'NCC Abatement (kt)': round(df_2050['ncc_abatement_kt'].sum(), 0),
            'Heat Pump Abatement (kt)': round(df_2050['hp_abatement_kt'].sum(), 0),
            'RE-PPA Abatement (kt)': round(df_2050['re_ppa_abatement_kt'].sum(), 0),
            'Electricity 2050 (TWh)': round(df_2050['elec_demand_mwh'].sum() / 1e6, 2),
        })

summary_df = pd.DataFrame(summary_data)
summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)

# ============================================================================
# Sheet 2: Assumptions - Technology
# ============================================================================
print("   Creating: Technology Assumptions...")

tech_display = tech_params[['technology', 'applies_to', 'trl', 'available_year',
                            'capex_2025_musd_per_mtco2', 'capex_2030_musd_per_mtco2',
                            'capex_2040_musd_per_mtco2', 'capex_2050_musd_per_mtco2',
                            'opex_pct_capex', 'lifetime_years', 'notes']].copy()
tech_display.columns = ['Technology', 'Application', 'TRL', 'Available Year',
                        'CAPEX 2025 (M$/MtCO2)', 'CAPEX 2030', 'CAPEX 2040', 'CAPEX 2050',
                        'OPEX (% CAPEX)', 'Lifetime (years)', 'Notes']
tech_display.to_excel(writer, sheet_name='Tech Assumptions', index=False)

# ============================================================================
# Sheet 3: Assumptions - Prices
# ============================================================================
print("   Creating: Price Trajectories...")

# Combine price data
prices_df = pd.DataFrame({
    'Year': h2_prices['year'],
    'Green H2 ($/kg)': h2_prices['h2_price_usd_per_kg'].round(3),
    'RE Electricity ($/MWh)': re_prices['re_price_usd_per_mwh'].round(2),
    'Grid EF (tCO2/MWh)': grid_ef['grid_ef_tco2_per_mwh'].round(4)
})
prices_df.to_excel(writer, sheet_name='Price Trajectories', index=False)

# ============================================================================
# Sheet 4: Facility Database
# ============================================================================
print("   Creating: Facility Database...")

fac_summary = facilities.groupby('location').agg({
    'capacity_kt': ['count', 'sum'],
    'product': lambda x: ', '.join(x.value_counts().head(3).index)
}).reset_index()
fac_summary.columns = ['Region', 'Facility Count', 'Total Capacity (kt)', 'Top Products']
fac_summary.to_excel(writer, sheet_name='Facility Summary', index=False)

# ============================================================================
# Sheets 5-10: Regional Data for Each Scenario
# ============================================================================
print("   Creating: Scenario Regional Data...")

for sid, info in SCENARIOS.items():
    if sid in scenario_data:
        df = scenario_data[sid]

        # Create regional summary for key years
        regional_data = []
        for year in [2025, 2030, 2035, 2040, 2045, 2050]:
            yr_df = df[df['year'] == year]
            for region in yr_df['region'].unique():
                r_df = yr_df[yr_df['region'] == region]
                regional_data.append({
                    'Year': int(year),
                    'Region': region,
                    'Facilities': int(r_df['n_facilities'].values[0]),
                    'Capacity (kt)': int(r_df['capacity_kt'].values[0]),
                    'BAU Emissions (kt)': round(r_df['bau_emissions_kt'].sum(), 1),
                    'Net Emissions (kt)': round(r_df['actual_emissions_kt'].sum(), 1),
                    'NCC Abatement (kt)': round(r_df['ncc_abatement_kt'].sum(), 1),
                    'HP Abatement (kt)': round(r_df['hp_abatement_kt'].sum(), 1),
                    'RE-PPA Abatement (kt)': round(r_df['re_ppa_abatement_kt'].sum(), 1),
                    'Electricity (GWh)': round(r_df['elec_demand_mwh'].sum() / 1e3, 1),
                })

        regional_df = pd.DataFrame(regional_data)

        # Short sheet name
        sheet_name = info['name'][:31]  # Excel limit
        regional_df.to_excel(writer, sheet_name=sheet_name, index=False)

# ============================================================================
# Sheet: Annual Trajectory (All Scenarios)
# ============================================================================
print("   Creating: Annual Trajectories...")

annual_data = []
for sid, info in SCENARIOS.items():
    if sid in scenario_data:
        df = scenario_data[sid]
        yearly = df.groupby('year').agg({
            'bau_emissions_kt': 'sum',
            'actual_emissions_kt': 'sum',
            'ncc_abatement_kt': 'sum',
            'hp_abatement_kt': 'sum',
            're_ppa_abatement_kt': 'sum',
            'elec_demand_mwh': 'sum'
        }).reset_index()

        yearly['Scenario'] = info['name']
        annual_data.append(yearly)

annual_df = pd.concat(annual_data, ignore_index=True)
annual_df = annual_df[['Scenario', 'year', 'bau_emissions_kt', 'actual_emissions_kt',
                        'ncc_abatement_kt', 'hp_abatement_kt', 're_ppa_abatement_kt', 'elec_demand_mwh']]
annual_df.columns = ['Scenario', 'Year', 'BAU Emissions (kt)', 'Net Emissions (kt)',
                     'NCC Abatement (kt)', 'HP Abatement (kt)', 'RE-PPA Abatement (kt)', 'Electricity (MWh)']
annual_df.to_excel(writer, sheet_name='Annual Trajectories', index=False)

# ============================================================================
# Sheet: 2050 Comparison
# ============================================================================
print("   Creating: 2050 Comparison...")

comparison_data = []
for sid, info in SCENARIOS.items():
    if sid in scenario_data:
        df = scenario_data[sid]
        df_2050 = df[df['year'] == 2050]

        for region in df_2050['region'].unique():
            r_df = df_2050[df_2050['region'] == region]
            comparison_data.append({
                'Scenario': info['name'],
                'Region': region,
                'BAU Emissions (kt)': round(r_df['bau_emissions_kt'].sum(), 1),
                'Net Emissions (kt)': round(r_df['actual_emissions_kt'].sum(), 1),
                'Reduction (%)': round((1 - r_df['actual_emissions_kt'].sum() / r_df['bau_emissions_kt'].sum()) * 100, 1),
                'Electricity (TWh)': round(r_df['elec_demand_mwh'].sum() / 1e6, 3),
            })

comparison_df = pd.DataFrame(comparison_data)
comparison_df.to_excel(writer, sheet_name='2050 Regional Comparison', index=False)

# Save and close
writer.close()

print(f"\n3. Excel file saved: {output_file}")
print("=" * 80)
print("COMPLETE!")
print("=" * 80)

# Print summary
print(f"\nSheets created:")
print(f"  1. Executive Summary")
print(f"  2. Tech Assumptions")
print(f"  3. Price Trajectories")
print(f"  4. Facility Summary")
print(f"  5-10. Regional data for each scenario")
print(f"  11. Annual Trajectories")
print(f"  12. 2050 Regional Comparison")
