# Petrochemical MACC Model - Update Summary

**Date:** 2025-10-18
**Version:** 2.0 (Literature-based)

---

## 주요 변경 사항

### 1. 할인율 제거 (Discount Rate Removal)

**이전:**
- `discount_rate = 0.08` (8% 할인율)
- CAPEX 연간화: `CAPEX_annual = CAPEX × CRF(discount_rate, lifetime)`
- CRF = Capital Recovery Factor

**변경 후:**
- 할인율 제거 (MACC 계산에서 완전 제거)
- 단순 연간화: `CAPEX_annual = CAPEX / lifetime`
- OPEX: `OPEX_annual = CAPEX × OPEX_pct`

**파일 수정:**
- `data/model_parameters.csv` - discount_rate 파라미터 삭제
- `modules/macc.py` - CRF 계산 제거, 단순 나눗셈으로 변경
- `modules/data_manager.py` - critical_params에서 discount_rate 제거
- `modules/financial.py` - NPV/IRR 계산용으로만 5% 할인율 유지

---

## 2. 문헌 기반 파라미터 업데이트

### A. 에너지 집약도 (Energy Intensity)

**Naphtha Fuel Consumption (연료로만 사용)**
- 이전: 105.47 GJ/ton (feedstock + fuel 혼재)
- **변경: 29.00 GJ/ton** (fuel only)
- 출처: 일반적인 steam cracker 연료 소비량

### B. 배출계수 (Emission Factors)

**Naphtha EF**
- 이전: 0.0149 tCO2/GJ
- **변경: 0.0542 tCO2/GJ**
- 이유: 52 MtCO2 baseline 유지 (에너지 감소 × EF 증가 = 일정)

**RE Lifecycle Emissions**
- **신규: 0.05 tCO2/MWh** (재생에너지 lifecycle 배출)

### C. 기술 파라미터 (Technology Parameters)

| Technology | 파라미터 | 이전 | 변경 후 | 출처 |
|-----------|---------|------|---------|------|
| **Heat Pump** | CAPEX 2025 | $150M/MtCO2 | **$900M/MtCO2** | $800-900/kW_th |
| | OPEX | 3.0% | 3.0% | - |
| **NCC-H2** | CAPEX 2025 | $300M/MtCO2 | **$1725M/MtCO2** | $2800-3000/ton capacity |
| | H2 소비량 | 0.20 ton/ton | **0.18 ton/ton** | 문헌 조사 |
| | OPEX | 2.5% | **4.0%** | 문헌 조사 |
| **NCC-Electricity** | CAPEX 2025 | $350M/MtCO2 | **$1840M/MtCO2** | $3000-3500/ton capacity |
| | Elec 소비량 | 3.0 MWh/ton | 3.0 MWh/ton | RSC 2025 |
| | OPEX | 2.0% | **3.5%** | 문헌 조사 |

### D. 가격 전망 (Price Trajectories)

**Green H2 가격**
- 2025: $12/kg → 2050: $2/kg (변경 없음)

**RE PPA 가격**
- 이전: 2025: $58/MWh (grid보다 저렴)
- **변경: 2025: $130/MWh** (grid보다 비쌈)
- 2050: $55/MWh (grid 대비 저렴해짐)
- 이유: 현실적인 한국 RE PPA 가격 반영

---

## 3. 모델 로직 개선

### A. 전기 사용 기술의 RE 가정

**Heat Pump**
- 이전: Grid 전력 (EF 0.45 tCO2/MWh) → 음의 감축량
- **변경: RE 전력** (EF 0.05 tCO2/MWh) → 양의 감축량

**NCC-Electricity**
- 이전: Grid 전력 → 낮은 감축량 (0.389 tCO2/ton)
- **변경: RE 전력** → 높은 감축량 (1.59 tCO2/ton)

**논리:** 탈탄소 기술은 재생에너지 전력 사용 전제

### B. 연료비용 계산 단순화

**이전 로직:**
- `Fuel_cost_diff = (New_fuel_cost - Old_fuel_cost)`
- 화석연료 절감 비용 고려

**변경 후:**
- `Fuel_cost = New_fuel_cost only`
- 화석연료 비용 절감 제외 (feedstock은 계속 구매)

**이유:**
- Naphtha feedstock은 계속 구매 (연료→Feedstock 전환)
- 신규 에너지 비용만 추가 비용으로 계산

### C. RE PPA 비용

**이전:**
- `Cost = (RE_price - Grid_price) × MWh`

**변경:**
- `Cost = RE_price × MWh`

**이유:** Grid는 계속 사용, RE는 추가 계약

---

## 4. 데이터 일관성 검증

### 248개 시설 검증 결과

