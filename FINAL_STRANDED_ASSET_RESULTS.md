# Final Stranded Asset Analysis Results
## Age-Based Retirement with Emission Path

**Date:** 2025-11-20
**Model:** Simplified Stranded Asset Model (Emission-Path Driven)

---

## Summary

Successfully implemented **age-based retirement logic** where stringent emission reduction targets force closure of old, high-emission facilities.

### Key Results (2050):

| Scenario | Facilities Retired | Stranded Value | Capacity Lost | Emissions Reduced |
|----------|-------------------|----------------|---------------|-------------------|
| All scenarios | **5 facilities** | **$210.4M** | **1,820 kt/year** | **4.3 MtCO2** |

**Stranding Rate:** 1.32% of total book value ($15.9B)

---

## Retired Facilities

The same 5 facilities retire across all scenarios (due to similar stringency levels 62-67%):

| Company | Location | Product | Built | Age | Book Value |
|---------|----------|---------|-------|-----|------------|
| Lotte Chemical | Daesan | Propylene | 1997 | 28 yrs | $44.0M |
| SK Energy | Ulsan | Propylene | 1996 | 29 yrs | $24.8M |
| Taekwang Industrial | Ulsan | Propylene | 1997 | 28 yrs | $24.0M |
| Lotte Chemical | Daesan | Butadiene | 1997 | 28 yrs | $15.2M |
| Lotte Chemical | Yeosu | Butadiene | 2011 | 14 yrs | $102.4M |

**Total Stranded:** $210.4M

**Pattern:** Old propylene and butadiene plants with remaining book value

---

## Retirement Logic

### Age-Based Risk Score:
```
Retirement Risk = (Age / Max_Age) × 0.6 + (Emission Intensity / Max_Intensity) × 0.4
```

### Adaptive Threshold (Emission-Path Driven):
```
IF stringency > 60% reduction:  threshold = 0.50 (aggressive retirement)
IF stringency > 50%:            threshold = 0.60 (moderate retirement)
ELSE:                           threshold = 0.75 (minimal retirement)
```

### Current Scenarios:
- **Shaheen**: 62.9% reduction → threshold = 0.50
- **Restructure 25%**: 61.9% reduction → threshold = 0.50
- **Restructure 40%**: 66.7% reduction → threshold = 0.50

All scenarios trigger aggressive retirement threshold.

---

## Why These Facilities?

1. **Age**: 14-29 years old (approaching end of 30-year lifetime)
2. **Book Value**: Still have remaining value to strand
3. **Products**: Propylene and Butadiene (downstream, not crackers)
4. **Emission Intensity**: Above median

**Note:** Old naphtha crackers (1979-1992) have **zero book value** (fully depreciated) → no stranding even if they close

---

## Insights

### 1. Limited Stranding Despite Aggressive Targets
- Only **5 of 248 facilities** (2%) forced to retire
- Only **$210M of $15.9B** (1.3%) stranded
- **Why?** Most old facilities already fully depreciated

### 2. Book Value Matters More Than Age
- **Yeochon NCC** (built 1979, age 46) → $0 book value → no stranding
- **Lotte Butadiene** (built 2011, age 14) → $102M book value → $102M stranded!

### 3. Emission Path Drives Threshold, Not Individual Facility Fate
- 62-67% sector reduction → forces retirement of 50th percentile risk
- Same 5 facilities across all scenarios
- More aggressive targets would retire more (lower threshold)

---

## Comparison with Original Model

| Aspect | Original Model | Simplified Model |
|--------|---------------|------------------|
| **Stranding Source** | Retirement + Retrofit + Operational | Retirement only |
| **Total Stranded (2050)** | $16.7B - $32.8B | $0.21B |
| **Facilities Retired** | 31-59 facilities | 5 facilities |
| **Retirement Driver** | >80% abatement requirement | Age + emission intensity |
| **Includes Retrofit Costs?** | Yes ($10-22B) | No |

**Key Difference:** Original model counted **retrofit CAPEX as stranding** (facilities continue but need massive investment). Simplified model counts only **premature closure**.

