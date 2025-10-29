# 한국 석유화학 MACC 모델 – 가정 및 결과 종합 설명서
**작성일**: 2025-10-23  
**모델 버전**: 2.2  
**적용 범위**: 한국 석유화학 산업 248개 시설 (2025-2050)

---

## 0. 문서 목적
- 프로젝트 전반의 가정·입력 데이터·방법론·시나리오 결과를 단일 문서로 집대성합니다.
- `data/`, `outputs/`, `modules/` 전역에서 사용 중인 실제 숫자와 경로를 그대로 인용하여 검증 가능한 기반을 제공합니다.
- 연구진·정책 담당자·모델 개발자가 동일한 정보 집합을 공유할 수 있도록 결과(한국 기준)와 근거를 연결합니다.

---

## 1. 모델 구조와 실행 파이프라인

### 1.1 모듈 구조 (코드: `modules/`)
1. **Module 1 – Baseline (`baseline.py`)**  
   - 입력: `data/baseline_2025_detailed.csv`, `data/energy_intensities.csv`  
   - 출력: `outputs/module_01/baseline_2025_detailed.csv`, `bau_trajectory_2025_2050.csv`, 제품·회사·지역별 분석 PNG
2. **Module 2 – MACC (`macc.py`)**  
   - 입력: Module 1 결과 + `data/technology_parameters.csv`, 가격/배출 궤적 CSV  
   - 출력: `outputs/module_02/macc_annual_2025_2050.csv`, `macc_cost_units_comparison.csv`
3. **Module 3 – 최적화 (`optimization.py`)**  
   - PuLP 기반 선형계획법.  
   - 출력: `outputs/module_03/*_deployment.csv`, `*_facility_allocation_2050.csv`, `scenario_summary_for_latex.csv`
4. **Module 4 – 재무분석 (`financial.py`)**  
   - 입력: 기본적으로 `conservative_deployment.csv` (최초 탐색 순서대로 로드)  
   - 출력: `outputs/module_04/financial_summary.csv`, `cash_flow_linear.csv`

### 1.2 실행 스크립트 및 산출물
- 전체 파이프라인: `python run_all.py`
- 모듈 단위 실행: `python run_module_0X.py`
- 시각화/보고서: `generate_report.py`, `visualize_sensitivity.py`, `latex_paper/main.tex`
- 핵심 CSV 산출물
  - `outputs/module_02/macc_annual_2025_2050.csv`: 연도·기술별 MACC 입력값
  - `outputs/module_03/aggressive_deployment.csv`: Aggressive 시나리오 연도별 최적 솔루션
  - `outputs/module_03/regional_baseline.csv`: 지역별 기준 배출 (2025)
  - `outputs/module_04/cash_flow_linear.csv`: 재무 모듈 현금흐름 (보수적 시나리오 기준)

---

## 2. 입력 데이터셋 요약 (`data/`)

### 2.1 주요 입력 파일
| 경로 | 내용 | 핵심 필드 |
|------|------|-----------|
| `data/baseline_2025_detailed.csv` | 248개 시설별 2025년 에너지 사용·배출량 | 제품/공정, GJ·kWh, 배출량(kt) |
| `data/energy_intensities.csv` | 시설별 단위 생산 에너지 원단위 | 연료·전력 GJ or kWh per ton |
| `data/facility_technology_applicability.csv` | 기술 적용 가능성 매트릭스 | Heat Pump, NCC-H₂, NCC-Elec, RE PPA 플래그 |
| `data/technology_parameters.csv` | 기술 CAPEX/OPEX, 수명, TRL | 연도별 CAPEX, OPEX%, lifetime |
| `data/technology_energy_requirements.csv` | 기술 전환 시 에너지 전환값 | H₂·전력 요구량, 효율 |
| `data/h2_price_trajectory.csv` | 2025-2050년 그린수소 가격 | $/kg |
| `data/re_price_trajectory.csv` | 2025-2050년 RE PPA 가격 | $/MWh |
| `data/grid_price_trajectory.csv` | 한전 전력요금 가정 | $/MWh |
| `data/grid_emission_trajectory.csv` | 전력 배출계수 경로 | tCO₂/MWh (2025~2075) |
| `data/fuel_price_trajectory.csv` | 납사·LNG 등 연료 가격 | $/GJ, 전력 $/kWh |
| `data/demand_growth_trajectory.csv` | 생산량 증가 시나리오 | 연도별 성장률, 누적 배수 |
| `data/emission_factors.csv` | 연료별 배출계수 | tCO₂/GJ |
| `data/model_parameters.csv` | 핵심 상수 | 납사 EF, COP, H₂ 소비량 등 |

