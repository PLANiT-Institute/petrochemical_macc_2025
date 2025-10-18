# 에너지 기반 MACC 모델 재설계

## 목적
LCOE 통합 방식을 버리고, **명시적인 에너지 소비 및 비용 분리 모델**로 재설계

## 핵심 원칙

### 1. 모든 기술은 다음으로 표현:
```
Total MACC Cost = CAPEX_annual + OPEX_annual + Fuel_Cost_Differential
```

### 2. 에너지 전환 명시화:
- **Before**: 화석연료 소비 (GJ)
- **After**: 신규 에너지 소비 (H2 kg, Electricity MWh)
- **Fuel Cost Diff** = (신규 에너지 비용 - 기존 연료 비용) / tCO2 abated

---

## 기술별 에너지 전환 설계

### Technology 1: Heat Pump
**적용 대상**: NCC 제외, <165°C 열 수요 공정

**에너지 전환**:
```
Before: Fossil fuel combustion = Naphtha + LNG + Fuel_Gas + ... [GJ/tonne product]
After:  Electricity = Fossil_fuel_GJ / COP [MWh]
```

**파라미터**:
- `cop`: 4.0 (성능계수)
- `applicable_temp`: <165°C
- `capex_musd_per_mtco2`: 150 (2025) → 75 (2050)
- `opex_pct_capex`: 3.0%
- `lifetime_years`: 20

**MACC 계산**:
```python
# 1. Abatement potential
fossil_fuels_gj = naphtha + lng + fuel_gas + lpg + fuel_oil + diesel
abatement_tco2 = fossil_fuels_gj * EF_fossil - (fossil_fuels_gj / COP / 3.6) * EF_grid

# 2. Costs
capex_annual = capex_musd_per_mtco2 * CRF
opex_annual = capex_annual * 0.03

# 3. Fuel cost differential (per tonne product)
elec_cost = (fossil_fuels_gj / COP / 3.6) * electricity_price_per_mwh
fuel_cost_baseline = fossil_fuels_gj * naphtha_price_per_gj
fuel_diff_per_tonne = elec_cost - fuel_cost_baseline

# 4. Per tCO2
fuel_diff_per_tco2 = fuel_diff_per_tonne / abatement_tco2_per_tonne

macc = capex_annual + opex_annual + fuel_diff_per_tco2
```

---

### Technology 2: NCC-H2 (Hydrogen Cracker)
**적용 대상**: Naphtha Cracker only

**에너지 전환**:
```
Before: Naphtha combustion = 105 GJ/tonne ethylene (열 공급용)
After:  H2 combustion = 0.8 tonne H2/tonne ethylene (문헌 기준)
```

**파라미터**:
- `h2_consumption_ton_per_ton_ethylene`: 0.8
- `capex_musd_per_mtco2`: 300 (2025) → 150 (2050)
- `opex_pct_capex`: 2.5%
- `lifetime_years`: 25

**MACC 계산**:
```python
# 1. Abatement (per tonne ethylene)
# Baseline emissions
naphtha_combustion_gj = 105  # GJ/ton ethylene (for heat)
naphtha_feedstock_gj = 50    # GJ/ton ethylene (feedstock, NOT combusted)
emission_baseline = naphtha_combustion_gj * 0.0149  # tCO2/ton ethylene

# H2 emissions (combustion only, assume green H2)
h2_consumption_ton = 0.8  # ton H2/ton ethylene
emission_h2 = 0.05  # Minimal (green H2 lifecycle)

abatement_tco2_per_ton = emission_baseline - emission_h2

# 2. Costs
capex_annual = capex_musd_per_mtco2 * CRF
opex_annual = capex_annual * 0.025

# 3. Fuel cost differential (per tonne ethylene)
h2_cost = h2_consumption_ton * 1000 * h2_price_per_kg  # $/ton ethylene
naphtha_cost = naphtha_combustion_gj * naphtha_price_per_gj  # $/ton ethylene
fuel_diff_per_ton = h2_cost - naphtha_cost

# 4. Per tCO2
fuel_diff_per_tco2 = fuel_diff_per_ton / abatement_tco2_per_ton

macc = capex_annual + opex_annual + fuel_diff_per_tco2
```

**Note**: Naphtha feedstock (원료용)은 그대로 유지. 오직 **열 생성용 연소분**만 H2로 대체.

---

