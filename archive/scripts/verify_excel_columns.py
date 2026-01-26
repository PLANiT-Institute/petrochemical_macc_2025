import pandas as pd
import sys

def verify_excel(filepath):
    print(f"Verifying {filepath}...")
    xls = pd.ExcelFile(filepath)
    
    # Check Regional Summary
    df_regional = pd.read_excel(xls, 'Regional_Summary')
    required_regional = ['capex_annual_usd', 'opex_annual_usd', 'new_fuel_cost_usd', 'capex_musd']
    missing_regional = [col for col in required_regional if col not in df_regional.columns]
    
    if missing_regional:
        print(f"❌ Regional_Summary missing columns: {missing_regional}")
    else:
        print("✅ Regional_Summary has all required columns.")
        print(f"   Sample CAPEX: {df_regional['capex_musd'].sum():.2f} MUSD")

    # Check Yearly Facility Detail
    df_yearly = pd.read_excel(xls, 'Yearly_Facility_Detail')
    required_yearly = ['remaining_naphtha_gj', 'remaining_lng_gj', 'fossil_fuel_reduced_gj']
    missing_yearly = [col for col in required_yearly if col not in df_yearly.columns]
    
    if missing_yearly:
        print(f"❌ Yearly_Facility_Detail missing columns: {missing_yearly}")
    else:
        print("✅ Yearly_Facility_Detail has all required columns.")
        print(f"   Sample Remaining Naphtha: {df_yearly['remaining_naphtha_gj'].sum()/1e6:.2f} million GJ")

if __name__ == "__main__":
    verify_excel('outputs/excel_report/MACC_Report_NCC_Electricity.xlsx')
