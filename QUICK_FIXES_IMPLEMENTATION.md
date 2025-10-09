# Quick Fixes Implementation Plan (Option A)

## ✅ Completed

### 1. Emission Constraints Relaxed by ~50%
**File:** `data/emission_scenarios_template.csv`

**New Scenarios:**
- **Moderate_2050:** 52 Mt → 10 Mt (81% reduction, was 96%)
  - 2030: 46 Mt (12% reduction, was 19%)
  - More achievable targets

- **Korea_NDC_Relaxed:**
  - 2030: 46 Mt (12% reduction, was 20.2%)
  - 2050: 15 Mt (71% reduction, was 99%)

- **Gradual_Path:**
  - 2030: 48 Mt (8% reduction)
  - 2050: 20 Mt (62% reduction)

**Carbon Budgets:**
- Budget_1200Mt (vs BAU 1304 Mt) - very generous
- Budget_1000Mt - moderate
- Budget_800Mt - ambitious

---

## 🚀 To Implement

### 2. Add Renewable Energy as Cost-Optimized Technology

#### A. Add RE Technology Parameters ✅ DONE
**File:** `data/technology_parameters.csv`
```csv
Renewable_Energy,All electricity consumers,,9,2025,180,140,100,80,1.5,25
```

#### B. Update MACC Module to Calculate RE Costs
**File:** `modules/macc.py`

Add new method after line 179:

```python
def _calculate_renewable_energy_macc(self, year, re_price, grid_emission_factor):
    """Calculate Renewable Energy MACC

    RE replaces grid electricity, avoiding grid emissions
    Cost = CAPEX + OPEX - (avoided grid electricity cost)
    Abatement = grid electricity emissions × RE adoption %
    """
    tech_costs = self.tech_cost_calc.get_technology_costs('Renewable_Energy', year)

    # Abatement potential = all electricity emissions
    total_electricity_emissions = self.df_baseline['emissions_electricity_kt'].sum() / 1000  # MtCO2

    # Costs
    capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
    lifetime = tech_costs['lifetime_years']
    crf = self.price_calc.calculate_capital_recovery_factor(self.discount_rate, lifetime)
    capex_ann = capex_musd_per_mtco2 * crf * 1e6  # $/tCO2

    opex_ann = capex_ann * (tech_costs['opex_pct_capex'] / 100)

    # Fuel cost differential (RE vs grid electricity)
    # Grid electricity price from fuel prices file
    grid_price = self.df_fuel_prices[
        self.df_fuel_prices['year'] == year
    ]['electricity_usd_per_mwh'].iloc[0]

    # RE LCOE (Levelized Cost of Energy)
    # RE price in $/MWh directly from price trajectory

    # $/tCO2 saved
    # 1 tCO2 electricity = emissions_electricity_kt / total_electricity_kwh
    total_elec_kwh = self.df_baseline['electricity_kwh_per_year'].sum()
    total_elec_mwh = total_elec_kwh / 1000
    kwh_per_tco2 = total_elec_mwh / (total_electricity_emissions * 1000)

    fuel_cost_diff = (re_price - grid_price) * kwh_per_tco2 / 1000  # $/tCO2

    total_cost = capex_ann + opex_ann + fuel_cost_diff

    return {
        'year': year,
        'technology': 'Renewable_Energy',
        'available': tech_costs['available'],
        'abatement_potential_mtco2': total_electricity_emissions,
        'capex_ann_usd_per_tco2': capex_ann,
        'opex_ann_usd_per_tco2': opex_ann,
        'fuel_cost_diff_usd_per_tco2': fuel_cost_diff,
        'total_cost_usd_per_tco2': total_cost,
        're_price_usd_per_mwh': re_price,
        'grid_price_usd_per_mwh': grid_price,
        're_generation_potential_gwh': total_elec_mwh / 1000,
    }
```

#### C. Add RE to Annual MACC Calculation
**In `calculate_macc_annual()` method, after line 79:**

