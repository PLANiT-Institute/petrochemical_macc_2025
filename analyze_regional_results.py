"""
지역별 주요 결과 분석
"""

import pandas as pd
import numpy as np

# 시설 데이터베이스 로드
df_facilities = pd.read_csv('data/facility_database.csv')

# 에너지 집약도 로드
df_energy = pd.read_csv('data/energy_intensities.csv')

# 배출 계수 로드
df_ef = pd.read_csv('data/emission_factors.csv')

# 시나리오 요약 로드
df_summary = pd.read_csv('outputs/scenarios_comparison_6scenarios/summary.csv')

# Shaheen + NCC-Elec 시나리오 선택
shaheen_elec = df_summary[df_summary['scenario_id'] == 'shaheen_ncc_elec'].iloc[0]

print("=" * 80)
print("지역별 주요 결과 분석 (Shaheen + NCC-Electricity)")
print("=" * 80)

# 시설 데이터와 에너지 집약도 병합
df = df_facilities.merge(
    df_energy[['product', 'Naphtha_GJ_per_tonne', 'Electricity_kWh_per_tonne',
               'LNG_GJ_per_tonne', 'Fuel_Gas_GJ_per_tonne', 'Byproduct_Gas_GJ_per_tonne']],
    on='product',
    how='left'
)

# 배출계수
ef_naphtha = 0.0542  # tCO2/GJ
ef_electricity = 0.436  # tCO2/MWh (2025)
ef_lng = 0.0561  # tCO2/GJ
ef_fuel_gas = 0.050  # tCO2/GJ
ef_byproduct = 0.048  # tCO2/GJ

# 각 시설의 배출량 계산
df['naphtha_emissions_kt'] = df['capacity_kt'] * df['Naphtha_GJ_per_tonne'] * ef_naphtha / 1000
df['electricity_emissions_kt'] = df['capacity_kt'] * df['Electricity_kWh_per_tonne'] / 1000 * ef_electricity / 1000
df['lng_emissions_kt'] = df['capacity_kt'] * df['LNG_GJ_per_tonne'] * ef_lng / 1000
df['fuel_gas_emissions_kt'] = df['capacity_kt'] * df['Fuel_Gas_GJ_per_tonne'] * ef_fuel_gas / 1000
df['byproduct_emissions_kt'] = df['capacity_kt'] * df['Byproduct_Gas_GJ_per_tonne'] * ef_byproduct / 1000

df['total_emissions_kt'] = (df['naphtha_emissions_kt'] + df['electricity_emissions_kt'] +
                             df['lng_emissions_kt'] + df['fuel_gas_emissions_kt'] +
                             df['byproduct_emissions_kt'])

# NCC 여부 판정
df['is_ncc'] = df['process'] == 'Naphtha Cracker'

# 지역별 집계
regional_summary = []

for location in df['location'].unique():
    df_region = df[df['location'] == location]

    # 기본 정보
    n_facilities = len(df_region)
    n_companies = df_region['company'].nunique()
    total_capacity = df_region['capacity_kt'].sum()

    # 배출량
    baseline_emissions = df_region['total_emissions_kt'].sum()

    # NCC 관련
    ncc_facilities = df_region[df_region['is_ncc']]
    ncc_capacity = ncc_facilities['capacity_kt'].sum()
    ncc_emissions = ncc_facilities['total_emissions_kt'].sum()

    # 전력 소비량 (MWh)
    electricity_mwh = df_region['capacity_kt'].sum() * df_region['Electricity_kWh_per_tonne'].mean() / 1000

    # 2050년 재생에너지 필요량 추정
    # NCC-Elec RE: NCC 용량 기준으로 5.0 MWh/ton 전력 필요
    ncc_elec_re_twh = ncc_capacity * 5.0 / 1000  # TWh

    # Grid->RE: 기존 전력 사용량의 재생에너지 전환 (NCC 제외)
    non_ncc_electricity_mwh = df_region[~df_region['is_ncc']]['capacity_kt'].sum() * \
                              df_region[~df_region['is_ncc']]['Electricity_kWh_per_tonne'].mean() / 1000
    grid_re_twh = non_ncc_electricity_mwh / 1e6  # TWh

    total_re_twh = ncc_elec_re_twh + grid_re_twh

    regional_summary.append({
        'Region': location,
        'Facilities': n_facilities,
        'Companies': n_companies,
        'Total_Capacity_kt': total_capacity,
        'Baseline_Emissions_kt': baseline_emissions,
        'NCC_Capacity_kt': ncc_capacity,
        'NCC_Emissions_kt': ncc_emissions,
        'NCC_Elec_RE_TWh': ncc_elec_re_twh,
        'Grid_RE_TWh': grid_re_twh,
        'Total_RE_TWh': total_re_twh,
    })

