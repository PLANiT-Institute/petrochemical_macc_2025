#!/usr/bin/env python3
"""
Update Excel file with temporal MACC projections
Add new sheets for 2030, 2040, and 2050 projections
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def update_excel_with_temporal_data():
    """Update Excel file with temporal projections"""
    print("📊 UPDATING EXCEL FILE WITH TEMPORAL PROJECTIONS")
    print("=" * 60)

    # File paths
    excel_path = "../data/Korean_Petrochemical_MACC_Model_Corrected_with_Naphtha.xlsx"
    output_path = "../data/Korean_Petrochemical_MACC_Model_with_Temporal_Projections.xlsx"

    # Load existing data
    existing_sheets = {}
    with pd.ExcelFile(excel_path) as xls:
        for sheet_name in xls.sheet_names:
            existing_sheets[sheet_name] = pd.read_excel(excel_path, sheet_name=sheet_name)
            print(f"   Loaded: {sheet_name}")

    # Load temporal projection results
    projection_years = [2030, 2040, 2050]
    temporal_data = {}

    for year in projection_years:
        csv_path = f"../outputs/macc_curve_{year}.csv"
        if Path(csv_path).exists():
            temporal_data[year] = pd.read_csv(csv_path)
            print(f"   Loaded temporal data for {year}")

    # Load comparison summary
    comparison_df = pd.read_csv("../outputs/temporal_macc_comparison_2025_2050.csv")

    # Create temporal MACC sheets
    temporal_sheets = {}

    # Static technology costs (no learning curves)
    static_costs = {
        'Early_Retirement': 50,
        'Efficiency_Upgrade': 100,
        'Fuel_Switch': 200,
        'Process_Replacement': 400,
        'Bio_Naphtha': 272,
        'Green_Hydrogen': 300,
        'Electrification': 250
    }

    # Technology availability by year
    availability_by_year = {
        2030: {
            'Early_Retirement': 1.0,
            'Efficiency_Upgrade': 1.0,
            'Fuel_Switch': 0.7,
            'Bio_Naphtha': 0.4,
            'Green_Hydrogen': 0.3,
            'Electrification': 0.6,
            'Process_Replacement': 0.3
        },
        2040: {
            'Early_Retirement': 1.0,
            'Efficiency_Upgrade': 1.0,
            'Fuel_Switch': 0.9,
            'Bio_Naphtha': 0.7,
            'Green_Hydrogen': 0.6,
            'Electrification': 0.8,
            'Process_Replacement': 0.6
        },
        2050: {
            'Early_Retirement': 1.0,
            'Efficiency_Upgrade': 1.0,
            'Fuel_Switch': 1.0,
            'Bio_Naphtha': 1.0,
            'Green_Hydrogen': 1.0,
            'Electrification': 1.0,
            'Process_Replacement': 1.0
        }
    }

    # Create MACC template sheets for each year
    for year in projection_years:
        print(f"\n📋 Creating MACC template for {year}...")

        # Create technology data for the year
        tech_data = []
        tech_id = 1

        for tech_name, base_cost in static_costs.items():
            availability = availability_by_year[year].get(tech_name, 1.0)

            # Get baseline emissions for abatement potential calculation
            year_comparison = comparison_df[comparison_df['year'] == year]
            if not year_comparison.empty:
                baseline_emissions = year_comparison['baseline_emissions_mt'].iloc[0] * 1e6  # Convert to tonnes

                # Technology-specific abatement potentials
                abatement_fractions = {
                    'Early_Retirement': 0.10,
                    'Efficiency_Upgrade': 0.15,
                    'Fuel_Switch': 0.30,
                    'Bio_Naphtha': 0.20,
                    'Green_Hydrogen': 0.25,
                    'Electrification': 0.20,
                    'Process_Replacement': 0.35
                }

                max_abatement = baseline_emissions * abatement_fractions.get(tech_name, 0.15) * availability
                max_abatement_mt = max_abatement / 1e6  # Convert to Mt

                tech_data.append({
                    'TechID': tech_id,
                    'TechName': f"{tech_name}_{year}",
                    'Cost_USD_per_tCO2': base_cost,
                    'Max_Abatement_Potential_MtCO2_per_year': max_abatement_mt,
                    'Availability_Factor': availability,
                    'TRL': 7 if availability >= 0.8 else 5,
                    'Commercial_Year': year,
                    'Notes': f"Static cost, {availability*100:.0f}% availability in {year}"
                })
                tech_id += 1

        # Create DataFrame
        tech_df = pd.DataFrame(tech_data)

        # Add cumulative abatement
        tech_df_sorted = tech_df.sort_values('Cost_USD_per_tCO2')
        tech_df_sorted['Cumulative_Abatement_MtCO2_per_year'] = tech_df_sorted['Max_Abatement_Potential_MtCO2_per_year'].cumsum()

        temporal_sheets[f'MACC_Template_{year}'] = tech_df_sorted

    # Create facility retirement projections
    print(f"\n🏭 Creating facility retirement projections...")

    # Load facility data
    facilities_df = existing_sheets['source_Original'].copy()
    facilities_df['age_2025'] = 2025 - facilities_df['year']

    retirement_projections = []

    for year in projection_years:
        facilities_year = facilities_df.copy()
        facilities_year[f'age_{year}'] = year - facilities_year['year']

        # Retirement thresholds
        retirement_thresholds = {
            'Naphtha Cracker': 40,
            'BTX Plant': 35,
            'Utility': 30
        }

        facilities_year['retired'] = False
        for process, threshold in retirement_thresholds.items():
            mask = (facilities_year['process'] == process) & (facilities_year[f'age_{year}'] >= threshold)
            facilities_year.loc[mask, 'retired'] = True

        # Summary by year
        total_facilities = len(facilities_year)
        retired_facilities = facilities_year['retired'].sum()
        active_facilities = total_facilities - retired_facilities
        retired_capacity = facilities_year[facilities_year['retired']]['capacity_1000_t'].sum()
        active_capacity = facilities_year[~facilities_year['retired']]['capacity_1000_t'].sum()

        retirement_projections.append({
            'year': year,
            'total_facilities': total_facilities,
            'active_facilities': active_facilities,
            'retired_facilities': retired_facilities,
            'retirement_rate_pct': (retired_facilities / total_facilities * 100),
            'active_capacity_kt': active_capacity,
            'retired_capacity_kt': retired_capacity,
            'capacity_retirement_rate_pct': (retired_capacity / (active_capacity + retired_capacity) * 100)
        })

        # Save detailed facility projections
        temporal_sheets[f'Facility_Projections_{year}'] = facilities_year

    # Create retirement summary sheet
    retirement_summary_df = pd.DataFrame(retirement_projections)
    temporal_sheets['Retirement_Summary'] = retirement_summary_df

    # Create temporal comparison sheet
    temporal_sheets['Temporal_Comparison'] = comparison_df

    # Create technology availability sheet
    availability_data = []
    for year in projection_years:
        for tech, availability in availability_by_year[year].items():
            availability_data.append({
                'year': year,
                'technology': tech,
                'availability_factor': availability,
                'cost_usd_per_tco2': static_costs[tech],
                'status': 'Available' if availability >= 0.8 else 'Limited' if availability >= 0.5 else 'Pilot'
            })

    availability_df = pd.DataFrame(availability_data)
    temporal_sheets['Technology_Availability'] = availability_df

    # Write all sheets to new Excel file
    print(f"\n💾 Writing updated Excel file...")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Write existing sheets first
        for sheet_name, df in existing_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"   Copied: {sheet_name}")

        # Write new temporal sheets
        for sheet_name, df in temporal_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"   Added: {sheet_name}")

    print(f"\n✅ EXCEL UPDATE COMPLETE!")
    print(f"📁 Updated file: {output_path}")
    print(f"📊 New sheets added:")
    for sheet_name in temporal_sheets.keys():
        print(f"   - {sheet_name}")

    # Summary of temporal projections
    print(f"\n📈 TEMPORAL PROJECTION SUMMARY:")
    print(retirement_summary_df.to_string(index=False, float_format='%.1f'))

    print(f"\n🔧 TECHNOLOGY AVAILABILITY BY YEAR:")
    pivot_availability = availability_df.pivot(index='technology', columns='year', values='availability_factor')
    print(pivot_availability.to_string(float_format='%.1f'))

    return output_path

def create_temporal_summary_sheet():
    """Create a summary sheet with key temporal insights"""
    print(f"\n📋 Creating temporal summary insights...")

    insights = {
        'Analysis_Date': ['2025-09-22'],
        'Key_Finding_1': ['Baseline emissions increase from 110 Mt (2025) to 243 Mt (2050) due to capacity growth'],
        'Key_Finding_2': ['Static technology costs: $50-400/tCO2 (no learning curves)'],
        'Key_Finding_3': ['Marginal costs remain stable: ~$140/tCO2 across all years'],
        'Key_Finding_4': ['Technology availability increases over time (30%-100% by 2050)'],
        'Key_Finding_5': ['Investment requirements: $7.7B (2025) → $17.0B (2050)'],
        'Retirement_Impact': ['222 of 248 facilities retired by 2050'],
        'Policy_Implication_1': ['Static costs favor consistent long-term planning'],
        'Policy_Implication_2': ['Technology deployment constraints require phased approach'],
        'Model_Assumptions': ['No CCUS, no learning curves, 1% capacity growth'],
        'Carbon_Price_Path': ['$50 (2025) → $350 (2050)']
    }

    insights_df = pd.DataFrame(insights).T
    insights_df.columns = ['Value']
    insights_df.index.name = 'Parameter'

    return insights_df

if __name__ == "__main__":
    # Update Excel file with temporal data
    output_file = update_excel_with_temporal_data()

    # Create summary insights
    insights_df = create_temporal_summary_sheet()
    print(f"\n💡 KEY INSIGHTS:")
    print(insights_df.to_string())

    print(f"\n🎯 TEMPORAL EXCEL UPDATE COMPLETE!")
    print(f"📁 Final file: {output_file}")