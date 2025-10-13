# User Guide: Adjusting Technology Cost Assumptions
## Korean Petrochemical MACC Model v2.1

**Date:** 2025-01-13
**Audience:** Model users who want to test different cost scenarios

---

## Quick Start

**To adjust technology costs:**
1. Edit CSV files in `data/` folder
2. Re-run the model
3. View updated results in dashboard

**Two types of technologies:**
- **Traditional (Heat Pump, RE PPA):** Edit `technology_parameters.csv`
- **Novel (NCC-Electricity, NCC-H2):** Edit `ncc_lcoe_trajectory.csv`

---

## Table of Contents

1. [Which File to Edit](#1-which-file-to-edit)
2. [Editing Traditional Technologies](#2-editing-traditional-technologies)
3. [Editing NCC Technologies (LCOE)](#3-editing-ncc-technologies-lcoe)
4. [Common Scenarios](#4-common-scenarios)
5. [Validation and Sanity Checks](#5-validation-and-sanity-checks)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Which File to Edit?

### Decision Tree

```
Is it NCC-Electricity or NCC-H2?
│
├─ YES → Edit ncc_lcoe_trajectory.csv
│   (These use LCOE methodology)
│
└─ NO → Edit technology_parameters.csv
    (Heat Pump, RE PPA use traditional CAPEX+OPEX)
```

### File Locations

```
data/
├── technology_parameters.csv        ← Heat Pump, RE PPA
├── ncc_lcoe_trajectory.csv         ← NCC-Electricity, NCC-H2
├── h2_price_trajectory.csv         ← H2 prices (affects NCC-H2)
└── re_price_trajectory.csv         ← RE prices (affects Heat Pump, NCC-Elec)
```

---

## 2. Editing Traditional Technologies

### File Format: `technology_parameters.csv`

```csv
technology,applies_to,cop,trl,available_year,capex_2025_musd_per_mtco2,capex_2030_musd_per_mtco2,capex_2040_musd_per_mtco2,capex_2050_musd_per_mtco2,opex_pct_capex,lifetime_years
Heat_Pump,All processes <165°C,4.0,9,2025,150,120,90,75,3.0,20
Renewable_Energy,All electricity consumers,,9,2025,180,140,100,80,1.5,25
```

### Parameters Explained

| Parameter | Unit | What it Means | Typical Range |
|-----------|------|---------------|---------------|
| `technology` | - | Technology name (DO NOT CHANGE) | - |
| `cop` | - | Coefficient of Performance (Heat Pump only) | 3.0-5.0 |
| `trl` | 1-9 | Technology Readiness Level | 6-9 |
| `available_year` | year | When technology becomes available | 2025-2035 |
| `capex_YEAR_musd_per_mtco2` | M$/MtCO2 | Capital cost per MtCO2 abatement capacity | 50-300 |
| `opex_pct_capex` | % | Annual operating cost as % of CAPEX | 1-5% |
| `lifetime_years` | years | Technology lifespan | 15-30 |

### Example 1: More Optimistic Heat Pump Costs

**Scenario:** Heat pump costs fall faster due to mass production

**Current values:**
```csv
Heat_Pump,...,150,120,90,75,...
```

**Optimistic scenario (30% cost reduction):**
```csv
Heat_Pump,...,105,84,63,52.5,...
```

**Impact:**
- Heat pumps become MORE attractive
- Deployed earlier and more extensively
- Higher savings in optimization

### Example 2: Conservative Heat Pump Costs

**Scenario:** Heat pumps face higher costs in industrial applications

**Current values:**
```csv
Heat_Pump,...,150,120,90,75,...
```

**Conservative scenario (20% cost increase):**
```csv
Heat_Pump,...,180,144,108,90,...
```

**Impact:**
- Heat pumps less attractive
- May deploy NCC technologies earlier instead
- Lower overall cost savings

### Example 3: Changing Heat Pump Efficiency (COP)

**Current value:**
```csv
Heat_Pump,All processes <165°C,4.0,...
```

**Higher efficiency (COP 5.0):**
```csv
Heat_Pump,All processes <165°C,5.0,...
```

**What this means:**
- 1 kWh electricity replaces 5 GJ thermal (instead of 4 GJ)
- BIGGER fuel cost savings
- Heat pumps become MORE competitive

**Lower efficiency (COP 3.0):**
```csv
Heat_Pump,All processes <165°C,3.0,...
```

**What this means:**
- Less energy efficient
- SMALLER fuel cost savings
- Heat pumps less competitive

### Example 4: Delaying Technology Availability

**Current value:**
```csv
Heat_Pump,...,2025,...
```

**Delayed commercialization:**
```csv
Heat_Pump,...,2028,...
```

**Impact:**
- Heat pump cannot be deployed 2025-2027
- Model will use other technologies during this period
- May increase total costs

---

## 3. Editing NCC Technologies (LCOE)

### File Format: `ncc_lcoe_trajectory.csv`

```csv
year,baseline_steam_cracker_usd_per_ton,ncc_electricity_usd_per_ton,ncc_h2_usd_per_ton,baseline_emission_intensity_tco2_per_ton,ncc_electricity_emission_intensity_tco2_per_ton,ncc_h2_emission_intensity_tco2_per_ton
2025,746,743,850,0.869,0.806,0.900
2030,746,730,750,0.869,0.726,0.650
2040,746,710,600,0.869,0.566,0.300
2050,746,690,500,0.869,0.406,0.100
```

### Parameters Explained

| Parameter | Unit | What it Means |
|-----------|------|---------------|
| `baseline_steam_cracker_usd_per_ton` | $/ton | Cost of conventional naphtha cracking |
| `ncc_electricity_usd_per_ton` | $/ton | Cost of electric cracking |
| `ncc_h2_usd_per_ton` | $/ton | Cost of hydrogen cracking |
| `baseline_emission_intensity_tco2_per_ton` | tCO2/ton | Conventional emissions |
| `ncc_electricity_emission_intensity_tco2_per_ton` | tCO2/ton | Electric cracker emissions |
| `ncc_h2_emission_intensity_tco2_per_ton` | tCO2/ton | H2 cracker emissions |

### Example 1: Faster NCC-Electricity Cost Reduction

**Scenario:** Electric crackers achieve economies of scale faster

**Current 2030-2050 values:**
```csv
2025,746,743,850,...
2030,746,730,750,...
2040,746,710,600,...
2050,746,690,500,...
```

**Optimistic scenario (faster learning curve):**
```csv
2025,746,743,850,...
2030,746,710,750,...  ← 2030 price drops to 2040 level
2040,746,680,600,...  ← Continued fast reduction
2050,746,650,500,...  ← Even cheaper than baseline!
```

**Impact:**
- NCC-Electricity becomes cost-competitive earlier (2030 instead of 2035)
- More deployment of electric crackers
- Less reliance on H2 pathway

### Example 2: H2 Price Assumptions

**Scenario:** Green H2 remains expensive longer

**Current H2 cracker costs:**
```csv
2025,...,850,...
2030,...,750,...  ← Big drop expected
2040,...,600,...
2050,...,500,...
```

**Pessimistic H2 scenario:**
```csv
2025,...,850,...
2030,...,800,...  ← Slower decline
2040,...,700,...  ← Still expensive
2050,...,600,...  ← Never reaches parity
```

**Impact:**
- NCC-H2 deployment delayed or avoided
- Model will prefer NCC-Electricity instead
- Different technology mix in optimization

### Example 3: Baseline Cost Inflation

**Scenario:** Conventional crackers become more expensive (carbon price, regulations)

**Current baseline:**
```csv
2025,746,...,0.869,...
2030,746,...,0.869,...  ← Constant at $746
2040,746,...,0.869,...
2050,746,...,0.869,...
```

**With carbon price ($100/tCO2 by 2050):**
```csv
2025,746,...,0.869,...
2030,790,...,0.869,...  ← +$44 (0.869 × $50 carbon price)
2040,830,...,0.869,...  ← +$84 (0.869 × $100)
2050,867,...,0.869,...  ← +$121 (0.869 × $140)
```

**Impact:**
- Makes NCC technologies MORE attractive
- Deployment happens earlier
- Larger emissions reductions

### Example 4: Optimistic NCC Emissions

**Scenario:** Electric crackers achieve near-zero emissions with 100% RE

**Current emission intensities:**
```csv
...,baseline_emission_intensity_tco2_per_ton,ncc_electricity_emission_intensity_tco2_per_ton,...
...,0.869,0.806,...  ← 2025
...,0.869,0.726,...  ← 2030
...,0.869,0.566,...  ← 2040
...,0.869,0.406,...  ← 2050
```

**Near-zero emissions scenario:**
```csv
...,0.869,0.700,...  ← 2025 (slightly better)
...,0.869,0.400,...  ← 2030 (much cleaner grid)
...,0.869,0.200,...  ← 2040 (mostly RE)
...,0.869,0.050,...  ← 2050 (near-zero)
```

**Impact:**
- LARGER abatement per cracker
- MORE attractive MACC cost (same cost, more abatement)
- Faster decarbonization possible

---

## 4. Common Scenarios

### Scenario A: Optimistic Technology Development

**Goal:** Test best-case cost reductions

**Changes needed:**
```
1. technology_parameters.csv:
   - Heat Pump CAPEX: -30% across all years
   - RE PPA CAPEX: -25% across all years

2. ncc_lcoe_trajectory.csv:
   - NCC-Electricity costs drop faster (reach 2050 values by 2040)
   - NCC-H2 costs drop faster (H2 at $2/kg by 2040)

3. h2_price_trajectory.csv:
   - Accelerate H2 cost decline (reach $1.5/kg by 2040)
```

**Expected result:**
- All technologies deploy earlier
- Much lower total cost
- Easier to meet aggressive emission targets

### Scenario B: Conservative / Pessimistic

**Goal:** Test worst-case cost increases

**Changes needed:**
```
1. technology_parameters.csv:
   - Heat Pump CAPEX: +25% across all years
   - Reduce COP from 4.0 → 3.5 (lower efficiency)

2. ncc_lcoe_trajectory.csv:
   - NCC-Electricity: slower cost reduction
   - NCC-H2: stays expensive ($700/ton in 2050)

3. Delay availability:
   - NCC-Electricity: 2032 instead of 2030
   - NCC-H2: 2035 instead of 2030
```

**Expected result:**
- Slower decarbonization
- Higher total costs
- May fail to meet aggressive targets

### Scenario C: Carbon Price Impact

**Goal:** Model explicit carbon pricing

**Changes needed:**
```
1. ncc_lcoe_trajectory.csv:
   Add carbon price to baseline:

   year,baseline_steam_cracker_usd_per_ton,...
   2025,746 + (0.869 × 20) = 763.4,...     ← $20/tCO2 carbon price
   2030,746 + (0.869 × 50) = 789.5,...     ← $50/tCO2
   2040,746 + (0.869 × 100) = 832.9,...    ← $100/tCO2
   2050,746 + (0.869 × 150) = 876.4,...    ← $150/tCO2
```

**Expected result:**
- All low-carbon technologies become MORE attractive
- Deployment accelerates
- Net cost may still be positive (paying for carbon)

### Scenario D: Renewable Energy Cost Sensitivity

**Goal:** Test impact of RE price assumptions

**Changes needed:**
```
1. re_price_trajectory.csv:
   Current: 80 → 50 $/MWh (2025 → 2050)

   Optimistic: 70 → 30 $/MWh (cheaper RE)
   Pessimistic: 100 → 70 $/MWh (more expensive RE)
```

**Expected result:**
- Affects Heat Pump fuel cost savings
- Affects NCC-Electricity operating costs
- Changes relative attractiveness of technologies

---

## 5. Validation and Sanity Checks

### After Editing, Check These

**1. CAPEX Trends (technology_parameters.csv)**
```
✓ CAPEX should DECREASE over time (learning curve)
✗ Don't have CAPEX increase over time (unless special reason)

Example:
✓ 150, 120, 90, 75     ← Good (declining)
✗ 150, 120, 130, 140   ← Bad (increases later)
```

**2. LCOE Trends (ncc_lcoe_trajectory.csv)**
```
✓ Technology LCOE should decrease (usually)
✓ Technology LCOE can be above baseline initially, then below
✗ Don't have baseline LCOE change (unless modeling carbon price)

Example NCC-Electricity:
✓ 743, 730, 710, 690   ← Good (declining towards parity)
✗ 743, 750, 760, 770   ← Bad (getting worse over time)
```

**3. Emission Intensities (ncc_lcoe_trajectory.csv)**
```
✓ Technology emissions should be LOWER than baseline
✓ Technology emissions should decrease (with grid decarbonization)
✗ Don't have technology emissions higher than baseline

Example:
✓ Baseline: 0.869, Technology: 0.406   ← Good (53% reduction)
✗ Baseline: 0.869, Technology: 0.950   ← Bad (increases emissions!)
```

**4. Run the Model and Check**
```bash
python run_module_02.py
```

**Look for:**
- MACC costs should be reasonable (-500 to +500 $/tCO2)
- Technologies should become cheaper over time
- No error messages about negative abatement

**Warning signs:**
```
MACC cost < -1000 $/tCO2  → Probably too optimistic
MACC cost > +1000 $/tCO2  → Technology won't deploy
Negative abatement        → ERROR in emission intensities
```

---

## 6. Troubleshooting

### Problem 1: Model Won't Run After Editing

**Error:** `KeyError: 'capex_2025_musd_per_mtco2'`

**Cause:** Column name typo or missing data

**Solution:**
```
1. Check CSV file has all required columns
2. No extra spaces in column names
3. All years present (2025, 2030, 2040, 2050)
```

### Problem 2: Weird Results (Extremely High/Low Costs)

**Symptom:** MACC shows -5000 $/tCO2 or +10000 $/tCO2

**Likely causes:**
```
1. Decimal point error
   - Entered 7.5 instead of 75 for CAPEX
   - Entered 0.004 instead of 4.0 for COP

2. Units mismatch
   - CAPEX is Million $/MtCO2, not $/tCO2
   - LCOE is $/ton product, not $/tCO2

3. Emission intensity error
   - Must be tCO2/ton product (0.4-0.9 range)
   - Not tCO2/GJ (would be 0.01-0.05 range)
```

**Solution:** Check units match original file

### Problem 3: Technologies Don't Deploy

**Symptom:** Optimization uses only Heat Pumps, ignores NCC

**Possible reasons:**
```
1. NCC costs too high → Lower LCOE values
2. NCC availability too late → Change available_year
3. Heat Pump too cheap → Increase Heat Pump CAPEX
4. Emission targets not aggressive enough → Try Aggressive scenario
```

### Problem 4: Model Says "Cannot Meet Target"

**Symptom:** Optimization fails with "insufficient abatement potential"

**Likely causes:**
```
1. Target too aggressive for available technologies
2. Technologies unavailable early enough
3. Abatement potential too low

Solutions:
- Relax emission targets
- Make technologies available earlier
- Increase technology abatement potential (check heat_pump_applicability.csv)
```

---

## 7. Best Practices

### DO:
✓ Make small changes and test
✓ Document your assumptions
✓ Compare results with baseline
✓ Validate against literature (if available)
✓ Keep backup copies of original files

### DON'T:
✗ Change technology names (code expects exact names)
✗ Delete columns (even if not using them)
✗ Mix units (CAPEX in $ instead of M$)
✗ Make all values the same year (breaks interpolation)
✗ Forget to re-run model after editing

### Workflow:
```
1. Copy original CSV → save as backup
2. Edit values in spreadsheet program (Excel, LibreOffice)
3. Save as CSV (UTF-8)
4. Run model: python run_module_02.py
5. Check outputs in outputs/module_02/
6. If good → proceed to optimization (run_module_03.py)
7. If bad → revert to backup and try again
```

---

## 8. Example: Complete Scenario Update

### Goal: Model EU-style carbon pricing + optimistic tech costs

**Step 1: Edit `ncc_lcoe_trajectory.csv`**

Add carbon price to baseline:
```csv
# OLD
year,baseline_steam_cracker_usd_per_ton,...
2025,746,...
2050,746,...

# NEW (with $200/tCO2 carbon price by 2050)
year,baseline_steam_cracker_usd_per_ton,...
2025,764,...  # 746 + (0.869 × 20)
2050,920,...  # 746 + (0.869 × 200)
```

**Step 2: Edit `technology_parameters.csv`**

Reduce Heat Pump CAPEX by 25%:
```csv
# OLD
Heat_Pump,...,150,120,90,75,...

# NEW
Heat_Pump,...,112.5,90,67.5,56.25,...
```

**Step 3: Run Model**
```bash
python run_all.py
```

**Step 4: Check Results**
```
Open: outputs/module_02/macc_curve_2030.png
Expect: All technologies shift down (more attractive)

Open: outputs/module_03/scenario_comparison.csv
Expect: Lower total costs, earlier deployment
```

---

## Quick Reference Card

### Common Edits Cheat Sheet

| Want to... | Edit this file | Change this parameter |
|------------|----------------|----------------------|
| Make Heat Pumps cheaper | `technology_parameters.csv` | `capex_YEAR_musd_per_mtco2` |
| Make Heat Pumps more efficient | `technology_parameters.csv` | `cop` |
| Make NCC-Elec cheaper | `ncc_lcoe_trajectory.csv` | `ncc_electricity_usd_per_ton` |
| Make NCC-H2 cheaper | `ncc_lcoe_trajectory.csv` | `ncc_h2_usd_per_ton` |
| Add carbon price | `ncc_lcoe_trajectory.csv` | `baseline_steam_cracker_usd_per_ton` |
| Make NCC cleaner | `ncc_lcoe_trajectory.csv` | `ncc_*_emission_intensity_tco2_per_ton` |
| Delay technology | `technology_parameters.csv` | `available_year` |
| Change RE price | `re_price_trajectory.csv` | `re_usd_per_mwh` |
| Change H2 price | `h2_price_trajectory.csv` | `h2_usd_per_kg` |

---

## Need Help?

**Common issues usually involve:**
1. Units mismatch
2. Decimal point errors
3. Missing columns after edit

**Check:**
- File format matches original exactly
- No extra spaces or special characters
- All required columns present
- Values are reasonable (not 10000x off)

**Still stuck?** Check error message and compare your edited file with the original backup.

---

## Appendix: File Templates

### Minimal `technology_parameters.csv`
```csv
technology,applies_to,cop,trl,available_year,capex_2025_musd_per_mtco2,capex_2030_musd_per_mtco2,capex_2040_musd_per_mtco2,capex_2050_musd_per_mtco2,opex_pct_capex,lifetime_years
Heat_Pump,All processes <165°C,4.0,9,2025,150,120,90,75,3.0,20
Renewable_Energy,All electricity consumers,,9,2025,180,140,100,80,1.5,25
```

### Minimal `ncc_lcoe_trajectory.csv` (key years only)
```csv
year,baseline_steam_cracker_usd_per_ton,ncc_electricity_usd_per_ton,ncc_h2_usd_per_ton,baseline_emission_intensity_tco2_per_ton,ncc_electricity_emission_intensity_tco2_per_ton,ncc_h2_emission_intensity_tco2_per_ton
2025,746,743,850,0.869,0.806,0.900
2030,746,730,750,0.869,0.726,0.650
2040,746,710,600,0.869,0.566,0.300
2050,746,690,500,0.869,0.406,0.100
```

**Note:** Model interpolates between these years, but you can add intermediate years for more control.

---

**Version:** 1.0
**Last Updated:** 2025-01-13
**Model Version:** 2.1
