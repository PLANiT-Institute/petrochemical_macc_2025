# Model Gaps Analysis & Redesign Plan

## 🚨 Critical Issues Identified

### 1. **No Energy Flow Visualization**
**Current Problem:**
- Model tracks energy consumption in GJ and kWh
- BUT: No visualization of energy flows
- Hydrogen input is calculated but not shown
- Cannot see where energy comes from or goes to

**Missing:**
- Energy Sankey diagrams
- Fuel input → Process → Emissions flow
- Technology impact on energy mix

---

### 2. **Renewable Energy (RE) Not Modeled**
**Current Problem:**
- Heat pumps assumed to use grid electricity
- NO tracking of renewable energy adoption
- Cannot model "grid electricity + RE" combinations
- RE price trajectory exists but not used properly

**Missing:**
- RE electricity generation capacity
- RE adoption scenarios (0%, 25%, 50%, 100%)
- Grid vs RE electricity split
- RE-specific emission factors (near zero)

---

### 3. **Shallow Energy Consumption Analysis**
**Current Problem:**
- Baseline tracks total energy per facility
- But process-level detail missing
- Heat pump electricity demand not separated
- Cannot analyze technology combinations per facility

**Missing:**
- Process heat requirements (by temperature)
- Electricity demand breakdown (process vs heat pump)
- Fuel substitution mapping (naphtha → H2)
- Technology applicability by process type

---

### 4. **No Facility-Level Technology Combinations**
**Current Problem:**
- Optimization deploys technologies in aggregate
- No visibility into which of 248 facilities get what
- Cannot see "Facility A: Heat Pump + 50% RE + H2 NCC"

**Missing:**
- Facility-level deployment matrix
- Technology combination chart (248 facilities × 3-5 technologies)
- Regional technology distribution maps
- Company-specific deployment patterns

---

## 📊 What Should Be Shown

### Energy Flow Diagram (Sankey)
```
[Naphtha] ──────────→ [NCC Process] ──→ [Ethylene] + [Emissions]
[Natural Gas] ───────→ [Boilers]     ──→ [Steam]    + [Emissions]
[Grid Electricity] ──→ [Equipment]   ──→ [Power]    + [Emissions]
[RE Electricity] ────→ [Heat Pumps]  ──→ [Heat]     + [Near Zero]
[H2 (Green)] ────────→ [NCC (H2)]    ──→ [Ethylene] + [Near Zero]
```

### Technology Deployment Matrix (248 × Technologies)
```
Facility | Heat Pump | H2-NCC | E-NCC | RE% | Grid% | Total Reduction
---------|-----------|---------|-------|-----|-------|----------------
LG-1     |    ✓      |   ✓    |   -   | 50% | 50%  |    5.2 MtCO2
LG-2     |    ✓      |   -    |   ✓   | 100%|  0%  |    3.1 MtCO2
Lotte-1  |    -      |   ✓    |   -   | 25% | 75%  |    4.8 MtCO2
...
```

---

## 🔧 Required Model Enhancements

### Enhancement 1: Energy Flow Tracking
**Add to baseline module:**

```python
class EnergyFlowTracker:
    """Track all energy inputs and outputs"""

    def calculate_energy_balance(facility):
        return {
            # Inputs
            'fossil_fuel_input_gj': {...},
            'grid_electricity_input_kwh': {...},
            're_electricity_input_kwh': {...},
            'h2_input_kg': {...},

            # Outputs
            'product_output_kt': {...},
            'process_heat_output_gj': {...},
            'emissions_output_tco2': {...},

            # Efficiency
            'energy_efficiency_pct': {...},
        }
```

**Visualizations needed:**
- Sankey diagram: Energy inputs → Process → Outputs
- Pie chart: Energy mix by source
- Time series: Energy transition 2025-2050

---

### Enhancement 2: Renewable Energy Module
**New: RE adoption calculator**

```python
class RenewableEnergyModule:
    """Model RE adoption scenarios"""

    def calculate_re_potential(facility):
        """Maximum RE capacity per facility"""
        return {
            'rooftop_solar_mw': ...,      # Based on facility size
            'wind_ppa_potential_mw': ...,  # Regional wind resources
            'total_re_potential_gwh': ..., # Annual generation
        }

    def calculate_re_deployment(facility, scenario):
        """RE deployment under scenario"""
        scenarios = {
            'conservative': 0.25,  # 25% RE by 2050
            'moderate': 0.50,      # 50% RE by 2050
            'ambitious': 0.80,     # 80% RE by 2050
            'full_re': 1.0,        # 100% RE by 2050
        }

        return {
            're_capacity_mw': ...,
            're_generation_gwh': ...,
            'grid_remaining_gwh': ...,
            'emission_reduction_kt': ...,
        }
```

