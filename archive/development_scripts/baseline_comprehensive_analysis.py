"""
Comprehensive Baseline Analysis for Korean Petrochemical MACC Model
==================================================================

This script provides comprehensive baseline analysis including:
1. Emission intensity analysis
2. Price projections for main alternative technologies
3. Current baseline emission shares by technologies and regions
4. Tables and graphs for alternative technologies
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
plt.style.use('default')
sns.set_palette("husl")

def load_updated_database():
    """Load the updated Excel database"""
    excel_path = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    
    print("LOADING UPDATED DATABASE")
    print("=" * 50)
    print(f"Path: {excel_path}")
    
    # Load all sheets
    excel_data = pd.read_excel(excel_path, sheet_name=None)
    
    print(f"\nSheets loaded:")
    for sheet_name, df in excel_data.items():
        print(f"  • {sheet_name}: {df.shape[0]} rows × {df.shape[1]} columns")
    
    return excel_data

def calculate_baseline_emissions_detailed(excel_data):
    """Calculate detailed baseline emissions by facility, technology, and region"""
    print("\n" + "=" * 50)
    print("DETAILED BASELINE EMISSIONS CALCULATION")
    print("=" * 50)
    
    consumption_df = excel_data['FacilityBaselineConsumption_2023']
    facilities_df = excel_data['RegionalFacilities']
    ef_df = excel_data['EmissionFactors_TimeSeries']
    
    # Get 2023 emission factors
    ef_2023 = ef_df[ef_df['Year'] == 2023].iloc[0]
    
    detailed_emissions = []
    
    for _, row in consumption_df.iterrows():
        # Calculate emissions by source
        emissions_detail = {
            'FacilityID': row['FacilityID'],
            'Company': row['Company'],
            'Region': row['Region'],
            'ProcessType': row['ProcessType'],
            'Capacity_kt_per_year': row['Activity_kt_product'],
            'EfficiencyFactor': row['EfficiencyFactor']
        }
        
        # Fuel emissions (GJ-based)
        ng_consumption_gj = row['Activity_kt_product'] * row['NaturalGas_GJ_per_t'] * 1000
        emissions_detail['NG_Consumption_GJ'] = ng_consumption_gj
        emissions_detail['NG_Emissions_ktCO2'] = ng_consumption_gj * ef_2023['Natural_Gas_tCO2_per_GJ'] / 1000
        
        fo_consumption_gj = row['Activity_kt_product'] * row['FuelOil_GJ_per_t'] * 1000
        emissions_detail['FO_Consumption_GJ'] = fo_consumption_gj
        emissions_detail['FO_Emissions_ktCO2'] = fo_consumption_gj * ef_2023['Fuel_Oil_tCO2_per_GJ'] / 1000
        
        elec_consumption_gj = row['Activity_kt_product'] * row['Electricity_GJ_per_t'] * 1000
        emissions_detail['Elec_Consumption_GJ'] = elec_consumption_gj
        emissions_detail['Elec_Emissions_ktCO2'] = elec_consumption_gj * ef_2023['Electricity_tCO2_per_GJ'] / 1000
        
        # Feedstock emissions (mass-based)
        emissions_detail['Naphtha_Consumption_kt'] = row['Activity_kt_product'] * row['Naphtha_t_per_t']
        emissions_detail['Naphtha_Emissions_ktCO2'] = emissions_detail['Naphtha_Consumption_kt'] * ef_2023['Naphtha_tCO2_per_t'] / 1000
        
        emissions_detail['LPG_Consumption_kt'] = row['Activity_kt_product'] * row['LPG_t_per_t']
        emissions_detail['LPG_Emissions_ktCO2'] = emissions_detail['LPG_Consumption_kt'] * ef_2023['LPG_tCO2_per_t'] / 1000
        
        emissions_detail['Reformate_Consumption_kt'] = row['Activity_kt_product'] * row['Reformate_t_per_t']
        emissions_detail['Reformate_Emissions_ktCO2'] = emissions_detail['Reformate_Consumption_kt'] * ef_2023['Reformate_tCO2_per_t'] / 1000
        
        # Total emissions
        emissions_detail['Total_Emissions_ktCO2'] = (
            emissions_detail['NG_Emissions_ktCO2'] + 
            emissions_detail['FO_Emissions_ktCO2'] + 
            emissions_detail['Elec_Emissions_ktCO2'] +
            emissions_detail['Naphtha_Emissions_ktCO2'] + 
            emissions_detail['LPG_Emissions_ktCO2'] + 
            emissions_detail['Reformate_Emissions_ktCO2']
        )
        
        # Emission intensity
        emissions_detail['Emission_Intensity_tCO2_per_t'] = emissions_detail['Total_Emissions_ktCO2'] * 1000 / row['Activity_kt_product']
        
        detailed_emissions.append(emissions_detail)
    
    emissions_df = pd.DataFrame(detailed_emissions)
    
    # Summary statistics
    total_emissions = emissions_df['Total_Emissions_ktCO2'].sum()
    total_capacity = emissions_df['Capacity_kt_per_year'].sum()
    avg_emission_intensity = total_emissions * 1000 / total_capacity
    
    print(f"\n1. OVERALL BASELINE EMISSIONS:")
    print("-" * 30)
    print(f"  Total Emissions:        {total_emissions:,.1f} ktCO2/year")
    print(f"  Total Capacity:         {total_capacity:,.0f} kt/year")
    print(f"  Average Emission Intensity: {avg_emission_intensity:.2f} tCO2/t product")
    
    return emissions_df

def analyze_emission_shares(emissions_df):
    """Analyze emission shares by technology and region"""
    print("\n2. EMISSION SHARES ANALYSIS:")
    print("-" * 30)
    
    # By Technology (ProcessType)
    tech_emissions = emissions_df.groupby('ProcessType')['Total_Emissions_ktCO2'].sum()
    tech_capacity = emissions_df.groupby('ProcessType')['Capacity_kt_per_year'].sum()
    total_emissions = tech_emissions.sum()
    
    print(f"\nBy Technology:")
    for tech in tech_emissions.index:
        emissions = tech_emissions[tech]
        capacity = tech_capacity[tech]
        share = emissions / total_emissions * 100
        intensity = emissions * 1000 / capacity
        print(f"  {tech:3}: {emissions:6.1f} ktCO2/year ({share:4.1f}%) - {intensity:.2f} tCO2/t")
    
    # By Region
    regional_emissions = emissions_df.groupby('Region')['Total_Emissions_ktCO2'].sum()
    regional_capacity = emissions_df.groupby('Region')['Capacity_kt_per_year'].sum()
    
    print(f"\nBy Region:")
    for region in regional_emissions.index:
        emissions = regional_emissions[region]
        capacity = regional_capacity[region]
        share = emissions / total_emissions * 100
        intensity = emissions * 1000 / capacity
        print(f"  {region:6}: {emissions:6.1f} ktCO2/year ({share:4.1f}%) - {intensity:.2f} tCO2/t")
    
    # By Company
    company_emissions = emissions_df.groupby('Company')['Total_Emissions_ktCO2'].sum().sort_values(ascending=False)
    
    print(f"\nBy Company (Top 5):")
    for i, (company, emissions) in enumerate(company_emissions.head().items()):
        share = emissions / total_emissions * 100
        print(f"  {i+1}. {company}: {emissions:.1f} ktCO2/year ({share:.1f}%)")
    
    return tech_emissions, regional_emissions, company_emissions

def analyze_alternative_technologies(excel_data):
    """Comprehensive analysis of alternative technologies"""
    print("\n" + "=" * 50)
    print("ALTERNATIVE TECHNOLOGIES ANALYSIS")
    print("=" * 50)
    
    alt_tech_df = excel_data['AlternativeTechnologies']
    alt_cost_df = excel_data['AlternativeCosts']
    fuel_costs_df = excel_data['FuelCosts_TimeSeries']
    
    # Merge technology data with cost data
    tech_analysis = alt_tech_df.merge(alt_cost_df, on='TechID', how='left')
    
    print(f"\n1. TECHNOLOGY PORTFOLIO OVERVIEW:")
    print("-" * 30)
    print(f"  Total Technologies: {len(tech_analysis)}")
    print(f"  Technology Categories: {tech_analysis['TechnologyCategory'].nunique()}")
    print(f"  Process Applications: {tech_analysis['TechGroup'].nunique()}")
    
    # Technology readiness distribution
    trl_dist = tech_analysis['TechnicalReadiness'].value_counts().sort_index()
    print(f"\n  Technology Readiness Level (TRL) Distribution:")
    for trl, count in trl_dist.items():
        print(f"    TRL {trl}: {count} technologies")
    
    # Commercialization timeline
    comm_timeline = tech_analysis['CommercialYear'].value_counts().sort_index()
    print(f"\n  Commercialization Timeline:")
    for year, count in comm_timeline.items():
        print(f"    {year}: {count} technologies")
    
    return tech_analysis

def calculate_technology_price_projections(tech_analysis, fuel_costs_df):
    """Calculate price projections for main alternative technologies"""
    print("\n2. TECHNOLOGY PRICE PROJECTIONS:")
    print("-" * 30)
    
    # Key years for analysis
    key_years = [2023, 2030, 2040, 2050]
    
    # Main technology categories
    main_categories = ['E-cracker', 'H2-furnace', 'Heat pump', 'Electric heater', 'Electric motor']
    
    price_projections = []
    
    for category in main_categories:
        cat_techs = tech_analysis[tech_analysis['TechnologyCategory'] == category]
        if len(cat_techs) == 0:
            continue
            
        # Average CAPEX and OPEX for this category
        avg_capex = cat_techs['CAPEX_Million_USD_per_kt_capacity'].mean()
        avg_opex_delta = cat_techs['OPEX_Delta_USD_per_t'].mean()
        avg_lifetime = cat_techs['Lifetime_years'].mean()
        
        print(f"\n  {category}:")
        print(f"    Technologies: {len(cat_techs)}")
        print(f"    Avg CAPEX: ${avg_capex:.1f}M per kt capacity")
        print(f"    Avg OPEX Delta: ${avg_opex_delta:.1f} per tonne")
        print(f"    Avg Lifetime: {avg_lifetime:.0f} years")
        
        # Calculate fuel cost impact over time
        for year in key_years:
            year_costs = fuel_costs_df[fuel_costs_df['Year'] == year].iloc[0]
            
            # Estimate technology-specific fuel cost impact
            fuel_cost_impact = 0
            if 'Electric' in category or 'E-cracker' in category:
                # Electric technologies benefit from grid decarbonization but pay electricity costs
                fuel_cost_impact = year_costs['Electricity_USD_per_GJ'] * 2.0  # Assume 2 GJ/t average
            elif 'H2' in category:
                # Hydrogen technologies
                fuel_cost_impact = year_costs['Green_Hydrogen_USD_per_GJ'] * 3.0  # Assume 3 GJ/t average
            
            # Total cost per tonne (CAPEX annualized + OPEX + fuel)
            annual_capex = avg_capex * 1000000 / (1000 * avg_lifetime)  # USD per tonne per year
            total_cost_per_t = annual_capex + avg_opex_delta + fuel_cost_impact
            
            price_projections.append({
                'Category': category,
                'Year': year,
                'CAPEX_USD_per_t_per_year': annual_capex,
                'OPEX_Delta_USD_per_t': avg_opex_delta,
                'Fuel_Cost_USD_per_t': fuel_cost_impact,
                'Total_Cost_USD_per_t': total_cost_per_t,
                'Technologies_Count': len(cat_techs)
            })
            
            print(f"      {year}: ${total_cost_per_t:.1f}/t (CAPEX: ${annual_capex:.1f}, OPEX: ${avg_opex_delta:.1f}, Fuel: ${fuel_cost_impact:.1f})")
    
    price_proj_df = pd.DataFrame(price_projections)
    return price_proj_df

def create_comprehensive_visualizations(emissions_df, tech_emissions, regional_emissions, 
                                      company_emissions, tech_analysis, price_proj_df, excel_data):
    """Create comprehensive visualizations"""
    print("\n" + "=" * 50)
    print("CREATING COMPREHENSIVE VISUALIZATIONS")
    print("=" * 50)
    
    # Create a large figure with multiple subplots
    fig = plt.figure(figsize=(20, 24))
    
    # 1. Emission Intensity by Technology and Region
    ax1 = plt.subplot(4, 3, 1)
    tech_intensity = emissions_df.groupby('ProcessType').apply(
        lambda x: x['Total_Emissions_ktCO2'].sum() * 1000 / x['Capacity_kt_per_year'].sum()
    )
    tech_intensity.plot(kind='bar', ax=ax1, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax1.set_title('Emission Intensity by Technology', fontweight='bold')
    ax1.set_ylabel('tCO2 per tonne product')
    ax1.tick_params(axis='x', rotation=0)
    ax1.grid(True, alpha=0.3)
    
    # Add benchmark line
    ax1.axhline(y=2.5, color='red', linestyle='--', alpha=0.7, label='Industry Min (2.5)')
    ax1.axhline(y=4.0, color='red', linestyle='--', alpha=0.7, label='Industry Max (4.0)')
    ax1.legend()
    
    # Add value labels on bars
    for i, (idx, value) in enumerate(tech_intensity.items()):
        ax1.text(i, value + 0.02, f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # 2. Regional Emission Distribution
    ax2 = plt.subplot(4, 3, 2)
    regional_emissions.plot(kind='pie', ax=ax2, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Emissions by Region', fontweight='bold')
    ax2.set_ylabel('')
    
    # 3. Technology Emission Shares
    ax3 = plt.subplot(4, 3, 3)
    tech_emissions.plot(kind='pie', ax=ax3, autopct='%1.1f%%', startangle=90, 
                       colors=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax3.set_title('Emissions by Technology', fontweight='bold')
    ax3.set_ylabel('')
    
    # 4. Company Emissions Ranking
    ax4 = plt.subplot(4, 3, 4)
    top_companies = company_emissions.head(6)
    top_companies.plot(kind='bar', ax=ax4, color='steelblue')
    ax4.set_title('Top Companies by Emissions', fontweight='bold')
    ax4.set_ylabel('ktCO2 per year')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    # Add value labels
    for i, (company, value) in enumerate(top_companies.items()):
        ax4.text(i, value + 10, f'{value:.0f}', ha='center', va='bottom', fontsize=9)
    
    # 5. Technology Readiness vs Cost
    ax5 = plt.subplot(4, 3, 5)
    scatter = ax5.scatter(tech_analysis['TechnicalReadiness'], 
                         tech_analysis['CAPEX_Million_USD_per_kt_capacity'],
                         s=60, alpha=0.6, c=tech_analysis.index, cmap='viridis')
    ax5.set_xlabel('Technical Readiness Level (TRL)')
    ax5.set_ylabel('CAPEX (Million USD per kt)')
    ax5.set_title('Technology Maturity vs Investment Cost', fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # 6. Commercialization Timeline
    ax6 = plt.subplot(4, 3, 6)
    comm_timeline = tech_analysis['CommercialYear'].value_counts().sort_index()
    comm_timeline.plot(kind='bar', ax=ax6, color='orange')
    ax6.set_title('Technology Commercialization Timeline', fontweight='bold')
    ax6.set_ylabel('Number of Technologies')
    ax6.set_xlabel('Commercial Year')
    ax6.tick_params(axis='x', rotation=45)
    ax6.grid(True, alpha=0.3)
    
    # 7. Alternative Technology Price Projections
    ax7 = plt.subplot(4, 3, 7)
    main_categories = ['E-cracker', 'H2-furnace', 'Heat pump', 'Electric heater']
    for category in main_categories:
        cat_data = price_proj_df[price_proj_df['Category'] == category]
        if len(cat_data) > 0:
            ax7.plot(cat_data['Year'], cat_data['Total_Cost_USD_per_t'], 
                    marker='o', label=category, linewidth=2)
    
    ax7.set_title('Alternative Technology Cost Evolution', fontweight='bold')
    ax7.set_ylabel('Total Cost (USD per tonne)')
    ax7.set_xlabel('Year')
    ax7.legend()
    ax7.grid(True, alpha=0.3)
    
    # 8. Technology Category Distribution
    ax8 = plt.subplot(4, 3, 8)
    cat_dist = tech_analysis['TechnologyCategory'].value_counts()
    cat_dist.plot(kind='bar', ax=ax8, color='lightgreen')
    ax8.set_title('Technology Portfolio by Category', fontweight='bold')
    ax8.set_ylabel('Number of Technologies')
    ax8.tick_params(axis='x', rotation=45)
    ax8.grid(True, alpha=0.3)
    
    # 9. Facility Capacity vs Emissions
    ax9 = plt.subplot(4, 3, 9)
    facility_summary = emissions_df.groupby('FacilityID').agg({
        'Capacity_kt_per_year': 'sum',
        'Total_Emissions_ktCO2': 'sum',
        'Company': 'first'
    }).reset_index()
    
    scatter9 = ax9.scatter(facility_summary['Capacity_kt_per_year'], 
                          facility_summary['Total_Emissions_ktCO2'],
                          s=100, alpha=0.7, c=range(len(facility_summary)), cmap='tab10')
    
    ax9.set_xlabel('Total Capacity (kt/year)')
    ax9.set_ylabel('Total Emissions (ktCO2/year)')
    ax9.set_title('Facility Capacity vs Emissions', fontweight='bold')
    ax9.grid(True, alpha=0.3)
    
    # Add facility labels
    for i, row in facility_summary.iterrows():
        ax9.annotate(row['Company'][:6], 
                    (row['Capacity_kt_per_year'], row['Total_Emissions_ktCO2']),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # 10. Green H2 vs Electricity Cost Comparison
    ax10 = plt.subplot(4, 3, 10)
    fuel_costs_df = excel_data['FuelCosts_TimeSeries']
    ax10.plot(fuel_costs_df['Year'], fuel_costs_df['Green_Hydrogen_USD_per_GJ'], 
             marker='o', label='Green Hydrogen', linewidth=3, color='green')
    ax10.plot(fuel_costs_df['Year'], fuel_costs_df['Electricity_USD_per_GJ'], 
             marker='s', label='Electricity', linewidth=3, color='blue')
    ax10.plot(fuel_costs_df['Year'], fuel_costs_df['Natural_Gas_USD_per_GJ'], 
             marker='^', label='Natural Gas', linewidth=3, color='orange')
    
    ax10.set_title('Fuel Cost Evolution (2023-2050)', fontweight='bold')
    ax10.set_ylabel('Cost (USD per GJ)')
    ax10.set_xlabel('Year')
    ax10.legend()
    ax10.grid(True, alpha=0.3)
    
    # 11. Emission Factor Evolution
    ax11 = plt.subplot(4, 3, 11)
    ef_df = excel_data['EmissionFactors_TimeSeries']
    ax11.plot(ef_df['Year'], ef_df['Electricity_tCO2_per_GJ'], 
             marker='o', label='Grid Electricity', linewidth=3, color='red')
    ax11.plot(ef_df['Year'], ef_df['Green_Hydrogen_tCO2_per_GJ'], 
             marker='s', label='Green Hydrogen', linewidth=3, color='green')
    ax11.plot(ef_df['Year'], ef_df['Natural_Gas_tCO2_per_GJ'], 
             marker='^', label='Natural Gas', linewidth=3, color='orange')
    
    ax11.set_title('Emission Factor Evolution (2023-2050)', fontweight='bold')
    ax11.set_ylabel('Emission Factor (tCO2 per GJ)')
    ax11.set_xlabel('Year')
    ax11.legend()
    ax11.grid(True, alpha=0.3)
    
    # 12. Regional Technology Distribution
    ax12 = plt.subplot(4, 3, 12)
    regional_tech = emissions_df.groupby(['Region', 'ProcessType'])['Capacity_kt_per_year'].sum().unstack(fill_value=0)
    regional_tech.plot(kind='bar', stacked=True, ax=ax12, 
                      colors=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax12.set_title('Regional Technology Distribution', fontweight='bold')
    ax12.set_ylabel('Capacity (kt/year)')
    ax12.tick_params(axis='x', rotation=0)
    ax12.legend(title='Technology')
    
    plt.tight_layout()
    plt.savefig('baseline/Comprehensive_Baseline_Analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_detailed_tables(emissions_df, tech_analysis, price_proj_df):
    """Generate detailed analysis tables"""
    print("\n" + "=" * 50)
    print("GENERATING DETAILED ANALYSIS TABLES")
    print("=" * 50)
    
    # 1. Facility-level emissions table
    facility_table = emissions_df.groupby(['FacilityID', 'Company', 'Region']).agg({
        'Capacity_kt_per_year': 'sum',
        'Total_Emissions_ktCO2': 'sum',
        'Emission_Intensity_tCO2_per_t': 'mean'
    }).reset_index()
    
    facility_table = facility_table.sort_values('Total_Emissions_ktCO2', ascending=False)
    facility_table['Emissions_Share_Pct'] = (facility_table['Total_Emissions_ktCO2'] / 
                                            facility_table['Total_Emissions_ktCO2'].sum() * 100).round(1)
    
    print("\n1. FACILITY-LEVEL EMISSIONS SUMMARY:")
    print("-" * 40)
    print(facility_table.to_string(index=False, float_format='%.1f'))
    
    # 2. Technology-level emissions table
    tech_table = emissions_df.groupby(['ProcessType']).agg({
        'Capacity_kt_per_year': 'sum',
        'Total_Emissions_ktCO2': 'sum',
        'NG_Emissions_ktCO2': 'sum',
        'Elec_Emissions_ktCO2': 'sum',
        'Naphtha_Emissions_ktCO2': 'sum',
        'LPG_Emissions_ktCO2': 'sum'
    }).reset_index()
    
    tech_table['Emission_Intensity'] = (tech_table['Total_Emissions_ktCO2'] * 1000 / 
                                       tech_table['Capacity_kt_per_year']).round(2)
    tech_table['Emissions_Share_Pct'] = (tech_table['Total_Emissions_ktCO2'] / 
                                        tech_table['Total_Emissions_ktCO2'].sum() * 100).round(1)
    
    print(f"\n2. TECHNOLOGY-LEVEL EMISSIONS SUMMARY:")
    print("-" * 40)
    print(tech_table.to_string(index=False, float_format='%.1f'))
    
    # 3. Alternative technologies summary table
    alt_tech_summary = tech_analysis.groupby(['TechnologyCategory', 'TechGroup']).agg({
        'TechID': 'count',
        'TechnicalReadiness': 'mean',
        'CommercialYear': 'min',
        'CAPEX_Million_USD_per_kt_capacity': 'mean',
        'OPEX_Delta_USD_per_t': 'mean',
        'Lifetime_years': 'mean'
    }).reset_index()
    
    alt_tech_summary.columns = ['Category', 'Process', 'Count', 'Avg_TRL', 'First_Commercial', 
                               'Avg_CAPEX_M$_kt', 'Avg_OPEX_Delta_$_t', 'Avg_Lifetime_years']
    
    print(f"\n3. ALTERNATIVE TECHNOLOGIES SUMMARY:")
    print("-" * 40)
    print(alt_tech_summary.to_string(index=False, float_format='%.1f'))
    
    # 4. Price projection summary table
    price_summary = price_proj_df.pivot_table(
        values='Total_Cost_USD_per_t', 
        index='Category', 
        columns='Year', 
        aggfunc='mean'
    ).round(1)
    
    # Calculate cost reduction
    if 2023 in price_summary.columns and 2050 in price_summary.columns:
        price_summary['Cost_Reduction_Pct'] = (
            (price_summary[2050] - price_summary[2023]) / price_summary[2023] * 100
        ).round(1)
    
    print(f"\n4. TECHNOLOGY COST PROJECTIONS (USD/tonne):")
    print("-" * 40)
    print(price_summary.to_string(float_format='%.1f'))
    
    # Save all tables to CSV
    facility_table.to_csv('baseline/Facility_Emissions_Summary.csv', index=False)
    tech_table.to_csv('baseline/Technology_Emissions_Summary.csv', index=False)
    alt_tech_summary.to_csv('baseline/Alternative_Technologies_Summary.csv', index=False)
    price_summary.to_csv('baseline/Technology_Price_Projections.csv')
    
    print(f"\n📁 Tables saved:")
    print(f"  • baseline/Facility_Emissions_Summary.csv")
    print(f"  • baseline/Technology_Emissions_Summary.csv")
    print(f"  • baseline/Alternative_Technologies_Summary.csv")
    print(f"  • baseline/Technology_Price_Projections.csv")
    
    return facility_table, tech_table, alt_tech_summary, price_summary

def generate_executive_summary(emissions_df, tech_analysis, price_proj_df):
    """Generate executive summary of baseline analysis"""
    
    total_emissions = emissions_df['Total_Emissions_ktCO2'].sum()
    total_capacity = emissions_df['Capacity_kt_per_year'].sum()
    avg_emission_intensity = total_emissions * 1000 / total_capacity
    
    executive_summary = f"""