### 2.2 시설 및 배출 기본 통계 (2025년)
| 항목 | 값 |
|------|----|
| 총 배출량 (`Σ total_emissions_kt`) | 52.001 MtCO₂ |
| 시설 수 | 248 |
| 납사 크래커 수 (`process == Naphtha Cracker`) | 41 |
| BTX 플랜트 수 | 47 |
| Utility/기타 | 160 |
| 고유 기업 수 | 60 |
| 고유 입지 수 | 14 |
| 전력 사용량 (`Σ electricity_kwh_per_year`) | 1.860 TWh |
| 연료 소비 합계 (`Σ GJ`) | 납사 700.5 PJ, LNG 149.8 PJ, 연료가스 190.2 PJ, 부산물가스 40.4 PJ, 나머지 <0.01 PJ |

### 2.3 제품군·공정·지역별 배출
**제품군별 (`outputs/module_01/emissions_by_product.csv`)**
| 제품군 | 배출량 (MtCO₂) | 비중 |
|--------|----------------|------|
| Olefins | 46.31 | 89.0% |
| Aromatics | 5.08 | 9.8% |
| Other | 0.48 | 0.9% |
| Polymers | 0.12 | 0.2% |
| Intermediates | 0.01 | ~0.0% |

**공정별**
| 공정 | 배출량 (MtCO₂) | 비중 |
|------|----------------|------|
| Naphtha Cracker | 46.66 | 89.7% |
| BTX Plant | 5.09 | 9.8% |
| Utility | 0.25 | 0.5% |

**상위 지역별 (`outputs/module_01/emissions_by_location.csv`)**
| 지역 | 배출량 (MtCO₂) |
|------|----------------|
| Yeosu | 21.05 |
| Daesan | 17.73 |
| Ulsan | 7.97 |
| Onsan | 5.13 |
| Incheon | 0.08 |

### 2.4 에너지 믹스 (제품군 기준, `outputs/module_01/product_group_energy_mix.csv`)
| 제품군 | 시설 수 | 배출량 (MtCO₂) | 납사 % | LNG % | 연료가스 % | 부산물가스 % | 전력 % |
|--------|---------|----------------|--------|-------|------------|--------------|--------|
| Olefins | 39 | 46.31 | 71.5 | 11.0 | 14.1 | 3.1 | 0.4 |
| Aromatics | 37 | 5.08 | 0.0 | 39.0 | 48.7 | 9.7 | 2.5 |
| Other | 108 | 0.48 | 98.6 | 0.0 | 0.0 | 0.0 | 1.4 |
| Polymers | 57 | 0.12 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 |
| Intermediates | 7 | 0.01 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 |

### 2.5 BAU 배출 경로 (`outputs/module_01/bau_trajectory_2025_2050.csv`)
| 연도 | 화석 연소 (MtCO₂) | 전력 (MtCO₂) | 총 배출 (MtCO₂) | 그리드 EF (tCO₂/MWh) |
|------|-------------------|--------------|------------------|----------------------|
| 2025 | 43.64 | 8.37 | 52.01 | 0.45 |
| 2030 | 47.00 | 8.22 | 55.21 | 0.41 |
| 2035 | 50.14 | 7.91 | 58.05 | 0.37 |
| 2040 | 52.67 | 7.41 | 60.08 | 0.33 |
| 2045 | 54.81 | 6.78 | 61.58 | 0.29 |
| 2050 | 56.20 | 5.99 | 62.19 | 0.25 |

---

## 3. 기술별 가정 상세