**New data files needed:**
- `re_potential_by_location.csv` (regional solar/wind resources)
- `re_adoption_scenarios.csv` (deployment curves 2025-2050)

---

### Enhancement 3: Process-Level Energy Analysis
**Add to energy intensities:**

```python
# Currently have:
energy_intensities.csv:
    - Total GJ per tonne
    - Total kWh per tonne

# Need to add:
process_energy_breakdown.csv:
    product | heat_<150C_gj | heat_150_400C_gj | heat_>400C_gj | power_kwh
    --------|---------------|------------------|---------------|----------
    Ethylene|     15.2      |      8.5         |     25.3      |   450

technology_applicability_matrix.csv:
    product | heat_pump_applicable | h2_ncc | e_ncc | re_applicable
    --------|---------------------|--------|-------|---------------
    Ethylene|        Yes          |  Yes   |  Yes  |     Yes
    HDPE    |        Yes          |   No   |   No  |     Yes
```

---

### Enhancement 4: Facility-Level Technology Deployment
**New optimization output:**

```python
class FacilityDeploymentOptimizer:
    """Optimize technology deployment per facility"""

    def optimize_facility_portfolio(facility, year, scenario):
        """Find best technology mix for this facility"""

        # Consider:
        # 1. Process type (NCC vs non-NCC)
        # 2. Heat temperature requirements
        # 3. RE potential at location
        # 4. Cost-effectiveness of each technology

        return {
            'facility_id': ...,
            'heat_pump_deployed': True/False,
            'heat_pump_capacity_mw': ...,
            'h2_ncc_deployed': True/False,
            'h2_ncc_pct': ...,           # % of NCC using H2
            'e_ncc_deployed': True/False,
            'e_ncc_pct': ...,
            're_capacity_mw': ...,
            're_share_pct': ...,          # % of electricity from RE
            'grid_electricity_gwh': ...,
            'total_abatement_kt': ...,
            'total_cost_musd': ...,
        }
```

**New visualization:**
- Heatmap: 248 facilities × technologies
- Map: Geographic distribution of technologies
- Company comparison: Technology mix by company

---

## 📋 Redesign Implementation Plan

### Phase 1: Energy Flow Foundation
**Tasks:**
1. Add `EnergyFlowTracker` class to utils
2. Expand baseline to track all energy flows
3. Create Sankey diagram function
4. Add energy balance validation

**Files to modify:**
- `modules/utils.py` - Add EnergyFlowTracker
- `modules/baseline.py` - Enhance energy tracking
- Add `plotly` for Sankey diagrams

---

### Phase 2: Renewable Energy Integration
**Tasks:**
1. Create `RenewableEnergyModule` class
2. Add RE potential data by location
3. Create RE adoption scenarios
4. Calculate emission factors for grid+RE mix

**New files:**
- `data/re_potential_by_location.csv`
- `data/re_adoption_curves.csv`
- `modules/renewable_energy.py`

---

### Phase 3: Process-Level Analysis
**Tasks:**
1. Break down energy consumption by temperature
2. Map technologies to process types
3. Calculate technology applicability per facility
4. Add process efficiency factors

**New data:**
- `data/process_heat_breakdown.csv`
- `data/technology_applicability.csv`

---

### Phase 4: Facility-Level Optimization
**Tasks:**
1. Create facility-level optimizer
2. Generate deployment matrix (248 × tech)
3. Build visualization: heatmap, maps, charts
4. Add to Streamlit dashboard

**Files to modify:**
- `modules/optimization.py` - Add facility-level logic
- `app.py` - Add facility deployment page

---

## 🎯 Expected Outcomes

### After Redesign:

#### 1. Energy Flow Visibility ✓
- Sankey diagram showing all energy flows
- Clear hydrogen input/output tracking
- Technology impact on energy mix visible