KOREAN PETROCHEMICAL MACC MODEL - BASELINE ANALYSIS EXECUTIVE SUMMARY
====================================================================
Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 KEY FINDINGS:
--------------
• Total Industry Emissions: {total_emissions:,.1f} ktCO2/year
• Total Production Capacity: {total_capacity:,.0f} kt/year
• Average Emission Intensity: {avg_emission_intensity:.2f} tCO2/t product
• Industry Benchmark Gap: {((avg_emission_intensity - 3.25) / 3.25 * 100):+.1f}% (vs 2.5-4.0 tCO2/t benchmark)

📊 EMISSION DISTRIBUTION:
-----------------------
Technology Shares:
"""
    
    tech_emissions = emissions_df.groupby('ProcessType')['Total_Emissions_ktCO2'].sum()
    for tech, emissions in tech_emissions.items():
        share = emissions / total_emissions * 100
        intensity = emissions * 1000 / emissions_df[emissions_df['ProcessType']==tech]['Capacity_kt_per_year'].sum()
        executive_summary += f"• {tech}: {share:.1f}% ({emissions:.0f} ktCO2/year, {intensity:.2f} tCO2/t)\n"
    
    regional_emissions = emissions_df.groupby('Region')['Total_Emissions_ktCO2'].sum()
    executive_summary += f"\nRegional Shares:\n"
    for region, emissions in regional_emissions.items():
        share = emissions / total_emissions * 100
        executive_summary += f"• {region}: {share:.1f}% ({emissions:.0f} ktCO2/year)\n"
    
    executive_summary += f"""
