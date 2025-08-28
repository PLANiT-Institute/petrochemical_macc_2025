"""
Korean Petrochemical MACC Database Structure Visualization
==========================================================

This script creates comprehensive visualizations and documentation for each sheet
in the Korea_Petrochemical_MACC_Database.xlsx without modifying any data.

Purpose: Document and visualize the current data structure for understanding.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for better looking plots
plt.style.use('default')
sns.set_palette("husl")

def load_excel_data():
    """Load all sheets from the Excel database"""
    excel_path = Path("../data/Korea_Petrochemical_MACC_Database.xlsx")
    
    if not excel_path.exists():
        excel_path = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    
    print(f"Loading data from: {excel_path}")
    
    # Load all sheets
    excel_data = pd.read_excel(excel_path, sheet_name=None)
    
    print("\nAvailable sheets:")
    for sheet_name in excel_data.keys():
        print(f"  - {sheet_name}: {excel_data[sheet_name].shape}")
    
    return excel_data

def visualize_baseline_consumption(df):
    """Visualize BaselineConsumption_2023 sheet structure"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('BaselineConsumption_2023: Current Process Structure', fontsize=16, fontweight='bold')
    
    # 1. Production capacity by technology group and band
    capacity_pivot = df.pivot_table(
        values='Activity_kt_product', 
        index='TechGroup', 
        columns='Band', 
        aggfunc='sum'
    )
    
    sns.heatmap(capacity_pivot, annot=True, fmt='.0f', cmap='Blues', ax=axes[0,0])
    axes[0,0].set_title('Production Capacity (kt/year)')
    axes[0,0].set_xlabel('Technology Band')
    axes[0,0].set_ylabel('Process Type')
    
    # 2. Natural gas consumption patterns
    ng_data = df.groupby('TechGroup')['NaturalGas_GJ_per_t'].mean()
    ng_data.plot(kind='bar', ax=axes[0,1], color='orange')
    axes[0,1].set_title('Natural Gas Consumption by Process')
    axes[0,1].set_ylabel('GJ per tonne product')
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # 3. Electricity consumption patterns
    elec_data = df.groupby('TechGroup')['Electricity_GJ_per_t'].mean()
    elec_data.plot(kind='bar', ax=axes[1,0], color='green')
    axes[1,0].set_title('Electricity Consumption by Process')
    axes[1,0].set_ylabel('GJ per tonne product')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    # 4. Feedstock consumption overview
    feedstock_cols = ['Naphtha_t_per_t', 'LPG_t_per_t', 'Reformate_t_per_t']
    feedstock_data = df[feedstock_cols].sum()
    feedstock_data.plot(kind='pie', ax=axes[1,1], autopct='%1.1f%%')
    axes[1,1].set_title('Total Feedstock Consumption Distribution')
    axes[1,1].set_ylabel('')
    
    plt.tight_layout()
    plt.savefig('01_BaselineConsumption_Structure.png', dpi=300, bbox_inches='tight')
    plt.show()

