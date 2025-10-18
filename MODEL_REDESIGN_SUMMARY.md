# 모델 재설계 완료 요약

**날짜**: 2025-10-16
**목적**: LCOE 통합 방식 → 명시적 에너지 기반 MACC 모델 전환

---

## 🎯 왜 재설계했나?

### 기존 LCOE 방식의 문제
1. **투명성 부족**:
   - CAPEX, 수소/전력 소비량이 LCOE에 묻혀서 보이지 않음
   - "수소 가격이 $6→$3이면?" 같은 질문에 답할 수 없음

2. **외부 데이터 의존**:
   - 논문 한 개(Green Chemistry 2025)의 LCOE 값에 전적으로 의존
   - 한국 상황과 다를 수 있고, 업데이트 불가능

3. **민감도 분석 제한**:
   - 가격 변화, 효율 변화 시뮬레이션 불가능

### 새로운 에너지 기반 방식

```
Total MACC = CAPEX(annual) + OPEX(annual) + Fuel_Cost_Differential

여기서:
- CAPEX: 기술별 자본비용 (명시적)
- OPEX: 운영비용 (명시적)
- Fuel Diff = (신규 에너지 비용 - 기존 연료 비용) / tCO2
```

**핵심**: 모든 에너지 전환을 **명시적으로 추적**

---

## 📋 완료된 작업

### 1. ✅ 아카이브 완료
```
archive_unused/legacy_lcoe_approach/
├── ncc_lcoe_trajectory.csv         # LCOE 데이터 (더 이상 사용 안 함)
├── macc_lcoe_version.py            # 기존 MACC 코드 백업
└── [모든 기존 문서 30개]           # 기존 분석 문서들
```

### 2. ✅ 기술 파라미터 업데이트
**파일**: `data/technology_parameters.csv`

#### 새로 추가된 컬럼:
| 컬럼 | 설명 | 예시 |
|------|------|------|
| `cop` | Heat Pump 성능계수 | 4.0 |
| `h2_ton_per_ton_ethylene` | 수소 소비량 | 0.8 ton H2/ton C2H4 |
| `elec_mwh_per_ton_ethylene` | 전력 소비량 | 13 MWh/ton C2H4 |
| `naphtha_combustion_gj_per_ton_ethylene` | 대체할 납사 연소량 | 105 GJ/ton C2H4 |
| `notes` | 기술 설명 | (설명) |

#### 기술별 파라미터 요약:

**Heat Pump**:
- COP: 4.0
- CAPEX: $150M/MtCO2 (2025) → $75M (2050)
- 적용: NCC 제외, <165°C 열 수요
- **에너지**: 화석연료 → 전력 (1/4 소비, COP 덕분)

**NCC-H2**:
- 수소 소비: 0.8 ton H2/ton 에틸렌
- 대체 연료: 105 GJ 납사 연소/ton (열 공급용만)
- CAPEX: $300M/MtCO2 (2025) → $150M (2050)
- 적용: 납사 크래커만

**NCC-Electricity**:
- 전력 소비: 13 MWh/ton 에틸렌
- 대체 연료: 105 GJ 납사 연소/ton
- CAPEX: $350M/MtCO2 (2025) → $180M (2050)
- 적용: 납사 크래커만
- 출처: Green Chemistry 2025 (DOI:10.1039/D4GC04538F)

**RE PPA**:
- CAPEX: $0 (인프라 투자 없음, 계약만)
- 적용: NCC 시설 전력만
- **에너지 변화 없음** (계약 전환만)

---

## 🔄 에너지 전환 로직

### Technology 1: Heat Pump

```python
# Before (기존)
fossil_fuels_gj = naphtha + lng + fuel_gas + lpg + fuel_oil + diesel
emissions_before = fossil_fuels_gj * 0.0149  # tCO2

# After (히트펌프)
electricity_mwh = fossil_fuels_gj / COP / 3.6  # MWh (COP=4.0)
emissions_after = electricity_mwh * grid_ef  # tCO2

# Abatement
abatement = emissions_before - emissions_after

# Costs
fuel_cost_before = fossil_fuels_gj * naphtha_price  # $/ton product
fuel_cost_after = electricity_mwh * elec_price      # $/ton product
fuel_diff_per_ton = fuel_cost_after - fuel_cost_before
fuel_diff_per_tco2 = fuel_diff_per_ton / abatement_per_ton

macc = capex_annual + opex_annual + fuel_diff_per_tco2
```