#### 2. RE Properly Modeled ✓
- RE adoption curves (25%, 50%, 80%, 100%)
- Grid vs RE electricity split tracked
- Emission factors adjusted for RE share
- Heat pumps run on grid+RE mix

#### 3. Deep Energy Analysis ✓
- Process heat by temperature range
- Technology applicability per process
- Heat pump electricity demand separated
- Fuel substitution pathways clear

#### 4. Facility-Level Detail ✓
- 248 × technology deployment matrix
- "Facility X: Heat Pump + 50% RE + H2 NCC"
- Regional technology distribution maps
- Company-specific patterns visible

---

## 📊 New Visualizations

### 1. Energy Sankey Diagram
Shows: Fuel inputs → Processes → Products + Emissions

### 2. Technology Deployment Matrix
Heatmap: 248 facilities × 5 technologies (Heat Pump, H2-NCC, E-NCC, RE, Grid)

### 3. RE Adoption Curves
Line chart: RE share over time (multiple scenarios)

### 4. Facility Technology Mix
Stacked bar: Each facility's technology portfolio

### 5. Energy Balance Dashboard
Shows: Before/After energy flows for each scenario

---

## 🚀 Implementation Priority

### Must Have (Critical):
1. ✅ Energy flow tracking in baseline
2. ✅ RE adoption module
3. ✅ Facility-level deployment matrix

### Should Have (Important):
4. ⚠️ Process-level heat breakdown
5. ⚠️ Sankey diagrams
6. ⚠️ Technology applicability matrix

### Nice to Have (Enhancement):
7. 📍 Geographic maps
8. 📊 Interactive energy dashboard
9. 🔄 Dynamic technology learning curves

---

## 💡 Quick Fixes (Can Do Immediately)

### Fix 1: Show H2 Input
**In MACC visualization:**
```python
# Add H2 consumption tracking
h2_consumption_kt = abatement_mt * h2_intensity_kg_per_tco2 / 1000
# Display in chart hover text
```

### Fix 2: Basic RE Tracking
**Assumption:**
```python
# Heat pumps use electricity
heat_pump_electricity_gwh = heat_pump_abatement_mt * electricity_per_mt

# RE share by year (simple linear)
re_share = {2025: 0.10, 2030: 0.25, 2040: 0.50, 2050: 0.80}

# Emissions from grid+RE mix
grid_emission_factor_adjusted = (
    grid_ef * (1 - re_share) +
    re_ef * re_share  # RE ~0.05 kgCO2/kWh (lifecycle)
)
```

### Fix 3: Facility-Level Output
**Add to optimization:**
```python
# Currently: Aggregate deployment by technology
# Add: Facility-level allocation

facility_deployment = allocate_technologies_to_facilities(
    total_deployment_mt,
    facility_suitability_matrix,
    cost_effectiveness_ranking
)

# Output: facility_technology_deployment.csv
```

---

## ⏱️ Estimated Work

### Full Redesign: ~8-12 hours
- Phase 1 (Energy Flow): 3-4 hours
- Phase 2 (RE Module): 2-3 hours
- Phase 3 (Process Detail): 2-3 hours
- Phase 4 (Facility Level): 2-3 hours

### Quick Fixes Only: ~2-3 hours
- H2 tracking: 30 min
- Basic RE: 1 hour
- Facility allocation: 1-1.5 hours

---

## 🎓 Key Insights

The current model is **functionally correct** but **analytically incomplete**:

✅ **What works:**
- Emissions calculations are correct
- Technology costs are reasonable
- Optimization logic is sound

❌ **What's missing:**
- Energy flow visibility
- RE integration
- Process-level detail
- Facility-level granularity

**Bottom line:** The model calculates the right numbers but doesn't show the energy story. Clients can't see:
- Where hydrogen comes from
- How RE reduces emissions
- Which facilities get which technologies
- How energy mix evolves over time

---

## 🤔 Discussion Questions

Before implementing, we should decide:

1. **RE scenarios:** How many? (Conservative/Moderate/Ambitious?)
2. **Granularity:** Process-level heat breakdown needed? Or facility-level sufficient?
3. **Visualizations:** Sankey critical? Or tables + charts OK?
4. **Dashboard:** Add energy flow page? Or enhance existing pages?
5. **Timeline:** Full redesign or quick fixes first?

**My recommendation:** Start with **Quick Fixes** to show energy flows, then do **Full Redesign** if client needs deeper analysis.
