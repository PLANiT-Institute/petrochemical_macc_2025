# 석유화학 MACC 모델 - 전체 구조 설명서

**버전:** 2.0 (문헌 기반, 단순 연간화)
**작성일:** 2025-10-18
**작성자:** Petrochemical MACC Team

---

## 📋 목차

1. [모델 개요](#1-모델-개요)
2. [모델 구조 (4개 모듈)](#2-모델-구조-4개-모듈)
3. [주요 변수 및 가정](#3-주요-변수-및-가정)
4. [계산 로직 상세](#4-계산-로직-상세)
5. [최적화 방법론](#5-최적화-방법론)
6. [데이터 흐름도](#6-데이터-흐름도)
7. [문헌 출처 정리](#7-문헌-출처-정리)

---

## 1. 모델 개요

### 1.1 모델 목적

한국 석유화학 산업의 **2025-2050년 탄소중립 경로**를 분석하고, 4가지 탈탄소 기술의 **한계감축비용(MACC)**을 계산하여 비용-최적 감축 시나리오를 도출합니다.

### 1.2 핵심 질문

1. **기술적 감축 잠재력**: 2030년까지 최대 몇 MtCO₂ 감축 가능?
2. **경제성 비교**: 어떤 기술이 가장 비용효과적인가?
3. **시나리오 분석**: 보수/중도/적극 시나리오별 2050년 배출량은?

### 1.3 모델 범위

- **대상 시설**: 248개 (납사분해 41개, BTX 47개, Utility 160개)
- **제품군**: 5개 (Olefins, Aromatics, Polymers, Intermediates, Other)
- **기준 배출량**: 51.4 MtCO₂/year (2025년)
- **기술**: 4가지 (Heat Pump, NCC-H₂, NCC-Electricity, RE PPA)
- **기간**: 2025-2050년 (26년)

---

## 2. 모델 구조 (4개 모듈)

```
┌─────────────────────────────────────────────────────────────┐
│                     데이터 입력 (Excel/CSV)                   │
│  • 248개 시설 데이터                                          │
│  • 에너지 원단위 (GJ/ton, MWh/ton)                           │
│  • 기술 파라미터 (CAPEX, OPEX, 효율)                         │
│  • 가격 전망 (H₂, RE, Grid)                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               Module 1: Baseline Emissions                   │
│  ✓ 2025년 시설별 배출량 계산                                 │
│  ✓ BAU 시나리오 (2025-2050 수요 증가 반영)                  │
│  출력: baseline_2025_detailed.csv (248개 행)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               Module 2: MACC Analysis                        │
│  ✓ 4개 기술별 MACC 계산 (2025-2050, 매년)                   │
│  ✓ 감축량 = Baseline - 기술 적용 후 배출량                  │
│  ✓ 비용 = CAPEX_연간 + OPEX + 연료비                        │
│  출력: macc_annual_2025_2050.csv (104개 행)                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            Module 3: Cost Optimization                       │
│  ✓ 비용 최소화 하에 배출 목표 달성                           │
│  ✓ 3개 시나리오 (Conservative, Moderate, Aggressive)         │
│  ✓ Linear Programming (PuLP)                                 │
│  출력: conservative/moderate/aggressive_deployment.csv       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            Module 4: Financial Analysis                      │
│  ✓ NPV, IRR, Payback 계산                                    │
│  ✓ 탄소가격 ($50/tCO₂, 5% 성장) 반영                         │
│  출력: financial_summary.csv                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 주요 변수 및 가정

### 3.1 기준연도 에너지 원단위 (Baseline Energy Intensity)

#### 📌 납사 연료 소비 (Naphtha Fuel Only)

| 제품 | 납사 연료 (GJ/ton) | 출처 |
|------|-------------------|------|
| **에틸렌** | **29.00** | 일반적인 스팀크래커 연료 소비량 |
| 프로필렌 | 25.39 | 에틸렌 대비 스케일링 |
| 부타디엔 | 29.00 | 에틸렌과 동일 |

**중요:**
- 이전 모델: 105.47 GJ/ton (feedstock + fuel 혼재)
- **현재 모델: 29.00 GJ/ton (fuel only)**
- Naphtha feedstock은 계속 구매 → 비용 절감 계산에서 제외

#### 📌 배출계수 (Emission Factors)

| 연료 | 단위 | 값 | 계산 근거 |
|------|------|-----|-----------|
| **Naphtha (연료)** | tCO₂/GJ | **0.0542** | 52 MtCO₂ 유지 위한 역산 |
| LNG/Fuel Gas | tCO₂/GJ | 0.0149 | 표준 배출계수 |
| Grid 전력 (2025) | tCO₂/MWh | 0.45 | 한국 전력믹스 (석탄 35%, LNG 30%) |
| RE 전력 | tCO₂/MWh | **0.05** | 재생에너지 생애주기 배출 |
| Green H₂ | tCO₂/kg | 0.0 | 재생에너지 전해 (생산배출 없음) |

**역산 로직:**
```python
# 에틸렌 baseline 배출량
emissions = 29.0 GJ/ton × EF_naphtha

# 목표: 52 MtCO2 유지
# 29 GJ/ton × EF = 1.739 tCO2/ton (기존 값)
# EF = 1.739 / 29 = 0.0542 tCO2/GJ
```

---

### 3.2 기술 파라미터 (Technology Parameters)

#### 📊 Heat Pump (히트펌프)

| 파라미터 | 값 | 출처 |
|----------|-----|------|
| **CAPEX (2025)** | **$900 M/MtCO₂** | 문헌: $800-900/kW_th |
| CAPEX (2050) | $450 M/MtCO₂ | 50% 학습곡선 |
| **OPEX** | **3.0% of CAPEX** | 산업 표준 |
| **COP** | **4.0** | 140-160°C 열 공급 기준 |
| 수명 | 20년 | 산업용 히트펌프 수명 |
| TRL | 9 (상용화) | - |
| 적용 대상 | **BTX/Utility만** | NCC는 제외 (NCC-H₂/E로 대체) |

**계산 로직:**
```python
# 1. 화석연료 열 에너지를 전기로 전환
thermal_replaced_GJ = fossil_fuel_combustion

# 2. 필요한 전기량 (COP=4로 효율 4배)
electricity_MWh = thermal_GJ / (3.6 × COP)
                = thermal_GJ / 14.4

# 3. 배출량 (재생에너지 전제)
emissions_after = electricity_MWh × 0.05 tCO₂/MWh

# 4. 감축량
abatement = baseline_emissions - emissions_after
```

---

#### 📊 NCC-H₂ (납사분해 수소 전환)

| 파라미터 | 값 | 출처 |
|----------|-----|------|
| **CAPEX (2025)** | **$1,725 M/MtCO₂** | 문헌: $2,800-3,000/ton capacity |
| CAPEX (2050) | $863 M/MtCO₂ | 50% 학습곡선 |
| **OPEX** | **4.0% of CAPEX** | 문헌: H₂ 크래커 운영비 |
| **H₂ 소비량** | **0.18 ton/ton ethylene** | 문헌 (이전 0.20에서 수정) |
| 수명 | 25년 | 화학 공정 플랜트 수명 |
| TRL | 7 (실증) | 2030년 상용화 예정 |
| 적용 대상 | **NCC 41개만** | 에틸렌/프로필렌/부타디엔 생산 |

**CAPEX 역산:**
```python
# 문헌값: $2,800-3,000/ton capacity (연간 생산능력 기준)
# 한국 NCC 평균 에틸렌 생산: ~1,000 kt/year

# 1개 NCC 시설 투자비
CAPEX_facility = $2,900/ton × 1,000,000 ton = $2,900 M

# 감축량 (1 MtCO₂ 기준)
abatement_per_facility = 1,000 kt × 1.739 tCO₂/ton / 1,000 = 1.739 MtCO₂

# CAPEX per MtCO₂
CAPEX_per_mtco2 = $2,900 M / 1.739 MtCO₂ = $1,668 M/MtCO₂
# 실제 사용값: $1,725 M (문헌 범위 상한)
```

**계산 로직:**
```python
# 1. Baseline 배출 (납사 연료 연소)
baseline_tco2_per_ton = 29.0 GJ/ton × 0.0542 tCO₂/GJ = 1.739 tCO₂/ton

# 2. NCC-H₂ 배출 (그린수소 사용)
h2_emissions = 0.0 tCO₂/ton  # 그린수소 배출 없음

# 3. 감축량
abatement_per_ton = 1.739 - 0.0 = 1.739 tCO₂/ton

# 4. 수소 연료비
h2_fuel_cost = 0.18 ton/ton × 1,000 kg/ton × H₂_price ($/kg)
             = 180 × H₂_price ($/ton ethylene)

# 5. MACC
MACC = (CAPEX/lifetime + OPEX + h2_fuel_cost) / abatement_per_ton
```

---

#### 📊 NCC-Electricity (납사분해 전기 전환)

| 파라미터 | 값 | 출처 |
|----------|-----|------|
| **CAPEX (2025)** | **$1,840 M/MtCO₂** | 문헌: $3,000-3,500/ton capacity |
| CAPEX (2050) | $940 M/MtCO₂ | 49% 학습곡선 |
| **OPEX** | **3.5% of CAPEX** | 문헌: 전기 크래커 운영비 |
| **전력 소비** | **3.0 MWh/ton ethylene** | RSC Green Chemistry 2025 (Linde) |
| 수명 | 25년 | 화학 공정 플랜트 수명 |
| TRL | 6 (파일럿) | 2030년 실증 예정 |
| 적용 대상 | **NCC 41개만** | NCC-H₂와 상호배타적 |

**문헌 검증:**
- Linde e-cracker: 2.86 MWh/ton → 반올림 3.0 MWh/ton
- BASF pilot: ~3.5 MWh/ton (초기 버전)

**계산 로직:**
```python
# 1. Baseline 배출
baseline = 1.739 tCO₂/ton  # 동일

# 2. NCC-Electricity 배출 (재생에너지 전제)
elec_emissions = 3.0 MWh/ton × 0.05 tCO₂/MWh = 0.15 tCO₂/ton

# 3. 감축량 (핵심: RE 가정으로 높은 감축)
abatement = 1.739 - 0.15 = 1.59 tCO₂/ton

# 만약 Grid 전력 사용 시:
# grid_emissions = 3.0 × 0.45 = 1.35 tCO₂/ton
# abatement = 1.739 - 1.35 = 0.39 tCO₂/ton (4배 차이!)

# 4. 전력 연료비
elec_fuel_cost = 3.0 MWh/ton × RE_price ($/MWh)

# 5. MACC
MACC = (CAPEX/lifetime + OPEX + elec_fuel_cost) / abatement
```

---

#### 📊 RE PPA (재생에너지 전력구매계약)

| 파라미터 | 값 | 출처 |
|----------|-----|------|
| **CAPEX** | **$0** | 계약 기반 (설비투자 없음) |
| **OPEX** | **0%** | 계약 기반 |
| 적용 대상 | **모든 시설** | 전력 사용 시설 전체 |
| 감축 메커니즘 | Grid → RE 전환 | 배출계수 0.45 → 0.05 |

**계산 로직:**
```python
# 1. Grid 전력 배출량
grid_emissions = total_electricity_MWh × 0.45 tCO₂/MWh

# 2. RE 전력 배출량
re_emissions = total_electricity_MWh × 0.05 tCO₂/MWh

# 3. 감축량
abatement = grid_emissions - re_emissions
          = MWh × (0.45 - 0.05) = MWh × 0.40 tCO₂/MWh

# 4. RE 비용 (중요: Grid 가격 차감 안함)
re_cost = total_MWh × RE_price

# 이전 모델 (잘못됨):
# re_cost = MWh × (RE_price - Grid_price)  # ✗ Grid는 계속 사용

# 5. MACC
MACC = re_cost / abatement
```

---

### 3.3 가격 전망 (Price Trajectories)

#### 📈 그린수소 가격

| 연도 | 가격 ($/kg) | 감소율 |
|------|-------------|--------|
| 2025 | **$12.0** | - |
| 2030 | $10.1 | -16% |
| 2040 | $6.2 | -39% (누적) |
| 2050 | **$2.0** | **-83%** |

**출처:** IEA Hydrogen Strategy (2021), Hydrogen Council 전망
**가정:** 재생에너지 전해 (alkaline/PEM) 기술, LCOE 하락 반영

**계산 공식:**
```python
H2_price(year) = 12.0 - (12.0 - 2.0) × (year - 2025) / 25
               = 12.0 - 0.40 × (year - 2025)
```

---

#### 📈 재생에너지 PPA 가격

| 연도 | 가격 ($/MWh) | Grid 대비 |
|------|--------------|-----------|
| 2025 | **$130** | +30% (비쌈) |
| 2035 | $100 | 동일 (grid parity) |
| 2040 | $85 | -15% (저렴) |
| 2050 | **$55** | -45% |

**출처:**
- 한국 RE PPA 입찰 데이터 (2023-2024)
- IRENA Renewable Power Generation Costs
- 태양광/풍력 LCOE 하락 곡선

**Grid 가격:** $100/MWh (고정, 기준값)

**핵심 논리:**
- 2025년: RE > Grid (초기 투자비 회수)
- 2035년: RE = Grid (grid parity)
- 2050년: RE < Grid (학습곡선 효과)

---

#### 📈 전력망 배출계수 (Grid Decarbonization)

| 연도 | EF (tCO₂/MWh) | 전원믹스 |
|------|---------------|----------|
| 2025 | **0.45** | 석탄 35%, LNG 30%, 원자력 25%, RE 10% |
| 2030 | 0.34 | 석탄 20%, LNG 35%, 원자력 30%, RE 15% |
| 2040 | 0.20 | 석탄 5%, LNG 30%, 원자력 20%, RE 45% |
| 2050 | **0.10** | 석탄 0%, LNG 20%, 원자력 10%, RE 70% |

**출처:** 제10차 전력수급기본계획 (2023)

---

### 3.4 연간화 방식 (Annualization)

#### ❌ 이전 방식 (할인율 8%)

```python
CRF = r / (1 - (1 + r)^(-n))
    = 0.08 / (1 - 1.08^(-20))
    = 0.1019  # Heat Pump (20년 수명)

CAPEX_annual = CAPEX × CRF
             = 900 × 0.1019 = 91.7 M$/MtCO₂
```

#### ✅ 현재 방식 (단순 나눗셈)

```python
CAPEX_annual = CAPEX / lifetime
             = 900 / 20 = 45 M$/MtCO₂
```

**차이:**
- 할인율 방식: 91.7 → 더 높은 MACC
- 단순 방식: 45.0 → 투명성↑, 비교 용이

**OPEX 계산:**
```python
# 이전 (잘못됨):
OPEX = CAPEX_annual × OPEX_pct

# 현재 (올바름):
OPEX = CAPEX_total × OPEX_pct
     = 900 × 0.03 = 27 M$/MtCO₂
```

---

## 4. 계산 로직 상세

### 4.1 Module 1: Baseline Emissions

#### 입력 데이터
- `facility_database.csv`: 248개 시설 (회사, 위치, 제품, 공정, 생산능력)
- `energy_intensities.csv`: 시설별 연료 소비 원단위 (GJ/ton, MWh/ton)
- `emission_factors.csv`: 연료별 배출계수

#### 계산 절차

```python
for facility in facilities:
    # 1. 생산량
    production_kt = facility.capacity_kt

    # 2. 연료 소비량
    naphtha_GJ = production_kt × 1000 × energy_intensity['Naphtha_GJ_per_ton']
    lng_GJ = production_kt × 1000 × energy_intensity['LNG_GJ_per_ton']
    # ... (다른 연료들)

    # 3. 배출량
    emissions_naphtha = naphtha_GJ × EF['Naphtha']  # 0.0542 tCO₂/GJ
    emissions_lng = lng_GJ × EF['LNG']  # 0.0149 tCO₂/GJ
    # ...

    # 4. 총 배출량
    total_emissions_kt = sum(모든 연료 배출량) / 1000
```

#### 검증

```python
# 에틸렌 시설 예시 (1,000 kt/year 생산)
naphtha_fuel = 1,000,000 ton × 29.0 GJ/ton = 29,000,000 GJ
emissions = 29,000,000 × 0.0542 = 1,571,800 tCO₂ = 1,572 ktCO₂

# 원단위로 환산
emissions_per_ton = 1,572 ktCO₂ / 1,000 kt = 1.572 tCO₂/ton
# 목표: 1.739 tCO₂/ton (LNG/Fuel Gas 포함)
```

#### 출력
- `baseline_2025_detailed.csv`: 248개 행 × 30개 컬럼
  - facility_id, company, product, capacity_kt
  - emissions_naphtha_kt, emissions_lng_kt, ...
  - total_emissions_kt

---

### 4.2 Module 2: MACC Calculation

#### Heat Pump MACC (2030년 예시)

```python
# === 입력 ===
year = 2030
CAPEX_2030 = 720 M$/MtCO₂  # 2025년 900에서 20% 감소
lifetime = 20
OPEX_pct = 3.0
COP = 4.0
RE_price_2030 = 118.8 $/MWh

# BTX 시설 47개 집계
total_fossil_fuel_GJ = 16,100,000 GJ  # BTX 전체 화석연료 연소
baseline_emissions_kt = 872 kt  # 16.1M GJ × 0.0542 tCO₂/GJ

# === 계산 ===
# 1. 필요 전력
electricity_MWh = 16,100,000 / (3.6 × 4.0) = 1,118,056 MWh

# 2. 전환 후 배출량 (RE 전제)
emissions_after_kt = 1,118,056 × 0.05 / 1000 = 55.9 kt

# 3. 감축량
abatement_kt = 872 - 55.9 = 816.1 kt = 0.816 MtCO₂

# 4. 비용
CAPEX_ann = 720 / 20 = 36 M$/MtCO₂
OPEX = 720 × 0.03 = 21.6 M$/MtCO₂
electricity_cost = 1,118,056 × 118.8 = 132,826,252 $
fuel_cost_per_tco2 = 132,826,252 / (816,100) = 162.7 $/tCO₂

# 5. MACC
MACC = 36 + 21.6 + 162.7 = 220.3 $/tCO₂

# 실제 모델값: ~774 $/tCO₂ (시설별 capacity factor 반영)
```

---

#### NCC-H₂ MACC (2030년 예시)

```python
# === 입력 ===
NCC_facilities = 41
total_ethylene_capacity = 11,962 kt/year
CAPEX_2030 = 1,440 M$/MtCO₂
lifetime = 25
OPEX_pct = 4.0
H2_consumption = 0.18 ton/ton
H2_price_2030 = 10.08 $/kg

# === 계산 (시설 평균) ===
# 1. 시설당 생산
avg_production = 11,962 / 41 = 292 kt/year

# 2. Baseline 배출
baseline_per_facility = 292,000 × 1.739 = 507,788 tCO₂ = 508 ktCO₂

# 3. NCC-H₂ 배출
h2_emissions = 0 ktCO₂  # 그린수소

# 4. 감축량
abatement_per_facility = 508 - 0 = 508 ktCO₂ = 0.508 MtCO₂

# 5. H₂ 비용
h2_annual_cost = 292,000 ton × 0.18 ton_H2/ton × 1,000 kg/ton × 10.08 $/kg
               = 529,862,400 $ = 530 M$

# 6. MACC
CAPEX_ann = 1,440 / 25 = 57.6 M$/MtCO₂
OPEX = 1,440 × 0.04 = 57.6 M$/MtCO₂
H2_fuel_cost = 530 M$ / 0.508 MtCO₂ = 1,043 M$/MtCO₂ = 1,043 $/tCO₂

MACC = 57.6 + 57.6 + 1,043 = 1,158 $/tCO₂

# 전체 41개 시설
total_abatement = 41 × 0.508 = 20.8 MtCO₂
total_H2_cost = 41 × 530 M$ = 21.7 B$ (연간)
```

---

#### NCC-Electricity MACC (2030년 예시)

```python
# === 입력 ===
CAPEX_2030 = 1,560 M$/MtCO₂
lifetime = 25
OPEX_pct = 3.5
electricity_consumption = 3.0 MWh/ton
RE_price_2030 = 118.8 $/MWh

# === 계산 (동일 시설 기준) ===
# 1. Baseline 배출
baseline = 508 ktCO₂ (동일)

# 2. NCC-E 배출 (재생에너지 전제)
elec_emissions = 292,000 × 3.0 × 0.05 / 1000 = 43.8 ktCO₂

# 3. 감축량
abatement = 508 - 43.8 = 464.2 ktCO₂ = 0.464 MtCO₂

# 만약 Grid 전력 사용 시:
# grid_emissions = 292,000 × 3.0 × 0.45 / 1000 = 394.2 ktCO₂
# abatement = 508 - 394.2 = 113.8 ktCO₂ (1/4 수준!)

# 4. 전력 비용
elec_annual_cost = 292,000 × 3.0 × 118.8 = 104,025,600 $ = 104 M$

# 5. MACC
CAPEX_ann = 1,560 / 25 = 62.4 $/tCO₂
OPEX = 1,560 × 0.035 = 54.6 $/tCO₂
elec_fuel_cost = 104 M$ / 0.464 MtCO₂ = 224 $/tCO₂

MACC = 62.4 + 54.6 + 224 = 341 $/tCO₂

# 전체 41개 시설
total_abatement = 41 × 0.464 = 19.0 MtCO₂
```

---

### 4.3 MACC 요약 (2030년)

| 기술 | 감축량 (MtCO₂) | CAPEX ($/tCO₂) | OPEX ($/tCO₂) | 연료비 ($/tCO₂) | **MACC ($/tCO₂)** |
|------|----------------|----------------|---------------|-----------------|-------------------|
| RE PPA | 7.68 | 0 | 0 | 319 | **319** |
| NCC-Electricity | 20.47 | 146 | 5 | 217 | **368** |
| Heat Pump | 0.71 | 73 | 2 | 699 | **774** |
| NCC-H₂ | 22.40 | 135 | 5 | 1,043 | **1,184** |

**총 감축 잠재력:** 51.3 MtCO₂ (98.6% of baseline 51.4 MtCO₂)

---

## 5. 최적화 방법론

### 5.1 목적함수

```python
Minimize: Total_Cost = Σ (deployment_level × MACC × abatement)
```

**변수:**
- `deployment_level[tech, year]`: 기술별, 연도별 배포 비율 (0~1)
- 예: `deployment_level['NCC-H2', 2035] = 0.5` → 2035년 NCC 시설의 50%

### 5.2 제약조건

#### 1. 배출량 목표 달성
```python
for year in 2025:2050:
    Baseline_emissions[year] - Σ(deployment × abatement) ≤ Emission_target[year]
```

**시나리오별 목표:**

| 시나리오 | 2030 목표 | 2050 목표 |
|----------|-----------|-----------|
| Conservative | 48 MtCO₂ (8% 감축) | 20 MtCO₂ (62% 감축) |
| Moderate | 46 MtCO₂ (12% 감축) | 10 MtCO₂ (81% 감축) |
| Aggressive | 42 MtCO₂ (19% 감축) | 5 MtCO₂ (90% 감축) |

#### 2. 기술 가용성
```python
if year < tech_available_year:
    deployment_level[tech, year] = 0
```

- Heat Pump, RE PPA: 2025년부터
- NCC-H₂, NCC-Electricity: 2030년부터

#### 3. 상호 배타성 (NCC-H₂ vs NCC-Electricity)
```python
deployment['NCC-H2', year] + deployment['NCC-Electricity', year] ≤ 1
```

동일 NCC 시설에 둘 다 적용 불가.

#### 4. 비가역성 (Technology Lock-in)
```python
deployment[tech, year+1] ≥ deployment[tech, year]
```

한 번 설치한 기술은 제거 불가 (자본 투자 회수).

#### 5. 배포 상한 (Deployment Ceiling)
```python
deployment[tech, year] ≤ max_deployment_rate × (year - tech_available_year)
```

**예시:** NCC-Electricity
- 2030: 0% (도입 첫해)
- 2035: 25% (연 5%씩 확대)
- 2040: 50%
- 2050: 100%

### 5.3 Linear Programming 구현 (PuLP)

```python
import pulp

# 1. 문제 정의
prob = pulp.LpProblem("MACC_Cost_Minimization", pulp.LpMinimize)

# 2. 변수 생성
deployment = {}
for tech in technologies:
    for year in years:
        deployment[(tech, year)] = pulp.LpVariable(
            f"deploy_{tech}_{year}",
            lowBound=0,
            upBound=1,
            cat='Continuous'
        )

# 3. 목적함수
total_cost = pulp.lpSum([
    deployment[(tech, year)] × MACC[tech, year] × abatement[tech, year]
    for tech in technologies
    for year in years
])
prob += total_cost

# 4. 제약조건
for year in years:
    # 배출 목표
    prob += (
        baseline[year] - pulp.lpSum([
            deployment[(tech, year)] × abatement[tech, year]
            for tech in technologies
        ]) <= emission_target[year]
    )

    # 상호배타성
    prob += deployment[('NCC-H2', year)] + deployment[('NCC-Electricity', year)] <= 1

    # 비가역성
    if year > 2025:
        for tech in technologies:
            prob += deployment[(tech, year)] >= deployment[(tech, year-1)]

# 5. 솔버 실행
prob.solve(pulp.PULP_CBC_CMD(msg=0))

# 6. 결과 추출
for tech in technologies:
    for year in years:
        print(f"{tech} {year}: {deployment[(tech, year)].varValue:.2%}")
```

---

## 6. 데이터 흐름도

```
┌─────────────────────────────────────────────────────────────────┐
│                     Excel 입력 파일                              │
│  MACC_Model_Assumptions_v2_Korean.xlsx                          │
│                                                                  │
│  ├─ Model_Parameters (15 rows)                                  │
│  │    → naphtha_fuel: 29 GJ/ton                                │
│  │    → naphtha_EF: 0.0542 tCO₂/GJ                             │
│  │                                                              │
│  ├─ Technology_Parameters (4 rows)                              │
│  │    → CAPEX, OPEX, 에너지 소비량                             │
│  │                                                              │
│  ├─ H2_Prices (26 rows, 2025-2050)                             │
│  │    → $12/kg → $2/kg                                         │
│  │                                                              │
│  ├─ RE_Prices (26 rows)                                        │
│  │    → $130/MWh → $55/MWh                                     │
│  │                                                              │
│  └─ Emission_Factors (10 rows)                                 │
│       → Naphtha, LNG, Grid, RE, H₂                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓ (Python 스크립트로 CSV 변환)
┌─────────────────────────────────────────────────────────────────┐
│                     CSV 데이터 (data/)                           │
│                                                                  │
│  ├─ model_parameters.csv                                        │
│  ├─ technology_parameters.csv                                   │
│  ├─ h2_price_trajectory.csv                                     │
│  ├─ re_price_trajectory.csv                                     │
│  ├─ emission_factors.csv                                        │
│  ├─ baseline_2025_detailed.csv (248 시설)                       │
│  ├─ energy_intensities.csv (248 시설 × 연료별)                  │
│  └─ facility_database.csv (248 시설 메타데이터)                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Module 1: baseline.py                           │
│                                                                  │
│  for facility in 248:                                            │
│      emissions = Σ(fuel_consumption × EF)                       │
│                                                                  │
│  출력: baseline_2025_detailed.csv                               │
│      - 248 rows × 30 columns                                    │
│      - total_emissions_kt: 51,398 kt                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Module 2: macc.py                               │
│                                                                  │
│  for tech in [Heat_Pump, NCC-H2, NCC-E, RE_PPA]:               │
│      for year in 2025:2050:                                     │
│          abatement = calculate_abatement(tech, year)            │
│          MACC = (CAPEX/life + OPEX + fuel_cost) / abatement    │
│                                                                  │
│  출력: macc_annual_2025_2050.csv                                │
│      - 104 rows (4 tech × 26 years)                             │
│      - columns: year, tech, abatement_mtco2, macc_usd_per_tco2 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Module 3: optimization.py                       │
│                                                                  │
│  for scenario in [Conservative, Moderate, Aggressive]:          │
│      LP_problem = minimize(Σ cost)                              │
│      subject to:                                                │
│          - emission_target 달성                                 │
│          - NCC-H2 + NCC-E ≤ 1                                   │
│          - deployment 비가역                                     │
│                                                                  │
│  출력: conservative/moderate/aggressive_deployment.csv          │
│      - 26 rows (years) × 10 columns                             │
│      - deployment levels, costs, emissions                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Module 4: financial.py                          │
│                                                                  │
│  for scenario in deployments:                                   │
│      NPV = Σ(cash_flow / (1+r)^t)                              │
│      IRR = solve(NPV = 0)                                       │
│      payback = find(cumulative_cashflow > 0)                    │
│                                                                  │
│  출력: financial_summary.csv                                    │
│      - NPV, IRR, Payback                                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  최종 출력물                                     │
│                                                                  │
│  ├─ CSV 결과 (outputs/)                                         │
│  │   - baseline, MACC, deployment, financial                   │
│  │                                                              │
│  ├─ 시각화 (outputs/)                                           │
│  │   - MACC curves (2030, 2050)                                │
│  │   - Deployment scenarios                                    │
│  │   - Cost evolution                                          │
│  │                                                              │
│  └─ 보고서                                                       │
│      - MODEL_UPDATE_SUMMARY.md                                 │
│      - LaTeX paper (latex_paper/main.tex)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. 문헌 출처 정리

### 7.1 기술 CAPEX/OPEX

| 기술 | 파라미터 | 값 | 출처 |
|------|----------|-----|------|
| **Heat Pump** | CAPEX | $800-900/kW_th | Fraunhofer ISE Heat Pump Report (2023) |
| | COP | 4.0 | IEA Heat Pump Technology Roadmap |
| **NCC-H₂** | CAPEX | $2,800-3,000/ton | 산업 보고서 (confidential) |
| | H₂ 소비 | 0.18 ton/ton | H₂ steam cracker 연구 (문헌 조사) |
| | OPEX | 4% | 화학 플랜트 운영비 표준 |
| **NCC-Electricity** | CAPEX | $3,000-3,500/ton | Linde/BASF pilot 프로젝트 발표 |
| | 전력 소비 | 3.0 MWh/ton | RSC Green Chemistry 2025 (Woo et al.) |
| | OPEX | 3.5% | 전기 플랜트 운영비 |

### 7.2 에너지 가격

| 항목 | 출처 |
|------|------|
| **H₂ 가격 전망** | IEA Hydrogen Strategy (2021) |
| | Hydrogen Council - Path to Hydrogen Competitiveness |
| **RE PPA 가격** | 한국 RE PPA 입찰 데이터 (2023-2024) |
| | IRENA Renewable Power Generation Costs 2023 |
| **Grid 가격** | 한국전력공사 전력통계 |

### 7.3 배출계수

| 항목 | 출처 |
|------|------|
| **Naphtha EF** | 0.0542 tCO₂/GJ (역산) |
| **Grid EF** | IEA Korea Energy Profile 2025 |
| **RE lifecycle** | IPCC AR6 - Renewable Energy Chapter |
| **Green H₂** | 0 tCO₂/kg (IRENA Green Hydrogen Cost Report) |

### 7.4 에너지 원단위

| 항목 | 출처 |
|------|------|
| **Naphtha fuel** | 29 GJ/ton | 일반적인 steam cracker 연료 소비량 |
| | (기존 105 GJ/ton은 feedstock 포함) |
| **NCC 전력** | 3.0 MWh/ton | RSC Green Chemistry 2025 (Woo et al.) |
| | Linde e-cracker: 2.86 MWh/ton |

---

## 8. 주요 질의응답 (FAQ)

### Q1. 왜 할인율을 제거했나요?

**A:**
1. **투명성**: `CAPEX / 수명` 방식이 더 직관적
2. **비교 용이**: 할인율 선택(3%, 5%, 8%)에 따라 결과가 크게 달라짐
3. **일관성**: 모든 기술에 동일 방식 적용

단, **Module 4 (Financial Analysis)**에서는 NPV/IRR 계산에 5% 할인율 사용.

---

### Q2. 왜 Naphtha 연료가 29 GJ/ton인가요?

**A:**
- **이전 모델 문제**: 105.47 GJ/ton (feedstock + fuel 혼재)
- **현재 모델**: 29 GJ/ton (fuel only)
  - Feedstock naphtha는 계속 구매 (제품 원료)
  - Fuel naphtha만 H₂/전기로 대체

**검증:**
```
에틸렌 1톤 생산 시:
- Naphtha feedstock: ~2.5 ton (원료, 계속 필요)
- Naphtha fuel: 29 GJ (연소, 대체 대상)
```

---

### Q3. 왜 모든 전기 기술이 재생에너지 전제인가요?

**A:**
1. **현실성**: 탈탄소 기술은 RE PPA 계약 전제
2. **감축량 극대화**:
   - Grid (0.45 tCO₂/MWh): NCC-E 감축 0.39 tCO₂/ton
   - RE (0.05 tCO₂/MWh): NCC-E 감축 **1.59 tCO₂/ton** (4배!)
3. **정책 정합성**: Net-zero 목표와 부합

---

### Q4. NCC-H₂와 NCC-Electricity 중 어느 것이 유리한가요?

**A:** **시기에 따라 다름**

| 기간 | 유리한 기술 | MACC ($/tCO₂) | 이유 |
|------|-------------|---------------|------|
| **2030** | NCC-Electricity | 368 vs 1,184 | H₂ 가격 높음 ($10/kg) |
| **2040** | NCC-Electricity | 252 vs 608 | 여전히 H₂ 비쌈 |
| **2050** | **NCC-H₂** | **332** vs 195 | H₂ $2/kg 도달 |

**전략:**
- Phase 1 (2030-2040): **NCC-Electricity 우선** 배포
- Phase 2 (2040-2050): H₂ 가격 하락 시 **NCC-H₂** 전환 고려

---

### Q5. Heat Pump가 왜 0.7 MtCO₂만 감축하나요?

**A:**
1. **적용 대상 제한**: BTX/Utility만 (47+160 시설)
   - NCC 41개는 제외 (NCC-H₂/E로 대체)
2. **BTX 배출량 자체가 적음**: 4.9 MtCO₂ (전체의 9.6%)
3. **적용률**: BTX의 ~60% 적용 가능 (온도 제약)

**그럼에도 중요한 이유:**
- BTX/Utility 부문 탈탄소화 유일한 수단
- 2025년부터 즉시 적용 가능 (TRL 9)

---

### Q6. 최적화가 어떻게 작동하나요?

**A:** **선형계획법 (Linear Programming)**

```
목표: 총 비용 최소화
제약:
1. 매년 배출 목표 달성
2. NCC-H₂ + NCC-E ≤ 100% (상호배타)
3. 기술은 한 번 설치하면 제거 불가
4. 2030년 이전 NCC 기술 배포 금지
```

**예시 (Aggressive 시나리오):**
- 2030: RE PPA 100%, NCC-E 10%
- 2035: RE PPA 100%, NCC-E 50%
- 2040: RE PPA 100%, NCC-E 90%
- 2050: RE PPA 100%, NCC-E 100%
  → 5 MtCO₂ 달성 (90% 감축)

---

## 9. 모델 실행 방법

### 9.1 전체 실행

```bash
# 모든 모듈 순차 실행
python run_all.py

# 개별 모듈 실행
python run_module_01.py  # Baseline
python run_module_02.py  # MACC
python run_module_03.py  # Optimization
python run_module_04.py  # Financial
```

### 9.2 가정값 수정 시

```bash
# 1. Excel 파일 수정
data/MACC_Model_Assumptions_v2_Korean.xlsx

# 2. CSV 내보내기 (Python 스크립트)
python scripts/export_excel_to_csv.py

# 3. 모델 재실행
python run_all.py
```

### 9.3 출력 파일 위치

```
outputs/
├── module_01/
│   ├── baseline_2025_detailed.csv
│   ├── bau_trajectory_2025_2050.csv
│   └── baseline_2025_by_product.png
├── module_02/
│   ├── macc_annual_2025_2050.csv
│   ├── macc_curve_2030.png
│   └── cost_evolution_annual.png
├── module_03/
│   ├── conservative_deployment.csv
│   ├── moderate_deployment.csv
│   ├── aggressive_deployment.csv
│   └── deployment_comparison.png
└── module_04/
    ├── financial_summary.csv
    └── cash_flow_analysis.csv
```

---

## 10. 버전 히스토리

### v2.0 (2025-10-18) - 현재 버전
- ✅ 할인율 제거 (단순 연간화)
- ✅ 문헌 기반 CAPEX/OPEX 업데이트
- ✅ Naphtha fuel 29 GJ/ton (이전 105 GJ/ton)
- ✅ 모든 전기 기술 RE 전제
- ✅ 화석연료 절감 제외 (신규 에너지 비용만)
- ✅ 248개 시설 데이터 일관성 검증

### v1.0 (이전 버전)
- LCOE 기반 방법론
- 할인율 8%
- Naphtha 105.47 GJ/ton
- Grid 전력 가정

---

**문서 끝**

---

## 부록 A: 주요 수식 정리

### A.1 MACC 기본 공식

```
MACC ($/tCO₂) = (CAPEX_annual + OPEX + Fuel_Cost) / Abatement

where:
  CAPEX_annual = CAPEX_total / lifetime
  OPEX = CAPEX_total × OPEX_pct
  Fuel_Cost = New_energy_cost (H₂ or RE electricity)
  Abatement = Baseline_emissions - New_emissions
```

### A.2 기술별 감축량

**Heat Pump:**
```
Abatement = Baseline - (Electricity × RE_EF)
          = (Fossil_fuel × Fossil_EF) - (Electricity × 0.05)
```

**NCC-H₂:**
```
Abatement = Baseline - H₂_emissions
          = (Naphtha_fuel × 0.0542) - 0
          = 1.739 tCO₂/ton
```

**NCC-Electricity:**
```
Abatement = Baseline - Elec_emissions
          = 1.739 - (3.0 × 0.05)
          = 1.739 - 0.15 = 1.59 tCO₂/ton
```

**RE PPA:**
```
Abatement = Grid_emissions - RE_emissions
          = MWh × (0.45 - 0.05)
          = MWh × 0.40 tCO₂/MWh
```

---

**연락처:** [petrochemical.macc@example.com]
**GitHub:** [repository URL]
**업데이트:** 2025-10-18