---

### Technology 2: NCC-H2

```python
# Before (기존 납사 크래커)
naphtha_combustion_gj = 105  # GJ/ton ethylene (열 생성용)
naphtha_feedstock_gj = 50    # GJ/ton (원료용 - 그대로 유지!)
emissions_before = naphtha_combustion_gj * 0.0149  # tCO2/ton

# After (수소 크래커)
h2_consumption_ton = 0.8     # ton H2/ton ethylene
emissions_after = 0.05       # tCO2/ton (green H2 lifecycle)

# Abatement
abatement_per_ton = emissions_before - emissions_after

# Costs
h2_cost = h2_consumption_ton * 1000 * h2_price_per_kg  # $/ton ethylene
naphtha_cost = naphtha_combustion_gj * naphtha_price   # $/ton ethylene
fuel_diff_per_ton = h2_cost - naphtha_cost
fuel_diff_per_tco2 = fuel_diff_per_ton / abatement_per_ton

macc = capex_annual + opex_annual + fuel_diff_per_tco2
```

**핵심**: 납사 feedstock (원료)는 그대로! 오직 **연소용**만 수소로 대체.

---

### Technology 3: NCC-Electricity

```python
# Before
naphtha_combustion_gj = 105  # GJ/ton ethylene
emissions_before = 105 * 0.0149  # tCO2/ton

# After
electricity_mwh = 13             # MWh/ton ethylene (문헌)
emissions_after = 13 * grid_ef   # tCO2/ton

# Abatement
abatement_per_ton = emissions_before - emissions_after

# Costs
elec_cost = 13 * elec_price      # $/ton ethylene
naphtha_cost = 105 * naphtha_price
fuel_diff_per_ton = elec_cost - naphtha_cost
fuel_diff_per_tco2 = fuel_diff_per_ton / abatement_per_ton

macc = capex_annual + opex_annual + fuel_diff_per_tco2
```

---

### Technology 4: RE PPA

```python
# 에너지 소비 변화 없음 (계약 전환만)

# Abatement (per MWh)
grid_ef = 0.4  # tCO2/MWh (2025, trajectory에서)
re_ef = 0.05   # tCO2/MWh (lifecycle)
abatement_per_mwh = grid_ef - re_ef

# Costs
re_price = 80    # $/MWh (trajectory)
grid_price = 100 # $/MWh (trajectory)
price_diff = re_price - grid_price  # $/MWh

# MACC
macc = price_diff / abatement_per_mwh  # $/tCO2
# Note: CAPEX = 0, OPEX = 0
```

---

## 🔍 모델 검증 체크리스트

### Heat Pump
- [x] CAPEX 명시적 증가: $150M/MtCO2 → $75M
- [x] 전력 소비 증가: (화석연료 GJ / COP / 3.6) MWh
- [x] 화석연료 완전 제거
- [ ] MACC 계산 구현 (다음 단계)

### NCC-H2
- [x] CAPEX 명시적: $300M/MtCO2 → $150M
- [x] 수소 소비 명시: 0.8 ton H2/ton ethylene
- [x] 납사 연소 제거 (105 GJ/ton)
- [x] 납사 feedstock 유지 (원료용)
- [ ] MACC 계산 구현 (다음 단계)

### NCC-Electricity
- [x] CAPEX 명시적: $350M/MtCO2 → $180M
- [x] 전력 소비 명시: 13 MWh/ton ethylene
- [x] 납사 연소 제거 (105 GJ/ton)
- [ ] MACC 계산 구현 (다음 단계)

### RE PPA
- [x] CAPEX = 0 (인프라 없음)
- [x] 에너지 소비 변화 없음
- [x] 가격 차이만 반영
- [ ] MACC 계산 구현 (다음 단계)

---

## 📝 다음 단계 (구현 필요)

