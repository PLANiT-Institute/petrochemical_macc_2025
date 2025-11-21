# Simplified Stranded Asset Model - Summary

## What I Built

A **pure emission-path driven retirement model** that calculates stranded assets based solely on whether facilities can meet emission reduction targets.

### Core Logic:
```
IF facility's required emission reduction > threshold (80-90%)
THEN facility RETIRES
ELSE facility continues with technology deployment

Stranded Asset = Book Value of Retired Facilities
```

### What's Included:
✅ Book value calculation (depreciation-based)
✅ Emission path analysis (2030, 2040, 2050)
✅ Retirement decision based on reduction threshold
✅ Facility-level detail by scenario
✅ New Streamlit dashboard (`dashboard_stranded_assets.py`)

### What's NOT Included (as requested):
❌ Carbon pricing
❌ Physical climate risk
❌ Retrofit costs
❌ Operational losses

---

## Current Results

### Key Finding: **NO FACILITIES RETIRE**

Under the current methodology, **0 facilities retire** across all scenarios because:

1. **Proportional Distribution**: Emission reduction requirements are distributed proportionally across all facilities
2. **Equal Burden**: All facilities face the same % reduction (e.g., 63.9% in Shaheen scenario)
3. **Below Threshold**: Even maximum reduction (66.7% in Restructure 40%) < 80% threshold

### Example (Shaheen Scenario):
- **Target**: 25.2 MtCO2 (vs BAU 68.0)
- **Required Reduction**: 42.8 MtCO2 (**63.9%**)
- **Per-Facility Reduction**: **63.9%** (identical for all)
- **Facilities Retired**: **0** (all below 80% threshold)
- **Stranded Assets**: **$0**

---

## Why This Happens: Distribution Methodology

Current approach:
```python
# Proportional distribution
facility_reduction_required = (facility_emissions / total_emissions) × total_reduction_needed
```

Result: **All facilities face identical % reduction**

---

## Alternative Approaches to Drive Retirement

To get realistic retirement based on emission paths, you need **differential treatment**:

### Option 1: **Prioritize High-Emission Facilities**
Oldest/dirtiest facilities face higher reduction requirements:

```python
# Weight by emission intensity
facility_weight = emission_intensity^2 / Σ(emission_intensity^2)
facility_reduction = facility_weight × total_reduction
```

**Result**: High-emission facilities (old crackers) forced to retire first

### Option 2: **Age-Based Retirement**
Facilities beyond a certain age must retire if emission target is stringent:

```python
if facility_age > 25 AND required_sector_reduction > 60%:
    RETIRE
```

**Result**: Old facilities with remaining book value → stranded assets

### Option 3: **Cost-Effectiveness Threshold**
Facilities where retrofit cost > remaining book value → retire:

```python
retrofit_cost = abatement × technology_capex
if retrofit_cost > book_value × α:  # α = threshold (e.g., 2.0)
    RETIRE
```

**Result**: Economically unviable retrofits → retirement

### Option 4: **Technology Incompatibility**
Some facilities cannot deploy certain technologies:

```python
if facility_type == "old_cracker" AND tech_required == "NCC-Electricity":
    RETIRE  # Cannot retrofit
```

**Result**: Technology-incompatible facilities → stranded

### Option 5: **Cumulative Budget Approach**
Cheapest abatement deployed first, most expensive facilities close:

```python
# Rank by abatement cost ($/tCO2)
# Deploy until budget exhausted
# Remaining high-cost facilities → RETIRE
```

**Result**: Cost-driven retirement

---

## Recommended Approach for Your Research

Based on your focus on **emission path driving retirement**, I recommend:

### **Hybrid: Age + Emission Intensity**

```python
# Retirement logic
retirement_score = (facility_age / max_age) × 0.5 +
                  (emission_intensity / max_intensity) × 0.5

if retirement_score > threshold AND required_reduction > 60%:
    RETIRE
```

**Why this works:**
1. **Emission-path driven**: Stringent targets increase retirement
2. **Realistic**: Old, dirty facilities close first
3. **Stranded assets**: Captures remaining book value loss
4. **Policy-relevant**: Mirrors real-world phase-out patterns

---

## How to Implement Different Approach

I can modify the `_analyze_retirement_timeline()` function in `stranded_assets_simple.py` to use any of these approaches. Which would you prefer?

---

## Current Model Files

### Analysis Module:
- `modules/stranded_assets_simple.py` - Core logic
- `run_stranded_assets_simple.py` - Runner script

### Outputs (even with 0 retirements):
- `facility_book_values.csv` - Asset valuation for all 248 facilities
- `stranding_summary_timeline.csv` - Timeline by scenario
- `facility_retirement_*.csv` - Facility-level detail per scenario
- Visualizations (PNG charts)

### Dashboard:
- `dashboard_stranded_assets.py` - New Streamlit dashboard

**Run dashboard:**
```bash
streamlit run dashboard_stranded_assets.py
```

---

## Next Steps - Your Decision

**Option A**: Keep current proportional distribution
- Useful for: Showing that **emission targets don't force retirement** if technology deployment is possible
- Insight: Technology investment avoids stranded assets

**Option B**: Implement differential retirement logic
- I can modify the code to use any of the 5 approaches above
- Will generate realistic stranded asset estimates

**Option C**: Add multiple retirement scenarios
- Run analysis with different retirement logics
- Compare stranded assets under different assumptions

---

## Questions for You

1. **What should drive retirement?**
   - Age + emission intensity?
   - Cost-effectiveness?
   - Technology compatibility?
   - Cumulative carbon budget?

2. **What's the threshold?**
   - Should old facilities always close under stringent targets?
   - Or should cost determine retirement?

3. **Research objective?**
   - Show that technology avoids stranding?
   - Or quantify unavoidable stranded assets?

Let me know which approach you'd like, and I'll implement it immediately!
