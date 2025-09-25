"""
Update Main Excel Database with Facility-Based Structure
========================================================

This script updates the main Korea_Petrochemical_MACC_Database.xlsx file with the new
facility-based structure from our comprehensive analysis.

Key Updates:
1. Replace BaselineConsumption_2023 with FacilityBaselineConsumption_2023
2. Update RegionalFacilities with correct company information
3. Preserve all time-series and technology sheets
4. Maintain backward compatibility where possible
"""

import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def load_analysis_results():
    """Load the analysis results from baseline folder"""
    print("LOADING ANALYSIS RESULTS")
    print("=" * 40)
    
    # Load the updated datasets from analysis
    facilities_df = pd.read_csv('baseline/Updated_RegionalFacilities.csv')
    consumption_df = pd.read_csv('baseline/Updated_FacilityBaselineConsumption_2023.csv')
    
    print(f"✅ Updated RegionalFacilities: {facilities_df.shape[0]} facilities")
    print(f"✅ Updated FacilityBaselineConsumption_2023: {consumption_df.shape[0]} records")
    
    return facilities_df, consumption_df

def load_original_excel():
    """Load the original Excel database"""
    excel_path = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    
    print(f"\nLOADING ORIGINAL DATABASE")
    print("=" * 40)
    print(f"Path: {excel_path}")
    
    # Load all original sheets
    original_sheets = pd.read_excel(excel_path, sheet_name=None)
    
    print(f"Original sheets loaded:")
    for sheet_name, df in original_sheets.items():
        print(f"  • {sheet_name}: {df.shape[0]} rows × {df.shape[1]} columns")
    
    return original_sheets

def create_updated_excel_structure(facilities_df, consumption_df, original_sheets):
    """Create updated Excel structure with new facility-based data"""
    print(f"\nCREATING UPDATED EXCEL STRUCTURE")
    print("=" * 40)
    
    updated_sheets = {}
    
    # 1. Replace RegionalFacilities with updated version
    updated_sheets['RegionalFacilities'] = facilities_df
    print("✅ RegionalFacilities → Updated with correct company info")
    
    # 2. Replace BaselineConsumption_2023 with FacilityBaselineConsumption_2023
    updated_sheets['FacilityBaselineConsumption_2023'] = consumption_df
    print("✅ BaselineConsumption_2023 → FacilityBaselineConsumption_2023 (facility-based)")
    
    # 3. Preserve time-series sheets (unchanged)
    time_series_sheets = ['EmissionFactors_TimeSeries', 'FuelCosts_TimeSeries', 'EmissionsTargets']
    for sheet_name in time_series_sheets:
        if sheet_name in original_sheets:
            updated_sheets[sheet_name] = original_sheets[sheet_name]
            print(f"✅ {sheet_name} → Preserved (no changes)")
    
    # 4. Preserve technology sheets (will need future updates but keep for now)
    tech_sheets = ['AlternativeTechnologies', 'AlternativeCosts']
    for sheet_name in tech_sheets:
        if sheet_name in original_sheets:
            updated_sheets[sheet_name] = original_sheets[sheet_name]
            print(f"⚠️  {sheet_name} → Preserved (needs facility mapping in future)")
    
    # 5. Preserve static emission factors for backward compatibility
    if 'EmissionFactors' in original_sheets:
        updated_sheets['EmissionFactors'] = original_sheets['EmissionFactors']
        print(f"✅ EmissionFactors → Preserved (reference)")
    
    # 6. Create a legacy sheet with old BaselineConsumption for reference
    if 'BaselineConsumption_2023' in original_sheets:
        updated_sheets['BaselineConsumption_2023_Legacy'] = original_sheets['BaselineConsumption_2023']
        print(f"📁 BaselineConsumption_2023_Legacy → Archived for reference")
    
    print(f"\nTotal sheets in updated database: {len(updated_sheets)}")
    return updated_sheets

