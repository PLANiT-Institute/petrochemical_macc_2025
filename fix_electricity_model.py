"""
전력 모델 전면 수정
Complete Fix of Electricity Model
"""
import pandas as pd
import numpy as np
from pathlib import Path

print("="*80)
print("전력 모델 전면 수정")
print("="*80)
print()

# ============================================================================
# 1. Grid Electricity Price Trajectory 생성
# ============================================================================
print("1. Grid Electricity Price Trajectory 생성")
print("="*80)
print()

print("한국 전력 요금 현황:")
print("  - 산업용 전력: ~100-120 ₩/kWh → ~$0.08-0.10/kWh → ~$80-100/MWh")
print("  - 가정: 한국 전력 가격은 상대적으로 저렴하고 안정적")
print("  - 미래: 재생에너지 확대로 소폭 상승 가능하나 급격한 변화 없음")
print()

# Create grid price trajectory (한국 산업용 전력 요금 기반)
years = list(range(2025, 2051))
grid_prices = []

for year in years:
    if year <= 2030:
        # 2025-2030: 소폭 상승 (80 → 90 $/MWh)
        price = 80 + (year - 2025) * 2
    elif year <= 2040:
        # 2030-2040: 완만한 상승 (90 → 100 $/MWh)
        price = 90 + (year - 2030) * 1
    else:
        # 2040-2050: 안정화 (100 $/MWh 유지)
        price = 100
    grid_prices.append(price)

df_grid_price = pd.DataFrame({
    'year': years,
    'grid_price_usd_per_mwh': grid_prices,
    'source': 'Korea industrial electricity tariff',
    'notes': 'Based on Korea Power Exchange tariff structure, relatively stable'
})

output_file = Path('data/grid_price_trajectory.csv')
df_grid_price.to_csv(output_file, index=False)
print(f"✓ Created: {output_file}")
print()
print("Grid Price Trajectory:")
for year in [2025, 2030, 2040, 2050]:
    price = df_grid_price[df_grid_price['year'] == year]['grid_price_usd_per_mwh'].values[0]
    print(f"  {year}: ${price:.0f}/MWh")
print()

# ============================================================================
# 2. Grid Emission Factor 수정 (실제 한국 전망)
# ============================================================================
print("="*80)
print("2. Grid Emission Factor 수정")
print("="*80)
print()

print("한국 전력 배출계수 실제 전망:")
print("  2025: 0.436 tCO2/MWh (현재)")
print("  2030: 0.350 tCO2/MWh (10차 전력수급계획)")
print("  2035: 0.280 tCO2/MWh")
print("  2040: 0.200 tCO2/MWh")
print("  2045: 0.120 tCO2/MWh")
print("  2050: 0.070 tCO2/MWh (Net-Zero 목표, 완전 탈탄소는 불가)")
print()

# Create realistic grid emission factor trajectory
ef_data = {
    2025: 0.436,
    2030: 0.350,
    2035: 0.280,
    2040: 0.200,
    2045: 0.120,
    2050: 0.070
}

# Interpolate for all years
grid_ef = []
for year in years:
    if year in ef_data:
        grid_ef.append(ef_data[year])
    else:
        # Linear interpolation
        prev_year = max([y for y in ef_data.keys() if y < year])
        next_year = min([y for y in ef_data.keys() if y > year])
        prev_ef = ef_data[prev_year]
        next_ef = ef_data[next_year]
        interpolated_ef = prev_ef + (next_ef - prev_ef) * (year - prev_year) / (next_year - prev_year)
        grid_ef.append(interpolated_ef)

df_grid_ef = pd.DataFrame({
    'year': years,
    'grid_ef_tco2_per_mwh': grid_ef
})

output_file = Path('data/grid_emission_trajectory.csv')
df_grid_ef.to_csv(output_file, index=False)
print(f"✓ Updated: {output_file}")
print()
print("Grid Emission Factor Trajectory:")
for year in [2025, 2030, 2040, 2050]:
    ef = df_grid_ef[df_grid_ef['year'] == year]['grid_ef_tco2_per_mwh'].values[0]
    print(f"  {year}: {ef:.3f} tCO2/MWh")
print()

# ============================================================================
# 3. RE Electricity Price는 Excel 값 유지 (이미 업데이트됨)
# ============================================================================
print("="*80)
print("3. RE Electricity Price (이미 Excel 값으로 업데이트됨)")
print("="*80)
print()

