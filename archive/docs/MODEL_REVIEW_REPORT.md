# Korea Petrochemical MACC Model Review Report

**Review Date:** January 2025
**Model Version:** planit_report_v0.5
**Review Scope:** Accuracy verification, assumption validation, methodology review
**Audience:** External stakeholders (clients, investors, regulators)

---

## Executive Summary

This report documents the comprehensive review of the Korea Petrochemical MACC (Marginal Abatement Cost Curve) model. The model analyzes decarbonization pathways for Korea's petrochemical industry (2025-2050), covering 237 facilities across 6 scenarios.

### Key Findings

| Category | Status | Summary |
|----------|--------|---------|
| **Calculation Accuracy** | ✅ Verified | Core formulas match documentation; NCC naphtha correctly treated as feedstock |
| **Data Quality** | ✅ Good | 100% facility-benchmark coverage; no NaN in critical fields |
| **Assumption Documentation** | ⚠️ Needs Work | 3 RED FLAG assumptions require resolution |
| **Methodology** | ✅ Sound | LCOA-based greedy optimization appropriate for planning purposes |
| **Test Coverage** | 🆕 Created | 75+ unit/integration tests now available |

---

## 1. Accuracy Verification

### 1.1 Manual Spot Checks

#### Facility 1: Yeochon NCC Ethylene (Large NCC)
- **Location:** Yeosu Complex
- **Capacity:** 2,285 kt/yr (largest NCC in Korea)
- **Process:** Naphtha Cracker

**Calculation Verification:**

| Parameter | Expected Calculation | Model Value | Status |
|-----------|---------------------|-------------|--------|
| Production (70% OR) | 2,285,000 × 0.7 = 1,599,500 t | ✓ | ✅ |
| Naphtha Energy | 1,599,500 × 29.0 = 46,385,500 GJ | ✓ | ✅ |
| LNG Energy | 1,599,500 × 2.027 = 3,242,187 GJ | ✓ | ✅ |
| LPG Energy | 1,599,500 × 5.223 = 8,354,509 GJ | ✓ | ✅ |
| **Naphtha Emissions** | **0 (feedstock, not fuel)** | ✓ | ✅ |
| LNG Emissions | 3,242,187 × 0.0561 = 181,887 tCO2 | ✓ | ✅ |
| LPG Emissions | 8,354,509 × 0.0631 = 527,169 tCO2 | ✓ | ✅ |

**Key Finding:** NCC naphtha correctly treated as feedstock (zero combustion emissions). This is the most critical calculation in the model and is implemented correctly.

#### Facility 2: SK Geocentric Propylene (Small NCC)
- **Location:** Ulsan Complex
- **Capacity:** 380 kt/yr (smallest NCC)
- **Process:** Naphtha Cracker

**Verification Result:** ✅ Pass - Scale effects correctly handled

#### Facility 3: Hanwha TotalEnergies Benzene (BTX Plant)
- **Location:** Daesan Complex
- **Capacity:** 1,267 kt/yr
- **Process:** BTX Plant

**Key Verification:**
- Naphtha_GJ_per_tonne = 0 (BTX has no naphtha feedstock) ✅
- Technology: RDH (RotoDynamic Heater) correctly assigned ✅
- RDH efficiency: 0.93 from CSV ✅

#### Facility 4: HDPE Facility (Utility Process)
- **Process:** Utility (polymer production)

**Key Verification:**
- Technology: Heat_Pump correctly assigned ✅
- COP: 4.0 from CSV ✅
- Electricity calculation: Heat_GJ / 3.6 / 4.0 ✅

#### Facility 5: Smallest Facility Edge Case
- **Capacity:** 8 kt (MA - Maleic Anhydride)

**Key Verification:**
- Calculations remain valid at small scale ✅
- No division by zero errors ✅

### 1.2 Formula Verification

| Formula | Code Location | Expected | Verified |
|---------|--------------|----------|----------|
| MAC | `capex_calculator.py:271` | (CAPEX_ann + OPEX + Energy - Savings) / Abatement | ✅ |
| Annualized CAPEX | `capex_calculator.py:149` | CAPEX_total / lifetime | ✅ |
| Emission | `utils.py:169` | Energy × EF | ✅ |
| Heat Pump Elec | `utils.py:515-516` | Heat_GJ / 3.6 / COP | ✅ |
| NCC-H2 Demand | `utils.py:492-493` | Production × 0.2 t-H2/t | ✅ |
| NCC-Elec Demand | `utils.py:496-497` | Production × 5.0 MWh/t | ✅ |

### 1.3 Unit Consistency