def validate_updated_structure(updated_sheets):
    """Validate the updated Excel structure"""
    print(f"\nVALIDATING UPDATED STRUCTURE")
    print("=" * 40)
    
    validation_results = []
    
    # 1. Check required sheets exist
    required_sheets = [
        'RegionalFacilities', 
        'FacilityBaselineConsumption_2023',
        'EmissionFactors_TimeSeries',
        'FuelCosts_TimeSeries'
    ]
    
    for sheet in required_sheets:
        if sheet in updated_sheets:
            validation_results.append(f"✅ {sheet} exists")
        else:
            validation_results.append(f"❌ {sheet} missing")
    
    # 2. Validate data alignment between RegionalFacilities and FacilityBaselineConsumption
    facilities_df = updated_sheets['RegionalFacilities']
    consumption_df = updated_sheets['FacilityBaselineConsumption_2023']
    
    # Check capacity alignment
    facilities_capacity = {
        'NCC': facilities_df['NCC_Capacity_kt_per_year'].sum(),
        'BTX': facilities_df['BTX_Capacity_kt_per_year'].sum(),
        'C4': facilities_df['C4_Capacity_kt_per_year'].sum()
    }
    
    consumption_capacity = consumption_df.groupby('ProcessType')['Activity_kt_product'].sum()
    
    print(f"\nCapacity Alignment Check:")
    for process in ['NCC', 'BTX', 'C4']:
        facilities_cap = facilities_capacity[process]
        consumption_cap = consumption_capacity[process]
        if facilities_cap == consumption_cap:
            validation_results.append(f"✅ {process} capacity aligned: {facilities_cap:,} kt/year")
        else:
            validation_results.append(f"❌ {process} capacity misaligned: {facilities_cap:,} vs {consumption_cap:,} kt/year")
    
    # 3. Check facility count alignment
    facilities_count = len(facilities_df)
    unique_facilities_in_consumption = consumption_df['FacilityID'].nunique()
    
    if facilities_count == unique_facilities_in_consumption:
        validation_results.append(f"✅ Facility count aligned: {facilities_count} facilities")
    else:
        validation_results.append(f"❌ Facility count misaligned: {facilities_count} vs {unique_facilities_in_consumption}")
    
    # 4. Check time-series data integrity
    if 'EmissionFactors_TimeSeries' in updated_sheets:
        ef_df = updated_sheets['EmissionFactors_TimeSeries']
        years_count = len(ef_df)
        year_range = f"{ef_df['Year'].min()}-{ef_df['Year'].max()}"
        validation_results.append(f"✅ EmissionFactors_TimeSeries: {years_count} years ({year_range})")
    
    if 'FuelCosts_TimeSeries' in updated_sheets:
        fc_df = updated_sheets['FuelCosts_TimeSeries']
        years_count = len(fc_df)
        year_range = f"{fc_df['Year'].min()}-{fc_df['Year'].max()}"
        validation_results.append(f"✅ FuelCosts_TimeSeries: {years_count} years ({year_range})")
    
    # Print all validation results
    print(f"\nValidation Results:")
    for result in validation_results:
        print(f"  {result}")
    
    # Overall validation status
    failed_validations = [r for r in validation_results if '❌' in r]
    if len(failed_validations) == 0:
        print(f"\n🎯 VALIDATION PASSED - Database ready for use")
        return True
    else:
        print(f"\n⚠️  VALIDATION ISSUES - {len(failed_validations)} problems found")
        return False

def backup_original_database():
    """Create backup of original database"""
    original_path = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    backup_path = Path("data/Korea_Petrochemical_MACC_Database_BACKUP.xlsx")
    
    if original_path.exists() and not backup_path.exists():
        import shutil
        shutil.copy2(original_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return True
    elif backup_path.exists():
        print(f"📁 Backup already exists: {backup_path}")
        return True
    else:
        print(f"❌ Could not create backup")
        return False

def save_updated_database(updated_sheets):
    """Save the updated database to Excel file"""
    print(f"\nSAVING UPDATED DATABASE")
    print("=" * 40)
    
    output_path = Path("data/Korea_Petrochemical_MACC_Database.xlsx")
    
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, df in updated_sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"✅ {sheet_name} saved ({df.shape[0]} rows)")
        
        print(f"\n🎯 DATABASE SUCCESSFULLY UPDATED")
        print(f"   File: {output_path}")
        print(f"   Sheets: {len(updated_sheets)}")
        
        # Verify file was created and show size
        if output_path.exists():
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   Size: {file_size:.2f} MB")
            return True
        else:
            print(f"❌ File was not created successfully")
            return False
            
    except Exception as e:
        print(f"❌ Error saving database: {str(e)}")
        return False

