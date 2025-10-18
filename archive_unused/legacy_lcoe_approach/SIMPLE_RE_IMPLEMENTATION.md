# Simple RE Implementation - RE as Electricity Source Choice

## Core Concept

**RE is NOT a technology deployment - it's just buying electricity from a different source:**

- **Baseline:** All facilities buy **Grid Electricity** (with grid emission factor)
- **RE Option:** Facilities can switch to **RE PPA** (with near-zero emissions)
- **Cost:** RE PPA price vs Grid price
- **Abatement:** (Grid EF - RE EF) × Electricity consumption

No infrastructure, no RE capacity modeling - just a **procurement decision**.

---

## Implementation (Super Simple)

### 1. Add RE as Electricity Procurement Option

**File: `modules/macc.py`**

Add after `_calculate_ncc_electricity_macc()`:

```python
def _calculate_re_ppa_macc(self, year, re_price, grid_emission_factor):
    """
    Calculate RE PPA MACC

    RE PPA = Renewable Power Purchase Agreement
    Simply switching from grid electricity to RE electricity
    No infrastructure needed - just procurement contract
    """

    # Get grid electricity price
    grid_price = self.df_fuel_prices[
        self.df_fuel_prices['year'] == year
    ]['electricity_usd_per_mwh'].iloc[0]

    # Total electricity emissions (from grid)
    total_elec_emissions_mt = self.df_baseline['emissions_electricity_kt'].sum() / 1000

    # Emission factors
    re_ef = 0.05  # kgCO2/kWh (lifecycle, mostly manufacturing)
    grid_ef = grid_emission_factor  # kgCO2/kWh (varies by year)

    # Abatement per kWh switched to RE
    emission_reduction_per_kwh = (grid_ef - re_ef) / 1000  # tCO2/kWh

    # Abatement potential = all electricity emissions × (1 - RE_EF/Grid_EF)
    abatement_potential_mt = total_elec_emissions_mt * (1 - re_ef/grid_ef)

    # Cost difference per MWh
    cost_diff_per_mwh = re_price - grid_price  # $/MWh

    # Cost per tCO2 abated
    kwh_per_tco2 = 1 / emission_reduction_per_kwh
    cost_per_tco2 = (cost_diff_per_mwh / 1000) * kwh_per_tco2  # $/tCO2

    # No CAPEX/OPEX - it's just a PPA contract
    # Only cost is the price differential

    return {
        'year': year,
        'technology': 'RE_PPA',
        'available': True,  # Always available
        'abatement_potential_mtco2': abatement_potential_mt,
        'capex_ann_usd_per_tco2': 0,  # No capital investment
        'opex_ann_usd_per_tco2': 0,   # Operating costs included in PPA price
        'fuel_cost_diff_usd_per_tco2': cost_per_tco2,  # This is the only cost
        'total_cost_usd_per_tco2': cost_per_tco2,
        're_price_usd_per_mwh': re_price,
        'grid_price_usd_per_mwh': grid_price,
        'grid_emission_factor': grid_ef,
        're_emission_factor': re_ef,
    }
```

**Add to `calculate_macc_annual()` (line ~79):**

```python
# 4. RE PPA
grid_ef = self.price_calc.get_grid_emission_factor(year)
re_ppa_macc = self._calculate_re_ppa_macc(year, re_price, grid_ef)
macc_data.append(re_ppa_macc)
```

---

### 2. Update Optimization to Include RE PPA

**File: `modules/optimization.py`**

**Line ~112, change:**
```python
# OLD:
deployed = {'Heat_Pump': 0, 'NCC-H2': 0, 'NCC-Electricity': 0}

# NEW:
deployed = {'Heat_Pump': 0, 'NCC-H2': 0, 'NCC-Electricity': 0, 'RE_PPA': 0}
```

**Line ~122, add RE_PPA to output:**
```python
deployment.append({
    'year': year,
    'target_mt': target,
    'bau_mt': bau,
    'heat_pump_mt': deployed['Heat_Pump'],
    'ncc_h2_mt': deployed['NCC-H2'],
    'ncc_elec_mt': deployed['NCC-Electricity'],
    're_ppa_mt': deployed['RE_PPA'],  # ADD THIS
    'total_deployed_mt': sum(deployed.values()),
    'actual_emissions_mt': bau - sum(deployed.values()),
    'shortfall_mt': max(0, bau - sum(deployed.values()) - target),
})
```

