import pandas as pd
import numpy as np

# Load results
df = pd.read_csv('outputs/scenario_results.csv')

def check_logic():
    errors = []
    
    # Check 1: No NaNs in critical columns
    critical_cols = ['total_cost_usd', 'emissions_tco2', 'abatement_tco2', 'mac_usd_per_tco2']
    for col in critical_cols:
        if df[col].isna().any():
            errors.append(f"CRITICAL: Found NaNs in {col}")
            
    # Check 2: Infinite MACs only allowed where abatement is 0
    # Access Inf directly
    inf_macs = df[np.isinf(df['mac_usd_per_tco2'])]
    if len(inf_macs) > 0:
        # If MAC is Inf, tech_deployed should be 0 OR abatement should be 0
        # Wait, if tech is deployed, MAC was finite initially. 
        # But if potential abatement is 0, MAC is Inf.
        # If potential abatement is 0, tech should usually not be deployed unless forced?
        # Let's check if any deployed tech has Inf MAC
        bad_inf = inf_macs[inf_macs['tech_deployed'] == 1]
        if len(bad_inf) > 0:
             errors.append(f"LOGIC: Found {len(bad_inf)} deployed facilities with Infinite MAC")

    # Check 3: Fuel Savings Logic
    # If tech_deployed == 1, fuel_savings_usd should generally be > 0 (unless it was 100% elec facility)
    deployed = df[df['tech_deployed'] == 1]
    # Filter for facilities that are likely to have fuel savings (Crackers, BTX)
    # Exclude weird edge cases
    no_savings = deployed[deployed['cost_component_fuel_savings_usd'] <= 0]
    if len(no_savings) > 0:
        # It's possible if prices are 0 or consumption was 0.
        # Let's just flag it as a warning
        print(f"WARNING: Found {len(no_savings)} deployed facilities with 0 fuel savings.")
        # Sample
        print(no_savings[['facility_id', 'process', 'year']].head())

    # Check 4: Total Cost consistency
    # Total = AnnualCapex + Opex + NewEnergy - FuelSavings
    # allow small floating point diff
    calc_total = (df['cost_component_capex_annual_usd'] + 
                  df['cost_component_opex_annual_usd'] + 
                  df['cost_component_new_energy_usd'] - 
                  df['cost_component_fuel_savings_usd'])
    
    diff = np.abs(df['total_cost_usd'] - calc_total)
    if diff.max() > 1.0: # allow $1 diff
        errors.append(f"MATH: Total Cost mismatch. Max diff: ${diff.max()}")

    if not errors:
        print("SUCCESS: All logic checks passed!")
    else:
        print("ERRORS FOUND:")
        for e in errors:
            print(e)
            
check_logic()