```python
# 4. RENEWABLE ENERGY
grid_ef = self.price_calc.get_grid_emission_factor(year)
re_macc = self._calculate_renewable_energy_macc(year, re_price, grid_ef)
macc_data.append(re_macc)
```

#### D. Update Optimization to Include RE
**File:** `modules/optimization.py`

In `_optimize_annual_path()` method, line 112:

```python
# Current:
deployed = {'Heat_Pump': 0, 'NCC-H2': 0, 'NCC-Electricity': 0}

# Change to:
deployed = {
    'Heat_Pump': 0,
    'NCC-H2': 0,
    'NCC-Electricity': 0,
    'Renewable_Energy': 0  # ADD THIS
}
```

And update line 122-132 to include RE in output:

```python
deployment.append({
    'year': year,
    'target_mt': target,
    'bau_mt': bau,
    'heat_pump_mt': deployed['Heat_Pump'],
    'ncc_h2_mt': deployed['NCC-H2'],
    'ncc_elec_mt': deployed['NCC-Electricity'],
    're_mt': deployed['Renewable_Energy'],  # ADD THIS
    'total_deployed_mt': sum(deployed.values()),
    'actual_emissions_mt': bau - sum(deployed.values()),
    'shortfall_mt': max(0, bau - sum(deployed.values()) - target),
})
```

---

### 3. Add Hydrogen Consumption Tracking

#### A. Add H2 Calculation to MACC
**In `_calculate_ncc_h2_macc()` method, add after line 168:**

```python
# Calculate H2 consumption
# Assume 0.15 kg H2 per kg naphtha replaced
# Naphtha intensity: ~67 GJ/tCO2 (from 1/0.0149)
kg_naphtha_per_tco2 = (1 / self.ef_naphtha) * 1000 / 42  # GJ to kg, 42 MJ/kg naphtha
h2_consumption_kg_per_tco2 = kg_naphtha_per_tco2 * 0.15

# Total H2 needed for full NCC abatement
h2_consumption_kt_per_year = (ncc_emissions * 1000 * h2_consumption_kg_per_tco2) / 1000

return {
    # ... existing fields ...
    'h2_consumption_kg_per_tco2': h2_consumption_kg_per_tco2,
    'h2_total_demand_kt_per_year': h2_consumption_kt_per_year,
}
```

#### B. Add H2 Consumption to Optimization Output
**File:** `modules/optimization.py`

Add H2 tracking in deployment dict (around line 122):

```python
# After deploying NCC-H2 technology
if 'NCC-H2' in deployed and deployed['NCC-H2'] > 0:
    # Get H2 intensity from MACC data
    h2_data = tech_year[tech_year['technology'] == 'NCC-H2']
    if len(h2_data) > 0:
        h2_intensity = h2_data.iloc[0]['h2_consumption_kg_per_tco2']
        h2_consumed_kt = deployed['NCC-H2'] * 1000 * h2_intensity / 1000
    else:
        h2_consumed_kt = 0
else:
    h2_consumed_kt = 0

deployment.append({
    # ... existing fields ...
    'h2_consumption_kt': h2_consumed_kt,  # ADD THIS
})
```

---

### 4. Create Facility-Level Technology Allocation

#### A. Add Facility Allocation Function
**File:** `modules/optimization.py`

Add new method after `_optimize_carbon_budget()`:

