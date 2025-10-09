# RE PPA Implementation Summary

**Status**: ✅ **COMPLETE** - RE PPA successfully integrated into the MACC model

## What Was Implemented

### 1. Renewable Energy as PPA (Power Purchase Agreement)
- **Simple procurement model**: Grid electricity vs RE electricity purchase
- **No infrastructure modeling**: No capacity/CAPEX - just price differential
- **Cost-competitive deployment**: RE PPA competes in MACC with other technologies

### 2. Technology Applicability
**User specification**: "RE is only applied to NCC"

- RE PPA restricted to **NCC facilities only** (41 facilities)
- BTX facilities (47 facilities) were analyzed and found to use electricity (39/47 facilities, 46.2 kWh/tonne)
- However, per user requirement, RE PPA only applies to NCC

### 3. Key Results (Moderate_2050 Scenario)

#### RE PPA Economics (2025)
- **Cost**: -$105/tCO2 (cost-saving!)
- **Abatement potential**: 7.2 MtCO2 (NCC electricity emissions)
- **Grid price**: $100/MWh
- **RE PPA price**: $58/MWh
- **Result**: RE is cheaper than grid electricity

#### RE PPA Economics (2050)
- **Cost**: -$131/tCO2 (increasing savings!)
- **Abatement potential**: 7.1 MtCO2
- **Grid price**: $100/MWh
- **RE PPA price**: $52.8/MWh
- **Result**: RE becomes even more attractive

#### Technology Deployment (Moderate_2050)
| Year | Heat Pump | NCC-H2 | NCC-Elec | RE PPA | Total |
|------|-----------|--------|----------|--------|-------|
| 2025 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 2030 | 0.0 | 0.0 | 0.0 | 5.3 | 5.3 |
| 2035 | 3.5 | 0.0 | 0.0 | 7.0 | 10.5 |
| 2040 | 3.9 | 7.0 | 0.0 | 6.9 | 17.8 |
| 2045 | 3.9 | 16.4 | 0.0 | 6.7 | 27.0 |
| 2050 | 3.9 | 27.9 | 0.0 | 6.5 | 38.3 |

**Key finding**: RE PPA is deployed FIRST in every scenario because it has negative cost (saves money)

### 4. H2 Consumption Tracking

Added hydrogen consumption tracking for NCC-H2 deployment:

| Year | NCC-H2 Abatement (MtCO2) | H2 Consumption (kt H2/year) |
|------|--------------------------|------------------------------|
| 2040 | 7.0 | 3.9 |
| 2045 | 16.4 | 9.2 |
| 2050 | 27.9 | 15.6 |

**Conversion factor**: ~559 kg H2 per tCO2 abated
**Peak H2 demand (2050)**: 15.6 kt H2/year

### 5. Emission Scenarios (Relaxed)

Updated emission constraints to be ~50% more generous:

| Scenario | 2030 Target | 2050 Target | Description |
|----------|-------------|-------------|-------------|
| Moderate_2050 | 46 Mt (12% reduction) | 10 Mt (81% reduction) | Realistic decarbonization |
| Korea_NDC_Relaxed | 46 Mt (12% reduction) | 15 Mt (71% reduction) | More achievable NDC |
| Gradual_Path | 48 Mt (8% reduction) | 20 Mt (62% reduction) | Conservative path |
| Budget_1200Mt | - | - | 1200 MtCO2 cumulative |
| Budget_1000Mt | - | - | 1000 MtCO2 cumulative |
| Budget_800Mt | - | - | 800 MtCO2 cumulative |

## Files Modified

### Data Files
1. **`data/emission_scenarios_template.csv`** - Added 6 relaxed scenarios
2. **`data/technology_parameters.csv`** - Added Renewable_Energy technology

### Module Files
3. **`modules/macc.py`**
   - Added `_calculate_re_ppa_macc()` method (line 218-274)
   - Integrated RE PPA into `calculate_macc_annual()` (line 82-85)
   - Updated visualizations for RE_PPA (line 296, 323)

4. **`modules/optimization.py`**
   - Added RE_PPA to deployment dict (line 112, 171)
   - Added `'re_ppa_mt'` to output columns (line 129, 211)
   - Added H2 consumption tracking (line 122-125, 210-212)
   - Updated visualizations for RE_PPA (line 232-234)
   - Added RE_PPA to scenario comparison (line 311)

## Technical Details

