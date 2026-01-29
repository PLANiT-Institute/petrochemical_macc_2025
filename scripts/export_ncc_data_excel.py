#!/usr/bin/env python3
"""
Export Korea NCC Data Summary to Excel

Creates an Excel file with 4 sheets containing Korea petrochemical NCC data:
1. NCC Production by Region
2. Baseline NCC Energy Split
3. Technology Assumptions
4. Regional Grid Constraints (placeholder)

Output: outputs/korea_ncc_data_summary.xlsx
"""

import pandas as pd
from pathlib import Path


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent


def create_sheet1_ncc_production(facility_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create Sheet 1: NCC Production by Region

    Aggregates facility data by region for Ethylene, Propylene, and Butadiene.
    Uses 70% utilization rate.
    """
    # Filter for NCC products only
    ncc_products = ['Ethylene', 'Propylene', 'Butadiene']
    ncc_df = facility_df[facility_df['product'].isin(ncc_products)].copy()

    # Define regions of interest (NCC complexes)
    ncc_regions = ['Daesan Complex', 'Yeosu Complex', 'Ulsan Complex']
    ncc_df = ncc_df[ncc_df['region'].isin(ncc_regions)]

    # Aggregate by region and product
    pivot = ncc_df.pivot_table(
        values='capacity_kt',
        index='region',
        columns='product',
        aggfunc='sum',
        fill_value=0
    )

    # Reorder columns
    pivot = pivot[['Ethylene', 'Propylene', 'Butadiene']]

    # Rename columns to include units
    pivot.columns = ['Ethylene (kt)', 'Propylene (kt)', 'Butadiene (kt)']

    # Add utilization column
    pivot['Utilization'] = '70%'

    # Reset index to make region a column
    pivot = pivot.reset_index()
    pivot.columns = ['Region'] + list(pivot.columns[1:])

    # Reorder rows
    region_order = ['Daesan Complex', 'Yeosu Complex', 'Ulsan Complex']
    pivot['_sort'] = pivot['Region'].map({r: i for i, r in enumerate(region_order)})
    pivot = pivot.sort_values('_sort').drop('_sort', axis=1)

    # Add total row
    total_row = pd.DataFrame([{
        'Region': 'Total',
        'Ethylene (kt)': pivot['Ethylene (kt)'].sum(),
        'Propylene (kt)': pivot['Propylene (kt)'].sum(),
        'Butadiene (kt)': pivot['Butadiene (kt)'].sum(),
        'Utilization': ''
    }])
    pivot = pd.concat([pivot, total_row], ignore_index=True)

    return pivot


def create_sheet2_energy_split(benchmarks_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create Sheet 2: Baseline NCC Energy Split (Process Energy Only)

    Extracts energy consumption data for NCC products.
    """
    # Filter for NCC products with Naphtha Cracker process
    ncc_products = ['Ethylene', 'Propylene', 'Butadiene']
    energy_df = benchmarks_df[
        (benchmarks_df['product'].isin(ncc_products)) &
        (benchmarks_df['process'] == 'Naphtha Cracker')
    ].copy()

    # Select and rename columns
    result = pd.DataFrame({
        'Product': energy_df['product'].values,
        'Naphtha (GJ/t)': energy_df['Naphtha_GJ_per_tonne'].values,
        'LNG (GJ/t)': energy_df['LNG_GJ_per_tonne'].round(2).values,
        'Byproduct Gas (GJ/t)': energy_df['Byproduct_Gas_GJ_per_tonne'].round(2).values,
        'LPG (GJ/t)': energy_df['LPG_GJ_per_tonne'].round(2).values,
        'Electricity (kWh/t)': energy_df['Electricity_kWh_per_tonne'].round(1).values
    })

    # Reorder rows
    product_order = {'Ethylene': 0, 'Propylene': 1, 'Butadiene': 2}
    result['_sort'] = result['Product'].map(product_order)
    result = result.sort_values('_sort').drop('_sort', axis=1).reset_index(drop=True)

    return result


def create_sheet3_technology(tech_df: pd.DataFrame, elec_df: pd.DataFrame) -> tuple:
    """
    Create Sheet 3: Technology Assumptions

    Returns two DataFrames:
    - Electrification technologies
    - Electrolyzer parameters
    """
    # Part 1: Electrification Technologies
    tech_data = []
    for _, row in tech_df.iterrows():
        tech_name = row['technology']
        if tech_name == 'RE_PPA':
            continue  # Skip RE_PPA as it's not an electrification technology

        # Map technology names to display names
        name_map = {
            'Heat_Pump': 'Heat Pump',
            'NCC-H2': 'NCC-H2',
            'NCC-Electricity': 'NCC-Electricity (eFurnace)',
            'RDH': 'RDH (RotoDynamic Heater)'
        }
        display_name = name_map.get(tech_name, tech_name)

        # Get efficiency/COP
        if pd.notna(row['cop']):
            efficiency = f"COP {row['cop']}"
        elif pd.notna(row['energy_conversion_efficiency']):
            efficiency = f"{int(row['energy_conversion_efficiency'] * 100)}%"
        else:
            efficiency = '-'

        # Application description
        app_map = {
            'Heat_Pump': 'Low-temp heat (<165°C)',
            'NCC-H2': 'H2 furnace retrofit',
            'NCC-Electricity': 'Cracker furnace',
            'RDH': 'BTX high-temp (>400°C)'
        }
        application = app_map.get(tech_name, row.get('applies_to', '-'))

        tech_data.append({
            'Technology': display_name,
            'Efficiency/COP': efficiency,
            'Application': application,
            'TRL': int(row['trl']) if pd.notna(row['trl']) else '-',
            'Available': int(row['available_year']) if pd.notna(row['available_year']) else '-'
        })

    electrification_df = pd.DataFrame(tech_data)

    # Sort by available year
    electrification_df = electrification_df.sort_values('Available').reset_index(drop=True)

    # Part 2: Electrolyzer Parameters (select key years)
    key_years = [2025, 2030, 2040, 2050]
    elec_filtered = elec_df[elec_df['year'].isin(key_years)].copy()

    electrolyzer_df = pd.DataFrame({
        'Year': elec_filtered['year'].values,
        'CAPEX ($/kW)': elec_filtered['capex_usd_per_kw'].round(2).values,
        'Efficiency (kWh/kg H2)': elec_filtered['efficiency_kwh_per_kg'].round(2).values,
        'Capacity Factor': elec_filtered['capacity_factor'].apply(lambda x: f"{int(x*100)}%").values
    })

    return electrification_df, electrolyzer_df


def create_sheet4_placeholder() -> pd.DataFrame:
    """
    Create Sheet 4: Regional Grid Constraints (Placeholder)

    Returns a DataFrame with a single note indicating data is not available.
    """
    return pd.DataFrame({
        'Note': ['Data not available in project - 11th Basic Plan regional grid constraints '
                 'not included in current model data.']
    })


def export_to_excel(output_path: Path, sheet1: pd.DataFrame, sheet2: pd.DataFrame,
                    sheet3a: pd.DataFrame, sheet3b: pd.DataFrame, sheet4: pd.DataFrame):
    """
    Export all sheets to Excel file with formatting.
    """
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sheet 1: NCC Production by Region
        sheet1.to_excel(writer, sheet_name='1. NCC Production by Region', index=False)

        # Sheet 2: Baseline Energy Split
        sheet2.to_excel(writer, sheet_name='2. Baseline Energy Split', index=False)

        # Sheet 3: Technology Assumptions (two tables)
        # Write electrification technologies first
        sheet3a.to_excel(writer, sheet_name='3. Technology Assumptions', index=False, startrow=1)

        # Add header for first table
        ws = writer.sheets['3. Technology Assumptions']
        ws.cell(row=1, column=1, value='Electrification Technologies')

        # Write electrolyzer parameters below with gap
        start_row = len(sheet3a) + 5
        ws.cell(row=start_row, column=1, value='Electrolyzer Parameters')
        sheet3b.to_excel(writer, sheet_name='3. Technology Assumptions', index=False,
                         startrow=start_row + 1, header=True)

        # Sheet 4: Regional Grid Constraints
        sheet4.to_excel(writer, sheet_name='4. Regional Grid Constraints', index=False)

    print(f"Excel file exported to: {output_path}")


def main():
    """Main function to orchestrate the export."""
    project_root = get_project_root()

    # Load source data
    facility_path = project_root / 'data' / 'assets' / 'facility_database_with_regions.csv'
    benchmarks_path = project_root / 'data' / 'assumptions' / 'product_benchmarks.csv'
    tech_path = project_root / 'data' / 'assumptions' / 'technology_parameters.csv'
    elec_path = project_root / 'data' / 'assumptions' / 'prices' / 'electrolyser_params.csv'

    print("Loading source data...")
    facility_df = pd.read_csv(facility_path)
    benchmarks_df = pd.read_csv(benchmarks_path)
    tech_df = pd.read_csv(tech_path)
    elec_df = pd.read_csv(elec_path)

    # Create sheets
    print("Creating Sheet 1: NCC Production by Region...")
    sheet1 = create_sheet1_ncc_production(facility_df)

    print("Creating Sheet 2: Baseline Energy Split...")
    sheet2 = create_sheet2_energy_split(benchmarks_df)

    print("Creating Sheet 3: Technology Assumptions...")
    sheet3a, sheet3b = create_sheet3_technology(tech_df, elec_df)

    print("Creating Sheet 4: Regional Grid Constraints (placeholder)...")
    sheet4 = create_sheet4_placeholder()

    # Export to Excel
    output_path = project_root / 'outputs' / 'korea_ncc_data_summary.xlsx'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Exporting to Excel...")
    export_to_excel(output_path, sheet1, sheet2, sheet3a, sheet3b, sheet4)

    # Print summary
    print("\n=== Export Summary ===")
    print(f"Sheet 1 - NCC Production by Region: {len(sheet1)} rows")
    print(f"Sheet 2 - Baseline Energy Split: {len(sheet2)} rows")
    print(f"Sheet 3 - Electrification Technologies: {len(sheet3a)} rows")
    print(f"Sheet 3 - Electrolyzer Parameters: {len(sheet3b)} rows")
    print(f"Sheet 4 - Regional Grid Constraints: placeholder")

    return output_path


if __name__ == '__main__':
    main()