### 3.1 공통 제약
- **기술 비가역성**: `Deployment[tech, year] ≥ Deployment[tech, year-1]`.
- **상호 배타성**: 동일 시설에서 `NCC-H₂ + NCC-Electricity ≤ 1`.
- **재생 전력 전제**: 히트펌프·전기 크래커는 `re_price_trajectory.csv`, `grid_emission_trajectory.csv`의 RE 배출계수 0.05 tCO₂/MWh 적용.
- **원료(Feedstock) 불변**: 납사 크래커의 feedstock 소비는 계속 유지, 연소분만 대체.
- **CAPEX 연간화 방식**: 할인률 대신 `CAPEX / lifetime`으로 단순 연차 비용 산정 (Module 2).

### 3.2 기술 파라미터 (출처: `data/technology_parameters.csv`)
| 기술 | 적용 대상 | 최초 적용 연도 | CAPEX 2025 (M$/MtCO₂) | CAPEX 2030 | CAPEX 2040 | CAPEX 2050 | OPEX (% CAPEX) | 수명 (년) | TRL | 주요 에너지 가정 |
|------|-----------|----------------|------------------------|-------------|-------------|-------------|----------------|-----------|-----|-------------------|
| Heat Pump | BTX·Utility (<165°C) | 2025 | 900 | 720 | 540 | 450 | 3.0 | 20 | 9 | COP 4.0, 효율 0.95 |
| RE PPA | 모든 전력 부하 | 2025 | 0 | 0 | 0 | 0 | 0.0 | 99 | - | 전력 계약, 배출 0.05 tCO₂/MWh |
| NCC-Electricity | 납사 크래커 | 2030 | 1,840 | 1,560 | 1,150 | 940 | 3.5 | 25 | 6 | 전력 3.0 MWh/ton Ethylene |
| NCC-H₂ | 납사 크래커 | 2030 | 1,725 | 1,440 | 1,035 | 863 | 4.0 | 25 | 7 | H₂ 0.18 ton/ton Ethylene |

### 3.3 기술별 상세 가정 및 데이터 근거
**Heat Pump**
- 적용 가능 시설: BTX 47개 + Utility 일부 (`heat_pump_applicable = TRUE`).
- 에너지 전환: 화석열 1 GJ → 전기 0.25 GJ (COP 4.0, `model_parameters.csv`).
- 잔여 배출: 재생전력 생애주기 0.05 tCO₂/MWh.
- 학습효과: CAPEX 2050년 50% 감소.

**RE PPA**
- 적용 대상: 모든 시설 전력 사용 (`re_ppa_applicable = TRUE`).
- 배출 감소량: (그리드 EF – 0.05) × 전력 사용량.
- 비용: 전력요금 차액만 반영 (CAPEX/OPEX 없음).

**NCC-Electricity**
- 에너지: 3.0 MWh/ton Ethylene (`technology_parameters.csv`), 효율 0.95.
- 연료 절감: 납사 연소 29 GJ/ton 전량 제거 (`model_parameters.csv`).
- 2030년부터 도입 가능 (`available == True` in `macc_annual_2025_2050.csv`).
- 전력 증분: Aggressive 시나리오 2050년 +129.76 TWh (`aggressive_deployment.csv`).

**NCC-H₂**
- 그린수소 소비: 0.18 ton/ton Ethylene (모델 파라미터), `technology_energy_requirements.csv`의 보수적 0.20 ton/ton과 일치 추정.
- 효율 0.85 → 연소 연료 완전 대체.
- 2050년 H₂ 수요: Aggressive 12.99 kt, Policy Target 12.88 kt (`*_deployment.csv`).

---

## 4. 가격·배출계수·수요 궤적

### 4.1 연료·전력·수소 가격 (선택 연도)
| 연도 | 납사 ($/GJ) | 그리드 전력 ($/MWh) | RE PPA ($/MWh) | H₂ ($/kg) |
|------|-------------|----------------------|----------------|-----------|
| 2025 | 15.0 | 100 | 130 | 12.0 |
| 2030 | 15.0 | 100 | 115 | 10.0 |
| 2040 | 15.0 | 100 | 85 | 6.0 |
| 2050 | 15.0 | 100 | 55 | 2.0 |