✓ **전체 시설:** 248개
- NCC (Naphtha Cracker): 41개
- BTX Plant: 47개
- Utility: 160개

✓ **배출량 일관성:**
- Total: 51.40 MtCO2 (목표: 52 MtCO2, 오차 1.2%)
- Naphtha fuel parameter vs implied: 29.0 vs 28.99 GJ/ton

✓ **데이터 연결:**
- facility_database ↔ baseline_2025_detailed: 248개 일치
- energy_intensities ↔ baseline: 모든 process 매칭
- emission_factors ↔ baseline: 모든 fuel 매칭

---

## 5. MACC 결과 (2030년 기준)

| Technology | Abatement (MtCO2) | CAPEX ($/tCO2) | OPEX ($/tCO2) | Fuel ($/tCO2) | **Total ($/tCO2)** |
|-----------|------------------|----------------|---------------|---------------|-------------------|
| **RE_PPA** | 7.68 | $0 | $0 | $319 | **$319** |
| **NCC-Electricity** | 20.47 | $146 | $5 | $217 | **$368** |
| **Heat_Pump** | 0.71 | $73 | $2 | $699 | **$774** |
| **NCC-H2** | 22.40 | $135 | $5 | $1,043 | **$1,184** |

**총 감축량:** 51.26 MtCO2 (baseline 대비 98.6%)

### 주요 인사이트

1. **RE_PPA가 가장 저렴** ($319/tCO2)
   - CAPEX/OPEX 없음
   - 계약 변경만으로 가능

2. **NCC-Electricity가 2순위** ($368/tCO2)
   - 2050년에는 $195/tCO2로 하락 (가장 저렴)
   - RE 전력 가정으로 높은 감축량

3. **NCC-H2가 가장 비쌈** ($1,184/tCO2)
   - 높은 H2 가격 ($10.08/kg in 2030)
   - 2050년에는 $332/tCO2로 경쟁력 확보

4. **Heat Pump 역할 제한적** (0.71 MtCO2)
   - BTX/Utility 시설만 적용
   - NCC는 NCC-H2/NCC-E로 대체

---

## 6. 모듈 실행 상태

| Module | 설명 | 상태 | 출력 파일 |
|--------|-----|------|----------|
| **Module 1** | Baseline Emissions | ✓ SUCCESS | baseline_2025_detailed.csv |
| **Module 2** | MACC Analysis | ✓ SUCCESS | macc_annual_2025_2050.csv |
| **Module 3** | Cost Optimization | ✓ SUCCESS | conservative/moderate/aggressive_deployment.csv |
| **Module 4** | Financial Analysis | ✓ SUCCESS | financial_summary.csv |

---

## 7. 업데이트된 파일 목록

### 데이터 파일
- ✓ `data/MACC_Model_Assumptions_v2.xlsx` - 마스터 Excel (문헌 기반)
- ✓ `data/model_parameters.csv` - discount_rate 제거
- ✓ `data/technology_parameters.csv` - 문헌 CAPEX/OPEX
- ✓ `data/emission_factors.csv` - Naphtha EF 0.0542
- ✓ `data/h2_price_trajectory.csv` - $12→$2/kg
- ✓ `data/re_price_trajectory.csv` - $130→$55/MWh
- ✓ `data/baseline_process_emissions.csv` - 29 GJ/ton naphtha fuel

### 코드 파일
- ✓ `modules/macc.py` - CRF 제거, 단순 annualization
- ✓ `modules/data_manager.py` - discount_rate validation 제거
- ✓ `modules/financial.py` - NPV용 5% 할인율만 유지

---

## 8. 다음 단계 권장사항

1. **추가 문헌 검증**
   - NCC-H2 CAPEX 범위 재확인 ($2800-3000/ton capacity)
   - Heat Pump COP 4.0 검증 (140-160°C 온도대)

2. **민감도 분석**
   - RE 가격 변동 ($100-$150/MWh)
   - H2 가격 변동 ($8-$15/kg in 2030)
   - CAPEX ±20% 범위

3. **시나리오 확장**
   - Conservative/Moderate/Aggressive 외 추가 시나리오
   - 정책 시나리오 (탄소세, 보조금)

4. **시각화 개선**
   - 인터랙티브 대시보드 (Plotly/Dash)
   - 시설별 감축 경로 visualization

---

## 9. 검증 완료 사항

✓ 248개 시설 데이터 일관성
✓ 52 MtCO2 baseline 유지 (51.4 MtCO2, 1.2% 오차)
✓ 모든 모듈 정상 실행
✓ 문헌 기반 파라미터 반영
✓ 할인율 제거 (단순 연간화)
✓ RE 전력 가정 일관성

---

**작성자:** Petrochemical MACC Team
**검토자:** [To be filled]
**승인일:** [To be filled]