def generate_update_summary(updated_sheets):
    """Generate summary of database updates"""
    print(f"\nDATABASE UPDATE SUMMARY")
    print("=" * 40)
    
    # Count total data points
    total_rows = sum(len(df) for df in updated_sheets.values())
    total_cols = sum(len(df.columns) for df in updated_sheets.values())
    
    print(f"📊 Database Statistics:")
    print(f"   • Total Sheets: {len(updated_sheets)}")
    print(f"   • Total Rows: {total_rows:,}")
    print(f"   • Total Columns: {total_cols:,}")
    print(f"   • Total Data Points: {total_rows * total_cols:,}")
    
    print(f"\n🔄 Key Changes Implemented:")
    print(f"   • ✅ Model structure: Technology bands → Facility-based")
    print(f"   • ✅ Company updates: Added 여천NCC, 한화 토탈, 현대케미칼, 대한유화")
    print(f"   • ✅ Data alignment: BaselineConsumption ↔ RegionalFacilities")
    print(f"   • ✅ Capacity validation: Perfect alignment achieved")
    print(f"   • ✅ Time-series preservation: All dynamic data retained")
    
    # Facility summary
    if 'RegionalFacilities' in updated_sheets:
        facilities_df = updated_sheets['RegionalFacilities']
        total_capacity = (facilities_df['NCC_Capacity_kt_per_year'].sum() +
                         facilities_df['BTX_Capacity_kt_per_year'].sum() +
                         facilities_df['C4_Capacity_kt_per_year'].sum())
        
        print(f"\n🏭 Facility Structure:")
        print(f"   • Total Facilities: {len(facilities_df)}")
        print(f"   • Total Capacity: {total_capacity:,} kt/year")
        
        regional_dist = facilities_df.groupby('Region').size()
        for region, count in regional_dist.items():
            capacity = (facilities_df[facilities_df['Region']==region]['NCC_Capacity_kt_per_year'].sum() +
                       facilities_df[facilities_df['Region']==region]['BTX_Capacity_kt_per_year'].sum() +
                       facilities_df[facilities_df['Region']==region]['C4_Capacity_kt_per_year'].sum())
            print(f"   • {region}: {count} facilities, {capacity:,} kt/year")
    
    print(f"\n📁 Files Modified:")
    print(f"   • data/Korea_Petrochemical_MACC_Database.xlsx (UPDATED)")
    print(f"   • data/Korea_Petrochemical_MACC_Database_BACKUP.xlsx (BACKUP)")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Update simulation and optimization models to use FacilityBaselineConsumption_2023")
    print(f"   2. Map AlternativeTechnologies to facility level")
    print(f"   3. Address emission intensity issue (currently 0.85 vs 2.5-4.0 tCO2/t benchmark)")
    print(f"   4. Validate model results with new facility-based structure")

def main():
    """Main function to update the Excel database"""
    print("UPDATING MAIN EXCEL DATABASE WITH FACILITY-BASED STRUCTURE")
    print("=" * 60)
    
    # 1. Load analysis results
    facilities_df, consumption_df = load_analysis_results()
    
    # 2. Load original Excel database
    original_sheets = load_original_excel()
    
    # 3. Create backup of original database
    backup_success = backup_original_database()
    if not backup_success:
        print("⚠️  Proceeding without backup - be careful!")
    
    # 4. Create updated Excel structure
    updated_sheets = create_updated_excel_structure(facilities_df, consumption_df, original_sheets)
    
    # 5. Validate updated structure
    validation_passed = validate_updated_structure(updated_sheets)
    
    if validation_passed:
        # 6. Save updated database
        save_success = save_updated_database(updated_sheets)
        
        if save_success:
            # 7. Generate summary
            generate_update_summary(updated_sheets)
            
            print(f"\n" + "=" * 60)
            print("✅ DATABASE UPDATE COMPLETED SUCCESSFULLY")
            print("=" * 60)
        else:
            print(f"\n❌ DATABASE UPDATE FAILED - Check error messages above")
    else:
        print(f"\n❌ VALIDATION FAILED - Database not updated")
        print(f"   Review validation issues above before proceeding")

if __name__ == "__main__":
    main()