```python
def allocate_technologies_to_facilities(self, year, deployed_tech_mt):
    """
    Allocate aggregate technology deployment to specific facilities

    Logic:
    1. Heat Pumps → All facilities (proportional to naphtha emissions)
    2. NCC-H2 → NCC facilities only (proportional to NCC capacity)
    3. NCC-Electricity → NCC facilities only
    4. RE → All facilities (proportional to electricity consumption)

    Returns: DataFrame with facility-level deployment
    """
    allocations = []

    for idx, facility in self.df_baseline.iterrows():
        alloc = {
            'facility_id': idx,
            'company': facility['company'],
            'location': facility['location'],
            'product': facility['product'],
            'capacity_kt': facility['capacity_kt'],
            'baseline_emissions_kt': facility['total_emissions_kt'],
        }

        # Heat Pump allocation (proportional to process heat potential)
        if deployed_tech_mt['Heat_Pump'] > 0:
            facility_share = (
                facility['emissions_naphtha_kt'] /
                self.df_baseline['emissions_naphtha_kt'].sum()
            )
            alloc['heat_pump_abatement_kt'] = (
                deployed_tech_mt['Heat_Pump'] * 1000 * facility_share
            )
        else:
            alloc['heat_pump_abatement_kt'] = 0

        # NCC-H2 allocation (NCC facilities only)
        if is_ncc_facility(facility['product']) and deployed_tech_mt['NCC-H2'] > 0:
            ncc_total = self.df_baseline[
                self.df_baseline['product'].apply(is_ncc_facility)
            ]['emissions_naphtha_kt'].sum()
            facility_share = facility['emissions_naphtha_kt'] / ncc_total
            alloc['ncc_h2_abatement_kt'] = (
                deployed_tech_mt['NCC-H2'] * 1000 * facility_share
            )
        else:
            alloc['ncc_h2_abatement_kt'] = 0

        # NCC-Electricity allocation
        if is_ncc_facility(facility['product']) and deployed_tech_mt['NCC-Electricity'] > 0:
            ncc_total = self.df_baseline[
                self.df_baseline['product'].apply(is_ncc_facility)
            ]['emissions_naphtha_kt'].sum()
            facility_share = facility['emissions_naphtha_kt'] / ncc_total
            alloc['ncc_elec_abatement_kt'] = (
                deployed_tech_mt['NCC-Electricity'] * 1000 * facility_share
            )
        else:
            alloc['ncc_elec_abatement_kt'] = 0

        # RE allocation (proportional to electricity consumption)
        if deployed_tech_mt.get('Renewable_Energy', 0) > 0:
            facility_share = (
                facility['electricity_kwh_per_year'] /
                self.df_baseline['electricity_kwh_per_year'].sum()
            )
            alloc['re_abatement_kt'] = (
                deployed_tech_mt['Renewable_Energy'] * 1000 * facility_share
            )
            alloc['re_capacity_mw'] = (
                facility['electricity_kwh_per_year'] / 8760 / 1000 *  # MW average
                (alloc['re_abatement_kt'] / facility['emissions_electricity_kt'])
            )
        else:
            alloc['re_abatement_kt'] = 0
            alloc['re_capacity_mw'] = 0

        # Total abatement for this facility
        alloc['total_abatement_kt'] = (
            alloc['heat_pump_abatement_kt'] +
            alloc['ncc_h2_abatement_kt'] +
            alloc['ncc_elec_abatement_kt'] +
            alloc['re_abatement_kt']
        )

        alloc['remaining_emissions_kt'] = (
            alloc['baseline_emissions_kt'] - alloc['total_abatement_kt']
        )

        allocations.append(alloc)

    return pd.DataFrame(allocations)
```

#### B. Call Facility Allocation in Optimization
**In `run_complete_analysis()` method:**

```python
# After line 101 (after saving deployment CSV)
# Generate facility-level allocation for selected years
for year in [2030, 2040, 2050]:
    year_deployment = df[df['year'] == year]
    if len(year_deployment) > 0:
        deployed = {
            'Heat_Pump': year_deployment['heat_pump_mt'].iloc[0],
            'NCC-H2': year_deployment['ncc_h2_mt'].iloc[0],
            'NCC-Electricity': year_deployment['ncc_elec_mt'].iloc[0],
            'Renewable_Energy': year_deployment.get('re_mt', pd.Series([0])).iloc[0],
        }

        facility_alloc = self.allocate_technologies_to_facilities(year, deployed)
        filename = f'{scenario.lower().replace(" ", "_")}_{year}_facility_allocation.csv'
        save_csv_output(facility_alloc, self.output_dir / filename)
        print(f"   ✓ Saved: {filename}")
```

