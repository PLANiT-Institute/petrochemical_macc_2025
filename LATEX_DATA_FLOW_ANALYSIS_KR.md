# LaTeX 논문 데이터 흐름 및 논리 상세 분석

**분석일:** 2025-10-19
**대상 파일:** `latex_paper/main.tex`

---

## 🔍 발견된 문제점

### 1. **하드코딩된 값과 실제 모델 결과 불일치**

| 항목 | LaTeX 값 | 실제 모델 값 | 차이 | 상태 |
|------|----------|-------------|------|------|
| **NCC-Electricity (2030)** | $368/tCO₂ | $334/tCO₂ | -$34 | ⚠️ 불일치 |
| **Heat Pump (2030)** | $774/tCO₂ | $215/tCO₂ | -$559 | ⚠️ **큰 불일치** |
| **NCC-H₂ (2030)** | $1,184/tCO₂ | $1,150/tCO₂ | -$34 | ⚠️ 불일치 |
| **RE PPA (2030)** | $319/tCO₂ | $319/tCO₂ | $0 | ✅ 일치 |

### 2. **Heat Pump 값 차이 원인 분석**

**LaTeX 계산 (잘못됨):**
```latex
% main.tex line 286-295
Heat Pump & 0.71 & 73 & 2 & 699 & \textbf{774} & 3 \\
```

**실제 모델 결과:**
- Abatement: 0.87 MtCO₂ (LaTeX: 0.71)
- Total MACC: $215/tCO₂ (LaTeX: $774)

**문제:**
1. Heat Pump가 **이전 모델 결과**를 사용 중
2. LaTeX에서 `macc_curve_2030_final.png` 참조하지만, 값은 **이전 run 결과**

---

## 📊 데이터가 어떻게 흐르는가

### 전체 데이터 흐름

