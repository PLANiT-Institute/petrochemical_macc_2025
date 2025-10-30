"""
생산량 시나리오 분석 스크립트
Analyze 3 production scenarios for Korean petrochemical industry
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load data
df_scenarios = pd.read_csv('data/demand_growth_trajectory_scenarios.csv')
df_baseline = pd.read_csv('outputs/module_01_corrected/baseline_2025_detailed.csv')

# Calculate baseline ethylene capacity
ethylene_baseline = df_baseline[df_baseline['product'] == 'Ethylene']
baseline_capacity_kt = ethylene_baseline['capacity_kt'].sum()
baseline_emissions_kt = ethylene_baseline['total_emissions_kt'].sum()
emission_intensity = baseline_emissions_kt / baseline_capacity_kt  # tCO2/ton

print("="*80)
print("생산량 시나리오 분석")
print("="*80)
print()

print(f"2025 베이스라인:")
print(f"  에틸렌 생산능력: {baseline_capacity_kt:,.0f} kt/year = {baseline_capacity_kt/1000:.2f} Mt/year")
print(f"  총 배출량:       {baseline_emissions_kt:,.0f} ktCO2/year = {baseline_emissions_kt/1000:.2f} MtCO2/year")
print(f"  배출원단위:      {emission_intensity:.3f} tCO2/ton ethylene")
print()

# Scenario definitions
scenarios = {
    'scenario_baseline': {
        'name': 'Baseline (현재 모델)',
        'description': '기존 성장 시나리오 (연평균 ~1% 성장)'
    },
    'scenario_shaheen': {
        'name': 'Shaheen (성장)',
        'description': 'S-Oil Shaheen 프로젝트 (+1.8 Mt, 2026), 이후 고정'
    },
    'scenario_restructure_25pct': {
        'name': '구조조정 25%',
        'description': '2026년 -3.7 Mt (25% 감축), 고정'
    },
    'scenario_restructure_40pct': {
        'name': '구조조정 40%',
        'description': '2040년까지 점진적 40% 감축'
    }
}

# Calculate production and emissions for each scenario
results = []

for scenario_col, scenario_info in scenarios.items():
    for idx, row in df_scenarios.iterrows():
        year = row['year']
        multiplier = row[scenario_col]

        capacity_kt = baseline_capacity_kt * multiplier
        emissions_kt = baseline_emissions_kt * multiplier

        results.append({
            'scenario': scenario_info['name'],
            'scenario_col': scenario_col,
            'year': year,
            'capacity_kt': capacity_kt,
            'capacity_mt': capacity_kt / 1000,
            'emissions_ktco2': emissions_kt,
            'emissions_mtco2': emissions_kt / 1000,
            'multiplier': multiplier
        })

df_results = pd.DataFrame(results)

# Display key years
print("시나리오별 생산량 및 배출량 (주요 연도):")
print()

key_years = [2025, 2026, 2030, 2035, 2040, 2050]

for year in key_years:
    print(f">>> {year}년:")
    df_year = df_results[df_results['year'] == year]

    for idx, row in df_year.iterrows():
        change_pct = (row['multiplier'] - 1.0) * 100
        print(f"  {row['scenario']:25s}: {row['capacity_mt']:>6.2f} Mt  ({row['emissions_mtco2']:>5.2f} MtCO2)  [{change_pct:+6.1f}%]")
    print()

# Summary table
print("="*80)
print("2050년 시나리오 비교")
print("="*80)
print()

df_2050 = df_results[df_results['year'] == 2050]

print(f"{'시나리오':<25s} {'생산량 (Mt)':>15s} {'BAU 배출 (MtCO2)':>20s} {'변화율':>10s}")
print("-" * 80)

for idx, row in df_2050.iterrows():
    change_pct = (row['multiplier'] - 1.0) * 100
    print(f"{row['scenario']:<25s} {row['capacity_mt']:>15.2f} {row['emissions_mtco2']:>20.2f} {change_pct:>9.1f}%")

print()

# Net-zero gap analysis
print("="*80)
print("2050 Net-Zero 달성 필요 감축량")
print("="*80)
print()

print(f"{'시나리오':<25s} {'BAU 배출':>15s} {'NCC-Elec (93%)':>18s} {'잔여 배출':>15s} {'필요 추가 감축':>18s}")
print("-" * 80)

for idx, row in df_2050.iterrows():
    bau_emissions = row['emissions_mtco2']
    ncc_elec_reduction = bau_emissions * 0.93  # 93% reduction
    remaining = bau_emissions - ncc_elec_reduction
    additional = remaining  # Need to reach zero

    print(f"{row['scenario']:<25s} {bau_emissions:>13.2f} Mt {ncc_elec_reduction:>15.2f} Mt {remaining:>13.2f} Mt {additional:>16.2f} Mt")

print()
print("* NCC-Electricity: 93% 감축 (전력 생애주기 배출 0.15 tCO2/ton 잔여)")
print("* 잔여 배출은 RE PPA 또는 CCS로 추가 감축 필요")
print()

# Investment comparison
print("="*80)
print("필요 투자 비교 (NCC-Electricity, 2030 기준)")
print("="*80)
print()

df_2030 = df_results[df_results['year'] == 2030]

capex_per_mtco2 = 1560  # M$/MtCO2 (2030)
abatement_per_ton = 2.11  # tCO2/ton ethylene

print(f"{'시나리오':<25s} {'생산량 (Mt)':>15s} {'감축량 (MtCO2)':>18s} {'CAPEX (억 USD)':>18s}")
print("-" * 80)

for idx, row in df_2030.iterrows():
    capacity_mt = row['capacity_mt']
    abatement_mtco2 = capacity_mt * abatement_per_ton  # MtCO2
    capex_musd = abatement_mtco2 * capex_per_mtco2  # M USD
    capex_billion = capex_musd / 100  # 억 USD

    print(f"{row['scenario']:<25s} {capacity_mt:>15.2f} {abatement_mtco2:>18.2f} {capex_billion:>18.1f}")

print()

# Create visualization
print("="*80)
print("시각화 생성 중...")
print("="*80)
print()

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Production capacity
ax1 = axes[0, 0]
for scenario_col, scenario_info in scenarios.items():
    df_scenario = df_results[df_results['scenario_col'] == scenario_col]
    ax1.plot(df_scenario['year'], df_scenario['capacity_mt'],
             linewidth=2.5, marker='o', markersize=4, label=scenario_info['name'])

ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('Ethylene Production (Mt/year)', fontsize=12, fontweight='bold')
ax1.set_title('에틸렌 생산량 시나리오 (2025-2050)', fontsize=14, fontweight='bold')
ax1.legend(loc='best', fontsize=10)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.axhline(y=baseline_capacity_kt/1000, color='gray', linestyle=':', linewidth=1.5, alpha=0.7, label='2025 Baseline')

# Plot 2: BAU Emissions
ax2 = axes[0, 1]
for scenario_col, scenario_info in scenarios.items():
    df_scenario = df_results[df_results['scenario_col'] == scenario_col]
    ax2.plot(df_scenario['year'], df_scenario['emissions_mtco2'],
             linewidth=2.5, marker='s', markersize=4, label=scenario_info['name'])

ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('BAU Emissions (MtCO2/year)', fontsize=12, fontweight='bold')
ax2.set_title('BAU 배출량 시나리오 (기술 전환 없을 시)', fontsize=14, fontweight='bold')
ax2.legend(loc='best', fontsize=10)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.axhline(y=0, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Net-Zero Target')

# Plot 3: Multiplier comparison
ax3 = axes[1, 0]
for scenario_col, scenario_info in scenarios.items():
    df_scenario = df_results[df_results['scenario_col'] == scenario_col]
    ax3.plot(df_scenario['year'], (df_scenario['multiplier'] - 1) * 100,
             linewidth=2.5, marker='^', markersize=4, label=scenario_info['name'])

ax3.set_xlabel('Year', fontsize=12, fontweight='bold')
ax3.set_ylabel('Change from 2025 Baseline (%)', fontsize=12, fontweight='bold')
ax3.set_title('2025년 대비 생산량 변화율', fontsize=14, fontweight='bold')
ax3.legend(loc='best', fontsize=10)
ax3.grid(True, alpha=0.3, linestyle='--')
ax3.axhline(y=0, color='black', linestyle='-', linewidth=1.5, alpha=0.7)

# Plot 4: 2050 comparison
ax4 = axes[1, 1]
df_2050_sorted = df_2050.sort_values('emissions_mtco2', ascending=False)

colors = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12']
bars = ax4.barh(df_2050_sorted['scenario'], df_2050_sorted['emissions_mtco2'], color=colors, alpha=0.8, edgecolor='black')

# Add NCC-Electricity reduction
for i, (idx, row) in enumerate(df_2050_sorted.iterrows()):
    bau = row['emissions_mtco2']
    after_ncc = bau * 0.07  # 93% reduction, 7% remaining
    ax4.barh(i, after_ncc, left=0, color='green', alpha=0.5, edgecolor='black', linewidth=1.5)

    # Add text
    ax4.text(bau/2, i, f"{bau:.1f} Mt", ha='center', va='center', fontweight='bold', fontsize=10)
    ax4.text(after_ncc/2, i, f"{after_ncc:.1f} Mt\n(NCC-Elec)", ha='center', va='center', fontsize=8, color='white')

ax4.set_xlabel('2050 Emissions (MtCO2/year)', fontsize=12, fontweight='bold')
ax4.set_title('2050년 시나리오별 배출량 (BAU vs NCC-Electricity)', fontsize=14, fontweight='bold')
ax4.grid(True, axis='x', alpha=0.3, linestyle='--')
ax4.axvline(x=0, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Net-Zero')

plt.tight_layout()

# Save
output_dir = Path('outputs/scenarios')
output_dir.mkdir(parents=True, exist_ok=True)
plt.savefig(output_dir / 'production_scenarios_comparison.png', dpi=300, bbox_inches='tight')
print(f"✓ 저장: {output_dir / 'production_scenarios_comparison.png'}")

# Save results
df_results.to_csv(output_dir / 'production_scenarios_results.csv', index=False)
print(f"✓ 저장: {output_dir / 'production_scenarios_results.csv'}")

print()
print("="*80)
print("분석 완료")
print("="*80)