| Parameter | Expected Unit | Verified |
|-----------|---------------|----------|
| Capacity | kt/yr → tonnes (×1000) | ✅ |
| Energy Intensity | GJ/t or kWh/t | ✅ |
| Emission Factors | tCO2/GJ or tCO2/kWh | ✅ |
| CAPEX Rate | $/t-product/yr | ✅ |
| H2 Price | $/kg → $/t (×1000) | ✅ |
| GJ to MWh | 3.6 GJ = 1 MWh | ✅ |

---

## 2. Assumption Validation

### 2.1 RED FLAG Assumptions (Critical - Action Required)

#### 🔴 RED FLAG 1: RDH CAPEX - No Public Data

| Parameter | Value | Issue |
|-----------|-------|-------|
| RDH CAPEX 2025 | $250/t-BTX/yr | "Estimated from Coolbrook 2024" |
| RDH CAPEX 2050 | $140/t-BTX/yr | "NO PUBLIC CAPEX DATA" in notes |

**Risk:** RDH technology (Coolbrook RotoDynamic Heater) has no independently verifiable CAPEX data. This affects all BTX facility calculations.

**Recommendation:**
1. Flag as "HIGH UNCERTAINTY" in all reports
2. Include ±30% sensitivity analysis
3. Seek independent quote from technology provider

---

#### 🔴 RED FLAG 2: Grid Price Logic Inconsistency

| Year | Grid Price | RE Price | Issue |
|------|-----------|----------|-------|
| 2025 | $100/MWh | $65/MWh | Grid higher (expected) |
| 2050 | $191/MWh | $30/MWh | Grid 6.4× higher than RE |

**Risk:** By 2050, grid electricity costs $191/MWh while renewable PPA is $30/MWh. This 6× difference lacks clear justification.

**Recommendation:**
1. Document policy rationale (e.g., infrastructure investment recovery)
2. Or revise trajectory to converge with RE by 2050
3. Add explanation in methodology documentation

---

#### 🔴 RED FLAG 3: NCC 85% Coverage Undocumented

**Issue:** Code comments mention "85% of NCC emissions" covered by technology, but no breakdown is provided.

**Questions:**
- What emits the remaining 15%?
- Is it auxiliary burners, hot oil systems, or other sources?
- Can these be addressed with Heat Pump?

**Recommendation:**
1. Document emission source breakdown (furnace vs auxiliary)
2. Clarify technology applicability to each source

---

### 2.2 AMBER FLAG Assumptions (Medium Priority)

| # | Assumption | Value | Issue | Recommendation |
|---|------------|-------|-------|----------------|
| 1 | Discount Rate | 8% | "Standard industrial rate" - no Korea-specific justification | Verify against Korean WACC (~6-10%) |
| 2 | Operating Rate | 70% | "Industry average" - no source cited | Verify against KPIA historical data |
| 3 | CAPEX Learning | 50% by 2050 | Round number, not evidence-based | Use IEA/IRENA technology-specific learning rates |
| 4 | Fuel Prices | Constant 2025-2050 | All fuels unchanged for 25 years | Confirm intentional policy or add trajectory |
| 5 | NCC-H2 Efficiency | 85% | "Blended HHV/LHV" | Clarify which basis used in calculations |

### 2.3 Well-Documented Assumptions (Low Risk)

| Assumption | Value | Source | Status |
|------------|-------|--------|--------|
| Heat Pump COP | 4.0 | Kosmadakis 2020 | ✅ Peer-reviewed |
| NCC-H2 H2 consumption | 0.2 t-H2/t-ethylene | Power Engineering 2022 | ✅ Industry source |
| NCC-Elec consumption | 5.0 MWh/t-ethylene | BASF/SABIC/Linde | ✅ Demo data |
| RE Price trajectory | $65→$30/MWh | IRENA 2024, IEA WEO 2024 | ✅ Official forecasts |
| H2 Price trajectory | $4.58→$2.01/kg | LCOH calculation | ✅ Methodology clear |
| Emission Factors | IPCC values | IPCC 2019 Table 2.3 | ✅ International standard |
| Grid EF 2025 | 0.436 tCO2/MWh | Korea MOE | ✅ Official data |
| Grid EF 2050 | 0.0 tCO2/MWh | Policy target | ✅ Net zero alignment |

---

## 3. Methodology Review

### 3.1 Amortization Method

**Current:** Linear amortization (CAPEX / lifetime)
```python
def calculate_annualized_capex(self, capex_total, lifetime_years):
    return capex_total / lifetime_years
```

**Alternative:** Capital Recovery Factor (CRF)
```
CRF = r × (1+r)^n / ((1+r)^n - 1)
For r=8%, n=25: CRF = 0.0937
```

**Impact Comparison:**
| Method | Annual Cost (per $1M CAPEX) |
|--------|---------------------------|
| Linear | $1M / 25 = $40,000/yr (4%) |
| CRF | $1M × 0.0937 = $93,700/yr (9.37%) |

**Recommendation:** Document linear method choice. For financial modeling, CRF more accurately reflects time value of money. Consider providing both for comparison.

