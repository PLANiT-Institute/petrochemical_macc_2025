#!/usr/bin/env python3
"""
Analyze Existing Excel Structure and Understand Cost Optimization Model Logic
"""

import pandas as pd
import numpy as np
import os

def analyze_cost_optimization_structure():
    """Analyze the existing Excel model structure to understand cost optimization logic"""

    print("🔍 ANALYZING EXISTING COST OPTIMIZATION MODEL STRUCTURE")
    print("=" * 80)

    # Load existing Excel file
    excel_path = "/Users/jinsupark/jinsu-coding/petrochemical_macc_2025/organized_analysis/data/korean_petrochemical_macc_enhanced.xlsx"

    if not os.path.exists(excel_path):
        print(f"❌ File not found: {excel_path}")
        return

    # Read all sheets
    sheets = pd.read_excel(excel_path, sheet_name=None)

    print(f"📊 Excel file contains {len(sheets)} sheets:")
    for sheet_name in sheets.keys():
        print(f"   • {sheet_name}")

    # Analyze CI sheet (consumption intensities)
    print(f"\n🔥 CI SHEET ANALYSIS (Consumption Intensities)")
    print("=" * 60)
    ci_df = sheets['CI']
    print(f"Shape: {ci_df.shape}")
    print(f"Columns: {list(ci_df.columns)}")

    # Translate Korean column names for clarity
    column_translation = {
        '제품': 'Product',
        '공정': 'Process',
        'LNG(GJ/t)': 'LNG_GJ_per_t',
        '부생가스(GJ/t)': 'Byproduct_Gas_GJ_per_t',
        'LPG-프로판(GJ/t)': 'LPG_Propane_GJ_per_t',
        'LPG-부탄(GJ/t)': 'LPG_Butane_GJ_per_t',
        '연료가스(Fuel gas mix)(GJ/t)': 'Fuel_Gas_Mix_GJ_per_t',
        '중유(Fuel oil)(GJ/t)': 'Fuel_Oil_GJ_per_t',
        '디젤(GJ/t)': 'Diesel_GJ_per_t',
        '전력(Baseline)(kWh/t)': 'Electricity_kWh_per_t'
    }

    ci_df_renamed = ci_df.rename(columns=column_translation)

    print(f"\n📋 CI Matrix Structure (Consumption per tonne product):")
    print(f"   Products/Processes: {len(ci_df_renamed)} entries")
    print(f"   Fuel types: {len(ci_df_renamed.columns)-2} fuels")

    # Show unique processes
    unique_processes = ci_df_renamed['Process'].unique()
    print(f"\n🏭 Process Types in CI Matrix:")
    for process in unique_processes:
        count = (ci_df_renamed['Process'] == process).sum()
        print(f"   • {process}: {count} products")

    # Check for naphtha in CI matrix
    naphtha_cols = [col for col in ci_df_renamed.columns if 'naphtha' in col.lower()]
    print(f"\n🛢️  Naphtha columns in CI matrix: {naphtha_cols}")
    if not naphtha_cols:
        print("   ❌ NAPHTHA MISSING from CI matrix!")

    # Analyze CI2 sheet (emission intensities)
    print(f"\n🌍 CI2 SHEET ANALYSIS (Emission Intensities)")
    print("=" * 60)
    ci2_df = sheets['CI2']
    print(f"Shape: {ci2_df.shape}")
    print(f"Columns: {list(ci2_df.columns)}")

    # Translate CI2 column names
    ci2_translation = {
        'LNG( tCO₂/GJ )': 'LNG_tCO2_per_GJ',
        '부생가스( tCO₂/GJ )': 'Byproduct_Gas_tCO2_per_GJ',
        'LPG-프로판( tCO₂/GJ )': 'LPG_Propane_tCO2_per_GJ',
        'LPG-부탄( tCO₂/GJ )': 'LPG_Butane_tCO2_per_GJ',
        '연료가스(Fuel gas mix)( tCO₂/GJ )': 'Fuel_Gas_Mix_tCO2_per_GJ',
        '중유(Fuel oil)( tCO₂/GJ )': 'Fuel_Oil_tCO2_per_GJ',
        '디젤( tCO₂/GJ )': 'Diesel_tCO2_per_GJ',
        '전력(Baseline)( tCO₂/kWh )': 'Electricity_tCO2_per_kWh'
    }

    ci2_df_renamed = ci2_df.rename(columns=ci2_translation)

    print(f"\n📋 CI2 Matrix Structure (Emission factors):")
    print(f"   Emission factor rows: {len(ci2_df_renamed)}")
    print(f"   Fuel types: {len(ci2_df_renamed.columns)} fuels")

    # Show emission factors
    print(f"\n🌍 Current Emission Factors:")
    for i, row in ci2_df_renamed.iterrows():
        print(f"   Row {i+1}:")
        for col in ci2_df_renamed.columns:
            if pd.notna(row[col]) and row[col] != 0:
                print(f"     {col}: {row[col]:.4f}")

    # Check for naphtha in CI2 matrix
    naphtha_cols_ci2 = [col for col in ci2_df_renamed.columns if 'naphtha' in col.lower()]
    print(f"\n🛢️  Naphtha columns in CI2 matrix: {naphtha_cols_ci2}")
    if not naphtha_cols_ci2:
        print("   ❌ NAPHTHA MISSING from CI2 matrix!")

    # Analyze MACC Template (cost optimization core)
    print(f"\n💰 MACC TEMPLATE ANALYSIS (Cost Optimization Core)")
    print("=" * 60)
    macc_df = sheets['MACC_Template']
    print(f"Shape: {macc_df.shape}")
    print(f"Columns: {list(macc_df.columns)}")

    print(f"\n📊 MACC Technologies:")
    for i, row in macc_df.iterrows():
        tech_name = row['TechName']
        cost = row['Cost_USD_per_tCO2']
        abatement = row['Abatement_Potential_MtCO2_per_year']
        print(f"   {tech_name}: ${cost:.0f}/tCO₂, {abatement:.1f} MtCO₂/year potential")

    # Check for bio-naphtha or naphtha alternatives
    naphtha_techs = [tech for tech in macc_df['TechName'] if 'naphtha' in str(tech).lower()]
    print(f"\n🛢️  Naphtha technologies in MACC: {naphtha_techs}")
    if not naphtha_techs:
        print("   ❌ NAPHTHA TECHNOLOGIES MISSING from MACC!")

    # Analyze source sheet (facility database)
    print(f"\n🏭 SOURCE SHEET ANALYSIS (Facility Database)")
    print("=" * 60)
    source_df = sheets['source']
    print(f"Shape: {source_df.shape}")
    print(f"Columns: {list(source_df.columns)}")

    process_counts = source_df['process'].value_counts()
    print(f"\n🏭 Facility Distribution:")
    for process, count in process_counts.items():
        print(f"   • {process}: {count} facilities")

    total_capacity = source_df['capacity_1000_t'].sum()
    print(f"\n📈 Total Industry Capacity: {total_capacity:.1f} thousand tonnes/year")

    # Understanding the cost optimization logic
    print(f"\n\n🧮 COST OPTIMIZATION MODEL LOGIC")
    print("=" * 80)

    print("📋 MODEL STRUCTURE:")
    print("   1. SOURCE sheet: 248 facilities with capacity data")
    print("   2. CI sheet: Fuel consumption per tonne product (GJ/t, kWh/t)")
    print("   3. CI2 sheet: Emission factors per fuel unit (tCO₂/GJ, tCO₂/kWh)")
    print("   4. MACC_Template: Technology costs and abatement potential")
    print("   5. TechOptions: Technology constraints and deployment")

    print(f"\n🔄 OPTIMIZATION FLOW:")
    print("   Facility Capacity × CI (consumption) × CI2 (emission factors) = Baseline Emissions")
    print("   Technology Deployment × Abatement Potential = Emission Reduction")
    print("   Technology Cost × Deployment = Total Investment Cost")
    print("   Objective: Minimize cost to achieve emission target")

    print(f"\n❌ MISSING COMPONENTS FOR NAPHTHA:")
    print("   1. Naphtha consumption columns missing from CI matrix")
    print("   2. Naphtha emission factors missing from CI2 matrix")
    print("   3. Bio-naphtha technology missing from MACC template")
    print("   4. External GHG factors not included in emission calculation")

    return {
        'ci_df': ci_df_renamed,
        'ci2_df': ci2_df_renamed,
        'macc_df': macc_df,
        'source_df': source_df,
        'sheets': sheets
    }

