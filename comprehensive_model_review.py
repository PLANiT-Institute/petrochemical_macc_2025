"""
전체 모델 철저 검토 - 전력 관련 로직 중심
Comprehensive Model Review - Focus on Electricity Logic
"""
import pandas as pd
from pathlib import Path

print("="*80)
print("한국 석유화학 MACC 모델 - 전체 검토")
print("="*80)
print()

# ============================================================================
# 1. 현재 전력 가격 데이터 확인
# ============================================================================
print("1. 전력 가격 데이터 검토")
print("="*80)
print()

# Grid electricity price
try:
    df_grid = pd.read_csv('data/grid_emission_trajectory.csv')
    print("Grid Emission Trajectory (data/grid_emission_trajectory.csv):")
    print(df_grid.head(10))
    print()
    print(f"Columns: {df_grid.columns.tolist()}")
    print()
except FileNotFoundError:
    print("⚠️  Grid emission trajectory file NOT FOUND")
    print()

# RE/PPA electricity price
print("RE/PPA Price Trajectory (data/re_price_trajectory.csv):")
df_re = pd.read_csv('data/re_price_trajectory.csv')
print(df_re[df_re['year'].isin([2025, 2030, 2040, 2050])].to_string(index=False))
print()

# Excel assumption
df_fuel = pd.read_excel('assumption.xlsx', sheet_name='fuel_price', header=0)
elec_row = df_fuel.iloc[1]
print("Excel Assumption - Electricity Price:")
for year in [2025, 2030, 2040, 2050]:
    print(f"  {year}: ${elec_row[year]:.2f}/MWh")
print()

print("⚠️  ISSUE DETECTED:")
print(f"  RE price file (2025): ${df_re[df_re['year']==2025]['re_price_usd_per_mwh'].values[0]:.2f}/MWh")
print(f"  Excel assumption (2025): ${elec_row[2025]:.2f}/MWh")
print(f"  → MISMATCH! Should use Excel values")
print()

# ============================================================================
# 2. Grid Emission Factor 확인
# ============================================================================
print("="*80)
print("2. Grid Emission Factor 검토")
print("="*80)
print()

try:
    df_grid = pd.read_csv('data/grid_emission_trajectory.csv')
    print("Current Grid Emission Trajectory:")
    print(df_grid[df_grid['year'].isin([2025, 2030, 2040, 2050])].to_string(index=False))
    print()

    ef_2050 = df_grid[df_grid['year'] == 2050]['grid_ef_tco2_per_mwh'].values[0]
    if ef_2050 == 0.0:
        print("⚠️  CRITICAL ISSUE: Grid EF goes to ZERO in 2050")
        print("   → This makes RE PPA worthless (no emission reduction)")
        print("   → Need realistic trajectory based on Korea's grid mix forecast")
    print()
except:
    print("⚠️  Grid emission trajectory file issues")
    print()

# ============================================================================
# 3. 한국 전력망 배출계수 실제 전망 조사
# ============================================================================
print("="*80)
print("3. 한국 전력망 배출계수 실제 전망")
print("="*80)
print()

print("한국 전력 배출계수 현황 및 전망:")
print("  2025: ~0.436 tCO2/MWh (현재 석탄 30%, 가스 30%, 원전 25%, 재생 15%)")
print("  2030: ~0.35 tCO2/MWh (10차 전력수급계획, 재생 21.6% 목표)")
print("  2035: ~0.28 tCO2/MWh (재생에너지 비중 증가)")
print("  2040: ~0.20 tCO2/MWh (석탄 감소, 재생 + 원전 확대)")
print("  2050: ~0.05-0.10 tCO2/MWh (Net-Zero 목표, 완전 탈탄소는 어려움)")
print()
print("⚠️  주요 제약:")
print("  - 한국은 계통 안정성 때문에 100% 재생에너지 전환 불가")
print("  - 원자력, LNG 백업이 일정 비율 유지 필요")
print("  - 2050년에도 잔여 배출 존재 (0.05-0.10 tCO2/MWh)")
print()

# ============================================================================
# 4. 전력 기술 로직 정리
# ============================================================================
print("="*80)
print("4. 전력 관련 기술 로직 정리")
print("="*80)
print()

