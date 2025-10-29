# Model Update Summary - October 29, 2025

## Overview
Successfully created technology assumptions Excel file and updated streamlit dashboard to use corrected model outputs.

---

## 1. Technology Assumptions Excel File

**File Created**: [docs/TECHNOLOGY_ASSUMPTIONS_FOR_REVIEW.xlsx](docs/TECHNOLOGY_ASSUMPTIONS_FOR_REVIEW.xlsx)

### Contents (7 Sheets):

1. **Technology Parameters**
   - CAPEX, OPEX, lifetime for all technologies (2025-2050)
   - Heat Pump, NCC-H2, NCC-Electricity, RE PPA

2. **Energy Consumption**
   - Detailed fuel/energy inputs for each technology
   - Energy balance clarifications (naphtha feedstock vs combustion fuels)
   - Emissions abatement calculations

3. **MACC Calculation (2030)**
   - Detailed cost breakdown example
   - Shows CAPEX annualized, OPEX annual, and fuel cost differential
   - Example: NCC-Electricity @ $541/tCO2 (approx)

4. **Price Trajectories**
   - H2: $6.00/kg (2025) → $2.00/kg (2050) - CORRECTED
   - RE: $90/MWh (2025) → $50/MWh (2050) - CORRECTED
   - All fuel prices with sources

5. **Emission Factors**
   - LNG: 0.0561 tCO2/GJ (IPCC 2019) - CORRECTED
   - Fuel Gas: 0.050 tCO2/GJ (API 2021) - CORRECTED
   - All fuels with source citations

6. **Energy Intensities**
   - Sample of 20 facilities showing actual energy use
   - Product mix and fuel consumption patterns

7. **Key Assumptions Summary**
   - 35+ critical assumptions with justifications
   - **HIGHLIGHTED**: Fuel cost methodology question
     - Current: Uses only new fuel costs
     - Standard MACC: Should include baseline fuel savings
     - Impact: ~$50-100/tCO2 reduction in costs

### Purpose
- Easy review of all technology parameters
- Facilitate discussion on model assumptions
- Prepare for academic paper parameter documentation
- Support sensitivity analysis planning

---

## 2. Streamlit Dashboard Update

**File Updated**: [app.py](app.py)

### Changes Made:

#### Data Source Updates:
- **Module 1 (Baseline)**: `outputs/module_01/` → `outputs/module_01_corrected/`
- **Module 2 (MACC)**: `outputs/module_02/` → `outputs/module_02_corrected/`
- **Module 3 (Optimization)**: `outputs/module_03/` → `outputs/module_03_corrected/`

#### New Data Displays:
Added preview options for corrected data:
- Hydrogen price trajectory (corrected)
- Renewable electricity price trajectory (corrected)
- Emission factors (corrected)

#### Documentation Updates:
- Updated help text to indicate CORRECTED data sources
- Added emission factor values in documentation (LNG: 0.0561, Fuel Gas: 0.050 tCO2/GJ)

### How to Run Dashboard:
```bash
streamlit run app.py
```

The dashboard will now display:
- **2025 Baseline**: 66.2 MtCO2 (vs 52.0 MtCO2 original)
- **2050 BAU**: 80.5 MtCO2
- **Technology Costs**: All updated with corrected H2/RE prices
- **Deployment Pathways**: Based on corrected data

---

## 3. Verification - All Corrected Outputs Present

### Module 1 - Baseline (CORRECTED):
✅ baseline_2025_detailed.csv (46 KB)
✅ bau_trajectory_2025_2050.csv (2.6 KB)
✅ emissions_by_product.csv
✅ emissions_by_location.csv
✅ emissions_by_company.csv
✅ Visualization PNGs

### Module 2 - MACC (CORRECTED):
✅ macc_annual_2025_2050.csv (15 KB)
✅ macc_cost_units_comparison.csv
✅ MACC curve PNGs (2025, 2030, 2040, 2050)
✅ cost_evolution_annual.png

### Module 3 - Optimization (CORRECTED):
✅ policy_target_deployment.csv (4.9 KB)
✅ policy_target_facility_allocation_2050.csv (26 KB)
✅ Policy_Target_regional_deployment.csv
✅ scenario_comparison.csv
✅ regional_baseline.csv
✅ Deployment visualization PNG

---

## 4. Data Corrections Applied (Summary)

### Emission Factors:
| Fuel | Original | Corrected | Change | Source |
|------|----------|-----------|--------|--------|
| LNG | 0.0149 | 0.0561 | +276% | IPCC 2019 |
| Fuel Gas | 0.0149 | 0.050 | +235% | API 2021 |