### 3.2 Optimization Approach

**Current:** Greedy LCOA-based deployment
- Facilities ranked by Levelized Cost of Abatement
- Deployed cheapest-first until emission target met
- No technology switching after deployment

**Assessment:**
- ✅ Appropriate for planning-level analysis
- ✅ Computationally efficient
- ⚠️ Not globally optimal (greedy heuristic)
- ⚠️ Assumes perfect foresight of future prices

**Recommendation:** Document as "cost-minimizing heuristic" rather than "optimal solution"

### 3.3 NCC Naphtha Treatment

**Current Implementation:** Naphtha treated as feedstock for NCC facilities
```python
# From utils.py:278-282
if is_ncc:
    # Naphtha is feedstock in NCC - no combustion emissions
    emissions_by_source['naphtha'] = 0.0
    # Also exclude naphtha from heat demand
    total_heat_gj -= energy_by_source['naphtha']
```

**Assessment:** ✅ **Correct**
- Naphtha in NCC is cracked into products (ethylene, propylene, etc.)
- Only LNG, LPG, and byproduct gas are heating fuels
- Fuel savings correctly exclude naphtha for NCC

---

## 4. Test Suite Summary

### 4.1 Tests Created

| Test File | Tests | Purpose |
|-----------|-------|---------|
| `test_calculators.py` | 35 | Unit tests for EmissionCalculator, CapexCalculator, MACCalculator, PriceCalculator |
| `test_data_validation.py` | 30 | Input data quality, ranges, completeness |
| `test_integration.py` | 15 | Scenario execution, baseline validation, cross-validation |
| **Total** | **80** | - |

### 4.2 Key Test Coverage

| Component | Test Coverage |
|-----------|--------------|
| Emission calculation by fuel | ✅ All 9 fuels |
| NCC naphtha feedstock treatment | ✅ Verified |
| CAPEX interpolation | ✅ 2025, 2030, 2040, 2050 |
| MAC formula | ✅ With/without fuel savings |
| Technology assignment | ✅ NCC/BTX/Utility |
| Price trajectory | ✅ H2, RE interpolation |
| Data bounds | ✅ EF, COP, prices |
| Baseline emissions | ✅ ~47 MtCO2 |
| Net zero 2050 | ✅ All scenarios |

### 4.3 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_calculators.py -v

# Run with coverage
pytest tests/ --cov=modules --cov-report=html
```

---

## 5. Known Limitations

### 5.1 Model Scope Limitations

| Limitation | Description |
|------------|-------------|
| No CCS/CCUS | Model focuses on electrification and green H2 |
| Scope 1+2 only | No Scope 3 (supply chain) emissions |
| No feedstock change | Assumes continued naphtha base (no bio-naphtha) |
| Korea-specific | Grid EF, prices, and policies are Korea-specific |

### 5.2 Methodology Limitations

| Limitation | Impact |
|------------|--------|
| Linear amortization | May understate financial costs vs CRF |
| Greedy optimization | Not globally optimal |
| Perfect foresight | Assumes known future prices |
| Technology lock-in | No retrofit or switching modeled |
| Constant fuel prices | 25-year flat fossil fuel prices |

### 5.3 Data Limitations

| Data Gap | Status |
|----------|--------|
| RDH CAPEX | Estimated - no public data |
| Grid price 2050 | Policy assumption needed |
| Facility-level validation | Based on KPIA aggregates |

---

## 6. Recommendations

### 6.1 Immediate Actions (Before External Release)

1. **Resolve RDH CAPEX** - Add uncertainty range or independent verification
2. **Document grid price logic** - Explain $191/MWh vs $30/MWh in 2050
3. **Add NCC coverage breakdown** - Document 85% vs 15% emission sources

### 6.2 Methodology Enhancements

1. **Provide CRF comparison** - Calculate both linear and CRF for financial audiences
2. **Sensitivity analysis** - H2 price ±20%, CAPEX ±30%, discount rate 6-10%
3. **Document optimization** - Clearly state greedy heuristic limitations

### 6.3 Documentation Improvements

1. **Assumption register** - Create Excel with sources, confidence levels
2. **Methodology summary** - 10-page document for external stakeholders
3. **Known limitations** - Include in all deliverables

---

## 7. Conclusion

The Korea Petrochemical MACC model is **fundamentally sound** for planning-level analysis. The core calculations are correct, with NCC naphtha properly treated as feedstock. The greedy LCOA-based optimization is appropriate for strategic planning purposes.

**Three critical issues require resolution** before external stakeholder release:
1. RDH CAPEX uncertainty
2. Grid price trajectory logic
3. NCC emission coverage documentation

With these addressed, the model provides a credible foundation for Korea petrochemical decarbonization planning.

---

*Report prepared as part of model review process*
