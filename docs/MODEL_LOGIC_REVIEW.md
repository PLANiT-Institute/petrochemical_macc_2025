# 모델 논리 철저 검토 (Model Logic Deep Review)
**Date**: 2025-10-29
**Purpose**: 학술 논문 준비를 위한 모델 가정 및 논리 검증

---

## 1. 납사(Naphtha)의 역할 명확화

### 현재 모델 데이터

**에틸렌 1톤 생산 시 에너지 소비**:
```
Naphtha:         29.0 GJ/ton
LNG:              4.49 GJ/ton (연소용)
Fuel Gas:         5.62 GJ/ton (연소용)
Byproduct Gas:    1.12 GJ/ton (연소용)
Electricity:     21.8 kWh/ton = 0.078 GJ/ton

Total:           ~40.3 GJ/ton
```

### 문헌 조사 결과

#### 총 에너지 소비
| Source | Value | Note |
|--------|-------|------|
| Web Search (multiple) | 26-40 GJ/ton | Range for total SEC |
| Web Search | 18-21 GJ/ton | Best practice cases |
| Our Model | 40.3 GJ/ton | ✅ Within literature range (upper end) |

#### 연소용 연료 (Fuel for Combustion)
| Source | Value | Note |
|--------|-------|------|
| Literature | ~25 GJ/ton | Fuel use for heating |
| Our Model | 11.2 GJ/ton | LNG + Fuel Gas + Byproduct |
| **Gap** | **-13.8 GJ/ton** | ⚠️ **SIGNIFICANT DISCREPANCY** |

#### CO2 배출 출처
- **문헌**: 70-90% of CO2 comes from **fuel combustion** (not feedstock)
- **문헌**: 1.0-1.6 tCO2/ton ethylene produced
- **우리 모델**:
  - Total: 2.26 tCO2/ton (Lotte Daesan example)
  - From naphtha: 1.73 tCO2/ton (77%)
  - From combustion fuels: 0.53 tCO2/ton (23%)

### ⚠️ CRITICAL ISSUE: Naphtha Role

**Question**: 납사 29 GJ/ton이 모두 **feedstock**인가, 아니면 일부는 **fuel**인가?

**Hypothesis 1 (Current Model Assumption)**:
- Naphtha 29 GJ/ton = **ALL feedstock** (chemically converted to ethylene)
- Combustion fuels (LNG, Fuel Gas, Byproduct) = 11.2 GJ/ton
- **Problem**: Total combustion (11 GJ/ton) << Literature (25 GJ/ton)

**Hypothesis 2 (Literature-Based)**:
- Naphtha feedstock (stoichiometric) ≈ 6.7 GJ/ton (only for cracking reaction)
- Naphtha fuel ≈ 22.3 GJ/ton (for heating furnace)
- Additional fuels (LNG, etc.) ≈ 11 GJ/ton
- **Total combustion**: 22.3 + 11 = 33.3 GJ/ton (closer to literature 25 GJ/ton)

**Hypothesis 3 (Mixed)**:
- Some naphtha is feedstock, some is fuel
- Need to separate:
  - `naphtha_feedstock_gj_per_ton` (chemical conversion)
  - `naphtha_fuel_gj_per_ton` (combustion for heat)

### 문헌 출처 필요

**URGENT**: 다음 데이터의 명확한 문헌 출처 필요:
1. Naphtha feedstock requirement (stoichiometric) for ethylene
2. Naphtha fuel requirement (combustion) for heating
3. Total fuel combustion energy per ton ethylene
4. Emission split: feedstock vs fuel

---

## 2. 그리드 배출계수 (Grid Emission Factor)

### 문헌 조사 결과

#### 현재 상태 (2024-2025)
- **출처**: Climate Transparency (2021 data)
- **값**: 411.3 gCO2/kWh = 0.411 tCO2/MWh
- **우리 모델 (2025)**: 0.45 tCO2/MWh ✅ Reasonable