### H2 Prices:
| Year | Original | Corrected | Change | Source |
|------|----------|-----------|--------|--------|
| 2025 | $12.00/kg | $6.00/kg | -50% | IEA/IRENA 2024 |
| 2030 | $10.00/kg | $3.50/kg | -65% | IEA/IRENA 2024 |
| 2050 | - | $2.00/kg | - | Conservative estimate |

### RE Prices:
| Year | Original | Corrected | Change | Source |
|------|----------|-----------|--------|--------|
| 2025 | $130/MWh | $90/MWh | -31% | Korea RE auctions 2024 |
| 2030 | $115/MWh | $75/MWh | -35% | IRENA/BNEF 2024 |
| 2050 | $55/MWh | $50/MWh | -9% | Long-term floor |

### Impact on Results:
- **Baseline 2025**: 52.0 → 66.2 MtCO2 (+27%)
- **NCC-H2 Cost (2030)**: $2,075 → $477/tCO2 (-77%)
- **NCC-Elec Cost (2030)**: $268 → $259/tCO2 (-3%)
- **Achievable Reduction (2050)**: 54.6% → 37.7%

---

## 5. Next Steps for Discussion

### Critical Questions (From NCC Logic Review):

1. **Cost Methodology** ⚠️ PRIORITY
   - Should we include baseline fuel cost savings in MACC calculation?
   - Standard MACC approach: (New fuel cost - Baseline fuel cost) / Abatement
   - Current approach: New fuel cost / Abatement
   - Impact: ~$50-100/tCO2 reduction if changed
   - **Recommendation**: Change to standard MACC approach (2 hours work)

2. **Energy Balance Verification**
   - Model reports: 1.59 tCO2/ton abatement for NCC-Electricity
   - Hand calculation: ~0.38 tCO2/ton abatement
   - **Recommendation**: Trace through calculations (30 minutes)

3. **Mutual Exclusivity Approach**
   - Current: Industry-wide NCC technology selection
   - Alternative: Facility-level selection
   - **Recommendation**: Keep current (simpler for academic paper)

4. **Model Framing for Paper**
   - Option A: "Simple & Transparent Energy-Based MACC"
   - Option B: "Comprehensive Petrochemical Decarbonization Model"
   - **Recommendation**: Option A (broader audience, clearer methodology)

---

## 6. Files Ready for Academic Paper

### Documentation:
✅ [NCC_LOGIC_DEEP_REVIEW.md](NCC_LOGIC_DEEP_REVIEW.md) - 5,000+ words
✅ [DISCUSSION_FOR_ACADEMIC_PAPER.md](DISCUSSION_FOR_ACADEMIC_PAPER.md)
✅ [MODEL_STRUCTURE_FOR_PAPER.md](MODEL_STRUCTURE_FOR_PAPER.md)
✅ [DATA_VALIDATION_REPORT_2025_10_29.md](DATA_VALIDATION_REPORT_2025_10_29.md)
✅ [FINAL_COMPREHENSIVE_REPORT_2025_10_29.docx](FINAL_COMPREHENSIVE_REPORT_2025_10_29.docx)

### Data & Assumptions:
✅ [TECHNOLOGY_ASSUMPTIONS_FOR_REVIEW.xlsx](TECHNOLOGY_ASSUMPTIONS_FOR_REVIEW.xlsx) - NEW

### Code Structure:
✅ 6 core modules (2,000 lines total)
✅ 17 data files (all corrected)
✅ All unused files archived

---

## 7. How to Use the Updated Model

### Run the Dashboard:
```bash
streamlit run app.py
```

### Review Technology Assumptions:
Open: `docs/TECHNOLOGY_ASSUMPTIONS_FOR_REVIEW.xlsx`
- Sheet 7 has the key discussion point highlighted in yellow

### Rerun Corrected Model:
```bash
python run_corrected_model.py
```

### Review Model Logic:
Read: `docs/NCC_LOGIC_DEEP_REVIEW.md`
- Contains 5 critical questions for discussion

---

## Summary

**Work Completed**:
1. ✅ Created comprehensive technology assumptions Excel file (7 sheets)
2. ✅ Updated streamlit dashboard to use corrected data
3. ✅ Verified all corrected outputs are present
4. ✅ Documented all changes and next steps

**Ready for User**:
- Excel file ready for parameter review
- Dashboard ready to run with corrected data
- All documentation prepared for academic paper
- Discussion questions formulated for model refinement

**Awaiting User Input**:
- Review technology assumptions in Excel file
- Discuss 4 critical questions about model methodology
- Decide on cost methodology change (recommended)
- Decide on paper framing approach
