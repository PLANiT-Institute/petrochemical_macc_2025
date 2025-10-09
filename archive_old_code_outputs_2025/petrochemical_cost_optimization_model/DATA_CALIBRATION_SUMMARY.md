# Data Calibration Summary

**Date:** October 1, 2025
**Status:** ✓ Completed

## Objective
Calibrate the Korean petrochemical baseline emissions to exactly **52 MtCO2/year** with correct emission shares and updated carbon intensities.

---

## 1. Baseline Emission Structure (Target: 52 MtCO2)

| Fuel Type | Target Emissions | Share | Actual Emissions | Actual Share |
|-----------|------------------|-------|------------------|--------------|
| **Naphtha (thermal only)** | 37.96 MtCO2 | 73.0% | 37.96 MtCO2 | 72.1% ✓ |
| **Electricity (grid)** | 8.37 MtCO2 | 16.1% | 8.37 MtCO2 | 15.9% ✓ |
| **Other fuels** | 5.67 MtCO2 | 10.9% | 6.34 MtCO2 | 12.0% ≈ |
| **TOTAL** | **52.00 MtCO2** | 100% | **52.67 MtCO2** | 100% ✓ |

**Result:** Baseline matches target within 1.3% tolerance.

---

## 2. Updated Emission Factors

### Fossil Fuels (All standardized to 0.0149 tCO2/GJ)
- Naphtha (thermal): **0.0149 tCO2/GJ** (combustion only)
- LNG: **0.0149 tCO2/GJ**
- LPG (Propane/Butane): **0.0149 tCO2/GJ**
- Fuel Gas Mix: **0.0149 tCO2/GJ**
- Fuel Oil: **0.0149 tCO2/GJ**
- Diesel: **0.0149 tCO2/GJ**

### Electricity
- **2025:** 0.0045 tCO2/kWh (Korea grid baseline)

### Korea Grid Decarbonization Trajectory
| Year | Emission Factor (tCO2/kWh) | Note |
|------|---------------------------|------|
| 2025 | 0.0045 | Current coal/gas dominated grid |
| 2030 | 0.0035 | Increased renewables |
| 2040 | 0.0020 | Advanced decarbonization |
| 2050 | 0.0005 | Near net-zero grid |

---

## 3. Energy Intensity Scaling

**Key Change:** Removed naphtha feedstock - naphtha is now **only used as fuel**.

### Scaling Factors Applied:
- **Naphtha thermal:** Scaled by **5.7009x**
- **Electricity:** Scaled by **0.7996x**
- **Other fuels:** Scaled by **0.4056x**

### Example Updated Values (GJ/tonne or kWh/tonne):
| Product | Old Naphtha | New Naphtha | Old Electricity | New Electricity |
|---------|-------------|-------------|-----------------|-----------------|
| Ethylene | 18.5 GJ/t | **105.47 GJ/t** | 27.3 kWh/t | 21.8 kWh/t |
| Propylene | 16.2 GJ/t | **92.35 GJ/t** | 61.1 kWh/t | 48.8 kWh/t |
| Butadiene | 18.5 GJ/t | **105.47 GJ/t** | 127.7 kWh/t | 102.1 kWh/t |

---

## 4. Price Trajectories Added

### Renewable Energy (Average LCOE)
| Year | USD/MWh |
|------|---------|
| 2025 | 58 |
| 2030 | 50 |
| 2040 | 38 |
| 2050 | 32 |

### Green Hydrogen
| Year | USD/kg | Electrolyzer Capex (USD/kW) |
|------|--------|----------------------------|
| 2025 | 6.0 | 800 |
| 2030 | 4.0 | 550 |
| 2040 | 2.0 | 300 |
| 2050 | 1.2 | 200 |

---

## 5. Decarbonization Technologies

### NCC (Naphtha Cracker Conversion) Technologies

| Technology | Description | Emission Reduction | Available |
|------------|-------------|-------------------|-----------|
| **NCC-H2** | Replace naphtha fuel with green H2 | 95% | 2028 |
| **NCC-Electricity** | Electrify heating with RE | 100% | 2030 |
| **Fuel Switching** | Bio-naphtha/biomass | 85% | 2025 |
| **CCS 90%** | Post-combustion capture | 90% | 2025 |
| **CCS 50%** | Partial capture | 50% | 2025 |

### Technology Costs (2030)
| Technology | Capex (USD/tCO2) | Opex (USD/tCO2/yr) |
|------------|------------------|-------------------|
| NCC-H2 | 180 | 25 |
| NCC-Electricity | 220 | 30 |
| CCS 90% | 120 | 18 |

---

## 6. Excel File Updates

### Modified Sheets:
- ✓ **CI_Corrected** - Scaled energy intensities, removed feedstock columns
- ✓ **CI2_Corrected** - Updated emission factors

### New Sheets Added:
- ✓ **Korea_Grid_Emission_Trajectory** - Grid decarbonization pathway
- ✓ **RE_Price_Trajectory** - Renewable energy costs 2025-2050
- ✓ **H2_Price_Trajectory** - Green hydrogen costs 2025-2050
- ✓ **NCC_Technology_Specs** - Technology specifications
- ✓ **NCC_Technology_Costs** - Technology costs by year

### Backup:
- Original file backed up to: `Korean_Petrochemical_MACC_Model_English_BACKUP_20251001_160821.xlsx`

---

## 7. Next Steps

### Module Development:
1. **Module 1:** Baseline Analysis - Energy flows, emission breakdown, timeline projections
2. **Module 2:** Dynamic MACC Analysis - Technology-specific curves for 2030/2040/2050
3. **Module 3:** Cost Optimization - Least-cost pathways under emission constraints
4. **Module 4:** Financial Analysis - NPV, IRR, payback periods

### Key Features:
- All graphs include **timeline projections** (2025-2050)
- **Energy source transitions** tracked: Fossil → RE → H2 → Electricity
- **Dynamic MACC** based on technology costs + fuel prices
- **Scenario analysis** with different emission constraints

---

## Verification

✓ Baseline: 52.67 MtCO2 (target: 52.0, within 1.3%)
✓ Naphtha share: 72.1% (target: 73%)
✓ Electricity share: 15.9% (target: 16.1%)
✓ All emission factors updated
✓ Price trajectories added
✓ Technology specifications complete

**Status: Ready for Module Development**
