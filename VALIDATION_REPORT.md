# Model Validation Report: Company Emissions Comparison

## Executive Summary

**Total Industry Emissions:** ✅ Model total (52 MtCO2) is reasonable for Korean petrochemical industry

**Company Distribution:** ⚠️ Significant discrepancies - Model does NOT match real-world company rankings

---

## Comparison Results

### Our Model Results (2025 Baseline)

| Rank | Company | Emissions (MtCO2) | Share (%) |
|------|---------|-------------------|-----------|
| 1 | Kumho Petrochemical | 8.97 | 17.3% |
| 2 | SK Chemicals | 7.31 | 14.1% |
| 3 | Hyundai Chemical | 7.26 | 14.0% |
| 4 | Hanwha Solutions | 7.15 | 13.7% |
| 5 | Samsung Total | 6.70 | 12.9% |
| 6 | **LG Chem** | **4.99** | **9.6%** ⚠️ |
| 7 | **Lotte Chemical** | **4.03** | **7.7%** ⚠️ |
| 8-10 | Others | 5.59 | 10.7% |

**Total: 52.00 MtCO2**

---

### Real-World Data (2023)

#### Verified Data:

**Lotte Chemical:**
- Real emissions: **6.06 MtCO2** (Scope 1+2, 2023)
- Source: Tracenable/ESG Report
- Model prediction: 4.03 MtCO2
- **Error: -33% (underestimated)**

**LG Chem:**
- Real emissions: **~10-15 MtCO2** (estimated, 2023)
- Source: Part of LG Group's 17 MtCO2 total
- Model prediction: 4.99 MtCO2
- **Error: -50% to -66% (severely underestimated)**

#### Industry Rankings by Production Capacity:

Based on ethylene production capacity (key indicator):

| Rank | Company | Ethylene Capacity (M tpy) | Expected Rank |
|------|---------|---------------------------|---------------|
| 1 | **LG Chem** | 3.38 | #1 |
| 2 | **Lotte Chemical** | 2.33 | #2 |
| 3 | Yeochun NCC (Hanwha/DL) | 2.29 | #3 |
| 4 | Hanwha TotalEnergies | 1.53 | #4 |
| 5 | Others | Various | #5+ |

---

## Key Issues Identified

### 1. Major Companies Underestimated

**LG Chem:**
- Should be: #1 (largest producer)
- Model rank: #6
- Emissions should be: ~10-15 MtCO2
- Model shows: 4.99 MtCO2
- **Issue: Severely underestimated by 50-66%**

**Lotte Chemical:**
- Should be: #2 (2nd largest)
- Model rank: #7
- Emissions should be: ~6-8 MtCO2
- Model shows: 4.03 MtCO2
- **Issue: Underestimated by 33-50%**

### 2. Minor Companies Overestimated

**Kumho Petrochemical:**
- Model rank: #1 (8.97 MtCO2)
- Reality: Should be mid-tier player
- **Issue: Overestimated**

**SK Chemicals:**
- Model rank: #2 (7.31 MtCO2)
- Reality: Should be smaller player
- **Issue: Overestimated**

---

## Root Cause Analysis

### Problem: Random Company Assignment

In `create_data_files.py`, line 48-57:

```python
for i in range(n_facilities):
    product_idx = i % n_products
    product = products_list[product_idx]

    # Random assignment - PROBLEM!
    facility = {
        'product': product,
        'company': np.random.choice(companies),  # ← Random!
        'location': np.random.choice(locations),
        'capacity': capacity_variation
    }
```

**Issue:** Facilities were assigned to companies randomly with equal probability, not weighted by actual market share.

**Impact:**
- LG Chem should own ~30-35% of facilities
- Lotte Chemical should own ~20-25% of facilities
- But random assignment gave them only ~12% and ~10% respectively

---

## Validation Against Real Data

### Total Industry Level: ✅ VALIDATED

- Korea petrochemical industry: ~50-60 MtCO2 (estimated)
- Model total: 52.00 MtCO2
- **Status: Reasonable**

### Company Distribution: ❌ NOT VALIDATED