---

### 5. Add Energy Flow Visualizations

#### A. Create Energy Flow Chart
**File:** `modules/optimization.py`

Add new visualization method:

```python
def create_energy_flow_chart(self, scenario_name, df_deployment):
    """Create energy flow visualization showing fuel transitions"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Select milestone years
    years = [2025, 2030, 2040, 2050]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[f"{y}" for y in years],
        specs=[[{'type': 'domain'}, {'type': 'domain'}],
               [{'type': 'domain'}, {'type': 'domain'}]]
    )

    row_col = [(1,1), (1,2), (2,1), (2,2)]

    for idx, year in enumerate(years):
        year_data = df_deployment[df_deployment['year'] == year]
        if len(year_data) == 0:
            continue

        # Energy sources
        labels = ['Naphtha', 'Grid Electricity', 'RE', 'H2',
                  'Heat Pump', 'NCC-H2', 'NCC-Elec', 'Process Heat', 'Emissions']

        # Simplified flow (you'll need to calculate actual values from baseline)
        source = [0, 1, 2, 3, 4, 5, 6, 7]  # From indices
        target = [7, 7, 4, 5, 7, 7, 7, 8]  # To indices
        value = [100, 20, 10, 5, 15, 10, 8, 80, 50]  # Placeholder values

        fig.add_trace(go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                label=labels,
                color=['brown', 'gray', 'green', 'lightblue',
                       'orange', 'blue', 'purple', 'yellow', 'red']
            ),
            link=dict(
                source=source,
                target=target,
                value=value
            )
        ), row=row_col[idx][0], col=row_col[idx][1])

    fig.update_layout(
        title_text=f"Energy Flow Evolution: {scenario_name}",
        height=800
    )

    return fig
```

---

### 6. Update Streamlit Dashboard

#### A. Add RE Column to Scenario Explorer
**File:** `app.py`

In `show_scenarios()` function, update line ~315:

```python
# Update stackplot to include RE
fig.add_trace(go.Scatter(
    x=df_scenario['year'],
    y=df_scenario['heat_pump_mt'],
    mode='lines',
    name='Heat Pumps',
    stackgroup='one',
    fillcolor='rgba(46, 204, 113, 0.7)'
))

fig.add_trace(go.Scatter(
    x=df_scenario['year'],
    y=df_scenario['ncc_h2_mt'],
    mode='lines',
    name='NCC-H2',
    stackgroup='one',
    fillcolor='rgba(52, 152, 219, 0.7)'
))

fig.add_trace(go.Scatter(
    x=df_scenario['year'],
    y=df_scenario['ncc_elec_mt'],
    mode='lines',
    name='NCC-Electricity',
    stackgroup='one',
    fillcolor='rgba(231, 76, 60, 0.7)'
))

# ADD RE
if 're_mt' in df_scenario.columns:
    fig.add_trace(go.Scatter(
        x=df_scenario['year'],
        y=df_scenario['re_mt'],
        mode='lines',
        name='Renewable Energy',
        stackgroup='one',
        fillcolor='rgba(46, 213, 115, 0.7)'
    ))
```

#### B. Add Facility-Level Page
**Add new page function:**

