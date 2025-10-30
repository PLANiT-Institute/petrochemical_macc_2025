"""
NCC-H2 수소 소비량 에너지 기반 재계산

목적: 베이스라인 연소 에너지를 완전히 대체하는 데 필요한 수소량을 계산
"""

import pandas as pd
from pathlib import Path

print("="*80)
print("NCC-H2 수소 소비량 에너지 기반 재계산")
print("="*80)
print()

# ============================================================================
# Part 1: 베이스라인 연소 에너지 계산
# ============================================================================

print("PART 1: 베이스라인 연소 에너지 (에틸렌 1톤 생산)")
print("-" * 80)
print()

# Load energy intensities
df_ei = pd.read_csv('data/energy_intensities.csv')
ethylene_ei = df_ei[df_ei['product'] == 'Ethylene'].iloc[0]

# Energy consumption
naphtha_gj = ethylene_ei['Naphtha_GJ_per_tonne']
lng_gj = ethylene_ei['LNG_GJ_per_tonne']
fuel_gas_gj = ethylene_ei['Fuel_Gas_GJ_per_tonne']
byproduct_gas_gj = ethylene_ei['Byproduct_Gas_GJ_per_tonne']
electricity_kwh = ethylene_ei['Electricity_kWh_per_tonne']

# Total combustion energy (excluding electricity)
total_combustion_gj = naphtha_gj + lng_gj + fuel_gas_gj + byproduct_gas_gj

print("연소 에너지 소비:")
print(f"  Naphtha (부생가스 연소):  {naphtha_gj:>8.3f} GJ/ton  ({naphtha_gj/total_combustion_gj*100:>5.1f}%)")
print(f"  LNG:                    {lng_gj:>8.3f} GJ/ton  ({lng_gj/total_combustion_gj*100:>5.1f}%)")
print(f"  Fuel Gas:               {fuel_gas_gj:>8.3f} GJ/ton  ({fuel_gas_gj/total_combustion_gj*100:>5.1f}%)")
print(f"  Byproduct Gas:          {byproduct_gas_gj:>8.3f} GJ/ton  ({byproduct_gas_gj/total_combustion_gj*100:>5.1f}%)")
print(f"  {'─'*50}")
print(f"  TOTAL 연소 에너지:      {total_combustion_gj:>8.3f} GJ/ton  (100.0%)")
print()
print(f"프로세스 전력 (별도):     {electricity_kwh:>8.3f} kWh/ton")
print()

# ============================================================================
# Part 2: 수소 소비량 계산 (여러 시나리오)
# ============================================================================

print("PART 2: 수소 필요량 계산")
print("-" * 80)
print()

# H2 properties
H2_HHV_GJ_PER_TON = 142.0  # Higher Heating Value
H2_LHV_GJ_PER_TON = 120.0  # Lower Heating Value (일반적으로 사용)

print(f"수소 열량:")
print(f"  HHV (Higher Heating Value): {H2_HHV_GJ_PER_TON} GJ/ton")
print(f"  LHV (Lower Heating Value):  {H2_LHV_GJ_PER_TON} GJ/ton")
print(f"  → 산업 표준: LHV 사용")
print()

# Combustion efficiency scenarios
scenarios = {
    'Conservative (낮은 효율)': {
        'baseline_eff': 0.70,  # 기존 화석연료 연소 효율
        'h2_eff': 0.80,        # 수소 연소 효율 (보수적)
        'heat_recovery': 0.0,  # 열 회수 없음
    },
    'Moderate (중간)': {
        'baseline_eff': 0.70,
        'h2_eff': 0.85,        # 수소 연소 효율 (일반적)
        'heat_recovery': 5.0,  # 5 GJ/ton 열 회수
    },
    'Optimistic (높은 효율)': {
        'baseline_eff': 0.70,
        'h2_eff': 0.90,        # 수소 연소 효율 (최적)
        'heat_recovery': 10.0, # 10 GJ/ton 열 회수
    },
    'Current Model': {
        'baseline_eff': 0.70,
        'h2_eff': 0.85,
        'heat_recovery': 9.6,  # Back-calculated from 0.18 ton/ton
    }
}