```
┌────────────────────────────────────────────────────────────────┐
│ Step 1: 가정값 입력 (Excel/CSV)                                 │
│ ─────────────────────────────────────────────────────────────  │
│ data/MACC_Model_Assumptions_v2_Korean.xlsx                     │
│   ├─ Model_Parameters                                          │
│   │   → naphtha_fuel: 29.00 GJ/ton                            │
│   │   → naphtha_EF: 0.0542 tCO₂/GJ                            │
│   │                                                            │
│   ├─ Technology_Parameters                                     │
│   │   → Heat_Pump CAPEX: 900 M$/MtCO₂                         │
│   │   → NCC-H2 CAPEX: 1,725 M$/MtCO₂                          │
│   │   → NCC-E CAPEX: 1,840 M$/MtCO₂                           │
│   │                                                            │
│   └─ Price Trajectories                                        │
│       → H2: $12/kg → $2/kg                                     │
│       → RE: $130/MWh → $55/MWh                                 │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 2: CSV 변환                                                │
│ ─────────────────────────────────────────────────────────────  │
│ Python 스크립트로 Excel → CSV 변환                             │
│                                                                 │
│ data/                                                           │
│   ├─ model_parameters.csv                                      │
│   ├─ technology_parameters.csv                                 │
│   ├─ h2_price_trajectory.csv                                   │
│   ├─ re_price_trajectory.csv                                   │
│   └─ emission_factors.csv                                      │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 3: Module 1 - Baseline 계산                                │
│ ─────────────────────────────────────────────────────────────  │
│ python run_module_01.py                                        │
│                                                                 │
│ 입력:                                                           │
│   - facility_database.csv (248 시설)                           │
│   - energy_intensities.csv (GJ/ton, MWh/ton)                  │
│   - emission_factors.csv (tCO₂/GJ)                             │
│                                                                 │
│ 계산:                                                           │
│   for each facility:                                           │
│     emissions_naphtha = capacity × 29 GJ/ton × 0.0542 tCO₂/GJ │
│     emissions_lng = capacity × 4.49 GJ/ton × 0.0149 tCO₂/GJ   │
│     ... (다른 연료들)                                           │
│     total_emissions = sum(모든 연료)                           │
│                                                                 │
│ 출력:                                                           │
│   outputs/module_01/baseline_2025_detailed.csv                 │
│     → 248 rows × 30 columns                                    │
│     → total: 51,398.77 ktCO₂ = 51.4 MtCO₂                     │
│                                                                 │
│   outputs/module_01/baseline_2025_by_product.png               │
│     → LaTeX Figure 1에서 사용                                  │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 4: Module 2 - MACC 계산                                    │
│ ─────────────────────────────────────────────────────────────  │
│ python run_module_02.py                                        │
│                                                                 │
│ 입력:                                                           │
│   - baseline_2025_detailed.csv (248 시설)                      │
│   - technology_parameters.csv (CAPEX, OPEX, 효율)              │
│   - h2_price_trajectory.csv (2025-2050)                        │
│   - re_price_trajectory.csv (2025-2050)                        │
│                                                                 │
│ 계산 로직:                                                      │
│   for year in 2025:2050:                                       │
│     for tech in [Heat_Pump, NCC-H2, NCC-E, RE_PPA]:           │
│                                                                 │
│       # 1. 감축량 계산                                          │
│       if tech == "Heat_Pump":                                  │
│         # BTX 47개 시설만                                       │
│         fossil_fuel_GJ = sum(BTX facilities fuel)             │
│         elec_MWh = fossil_fuel_GJ / (3.6 × 4.0)  # COP=4     │
│         emissions_after = elec_MWh × 0.05  # RE 전제          │
│         abatement = baseline - emissions_after                │
│                                                                 │
│       elif tech == "NCC-H2":                                   │
│         # NCC 41개 시설만                                       │
│         baseline_tco2_per_ton = 29 × 0.0542 = 1.739 tCO₂/ton │
│         h2_emissions = 0.0  # 그린수소                         │
│         abatement_per_ton = 1.739 - 0 = 1.739 tCO₂/ton       │
│         total_abatement = capacity × abatement_per_ton        │
│                                                                 │
│       elif tech == "NCC-Electricity":                          │
│         baseline = 1.739 tCO₂/ton                             │
│         elec_emissions = 3.0 MWh/ton × 0.05 = 0.15 tCO₂/ton  │
│         abatement_per_ton = 1.739 - 0.15 = 1.59 tCO₂/ton     │
│                                                                 │
│       # 2. 비용 계산                                            │
│       CAPEX_ann = CAPEX_total / lifetime  # 단순 나눗셈        │
│       OPEX = CAPEX_total × OPEX_pct                           │
│                                                                 │
│       if tech == "Heat_Pump":                                  │
│         fuel_cost = elec_MWh × RE_price                       │
│       elif tech == "NCC-H2":                                   │
│         fuel_cost = 0.18 ton/ton × 1000 × H2_price           │
│       elif tech == "NCC-E":                                    │
│         fuel_cost = 3.0 MWh/ton × RE_price                    │
│                                                                 │
│       # 3. MACC                                                │
│       MACC = (CAPEX_ann + OPEX + fuel_cost) / abatement       │
│                                                                 │
│ 출력:                                                           │
│   outputs/module_02/macc_annual_2025_2050.csv                  │
│     → 104 rows (4 tech × 26 years)                            │
│     → columns: year, technology, abatement_mtco2,             │
│                capex_ann, opex, fuel_cost, total_cost         │
│                                                                 │
│   outputs/module_02/macc_curve_2030.png                        │
│   outputs/module_02/cost_evolution_annual.png                  │
│     → LaTeX Figure 2, 3에서 사용                               │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ Step 5: LaTeX 논문 작성                                         │
│ ─────────────────────────────────────────────────────────────  │
│ latex_paper/main.tex                                           │
│                                                                 │
│ 현재 문제:                                                      │
│   ✗ Table \ref{tab:macc_2030} - 하드코딩된 값 (불일치!)       │
│   ✗ Table \ref{tab:tech_params} - 하드코딩된 값               │
│   ✓ Figures - PNG 자동 로드 (OK)                              │
│   ✗ csvsimple tables - CSV 파일 부재                          │
│                                                                 │
│ 필요한 수정:                                                    │
│   1. 하드코딩된 Table 값을 실제 CSV로 교체                    │
│   2. csvsimple로 자동 로드 구현                                │
│   3. 모든 숫자를 최신 모델 결과와 동기화                       │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔧 구체적인 계산 로직 (2030년 예시)

### Heat Pump (실제 모델 vs LaTeX)

#### **실제 모델 계산:**

```python
# modules/macc.py line 147-220

# 1. 대상: BTX 47개 시설
df_btx = baseline[baseline['process'] == 'BTX Plant']
# NCC 제외 (line 149-152)