자료: `data/fuel_price_trajectory.csv`, `data/re_price_trajectory.csv`, `data/grid_price_trajectory.csv`, `data/h2_price_trajectory.csv`.

### 4.2 전력 배출계수 (`data/grid_emission_trajectory.csv`)
| 연도 | tCO₂/MWh (그리드) | tCO₂/MWh (RE 생애주기) |
|------|--------------------|------------------------|
| 2025 | 0.45 | 0.05 |
| 2030 | 0.41 | 0.05 |
| 2040 | 0.33 | 0.05 |
| 2050 | 0.25 | 0.05 |

### 4.3 수요 증가 궤적 (`data/demand_growth_trajectory.csv`)
| 연도 | 연간 성장률 | 누적 용량 배수 | 비고 |
|------|-------------|----------------|------|
| 2025 | 0.0% | 1.000 | 기준연도 |
| 2030 | 1.5% | 1.077 | 2030 마일스톤 |
| 2040 | 1.0% | 1.207 | 수요 둔화 구간 |
| 2050 | 0.5% | 1.288 | 2050 최종 (28.8% 증가) |

### 4.4 탄소가격 및 재무 파라미터 (Module 4)
- 초기 탄소가격: $50/tCO₂ (2025), 연 5% 성장 (`financial.py`).
- 재무 할인율: 5%.
- CAPEX 가정: 기술별 차등이 아닌 평균 $150M/MtCO₂ (단순화).
- OPEX: CAPEX의 3%.

---

## 5. MACC 계산 (Module 2)

### 5.1 계산 방식 (`outputs/module_02/macc_annual_2025_2050.csv`)
```
MACC_total = (CAPEX / lifetime) + (OPEX %) + (Δ연료비)  [$/tCO₂]
Δ연료비 = (신규 에너지 비용 – 기존 연료 비용) / 감축량
```
- 감축량은 `baseline_combustion_emissions_tco2_per_ton` 대비 기술 적용 후 잔존 배출을 차감하여 산출.
- 전력 기술의 경우 `electricity_consumption_mwh_per_ton_ethylene × re_price`로 비용 계산.
- `available` 플래그가 False인 연도에는 감축 잠재량만 계산하고 최적화 대상에서 제외.

### 5.2 연도·기술별 비용 구성
| 연도 | 기술 | 감축 잠재량 (MtCO₂) | CAPEX ($/t) | OPEX ($/t) | 연료 차액 ($/t) | 총비용 ($/t) |
|------|------|---------------------|------------|------------|-----------------|--------------|
| 2025 | Heat Pump | 0.81 | 45.0 | 27.0 | 178.0 | 250.0 |
| 2025 | RE PPA | 7.21 | 0.0 | 0.0 | 325.0 | 325.0 |
| 2025 | NCC-Electricity | 19.01 | 73.6 | 64.4 | 245.4 | 383.4 |
| 2025 | NCC-H₂ | 20.80 | 69.0 | 69.0 | 1,242.1 | 1,380.1 |
| 2030 | Heat Pump | 0.87 | 36.0 | 21.6 | 157.4 | 215.0 |
| 2030 | RE PPA | 7.68 | 0.0 | 0.0 | 319.4 | 319.4 |
| 2030 | NCC-Electricity | 20.47 | 62.3 | 54.6 | 217.1 | 334.1 |
| 2030 | NCC-H₂ | 22.40 | 57.6 | 57.6 | 1,035.1 | 1,150.3 |
| 2040 | Heat Pump | 0.98 | 27.0 | 16.2 | 116.4 | 159.6 |
| 2040 | RE PPA | 8.31 | 0.0 | 0.0 | 303.6 | 303.6 |
| 2040 | NCC-Electricity | 22.94 | 49.2 | 40.3 | 160.5 | 246.7 |
| 2040 | NCC-H₂ | 25.11 | 51.8 | 41.4 | 621.0 | 703.8 |
| 2050 | Heat Pump | 1.04 | 23.1 | 13.5 | 75.3 | 111.3 |
| 2050 | RE PPA | 8.36 | 0.0 | 0.0 | 275.0 | 275.0 |
| 2050 | NCC-Electricity | 24.48 | 37.6 | 32.9 | 103.8 | 174.3 |
| 2050 | NCC-H₂ | 26.79 | 34.6 | 34.5 | 207.0 | 276.1 |