print("현재 모델의 전력 관련 기술:")
print()

df_tech = pd.read_csv('data/technology_parameters.csv')
elec_techs = df_tech[df_tech['technology'].str.contains('Elec|PPA|Heat', na=False, case=False)]
print(elec_techs[['technology', 'applies_to', 'elec_mwh_per_ton_ethylene', 'notes']].to_string(index=False))
print()

print("="*80)
print("문제점 분석:")
print("="*80)
print()

print("1. RE_PPA 기술의 역할이 불명확:")
print("   - 현재: 'NCC electricity only' → NCC 공정 전력을 재생에너지로 전환")
print("   - 문제: Grid EF가 0이면 감축 효과 없음")
print("   - 가격: re_price_trajectory.csv 사용 (잘못된 가격)")
print()

print("2. NCC-Electricity 기술:")
print("   - 화석연료 연소 → 전기 가열로 전환")
print("   - 전력 소비: 5.5 MWh/ton")
print("   - 질문: 어떤 전력 사용? Grid? RE?")
print()

print("3. Heat_Pump 기술:")
print("   - 저온 공정(<165°C) 전기화")
print("   - 전력 소비 있음 (COP 4.0)")
print("   - 질문: 어떤 전력 사용? Grid? RE?")
print()

# ============================================================================
# 5. 올바른 모델 구조 제안
# ============================================================================
print("="*80)
print("5. 올바른 모델 구조 제안")
print("="*80)
print()

print("명확한 전력 구분:")
print()
print("A. Grid Electricity (계통 전력)")
print("   - 가격: 한국 전력 요금 (assumption.xlsx의 Electricity 가격 사용)")
print("   - 배출계수: 시간에 따라 감소 (0.436 → 0.05-0.10 tCO2/MWh)")
print("   - 사용처: 기본 공정 전력")
print()

print("B. Renewable Electricity (재생에너지, 직접 구매)")
print("   - 가격: RE PPA 가격 (assumption.xlsx의 동일 가격? 또는 더 비쌈?)")
print("   - 배출계수: 0.0 tCO2/MWh")
print("   - 사용처: 추가 감축이 필요한 경우")
print()

print("C. 기술별 전력 사용:")
print()
print("   NCC-Electricity:")
print("     - 5.5 MWh/ton 추가 전력 소비")
print("     - 선택지 1: Grid 전력 사용 → Grid EF 적용")
print("     - 선택지 2: RE 전력 사용 → 0 배출이지만 더 비쌈")
print()
print("   Heat_Pump:")
print("     - 전력 소비 (COP 4.0)")
print("     - 선택지 1: Grid 전력 사용")
print("     - 선택지 2: RE 전력 사용")
print()
print("   RE 전환 (별도 기술):")
print("     - 기존 Grid 전력 → RE 전력으로 교체")
print("     - CAPEX: 0 (PPA 계약)")
print("     - 감축량: (Grid EF - 0) × 전력량")
print("     - 비용: (RE price - Grid price) × 전력량")
print()

# ============================================================================
# 6. 권장 사항
# ============================================================================
print("="*80)
print("6. 권장 사항 및 다음 단계")
print("="*80)
print()

print("A. 즉시 수정해야 할 사항:")
print("   1. Grid emission factor: 0이 아닌 실제 한국 전망 사용")
print("   2. Grid electricity price: Excel assumption 가격 사용")
print("   3. RE electricity price: Excel assumption 가격 사용 (동일 또는 약간 높게)")
print()

print("B. 모델 로직 단순화:")
print("   1. NCC-Electricity: Grid 전력 사용으로 가정")
print("   2. Heat_Pump: Grid 전력 사용으로 가정")
print("   3. RE 전환: 별도 감축 옵션으로 명확히 분리")
print()

print("C. 제거 또는 재정의:")
print("   - 'RE_PPA' 기술명 → 'Grid_to_RE_Switching'으로 명확히")
print("   - 또는 아예 제거하고 Grid EF 감소에만 의존")
print()

print("="*80)
print("검토 완료 - 수정 계획을 세우시겠습니까?")
print("="*80)