print("시나리오별 수소 필요량:")
print()

results = []

for scenario_name, params in scenarios.items():
    baseline_eff = params['baseline_eff']
    h2_eff = params['h2_eff']
    heat_recovery = params['heat_recovery']

    # Step 1: 베이스라인 유효 열량
    baseline_effective_heat = total_combustion_gj * baseline_eff

    # Step 2: 실제 필요 열량 (열 회수 고려)
    required_heat = baseline_effective_heat - heat_recovery

    # Step 3: 필요 수소 에너지 (효율 고려)
    required_h2_energy = required_heat / h2_eff

    # Step 4: 필요 수소량 (LHV 기준)
    required_h2_ton = required_h2_energy / H2_LHV_GJ_PER_TON

    results.append({
        'scenario': scenario_name,
        'baseline_eff': baseline_eff,
        'h2_eff': h2_eff,
        'heat_recovery_gj': heat_recovery,
        'baseline_heat_gj': baseline_effective_heat,
        'required_heat_gj': required_heat,
        'h2_energy_gj': required_h2_energy,
        'h2_ton_per_ton': required_h2_ton
    })

    print(f"  {scenario_name}:")
    print(f"    베이스라인 유효 열:      {baseline_effective_heat:>6.2f} GJ/ton (효율 {baseline_eff*100:.0f}%)")
    print(f"    열 회수:                {heat_recovery:>6.2f} GJ/ton")
    print(f"    필요 순 열량:           {required_heat:>6.2f} GJ/ton")
    print(f"    수소 연소 효율:         {h2_eff*100:>6.1f}%")
    print(f"    필요 수소 에너지:       {required_h2_energy:>6.2f} GJ/ton")
    print(f"    >>> 필요 수소량:        {required_h2_ton:>6.3f} ton H2/ton ethylene")
    print()

df_results = pd.DataFrame(results)

# ============================================================================
# Part 3: 비용 영향 분석
# ============================================================================

print("PART 3: 비용 영향 분석")
print("-" * 80)
print()

# Load H2 prices
df_h2_price = pd.read_csv('data/h2_price_trajectory.csv')
h2_price_2030 = df_h2_price[df_h2_price['year'] == 2030]['h2_price_usd_per_kg'].iloc[0]
h2_price_2050 = df_h2_price[df_h2_price['year'] == 2050]['h2_price_usd_per_kg'].iloc[0]

print(f"수소 가격 (모델):")
print(f"  2030: ${h2_price_2030:.2f}/kg = ${h2_price_2030*1000:.0f}/ton")
print(f"  2050: ${h2_price_2050:.2f}/kg = ${h2_price_2050*1000:.0f}/ton")
print()

# Baseline emissions (from previous analysis)
baseline_emissions_tco2_per_ton = 2.257

print(f"베이스라인 배출량: {baseline_emissions_tco2_per_ton:.3f} tCO2/ton ethylene")
print()

# Cost calculation for each scenario
print("시나리오별 연료비 (2030년, H2 = $3.5/kg):")
print()

for idx, row in df_results.iterrows():
    h2_ton = row['h2_ton_per_ton']

    # Fuel cost
    h2_cost_per_ton_ethylene = h2_ton * h2_price_2030 * 1000  # $/ton ethylene

    # Per tCO2 abated
    fuel_cost_per_tco2 = h2_cost_per_ton_ethylene / baseline_emissions_tco2_per_ton

    print(f"  {row['scenario']}:")
    print(f"    H2 소비: {h2_ton:.3f} ton/ton")
    print(f"    연료비: ${h2_cost_per_ton_ethylene:,.0f}/ton ethylene")
    print(f"    연료비: ${fuel_cost_per_tco2:,.1f}/tCO2 abated")
    print()