### 1. ⏳ modules/macc.py 재작성
**파일**: `modules/macc.py`

다음 함수들을 에너지 기반 로직으로 재구현:
- `_calculate_heat_pump_macc()`: 화석연료 → 전력 전환
- `_calculate_ncc_h2_macc()`: 납사 연소 → 수소 전환
- `_calculate_ncc_electricity_macc()`: 납사 연소 → 전력 전환
- `_calculate_re_ppa_macc()`: 이미 맞음 (유지)

### 2. ⏳ utils.py 업데이트
`TechnologyCostCalculator` 클래스:
- 새 컬럼 읽기 추가 (`h2_ton_per_ton_ethylene`, `elec_mwh_per_ton_ethylene` 등)

### 3. ⏳ 테스트 및 검증
- Module 2 단독 실행: `python run_module_02.py`
- MACC curve 생성 확인
- 비용 component 분리 확인 (CAPEX vs OPEX vs Fuel)

### 4. ⏳ Module 3 & 4 호환성 검증
- Module 3 (optimization): `df_macc` 컬럼 구조 확인
- Module 4 (financial): deployment 결과 사용 → 영향 없음

---

## 🎓 주요 개선점 요약

| 항목 | 기존 LCOE | 새로운 에너지 기반 |
|------|-----------|-------------------|
| **CAPEX** | 숨겨짐 | 명시적 ($M/MtCO2) |
| **수소 소비** | 숨겨짐 | 명시적 (ton H2/ton C2H4) |
| **전력 소비** | 숨겨짐 | 명시적 (MWh/ton C2H4) |
| **민감도 분석** | 불가능 | 가능 (가격, 효율 변화) |
| **가격 시나리오** | 제한적 | 자유로움 |
| **투명성** | ❌ | ✅ |
| **검증 가능성** | ❌ | ✅ |

---

## 📂 프로젝트 구조 (업데이트)

```
petrochemical_macc_2025/
├── data/
│   ├── technology_parameters.csv        # ✅ 업데이트됨 (에너지 파라미터 추가)
│   ├── energy_intensities.csv          # 기존 유지
│   ├── h2_price_trajectory.csv         # 기존 유지
│   ├── fuel_price_trajectory.csv       # 기존 유지
│   └── [기타 데이터 파일들]
│
├── modules/
│   ├── macc.py                         # ⏳ 재작성 필요
│   ├── utils.py                        # ⏳ 업데이트 필요
│   ├── optimization.py                 # ✅ 유지 (변경 없음)
│   ├── financial.py                    # ✅ 유지 (변경 없음)
│   └── baseline.py                     # ✅ 유지 (변경 없음)
│
├── archive_unused/
│   └── legacy_lcoe_approach/           # ✅ LCOE 방식 전체 보관
│       ├── ncc_lcoe_trajectory.csv
│       ├── macc_lcoe_version.py
│       └── [30개 문서]
│
├── REDESIGN_ENERGY_BASED_MODEL.md      # ✅ 상세 설계 문서
├── MODEL_REDESIGN_SUMMARY.md           # ✅ 이 문서
└── run_module_02.py                    # ⏳ 테스트 예정
```

---

## ✅ 완료 확인

- [x] LCOE 파일들 아카이브 완료
- [x] 기존 문서 30개 아카이브 완료
- [x] `technology_parameters.csv` 에너지 파라미터 추가
- [x] 에너지 전환 로직 설계 완료
- [x] 검증 체크리스트 작성
- [x] 상세 설계 문서 작성 ([REDESIGN_ENERGY_BASED_MODEL.md](REDESIGN_ENERGY_BASED_MODEL.md))
- [x] 요약 문서 작성 (이 문서)

---

## 💡 다음 작업 (사용자 확인 필요)

1. **설계 검토**: 위 에너지 전환 로직이 맞는지 확인
2. **파라미터 검증**:
   - H2 소비 0.8 ton/ton 적절한가?
   - 전기 소비 13 MWh/ton 적절한가?
   - 납사 연소 105 GJ/ton 맞는가?
3. **승인 후**: `modules/macc.py` 재작성 시작

---

**질문이나 수정사항 있으시면 말씀해주세요!**