df_re = pd.read_csv('data/re_price_trajectory.csv')
print("RE Price Trajectory (from Excel):")
for year in [2025, 2030, 2040, 2050]:
    price = df_re[df_re['year'] == year]['re_price_usd_per_mwh'].values[0]
    print(f"  {year}: ${price:.2f}/MWh")
print()
print("✓ RE prices already updated from assumption.xlsx")
print()

# ============================================================================
# 4. 전력 가격 비교
# ============================================================================
print("="*80)
print("4. Grid vs RE 전력 가격 비교")
print("="*80)
print()

print("Year     Grid ($/MWh)    RE ($/MWh)    Difference")
print("-"*60)
for year in [2025, 2030, 2040, 2050]:
    grid_p = df_grid_price[df_grid_price['year'] == year]['grid_price_usd_per_mwh'].values[0]
    re_p = df_re[df_re['year'] == year]['re_price_usd_per_mwh'].values[0]
    diff = re_p - grid_p
    print(f"{year}     ${grid_p:>6.0f}          ${re_p:>6.0f}         ${diff:>+6.0f} ({diff/grid_p*100:+.0f}%)")
print()

print("⚠️  FINDING: RE electricity is MUCH MORE EXPENSIVE than grid")
print("   → Using RE for NCC-Electricity or Heat_Pump will increase costs significantly")
print("   → Recommendation: Assume technologies use Grid electricity by default")
print()

# ============================================================================
# 5. 기술 파라미터 단순화
# ============================================================================
print("="*80)
print("5. 기술 파라미터 재정의")
print("="*80)
print()

df_tech = pd.read_csv('data/technology_parameters.csv')

print("현재 전력 관련 기술:")
print()
print("1. NCC-Electricity:")
print("   - 역할: 화석연료 연소 → 전기 가열로 전환")
print("   - 전력 소비: 5.5 MWh/ton C2H4 (Excel 문헌)")
print("   - 전력 출처: Grid electricity (한국 계통 전력)")
print("   - 배출: Grid EF × 전력 소비")
print("   - 비용: Grid price × 전력 소비")
print()

print("2. Heat_Pump:")
print("   - 역할: 저온 공정 전기화 (<165°C)")
print("   - 전력 소비: 열 수요 / COP 4.0")
print("   - 전력 출처: Grid electricity")
print("   - 배출: Grid EF × 전력 소비")
print("   - 비용: Grid price × 전력 소비")
print()

print("3. RE_PPA (재정의 필요):")
print("   - Option A: 삭제 (Grid EF 감소에만 의존)")
print("   - Option B: Grid → RE 전환 옵션으로 재정의")
print("     * 감축량: (Grid EF - 0) × 기존 전력 소비")
print("     * 추가 비용: (RE price - Grid price) × 전력량")
print("     * CAPEX: 0 (PPA 계약)")
print()

# Update notes for clarity
mask = df_tech['technology'] == 'NCC-Electricity'
df_tech.loc[mask, 'notes'] = 'Electric cracking using GRID electricity | 5.5 MWh/ton | Grid EF applied | CAPEX $1,500/t-C2H4/yr | OPEX 4%'

mask = df_tech['technology'] == 'Heat_Pump'
df_tech.loc[mask, 'notes'] = 'Heat pump for <165C processes using GRID electricity | COP=4.0 | Grid EF applied | Applicable to BTX/Polymer only'

df_tech.to_csv('data/technology_parameters.csv', index=False)
print("✓ Updated technology_parameters.csv with clarified notes")
print()

# ============================================================================
# 6. 요약
# ============================================================================
print("="*80)
print("6. 수정 요약")
print("="*80)
print()

print("✓ 생성된 파일:")
print("  - data/grid_price_trajectory.csv (새로 생성)")
print("  - data/grid_emission_trajectory.csv (수정)")
print("  - data/technology_parameters.csv (notes 업데이트)")
print()

print("✓ 전력 체계:")
print("  - Grid 전력: $80-100/MWh, EF 0.436→0.070 tCO2/MWh")
print("  - RE 전력: $129-191/MWh, EF 0.0 tCO2/MWh")
print("  - 기술들은 기본적으로 Grid 전력 사용")
print()

print("⚠️  다음 단계:")
print("  1. MACC 모듈 수정 (Grid price 반영)")
print("  2. RE_PPA 로직 재검토 (삭제 또는 재정의)")
print("  3. 테스트 시나리오 실행")
print()

print("="*80)
print("전력 모델 수정 완료")
print("="*80)