def visualize_emission_factors_timeseries(df):
    """Visualize EmissionFactors_TimeSeries sheet structure"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('EmissionFactors_TimeSeries: Dynamic Emission Factor Evolution (2023-2050)', fontsize=16, fontweight='bold')
    
    # 1. Grid decarbonization pathway
    axes[0,0].plot(df['Year'], df['Electricity_tCO2_per_GJ'], marker='o', linewidth=3, color='red', label='Grid Electricity')
    axes[0,0].plot(df['Year'], df['Green_Hydrogen_tCO2_per_GJ'], marker='s', linewidth=3, color='green', label='Green Hydrogen')
    axes[0,0].set_title('Grid Decarbonization & Green H2')
    axes[0,0].set_ylabel('tCO2 per GJ')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # 2. Fossil fuel emission factors over time
    fossil_fuels = ['Natural_Gas_tCO2_per_GJ', 'Fuel_Oil_tCO2_per_GJ']
    for fuel in fossil_fuels:
        axes[0,1].plot(df['Year'], df[fuel], marker='o', label=fuel.replace('_tCO2_per_GJ', ''))
    axes[0,1].set_title('Fossil Fuel Emission Factors')
    axes[0,1].set_ylabel('tCO2 per GJ')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # 3. Feedstock emission factors
    feedstock_cols = ['Naphtha_tCO2_per_t', 'LPG_tCO2_per_t', 'Reformate_tCO2_per_t']
    for col in feedstock_cols:
        axes[1,0].plot(df['Year'], df[col], marker='o', label=col.replace('_tCO2_per_t', ''))
    axes[1,0].set_title('Feedstock Emission Factors')
    axes[1,0].set_ylabel('tCO2 per tonne')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # 4. Emission factor comparison (2023 vs 2050)
    comparison_data = {
        'Electricity': [df['Electricity_tCO2_per_GJ'].iloc[0], df['Electricity_tCO2_per_GJ'].iloc[-1]],
        'Natural Gas': [df['Natural_Gas_tCO2_per_GJ'].iloc[0], df['Natural_Gas_tCO2_per_GJ'].iloc[-1]],
        'Green H2': [df['Green_Hydrogen_tCO2_per_GJ'].iloc[0], df['Green_Hydrogen_tCO2_per_GJ'].iloc[-1]]
    }
    
    x = np.arange(len(comparison_data))
    width = 0.35
    
    values_2023 = [comparison_data[key][0] for key in comparison_data.keys()]
    values_2050 = [comparison_data[key][1] for key in comparison_data.keys()]
    
    axes[1,1].bar(x - width/2, values_2023, width, label='2023', alpha=0.8)
    axes[1,1].bar(x + width/2, values_2050, width, label='2050', alpha=0.8)
    axes[1,1].set_title('Emission Factor Changes: 2023 vs 2050')
    axes[1,1].set_ylabel('tCO2 per GJ')
    axes[1,1].set_xticks(x)
    axes[1,1].set_xticklabels(comparison_data.keys())
    axes[1,1].legend()
    
    plt.tight_layout()
    plt.savefig('02_EmissionFactors_TimeSeries_Structure.png', dpi=300, bbox_inches='tight')
    plt.show()

def visualize_fuel_costs_timeseries(df):
    """Visualize FuelCosts_TimeSeries sheet structure"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('FuelCosts_TimeSeries: Fuel Cost Evolution & Green H2 Learning Curve (2023-2050)', fontsize=16, fontweight='bold')
    
    # 1. Green H2 cost decline trajectory
    axes[0,0].plot(df['Year'], df['Green_Hydrogen_USD_per_GJ'], marker='o', linewidth=4, color='green')
    axes[0,0].fill_between(df['Year'], df['Green_Hydrogen_USD_per_GJ'], alpha=0.3, color='green')
    axes[0,0].set_title('Green Hydrogen Cost Learning Curve')
    axes[0,0].set_ylabel('USD per GJ')
    axes[0,0].grid(True, alpha=0.3)
    axes[0,0].text(2035, df['Green_Hydrogen_USD_per_GJ'].mean(), 
                   f"${df['Green_Hydrogen_USD_per_GJ'].iloc[0]:.1f} → ${df['Green_Hydrogen_USD_per_GJ'].iloc[-1]:.1f}/GJ", 
                   fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"))
    
    # 2. All fuel cost trajectories
    fuel_cols = ['Natural_Gas_USD_per_GJ', 'Fuel_Oil_USD_per_GJ', 'Electricity_USD_per_GJ', 'Green_Hydrogen_USD_per_GJ']
    for col in fuel_cols:
        axes[0,1].plot(df['Year'], df[col], marker='o', label=col.replace('_USD_per_GJ', ''))
    axes[0,1].set_title('All Fuel Cost Evolution')
    axes[0,1].set_ylabel('USD per GJ')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # 3. Feedstock cost evolution
    feedstock_cols = ['Naphtha_USD_per_t', 'LPG_USD_per_t', 'Reformate_USD_per_t']
    for col in feedstock_cols:
        axes[1,0].plot(df['Year'], df[col], marker='o', label=col.replace('_USD_per_t', ''))
    axes[1,0].set_title('Feedstock Cost Evolution')
    axes[1,0].set_ylabel('USD per tonne')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # 4. Cost competitiveness analysis (2023 vs 2050)
    cost_comparison = {
        'Natural Gas': [df['Natural_Gas_USD_per_GJ'].iloc[0], df['Natural_Gas_USD_per_GJ'].iloc[-1]],
        'Electricity': [df['Electricity_USD_per_GJ'].iloc[0], df['Electricity_USD_per_GJ'].iloc[-1]],
        'Green H2': [df['Green_Hydrogen_USD_per_GJ'].iloc[0], df['Green_Hydrogen_USD_per_GJ'].iloc[-1]]
    }
    
    x = np.arange(len(cost_comparison))
    width = 0.35
    
    values_2023 = [cost_comparison[key][0] for key in cost_comparison.keys()]
    values_2050 = [cost_comparison[key][1] for key in cost_comparison.keys()]
    
    bars1 = axes[1,1].bar(x - width/2, values_2023, width, label='2023', alpha=0.8, color='orange')
    bars2 = axes[1,1].bar(x + width/2, values_2050, width, label='2050', alpha=0.8, color='blue')
    
    axes[1,1].set_title('Fuel Cost Competitiveness: 2023 vs 2050')
    axes[1,1].set_ylabel('USD per GJ')
    axes[1,1].set_xticks(x)
    axes[1,1].set_xticklabels(cost_comparison.keys())
    axes[1,1].legend()
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        axes[1,1].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                      f'${height:.1f}', ha='center', va='bottom')
    for bar in bars2:
        height = bar.get_height()
        axes[1,1].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                      f'${height:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('03_FuelCosts_TimeSeries_Structure.png', dpi=300, bbox_inches='tight')
    plt.show()