---

## Dashboard

New Streamlit dashboard available:

```bash
streamlit run dashboard_stranded_assets.py
```

**Features:**
- Timeline analysis (2030-2050)
- Scenario comparison
- Facility-level retirement detail
- Regional/sectoral breakdown
- Interactive visualizations

---

## Methodology Documentation

### Assumptions:
- **Facility lifetime:** 30 years
- **Depreciation:** Straight-line
- **Capital intensity:**
  - Naphtha Cracker: $1.2M/kt
  - Aromatics: $0.8M/kt
  - Polymer: $0.6M/kt
  - Other: $0.4M/kt
- **Retirement threshold:** Age (60%) + Intensity (40%)
- **Emission stringency levels:** 50%, 60% determine threshold

### What's NOT Included:
❌ Carbon pricing
❌ Physical climate risk
❌ Retrofit costs
❌ Operational losses
❌ Competitive dynamics

### What IS Included:
✅ Age-based retirement
✅ Emission intensity
✅ Emission path stringency
✅ Book value calculation
✅ Facility-level detail

---

## Files Generated

### Analysis Outputs:
- `facility_book_values.csv` - All 248 facilities with valuations
- `stranding_summary_timeline.csv` - Results for 2030, 2040, 2050
- `stranding_summary_2050.csv` - Final year summary
- `facility_retirement_*.csv` - Facility-level detail per scenario (6 files)

### Visualizations:
- `stranded_assets_emission_path.png` - Timeline chart
- `stranding_rate_comparison.png` - Scenario comparison

### Location:
```
outputs/module_04_stranded_assets_simple/
```

---

## How to Adjust Retirement Behavior

Want more/fewer retirements? Modify in `modules/stranded_assets_simple.py`:

### Make Retirement More Aggressive:
```python
# Line 205-210: Lower thresholds
if stringency_factor > 0.6:
    retirement_threshold = 0.40  # More aggressive (currently 0.50)
elif stringency_factor > 0.5:
    retirement_threshold = 0.50  # More aggressive (currently 0.60)
```

### Change Age vs Intensity Weight:
```python
# Line 193-196: Adjust weights (must sum to 1.0)
retirement_risk_score = (
    (facility_age / max_age) * 0.7 +           # Increase age weight
    (emission_intensity / max_intensity) * 0.3  # Decrease intensity weight
)
```

### Add New Retirement Criteria:
```python
# Add after line 216:
df_facilities['must_retire'] = (
    (df_facilities['retirement_risk_score'] >= retirement_threshold) &
    (df_facilities['remaining_life'] > 0) &
    (df_facilities['capacity_kt'] < 500)  # NEW: Only small facilities
)
```

---

## Research Applications

### Policy Analysis:
1. **Transition support needs:** $210M required to compensate stranded assets
2. **Regional impact:** Daesan (2) and Ulsan (2) most affected
3. **Product vulnerability:** Propylene/Butadiene plants at risk

### Scenario Testing:
- Test different emission stringency levels
- Vary retirement thresholds
- Compare with technology-driven scenarios

### Extensions:
1. Add temporal dynamics (year-by-year retirement)
2. Include technology compatibility constraints
3. Model competitive market dynamics
4. Add regional policy variations

---

## Conclusion

**Pure emission-path driven retirement model shows:**
- ✅ Modest stranding ($210M / 1.3%) under current logic
- ✅ Primarily affects older downstream facilities
- ✅ Most old facilities already fully depreciated
- ✅ Emission target stringency drives retirement threshold

**This contrasts with retrofit-inclusive models showing:**
- 📊 Major stranding ($17-33B) when retrofit costs included
- 📊 Technology investment creates "economic stranding"
- 📊 Different policy implications (support technology vs compensate closures)

**Your model is ready for:**
- Dashboard visualization
- Scenario sensitivity analysis
- Policy recommendation development
- Academic paper / policy brief

---

**Contact:** Review `STRANDED_ASSET_SIMPLIFIED_SUMMARY.md` for detailed methodology and alternative approaches.
