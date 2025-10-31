"""
지역별 주요 결과 표 생성 - 최종 버전
"""

import pandas as pd

print("="*80)
print("지역별 주요 결과 표 생성")
print("="*80)

# 1. Baseline 데이터 로드
print("\n1. Baseline 데이터 로드...")
df_baseline = pd.read_csv('outputs/scenarios_shaheen_ncc_elec/module_01_baseline/baseline_2025_detailed.csv')

print(f"   총 시설 수: {len(df_baseline)}개")
print(f"   총 배출량: {df_baseline['total_emissions_kt'].sum():.1f} kt ({df_baseline['total_emissions_kt'].sum()/1000:.1f} Mt)")

# 2. Demand growth 데이터
print("\n2. 수요 성장 데이터 로드...")
df_growth = pd.read_csv('data/demand_growth_trajectory_scenarios.csv')
multiplier_2050 = df_growth[df_growth['year'] == 2050]['scenario_shaheen'].iloc[0]
print(f"   2050 용량 배수 (Shaheen): {multiplier_2050:.3f}")

# 3. 시나리오 결과
print("\n3. 시나리오 결과 로드...")
df_summary = pd.read_csv('outputs/scenarios_comparison_6scenarios/summary.csv')
shaheen_elec = df_summary[df_summary['scenario_id'] == 'shaheen_ncc_elec'].iloc[0]

print(f"   Shaheen + NCC-Elec:")
print(f"   - BAU 2050: {shaheen_elec['bau_emissions_2050_mt']:.1f} Mt")
print(f"   - 비용: ${shaheen_elec['cost_2050_billion_usd']:.1f}B")
print(f"   - NCC-Elec: {shaheen_elec['ncc_elec_mt']:.1f} Mt")
print(f"   - RE: {shaheen_elec['re_ppa_mt']:.1f} Mt")
print(f"   - Heat Pump: {shaheen_elec['heat_pump_mt']:.1f} Mt")
print(f"   - 전력 증가: {shaheen_elec['electricity_increase_twh']:.1f} TWh")

# 4. 지역별 집계
print("\n4. 지역별 집계...")

# NCC 여부 판정
df_baseline['is_ncc'] = df_baseline['product'].isin(['Ethylene', 'Propylene', 'Butadiene'])

# 전체 NCC 용량
total_ncc_capacity_2025 = df_baseline[df_baseline['is_ncc']]['capacity_kt'].sum()
total_ncc_capacity_2050 = total_ncc_capacity_2025 * multiplier_2050

# NCC 제외 전력 배출량
non_ncc_elec_emissions_kt = df_baseline[~df_baseline['is_ncc']]['emissions_electricity_kt'].sum()

regional_data = []

for location in sorted(df_baseline['location'].unique()):
    df_loc = df_baseline[df_baseline['location'] == location].copy()

    # 기본 정보
    n_facilities = len(df_loc)
    n_companies = df_loc['company'].nunique()

    # 배출량
    baseline_emissions_kt = df_loc['total_emissions_kt'].sum()
    baseline_emissions_mt = baseline_emissions_kt / 1000
    bau_2050_mt = baseline_emissions_mt * multiplier_2050

    # NCC
    df_ncc = df_loc[df_loc['is_ncc']]
    ncc_capacity_2025 = df_ncc['capacity_kt'].sum()
    ncc_capacity_2050 = ncc_capacity_2025 * multiplier_2050

    # NCC-Elec RE 배분 (NCC 용량 기준)
    if total_ncc_capacity_2050 > 0:
        ncc_share = ncc_capacity_2050 / total_ncc_capacity_2050
    else:
        ncc_share = 0
    ncc_elec_re_twh = shaheen_elec['electricity_increase_twh'] * ncc_share

    # Grid->RE 배분 (NCC 제외 전력 배출량 기준)
    non_ncc_elec_kt = df_loc[~df_loc['is_ncc']]['emissions_electricity_kt'].sum()
    if non_ncc_elec_emissions_kt > 0:
        grid_re_share = non_ncc_elec_kt / non_ncc_elec_emissions_kt
    else:
        grid_re_share = 0

    grid_re_mt = shaheen_elec['re_ppa_mt'] * grid_re_share

    # Mt를 TWh로 변환
    grid_ef_2025 = 0.436  # tCO2/MWh
    grid_re_twh = grid_re_mt / grid_ef_2025

    total_re_twh = ncc_elec_re_twh + grid_re_twh

    # 필요 RE 설비 (가동률 30%)
    required_gw = total_re_twh * 1000 / (365 * 24 * 0.3)

    regional_data.append({
        'Region': location,
        'Facilities': n_facilities,
        'Companies': n_companies,
        'Baseline_2025_Mt': baseline_emissions_mt,
        'BAU_2050_Mt': bau_2050_mt,
        'NCC_Cap_2050_kt': ncc_capacity_2050,
        'NCC_Elec_RE_TWh': ncc_elec_re_twh,
        'Grid_RE_TWh': grid_re_twh,
        'Total_RE_TWh': total_re_twh,
        'RE_Capacity_GW': required_gw,
    })

