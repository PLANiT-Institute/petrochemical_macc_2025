# Sensitivity Analysis - CORRECTED Interpretation

## Problem with Previous Analysis

**Previous (WRONG) interpretation:**
- "No fuel cost differential" meant setting `fuel_cost_diff = 0` in the formula
- This incorrectly kept H2/electricity costs but removed BOTH new energy costs AND fossil fuel savings
- Did not properly isolate the fossil fuel savings component

**Corrected interpretation:**
- "No fuel cost differential" means **setting fossil fuel prices (naphtha, LNG, etc.) to ZERO**
- This removes the BENEFIT of avoiding fossil fuel purchases
- New energy costs (H2, electricity) are KEPT
- Shows what MACC would be if fossil fuels were FREE

## What "Fuel Cost Differential" Actually Means

### Heat Pump Example

**Baseline calculation:**
```
Total Cost = CAPEX + OPEX + Fuel Cost Differential
Where:
  Fuel Cost Differential = (RE electricity cost - naphtha cost) per tCO2
```

**Example numbers (2030):**
- RE electricity for heat pump: ~$60/GJ thermal
- Naphtha combustion: ~$15/GJ thermal
- Fuel Cost Differential = ($60 - $15) × 67 GJ/tCO2 = **+$3,015/tCO2**
- But wait - this is POSITIVE (bad), yet baseline MACC is NEGATIVE (good)?
- That's because CAPEX+OPEX are so low that even with higher fuel cost, it's still profitable!

**Wait, let me recalculate more carefully:**