# 2. 화석연료 연소량
total_fossil_fuel_GJ = sum(BTX facilities naphtha + LNG + fuel_gas)

# 3. 필요한 전력 (COP = 4.0)
elec_MWh = total_fossil_fuel_GJ / (3.6 × 4.0)

# 4. 배출량 (재생에너지 전제)
emissions_after = elec_MWh × 0.05 tCO₂/MWh  # line 177-179

# 5. 감축량
abatement_MtCO2 = (baseline_emissions - emissions_after) / 1e6

# 6. 비용 (2030년)
CAPEX_2030 = 720 M$/MtCO₂  # 2025년 900에서 20% 감소
lifetime = 20
CAPEX_ann = 720 / 20 = 36 M$/MtCO₂  # line 187

OPEX = 720 × 0.03 = 21.6 M$/MtCO₂  # line 188

RE_price_2030 = 118.8 $/MWh
fuel_cost = (elec_MWh × RE_price_2030) / (abatement_MtCO2 × 1e6)

# 7. MACC
MACC = CAPEX_ann + OPEX + fuel_cost

# 실제 결과: $215/tCO₂
```

#### **LaTeX에 쓰인 값 (출처 불명):**

```latex
% line 286
Heat Pump & 0.71 & 73 & 2 & 699 & \textbf{774} & 3 \\
```

이 값들은 **이전 모델 run 또는 추정값**으로 보입니다.

---

### NCC-Electricity (실제 vs LaTeX)

#### **실제 모델 계산 (2030년):**

```python
# modules/macc.py line 320-380

# 1. 대상: NCC 41개 시설
total_ethylene_kt = 11,962 kt/year

# 2. Baseline 배출
baseline_per_ton = 29.0 GJ/ton × 0.0542 tCO₂/GJ = 1.739 tCO₂/ton

# 3. NCC-E 배출 (재생에너지 전제!)
elec_emissions = 3.0 MWh/ton × 0.05 tCO₂/MWh = 0.15 tCO₂/ton

# 4. 감축량
abatement_per_ton = 1.739 - 0.15 = 1.59 tCO₂/ton
total_abatement = 11,962 × 1.59 / 1000 = 19.0 MtCO₂

# 성장 반영 (2030년 capacity multiplier)
total_abatement_2030 = 19.0 × 1.077 = 20.47 MtCO₂  ✓ (LaTeX 일치)

# 5. 비용
CAPEX_2030 = 1,560 M$/MtCO₂
CAPEX_ann = 1,560 / 25 = 62.4 $/tCO₂

OPEX = 1,560 × 0.035 = 54.6 $/tCO₂

RE_price_2030 = 118.8 $/MWh
fuel_cost = (3.0 MWh/ton × 118.8) / 1.59 = 224 $/tCO₂

# MACC (per facility, normalized)
MACC_raw = 62.4 + 54.6 + 224 = 341 $/tCO₂

# 실제 모델 결과: $334/tCO₂ (시설별 capacity factor 반영)
```

#### **LaTeX 값:**

```latex
NCC-Electricity & 20.47 & 146 & 5 & 217 & \textbf{368} & 2 \\
```

- **Abatement**: 20.47 MtCO₂ ✓ (일치)
- **Total**: $368/tCO₂ vs 실제 $334/tCO₂ (10% 차이)

**차이 원인:**
- CAPEX_ann이 146 (LaTeX) vs 62.4 (실제)
- LaTeX가 **이전 할인율 방식** 계산 사용 중:
  ```
  CRF = 0.08 / (1 - 1.08^-25) ≈ 0.0937
  CAPEX_ann = 1,560 × 0.0937 = 146 $/tCO₂
  ```

---

## 🎯 올바른 데이터 흐름 (수정 후)

### 방법 1: CSV 자동 로드 (권장)

```latex
% main.tex에 추가
\begin{table}[htbp]
    \centering
    \caption{MACC results for 2030 (from model outputs)}
    \label{tab:macc_2030_auto}
    \begin{tabular}{lcccccc}
        \toprule
        \textbf{Technology} & \textbf{Abatement} & \textbf{CAPEX} & ... \\
        & \textbf{(MtCO\textsubscript{2})} & & & & & \\
        \midrule
        \csvreader[
            head to column names,
            filter strcmp={\year}{2030},
            late after line=\\
        ]{../../outputs/module_02/macc_annual_2025_2050.csv}{}%
        {\technology &
         \num{\abatement_potential_mtco2} &
         \num{\capex_ann_usd_per_tco2} &
         \num{\opex_ann_usd_per_tco2} &
         \num{\fuel_cost_diff_usd_per_tco2} &
         \num{\total_cost_usd_per_tco2}}
        \bottomrule
    \end{tabular}