df_regional = pd.DataFrame(regional_data)
df_regional = df_regional.sort_values('Total_RE_TWh', ascending=False)

# 비율 계산
total_re = df_regional['Total_RE_TWh'].sum()
df_regional['RE_Share_Pct'] = (df_regional['Total_RE_TWh'] / total_re * 100)

print("\n" + "="*80)
print("### 마크다운 표: 지역별 주요 결과 (Shaheen + NCC-Elec, 2050)")
print("="*80)

print("\n| 지역 | 시설 수 | 기업 수 | 2025<br/>배출량 (Mt) | 2050 BAU<br/>배출량 (Mt) | NCC 생산<br/>능력 (kt/yr) | NCC-Elec<br/>RE (TWh) | Grid→RE<br/>(TWh) | 총 RE<br/>(TWh) | RE 비중<br/>(%) | 필요 RE<br/>설비 (GW) |")
print("|------|---------|---------|---------------------|--------------------------|--------------------------|----------------------|------------------|----------------|---------------|---------------------|")

for _, row in df_regional.iterrows():
    print(f"| **{row['Region']}** | {int(row['Facilities'])} | {int(row['Companies'])} | {row['Baseline_2025_Mt']:.1f} | {row['BAU_2050_Mt']:.1f} | {row['NCC_Cap_2050_kt']:.0f} | {row['NCC_Elec_RE_TWh']:.1f} | {row['Grid_RE_TWh']:.1f} | {row['Total_RE_TWh']:.1f} | {row['RE_Share_Pct']:.1f}% | {row['RE_Capacity_GW']:.1f} |")

# 합계
print(f"| **전체** | **{df_regional['Facilities'].sum()}** | **{df_baseline['company'].nunique()}** | **{df_regional['Baseline_2025_Mt'].sum():.1f}** | **{df_regional['BAU_2050_Mt'].sum():.1f}** | **{df_regional['NCC_Cap_2050_kt'].sum():.0f}** | **{df_regional['NCC_Elec_RE_TWh'].sum():.1f}** | **{df_regional['Grid_RE_TWh'].sum():.1f}** | **{df_regional['Total_RE_TWh'].sum():.1f}** | **100.0%** | **{df_regional['RE_Capacity_GW'].sum():.1f}** |")

print("\n" + "="*80)
print("### 주요 4개 지역 상세")
print("="*80)

top4 = df_regional.head(4)

for idx, (_, row) in enumerate(top4.iterrows(), 1):
    print(f"\n#### {idx}. {row['Region']}")
    print(f"- **시설 및 기업**: {int(row['Facilities'])}개 시설, {int(row['Companies'])}개 기업")
    print(f"- **2050 BAU 배출량**: {row['BAU_2050_Mt']:.1f} Mt CO₂")
    print(f"- **NCC 생산능력** (2050): {row['NCC_Cap_2050_kt']:.0f} kt/yr")
    print(f"- **재생에너지 필요량** (2050):")
    print(f"  - NCC-Elec RE: {row['NCC_Elec_RE_TWh']:.1f} TWh (신규 전력)")
    print(f"  - Grid→RE: {row['Grid_RE_TWh']:.1f} TWh (기존 전력 전환)")
    print(f"  - **총**: {row['Total_RE_TWh']:.1f} TWh (전국의 {row['RE_Share_Pct']:.1f}%)")
    print(f"- **필요 재생설비**: 약 {row['RE_Capacity_GW']:.1f} GW (가동률 30% 가정)")

# CSV 저장
output_file = 'outputs/regional_summary_table.csv'
df_regional.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n\n결과 저장: {output_file}")

print("\n" + "="*80)
print("완료!")
print("="*80)