### Technology 3: NCC-Electricity (Electric Cracker)
**적용 대상**: Naphtha Cracker only

**에너지 전환**:
```
Before: Naphtha combustion = 105 GJ/tonne ethylene
After:  Electricity = 13 MWh/tonne ethylene (문헌: Green Chemistry 2025)
```

**파라미터**:
- `electricity_consumption_mwh_per_ton_ethylene`: 13.0
- `capex_musd_per_mtco2`: 350 (2025) → 180 (2050)
- `opex_pct_capex`: 2.0%
- `lifetime_years`: 25

**MACC 계산**:
```python
# 1. Abatement (per tonne ethylene)
emission_baseline = 105 * 0.0149  # tCO2/ton ethylene (naphtha combustion)
emission_elec = 13 * grid_ef_tco2_per_mwh  # tCO2/ton ethylene
abatement_tco2_per_ton = emission_baseline - emission_elec

# 2. Costs
capex_annual = capex_musd_per_mtco2 * CRF
opex_annual = capex_annual * 0.02

# 3. Fuel cost differential
elec_cost = 13 * electricity_price_per_mwh  # $/ton ethylene
naphtha_cost = 105 * naphtha_price_per_gj  # $/ton ethylene
fuel_diff_per_ton = elec_cost - naphtha_cost

# 4. Per tCO2
fuel_diff_per_tco2 = fuel_diff_per_ton / abatement_tco2_per_ton

macc = capex_annual + opex_annual + fuel_diff_per_tco2
```

---

### Technology 4: RE PPA (Renewable Energy PPA)
**적용 대상**: NCC facilities의 기존 전력 소비만

**에너지 전환**:
```
Before: Grid electricity = 현재 소비량 그대로
After:  RE electricity = 동일 소비량 (계약만 변경)
```

**파라미터**:
- `capex_musd_per_mtco2`: 0 (인프라 투자 없음)
- `opex_pct_capex`: 0
- No lifetime (계약 방식)

**MACC 계산**:
```python
# 1. Abatement (per MWh switched)
grid_ef = 0.4  # tCO2/MWh (trajectory에서)
re_ef = 0.05   # tCO2/MWh (lifecycle)
abatement_per_mwh = grid_ef - re_ef

# 2. Costs
capex_annual = 0
opex_annual = 0

# 3. Fuel cost differential (per MWh)
re_price = 80  # $/MWh (trajectory에서)
grid_price = 100  # $/MWh (trajectory에서)
price_diff_per_mwh = re_price - grid_price

# 4. Per tCO2
macc = price_diff_per_mwh / abatement_per_mwh
```

---

## 필요한 데이터 파일 업데이트

### 1. technology_parameters.csv
기존 컬럼 유지 + 추가:
```csv
technology,applies_to,cop,h2_ton_per_ton_ethylene,elec_mwh_per_ton_ethylene,trl,available_year,capex_2025_musd_per_mtco2,...
Heat_Pump,All processes <165°C,4.0,,,9,2025,150,...
NCC-H2,Naphtha crackers only,,0.8,,7,2030,300,...
NCC-Electricity,Naphtha crackers only,,,13.0,6,2030,350,...
RE_PPA,NCC electricity only,,,,,2025,0,...
```

### 2. 삭제 파일
- `data/ncc_lcoe_trajectory.csv` → archive

---

## 구현 계획

1. ✅ Archive LCOE files
2. ⏳ Update `technology_parameters.csv` with energy parameters
3. ⏳ Rewrite `modules/macc.py`:
   - `_calculate_heat_pump_macc()`: Use energy conversion
   - `_calculate_ncc_h2_macc()`: Use H2 consumption
   - `_calculate_ncc_electricity_macc()`: Use electricity consumption
   - `_calculate_re_ppa_macc()`: Keep simple (already correct)
4. ⏳ Test calculations
5. ⏳ Verify Module 3 & 4 still work

---

## 검증 체크리스트

- [ ] Heat Pump: CAPEX 증가, 전력 소비 증가, 화석연료 감소
- [ ] NCC-H2: CAPEX 증가, 수소 소비 증가, 납사 연소 감소
- [ ] NCC-Electricity: CAPEX 증가, 전력 소비 증가, 납사 연소 감소
- [ ] RE PPA: CAPEX 없음, 에너지 소비 변화 없음, 가격 차이만
- [ ] Module 4 (Financial) 동작 확인
