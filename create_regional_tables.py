"""
지역별 주요 결과 표 생성 - 모듈 기반
"""

import sys
import pandas as pd
import numpy as np

# 모듈 임포트
from modules.baseline import BaselineAnalyzer
from modules.demand_growth import DemandGrowthScenarios

print("="*80)
print("지역별 주요 결과 표 생성")
print("="*80)

# Baseline 계산
print("\n1. Baseline 데이터 계산...")
baseline_analyzer = BaselineAnalyzer()
df_baseline = baseline_analyzer.df_baseline.copy()

print(f"   총 시설 수: {len(df_baseline)}개")
print(f"   총 배출량: {df_baseline['total_emissions_kt'].sum():.1f} kt ({df_baseline['total_emissions_kt'].sum()/1000:.1f} Mt)")

# Demand growth 적용 (Shaheen 시나리오)
print("\n2. 수요 성장 시나리오 적용...")
demand_scenarios = DemandGrowthScenarios()
df_growth = demand_scenarios.get_scenario('shaheen')

# 2050년 capacity multiplier
multiplier_2050 = df_growth[df_growth['year'] == 2050]['cumulative_capacity_multiplier'].iloc[0]
print(f"   2050 용량 배수: {multiplier_2050:.3f}")

# 시나리오 요약 데이터
df_summary = pd.read_csv('outputs/scenarios_comparison_6scenarios/summary.csv')
shaheen_elec = df_summary[df_summary['scenario_id'] == 'shaheen_ncc_elec'].iloc[0]
shaheen_h2 = df_summary[df_summary['scenario_id'] == 'shaheen_ncc_h2'].iloc[0]

print(f"\n3. Shaheen + NCC-Electricity 시나리오")
print(f"   BAU 배출량 (2050): {shaheen_elec['bau_emissions_2050_mt']:.1f} Mt")
print(f"   2050 배출량: {shaheen_elec['emissions_2050_mt']:.1f} Mt")
print(f"   총 비용: ${shaheen_elec['cost_2050_billion_usd']:.1f}B")
print(f"   NCC-Elec: {shaheen_elec['ncc_elec_mt']:.1f} Mt")
print(f"   RE: {shaheen_elec['re_ppa_mt']:.1f} Mt")
print(f"   Heat Pump: {shaheen_elec['heat_pump_mt']:.1f} Mt")
print(f"   전력 증가: {shaheen_elec['electricity_increase_twh']:.1f} TWh")

# 지역별 집계
print("\n4. 지역별 집계...")

# NCC 여부 판정
df_baseline['is_ncc'] = df_baseline['product'].isin(['Ethylene', 'Propylene', 'Butadiene'])

regional_data = []