### RE PPA Calculation Logic

```python
def _calculate_re_ppa_macc(self, year, re_price, grid_ef):
    """
    Calculate RE PPA MACC (NCC facilities only)

    Simple procurement: Grid vs RE electricity
    No CAPEX/OPEX - just price difference
    """
    # Get grid electricity price
    grid_price = electricity_price * 1000  # $/MWh

    # Filter NCC facilities only (user constraint)
    ncc_facilities = df[df['product'].apply(is_ncc_facility)]

    # Calculate abatement potential
    total_elec_emissions_mt = ncc_facilities['emissions_electricity_kt'].sum() / 1000

    # Emission factors
    re_ef = 0.05  # tCO2/MWh (lifecycle)
    grid_ef = grid_ef_tco2_per_mwh  # tCO2/MWh (trajectory)

    # Abatement per MWh
    abatement_per_mwh = grid_ef - re_ef

    # Cost per tCO2
    cost_per_tco2 = (re_price - grid_price) / abatement_per_mwh

    return cost_per_tco2  # Negative = saves money!
```

### H2 Consumption Calculation

```python
# From naphtha cracker energy balance:
# 1 tCO2 from naphtha = 67.11 GJ naphtha (at 0.0149 tCO2/GJ)
# 1 GJ naphtha replaced by H2 = 1/120 GJ H2 = 8.33 kg H2 (at 120 MJ/kg)
# Therefore: 1 tCO2 abated = 67.11 * 8.33 = 559 kg H2

kg_h2_per_tco2 = (1 / 0.0149) / 120 * 1000  # ~559 kg H2/tCO2
h2_consumption_kt = ncc_h2_deployment_mt * kg_h2_per_tco2 / 1000
```

## Outputs Generated

### MACC Analysis (Module 2)
- `outputs/module_02/macc_annual_2025_2050.csv` - Includes RE_PPA technology
- `outputs/module_02/macc_curve_YYYY.png` - RE_PPA in orange (#F39C12)
- `outputs/module_02/cost_evolution_annual.png` - RE_PPA cost trajectory

### Optimization (Module 3)
- `outputs/module_03/*_deployment.csv` - Includes `re_ppa_mt` and `h2_consumption_kt` columns
- `outputs/module_03/deployment_*.png` - RE_PPA in orange on stack plots
- `outputs/module_03/scenario_comparison.csv` - Includes `total_re_ppa_2050_mt`

## Key Findings

1. **RE PPA is the cheapest technology** - Negative cost from day 1
2. **RE PPA deployed first** - Optimizer prioritizes cost-saving technologies
3. **Limited by NCC electricity** - Only 7.2 Mt potential (NCC facilities only)
4. **H2 demand is modest** - Peak 15.6 kt/year in 2050 (achievable scale)
5. **Technology mix in 2050**:
   - RE PPA: 6.5 Mt (17% of abatement)
   - NCC-H2: 27.9 Mt (73% of abatement)
   - Heat Pump: 3.9 Mt (10% of abatement)

## Next Steps

### Potential Extensions
1. **Expand RE to BTX facilities** - If user wants to test sensitivity
2. **Add facility-level allocation** - Show which of 248 facilities get which technologies
3. **Update Streamlit dashboard** - Add RE PPA to interactive visualizations
4. **Add RE capacity modeling** - If client wants infrastructure details later

### For Dashboard
- Add RE PPA trace to technology deployment charts
- Show H2 consumption as separate metric
- Compare scenarios with/without RE

## BTX Facility Analysis (For Reference)

User specified "RE is only applied to NCC" but for completeness:

**BTX Electricity Usage:**
- 47 BTX facilities total
- 39/47 use electricity (83%)
- Mean: 46.2 kWh/tonne (84% of NCC level)
- BTX uses NO naphtha (0.0 GJ/tonne)

**If RE were expanded to BTX:**
- Additional potential: ~6.5 MtCO2 (50% more abatement)
- Total RE potential: ~13.7 MtCO2
- Same negative cost economics

## Model Validation

✅ **Module 1** - Baseline runs successfully
✅ **Module 2** - MACC includes RE_PPA with correct calculations
✅ **Module 3** - Optimization deploys RE_PPA in cost order
✅ **Module 4** - Financial analysis incorporates RE_PPA costs
✅ **Full run** - All 4 modules complete in ~10-15 seconds

**Total runtime**: ~10-15 seconds for complete analysis