#### 2030 목표
- **출처**: MDPI Energy (2022) - "Scenario Analysis of GHG Emissions through 2030"
- **값**: 0.253-0.330 kgCO2/kWh (다양한 시나리오)
- **출처**: 10th Basic Electricity Plan (2023)
  - Coal: 19.7% → 21.2%
  - Renewables: 21.6%
  - Nuclear: 32.4%
- **우리 모델 (2030)**: 0.375 tCO2/MWh
- **Assessment**: ✅ Within scenario range but on higher end

#### 2050 목표
- **출처**: Korea 2050 Carbon Neutral Strategy
- **공식 목표**: Net-zero emissions by 2050
- **전력 부문**: Hydrogen/ammonia turbines (13.8-21.5% of generation)
- **우리 모델 (2050)**: 0.0 tCO2/MWh ✅ **Aligned with net-zero goal**

### 그리드 배출계수 궤적 (수정됨)

```csv
year,grid_ef_tco2_per_mwh,source
2025,0.45,"Climate Transparency 2021 data"
2030,0.375,"MDPI Energy 2022, mid-range scenario"
2035,0.30,"Linear interpolation to 2050 net-zero"
2040,0.15,"Linear interpolation"
2045,0.02,"Approaching net-zero"
2050,0.00,"Korea 2050 Carbon Neutral Strategy"
```

### 문헌 출처

1. **Climate Transparency (2022)**: "South Korea Country Profile"
   - https://www.climate-transparency.org/wp-content/uploads/2022/10/CT2022-South-Korea-Web.pdf

2. **MDPI Energies (2022)**: "Scenario Analysis of the GHG Emissions in the Electricity Sector through 2030 in South Korea Considering Updated NDC"
   - https://www.mdpi.com/1996-1073/15/9/3310
   - DOI: 10.3390/en15093310

3. **Korea 2050 Carbon Neutral Strategy (2020)**:
   - https://unfccc.int/sites/default/files/resource/LTS1_RKorea.pdf

---

## 3. NCC 기술 에너지 소비

### NCC-Electricity (Electric Cracking)

#### 문헌 조사 결과

| Source | Value | Year | Note |
|--------|-------|------|------|
| Literature 1 | 2.86 MWh/ton | 2023 | Electric cracker power consumption |
| Literature 2 | 2.14 MWh/ton | 2022 | Electrified cracking energy demand (7.7 GJ/t) |
| Literature 3 | 350-400 MW | - | For 1 Mt/year plant (= 3.06-3.50 MWh/ton) |
| **Our Model** | **3.0 MWh/ton** | - | ✅ **Within literature range** |

#### 문헌 출처

1. **ACS Sustainable Chemistry & Engineering (2022)**: "Review of Electric Cracking of Hydrocarbons"
   - DOI: 10.1021/acssuschemeng.2c03427
   - Cited: 2.86 kWh/kg-ethylene

2. **ScienceDirect (2022)**: "Electrified steam cracking for carbon neutral ethylene"
   - DOI: 10.1016/j.apenergy.2022.119862
   - Cited: 7.7 GJ/t C2H4 = 2.14 MWh/ton

3. **Industrial & Engineering Chemistry Research (2023)**: "Optimization of Electric Ethylene Production"
   - DOI: 10.1021/acs.iecr.3c02226
   - Cited: 350-400 MW for 1 Mt/year

### NCC-H2 (Hydrogen Cracking)

#### 현재 모델 가정
```python
H2 consumption: 0.18 ton H2 per ton ethylene
Energy content: 0.18 ton × 120 GJ/ton H2 = 21.6 GJ/ton ethylene
```

#### 문헌 필요
- ⚠️ **NO CLEAR LITERATURE FOUND YET**
- **URGENT**: Need peer-reviewed source for hydrogen consumption in naphtha cracking
- Alternative: Estimate from stoichiometry + process heat

#### 논리 검증
1. **Stoichiometric requirement** (화학 반응):
   - C10H22 (naphtha) + H2 → C2H4 (ethylene)
   - Need to calculate exact H2 requirement

2. **Process heat requirement** (열 공급):
   - Replace LNG/Fuel Gas combustion (~11 GJ/ton) with H2 combustion
   - H2 lower heating value: 120 GJ/ton
   - H2 needed for heat: 11 / 120 = 0.092 ton H2/ton ethylene