🔧 ALTERNATIVE TECHNOLOGIES:
---------------------------
• Total Technologies Available: {len(tech_analysis)}
• Technology Categories: {tech_analysis['TechnologyCategory'].nunique()}
• Average TRL: {tech_analysis['TechnicalReadiness'].mean():.1f}
• Commercial Timeframe: {tech_analysis['CommercialYear'].min()}-{tech_analysis['CommercialYear'].max()}

💰 TECHNOLOGY ECONOMICS:
-----------------------
• Average CAPEX: ${tech_analysis['CAPEX_Million_USD_per_kt_capacity'].mean():.1f}M per kt capacity
• Average Technology Lifetime: {tech_analysis['Lifetime_years'].mean():.0f} years

Key Technology Cost Trends (2023→2050):
"""
    
    # Add cost trends for main technologies
    main_techs = ['E-cracker', 'H2-furnace', 'Heat pump']
    for tech in main_techs:
        tech_costs = price_proj_df[price_proj_df['Category'] == tech]
        if len(tech_costs) > 0:
            cost_2023 = tech_costs[tech_costs['Year'] == 2023]['Total_Cost_USD_per_t'].iloc[0]
            cost_2050 = tech_costs[tech_costs['Year'] == 2050]['Total_Cost_USD_per_t'].iloc[0]
            reduction = (cost_2050 - cost_2023) / cost_2023 * 100
            executive_summary += f"• {tech}: ${cost_2023:.0f} → ${cost_2050:.0f}/t ({reduction:+.1f}%)\n"
    
    executive_summary += f"""