**Same changes in `_optimize_carbon_budget()` around line ~170.**

---

### 3. Add H2 Consumption Tracking (Simple Display)

**File: `modules/macc.py`**

In `_calculate_ncc_h2_macc()`, add after line ~165:

```python
# H2 consumption calculation
# Industry standard: ~0.12-0.15 kg H2 per kg naphtha replaced
# For NCC: ~50 GJ naphtha per tonne ethylene
# H2 energy content: 120 MJ/kg = 0.12 GJ/kg
gj_naphtha_per_tco2 = 1 / self.ef_naphtha  # ~67 GJ
kg_h2_per_gj_naphtha = 0.12 / 42 * 1000  # naphtha ~42 MJ/kg
h2_kg_per_tco2 = gj_naphtha_per_tco2 * kg_h2_per_gj_naphtha

# Add to return dict:
return {
    # ... existing fields ...
    'h2_consumption_kg_per_tco2': h2_kg_per_tco2,
    'h2_total_annual_demand_kt': ncc_emissions * h2_kg_per_tco2 / 1000,
}
```

**In optimization output, add H2 tracking:**

```python
# After deploying NCC-H2, calculate H2 consumption
h2_consumed = 0
if 'NCC-H2' in deployed and deployed['NCC-H2'] > 0:
    h2_data = tech_year[tech_year['technology'] == 'NCC-H2']
    if len(h2_data) > 0 and 'h2_consumption_kg_per_tco2' in h2_data.columns:
        h2_intensity = h2_data.iloc[0]['h2_consumption_kg_per_tco2']
        h2_consumed = (deployed['NCC-H2'] * 1000000 * h2_intensity) / 1000  # kt

deployment.append({
    # ... existing fields ...
    'h2_consumption_kt': h2_consumed,  # ADD THIS
})
```

---

### 4. Simple Facility Allocation (Just for Display)

**File: `modules/optimization.py`**

Add simple method:

```python
def create_facility_summary(self, year, scenario_deployment):
    """
    Create simple facility-level summary
    Just shows proportional allocation - not optimization
    """

    deployed_mt = {
        'Heat_Pump': scenario_deployment['heat_pump_mt'],
        'NCC-H2': scenario_deployment['ncc_h2_mt'],
        'NCC-Electricity': scenario_deployment['ncc_elec_mt'],
        'RE_PPA': scenario_deployment.get('re_ppa_mt', 0),
    }

    facilities = []

    for idx, fac in self.df_baseline.iterrows():
        alloc = {
            'company': fac['company'],
            'location': fac['location'],
            'product': fac['product'],
            'baseline_emissions_kt': fac['total_emissions_kt'],
        }

        # Heat Pump (proportional to naphtha use)
        hp_share = fac['emissions_naphtha_kt'] / self.df_baseline['emissions_naphtha_kt'].sum()
        alloc['heat_pump_kt'] = deployed_mt['Heat_Pump'] * 1000 * hp_share

        # NCC technologies (NCC facilities only)
        if is_ncc_facility(fac['product']):
            ncc_total = self.df_baseline[
                self.df_baseline['product'].apply(is_ncc_facility)
            ]['emissions_naphtha_kt'].sum()
            ncc_share = fac['emissions_naphtha_kt'] / ncc_total
            alloc['ncc_h2_kt'] = deployed_mt['NCC-H2'] * 1000 * ncc_share
            alloc['ncc_elec_kt'] = deployed_mt['NCC-Electricity'] * 1000 * ncc_share
        else:
            alloc['ncc_h2_kt'] = 0
            alloc['ncc_elec_kt'] = 0

        # RE PPA (proportional to electricity use)
        elec_share = fac['emissions_electricity_kt'] / self.df_baseline['emissions_electricity_kt'].sum()
        alloc['re_ppa_kt'] = deployed_mt['RE_PPA'] * 1000 * elec_share

        # Total
        alloc['total_abatement_kt'] = (
            alloc['heat_pump_kt'] +
            alloc['ncc_h2_kt'] +
            alloc['ncc_elec_kt'] +
            alloc['re_ppa_kt']
        )

        alloc['remaining_emissions_kt'] = (
            alloc['baseline_emissions_kt'] - alloc['total_abatement_kt']
        )

        # Technology flags (simple Yes/No)
        alloc['uses_heat_pump'] = 'Yes' if alloc['heat_pump_kt'] > 1 else 'No'
        alloc['uses_h2'] = 'Yes' if alloc['ncc_h2_kt'] > 1 else 'No'
        alloc['uses_re_ppa'] = 'Yes' if alloc['re_ppa_kt'] > 1 else 'No'

        facilities.append(alloc)

    return pd.DataFrame(facilities)
```