3. **Total H2 estimate**:
   - Chemical: ~? ton H2/ton ethylene (need calculation)
   - Thermal: ~0.092 ton H2/ton ethylene
   - **Total**: Need verification

---

## 4. CAPEX 및 비용 가정

### 현재 모델 데이터

#### NCC-H2
```
CAPEX: $1,560 per ton abatement capacity (2030)
Lifetime: 25 years
OPEX: 3.5% of CAPEX annually
```

#### NCC-Electricity
```
CAPEX: $1,820 per ton abatement capacity (2030)
Lifetime: 25 years
OPEX: 3.5% of CAPEX annually
```

### 문헌 필요
- ⚠️ **NO CLEAR CAPEX DATA FOUND IN OPEN LITERATURE**
- **Alternative sources**:
  - Industry reports (IHS Markit, Wood Mackenzie)
  - Technology providers (Technip, BASF, Linde)
  - Academic techno-economic analyses

### 비용 계산 논리

**MACC Formula**:
```
Total Cost ($/tCO2) = CAPEX_annual + OPEX_annual + Fuel_cost_differential

Where:
- CAPEX_annual = CAPEX_total / Lifetime (simple annualization, no discounting)
- OPEX_annual = CAPEX_total × OPEX_rate
- Fuel_cost_differential = (New_fuel_cost - Baseline_fuel_cost) / Abatement
```

**Example (NCC-H2, 2030)**:
```
CAPEX_annual = $1,560 / 25 = $62.4/tCO2
OPEX_annual = $1,560 × 0.035 = $54.6/tCO2
H2_cost = 0.18 ton H2 × $3.5/kg / abatement = ~$115/tCO2
Fuel_saved = LNG + Fuel Gas cost savings (NOT included in current model)

Total = $62.4 + $54.6 + $115 - Fuel_saved = $232/tCO2 (before fuel savings)
```

---

## 5. 모델 논리 흐름

### Module 1: Baseline
```
1. Load 248 facilities with capacity data
2. Apply energy intensities (GJ/ton, kWh/ton)
3. Calculate emissions using emission factors
4. Project BAU trajectory (2025-2050) with demand growth

Result: Baseline emissions = 66.2 MtCO2 (2025)
```

### Module 2: MACC
```
1. For each technology and year:
   a. Calculate energy consumption (new vs baseline)
   b. Calculate emissions abatement
   c. Calculate costs: CAPEX_ann + OPEX_ann + Fuel_diff
   d. Compute $/tCO2

Result: Technology costs by year
- Heat Pump: $160/tCO2 (2030)
- NCC-H2: $115/tCO2 (2030)  ← CHEAPEST
- NCC-Electricity: $117/tCO2 (2030)
- RE PPA: $231/tCO2 (2030)
```

### Module 3: Optimization
```
1. Load emission scenario targets (2025-2050)
2. For each year:
   a. Calculate required abatement
   b. Deploy technologies in cost order (greedy algorithm)
   c. Constraint: NCC technologies mutually exclusive
   d. Constraint: Technology irreversibility (no capacity reduction)

3. NCC technology choice:
   - FIRST TIME (2030): Choose cheaper option (H2 vs Electricity)
   - ALL FUTURE YEARS: Locked into initial choice

Result: Technology deployment trajectory
- 2050: NCC-H2 (90%), Heat Pump (4%), RE PPA (6%)
- Total investment: $63.5 billion
```

---

## 6. 주요 가정 및 제약사항

### Simplifying Assumptions

1. **Energy Intensities**:
   - ✅ All ethylene NCCs use same energy intensity (29 GJ naphtha/ton)
   - ⚠️ No distinction between old/new plants
   - ⚠️ No efficiency improvement over time

2. **NCC Technology Choice**:
   - ⚠️ **Industry-wide**: All NCCs adopt same technology (H2 OR Electricity)
   - Alternative: Facility-level choice (more realistic, more complex)
   - Justification: Simplification for academic model clarity