# ============================================================================
# Part 4: 총 MACC 비용 비교
# ============================================================================

print("PART 4: 총 MACC 비용 비교 (2030년)")
print("-" * 80)
print()

# CAPEX/OPEX from technology parameters
df_tech = pd.read_csv('data/technology_parameters.csv')
ncc_h2_tech = df_tech[df_tech['technology'] == 'NCC-H2'].iloc[0]

capex_2030 = ncc_h2_tech['capex_2030_musd_per_mtco2']  # M$/MtCO2
opex_pct = ncc_h2_tech['opex_pct_capex']
lifetime = ncc_h2_tech['lifetime_years']

capex_ann = capex_2030 / lifetime  # Simple annualization
opex_ann = capex_2030 * (opex_pct / 100)

print(f"NCC-H2 기술 파라미터:")
print(f"  CAPEX (2030): ${capex_2030:.0f} M$/MtCO2")
print(f"  Lifetime: {lifetime} years")
print(f"  OPEX: {opex_pct}% of CAPEX")
print()
print(f"연간 비용 ($/tCO2):")
print(f"  CAPEX_ann: ${capex_ann:.2f}/tCO2")
print(f"  OPEX_ann:  ${opex_ann:.2f}/tCO2")
print()

print("총 MACC 비용 (CAPEX_ann + OPEX_ann + Fuel):")
print()

for idx, row in df_results.iterrows():
    h2_ton = row['h2_ton_per_ton']
    h2_cost_per_ton_ethylene = h2_ton * h2_price_2030 * 1000
    fuel_cost_per_tco2 = h2_cost_per_ton_ethylene / baseline_emissions_tco2_per_ton

    total_cost = capex_ann + opex_ann + fuel_cost_per_tco2

    print(f"  {row['scenario']}:")
    print(f"    H2: {h2_ton:.3f} ton/ton → Fuel: ${fuel_cost_per_tco2:,.1f}/tCO2")
    print(f"    Total MACC: ${total_cost:,.1f}/tCO2")
    print()

# ============================================================================
# Part 5: NCC-Electricity 비교
# ============================================================================

print("PART 5: NCC-Electricity 비교 (2030년)")
print("-" * 80)
print()

ncc_elec_tech = df_tech[df_tech['technology'] == 'NCC-Electricity'].iloc[0]

capex_elec_2030 = ncc_elec_tech['capex_2030_musd_per_mtco2']
opex_elec_pct = ncc_elec_tech['opex_pct_capex']
lifetime_elec = ncc_elec_tech['lifetime_years']
elec_mwh_per_ton = ncc_elec_tech['elec_mwh_per_ton_ethylene']

capex_elec_ann = capex_elec_2030 / lifetime_elec
opex_elec_ann = capex_elec_2030 * (opex_elec_pct / 100)

# RE price (2030)
df_re_price = pd.read_csv('data/re_price_trajectory.csv')
re_price_2030 = df_re_price[df_re_price['year'] == 2030]['re_price_usd_per_mwh'].iloc[0]

# Grid EF (2030)
df_grid = pd.read_csv('data/grid_emission_trajectory.csv')
grid_ef_2030 = df_grid[df_grid['year'] == 2030]['grid_ef_tco2_per_mwh'].iloc[0]

# Fuel cost
elec_cost_per_ton_ethylene = elec_mwh_per_ton * re_price_2030
fuel_cost_elec_per_tco2 = elec_cost_per_ton_ethylene / baseline_emissions_tco2_per_ton

# Total cost
total_cost_elec = capex_elec_ann + opex_elec_ann + fuel_cost_elec_per_tco2