for location in df_baseline['location'].unique():
    df_loc = df_baseline[df_baseline['location'] == location].copy()

    # 기본 정보
    n_facilities = len(df_loc)
    n_companies = df_loc['company'].nunique()

    # 배출량 (2025 기준)
    baseline_emissions_kt = df_loc['total_emissions_kt'].sum()
    baseline_emissions_mt = baseline_emissions_kt / 1000

    # 2050 BAU 배출량 (수요 성장 반영)
    bau_2050_mt = baseline_emissions_mt * multiplier_2050

    # NCC 관련
    df_ncc = df_loc[df_loc['is_ncc']]
    ncc_capacity_2025 = df_ncc['capacity_kt'].sum()
    ncc_capacity_2050 = ncc_capacity_2025 * multiplier_2050
    ncc_emissions_kt = df_ncc['total_emissions_kt'].sum()
    ncc_emissions_mt = ncc_emissions_kt / 1000
    ncc_emissions_2050_mt = ncc_emissions_mt * multiplier_2050

    # NCC-Elec RE: 5.0 MWh/ton ethylene equivalent
    # 지역 비율로 배분
    regional_ncc_share = ncc_capacity_2050 / df_baseline[df_baseline['is_ncc']]['capacity_kt'].sum() / multiplier_2050 * multiplier_2050
    ncc_elec_re_twh = shaheen_elec['electricity_increase_twh'] * regional_ncc_share

    # Grid->RE: RE_PPA 배출 감축량 기반
    # 전력 배출량 기준으로 배분
    elec_emissions_kt = df_loc['emissions_electricity_kt'].sum()
    total_elec_emissions = df_baseline['emissions_electricity_kt'].sum()

    if total_elec_emissions > 0:
        regional_re_share = elec_emissions_kt / total_elec_emissions
    else:
        regional_re_share = 0

    # NCC-Elec 시나리오에서는 NCC 제외
    if ncc_capacity_2050 > 0:
        # NCC가 있는 지역은 non-NCC만 RE 적용
        non_ncc_elec_kt = df_loc[~df_loc['is_ncc']]['emissions_electricity_kt'].sum()
        total_non_ncc_elec = df_baseline[~df_baseline['is_ncc']]['emissions_electricity_kt'].sum()
        if total_non_ncc_elec > 0:
            regional_re_share = non_ncc_elec_kt / total_non_ncc_elec
        else:
            regional_re_share = 0

    grid_re_mt = shaheen_elec['re_ppa_mt'] * regional_re_share

    # Mt를 TWh로 변환 (grid EF 2025 = 0.436 tCO2/MWh)
    grid_ef_2025 = 0.436
    grid_re_twh = grid_re_mt / grid_ef_2025

    total_re_twh = ncc_elec_re_twh + grid_re_twh

    # 필요 재생설비 (가동률 30%)
    required_gw = total_re_twh * 1000 / (365 * 24 * 0.3)

    regional_data.append({
        'Region': location,
        'Facilities': n_facilities,
        'Companies': n_companies,
        'Baseline_Emissions_2025_Mt': baseline_emissions_mt,
        'BAU_Emissions_2050_Mt': bau_2050_mt,
        'NCC_Capacity_2050_kt': ncc_capacity_2050,
        'NCC_Emissions_2050_Mt': ncc_emissions_2050_mt,
        'NCC_Elec_RE_TWh': ncc_elec_re_twh,
        'Grid_RE_TWh': grid_re_twh,
        'Total_RE_TWh': total_re_twh,
        'Required_RE_Capacity_GW': required_gw,
    })

df_regional = pd.DataFrame(regional_data)
df_regional = df_regional.sort_values('Total_RE_TWh', ascending=False)

# 비율 계산
total_re = df_regional['Total_RE_TWh'].sum()
df_regional['RE_Share_Pct'] = (df_regional['Total_RE_TWh'] / total_re * 100)

print("\n" + "="*80)
print("### 표 1: 지역별 기본 현황 (2025 기준)")
print("="*80)

table1 = df_regional[['Region', 'Facilities', 'Companies',
                       'Baseline_Emissions_2025_Mt', 'BAU_Emissions_2050_Mt']].copy()
table1.columns = ['지역', '시설 수', '기업 수', '2025 배출량 (Mt)', '2050 BAU 배출량 (Mt)']

print("\n" + table1.to_string(index=False))

print("\n" + "="*80)
print("### 표 2: 지역별 NCC 현황 (2050, Shaheen 시나리오)")
print("="*80)

table2 = df_regional[['Region', 'NCC_Capacity_2050_kt', 'NCC_Emissions_2050_Mt']].copy()
table2.columns = ['지역', 'NCC 생산능력 (kt/yr)', 'NCC BAU 배출량 (Mt)']

print("\n" + table2.to_string(index=False))

print("\n" + "="*80)
print("### 표 3: 지역별 재생에너지 필요량 (2050, Shaheen + NCC-Elec)")
print("="*80)

table3 = df_regional[['Region', 'NCC_Elec_RE_TWh', 'Grid_RE_TWh',
                       'Total_RE_TWh', 'RE_Share_Pct', 'Required_RE_Capacity_GW']].copy()
table3.columns = ['지역', 'NCC-Elec RE (TWh)', 'Grid→RE (TWh)',
                   '총 RE (TWh)', '비중 (%)', '필요 RE 설비 (GW)']

print("\n" + table3.to_string(index=False))

print("\n" + "="*80)
print("### 주요 4개 지역 상세")
print("="*80)

top4 = df_regional.head(4)