**Call in `run_complete_analysis()` for milestone years:**

```python
# After saving deployment CSV (line ~280)
# Create facility summary for key years
for key_year in [2030, 2040, 2050]:
    year_data = df[df['year'] == key_year]
    if len(year_data) > 0:
        fac_summary = self.create_facility_summary(key_year, year_data.iloc[0])
        filename = f'{scenario.lower().replace(" ", "_")}_{key_year}_facilities.csv'
        save_csv_output(fac_summary, self.output_dir / filename)
```

---

### 5. Update Dashboard

**File: `app.py`**

**In `show_scenarios()`, add RE PPA to chart (~line 315):**

```python
# After NCC-Electricity trace, add:
if 're_ppa_mt' in df_scenario.columns:
    fig.add_trace(go.Scatter(
        x=df_scenario['year'],
        y=df_scenario['re_ppa_mt'],
        mode='lines',
        name='RE PPA',
        fill='tonexty',
        line=dict(width=0.5, color='#27AE60'),
        fillcolor='rgba(39, 174, 96, 0.7)'
    ))
```

**Add H2 consumption chart:**

```python
# After technology deployment chart
if 'h2_consumption_kt' in df_scenario.columns:
    st.markdown("---")
    st.markdown("### 🔋 Hydrogen Consumption")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_scenario['year'],
        y=df_scenario['h2_consumption_kt'],
        mode='lines+markers',
        name='H2 Demand',
        line=dict(width=3, color='lightblue'),
        marker=dict(size=8)
    ))
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="H2 Consumption (kt/year)",
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

    # Show 2050 H2 demand
    h2_2050 = df_scenario[df_scenario['year'] == 2050]['h2_consumption_kt'].iloc[0]
    st.info(f"💡 By 2050, this scenario requires **{h2_2050:.0f} kt H2/year** for NCC-H2 deployment")
```

---

## That's It! Much Simpler.

### What This Gives You:

1. **RE as simple choice:** Grid electricity vs RE PPA
   - Cost = Price difference
   - No infrastructure modeling
   - Optimizer picks based on $/tCO2

2. **H2 consumption visible:** Shows how much H2 needed
   - Displayed in charts
   - Helps H2 supply planning
   - Not a constraint, just information

3. **Facility summary:** Which facilities use which technologies
   - Simple proportional allocation
   - Yes/No flags for each technology
   - Good for client presentations

4. **Realistic constraints:** 50% more generous targets

---

## Expected Output

**MACC (4 options):**
```
Year | Heat Pump | RE PPA | NCC-H2 | NCC-Elec
-----|-----------|--------|--------|----------
2025 | -$34/t    | $12/t  | $273/t | $324/t
2050 | -$106/t   | -$8/t  | $73/t  | $92/t
```

**Optimization chooses cheapest:**
```
Year | Heat Pump | RE PPA | NCC-H2 | H2 (kt)
-----|-----------|--------|--------|--------
2030 | 3.9 Mt    | 4.2 Mt | 0      | 0
2040 | 3.9 Mt    | 8.4 Mt | 8.0 Mt | 1,200
2050 | 3.9 Mt    | 8.4 Mt | 20 Mt  | 3,000
```

**Facility output:**
```
Company   | Heat Pump | H2 | RE PPA | Total
----------|-----------|----|---------|---------
LG Chem   | Yes       | Yes| Yes    | 15.2 Mt
Lotte     | Yes       | Yes| Yes    | 12.8 Mt
```

---

## Implementation Time: ~3 hours

- RE PPA MACC: 30 min
- Optimization update: 30 min
- H2 tracking: 30 min
- Facility summary: 45 min
- Dashboard: 45 min

**Want me to implement this simplified version?** 🚀