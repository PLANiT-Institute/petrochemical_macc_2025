
import sys
import pandas as pd
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.utils import save_figure_data
from modules.figure_style import apply_style, save_figure

# Path configuration - works when run from project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'outputs'

def main():
    # File paths
    asset_file = DATA_DIR / 'assets/facility_database_with_shaheen.csv'
    emission_factors_file = DATA_DIR / 'assumptions/emission_factors.csv'
    benchmarks_file = DATA_DIR / 'assumptions/product_benchmarks.csv'

    # Load data
    print("Loading data...")
    df_assets = pd.read_csv(asset_file)
    df_factors = pd.read_csv(emission_factors_file)
    df_benchmarks = pd.read_csv(benchmarks_file)

    # 1. Prepare Emission Factors
    # Create a dictionary for easy lookup: {fuel: factor}
    # Priority: tCO2_per_GJ, then tCO2_per_kWh
    factors = {}
    for _, row in df_factors.iterrows():
        fuel = row['fuel']
        if pd.notna(row['tCO2_per_GJ']):
            factors[fuel] = {'value': row['tCO2_per_GJ'], 'unit': 'tCO2/GJ'}
        elif pd.notna(row['tCO2_per_kWh']):
            factors[fuel] = {'value': row['tCO2_per_kWh'], 'unit': 'tCO2/kWh'}
    
    print("Emission Factors:", factors)

    # 2. Merge Assets with Benchmarks
    # Merge on product and process
    df_merged = pd.merge(df_assets, df_benchmarks, on=['product', 'process'], how='left')

    # Check for unmerged rows
    unmerged = df_merged[df_merged['Electricity_kWh_per_tonne'].isna()]
    if not unmerged.empty:
        print(f"Warning: {len(unmerged)} rows could not be matched with benchmarks.")
        print(unmerged[['product', 'process']].drop_duplicates())
    
    # 3. Calculate Energy and Emissions
    # We need to iterate over known fuel types in benchmarks
    # Benchmark cols: Naphtha_GJ_per_tonne, Electricity_kWh_per_tonne, LNG_GJ_per_tonne, Fuel_Gas_GJ_per_tonne, ...
    
    fuel_cols = [c for c in df_benchmarks.columns if '_per_tonne' in c]
    
    # Initialize total emission column
    df_merged['Total_Emission_tCO2'] = 0.0
    df_merged['Total_Energy_TJ'] = 0.0 # Just for reference, summing GJ and MWh->GJ

    for col in fuel_cols:
        fuel_type = col.replace('_GJ_per_tonne', '').replace('_kWh_per_tonne', '')
        
        # Calculate Total Energy Consumption for this fuel
        # capacity is in kt (1000 tonnes) -> convert to tonnes: * 1000
        production_tonnes = df_merged['capacity_kt'] * 1000
        
        if 'kWh' in col:
            # Electricity
            # Energy in kWh
            energy_kwh = production_tonnes * df_merged[col]
            df_merged[f'Energy_{fuel_type}_kWh'] = energy_kwh
            
            # Emissions
            if fuel_type in factors and factors[fuel_type]['unit'] == 'tCO2/kWh':
                factor = factors[fuel_type]['value']
                emissions = energy_kwh * factor
                
                df_merged[f'Emission_{fuel_type}_tCO2'] = emissions
                df_merged['Total_Emission_tCO2'] += emissions.fillna(0)
            else:
                 print(f"Warning: No matching emission factor for {fuel_type} (kWh)")
            
            # Add to Total Energy (TJ)
            # kWh to TJ: 1 kWh = 0.0036 GJ = 0.0000036 TJ
            df_merged['Total_Energy_TJ'] += (energy_kwh.fillna(0) * 0.0000036)
        
        else:
            # Fuel in GJ
            energy_gj = production_tonnes * df_merged[col]
            df_merged[f'Energy_{fuel_type}_GJ'] = energy_gj
            
             # Emissions
            if fuel_type in factors and factors[fuel_type]['unit'] == 'tCO2/GJ':
                factor = factors[fuel_type]['value']
                emissions = energy_gj * factor
                
                df_merged[f'Emission_{fuel_type}_tCO2'] = emissions
                df_merged['Total_Emission_tCO2'] += emissions.fillna(0)
            
            # Add to Total Energy (TJ)
            # GJ to TJ: / 1000
            df_merged['Total_Energy_TJ'] += (energy_gj.fillna(0) / 1000)


    # 4. Aggregation and Output
    
    # Save detailed results
    output_path = OUTPUT_DIR / 'energy_emission_analysis.csv'
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df_merged.to_csv(output_path, index=False)
    print(f"Detailed analysis saved to {output_path}")

    # Aggregations
    loc_agg = df_merged.groupby('location')['Total_Emission_tCO2'].sum().sort_values(ascending=False)
    comp_agg = df_merged.groupby('company')['Total_Emission_tCO2'].sum().sort_values(ascending=False)
    loc_energy_tj = df_merged.groupby('location')['Total_Energy_TJ'].sum().sort_values(ascending=False)

    # Print to console
    print("\n--- Emissions by Location (tCO2) ---")
    print(loc_agg)
    print("\n--- Emissions by Company (tCO2) ---")
    print(comp_agg)
    print("\n--- Total Energy by Location (TJ) ---")
    print(loc_energy_tj)

    # --- Visualization ---
    import matplotlib.pyplot as plt
    import seaborn as sns

    apply_style()
    
    # helper for plotting
    def save_barplot(series, title, xlabel, ylabel, filename, color_palette='viridis'):
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=series.values, y=series.index, palette=color_palette, ax=ax)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        save_path = OUTPUT_DIR / filename
        save_figure(fig, save_path)
        print(f"Saved plot: {save_path}")
        # CSV export
        tidy = pd.DataFrame({'category': series.index, 'value': series.values})
        tidy['unit'] = xlabel.split('(')[-1].rstrip(')') if '(' in xlabel else xlabel
        save_figure_data(tidy, save_path, figure_type='bar')

    # 1. Emissions by Location
    save_barplot(loc_agg, 'Total Emissions by Location', 'Emissions (tCO2)', 'Location', 'emissions_by_location.png', 'Reds_r')

    # 2. Emissions by Company
    save_barplot(comp_agg, 'Total Emissions by Company', 'Emissions (tCO2)', 'Company', 'emissions_by_company.png', 'Blues_r')

    # 3. Energy by Location
    save_barplot(loc_energy_tj, 'Total Energy Consumption by Location', 'Energy (TJ)', 'Location', 'energy_by_location.png', 'Oranges_r')

    # Save aggregated tables for report
    loc_agg.to_csv(OUTPUT_DIR / 'emissions_by_location_summary.csv')
    comp_agg.to_csv(OUTPUT_DIR / 'emissions_by_company_summary.csv')


if __name__ == "__main__":
    main()
