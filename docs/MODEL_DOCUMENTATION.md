# Korean Petrochemical MACC Model Documentation
# 한국 석유화학 MACC 모델 문서

**Date:** December 10, 2024
**Version:** 2.0
**Status:** COMPLETE - All scenarios executed with final assumptions

---

## Executive Summary

This model analyzes decarbonization pathways for Korea's petrochemical industry (2025-2050), covering **237 baseline facilities** with **100,066 kt/year capacity**. The model calculates Marginal Abatement Cost Curves (MACC) and optimizes technology deployment across 6 scenarios.

---

## 1. Price Trajectories

### 1.1 Two Types of Electricity

| Type | 2025 Price | 2050 Price | Emission Factor | Usage |
|------|------------|------------|-----------------|-------|
| **Grid** | $100/MWh | $191/MWh | 0.436→0.0 tCO₂/MWh | Heat Pump, baseline electricity |
| **Renewable (RE-PPA)** | $65/MWh | $30/MWh | 0.0 tCO₂/MWh | NCC-Electricity, RE switching |

**Key Points:**
- Grid electricity price increases due to decarbonization infrastructure investment
- RE-PPA price declines following global renewable cost trends (IRENA 2024)
- Grid achieves complete decarbonization (EF = 0) by 2050

### 1.2 Green Hydrogen Price (LCOH-Linked)

**Critical: H₂ price is calculated from RE price via LCOH formula.**

```
LCOH = (CAPEX × CRF + OPEX + Stack) / H2_Production + Electricity_Cost

Where:
- Electricity = RE price (green H2 from electrolysis)
- CAPEX: $1,000/kW (2025) → $500/kW (2050)
- Efficiency: 70% (2025) → 75% (2050)
- Capacity Factor: 90%
```

| Year | H₂ Price ($/kg) | RE Price ($/MWh) | Electrolyzer CAPEX |
|------|-----------------|------------------|-------------------|
| 2025 | 4.58 | $65 | $1,000/kW |
| 2030 | 3.91 | $56 | $900/kW |
| 2040 | 2.82 | $41 | $700/kW |
| 2050 | 2.01 | $30 | $500/kW |

**Decline rate:** 56% reduction (H₂), 54% reduction (RE) from 2025 to 2050

### 1.3 Grid Emission Factor Trajectory

| Year | Grid EF (tCO₂/MWh) | Reduction |
|------|-------------------|-----------|
| 2025 | 0.436 | Baseline |
| 2030 | 0.349 | -20% |
| 2040 | 0.140 | -68% |
| 2050 | 0.000 | -100% (Net Zero) |

---

## 2. Technology Assumptions

### 2.1 NCC-Electricity (Electric Cracker)

| Parameter | Value | Source |
|-----------|-------|--------|
| **Electricity consumption** | 5.0 MWh/ton C₂H₄ | BASF/SABIC/Linde 2024 pilot |
| **CAPEX 2025** | $1,500/t/yr | Toribio-Ramirez et al. 2025 |
| **CAPEX 2050** | $750/t/yr | 50% learning curve |
| **OPEX** | 4% of CAPEX | Industry standard |
| **TRL** | 8 | Commercial pilot demonstrated |
| **Available from** | 2030 | Conservative deployment |

### 2.2 NCC-H₂ (Hydrogen-Fueled Cracker)

| Parameter | Value | Source |
|-----------|-------|--------|
| **H₂ consumption** | 0.2 ton/ton C₂H₄ | Lummus Tech 2023 |
| **CAPEX 2025** | $1,700/t/yr | Thunder Said Energy 2023 |
| **CAPEX 2050** | $850/t/yr | 50% learning curve |
| **OPEX** | 4% of CAPEX | Industry standard |
| **TRL** | 7 | ExxonMobil validated |
| **Available from** | 2030 | Conservative deployment |

### 2.3 Heat Pump

| Parameter | Value | Source |
|-----------|-------|--------|
| **COP** | 4.0 | Kosmadakis 2020 |
| **CAPEX 2025** | $800 M/MtCO₂ | Industry benchmark |
| **CAPEX 2050** | $400 M/MtCO₂ | 50% learning curve |
| **OPEX** | 3% of CAPEX | Industry standard |
| **Applicable to** | Processes <165°C | Temperature limit |
| **TRL** | 9 | Commercially mature |
| **Available from** | 2025 | Immediate |

### 2.4 RDH (RotoDynamic Heater)

| Parameter | Value | Source |
|-----------|-------|--------|
| **Application** | High-temp BTX | Coolbrook technology |
| **Efficiency** | 93% | Coolbrook specs |
| **CAPEX 2025** | $900 M/MtCO₂ | Industry estimate |
| **CAPEX 2050** | $450 M/MtCO₂ | 50% learning curve |
| **OPEX** | 3% of CAPEX | Industry standard |
| **TRL** | 8 | Pilot demonstrated |
| **Available from** | 2026 | Near-term deployment |