def design_corrected_model_structure(analysis_result):
    """Design the corrected model structure with naphtha integration"""

    print(f"\n\n🔧 DESIGNING CORRECTED MODEL STRUCTURE")
    print("=" * 80)

    print("🎯 CORRECTED CI MATRIX (with naphtha):")
    print("   Existing columns: LNG, Byproduct_Gas, LPG_Propane, LPG_Butane, Fuel_Gas_Mix, Fuel_Oil, Diesel, Electricity")
    print("   ➕ ADD: Naphtha_Feedstock_GJ_per_t")
    print("   ➕ ADD: Naphtha_Thermal_GJ_per_t")
    print("   Structure: Product × Process × [Fuel_Consumptions + Naphtha_Consumptions]")

    print(f"\n🎯 CORRECTED CI2 MATRIX (with naphtha emission factors):")
    print("   Existing columns: emission factors for 8 fuel types")
    print("   ➕ ADD: Naphtha_Feedstock_tCO2_per_GJ (with external GHG: 0.90 tCO2/t ÷ 43.5 GJ/t)")
    print("   ➕ ADD: Naphtha_Thermal_tCO2_per_GJ (combustion + external GHG)")
    print("   ➕ ADD: Bio_Naphtha_Feedstock_tCO2_per_GJ (85% reduction)")
    print("   ➕ ADD: Bio_Naphtha_Thermal_tCO2_per_GJ (carbon neutral)")

    print(f"\n🎯 CORRECTED MACC MATRIX (with naphtha technologies):")
    print("   Existing technologies: 23 technologies with costs and abatement")
    print("   ➕ ADD: Bio_Naphtha_Substitution")
    print("     - Cost: Processing CAPEX + feedstock premium")
    print("     - Abatement: Based on naphtha consumption × emission reduction")
    print("     - Constraint: Supply-limited deployment")

    print(f"\n🔄 CORRECTED OPTIMIZATION LOGIC:")
    print("   1. Baseline = Facility_Capacity × (CI_fuels + CI_naphtha) × (CI2_fuels + CI2_naphtha)")
    print("   2. Naphtha_Baseline = Total_Naphtha_Consumption × External_GHG_Factor")
    print("   3. Total_Baseline = Fuel_Emissions + Naphtha_External_Emissions")
    print("   4. Technology_Abatement = ∑(Tech_Deployment × Tech_Potential)")
    print("   5. Final_Emissions = Total_Baseline - Technology_Abatement")
    print("   6. Minimize: ∑(Tech_Cost × Tech_Deployment)")
    print("   7. Subject to: Final_Emissions ≤ Emission_Target")

    print(f"\n📐 NAPHTHA CALCULATION FRAMEWORK:")
    naphtha_external_ghg = 0.90  # tCO2/t from your analysis
    naphtha_heating_value = 43.5  # GJ/t
    naphtha_emission_factor = naphtha_external_ghg / naphtha_heating_value

    print(f"   External GHG factor: {naphtha_external_ghg:.2f} tCO₂/t naphtha")
    print(f"   Heating value: {naphtha_heating_value:.1f} GJ/t naphtha")
    print(f"   Emission factor: {naphtha_emission_factor:.4f} tCO₂/GJ naphtha")
    print(f"   Bio-naphtha reduction: 85% → {naphtha_emission_factor * 0.15:.4f} tCO₂/GJ")

    return {
        'naphtha_external_ghg': naphtha_external_ghg,
        'naphtha_heating_value': naphtha_heating_value,
        'naphtha_emission_factor': naphtha_emission_factor,
        'bio_naphtha_emission_factor': naphtha_emission_factor * 0.15
    }

def main():
    """Main analysis function"""

    print("🏭 KOREAN PETROCHEMICAL MACC MODEL")
    print("EXISTING STRUCTURE ANALYSIS & COST OPTIMIZATION DESIGN")
    print("=" * 80)

    # Analyze existing structure
    analysis_result = analyze_cost_optimization_structure()

    if analysis_result:
        # Design corrected structure
        design_result = design_corrected_model_structure(analysis_result)

        print(f"\n\n✅ ANALYSIS COMPLETE")
        print("=" * 50)
        print("🎯 Next Steps:")
        print("   1. Add naphtha columns to CI matrix")
        print("   2. Add naphtha emission factors to CI2 matrix")
        print("   3. Add bio-naphtha technology to MACC template")
        print("   4. Integrate external GHG factors")
        print("   5. Update cost optimization logic")

if __name__ == "__main__":
    main()