for _, row in top4.iterrows():
    print(f"\n**{row['Region']}**")
    print(f"  • 시설: {int(row['Facilities'])}개 / 기업: {int(row['Companies'])}개")
    print(f"  • 2050 BAU 배출량: {row['BAU_Emissions_2050_Mt']:.1f} Mt")
    print(f"  • NCC 생산능력(2050): {row['NCC_Capacity_2050_kt']:.0f} kt/yr")
    print(f"  • 재생에너지 필요량:")
    print(f"    - NCC-Elec RE: {row['NCC_Elec_RE_TWh']:.1f} TWh")
    print(f"    - Grid→RE: {row['Grid_RE_TWh']:.1f} TWh")
    print(f"    - 총: {row['Total_RE_TWh']:.1f} TWh ({row['RE_Share_Pct']:.1f}%)")
    print(f"  • 필요 재생설비: 약 {row['Required_RE_Capacity_GW']:.1f} GW")

print("\n" + "="*80)
print("### 전국 총계")
print("="*80)

print(f"  • 총 시설: {df_regional['Facilities'].sum()}개")
print(f"  • 총 기업: {df_baseline['company'].nunique()}개")
print(f"  • 2025 배출량: {df_regional['Baseline_Emissions_2025_Mt'].sum():.1f} Mt")
print(f"  • 2050 BAU 배출량: {df_regional['BAU_Emissions_2050_Mt'].sum():.1f} Mt")
print(f"  • 2050 NCC 생산능력: {df_regional['NCC_Capacity_2050_kt'].sum():.0f} kt/yr")
print(f"  • 2050 재생에너지:")
print(f"    - NCC-Elec RE: {df_regional['NCC_Elec_RE_TWh'].sum():.1f} TWh")
print(f"    - Grid→RE: {df_regional['Grid_RE_TWh'].sum():.1f} TWh")
print(f"    - 총: {df_regional['Total_RE_TWh'].sum():.1f} TWh")
print(f"  • 필요 재생설비: 약 {df_regional['Required_RE_Capacity_GW'].sum():.1f} GW")

# 마크다운 표 형식으로 출력
print("\n" + "="*80)
print("### 마크다운 형식 표")
print("="*80)

print("\n**표 1: 지역별 기본 현황 및 재생에너지 필요량 (Shaheen + NCC-Elec, 2050)**\n")
print("| 지역 | 시설 수 | 기업 수 | 2050 BAU<br/>배출량 (Mt) | NCC 생산능력<br/>(kt/yr) | NCC-Elec RE<br/>(TWh) | Grid→RE<br/>(TWh) | 총 RE<br/>(TWh) | RE 비중<br/>(%) | 필요 RE 설비<br/>(GW) |")
print("|------|---------|---------|--------------------------|--------------------------|----------------------|------------------|----------------|---------------|---------------------|")

for _, row in df_regional.iterrows():
    print(f"| {row['Region']} | {int(row['Facilities'])} | {int(row['Companies'])} | {row['BAU_Emissions_2050_Mt']:.1f} | {row['NCC_Capacity_2050_kt']:.0f} | {row['NCC_Elec_RE_TWh']:.1f} | {row['Grid_RE_TWh']:.1f} | {row['Total_RE_TWh']:.1f} | {row['RE_Share_Pct']:.1f}% | {row['Required_RE_Capacity_GW']:.1f} |")

print(f"| **전체** | **{df_regional['Facilities'].sum()}** | **{df_baseline['company'].nunique()}** | **{df_regional['BAU_Emissions_2050_Mt'].sum():.1f}** | **{df_regional['NCC_Capacity_2050_kt'].sum():.0f}** | **{df_regional['NCC_Elec_RE_TWh'].sum():.1f}** | **{df_regional['Grid_RE_TWh'].sum():.1f}** | **{df_regional['Total_RE_TWh'].sum():.1f}** | **100.0%** | **{df_regional['Required_RE_Capacity_GW'].sum():.1f}** |")

# CSV 저장
output_file = 'outputs/regional_summary_table.csv'
df_regional.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n\n결과 저장: {output_file}")

print("\n" + "="*80)
print("완료!")
print("="*80)