### 5.3 2050년 최대 감축 잠재량
- Heat Pump: **1.04 MtCO₂**
- NCC-Electricity: **24.48 MtCO₂**
- NCC-H₂: **26.79 MtCO₂**
- RE PPA: **8.36 MtCO₂**

---

## 6. 시나리오 최적화 결과 (Module 3)

### 6.1 목표 경로 비교 (`outputs/module_03/*_deployment.csv`)
| 연도 | BAU (MtCO₂) | Conservative | Moderate | Aggressive | Policy Target |
|------|-------------|--------------|----------|------------|---------------|
| 2025 | 52.01 | 52.0 | 52.0 | 52.0 | 52.0 |
| 2030 | 55.21 | 48.0 | 46.0 | 42.0 | 39.0 |
| 2035 | 58.05 | 44.0 | 40.0 | 32.0 | 26.0 |
| 2040 | 60.08 | 38.0 | 32.0 | 22.0 | 19.07 |
| 2045 | 61.58 | 30.0 | 22.0 | 12.0 | 12.13 |
| 2050 | 62.19 | 20.0 | 10.0 | 5.0 | 5.2 |

**누적 감축량(2025-2050)**  
Conservative 501.0 Mt, Moderate 631.0 Mt, Aggressive 803.9 Mt, Policy Target 858.5 Mt (BAU 대비 면적).

### 6.2 2030년 기술 기여도
| 시나리오 | Heat Pump (Mt) | NCC-H₂ (Mt) | NCC-Elec (Mt) | RE PPA (Mt) | 총 감축 (Mt) | 누적 CAPEX (M$) |
|----------|----------------|-------------|---------------|-------------|--------------|-----------------|
| Conservative | 0.871 | 0.000 | 0.000 | 6.340 | 7.211 | 748.7 |
| Moderate | 0.871 | 0.000 | 0.664 | 7.676 | 9.211 | 1,577.7 |
| Aggressive | 0.871 | 0.000 | 4.664 | 7.676 | 13.211 | 6,569.7 |
| Policy Target | 0.871 | 0.000 | 7.664 | 7.676 | 16.211 | 10,313.7 |

### 6.3 2050년 기술 배치·인프라 요구
| 시나리오 | 2050 배출 (Mt) | 총 감축 (Mt) | Heat Pump (Mt) | NCC-H₂ (Mt) | NCC-Elec (Mt) | RE PPA (Mt) | H₂ 수요 (kt) | 전력 증분 (TWh) | 누적 CAPEX (M$) |
|----------|----------------|--------------|----------------|-------------|---------------|-------------|--------------|-----------------|-----------------|
| Conservative | 20.0 | 42.19 | 1.042 | 8.243 | 24.482 | 8.427 | 4.61 | 129.76 | 30,259.2 |
| Moderate | 10.0 | 52.19 | 1.042 | 18.233 | 24.482 | 8.437 | 10.20 | 129.76 | 39,450.1 |
| Aggressive | 5.0 | 57.19 | 1.042 | 23.233 | 24.482 | 8.437 | 12.99 | 129.76 | 46,467.7 |
| Policy Target | 5.2 | 56.99 | 1.042 | 23.033 | 24.482 | 8.437 | 12.88 | 129.76 | 47,865.6 |

> 전력 증분은 모든 시나리오에서 동일하게 129.76 TWh 증가 (NCC-Electricity 도입량 동일)하나, 수소 수요는 시나리오별 NCC-H₂ 비중에 따라 상이합니다.

### 6.4 제약 조건 확인
- 기술 도입량은 연도별로 비감소.
- `facility_technology_applicability.csv` 기반으로 지역·공정별 최대 도입률 상한 적용.
- Policy Target 시나리오는 `data/emission_scenarios_clean.csv`의 2035 26 Mt, 2050 5.2 Mt 목표를 그대로 반영.

---

## 7. 지역별 배치 (Aggressive 시나리오, 2050)