def visualize_regional_facilities(df):
    """Visualize RegionalFacilities sheet structure"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('RegionalFacilities: Spatial Distribution & Facility Characteristics', fontsize=16, fontweight='bold')
    
    # 1. Regional capacity distribution
    regional_capacity = df.groupby('Region')[['NCC_Capacity_kt_per_year', 'BTX_Capacity_kt_per_year', 'C4_Capacity_kt_per_year']].sum()
    regional_capacity.plot(kind='bar', stacked=True, ax=axes[0,0])
    axes[0,0].set_title('Production Capacity by Region')
    axes[0,0].set_ylabel('Capacity (kt/year)')
    axes[0,0].tick_params(axis='x', rotation=45)
    axes[0,0].legend(title='Process Type')
    
    # 2. Infrastructure readiness vs technical readiness
    scatter = axes[0,1].scatter(df['Infrastructure_Score'], df['TechnicalReadiness_Level'], 
                               s=df['NCC_Capacity_kt_per_year']/10, alpha=0.6, c=df.index, cmap='viridis')
    axes[0,1].set_xlabel('Infrastructure Score (1-10)')
    axes[0,1].set_ylabel('Technical Readiness Level (1-9)')
    axes[0,1].set_title('Facility Readiness Assessment\n(Bubble size = NCC Capacity)')
    
    # Add facility labels
    for i, row in df.iterrows():
        axes[0,1].annotate(f"{row['Company'][:6]}", 
                          (row['Infrastructure_Score'], row['TechnicalReadiness_Level']),
                          xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # 3. Regional cost characteristics
    cost_data = df.groupby('Region')[['Labor_Cost_Index', 'Electricity_Price_USD_per_MWh']].mean()
    
    x = np.arange(len(cost_data.index))
    width = 0.35
    
    bars1 = axes[1,0].bar(x - width/2, cost_data['Labor_Cost_Index'], width, label='Labor Cost Index', alpha=0.8)
    
    # Create second y-axis for electricity price
    ax2 = axes[1,0].twinx()
    bars2 = ax2.bar(x + width/2, cost_data['Electricity_Price_USD_per_MWh'], width, 
                   label='Electricity Price', alpha=0.8, color='orange')
    
    axes[1,0].set_xlabel('Region')
    axes[1,0].set_ylabel('Labor Cost Index', color='blue')
    ax2.set_ylabel('Electricity Price (USD/MWh)', color='orange')
    axes[1,0].set_title('Regional Cost Characteristics')
    axes[1,0].set_xticks(x)
    axes[1,0].set_xticklabels(cost_data.index)
    
    # 4. Company distribution by region
    company_region = df.groupby(['Region', 'Company']).size().unstack(fill_value=0)
    company_region.plot(kind='bar', stacked=True, ax=axes[1,1])
    axes[1,1].set_title('Company Distribution by Region')
    axes[1,1].set_ylabel('Number of Facilities')
    axes[1,1].tick_params(axis='x', rotation=45)
    axes[1,1].legend(title='Company', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig('04_RegionalFacilities_Structure.png', dpi=300, bbox_inches='tight')
    plt.show()

def visualize_alternative_technologies(df):
    """Visualize AlternativeTechnologies sheet structure"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('AlternativeTechnologies: Technology Portfolio & Maturity Analysis', fontsize=16, fontweight='bold')
    
    # 1. Technology readiness by category and process
    trl_data = df.groupby(['TechnologyCategory', 'TechGroup'])['TechnicalReadiness'].mean().unstack(fill_value=0)
    sns.heatmap(trl_data, annot=True, fmt='.1f', cmap='RdYlGn', ax=axes[0,0])
    axes[0,0].set_title('Technology Readiness Level (TRL) by Category & Process')
    axes[0,0].set_xlabel('Process Type')
    axes[0,0].set_ylabel('Technology Category')
    
    # 2. Commercialization timeline
    comm_years = df['CommercialYear'].value_counts().sort_index()
    comm_years.plot(kind='bar', ax=axes[0,1], color='skyblue')
    axes[0,1].set_title('Technology Commercialization Timeline')
    axes[0,1].set_xlabel('Commercial Year')
    axes[0,1].set_ylabel('Number of Technologies')
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # 3. Fuel consumption profiles comparison
    fuel_cols = ['NaturalGas_GJ_per_t', 'Electricity_GJ_per_t', 'Hydrogen_GJ_per_t']
    fuel_data = df[fuel_cols].mean()
    
    colors = ['orange', 'green', 'blue']
    wedges, texts, autotexts = axes[1,0].pie(fuel_data, labels=fuel_data.index, autopct='%1.1f%%', 
                                            colors=colors, explode=[0.05, 0.05, 0.1])
    axes[1,0].set_title('Average Fuel Consumption Profile\n(Alternative Technologies)')
    
    # 4. Technology distribution by process type
    tech_dist = df.groupby(['TechGroup', 'TechnologyCategory']).size().unstack(fill_value=0)
    tech_dist.plot(kind='bar', ax=axes[1,1])
    axes[1,1].set_title('Technology Distribution by Process Type')
    axes[1,1].set_ylabel('Number of Technologies')
    axes[1,1].tick_params(axis='x', rotation=45)
    axes[1,1].legend(title='Technology Category', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig('05_AlternativeTechnologies_Structure.png', dpi=300, bbox_inches='tight')
    plt.show()

def visualize_alternative_costs(df):
    """Visualize AlternativeCosts sheet structure"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('AlternativeCosts: Technology Economics & Investment Analysis', fontsize=16, fontweight='bold')
    
    # 1. CAPEX distribution by technology
    df['CAPEX_Million_USD_per_kt_capacity'].plot(kind='hist', bins=15, ax=axes[0,0], alpha=0.7, color='blue')
    axes[0,0].set_title('CAPEX Distribution\n(Million USD per kt capacity)')
    axes[0,0].set_xlabel('CAPEX (Million USD/kt)')
    axes[0,0].set_ylabel('Number of Technologies')
    axes[0,0].grid(True, alpha=0.3)
    
    # Add mean line
    mean_capex = df['CAPEX_Million_USD_per_kt_capacity'].mean()
    axes[0,0].axvline(mean_capex, color='red', linestyle='--', linewidth=2, 
                     label=f'Mean: ${mean_capex:.1f}M/kt')
    axes[0,0].legend()
    
    # 2. OPEX vs CAPEX correlation
    scatter = axes[0,1].scatter(df['CAPEX_Million_USD_per_kt_capacity'], df['OPEX_Delta_USD_per_t'], 
                               s=60, alpha=0.6, c=df.index, cmap='viridis')
    axes[0,1].set_xlabel('CAPEX (Million USD per kt capacity)')
    axes[0,1].set_ylabel('OPEX Delta (USD per tonne)')
    axes[0,1].set_title('Investment Trade-off: CAPEX vs OPEX')
    axes[0,1].grid(True, alpha=0.3)
    
    # Add trend line
    z = np.polyfit(df['CAPEX_Million_USD_per_kt_capacity'], df['OPEX_Delta_USD_per_t'], 1)
    p = np.poly1d(z)
    axes[0,1].plot(df['CAPEX_Million_USD_per_kt_capacity'], p(df['CAPEX_Million_USD_per_kt_capacity']), 
                  "r--", alpha=0.8, linewidth=2)
    
    # 3. Technology lifetime distribution
    lifetime_dist = df['Lifetime_years'].value_counts().sort_index()
    lifetime_dist.plot(kind='bar', ax=axes[1,0], color='green', alpha=0.7)
    axes[1,0].set_title('Technology Lifetime Distribution')
    axes[1,0].set_xlabel('Lifetime (years)')
    axes[1,0].set_ylabel('Number of Technologies')
    axes[1,0].tick_params(axis='x', rotation=0)
    
    # 4. Maintenance cost analysis
    maintenance_stats = df.groupby(pd.cut(df['CAPEX_Million_USD_per_kt_capacity'], bins=5))['MaintenanceCost_Pct'].mean()
    maintenance_stats.plot(kind='bar', ax=axes[1,1], color='orange', alpha=0.7)
    axes[1,1].set_title('Maintenance Cost vs CAPEX Categories')
    axes[1,1].set_ylabel('Maintenance Cost (% of CAPEX)')
    axes[1,1].set_xlabel('CAPEX Categories (Million USD/kt)')
    axes[1,1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('06_AlternativeCosts_Structure.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_data_overview_summary(excel_data):
    """Create a comprehensive overview of the entire database structure"""
    fig, axes = plt.subplots(3, 2, figsize=(16, 18))
    fig.suptitle('Korean Petrochemical MACC Database: Complete Structure Overview', fontsize=18, fontweight='bold')
    
    # 1. Database structure overview
    sheet_info = []
    for sheet_name, df in excel_data.items():
        sheet_info.append({
            'Sheet': sheet_name,
            'Rows': len(df),
            'Columns': len(df.columns),
            'Data_Points': len(df) * len(df.columns)
        })
    
    sheet_df = pd.DataFrame(sheet_info)
    sheet_df.set_index('Sheet')['Data_Points'].plot(kind='barh', ax=axes[0,0], color='steelblue')
    axes[0,0].set_title('Database Size by Sheet\n(Total Data Points)')
    axes[0,0].set_xlabel('Number of Data Points')
    
    # 2. Time series coverage (for time-dependent sheets)
    time_sheets = ['EmissionFactors_TimeSeries', 'FuelCosts_TimeSeries']
    if all(sheet in excel_data for sheet in time_sheets):
        years = excel_data['EmissionFactors_TimeSeries']['Year']
        axes[0,1].plot(years, [1]*len(years), 'o-', markersize=8, linewidth=3, color='green')
        axes[0,1].set_title('Time Series Coverage\n(2023-2050)')
        axes[0,1].set_xlabel('Year')
        axes[0,1].set_ylabel('Coverage')
        axes[0,1].set_ylim(0.5, 1.5)
        axes[0,1].grid(True, alpha=0.3)
        
        # Add milestone markers
        milestones = [2030, 2040, 2050]
        for milestone in milestones:
            if milestone in years.values:
                axes[0,1].annotate(f'{milestone}\nTarget Year', xy=(milestone, 1), 
                                  xytext=(milestone, 1.3), ha='center',
                                  arrowprops=dict(arrowstyle='->', color='red'))
    
    # 3. Technology portfolio overview
    if 'AlternativeTechnologies' in excel_data:
        tech_df = excel_data['AlternativeTechnologies']
        tech_categories = tech_df['TechnologyCategory'].value_counts()
        tech_categories.plot(kind='pie', ax=axes[1,0], autopct='%1.1f%%')
        axes[1,0].set_title('Technology Portfolio Distribution')
        axes[1,0].set_ylabel('')
    
    # 4. Regional capacity overview
    if 'RegionalFacilities' in excel_data:
        facilities_df = excel_data['RegionalFacilities']
        regional_total = facilities_df.groupby('Region')[['NCC_Capacity_kt_per_year', 'BTX_Capacity_kt_per_year', 'C4_Capacity_kt_per_year']].sum().sum(axis=1)
        regional_total.plot(kind='bar', ax=axes[1,1], color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        axes[1,1].set_title('Total Production Capacity by Region')
        axes[1,1].set_ylabel('Total Capacity (kt/year)')
        axes[1,1].tick_params(axis='x', rotation=45)
    
    # 5. Cost evolution summary
    if 'FuelCosts_TimeSeries' in excel_data:
        costs_df = excel_data['FuelCosts_TimeSeries']
        key_fuels = ['Natural_Gas_USD_per_GJ', 'Electricity_USD_per_GJ', 'Green_Hydrogen_USD_per_GJ']
        for fuel in key_fuels:
            axes[2,0].plot(costs_df['Year'], costs_df[fuel], marker='o', label=fuel.replace('_USD_per_GJ', ''))
        axes[2,0].set_title('Key Fuel Cost Evolution (2023-2050)')
        axes[2,0].set_ylabel('USD per GJ')
        axes[2,0].legend()
        axes[2,0].grid(True, alpha=0.3)
    
    # 6. Emission factor evolution summary
    if 'EmissionFactors_TimeSeries' in excel_data:
        ef_df = excel_data['EmissionFactors_TimeSeries']
        key_factors = ['Natural_Gas_tCO2_per_GJ', 'Electricity_tCO2_per_GJ', 'Green_Hydrogen_tCO2_per_GJ']
        for factor in key_factors:
            axes[2,1].plot(ef_df['Year'], ef_df[factor], marker='o', label=factor.replace('_tCO2_per_GJ', ''))
        axes[2,1].set_title('Key Emission Factor Evolution (2023-2050)')
        axes[2,1].set_ylabel('tCO2 per GJ')
        axes[2,1].legend()
        axes[2,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('00_Database_Overview.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return sheet_df

def generate_summary_report(excel_data, sheet_summary):
    """Generate a comprehensive text summary of the database structure"""
    
    report = """
KOREAN PETROCHEMICAL MACC DATABASE STRUCTURE REPORT
==================================================
Generated: """ + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + """

DATABASE OVERVIEW:
-----------------
Total Sheets: """ + str(len(excel_data)) + """
Total Data Points: """ + str(sheet_summary['Data_Points'].sum()) + """
Time Coverage: 2023-2050 (28 years)

SHEET-BY-SHEET ANALYSIS:
-----------------------
"""
    
    for sheet_name, df in excel_data.items():
        report += f"""
{sheet_name}:
  • Dimensions: {len(df)} rows × {len(df.columns)} columns
  • Key Columns: {', '.join(df.columns[:5].tolist())}{'...' if len(df.columns) > 5 else ''}
  • Data Types: {df.dtypes.value_counts().to_dict()}
  • Missing Values: {df.isnull().sum().sum()} total
"""
        
        # Add specific insights for each sheet
        if 'BaselineConsumption' in sheet_name:
            total_capacity = df['Activity_kt_product'].sum()
            report += f"  • Total Production Capacity: {total_capacity:,.0f} kt/year\n"
            report += f"  • Process Types: {df['TechGroup'].nunique()} ({', '.join(df['TechGroup'].unique())})\n"
            report += f"  • Technology Bands: {df['Band'].nunique()} ({', '.join(df['Band'].unique())})\n"
        
        elif 'EmissionFactors_TimeSeries' in sheet_name:
            years_covered = df['Year'].max() - df['Year'].min() + 1
            report += f"  • Time Coverage: {years_covered} years ({df['Year'].min()}-{df['Year'].max()})\n"
            grid_reduction = ((df['Electricity_tCO2_per_GJ'].iloc[0] - df['Electricity_tCO2_per_GJ'].iloc[-1]) / df['Electricity_tCO2_per_GJ'].iloc[0]) * 100
            report += f"  • Grid Decarbonization: {grid_reduction:.1f}% reduction by 2050\n"
        
        elif 'FuelCosts_TimeSeries' in sheet_name:
            h2_cost_reduction = ((df['Green_Hydrogen_USD_per_GJ'].iloc[0] - df['Green_Hydrogen_USD_per_GJ'].iloc[-1]) / df['Green_Hydrogen_USD_per_GJ'].iloc[0]) * 100
            report += f"  • Green H2 Cost Decline: {h2_cost_reduction:.1f}% reduction by 2050\n"
            report += f"  • H2 Cost Range: ${df['Green_Hydrogen_USD_per_GJ'].min():.1f} - ${df['Green_Hydrogen_USD_per_GJ'].max():.1f} per GJ\n"
        
        elif 'RegionalFacilities' in sheet_name:
            report += f"  • Facilities: {len(df)} total across {df['Region'].nunique()} regions\n"
            report += f"  • Regions: {', '.join(df['Region'].unique())}\n"
            report += f"  • Companies: {df['Company'].nunique()} ({', '.join(df['Company'].unique())})\n"
        
        elif 'AlternativeTechnologies' in sheet_name:
            report += f"  • Technologies: {len(df)} alternative technologies\n"
            report += f"  • Categories: {df['TechnologyCategory'].nunique()} ({', '.join(df['TechnologyCategory'].unique())})\n"
            avg_trl = df['TechnicalReadiness'].mean()
            report += f"  • Average TRL: {avg_trl:.1f}/9\n"
        
        elif 'AlternativeCosts' in sheet_name:
            avg_capex = df['CAPEX_Million_USD_per_kt_capacity'].mean()
            report += f"  • Average CAPEX: ${avg_capex:.1f}M per kt capacity\n"
            avg_lifetime = df['Lifetime_years'].mean()
            report += f"  • Average Technology Lifetime: {avg_lifetime:.0f} years\n"
    
    report += """

KEY DATA RELATIONSHIPS:
----------------------
• Baseline consumption profiles → Alternative technology profiles (consumption reduction analysis)
• Regional facilities → Technology deployment → Investment requirements
• Time-series emission factors → Dynamic emission calculations
• Time-series fuel costs → Economic optimization pathways
• Technology readiness levels → Commercialization timeline → Deployment feasibility
• Policy targets → Optimization constraints → Technology selection priorities

RESEARCH APPLICATIONS:
---------------------
• Industrial decarbonization pathway optimization
• Technology portfolio analysis and selection
• Regional deployment strategy development  
• Green hydrogen integration feasibility assessment
• Korean NDC compliance analysis
• Investment requirement forecasting
• Policy scenario modeling and sensitivity analysis

MODEL CAPABILITIES:
------------------
• Dual approach: Simulation (realistic) + Optimization (target-driven)
• Facility-level granularity with regional characteristics
• Time-dynamic parameters (2023-2050)
• Multi-fuel/feedstock consumption modeling
• Technology readiness-based deployment timing
• Green hydrogen cost learning curve integration
• Korean energy transition pathway alignment
"""
    
    # Save the report
    with open('Database_Structure_Report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)

def validate_data_alignment(excel_data):
    """Validate alignment between BaselineConsumption_2023 and RegionalFacilities"""
    print("\nDATA ALIGNMENT VALIDATION:")
    print("-" * 40)
    
    baseline_df = excel_data['BaselineConsumption_2023']
    facilities_df = excel_data['RegionalFacilities']
    
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
    
    return baseline_totals, facilities_totals

def main():
    """Main function to generate all visualizations and documentation"""
    print("Korean Petrochemical MACC Database Structure Documentation")
    print("=" * 60)
    
    # Load data
    excel_data = load_excel_data()
    
    # Validate data alignment first
    validate_data_alignment(excel_data)
    
    # Generate overview first
    print("\n1. Creating database overview...")
    sheet_summary = create_data_overview_summary(excel_data)
    
    # Generate individual sheet visualizations
    print("\n2. Creating individual sheet visualizations...")
    
    if 'BaselineConsumption_2023' in excel_data:
        print("   - BaselineConsumption_2023...")
        visualize_baseline_consumption(excel_data['BaselineConsumption_2023'])
    
    if 'EmissionFactors_TimeSeries' in excel_data:
        print("   - EmissionFactors_TimeSeries...")
        visualize_emission_factors_timeseries(excel_data['EmissionFactors_TimeSeries'])
    
    if 'FuelCosts_TimeSeries' in excel_data:
        print("   - FuelCosts_TimeSeries...")
        visualize_fuel_costs_timeseries(excel_data['FuelCosts_TimeSeries'])
    
    if 'RegionalFacilities' in excel_data:
        print("   - RegionalFacilities...")
        visualize_regional_facilities(excel_data['RegionalFacilities'])
    
    if 'AlternativeTechnologies' in excel_data:
        print("   - AlternativeTechnologies...")
        visualize_alternative_technologies(excel_data['AlternativeTechnologies'])
    
    if 'AlternativeCosts' in excel_data:
        print("   - AlternativeCosts...")
        visualize_alternative_costs(excel_data['AlternativeCosts'])
    
    # Generate summary report
    print("\n3. Creating comprehensive summary report...")
    generate_summary_report(excel_data, sheet_summary)
    
    print("\n" + "=" * 60)
    print("Documentation complete! Files saved in 'baseline/' folder:")
    print("  • 00_Database_Overview.png")
    print("  • 01_BaselineConsumption_Structure.png") 
    print("  • 02_EmissionFactors_TimeSeries_Structure.png")
    print("  • 03_FuelCosts_TimeSeries_Structure.png")
    print("  • 04_RegionalFacilities_Structure.png")
    print("  • 05_AlternativeTechnologies_Structure.png")
    print("  • 06_AlternativeCosts_Structure.png")
    print("  • Database_Structure_Report.txt")
    print("=" * 60)

if __name__ == "__main__":
    main()