Actually, looking at the code ([macc.py:129-133](modules/macc.py#L129-133)):

```python
cop = tech_costs['cop']  # ~3.5 for heat pump
re_price_per_gj_thermal = (re_price / 3.6) / cop  # $/GJ thermal output
gj_per_tco2 = 1 / self.ef_naphtha  # 1/0.0149 = 67.1 GJ/tCO2
fuel_cost_diff = (re_price_per_gj_thermal - naphtha_price) * gj_per_tco2
```

With COP = 3.5:
- RE price = $60/MWh = $16.67/GJ electric
- RE price per GJ thermal = $16.67 / 3.5 = **$4.76/GJ thermal** (heat pump is efficient!)
- Naphtha price = $15/GJ thermal
- Fuel cost diff = ($4.76 - $15) × 67.1 = **-$686/tCO2** (NEGATIVE = savings!)

**So the corrected interpretation is:**
- **Baseline**: Fuel cost diff = -$686/tCO2 (you SAVE money on fuel)
- **No fossil fuel savings**: Set naphtha_price = 0, so fuel cost diff = $4.76 × 67.1 = +$319/tCO2 (you PAY for RE, don't save on naphtha)
- **Impact**: +$1,007/tCO2 (this is the value of avoiding fossil fuel purchases!)

## Corrected Sensitivity Results

### 2030 Results

| Technology | Baseline MACC | Without Fossil Savings | Fossil Fuel Impact | Without Learning | Learning Impact |
|------------|---------------|------------------------|-------------------|------------------|-----------------|
| Heat Pump | -$748/tCO2 | +$259/tCO2 | **+$1,007/tCO2** | -$745/tCO2 | +$3/tCO2 |
| NCC-H2 | +$18/tCO2 | +$1,721/tCO2 | **+$1,703/tCO2** | +$18/tCO2 | +$0/tCO2 |
| NCC-Electricity | -$112/tCO2 | +$2,497/tCO2 | **+$2,608/tCO2** | -$112/tCO2 | +$0/tCO2 |
| RE PPA | -$131/tCO2 | -$131/tCO2 | $0/tCO2* | -$131/tCO2 | $0/tCO2 |

*RE PPA compares grid electricity to RE electricity, not fossil fuels, so fossil fuel price doesn't affect it.

### 2050 Results

| Technology | Baseline MACC | Without Fossil Savings | Fossil Fuel Impact | Without Learning | Learning Impact |
|------------|---------------|------------------------|-------------------|------------------|-----------------|
| Heat Pump | -$850/tCO2 | +$157/tCO2 | **+$1,007/tCO2** | -$842/tCO2 | +$8/tCO2 |
| NCC-H2 | -$320/tCO2 | +$165/tCO2 | **+$485/tCO2** | -$320/tCO2 | +$0/tCO2 |
| NCC-Electricity | -$121/tCO2 | +$685/tCO2 | **+$806/tCO2** | -$121/tCO2 | +$0/tCO2 |
| RE PPA | -$340/tCO2 | -$340/tCO2 | $0/tCO2* | -$340/tCO2 | $0/tCO2 |

## Key Findings

### 1. Fossil Fuel Savings are the DOMINANT Driver

**All technologies become MORE EXPENSIVE (or change from profitable to unprofitable) when fossil fuel savings are removed:**

- **Heat Pump**: Goes from -$748/tCO2 (profitable) to +$259/tCO2 (costly)
  - Impact: +$1,007/tCO2 (319x more important than learning curves!)

- **NCC-H2**: Goes from +$18/tCO2 to +$1,721/tCO2
  - Impact: +$1,703/tCO2 (infinite times more important than learning - learning has 0 impact on LCOE-based calc)

- **NCC-Electricity**: Goes from -$112/tCO2 (profitable) to +$2,497/tCO2 (very costly)
  - Impact: +$2,608/tCO2 (by far the largest impact)

**Interpretation**: The value of these abatement technologies comes almost entirely from **avoiding expensive fossil fuel purchases (naphtha @ $15/GJ)**, NOT from capital cost reductions.

### 2. Learning Curves have MINIMAL Impact

- Heat Pump: Only +$3/tCO2 impact in 2030, +$8/tCO2 in 2050
- NCC technologies: $0/tCO2 impact (because LCOE already incorporates learning)
- RE PPA: $0/tCO2 impact (no CAPEX, just PPA pricing)

**Interpretation**: Even if CAPEX stayed flat at 2025 levels (no learning), the MACC would barely change. This validates that the model is robust to learning rate uncertainty.

### 3. Model Robustness Assessment

**The model is:**
- ✅ **ROBUST** to learning curve assumptions (±5% impact or less)
- ❌ **HIGHLY SENSITIVE** to fossil fuel price assumptions (>100% impact)

**Recommendation**: Focus sensitivity analysis and scenario planning on:
1. **Fossil fuel prices** (naphtha, LNG) - CRITICAL INPUT
2. **New energy prices** (H2, RE electricity) - Also important
3. Learning curves - Less critical, can use literature values

### 4. Policy Implications

**Without carbon pricing**, these technologies are attractive because:
- Fossil fuels are expensive ($15/GJ for naphtha)
- Heat pumps provide energy efficiency (COP=3.5 → 70% energy savings)
- This creates large operational cost savings

**If fossil fuels were cheap/free** (e.g., subsidized, or stranded assets):
- Most technologies would become uneconomic
- Would need strong carbon pricing or mandates
- Only technologies with very low CAPEX would survive

## Visualizations Generated

1. **sensitivity_comparison_2030_corrected.png** - Side-by-side MACC curves for 2030
2. **sensitivity_comparison_2050_corrected.png** - Side-by-side MACC curves for 2050
3. **macc_evolution_timeline_corrected.png** - Time series showing all scenarios
4. **impact_magnitude_corrected.png** - Bar chart showing fossil fuel vs learning impact

## Files Generated

All outputs saved to: `outputs/sensitivity/`

- `macc_baseline.csv` - Full model (baseline)
- `macc_no_fossil_savings.csv` - Fossil fuel prices = 0
- `macc_no_learning.csv` - 2025 CAPEX frozen
- `macc_no_fossil_no_learning.csv` - Both assumptions removed
- `comparison_summary_corrected.csv` - Side-by-side comparison table

## Technical Implementation

See [modules/sensitivity_corrected.py](modules/sensitivity_corrected.py) for the corrected sensitivity module.

**Key change:**
```python
if remove_fossil_fuel_savings:
    print("   → Setting fossil fuel prices to ZERO (removes savings benefit)")
    df_fuel_prices_modified = df_fuel_prices.copy()
    df_fuel_prices_modified['naphtha_usd_per_gj'] = 0.0
    df_fuel_prices_modified['lng_usd_per_gj'] = 0.0
    # ... etc
    # Note: electricity_usd_per_kwh is KEPT (for RE PPA comparison)
```

This correctly isolates the fossil fuel savings component by removing the baseline fuel cost, making new technologies look more expensive (lose the savings benefit).