### 2.5 RE-PPA (Renewable Power Purchase Agreement)

| Parameter | Value | Source |
|-----------|-------|--------|
| **CAPEX** | $0 | Contract-based |
| **OPEX** | $0 | Included in PPA price |
| **Application** | Grid→RE switching | All electricity users |
| **Available from** | 2025 | Immediate |

---

## 3. Emission Factors

| Fuel | Emission Factor | Unit | Source |
|------|-----------------|------|--------|
| Naphtha | 0.0542 | tCO₂/GJ | IPCC 2019, Table 2.3 |
| LNG | 0.0561 | tCO₂/GJ | IPCC 2019, Table 2.3 |
| Fuel Gas | 0.050 | tCO₂/GJ | API Compendium 2021 |
| Byproduct Gas | 0.048 | tCO₂/GJ | API Compendium 2021 |
| LPG | 0.0631 | tCO₂/GJ | IPCC 2019, Table 2.3 |
| Fuel Oil | 0.0773 | tCO₂/GJ | IPCC 2019, Table 2.3 |
| Diesel | 0.0741 | tCO₂/GJ | IPCC 2019, Table 2.3 |
| Green H₂ | 0.0 | tCO₂/kg | Electrolysis (zero-emission) |

---

## 4. Scenario Framework

### 4.1 Six Scenarios (3 Production × 2 Technology)

| # | Scenario | Production | NCC Technology |
|---|----------|------------|----------------|
| 1 | shaheen_ncc_h2 | Shaheen Growth (+6 facilities) | NCC-H₂ |
| 2 | shaheen_ncc_elec | Shaheen Growth (+6 facilities) | NCC-Electricity |
| 3 | restructure_25pct_ncc_h2 | -25% NCC capacity | NCC-H₂ |
| 4 | restructure_25pct_ncc_elec | -25% NCC capacity | NCC-Electricity |
| 5 | restructure_40pct_ncc_h2 | -40% NCC capacity | NCC-H₂ |
| 6 | restructure_40pct_ncc_elec | -40% NCC capacity | NCC-Electricity |

### 4.2 Key Results

- **All scenarios achieve Net Zero by 2050**
- **Investment range:** $13.4B - $22.1B depending on scenario
- **No CCS/CCUS** - focus on electrification and green hydrogen

---

## 5. Key Files

### Data Files
- `data/inputs/facilities.csv` - 237 baseline facilities
- `data/inputs/energy_intensities.csv` - Energy consumption by product
- `data/inputs/emission_factors.csv` - CO₂ emission factors
- `data/inputs/technology_capex.csv` - Technology parameters
- `data/price_trajectories/h2_price_trajectory.csv` - H₂ prices (LCOH-derived)
- `data/price_trajectories/re_price_trajectory.csv` - RE prices
- `data/price_trajectories/grid_emission_trajectory.csv` - Grid EF trajectory

### Code Modules
- `modules/baseline.py` - Baseline emission calculations
- `modules/macc.py` - MACC curve generation
- `modules/optimization_v2.py` - Technology deployment optimization
- `modules/lcoh.py` - LCOH calculation (RE→H₂ price link)

### Outputs
- `outputs/scenario_results.csv` - Complete scenario results
- `reports/Korea_Petrochemical_NetZero_Analysis_*.xlsx` - Client reports

---

## 6. Usage

### Run Scenarios
```bash
python run_scenarios.py
```

### Generate Reports
```bash
python analyze_results.py
```

### Launch Dashboard
```bash
streamlit run streamlit_app.py
```

---

## 7. References

### Technology Data
1. **BASF/SABIC/Linde (2024)** - Electric cracker pilot (5.0 MWh/ton)
2. **Toribio-Ramirez et al. (2025)** - E-cracker CAPEX ($1,500/t)
3. **Lummus Tech (2023)** - H₂ cracker case study (200 kg H₂/ton)
4. **Thunder Said Energy (2023)** - H₂ cracker economics ($1,700/t)
5. **Kosmadakis (2020)** - Heat pump COP values
6. **Coolbrook (2024)** - RDH technology specifications

### Price & Emission Data
7. **IRENA 2024** - Renewable electricity price trajectories
8. **IEA WEO 2024** - Energy price projections
9. **IPCC 2019** - Fuel emission factors (Table 2.3)
10. **API Compendium 2021** - Refinery gas emission factors
11. **Korea MOE** - Grid emission factor trajectory

### Attribution
This model incorporates data and methodologies from **PLANiT Institute (2025)**:
- RE PPA Price Trajectory
- LCOH Calculation Methodology

---

## Document Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Oct 2024 | Initial release |
| 2.0 | Dec 10, 2024 | Updated all price trajectories; Corrected Grid EF to 0.0 (2050); Added LCOH formula; Synchronized with data files |

---

**Model Status:** COMPLETE - Ready for analysis and reporting

**Last Updated:** December 10, 2024