df_regional = pd.DataFrame(regional_summary)
df_regional = df_regional.sort_values('Total_RE_TWh', ascending=False)

print("\n### 지역별 기본 정보")
print(df_regional[['Region', 'Facilities', 'Companies', 'Total_Capacity_kt',
                    'Baseline_Emissions_kt']].to_string(index=False))

print("\n### 지역별 NCC 현황")
print(df_regional[['Region', 'NCC_Capacity_kt', 'NCC_Emissions_kt']].to_string(index=False))

print("\n### 지역별 재생에너지 필요량 (2050, Shaheen + NCC-Elec)")
print(df_regional[['Region', 'NCC_Elec_RE_TWh', 'Grid_RE_TWh', 'Total_RE_TWh']].to_string(index=False))

# 주요 4개 지역
print("\n" + "=" * 80)
print("주요 4개 지역 상세 분석")
print("=" * 80)

top4_regions = df_regional.head(4)

for _, row in top4_regions.iterrows():
    region = row['Region']
    print(f"\n### {region}")
    print(f"- 시설 수: {int(row['Facilities'])}개")
    print(f"- 기업 수: {int(row['Companies'])}개")
    print(f"- 총 생산능력: {row['Total_Capacity_kt']:.0f} kt/yr")
    print(f"- 기준 배출량: {row['Baseline_Emissions_kt']:.1f} kt CO₂")
    print(f"- NCC 용량: {row['NCC_Capacity_kt']:.0f} kt/yr")
    print(f"- 2050 재생에너지:")
    print(f"  - NCC-Elec RE: {row['NCC_Elec_RE_TWh']:.1f} TWh")
    print(f"  - Grid→RE: {row['Grid_RE_TWh']:.1f} TWh")
    print(f"  - 총: {row['Total_RE_TWh']:.1f} TWh")

    # 필요 재생설비 용량 (가동률 30% 가정)
    required_gw = row['Total_RE_TWh'] * 1000 / (365 * 24 * 0.3)
    print(f"- 필요 재생설비: 약 {required_gw:.1f} GW (가동률 30% 가정)")

# 전체 합계
print("\n" + "=" * 80)
print("전국 총계")
print("=" * 80)
print(f"총 시설 수: {df_regional['Facilities'].sum():.0f}개")
print(f"총 기업 수: {df['company'].nunique()}개")
print(f"총 생산능력: {df_regional['Total_Capacity_kt'].sum():.0f} kt/yr")
print(f"총 기준 배출량: {df_regional['Baseline_Emissions_kt'].sum():.1f} kt CO₂ ({df_regional['Baseline_Emissions_kt'].sum()/1000:.1f} Mt)")
print(f"총 NCC 용량: {df_regional['NCC_Capacity_kt'].sum():.0f} kt/yr")
print(f"\n2050 재생에너지 필요량:")
print(f"- NCC-Elec RE: {df_regional['NCC_Elec_RE_TWh'].sum():.1f} TWh")
print(f"- Grid→RE: {df_regional['Grid_RE_TWh'].sum():.1f} TWh")
print(f"- 총: {df_regional['Total_RE_TWh'].sum():.1f} TWh")
total_re = df_regional['Total_RE_TWh'].sum()
total_gw = total_re * 1000 / (365 * 24 * 0.3)
print(f"- 필요 재생설비: 약 {total_gw:.1f} GW (가동률 30% 가정)")

# CSV로 저장
df_regional.to_csv('outputs/regional_analysis_shaheen_ncc_elec.csv', index=False)
print(f"\n결과 저장: outputs/regional_analysis_shaheen_ncc_elec.csv")