\end{table}
```

### 방법 2: Python 스크립트로 LaTeX snippet 생성

```python
# scripts/generate_latex_tables.py

import pandas as pd

df = pd.read_csv('outputs/module_02/macc_annual_2025_2050.csv')
df_2030 = df[df['year'] == 2030].sort_values('total_cost_usd_per_tco2')

latex_rows = []
for _, row in df_2030.iterrows():
    tech = row['technology'].replace('_', '-')
    abate = f"{row['abatement_potential_mtco2']:.2f}"
    capex = f"{row['capex_ann_usd_per_tco2']:.0f}"
    opex = f"{row['opex_ann_usd_per_tco2']:.0f}"
    fuel = f"{row['fuel_cost_diff_usd_per_tco2']:.0f}"
    total = f"{row['total_cost_usd_per_tco2']:.0f}"

    latex_rows.append(f"{tech} & {abate} & {capex} & {opex} & {fuel} & \\textbf{{{total}}} \\\\")

print("\\n".join(latex_rows))
```

**출력:**
```latex
RE-PPA & 7.68 & 0 & 0 & 319 & \textbf{319} \\
NCC-Electricity & 20.47 & 62 & 55 & 217 & \textbf{334} \\
Heat-Pump & 0.87 & 36 & 22 & 157 & \textbf{215} \\
NCC-H2 & 22.40 & 58 & 58 & 1035 & \textbf{1150} \\
```

---

## 📋 수정 필요 항목 체크리스트

### LaTeX Table 수정

- [ ] **Table \ref{tab:macc_2030}** (line 269-285)
  - [ ] NCC-Electricity: 368 → 334
  - [ ] Heat Pump: 774 → 215 (큰 변경!)
  - [ ] NCC-H2: 1184 → 1150
  - [ ] Heat Pump abatement: 0.71 → 0.87
  - [ ] CAPEX/OPEX 값들 전면 수정

- [ ] **Text references** (line 287-299)
  - [ ] Heat Pump 설명 업데이트 ($774 → $215)
  - [ ] "High fuel cost dominates" → "Moderate cost profile"

- [ ] **Discussion 섹션** (line 378-415)
  - [ ] 2050년 비용 검증
  - [ ] Heat Pump 역할 재평가 (limited role인지?)

### CSV 파일 생성

- [ ] `outputs/module_02/macc_cost_snapshot.csv` 검증
- [ ] `outputs/module_01/product_group_energy_mix.csv` 검증

---

## 🔬 근본 원인 분석

### 왜 LaTeX와 모델이 불일치했는가?

1. **수동 입력 오류**: LaTeX에 수동으로 값 입력 → 모델 업데이트 시 LaTeX 미갱신
2. **다른 run 결과 사용**: LaTeX는 이전 모델 run 결과 사용 중
3. **할인율 방식 차이**: LaTeX CAPEX 값이 CRF 방식 계산 (이전 모델)

### 해결 방법

1. **자동화**: CSV → LaTeX table 자동 생성
2. **검증 스크립트**: LaTeX compile 전 값 일치 여부 체크
3. **문서화**: 모든 숫자의 출처 명시

---

## 💡 권장 사항

### 단기 (즉시)
1. LaTeX Table 값을 최신 모델 결과로 수동 업데이트
2. 주요 숫자 검증 스크립트 실행

### 중기 (1주일 이내)
1. Python 스크립트로 LaTeX snippet 자동 생성
2. csvsimple로 Figure 외 Table도 자동 로드

### 장기 (논문 제출 전)
1. 모든 Table을 CSV 기반 자동 생성으로 전환
2. CI/CD: 모델 run → LaTeX compile → 값 검증 파이프라인

---

**작성자:** Petrochemical MACC Team
**분석일:** 2025-10-19
**상태:** 수정 필요 (LaTeX 하드코딩 값과 모델 불일치)
