import pandas as pd
import sys

def verify_comparison_report(filepath):
    print(f"Verifying {filepath}...")
    try:
        xls = pd.ExcelFile(filepath)
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return

    # 1. Check Scenario Comparison
    if 'Scenario_Comparison' in xls.sheet_names:
        df = pd.read_excel(xls, 'Scenario_Comparison')
        required = ['Emissions_Elec_Mt', 'Emissions_H2_Mt', 'Total_Cost_Elec_MUSD']
        if all(col in df.columns for col in required):
            print("✅ Scenario_Comparison sheet valid.")
            print(f"   2050 Elec Emissions: {df[df['Year']==2050]['Emissions_Elec_Mt'].values[0]:.2f} Mt")
        else:
            print(f"❌ Scenario_Comparison missing columns. Found: {df.columns.tolist()}")
    else:
        print("❌ Scenario_Comparison sheet missing.")

    # 2. Check Regional Annual
    if 'Regional_Annual' in xls.sheet_names:
        df = pd.read_excel(xls, 'Regional_Annual')
        # Check if it looks like a pivot table (years as columns)
        if 2030 in df.columns or '2030' in df.columns:
             print("✅ Regional_Annual sheet valid (Pivot structure confirmed).")
        else:
             print("⚠️ Regional_Annual might not be pivoted correctly. Check columns.")
             print(f"   Columns: {df.columns.tolist()[:5]}...")
    else:
        print("❌ Regional_Annual sheet missing.")

    # 3. Check Facility Transition Matrix
    if 'Facility_Transition_Matrix' in xls.sheet_names:
        df = pd.read_excel(xls, 'Facility_Transition_Matrix')
        print("✅ Facility_Transition_Matrix sheet valid.")
    else:
        print("❌ Facility_Transition_Matrix sheet missing.")

if __name__ == "__main__":
    verify_comparison_report('outputs/excel_report/Client_Comparison_Report.xlsx')
