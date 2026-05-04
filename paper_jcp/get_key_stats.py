
import pandas as pd
from pathlib import Path

df = pd.read_csv('paper_jcp/results/jcp_consolidated_results.csv')

def get_stats(scenario, year):
    sub = df[(df['scenario'] == scenario) & (df['year'] == year)]
    total_cost = sub['total_cost_usd'].sum() / 1e9 # Bn USD
    total_abatement = sub['abatement_tco2'].sum() / 1e6 # MtCO2
    avg_mac = sub[sub['abatement_tco2']>0]['mac_usd_per_tco2'].mean()
    
    return total_cost, total_abatement, avg_mac

print("--- KEY STATS FOR MANUSCRIPT ---")
for year in [2030, 2050]:
    c1, a1, m1 = get_stats('S1_Baseline_Trends', year)
    c2, a2, m2 = get_stats('S2_NetZero_HighAmbition', year)
    
    print(f"Year {year}")
    print(f"  S1 (Baseline): Cost=${c1:.2f}B, Abatement={a1:.1f}Mt")
    print(f"  S2 (NetZero) : Cost=${c2:.2f}B, Abatement={a2:.1f}Mt, Avg MAC=${m2:.0f}/t")
    
    if year == 2050:
        print(f"  Cost Increase S2 vs S1: ${c2 - c1:.2f}B")
