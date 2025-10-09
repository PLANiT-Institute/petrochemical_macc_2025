#!/usr/bin/env python3
"""
Quick visualization of integrated model results
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (16, 10)

# Load results
output_dir = Path('integrated_outputs_v2')

baseline = pd.read_csv(output_dir / 'baseline_2025_totals.csv')
macc = pd.read_csv(output_dir / 'macc_wedges.csv')
scenarios = pd.read_csv(output_dir / 'results_by_scenario.csv')

# Load pathway data
pathway_a = pd.read_csv(output_dir / 'pathway_yearly_Scenario_A_Budget.csv')
pathway_b = pd.read_csv(output_dir / 'pathway_yearly_Scenario_B_Point_Targets.csv')
pathway_c = pd.read_csv(output_dir / 'pathway_yearly_Scenario_C_Linear.csv')

# Create visualization
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('Integrated Petrochemical Cost Optimization Model - Results Summary',
             fontsize=16, fontweight='bold', y=0.995)

# 1. Baseline Validation
ax = axes[0, 0]
baseline_metrics = baseline[baseline['metric'].isin([
    'total_emissions', 'scope1_emissions', 'scope2_emissions'
])]
ax.barh(baseline_metrics['metric'], baseline_metrics['value'], alpha=0.7)
ax.set_xlabel('MtCO₂')
ax.set_title('Baseline Emissions (2025)\nTotal: 52.0 MtCO₂')
ax.set_xlim(0, 60)
for i, row in baseline_metrics.iterrows():
    ax.text(row['value'] + 1, i, f"{row['value']:.1f}", va='center')

# 2. Emission Pathways - All Scenarios
ax = axes[0, 1]
ax.plot(pathway_a['year'], pathway_a['total_emissions_mtco2'],
        'o-', label='Scenario A: Budget', linewidth=2, markersize=4)
ax.plot(pathway_b['year'], pathway_b['total_emissions_mtco2'],
        's-', label='Scenario B: Point Targets', linewidth=2, markersize=4)
ax.plot(pathway_c['year'], pathway_c['total_emissions_mtco2'],
        '^-', label='Scenario C: Linear', linewidth=2, markersize=4)

# Plot targets for Scenario B
targets_b = pathway_b[pathway_b['target_emissions_mtco2'].notna()]
ax.scatter(targets_b['year'], targets_b['target_emissions_mtco2'],
          color='red', s=100, marker='*', label='Targets (B)', zorder=5)

ax.set_xlabel('Year')
ax.set_ylabel('Emissions (MtCO₂)')
ax.set_title('Emission Pathways (2025-2050)')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 60)

# 3. MACC Curve for 2050
ax = axes[0, 2]
macc_2050 = macc[macc['target_year'] == 2050].sort_values('marginal_cost_usd_tco2')
if len(macc_2050) > 0:
    ax.bar(range(len(macc_2050)), macc_2050['abatement_mtco2'],
           width=0.8, alpha=0.7)
    ax.set_xlabel('Technology Wedge')
    ax.set_ylabel('Abatement (MtCO₂/yr)')
    ax.set_title('MACC 2050 - Abatement Potential')
    ax.set_xticks(range(len(macc_2050)))
    ax.set_xticklabels([t[:15] for t in macc_2050['technology']], rotation=45, ha='right')

# 4. Scope 1 vs Scope 2 Evolution (Scenario B)
ax = axes[1, 0]
ax.fill_between(pathway_b['year'], 0, pathway_b['scope1_mtco2'],
                alpha=0.6, label='Scope 1', color='#FF6B6B')
ax.fill_between(pathway_b['year'], pathway_b['scope1_mtco2'],
                pathway_b['scope1_mtco2'] + pathway_b['scope2_mtco2'],
                alpha=0.6, label='Scope 2', color='#4ECDC4')
ax.set_xlabel('Year')
ax.set_ylabel('Emissions (MtCO₂)')
ax.set_title('Scope 1 & 2 Evolution (Scenario B)')
ax.legend()
ax.grid(True, alpha=0.3)

# 5. Scenario Comparison
ax = axes[1, 1]
width = 0.35
x = range(len(scenarios))
ax.bar([i - width/2 for i in x], scenarios['final_emissions_2050'],
       width, label='Final 2050 Emissions', alpha=0.7)
ax.bar([i + width/2 for i in x], scenarios['total_abatement_mtco2'],
       width, label='Total Abatement', alpha=0.7)
ax.set_ylabel('MtCO₂')
ax.set_title('Scenario Comparison')
ax.set_xticks(x)
ax.set_xticklabels([s.replace('_', '\n') for s in scenarios['scenario']], fontsize=8)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# 6. Summary Statistics
ax = axes[1, 2]
ax.axis('off')

summary_text = f"""
INTEGRATED MODEL SUMMARY

Baseline (2025):
  • Total Emissions: 52.0 MtCO₂
  • Scope 1: 50.2 MtCO₂ (96.6%)
  • Scope 2: 1.8 MtCO₂ (3.4%)
  • Total Energy: 62.8 Mtoe
  • Facilities: 87

Scenarios Optimized: 3
  ✓ Scenario A: Budget (780 MtCO₂)
  ✓ Scenario B: Point Targets
  ✓ Scenario C: Linear to Zero

Technologies: 1 configured
  • Bio-Naphtha (ready)
  • Framework for 5 more

MACC Analysis:
  • Years: 2030, 2040, 2050
  • Total Potential: 32.9 MtCO₂/yr

Outputs Generated:
  ✓ baseline_2025_totals.csv
  ✓ macc_wedges.csv
  ✓ pathway_yearly_*.csv (×3)
  ✓ results_by_scenario.csv

Status: ✅ Operational
Version: 2.0 Enhanced
"""

ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
        fontsize=10, verticalalignment='top', family='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.tight_layout()
plt.savefig('integrated_outputs_v2/model_results_summary.png',
            dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Saved: integrated_outputs_v2/model_results_summary.png")

# Print summary
print("\n" + "=" * 70)
print("VISUALIZATION COMPLETE")
print("=" * 70)
print(f"📊 Baseline: {baseline[baseline['metric']=='total_emissions']['value'].values[0]:.1f} MtCO₂")
print(f"🎯 Scenarios: {len(scenarios)}")
print(f"📈 MACC wedges: {len(macc)}")
print(f"📁 Summary chart: integrated_outputs_v2/model_results_summary.png")
print("=" * 70)