print(f"NCC-Electricity 파라미터:")
print(f"  CAPEX (2030): ${capex_elec_2030:.0f} M$/MtCO2")
print(f"  전력 소비: {elec_mwh_per_ton:.1f} MWh/ton ethylene")
print(f"  RE 가격 (2030): ${re_price_2030:.1f}/MWh")
print()
print(f"비용:")
print(f"  CAPEX_ann: ${capex_elec_ann:.2f}/tCO2")
print(f"  OPEX_ann:  ${opex_elec_ann:.2f}/tCO2")
print(f"  Fuel cost: ${fuel_cost_elec_per_tco2:.2f}/tCO2")
print(f"  >>> Total MACC: ${total_cost_elec:.2f}/tCO2")
print()

# ============================================================================
# Part 6: 권장사항
# ============================================================================

print("="*80)
print("권장사항")
print("="*80)
print()

# Find realistic scenario (moderate)
moderate_row = df_results[df_results['scenario'] == 'Moderate (중간)'].iloc[0]
h2_moderate = moderate_row['h2_ton_per_ton']
h2_cost_moderate = h2_moderate * h2_price_2030 * 1000 / baseline_emissions_tco2_per_ton
total_cost_moderate = capex_ann + opex_ann + h2_cost_moderate

# Find conservative scenario
conservative_row = df_results[df_results['scenario'] == 'Conservative (낮은 효율)'].iloc[0]
h2_conservative = conservative_row['h2_ton_per_ton']
h2_cost_conservative = h2_conservative * h2_price_2030 * 1000 / baseline_emissions_tco2_per_ton
total_cost_conservative = capex_ann + opex_ann + h2_cost_conservative

print("1. 현재 모델 (0.18 ton/ton) 문제점:")
print(f"   - 에너지 수지 불균형: 21.6 GJ < 40 GJ 베이스라인")
print(f"   - 비현실적인 열 회수 가정: 9.6 GJ/ton (24%)")
print(f"   - 결과: NCC-H2가 과소평가됨 (너무 저렴)")
print()

print("2. 에너지 기반 재계산 결과:")
print(f"   Conservative (효율 80%, 열회수 0 GJ):")
print(f"     - H2 필요량: {h2_conservative:.3f} ton/ton")
print(f"     - MACC 비용: ${total_cost_conservative:.1f}/tCO2")
print()
print(f"   Moderate (효율 85%, 열회수 5 GJ):")
print(f"     - H2 필요량: {h2_moderate:.3f} ton/ton")
print(f"     - MACC 비용: ${total_cost_moderate:.1f}/tCO2")
print()
print(f"   NCC-Electricity (비교):")
print(f"     - MACC 비용: ${total_cost_elec:.1f}/tCO2")
print()

print("3. 권장 파라미터:")
print()
if total_cost_moderate < total_cost_elec:
    print(f"   ✅ Moderate 시나리오 (H2 = {h2_moderate:.3f} ton/ton)")
    print(f"      - 합리적인 효율 가정 (85%)")
    print(f"      - 보수적인 열 회수 (5 GJ/ton)")
    print(f"      - NCC-Electricity보다 여전히 경쟁력 있음")
    recommended_h2 = h2_moderate
else:
    print(f"   ⚠️ Conservative 시나리오 사용 권장 (H2 = {h2_conservative:.3f} ton/ton)")
    print(f"      - 가장 보수적인 가정")
    print(f"      - NCC-Electricity보다 비용 높음 → 기술 선택 변경 가능")
    recommended_h2 = h2_conservative

print()
print(f"4. 모델 업데이트:")
print(f"   기존: h2_ton_per_ton_ethylene = 0.18")
print(f"   권장: h2_ton_per_ton_ethylene = {recommended_h2:.3f}")
print()

print("="*80)
print("END OF ANALYSIS")
print("="*80)

# Save results
output_path = Path('outputs/ncc_h2_energy_analysis.csv')
output_path.parent.mkdir(parents=True, exist_ok=True)
df_results.to_csv(output_path, index=False)
print(f"\n결과 저장: {output_path}")
