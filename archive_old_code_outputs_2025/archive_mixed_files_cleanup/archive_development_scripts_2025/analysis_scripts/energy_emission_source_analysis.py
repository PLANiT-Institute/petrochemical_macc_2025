#!/usr/bin/env python3
"""
Energy Emission Source Analysis for Korean Petrochemical Industry

This script analyzes emissions by energy source (naphtha, LPG, electricity)
based on the actual data structure in the Korean_Petrochemical_MACC_Model_English.xlsx file.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def load_data(data_path):
    """Load data from Excel file"""
    print("📁 Loading data from Excel file...")

    # Load all relevant sheets
    source_df = pd.read_excel(data_path, sheet_name='source_Original')
    ci_df = pd.read_excel(data_path, sheet_name='CI_Corrected')
    utilities_df = pd.read_excel(data_path, sheet_name='utilities_Original')

    print(f"✅ Loaded {len(source_df)} facility records")
    print(f"✅ Loaded {len(ci_df)} carbon intensity records")
    print(f"✅ Loaded {len(utilities_df)} utility records")

    return source_df, ci_df, utilities_df

def calculate_energy_consumption(source_df, ci_df):
    """Calculate energy consumption by source for each facility"""

    # Merge source data with carbon intensity data
    merged_df = source_df.merge(
        ci_df,
        left_on=['products', 'process'],
        right_on=['Product', 'Process'],
        how='left'
    )

    # Calculate energy consumption for each energy source
    energy_sources = {
        'Naphtha_Feedstock': 'Naphtha_Feedstock_GJ_per_t',
        'Naphtha_Thermal': 'Naphtha_Thermal_GJ_per_t',
        'LNG': 'LNG_GJ_per_t',
        'LPG_Propane': 'LPG_Propane_GJ_per_t',
        'LPG_Butane': 'LPG_Butane_GJ_per_t',
        'Fuel_Gas_Mix': 'Fuel_Gas_Mix_GJ_per_t',
        'Electricity': 'Electricity_kWh_per_t'
    }

    # Convert capacity from 1000_t to t
    merged_df['capacity_t'] = merged_df['capacity_1000_t'] * 1000

    # Calculate total energy consumption for each source
    for source_name, intensity_col in energy_sources.items():
        if intensity_col in merged_df.columns:
            if source_name == 'Electricity':
                # Convert kWh to GJ (1 kWh = 0.0036 GJ)
                merged_df[f'{source_name}_GJ'] = merged_df[intensity_col] * merged_df['capacity_t'] * 0.0036
            else:
                merged_df[f'{source_name}_GJ'] = merged_df[intensity_col] * merged_df['capacity_t']

    return merged_df

def calculate_emissions(energy_df):
    """Calculate emissions from energy consumption"""

    # Emission factors (kg CO2/GJ) - typical values for Korean energy mix
    emission_factors = {
        'Naphtha_Feedstock': 70.5,  # kg CO2/GJ
        'Naphtha_Thermal': 70.5,
        'LNG': 56.1,
        'LPG_Propane': 63.1,
        'LPG_Butane': 64.2,
        'Fuel_Gas_Mix': 60.0,  # Average for mixed fuel gas
        'Electricity': 466.0  # kg CO2/GJ - Korean grid emission factor
    }

    # Calculate emissions for each energy source
    for source in emission_factors.keys():
        energy_col = f'{source}_GJ'
        emission_col = f'{source}_emissions_kg_CO2'

        if energy_col in energy_df.columns:
            energy_df[emission_col] = energy_df[energy_col] * emission_factors[source]

    # Convert to tonnes CO2
    emission_cols = [col for col in energy_df.columns if 'emissions_kg_CO2' in col]
    for col in emission_cols:
        new_col = col.replace('kg_CO2', 't_CO2')
        energy_df[new_col] = energy_df[col] / 1000

    return energy_df

def aggregate_by_energy_source(emissions_df):
    """Aggregate emissions by energy source"""

    # Define energy source categories
    energy_categories = {
        'Naphtha': ['Naphtha_Feedstock_emissions_t_CO2', 'Naphtha_Thermal_emissions_t_CO2'],
        'LPG': ['LPG_Propane_emissions_t_CO2', 'LPG_Butane_emissions_t_CO2'],
        'Natural_Gas': ['LNG_emissions_t_CO2', 'Fuel_Gas_Mix_emissions_t_CO2'],
        'Electricity': ['Electricity_emissions_t_CO2']
    }

    # Create aggregated emissions by energy source
    energy_summary = {}

    for category, columns in energy_categories.items():
        available_cols = [col for col in columns if col in emissions_df.columns]
        if available_cols:
            energy_summary[category] = emissions_df[available_cols].sum(axis=1).sum()
        else:
            energy_summary[category] = 0

    return pd.Series(energy_summary)

def create_emission_source_analysis():
    """Create comprehensive emission source analysis by energy type"""
    print("🔋 ENERGY EMISSION SOURCE ANALYSIS")
    print("=" * 80)

    try:
        # Load the English version of the data
        data_path = "../data/Korean_Petrochemical_MACC_Model_English.xlsx"
        print(f"📁 Loading data from: {data_path}")

        # Load data
        source_df, ci_df, utilities_df = load_data(data_path)

        # Calculate energy consumption
        print("⚡ Calculating energy consumption...")
        energy_df = calculate_energy_consumption(source_df, ci_df)

        # Calculate emissions
        print("💨 Calculating emissions...")
        emissions_df = calculate_emissions(energy_df)

        # Aggregate by energy source
        print("📊 Aggregating by energy source...")
        energy_summary = aggregate_by_energy_source(emissions_df)

        # Calculate total emissions
        total_emissions = energy_summary.sum()
        print(f"📊 Total industry emissions: {total_emissions/1e6:.1f} MtCO₂e/year")

        # Additional analysis by process and company
        process_analysis = emissions_df.groupby('process').agg({
            'capacity_1000_t': 'sum',
            'company': 'nunique'
        }).rename(columns={'company': 'num_companies'})

        company_analysis = emissions_df.groupby('company').agg({
            'capacity_1000_t': 'sum',
            'products': 'nunique'
        }).rename(columns={'products': 'num_products'}).sort_values('capacity_1000_t', ascending=False)

        # Create comprehensive visualization
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Korean Petrochemical Industry - Energy Emission Sources Analysis', fontsize=16, fontweight='bold')

        # Set up colors
        colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99']

        # 1. Emission Share by Energy Source (Pie Chart)
        energy_sources = list(energy_summary.index)
        emission_shares = list(energy_summary.values)

        wedges, texts, autotexts = ax1.pie(emission_shares, labels=energy_sources, autopct='%1.1f%%',
                                          colors=colors, startangle=90)
        ax1.set_title('Annual CO₂ Emissions by Energy Source\n(Total: {:.1f} MtCO₂e/year)'.format(total_emissions/1e6))

        # 2. Emissions by Process Type (Bar Chart)
        process_emissions = emissions_df.groupby('process').agg({
            col: 'sum' for col in emissions_df.columns if 'emissions_t_CO2' in col
        }).fillna(0)

        emission_cols = [col for col in process_emissions.columns if 'emissions_t_CO2' in col]
        process_total = process_emissions[emission_cols].sum(axis=1)

        ax2.bar(process_total.index, process_total.values, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax2.set_title('Total Emissions by Process Type')
        ax2.set_ylabel('Emissions (Million tonnes CO₂/year)')
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
        ax2.tick_params(axis='x', rotation=45)

        # 3. Top Companies by Emissions (Horizontal Bar)
        company_emissions = emissions_df.groupby('company').agg({
            col: 'sum' for col in emissions_df.columns if 'emissions_t_CO2' in col
        }).fillna(0)

        company_total = company_emissions[emission_cols].sum(axis=1).sort_values(ascending=True)
        top_companies = company_total.tail(8)  # Top 8 companies

        ax3.barh(range(len(top_companies)), top_companies.values, color='skyblue')
        ax3.set_title('Top 8 Companies by Total Emissions')
        ax3.set_xlabel('Emissions (Million tonnes CO₂/year)')
        ax3.set_yticks(range(len(top_companies)))
        ax3.set_yticklabels(top_companies.index)
        ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))

        # 4. Energy Source Breakdown by Process (Stacked Bar)
        process_energy = {}
        for process in emissions_df['process'].unique():
            process_data = emissions_df[emissions_df['process'] == process]
            energy_totals = {}

            for category, columns in {
                'Naphtha': ['Naphtha_Feedstock_emissions_t_CO2', 'Naphtha_Thermal_emissions_t_CO2'],
                'LPG': ['LPG_Propane_emissions_t_CO2', 'LPG_Butane_emissions_t_CO2'],
                'Natural_Gas': ['LNG_emissions_t_CO2', 'Fuel_Gas_Mix_emissions_t_CO2'],
                'Electricity': ['Electricity_emissions_t_CO2']
            }.items():
                available_cols = [col for col in columns if col in process_data.columns]
                if available_cols:
                    energy_totals[category] = process_data[available_cols].sum().sum()
                else:
                    energy_totals[category] = 0

            process_energy[process] = energy_totals

        # Convert to DataFrame for plotting
        process_energy_df = pd.DataFrame(process_energy).fillna(0)

        # Create stacked bar chart
        bottom = np.zeros(len(process_energy_df.columns))

        for i, (energy_source, color) in enumerate(zip(process_energy_df.index, colors)):
            ax4.bar(process_energy_df.columns, process_energy_df.loc[energy_source],
                   bottom=bottom, label=energy_source, color=color)
            bottom += process_energy_df.loc[energy_source]

        ax4.set_title('Emissions by Energy Source and Process')
        ax4.set_ylabel('Emissions (Million tonnes CO₂/year)')
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
        ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        # Save the visualization
        output_path = Path("../outputs/energy_emission_source_analysis.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"📊 Visualization saved: {output_path}")

        # Create detailed analysis report
        energy_summary_df = pd.DataFrame({
            'Energy_Source': energy_summary.index,
            'Annual_Emissions_tonnes_CO2': energy_summary.values,
            'Share_percent': (energy_summary.values / total_emissions * 100).round(2)
        })

        report_path = Path("../outputs/energy_emission_source_report.csv")
        energy_summary_df.to_csv(report_path, index=False)
        print(f"📋 Report saved: {report_path}")

        # Save process and company analysis
        process_analysis.to_csv(Path("../outputs/process_analysis.csv"))
        company_analysis.to_csv(Path("../outputs/company_analysis.csv"))

        # Summary statistics
        print(f"\n🎯 KEY FINDINGS:")
        print(f"   Total Industry Emissions: {total_emissions/1e6:.1f} MtCO₂e/year")
        print(f"   Top Emission Source: {energy_summary.idxmax()} ({energy_summary.max()/1e6:.1f} MtCO₂e)")
        print(f"   Total Production Capacity: {emissions_df['capacity_1000_t'].sum():.0f} thousand tonnes/year")

        # Process-specific insights
        print(f"\n🏭 PROCESS INSIGHTS:")
        for process, data in process_analysis.iterrows():
            print(f"   {process}: {data['capacity_1000_t']:,.0f} kt capacity, {data['num_companies']:.0f} companies")

        # Energy source breakdown
        print(f"\n⚡ ENERGY SOURCE BREAKDOWN:")
        for source, emissions in energy_summary.items():
            share = emissions / total_emissions * 100
            print(f"   {source:12}: {emissions/1e6:6.2f} MtCO₂e ({share:5.1f}%)")

        plt.show()
        return output_path, report_path

    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("🚀 STARTING ENERGY EMISSION SOURCE ANALYSIS")
    output_viz, output_report = create_emission_source_analysis()
    print(f"\n✅ ANALYSIS COMPLETE!")
    print(f"📊 Visualization: {output_viz}")
    print(f"📋 Report: {output_report}")