⚠️  CRITICAL ISSUES:
------------------
1. Emission Intensity Below Industry Benchmark
   - Current: {avg_emission_intensity:.2f} tCO2/t
   - Industry Standard: 2.5-4.0 tCO2/t
   - Likely Missing: Process emissions, utilities, flaring
   
2. Scale Validation Needed
   - Current Total: {total_emissions:,.0f} ktCO2/year
   - Industry Target: ~50,000 ktCO2/year
   - Gap: {50000 - total_emissions:,.0f} ktCO2/year

🎯 RECOMMENDATIONS:
-----------------
1. Add process emission sources (steam cracking reactions)
2. Include utility systems emissions (steam, flaring, cooling)
3. Validate consumption profiles against industry data
4. Map alternative technologies to specific facilities
5. Develop technology deployment scenarios

📈 MODEL READINESS:
-----------------
✅ Facility-based structure implemented
✅ Regional distribution validated
✅ Technology portfolio comprehensive
✅ Time-series data integrated
⚠️  Emission factors need adjustment
⚠️  Process emissions missing

NEXT PHASE: Address emission intensity to reach realistic 50 MtCO2 baseline
"""
    
    with open('baseline/Executive_Summary_Baseline_Analysis.txt', 'w', encoding='utf-8') as f:
        f.write(executive_summary)
    
    print(executive_summary)

def main():
    """Main function for comprehensive baseline analysis"""
    print("COMPREHENSIVE BASELINE ANALYSIS FOR KOREAN PETROCHEMICAL MACC MODEL")
    print("=" * 70)
    
    # Load updated database
    excel_data = load_updated_database()
    
    # Calculate detailed baseline emissions
    emissions_df = calculate_baseline_emissions_detailed(excel_data)
    
    # Analyze emission shares
    tech_emissions, regional_emissions, company_emissions = analyze_emission_shares(emissions_df)
    
    # Analyze alternative technologies
    tech_analysis = analyze_alternative_technologies(excel_data)
    
    # Calculate technology price projections
    price_proj_df = calculate_technology_price_projections(tech_analysis, excel_data['FuelCosts_TimeSeries'])
    
    # Create comprehensive visualizations
    create_comprehensive_visualizations(emissions_df, tech_emissions, regional_emissions, 
                                      company_emissions, tech_analysis, price_proj_df, excel_data)
    
    # Generate detailed tables
    facility_table, tech_table, alt_tech_summary, price_summary = generate_detailed_tables(
        emissions_df, tech_analysis, price_proj_df
    )
    
    # Generate executive summary
    generate_executive_summary(emissions_df, tech_analysis, price_proj_df)
    
    print("\n" + "=" * 70)
    print("✅ COMPREHENSIVE BASELINE ANALYSIS COMPLETED")
    print("=" * 70)
    print("📁 Files Generated:")
    print("  • baseline/Comprehensive_Baseline_Analysis.png")
    print("  • baseline/Facility_Emissions_Summary.csv")
    print("  • baseline/Technology_Emissions_Summary.csv")  
    print("  • baseline/Alternative_Technologies_Summary.csv")
    print("  • baseline/Technology_Price_Projections.csv")
    print("  • baseline/Executive_Summary_Baseline_Analysis.txt")

if __name__ == "__main__":
    main()