```python
def show_facility_deployment(data):
    """Facility-level technology deployment"""
    st.markdown('<div class="sub-header">Facility-Level Technology Deployment</div>',
                unsafe_allow_html=True)

    # Load facility allocation files
    facility_files = list(Path('outputs/module_03').glob('*_facility_allocation.csv'))

    if len(facility_files) == 0:
        st.warning("No facility-level data found. Run optimization first.")
        return

    # Scenario and year selector
    scenario = st.sidebar.selectbox("Select Scenario",
                                    [f.stem.split('_')[0] for f in facility_files])
    year = st.sidebar.selectbox("Select Year", [2030, 2040, 2050])

    # Load data
    filename = f"{scenario}_{year}_facility_allocation.csv"
    df_fac = pd.read_csv(f'outputs/module_03/{filename}')

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Facilities", len(df_fac))
    with col2:
        st.metric("Total Abatement", f"{df_fac['total_abatement_kt'].sum()/1000:.1f} Mt")
    with col3:
        n_with_tech = len(df_fac[df_fac['total_abatement_kt'] > 0])
        st.metric("Facilities with Tech", n_with_tech)
    with col4:
        avg_abatement = df_fac['total_abatement_kt'].mean()
        st.metric("Avg Abatement", f"{avg_abatement:.1f} kt")

    # Technology deployment heatmap
    st.markdown("### Technology Deployment by Facility")

    # Prepare heatmap data
    tech_cols = ['heat_pump_abatement_kt', 'ncc_h2_abatement_kt',
                 'ncc_elec_abatement_kt', 're_abatement_kt']
    heatmap_data = df_fac[tech_cols].T
    heatmap_data.columns = df_fac['company'] + ' - ' + df_fac['product']

    fig = px.imshow(heatmap_data,
                    labels=dict(x="Facility", y="Technology", color="Abatement (kt)"),
                    aspect="auto",
                    color_continuous_scale='YlOrRd')
    st.plotly_chart(fig, use_container_width=True)

    # Detailed table
    st.markdown("### Facility Details")
    st.dataframe(df_fac, use_container_width=True)
```

---

## 📋 Testing Checklist

After implementing:

- [ ] Run Module 2 (MACC) - should have 4 technologies now
- [ ] Check MACC CSV includes RE with costs
- [ ] Run Module 3 (Optimization) - should deploy RE if cost-effective
- [ ] Check deployment CSV includes re_mt column
- [ ] Verify H2 consumption tracking in outputs
- [ ] Check facility allocation CSVs exist for 2030/2040/2050
- [ ] Open Streamlit dashboard
- [ ] Verify RE shows in technology deployment charts
- [ ] Check facility-level page (if added)

---

## 🎯 Expected Results

### MACC Output
```
year,technology,abatement_potential_mtco2,total_cost_usd_per_tco2
2025,Heat_Pump,3.9,-34
2025,Renewable_Energy,8.4,45    # NEW!
2025,NCC-H2,37.6,273
2025,NCC-Electricity,37.6,324
```

### Optimization Output
```
year,heat_pump_mt,ncc_h2_mt,ncc_elec_mt,re_mt,h2_consumption_kt
2030,3.9,0,0,2.5,0            # RE deployed if cheap!
2040,3.9,15.2,0,6.8,2280       # H2 consumption tracked
2050,3.9,37.6,2.1,8.4,5640
```

### Facility Allocation
```
facility,company,heat_pump_kt,ncc_h2_kt,re_kt,total_kt
LG-1,LG Chem,12.5,45.3,8.2,66.0
Lotte-1,Lotte,8.3,38.1,5.4,51.8
```

---

## ⏱️ Estimated Implementation Time

- [ ] Update MACC for RE: **1.5 hours**
- [ ] Update optimization for RE: **1 hour**
- [ ] Add H2 tracking: **0.5 hours**
- [ ] Facility allocation: **1.5 hours**
- [ ] Dashboard updates: **1 hour**
- [ ] Testing & debugging: **1 hour**

**Total: ~6-7 hours**

---

## 💡 Key Design Decisions

### 1. RE as Separate Technology (Not bundled with heat pumps)
**Rationale:** RE can reduce ALL electricity emissions, not just heat pump load

### 2. Cost-Effectiveness Drives Deployment
**Logic:** Optimizer sorts all 4 technologies by $/tCO2 and deploys cheapest first

### 3. Facility Allocation is Proportional
**Method:** Each facility gets tech based on their share of applicable emissions

### 4. H2 Tracking is Descriptive (Not Constrained)
**Approach:** Calculate and display H2 needs; don't constrain by H2 supply

---

This implementation maintains the optimization-first philosophy while adding energy visibility!
