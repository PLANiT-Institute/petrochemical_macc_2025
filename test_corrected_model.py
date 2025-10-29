"""
Test the corrected optimization model (V2)
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.optimization_v2 import CostOptimizerV2

def test_corrected_model():
    """Test the corrected model with Policy Target scenario"""

    print("="*80)
    print("TESTING CORRECTED MODEL (V2)")
    print("="*80)
    print()
    print("Changes implemented:")
    print("1. NCC-H2 and NCC-Electricity are now mutually exclusive")
    print("2. Model selects cheaper option each year")
    print("3. Once selected, choice persists (irreversibility)")
    print("4. Facility allocation prevents double-counting")
    print()
    print("="*80)
    print()

    # Initialize corrected optimizer
    optimizer = CostOptimizerV2(
        baseline_output='outputs/module_01',
        macc_output='outputs/module_02',
        output_dir='outputs/module_03_v2',  # Save to new directory
        scenario_file='data/emission_scenarios_clean.csv'
    )

    # Run Policy Target scenario only
    print("\n" + "="*80)
    print("RUNNING POLICY TARGET SCENARIO")
    print("="*80)

    scenario_name = 'Policy_Target'
    df_deployment = optimizer.optimize_scenario(scenario_name)

    # Save deployment results
    from modules.utils import save_csv_output
    save_csv_output(df_deployment,
                   Path('outputs/module_03_v2') / f'{scenario_name.lower()}_deployment_corrected.csv')

    # Create facility allocation
    df_allocation = optimizer.create_facility_level_allocation(scenario_name, df_deployment)

    # Print summary
    print("\n" + "="*80)
    print("CORRECTED MODEL RESULTS SUMMARY")
    print("="*80)

    final_year = df_deployment[df_deployment['year'] == 2050].iloc[0]

    print("\n2050 Deployment:")
    print(f"  Heat Pump:        {final_year['heat_pump_mt']:>10.2f} MtCO2")
    print(f"  NCC-H2:           {final_year['ncc_h2_mt']:>10.2f} MtCO2")
    print(f"  NCC-Electricity:  {final_year['ncc_elec_mt']:>10.2f} MtCO2")
    print(f"  RE PPA:           {final_year['re_ppa_mt']:>10.2f} MtCO2")
    print(f"  ─────────────────────────────")
    print(f"  Total Abatement:  {final_year['total_deployed_mt']:>10.2f} MtCO2")

    print(f"\nEmissions:")
    print(f"  BAU 2050:         {final_year['bau_mt']:>10.2f} MtCO2")
    print(f"  Actual 2050:      {final_year['actual_emissions_mt']:>10.2f} MtCO2")
    reduction_pct = ((final_year['bau_mt'] - final_year['actual_emissions_mt']) / final_year['bau_mt']) * 100
    print(f"  Reduction:        {reduction_pct:>10.1f}%")

    print(f"\nInvestment:")
    print(f"  Total CAPEX:      ${final_year['cumulative_capex_musd']/1000:>10.2f} Billion")

    print(f"\nEnergy Impacts:")
    print(f"  H2 Consumption:   {final_year['h2_consumption_kt']:>10.1f} kt/year")
    print(f"  Elec Increase:    {final_year['electricity_consumption_increase_twh']:>10.1f} TWh/year")

    # Check for negative emissions in facility allocation
    negative_count = (df_allocation['emissions_2050_kt'] < 0).sum()
    if negative_count == 0:
        print(f"\n✓ SUCCESS: No negative emissions in facility allocation!")
    else:
        print(f"\n⚠️  WARNING: {negative_count} facilities still have negative emissions")

    # Check abatement percentage
    max_abatement_pct = (df_allocation['abatement_mt'] * 1000 / df_allocation['total_emissions_kt']).max()
    print(f"✓ Maximum abatement percentage: {max_abatement_pct*100:.1f}%")

    if max_abatement_pct > 1.0:
        print(f"⚠️  WARNING: Some facilities have >100% abatement!")
    else:
        print(f"✓ SUCCESS: All facilities have ≤100% abatement")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print(f"\nOutputs saved to: outputs/module_03_v2/")

    return optimizer, df_deployment, df_allocation

if __name__ == '__main__':
    optimizer, df_deployment, df_allocation = test_corrected_model()
