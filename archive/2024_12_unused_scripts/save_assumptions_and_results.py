"""
SAVE ASSUMPTIONS AND RESULTS AS STRUCTURED CSVs
================================================
This script extracts all model assumptions and results into clean CSV files
for verification and auditing purposes.

Output Directory: outputs/verification/
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob

# Directories
DATA_DIR = Path('data')
OUTPUT_DIR = Path('outputs/verification')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("SAVING MODEL ASSUMPTIONS AND RESULTS")
print("=" * 80)

# =============================================================================
# PART 1: ASSUMPTIONS
# =============================================================================
print("\n" + "=" * 80)
print("PART 1: ASSUMPTIONS")
print("=" * 80)

# 1.1 Emission Factors
print("\n1.1 Emission Factors...")
df_ef = pd.read_csv(DATA_DIR / 'emission_factors.csv')
df_ef.to_csv(OUTPUT_DIR / 'assumptions_01_emission_factors.csv', index=False)
print(f"   Saved: assumptions_01_emission_factors.csv ({len(df_ef)} fuels)")

# 1.2 Technology Parameters (CAPEX, OPEX, Learning Curves)
print("\n1.2 Technology Parameters...")
df_tech = pd.read_csv(DATA_DIR / 'technology_parameters.csv')
df_tech.to_csv(OUTPUT_DIR / 'assumptions_02_technology_parameters.csv', index=False)
print(f"   Saved: assumptions_02_technology_parameters.csv ({len(df_tech)} technologies)")

# 1.3 H2 Price Trajectory (LCOH-based)
print("\n1.3 H2 Price Trajectory...")
df_h2 = pd.read_csv(DATA_DIR / 'h2_price_trajectory.csv')
df_h2.to_csv(OUTPUT_DIR / 'assumptions_03_h2_price_trajectory.csv', index=False)
print(f"   Saved: assumptions_03_h2_price_trajectory.csv ({len(df_h2)} years)")

# 1.4 RE Price Trajectory
print("\n1.4 RE Price Trajectory...")
df_re = pd.read_csv(DATA_DIR / 're_price_trajectory.csv')
df_re.to_csv(OUTPUT_DIR / 'assumptions_04_re_price_trajectory.csv', index=False)
print(f"   Saved: assumptions_04_re_price_trajectory.csv ({len(df_re)} years)")

# 1.5 Grid Emission Trajectory
print("\n1.5 Grid Emission Trajectory...")
df_grid = pd.read_csv(DATA_DIR / 'grid_emission_trajectory.csv')
df_grid.to_csv(OUTPUT_DIR / 'assumptions_05_grid_emission_trajectory.csv', index=False)
print(f"   Saved: assumptions_05_grid_emission_trajectory.csv ({len(df_grid)} years)")

# 1.6 Grid Price Trajectory
print("\n1.6 Grid Price Trajectory...")
df_grid_price = pd.read_csv(DATA_DIR / 'grid_price_trajectory.csv')
df_grid_price.to_csv(OUTPUT_DIR / 'assumptions_06_grid_price_trajectory.csv', index=False)
print(f"   Saved: assumptions_06_grid_price_trajectory.csv ({len(df_grid_price)} years)")

# 1.7 Fuel Price Trajectory
print("\n1.7 Fuel Price Trajectory...")
df_fuel = pd.read_csv(DATA_DIR / 'fuel_price_trajectory.csv')
df_fuel.to_csv(OUTPUT_DIR / 'assumptions_07_fuel_price_trajectory.csv', index=False)
print(f"   Saved: assumptions_07_fuel_price_trajectory.csv ({len(df_fuel)} years)")

# 1.8 Heat Pump Applicability
print("\n1.8 Heat Pump Applicability...")
df_hp = pd.read_csv(DATA_DIR / 'heat_pump_applicability.csv')
df_hp.to_csv(OUTPUT_DIR / 'assumptions_08_heat_pump_applicability.csv', index=False)
print(f"   Saved: assumptions_08_heat_pump_applicability.csv ({len(df_hp)} product groups)")

# 1.9 Emission Targets (Policy Constraints)
print("\n1.9 Emission Targets...")
df_targets = pd.read_csv(DATA_DIR / 'emission_scenarios_clean.csv')
df_targets.to_csv(OUTPUT_DIR / 'assumptions_09_emission_targets.csv', index=False)
print(f"   Saved: assumptions_09_emission_targets.csv ({len(df_targets)} targets)")

# 1.10 Demand Growth Trajectory
print("\n1.10 Demand Growth Trajectory...")
df_demand = pd.read_csv(DATA_DIR / 'demand_growth_trajectory.csv')
df_demand.to_csv(OUTPUT_DIR / 'assumptions_10_demand_growth_trajectory.csv', index=False)
print(f"   Saved: assumptions_10_demand_growth_trajectory.csv ({len(df_demand)} years)")

# 1.11 Facility Database
print("\n1.11 Facility Database...")
df_fac = pd.read_csv(DATA_DIR / 'facility_database_with_regions.csv')
df_fac.to_csv(OUTPUT_DIR / 'assumptions_11_facility_database.csv', index=False)
print(f"   Saved: assumptions_11_facility_database.csv ({len(df_fac)} facilities)")

# 1.12 Create Summary Assumptions Table
print("\n1.12 Creating Summary Assumptions...")
summary_assumptions = []

# Key assumptions
summary_assumptions.append({'category': 'Emission Factors', 'parameter': 'Naphtha EF', 'value': df_ef[df_ef['fuel']=='Naphtha']['tCO2_per_GJ'].values[0], 'unit': 'tCO2/GJ', 'source': 'IPCC 2019'})
summary_assumptions.append({'category': 'Emission Factors', 'parameter': 'LNG EF', 'value': df_ef[df_ef['fuel']=='LNG']['tCO2_per_GJ'].values[0], 'unit': 'tCO2/GJ', 'source': 'IPCC 2019'})
summary_assumptions.append({'category': 'Emission Factors', 'parameter': 'Grid EF (2025)', 'value': df_grid[df_grid['year']==2025]['grid_ef_tco2_per_mwh'].values[0], 'unit': 'tCO2/MWh', 'source': 'Korea Power Exchange'})
summary_assumptions.append({'category': 'Emission Factors', 'parameter': 'Grid EF (2050)', 'value': df_grid[df_grid['year']==2050]['grid_ef_tco2_per_mwh'].values[0], 'unit': 'tCO2/MWh', 'source': 'Korea NDC Target'})

# H2 prices
summary_assumptions.append({'category': 'Energy Prices', 'parameter': 'H2 Price (2025)', 'value': df_h2[df_h2['year']==2025]['h2_price_usd_per_kg'].values[0], 'unit': 'USD/kg', 'source': 'LCOH Calculation'})
summary_assumptions.append({'category': 'Energy Prices', 'parameter': 'H2 Price (2050)', 'value': df_h2[df_h2['year']==2050]['h2_price_usd_per_kg'].values[0], 'unit': 'USD/kg', 'source': 'LCOH Calculation'})
summary_assumptions.append({'category': 'Energy Prices', 'parameter': 'RE Price (2025)', 'value': df_re[df_re['year']==2025]['re_price_usd_per_mwh'].values[0], 'unit': 'USD/MWh', 'source': 'Korea RE PPA Market'})
summary_assumptions.append({'category': 'Energy Prices', 'parameter': 'RE Price (2050)', 'value': df_re[df_re['year']==2050]['re_price_usd_per_mwh'].values[0], 'unit': 'USD/MWh', 'source': 'Learning Curve Projection'})

# Technology parameters
for _, row in df_tech.iterrows():
    summary_assumptions.append({'category': 'Technology CAPEX', 'parameter': f"{row['technology']} CAPEX (2025)", 'value': row['capex_2025_musd_per_mtco2'], 'unit': 'M USD/MtCO2', 'source': row.get('notes', 'N/A')})
    summary_assumptions.append({'category': 'Technology CAPEX', 'parameter': f"{row['technology']} CAPEX (2050)", 'value': row['capex_2050_musd_per_mtco2'], 'unit': 'M USD/MtCO2', 'source': row.get('notes', 'N/A')})

# Emission targets
for _, row in df_targets.iterrows():
    if pd.notna(row['year']):
        summary_assumptions.append({'category': 'Policy Targets', 'parameter': f"Target {int(row['year'])}", 'value': row['target_mt'], 'unit': 'MtCO2', 'source': 'Korea NDC'})

# Facilities
summary_assumptions.append({'category': 'Facilities', 'parameter': 'Total Facilities', 'value': len(df_fac), 'unit': 'count', 'source': 'KPIA Database'})
summary_assumptions.append({'category': 'Facilities', 'parameter': 'NCC Facilities', 'value': len(df_fac[df_fac['process']=='Naphtha Cracker']), 'unit': 'count', 'source': 'KPIA Database'})
summary_assumptions.append({'category': 'Facilities', 'parameter': 'BTX Facilities', 'value': len(df_fac[df_fac['process']=='BTX Plant']), 'unit': 'count', 'source': 'KPIA Database'})

df_summary_assumptions = pd.DataFrame(summary_assumptions)
df_summary_assumptions.to_csv(OUTPUT_DIR / 'assumptions_00_summary.csv', index=False)
print(f"   Saved: assumptions_00_summary.csv ({len(df_summary_assumptions)} parameters)")

# =============================================================================
# PART 2: RESULTS
# =============================================================================
print("\n" + "=" * 80)
print("PART 2: RESULTS")
print("=" * 80)

scenarios = [
    ('scenario_shaheen_ncc_h2', 'Shaheen NCC-H2'),
    ('scenario_shaheen_ncc_electricity', 'Shaheen NCC-Elec'),
    ('scenario_restructure_25pct_ncc_h2', 'Restructure 25% H2'),
    ('scenario_restructure_25pct_ncc_electricity', 'Restructure 25% Elec'),
    ('scenario_restructure_40pct_ncc_h2', 'Restructure 40% H2'),
    ('scenario_restructure_40pct_ncc_electricity', 'Restructure 40% Elec'),
]

# 2.1 Deployment Trajectories (all scenarios combined)
print("\n2.1 Deployment Trajectories...")
all_deployments = []
for folder, name in scenarios:
    deploy_files = glob.glob(f'outputs/{folder}/module_03_optimization/*_deployment.csv')
    if deploy_files:
        df = pd.read_csv(deploy_files[0])
        df['scenario'] = name
        all_deployments.append(df)

df_all_deploy = pd.concat(all_deployments, ignore_index=True)
df_all_deploy.to_csv(OUTPUT_DIR / 'results_01_deployment_trajectories.csv', index=False)
print(f"   Saved: results_01_deployment_trajectories.csv ({len(df_all_deploy)} rows)")

# 2.2 MACC Data (from first scenario as reference)
print("\n2.2 MACC Data...")
macc_file = 'outputs/scenario_shaheen_ncc_h2/module_02_macc/macc_annual_2025_2050.csv'
df_macc = pd.read_csv(macc_file)
df_macc.to_csv(OUTPUT_DIR / 'results_02_macc_annual.csv', index=False)
print(f"   Saved: results_02_macc_annual.csv ({len(df_macc)} rows)")

# 2.3 Baseline Emissions (from first scenario)
print("\n2.3 Baseline Emissions...")
baseline_file = 'outputs/scenario_shaheen_ncc_h2/module_01_baseline/baseline_2025_detailed.csv'
df_baseline = pd.read_csv(baseline_file)
df_baseline.to_csv(OUTPUT_DIR / 'results_03_baseline_emissions.csv', index=False)
print(f"   Saved: results_03_baseline_emissions.csv ({len(df_baseline)} facilities)")

# 2.4 BAU Trajectory
print("\n2.4 BAU Trajectory...")
bau_file = 'outputs/scenario_shaheen_ncc_h2/module_01_baseline/bau_trajectory_2025_2050.csv'
df_bau = pd.read_csv(bau_file)
df_bau.to_csv(OUTPUT_DIR / 'results_04_bau_trajectory.csv', index=False)
print(f"   Saved: results_04_bau_trajectory.csv ({len(df_bau)} years)")

# 2.5 Final Scenario Summary
print("\n2.5 Final Scenario Summary...")
df_summary = pd.read_csv('outputs/scenario_summary_final.csv')
df_summary.to_csv(OUTPUT_DIR / 'results_05_scenario_summary.csv', index=False)
print(f"   Saved: results_05_scenario_summary.csv ({len(df_summary)} scenarios)")

# 2.6 Create Key Results Table (2050 values)
print("\n2.6 Creating Key Results Table...")
key_results = []
for folder, name in scenarios:
    deploy_files = glob.glob(f'outputs/{folder}/module_03_optimization/*_deployment.csv')
    if deploy_files:
        df = pd.read_csv(deploy_files[0])
        d2050 = df[df['year'] == 2050].iloc[0]
        d2035 = df[df['year'] == 2035].iloc[0]
        d2030 = df[df['year'] == 2030].iloc[0]

        key_results.append({
            'scenario': name,
            'bau_2030_mt': d2030['bau_mt'],
            'actual_2030_mt': d2030['actual_emissions_mt'],
            'bau_2035_mt': d2035['bau_mt'],
            'actual_2035_mt': d2035['actual_emissions_mt'],
            'bau_2050_mt': d2050['bau_mt'],
            'actual_2050_mt': d2050['actual_emissions_mt'],
            'heat_pump_2050_mt': d2050['heat_pump_mt'],
            'ncc_h2_2050_mt': d2050['ncc_h2_mt'],
            'ncc_elec_2050_mt': d2050['ncc_elec_mt'],
            're_ppa_2050_mt': d2050['re_ppa_mt'],
            'rdh_2050_mt': d2050['rdh_mt'],
            'total_abatement_2050_mt': d2050['total_deployed_mt'],
            'h2_demand_2050_kt': d2050['h2_consumption_kt'],
            'elec_increase_2050_twh': d2050['electricity_consumption_increase_twh'],
            'capex_total_busd': d2050['cumulative_capex_musd'] / 1000,
        })

df_key_results = pd.DataFrame(key_results)
df_key_results.to_csv(OUTPUT_DIR / 'results_06_key_results_by_scenario.csv', index=False)
print(f"   Saved: results_06_key_results_by_scenario.csv ({len(df_key_results)} scenarios)")

# 2.7 Technology Cost Evolution
print("\n2.7 Technology Cost Evolution...")
tech_costs = []
for year in [2025, 2030, 2035, 2040, 2045, 2050]:
    year_data = df_macc[df_macc['year'] == year]
    for _, row in year_data.iterrows():
        tech_costs.append({
            'year': year,
            'technology': row['technology'],
            'available': row['available'],
            'abatement_potential_mtco2': row['abatement_potential_mtco2'],
            'capex_ann_usd_per_tco2': row['capex_ann_usd_per_tco2'],
            'opex_ann_usd_per_tco2': row['opex_ann_usd_per_tco2'],
            'fuel_cost_diff_usd_per_tco2': row['fuel_cost_diff_usd_per_tco2'],
            'total_cost_usd_per_tco2': row['total_cost_usd_per_tco2'],
        })

df_tech_costs = pd.DataFrame(tech_costs)
df_tech_costs.to_csv(OUTPUT_DIR / 'results_07_technology_cost_evolution.csv', index=False)
print(f"   Saved: results_07_technology_cost_evolution.csv ({len(df_tech_costs)} rows)")

# =============================================================================
# PART 3: CALCULATION INPUTS (for verification)
# =============================================================================
print("\n" + "=" * 80)
print("PART 3: CALCULATION INPUTS FOR VERIFICATION")
print("=" * 80)

# 3.1 Baseline by Facility Type
print("\n3.1 Baseline by Facility Type...")
baseline_by_type = df_baseline.groupby(['process', 'product_group']).agg({
    'total_emissions_kt': 'sum',
    'emissions_electricity_kt': 'sum',
    'emissions_naphtha_kt': 'sum',
    'emissions_lng_kt': 'sum',
    'emissions_fuel_gas_kt': 'sum',
    'capacity_kt': 'sum',
}).reset_index()
baseline_by_type['combustion_emissions_kt'] = (
    baseline_by_type['total_emissions_kt'] - baseline_by_type['emissions_electricity_kt']
)
baseline_by_type.to_csv(OUTPUT_DIR / 'calc_input_01_baseline_by_facility_type.csv', index=False)
print(f"   Saved: calc_input_01_baseline_by_facility_type.csv")

# 3.2 Technology Applicability Matrix
print("\n3.2 Technology Applicability Matrix...")
tech_applicability = []
# NCC facilities
tech_applicability.append({'facility_type': 'Naphtha Cracker', 'technology': 'NCC-H2', 'applicable': True, 'notes': 'Mutually exclusive with NCC-Elec'})
tech_applicability.append({'facility_type': 'Naphtha Cracker', 'technology': 'NCC-Electricity', 'applicable': True, 'notes': 'Mutually exclusive with NCC-H2'})
tech_applicability.append({'facility_type': 'Naphtha Cracker', 'technology': 'Heat_Pump', 'applicable': False, 'notes': 'NCC uses NCC technologies'})
tech_applicability.append({'facility_type': 'Naphtha Cracker', 'technology': 'RDH', 'applicable': False, 'notes': 'NCC uses NCC technologies'})
tech_applicability.append({'facility_type': 'Naphtha Cracker', 'technology': 'RE_PPA', 'applicable': True, 'notes': 'For existing electricity'})

# BTX facilities
tech_applicability.append({'facility_type': 'BTX Plant', 'technology': 'NCC-H2', 'applicable': False, 'notes': 'Only for NCC'})
tech_applicability.append({'facility_type': 'BTX Plant', 'technology': 'NCC-Electricity', 'applicable': False, 'notes': 'Only for NCC'})
tech_applicability.append({'facility_type': 'BTX Plant', 'technology': 'Heat_Pump', 'applicable': True, 'notes': '60% of heat demand'})
tech_applicability.append({'facility_type': 'BTX Plant', 'technology': 'RDH', 'applicable': True, 'notes': '40% of heat demand (high-temp)'})
tech_applicability.append({'facility_type': 'BTX Plant', 'technology': 'RE_PPA', 'applicable': True, 'notes': 'For existing electricity'})

# Other facilities
tech_applicability.append({'facility_type': 'Other', 'technology': 'NCC-H2', 'applicable': False, 'notes': 'Only for NCC'})
tech_applicability.append({'facility_type': 'Other', 'technology': 'NCC-Electricity', 'applicable': False, 'notes': 'Only for NCC'})
tech_applicability.append({'facility_type': 'Other', 'technology': 'Heat_Pump', 'applicable': True, 'notes': 'Based on product group'})
tech_applicability.append({'facility_type': 'Other', 'technology': 'RDH', 'applicable': True, 'notes': 'Gap not covered by HP'})
tech_applicability.append({'facility_type': 'Other', 'technology': 'RE_PPA', 'applicable': True, 'notes': 'For existing electricity'})

df_tech_applicability = pd.DataFrame(tech_applicability)
df_tech_applicability.to_csv(OUTPUT_DIR / 'calc_input_02_technology_applicability.csv', index=False)
print(f"   Saved: calc_input_02_technology_applicability.csv")

# 3.3 Key Conversion Factors
print("\n3.3 Key Conversion Factors...")
conversion_factors = [
    {'parameter': 'H2 consumption per ton ethylene', 'value': 0.098, 'unit': 'ton H2/ton ethylene', 'source': 'BASF/SABIC Pilot'},
    {'parameter': 'Electricity consumption NCC-Elec', 'value': 5.0, 'unit': 'MWh/ton ethylene', 'source': 'BASF/SABIC Pilot'},
    {'parameter': 'Heat Pump COP', 'value': 4.0, 'unit': 'dimensionless', 'source': 'Industry average'},
    {'parameter': 'RDH efficiency', 'value': 0.93, 'unit': 'dimensionless', 'source': 'Coolbrook'},
    {'parameter': 'Technology lifetime', 'value': 20, 'unit': 'years', 'source': 'Standard assumption'},
    {'parameter': 'NCC baseline combustion EF', 'value': 1.74, 'unit': 'tCO2/ton product', 'source': 'Calculated from baseline'},
    {'parameter': 'GJ to MWh conversion', 'value': 3.6, 'unit': 'GJ/MWh', 'source': 'Physical constant'},
]
df_conversion = pd.DataFrame(conversion_factors)
df_conversion.to_csv(OUTPUT_DIR / 'calc_input_03_conversion_factors.csv', index=False)
print(f"   Saved: calc_input_03_conversion_factors.csv")

print("\n" + "=" * 80)
print("COMPLETE: All files saved to outputs/verification/")
print("=" * 80)

# List all files
import os
files = sorted(os.listdir(OUTPUT_DIR))
print(f"\nGenerated {len(files)} files:")
for f in files:
    size = os.path.getsize(OUTPUT_DIR / f)
    print(f"   {f} ({size:,} bytes)")