3. **Cost Calculation**:
   - ✅ Simple annualization (CAPEX / lifetime)
   - ⚠️ No discount rate (NPV)
   - ⚠️ No fuel cost savings included in MACC
   - Standard MACC: Should include (New_fuel - Baseline_fuel)

4. **Facility Lifetime**:
   - ✅ Infinite lifetime (no retirement)
   - Justification: Conservative BAU scenario

5. **Technology Irreversibility**:
   - ✅ Once deployed, capacity cannot decrease
   - Justification: Capital lock-in

---

## 7. 논리 검증 체크리스트

### Data Quality
- [ ] ⚠️ **Naphtha role**: Clarify feedstock vs fuel split
- [x] ✅ **Grid trajectory**: Aligned with Korea 2050 net-zero
- [x] ✅ **NCC-Electricity**: 3.0 MWh/ton (within literature 2.14-3.5)
- [ ] ⚠️ **NCC-H2**: 0.18 ton H2/ton ethylene (need literature source)
- [ ] ⚠️ **CAPEX**: Need literature sources or industry data

### Model Logic
- [x] ✅ **Baseline calculation**: Correct emission factor application
- [x] ✅ **MACC calculation**: Energy-based, transparent
- [ ] ⚠️ **Fuel cost savings**: Should be included in standard MACC
- [ ] ⚠️ **NCC choice**: Industry-wide vs facility-level (discuss trade-offs)
- [x] ✅ **Optimization**: Greedy cost-ordered deployment

### Academic Rigor
- [ ] **Literature review**: Complete for all key parameters
- [ ] **Uncertainty analysis**: Not yet performed
- [ ] **Sensitivity analysis**: Not yet performed
- [ ] **Model validation**: Compare with other Korea studies

---

## 8. 다음 단계 (Next Steps)

### Urgent (Before Paper Submission)
1. **Naphtha clarification**:
   - Find literature on naphtha feedstock vs fuel split
   - Revise energy balance if needed

2. **Literature sources**:
   - NCC-H2 hydrogen consumption: Find peer-reviewed source
   - CAPEX: Find industry reports or academic estimates
   - Validate all assumptions with citations

3. **Model refinement**:
   - Decide: Include fuel savings in MACC? (standard approach)
   - Decide: Industry-wide vs facility-level NCC choice?
   - Verify energy balance calculations

4. **Validation**:
   - Compare results with other Korea petrochemical studies
   - Sensitivity analysis on key parameters
   - Uncertainty quantification

### For Discussion
1. Accept current simplifications or increase complexity?
2. Academic paper framing: "Simple & Transparent" vs "Comprehensive"?
3. Target journal and methodology requirements?

---

## 9. 참고 문헌 (Preliminary)

### Grid Emission Factors
1. Climate Transparency (2022). "South Korea Country Profile"
2. Kim et al. (2022). "Scenario Analysis of GHG Emissions in Electricity Sector through 2030." *Energies* 15(9):3310.
3. Republic of Korea (2020). "2050 Carbon Neutral Strategy." UNFCCC.

### Electric Cracking
4. Tijani et al. (2022). "Review of Electric Cracking of Hydrocarbons." *ACS Sustainable Chemistry & Engineering*.
5. Park et al. (2022). "Electrified steam cracking for carbon neutral ethylene production." *Applied Energy*.
6. Chen et al. (2023). "Optimization of Electric Ethylene Production." *Industrial & Engineering Chemistry Research*.

### Naphtha Cracking Energy
7. Ren et al. (2006). "Olefins from conventional and heavy feedstocks: Energy use in steam cracking." *Energy* 31(3):425-451.
8. Various web sources (specific papers need identification)

### Korea Petrochemical
9. [Need to find Korea-specific petrochemical decarbonization studies]

---

**Status**: 🔴 **INCOMPLETE - LITERATURE REVIEW NEEDED**

**Priority Actions**:
1. ✅ Grid trajectory: Documented
2. ⚠️ Naphtha role: CRITICAL - Need clarification
3. ⚠️ NCC-H2 consumption: Need literature
4. ⚠️ CAPEX: Need sources
5. ⚠️ Model logic: Decide on fuel savings inclusion