| Company | Expected Share | Model Share | Status |
|---------|----------------|-------------|--------|
| LG Chem | 25-30% | 9.6% | ❌ Too Low |
| Lotte Chemical | 15-20% | 7.7% | ❌ Too Low |
| Hanwha | 10-15% | 13.7% | ⚠️ Slightly High |
| Others | 40-50% | 69.0% | ⚠️ Distribution Wrong |

---

## Recommendations

### 1. Fix Company Allocation (Priority: HIGH)

Replace random assignment with weighted allocation based on real market share:

```python
# Proposed fix in create_data_files.py
company_weights = {
    'LG Chem': 0.30,           # 30% of facilities
    'Lotte Chemical': 0.22,     # 22% of facilities
    'Hanwha Solutions': 0.15,   # 15% of facilities
    'Yeochun NCC': 0.12,        # 12% of facilities
    'SK Chemicals': 0.08,       # 8% of facilities
    'Samsung Total': 0.05,      # 5% of facilities
    'Others': 0.08              # 8% of facilities
}

company = np.random.choice(
    list(company_weights.keys()),
    p=list(company_weights.values())
)
```

### 2. Validate Against Production Data

Match emissions to ethylene/propylene production:

- LG Chem: 3.38M tpy ethylene → expect ~10-12 MtCO2
- Lotte: 2.33M tpy ethylene → expect ~6-8 MtCO2
- Use production intensity: ~3-3.5 tCO2 per ton ethylene

### 3. Use Real Facility Database

Replace synthetic data with actual facility data:

**Data Sources:**
- Korean Petrochemical Industry Association (KPIA)
- K-REACH facility registration
- Company sustainability reports
- Ministry of Environment GHG reporting system
- Korea Emissions Trading System (K-ETS) data

### 4. Cross-Validate with ESG Reports

Obtain and validate against company ESG reports:
- Lotte Chemical: 6.06 MtCO2 (2023) ✅ Available
- LG Chem: Need to extract from 2024 report
- Hanwha Solutions: Need ESG data
- SK Chemicals: Need ESG data

---

## Impact on Model Results

### What is NOT Affected: ✅

1. **Total industry emissions** (52 MtCO2)
2. **Technology potential** (MACC curves)
3. **Overall decarbonization pathways**
4. **Cost estimates** (aggregated level)
5. **Policy recommendations** (industry-wide)

### What IS Affected: ⚠️

1. **Company-specific analysis** (wrong rankings)
2. **Facility ownership patterns**
3. **Company benchmarking** (not reliable)
4. **Investment allocation by company**
5. **Company-specific targets** (inaccurate)

---

## Interim Solution

**For Industry-Level Analysis:** ✅ Current model is acceptable

Use current model for:
- Total industry abatement potential
- Technology deployment scenarios
- Aggregated cost analysis
- Policy scenario modeling

**For Company-Level Analysis:** ⚠️ Use with caution

Current company rankings are NOT reliable. Do not use for:
- Company benchmarking
- Facility-specific targeting
- Company investment allocation
- Regulatory allocation by company

---

## Next Steps

### Immediate Actions:

1. ✅ Document this validation issue
2. ⏳ Decide if company-level accuracy is needed
3. ⏳ If yes, implement weighted allocation fix
4. ⏳ Re-run analysis with corrected data

### Future Improvements:

1. Obtain real facility database
2. Validate all company emissions against ESG reports
3. Include facility-level production data
4. Add company-specific technology constraints

---

## Conclusion

**Total Industry Level:** The model is **VALID** for total Korean petrochemical industry analysis (52 MtCO2).

**Company Level:** The model is **NOT VALID** for company-specific analysis due to random facility allocation.

**Recommendation:**
- ✅ Use current model for industry-wide policy and technology analysis
- ❌ Do NOT use for company rankings or benchmarking
- 🔧 Fix company allocation if company-level analysis is required

The core analytical framework is sound, but data generation needs improvement for company-level accuracy.

---

**Report Date:** October 2025
**Model Version:** v2.0
**Status:** Total emissions validated ✅ / Company distribution needs correction ⚠️