`outputs/module_03/Aggressive_regional_deployment.csv` 기준 4대 클러스터는 모두 순 배출이 음수로 전환됩니다.

| 지역 | 시설 수 | 기준 배출 (Mt) | 총 감축 (Mt) | 2050 배출 (Mt) | Heat Pump 적용률 | NCC-H₂ 적용률 | NCC-Elec 적용률 | RE PPA 적용률 |
|------|---------|----------------|--------------|----------------|------------------|----------------|------------------|----------------|
| Daesan | 57 | 17.73 | 19.75 | -2.02 | 0.63% | 14.09% | 14.85% | 40.12% |
| Yeosu | 87 | 21.05 | 23.67 | -2.62 | 0.41% | 9.23% | 9.73% | 29.87% |
| Onsan | 14 | 5.13 | 5.64 | -0.50 | 0.78% | 17.65% | 18.60% | 74.25% |
| Ulsan | 71 | 7.97 | 8.09 | -0.13 | 0.43% | 7.83% | 8.25% | 21.96% |

- 음수 배출은 RE PPA 및 NCC 기술 도입으로 Scope 1·2 배출이 0 이하로 전환되며, 여분의 RE 계약으로 상쇄 효과가 발생함을 의미합니다.
- 소수 지역(인천·광양 등)은 잔존 배출이 소량 존재하나, 전체 배출 기여도는 0.1 MtCO₂ 미만입니다.

---

## 8. 재무 분석 (Module 4)

### 8.1 분석 대상 및 가정
- 기본 입력: `outputs/module_03/conservative_deployment.csv` (모듈 내 하드코딩된 로딩 순서).
- 탄소가격: 2025년 $50/tCO₂, 연 5% 상승.
- CAPEX: 감축량 × $150M/MtCO₂ (기술 구분 없음).
- OPEX: CAPEX의 3%.
- 할인율: 5%.

### 8.2 결과 (`outputs/module_04/*`)
| 항목 | 값 |
|------|----|
| 총 탄소 편익 | 60,744 M$ |
| 총 CAPEX 지출 | 75,148 M$ |
| 총 OPEX 지출 | 2,254 M$ |
| 총 순현금흐름 (할인 전) | -16,658 M$ |
| NPV (할인 반영) | -9,666 M$ |
| IRR | 계산 실패 (음수 현금흐름 지속) |

- 보수적 시나리오 기준으로도 탄소 편익이 CAPEX를 상쇄하지 못해 NPV가 음수이며, IRR은 수렴하지 않아 `NaN`으로 기록됩니다 (`financial_summary.csv`).
- 보다 현실적인 재무분석을 위해서는 기술별 CAPEX·OPEX, 수소·전력 실거래가, 보조금 효과 등을 세분화해야 함.

---

## 9. 데이터 추적 및 검증 포인트
- Baseline 검증: `outputs/module_01/baseline_2025_detailed.csv` 합계가 52.001 MtCO₂와 일치해야 함.
- 기술별 MACC 검증: `outputs/module_02/macc_annual_2025_2050.csv`에서 `available == True` 연도만 Module 3에서 선택되는지 확인.
- 시나리오 검증: `outputs/module_03/scenario_summary_for_latex.csv`와 최적화 그래프(`deployment_*.png`) 비교.
- 지역 분석: `*_regional_deployment.csv`의 `num_facilities` 합이 248인지 확인.
- 재무모듈 검증: `modules/financial.py`는 평균 CAPEX를 사용하므로, 기술별 투자비 반영을 위해서는 수정이 필요.

---

## 10. 참고 문헌
- Woo, J. et al. (2025). *Techno-economic analysis of low-carbon ethylene production via electrified steam cracking*. RSC Green Chemistry.
- IEA (2023). *Industrial Heat Pumps Technologies & Applications*.
- IEA (2021). *Net Zero by 2050*.
- KEEI (2023). *2050 탄소중립 시나리오 산업부문 분석*.
- 제10차 전력수급기본계획 (2023).
- IRENA (2023). *Renewable Power Generation Costs*.

---

**문의**: 프로젝트 연구팀 (README 참조)  
**Last Updated**: 2025-10-23
