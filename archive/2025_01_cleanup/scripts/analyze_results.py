"""
ANALYZE RESULTS - Generate Excel Reports from Scenario Results
==============================================================
Reads outputs/scenario_results.csv and generates comprehensive Excel reports.

Output: reports/Korea_Petrochemical_NetZero_Analysis_YYYYMMDD.xlsx

Sheets:
1. Raw_Data - Complete long-format output (source of truth)
2. Assumptions - Technology parameters and price trajectories
3. Scenario_Summary - Key metrics by scenario (2050)
4. Regional_Summary - Emissions and costs by region
5. Technology_Deployment - Technology mix and deployment
6. Facility_Summary - Facility counts by region and technology
7. MACC_Data - Data for MACC curve generation
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
INPUT_FILE = Path('outputs/scenario_results.csv')
DATA_DIR = Path('data')
REPORTS_DIR = Path('reports')
REPORTS_DIR.mkdir(exist_ok=True)

# Output filename with date
TODAY = datetime.now().strftime('%Y%m%d')
OUTPUT_FILE = REPORTS_DIR / f'Korea_Petrochemical_NetZero_Analysis_{TODAY}.xlsx'


def load_results():
    """Load scenario results from CSV"""
    print("Loading scenario results...")
    df = pd.read_csv(INPUT_FILE)
    print(f"  Loaded {len(df):,} rows")
    return df


def create_raw_data_sheet(df):
    """Sheet 1: Raw_Data - Complete long-format output"""
    print("Creating Raw_Data sheet...")
    return df.copy()


def create_assumptions_sheet():
    """Sheet 2: Assumptions - Technology parameters and price trajectories in long format"""
    print("Creating Assumptions sheet...")

    assumptions = []

    # Technology CAPEX
    tech = pd.read_csv(DATA_DIR / 'technology_parameters.csv')
    for _, row in tech.iterrows():
        tech_name = row['technology']
        for year in [2025, 2030, 2040, 2050]:
            assumptions.append({
                'year': year,
                'category': 'Technology CAPEX',
                'technology': tech_name,
                'product': 'All',
                'parameter': 'capex_musd_per_mtco2',
                'value': row[f'capex_{year}_musd_per_mtco2'],
                'unit': 'M$/MtCO2'
            })
        # Add other parameters
        assumptions.append({
            'year': 2025,
            'category': 'Technology Parameter',
            'technology': tech_name,
            'product': 'All',
            'parameter': 'opex_pct_capex',
            'value': row.get('opex_pct_capex', 0),
            'unit': '%'
        })
        assumptions.append({
            'year': 2025,
            'category': 'Technology Parameter',
            'technology': tech_name,
            'product': 'All',
            'parameter': 'lifetime_years',
            'value': row.get('lifetime_years', 25),
            'unit': 'years'
        })
        assumptions.append({
            'year': 2025,
            'category': 'Technology Parameter',
            'technology': tech_name,
            'product': 'All',
            'parameter': 'available_year',
            'value': row.get('available_year', 2025),
            'unit': 'year'
        })
        if pd.notna(row.get('cop')):
            assumptions.append({
                'year': 2025,
                'category': 'Technology Parameter',
                'technology': tech_name,
                'product': 'All',
                'parameter': 'cop',
                'value': row['cop'],
                'unit': '-'
            })

    # H2 Price trajectory
    h2 = pd.read_csv(DATA_DIR / 'h2_price_trajectory.csv')
    for _, row in h2.iterrows():
        assumptions.append({
            'year': int(row['year']),
            'category': 'Energy Price',
            'technology': 'H2',
            'product': 'All',
            'parameter': 'h2_price',
            'value': row['h2_price_usd_per_kg'],
            'unit': '$/kg'
        })

    # RE Price trajectory
    re = pd.read_csv(DATA_DIR / 're_price_trajectory.csv')
    for _, row in re.iterrows():
        assumptions.append({
            'year': int(row['year']),
            'category': 'Energy Price',
            'technology': 'RE',
            'product': 'All',
            'parameter': 're_price',
            'value': row['re_price_usd_per_mwh'],
            'unit': '$/MWh'
        })

    # Grid Emission Factor trajectory
    grid = pd.read_csv(DATA_DIR / 'grid_emission_trajectory.csv')
    for _, row in grid.iterrows():
        assumptions.append({
            'year': int(row['year']),
            'category': 'Grid Parameter',
            'technology': 'Grid',
            'product': 'All',
            'parameter': 'grid_ef',
            'value': row['grid_ef_tco2_per_mwh'],
            'unit': 'tCO2/MWh'
        })

    # Key model parameters
    model_params = [
        {'year': 2025, 'category': 'Model Parameter', 'technology': 'All', 'product': 'All',
         'parameter': 'operating_rate', 'value': 70, 'unit': '%'},
        {'year': 2025, 'category': 'Model Parameter', 'technology': 'Heat_Pump', 'product': 'All',
         'parameter': 'cop', 'value': 4.0, 'unit': '-'},
        {'year': 2025, 'category': 'Model Parameter', 'technology': 'NCC-H2', 'product': 'Ethylene',
         'parameter': 'h2_consumption', 'value': 0.2, 'unit': 't-H2/t-C2H4'},
        {'year': 2025, 'category': 'Model Parameter', 'technology': 'NCC-Electricity', 'product': 'Ethylene',
         'parameter': 'elec_consumption', 'value': 5.0, 'unit': 'MWh/t-C2H4'},
    ]
    assumptions.extend(model_params)

    return pd.DataFrame(assumptions)


def create_scenario_summary(df):
    """Sheet 3: Scenario_Summary - Key metrics by scenario (2050)"""
    print("Creating Scenario_Summary sheet...")

    summary_data = []

    for scenario in df['scenario'].unique():
        df_s = df[df['scenario'] == scenario]

        # 2025 baseline
        df_2025 = df_s[df_s['year'] == 2025]
        baseline_emissions = df_2025['bau_emissions_tco2'].sum()

        # 2050 results
        df_2050 = df_s[df_s['year'] == 2050]
        final_emissions = df_2050['emissions_tco2'].sum()
        total_abatement = df_2050['abatement_tco2'].sum()
        total_cost = df_2050['total_cost_usd'].sum()
        total_capex = df_2050['capex_usd'].sum()

        # MAC calculation
        mac = total_cost / total_abatement if total_abatement > 0 else 0

        # Facility counts
        total_facilities = df_2050['facility_id'].nunique()
        deployed_facilities = df_2050[df_2050['tech_deployed'] == 1]['facility_id'].nunique()

        # Energy demands
        h2_demand = df_2050['h2_demand_t'].sum()
        elec_demand = df_2050['elec_demand_mwh'].sum()

        summary_data.append({
            'scenario': scenario,
            'baseline_emissions_mtco2': baseline_emissions / 1e6,
            'final_emissions_mtco2': final_emissions / 1e6,
            'total_abatement_mtco2': total_abatement / 1e6,
            'emission_reduction_pct': (1 - final_emissions / baseline_emissions) * 100 if baseline_emissions > 0 else 0,
            'total_capex_b_usd': total_capex / 1e9,
            'total_cost_b_usd': total_cost / 1e9,
            'mac_usd_per_tco2': mac,
            'total_facilities': total_facilities,
            'deployed_facilities': deployed_facilities,
            'h2_demand_mt': h2_demand / 1e6,
            'elec_demand_twh': elec_demand / 1e6,
        })

    return pd.DataFrame(summary_data)


def create_regional_summary(df):
    """Sheet 4: Regional_Summary - Emissions and costs by region and scenario"""
    print("Creating Regional_Summary sheet...")

    regional_data = []

    for scenario in df['scenario'].unique():
        df_s = df[df['scenario'] == scenario]

        for year in df_s['year'].unique():
            df_y = df_s[df_s['year'] == year]

            for region in df_y['region'].unique():
                df_r = df_y[df_y['region'] == region]

                regional_data.append({
                    'scenario': scenario,
                    'year': year,
                    'region': region,
                    'bau_emissions_mtco2': df_r['bau_emissions_tco2'].sum() / 1e6,
                    'emissions_mtco2': df_r['emissions_tco2'].sum() / 1e6,
                    'abatement_mtco2': df_r['abatement_tco2'].sum() / 1e6,
                    'capex_b_usd': df_r['capex_usd'].sum() / 1e9,
                    'total_cost_b_usd': df_r['total_cost_usd'].sum() / 1e9,
                    'h2_demand_kt': df_r['h2_demand_t'].sum() / 1e3,
                    'elec_demand_twh': df_r['elec_demand_mwh'].sum() / 1e6,
                    'facility_count': df_r['facility_id'].nunique(),
                })

    return pd.DataFrame(regional_data)


def create_technology_deployment(df):
    """Sheet 5: Technology_Deployment - Technology mix and deployment over time"""
    print("Creating Technology_Deployment sheet...")

    tech_data = []

    for scenario in df['scenario'].unique():
        df_s = df[df['scenario'] == scenario]

        for year in df_s['year'].unique():
            df_y = df_s[df_s['year'] == year]

            for tech in df_y['technology'].unique():
                df_t = df_y[df_y['technology'] == tech]

                tech_data.append({
                    'scenario': scenario,
                    'year': year,
                    'technology': tech,
                    'facility_count': df_t['facility_id'].nunique(),
                    'deployed_count': df_t[df_t['tech_deployed'] == 1]['facility_id'].nunique(),
                    'abatement_mtco2': df_t['abatement_tco2'].sum() / 1e6,
                    'capex_b_usd': df_t['capex_usd'].sum() / 1e9,
                    'total_cost_b_usd': df_t['total_cost_usd'].sum() / 1e9,
                    'mac_usd_per_tco2': df_t['total_cost_usd'].sum() / df_t['abatement_tco2'].sum() if df_t['abatement_tco2'].sum() > 0 else 0,
                    'h2_demand_kt': df_t['h2_demand_t'].sum() / 1e3,
                    'elec_demand_twh': df_t['elec_demand_mwh'].sum() / 1e6,
                })

    return pd.DataFrame(tech_data)


def create_facility_summary(df):
    """Sheet 6: Facility_Summary - Facility counts by region and technology"""
    print("Creating Facility_Summary sheet...")

    # Get 2050 data for summary
    df_2050 = df[df['year'] == 2050]

    facility_data = []

    for scenario in df_2050['scenario'].unique():
        df_s = df_2050[df_2050['scenario'] == scenario]

        for region in df_s['region'].unique():
            df_r = df_s[df_s['region'] == region]

            # By technology
            for tech in df_r['technology'].unique():
                df_t = df_r[df_r['technology'] == tech]

                facility_data.append({
                    'scenario': scenario,
                    'region': region,
                    'technology': tech,
                    'process': df_t['process'].mode().iloc[0] if len(df_t) > 0 else '',
                    'facility_count': df_t['facility_id'].nunique(),
                    'deployed_count': df_t[df_t['tech_deployed'] == 1]['facility_id'].nunique(),
                    'capacity_kt': df_t['capacity_tpy'].sum() / 1e3,
                    'bau_emissions_ktco2': df_t['bau_emissions_tco2'].sum() / 1e3,
                    'abatement_ktco2': df_t['abatement_tco2'].sum() / 1e3,
                })

    return pd.DataFrame(facility_data)


def create_macc_data(df):
    """Sheet 7: MACC_Data - Data for MACC curve generation sorted by MAC"""
    print("Creating MACC_Data sheet...")

    # Get 2050 data for MACC
    df_2050 = df[df['year'] == 2050].copy()

    # Only include facilities with positive abatement
    df_macc = df_2050[df_2050['abatement_tco2'] > 0].copy()

    # Calculate MAC where needed
    df_macc['mac_calculated'] = df_macc['total_cost_usd'] / df_macc['abatement_tco2']

    # Select and rename columns
    macc_cols = [
        'scenario', 'region', 'facility_id', 'company', 'product', 'process', 'technology',
        'bau_emissions_tco2', 'emissions_tco2', 'abatement_tco2',
        'total_cost_usd', 'mac_calculated'
    ]

    df_macc = df_macc[macc_cols].copy()
    df_macc = df_macc.rename(columns={
        'abatement_tco2': 'abatement_tco2',
        'mac_calculated': 'mac_usd_per_tco2'
    })

    # Sort by MAC ascending (for MACC curve)
    df_macc = df_macc.sort_values(['scenario', 'mac_usd_per_tco2'])

    # Add cumulative abatement for each scenario
    df_macc['cumulative_abatement_tco2'] = df_macc.groupby('scenario')['abatement_tco2'].cumsum()
    df_macc['cumulative_abatement_mtco2'] = df_macc['cumulative_abatement_tco2'] / 1e6

    return df_macc


def write_excel(sheets_dict, output_file):
    """Write all sheets to Excel file with formatting"""
    print(f"\nWriting Excel file: {output_file}")

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, df in sheets_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Auto-adjust column widths
            worksheet = writer.sheets[sheet_name]
            for i, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                ) + 2
                worksheet.column_dimensions[chr(65 + i) if i < 26 else f'{chr(65 + i//26 - 1)}{chr(65 + i%26)}'].width = min(max_length, 50)

            print(f"  Wrote {sheet_name}: {len(df):,} rows")

    print(f"\nExcel report saved to: {output_file}")


def main():
    """Main execution"""
    print("=" * 70)
    print("KOREA PETROCHEMICAL NET ZERO - EXCEL REPORT GENERATOR")
    print("=" * 70)

    # Load data
    df = load_results()

    # Create sheets
    sheets = {
        'Raw_Data': create_raw_data_sheet(df),
        'Assumptions': create_assumptions_sheet(),
        'Scenario_Summary': create_scenario_summary(df),
        'Regional_Summary': create_regional_summary(df),
        'Technology_Deployment': create_technology_deployment(df),
        'Facility_Summary': create_facility_summary(df),
        'MACC_Data': create_macc_data(df),
    }

    # Write Excel
    write_excel(sheets, OUTPUT_FILE)

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    df_2050 = df[(df['year'] == 2050) & (df['scenario'] == 'shaheen_ncc_h2')]
    print(f"  Total facilities: {df['facility_id'].nunique()}")
    print(f"  Scenarios: {df['scenario'].nunique()}")
    print(f"  Years: {sorted(df['year'].unique())}")
    print(f"  2050 Total Abatement (shaheen_ncc_h2): {df_2050['abatement_tco2'].sum()/1e6:.2f} MtCO2")
    print(f"  2050 Total CAPEX (shaheen_ncc_h2): ${df_2050['capex_usd'].sum()/1e9:.2f}B")

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)

    return sheets


if __name__ == '__main__':
    sheets = main()
