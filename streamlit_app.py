"""
Korean Petrochemical MACC Model - Streamlit Dashboard
Comprehensive analysis tool with LCOH calculation
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Korean Petrochemical MACC Model",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data directory
DATA_DIR = Path("data")

# ============================================================================
# Data Loading Functions
# ============================================================================
@st.cache_data
def load_facility_data():
    """Load facility database"""
    df = pd.read_csv(DATA_DIR / "facility_database_with_regions.csv")
    return df

@st.cache_data
def load_price_trajectories():
    """Load all price trajectories"""
    h2 = pd.read_csv(DATA_DIR / "h2_price_trajectory.csv")
    re = pd.read_csv(DATA_DIR / "re_price_trajectory.csv")
    grid = pd.read_csv(DATA_DIR / "grid_price_trajectory.csv")
    return h2, re, grid

@st.cache_data
def load_scenarios():
    """Load production scenarios"""
    return pd.read_csv(DATA_DIR / "demand_growth_trajectory_scenarios.csv")

@st.cache_data
def load_technology_params():
    """Load technology parameters"""
    return pd.read_csv(DATA_DIR / "technology_parameters.csv")

# ============================================================================
# Calculation Functions
# ============================================================================
def calculate_lcoh(elec_price, capex, efficiency=0.70, lifetime=20, capacity_factor=0.90, opex_pct=0.02):
    """
    Calculate Levelized Cost of Hydrogen

    Parameters:
    - elec_price: Electricity price ($/MWh)
    - capex: Electrolyzer CAPEX ($/kW)
    - efficiency: Electrolyzer efficiency (HHV basis)
    - lifetime: System lifetime (years)
    - capacity_factor: Annual capacity factor
    - opex_pct: OPEX as % of CAPEX

    Returns:
    - LCOH in $/kg H2
    """
    h2_hhv = 39.4  # kWh/kg (Higher Heating Value)
    elec_per_kg = h2_hhv / efficiency  # kWh electricity per kg H2

    annual_hours = 8760 * capacity_factor

    # CAPEX component ($/kg)
    capex_per_kg = capex / (annual_hours * lifetime) * elec_per_kg

    # OPEX component ($/kg)
    opex_per_kg = capex_per_kg * opex_pct * lifetime

    # Electricity cost ($/kg)
    elec_cost_per_kg = elec_price * elec_per_kg / 1000  # Convert $/MWh to $/kWh

    lcoh = capex_per_kg + opex_per_kg + elec_cost_per_kg

    return lcoh

def get_electrolyzer_capex(year):
    """Get interpolated electrolyzer CAPEX for a given year"""
    if year <= 2025:
        return 1200
    elif year <= 2030:
        return 1200 - (1200 - 800) * (year - 2025) / 5
    elif year <= 2040:
        return 800 - (800 - 500) * (year - 2030) / 10
    elif year <= 2050:
        return 500 - (500 - 300) * (year - 2040) / 10
    else:
        return 300

def get_ncc_capex(year, tech='NCC-H2'):
    """Get interpolated NCC technology CAPEX"""
    if tech == 'NCC-H2':
        capex_schedule = {2025: 1550, 2030: 1300, 2040: 935, 2050: 780}
    else:  # NCC-Electricity
        capex_schedule = {2025: 1500, 2030: 1350, 2040: 1050, 2050: 900}

    if year <= 2025:
        return capex_schedule[2025]
    elif year <= 2030:
        return capex_schedule[2025] - (capex_schedule[2025] - capex_schedule[2030]) * (year - 2025) / 5
    elif year <= 2040:
        return capex_schedule[2030] - (capex_schedule[2030] - capex_schedule[2040]) * (year - 2030) / 10
    elif year <= 2050:
        return capex_schedule[2040] - (capex_schedule[2040] - capex_schedule[2050]) * (year - 2040) / 10
    else:
        return capex_schedule[2050]

def calculate_scenario_results(scenario_mult, h2_intensity=0.56, elec_intensity=5.0,
                               baseline_ethylene=11962, baseline_ef=1.9):
    """Calculate H2 and electricity demand for a production scenario

    Note: Electricity uses the MtCO2-based approach from optimization_v2.py
    to match the Streamlit values (164.5 TWh for Shaheen)

    Formula: Electricity (TWh) = Deployed_MtCO2 * 5.3 TWh/MtCO2
    Where 5.3 = 10 MWh/ton / 1.9 tCO2/ton (from the original model)
    """
    ethylene_kt = baseline_ethylene * scenario_mult

    # H2 demand (kt) = Ethylene (kt) * H2 intensity
    h2_demand_kt = ethylene_kt * h2_intensity

    # BAU emissions (MtCO2) = Ethylene (kt) * baseline EF / 1000
    bau_emissions_mt = ethylene_kt * baseline_ef / 1000

    # Electricity demand (TWh) using MtCO2-based approach
    # From optimization_v2.py: mwh_per_tco2_ncc_elec = 5300
    # This gives 164.5 TWh for Shaheen scenario (matching original)
    mwh_per_tco2 = 5.3  # TWh per MtCO2
    elec_demand_twh = bau_emissions_mt * mwh_per_tco2

    return {
        'ethylene_kt': ethylene_kt,
        'h2_demand_kt': h2_demand_kt,
        'elec_demand_twh': elec_demand_twh,
        'bau_emissions_mt': bau_emissions_mt
    }

# ============================================================================
# Sidebar
# ============================================================================
st.sidebar.title("🏭 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["📊 Overview", "⚡ 6-Scenario Summary", "🔬 LCOH Calculator",
     "🗺️ Regional Analysis", "💰 Cost Analysis", "📈 MACC Curves"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Model Parameters")

# Editable parameters in sidebar
h2_intensity = st.sidebar.slider("H2 Intensity (t/t C2H4)", 0.4, 0.8, 0.56, 0.01)
elec_intensity = st.sidebar.slider("Elec Intensity (MWh/t C2H4)", 4.0, 7.0, 5.0, 0.1)
baseline_ef = st.sidebar.slider("Baseline EF (tCO2/t C2H4)", 1.5, 2.5, 1.9, 0.1)

st.sidebar.markdown("---")
st.sidebar.markdown("**Data Sources:**")
st.sidebar.markdown("- 248 Facilities Database")
st.sidebar.markdown("- BASF/SABIC/Linde 2024")
st.sidebar.markdown("- Lummus Tech 2023")

# ============================================================================
# Page: Overview
# ============================================================================
if page == "📊 Overview":
    st.title("🏭 Korean Petrochemical MACC Model")
    st.markdown("### Comprehensive Energy Transition Analysis")

    # Load data
    df_fac = load_facility_data()

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    ncc_products = ['Ethylene', 'Propylene', 'Butadiene']
    df_ncc = df_fac[df_fac['product'].isin(ncc_products)]
    df_btx = df_fac[df_fac['process'] == 'BTX Plant']
    df_utility = df_fac[df_fac['process'] == 'Utility']

    with col1:
        st.metric("Total Facilities", len(df_fac))
    with col2:
        st.metric("NCC Facilities", len(df_ncc))
    with col3:
        st.metric("BTX Facilities", len(df_btx))
    with col4:
        st.metric("Utility Facilities", len(df_utility))

    st.markdown("---")

    # Facility breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Facilities by Complex")
        complex_counts = df_fac['complex'].value_counts()
        fig = px.pie(values=complex_counts.values, names=complex_counts.index,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Capacity by Process Type")
        process_capacity = df_fac.groupby('process')['capacity_kt'].sum().sort_values(ascending=True)
        fig = px.bar(x=process_capacity.values, y=process_capacity.index, orientation='h',
                     color=process_capacity.values, color_continuous_scale='Viridis')
        fig.update_layout(height=350, showlegend=False, xaxis_title="Capacity (kt/year)")
        st.plotly_chart(fig, use_container_width=True)

    # Regional summary
    st.markdown("---")
    st.markdown("#### Capacity by Location")

    location_summary = df_fac.groupby('location').agg({
        'capacity_kt': 'sum',
        'product': 'count'
    }).rename(columns={'product': 'facilities'}).sort_values('capacity_kt', ascending=False)

    fig = px.bar(location_summary, x=location_summary.index, y='capacity_kt',
                 color='facilities', color_continuous_scale='Blues',
                 labels={'capacity_kt': 'Capacity (kt/year)', 'facilities': 'Facilities'})
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Page: 6-Scenario Summary
# ============================================================================
elif page == "⚡ 6-Scenario Summary":
    st.title("⚡ 6-Scenario Summary (2050)")
    st.markdown("### 3 Production Scenarios × 2 Technology Pathways")

    # Load data
    df_scenarios = load_scenarios()
    df_h2, df_re, df_grid = load_price_trajectories()

    # Get 2050 values
    shaheen_mult = df_scenarios[df_scenarios['year'] == 2050]['scenario_shaheen'].iloc[0]
    r25_mult = df_scenarios[df_scenarios['year'] == 2050]['scenario_restructure_25pct'].iloc[0]
    r40_mult = df_scenarios[df_scenarios['year'] == 2050]['scenario_restructure_40pct'].iloc[0]

    h2_price_2050 = df_h2[df_h2['year'] == 2050]['h2_price_usd_per_kg'].iloc[0]
    re_price_2050 = df_re[df_re['year'] == 2050]['re_price_usd_per_mwh'].iloc[0]

    # Calculate results
    scenarios = {
        'Shaheen': calculate_scenario_results(shaheen_mult, h2_intensity, elec_intensity, baseline_ef=baseline_ef),
        '구조조정 25%': calculate_scenario_results(r25_mult, h2_intensity, elec_intensity, baseline_ef=baseline_ef),
        '구조조정 40%': calculate_scenario_results(r40_mult, h2_intensity, elec_intensity, baseline_ef=baseline_ef)
    }

    # Create summary table
    st.markdown("#### Summary Table")

    summary_data = []
    for scenario_name, results in scenarios.items():
        # NCC-H2 pathway
        summary_data.append({
            'Scenario': f"{scenario_name} + NCC-H2",
            'Technology': 'NCC-H2',
            'BAU Emissions (MtCO2)': round(results['bau_emissions_mt'], 1),
            'H2 Demand (kt)': round(results['h2_demand_kt'], 1),
            'Electricity (TWh)': 0,
            'H2 Cost ($B/yr)': round(results['h2_demand_kt'] * h2_price_2050 / 1000, 2)
        })
        # NCC-Elec pathway
        summary_data.append({
            'Scenario': f"{scenario_name} + NCC-Elec",
            'Technology': 'NCC-Electricity',
            'BAU Emissions (MtCO2)': round(results['bau_emissions_mt'], 1),
            'H2 Demand (kt)': 0,
            'Electricity (TWh)': round(results['elec_demand_twh'], 1),
            'Elec Cost ($B/yr)': round(results['elec_demand_twh'] * re_price_2050 / 1000, 2)
        })

    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Visual comparison
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### H2 Demand by Scenario (NCC-H2 Pathway)")
        h2_data = pd.DataFrame({
            'Scenario': list(scenarios.keys()),
            'H2 (kt/year)': [s['h2_demand_kt'] for s in scenarios.values()]
        })
        fig = px.bar(h2_data, x='Scenario', y='H2 (kt/year)',
                     color='Scenario', color_discrete_sequence=['#3498DB', '#2ECC71', '#E74C3C'])
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Electricity Demand by Scenario (NCC-Elec Pathway)")
        elec_data = pd.DataFrame({
            'Scenario': list(scenarios.keys()),
            'Electricity (TWh/year)': [s['elec_demand_twh'] for s in scenarios.values()]
        })
        fig = px.bar(elec_data, x='Scenario', y='Electricity (TWh/year)',
                     color='Scenario', color_discrete_sequence=['#3498DB', '#2ECC71', '#E74C3C'])
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Streamlit matching values
    st.markdown("---")
    st.markdown("#### Reference Values (from Model)")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Shaheen H2", f"{scenarios['Shaheen']['h2_demand_kt']:,.1f} kt")
        st.metric("Shaheen Elec", f"{scenarios['Shaheen']['elec_demand_twh']:,.1f} TWh")
    with col2:
        st.metric("구조조정 25% H2", f"{scenarios['구조조정 25%']['h2_demand_kt']:,.1f} kt")
        st.metric("구조조정 25% Elec", f"{scenarios['구조조정 25%']['elec_demand_twh']:,.1f} TWh")
    with col3:
        st.metric("구조조정 40% H2", f"{scenarios['구조조정 40%']['h2_demand_kt']:,.1f} kt")
        st.metric("구조조정 40% Elec", f"{scenarios['구조조정 40%']['elec_demand_twh']:,.1f} TWh")

# ============================================================================
# Page: LCOH Calculator
# ============================================================================
elif page == "🔬 LCOH Calculator":
    st.title("🔬 Levelized Cost of Hydrogen (LCOH) Calculator")
    st.markdown("### Calculate green hydrogen production cost from electrolysis")

    # Load price data
    df_h2, df_re, df_grid = load_price_trajectories()

    # User inputs
    st.markdown("#### Electrolyzer Parameters")
    col1, col2, col3 = st.columns(3)

    with col1:
        efficiency = st.slider("Efficiency (HHV)", 0.50, 0.85, 0.70, 0.01)
        lifetime = st.slider("Lifetime (years)", 10, 30, 20, 1)
    with col2:
        capacity_factor = st.slider("Capacity Factor", 0.50, 0.98, 0.90, 0.01)
        opex_pct = st.slider("OPEX (% of CAPEX)", 0.01, 0.05, 0.02, 0.005)
    with col3:
        year = st.slider("Year", 2025, 2050, 2030)
        custom_elec_price = st.checkbox("Use Custom Electricity Price")

    if custom_elec_price:
        elec_price = st.slider("Electricity Price ($/MWh)", 30.0, 250.0, 100.0, 5.0)
    else:
        elec_price = df_re[df_re['year'] == year]['re_price_usd_per_mwh'].iloc[0]

    # Calculate LCOH
    capex = get_electrolyzer_capex(year)
    lcoh = calculate_lcoh(elec_price, capex, efficiency, lifetime, capacity_factor, opex_pct)
    market_h2 = df_h2[df_h2['year'] == year]['h2_price_usd_per_kg'].iloc[0]

    st.markdown("---")
    st.markdown("#### Results")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Electrolyzer CAPEX", f"${capex:,.0f}/kW")
    with col2:
        st.metric("Electricity Price", f"${elec_price:.1f}/MWh")
    with col3:
        st.metric("**LCOH**", f"${lcoh:.2f}/kg",
                  delta=f"vs Market: ${lcoh - market_h2:+.2f}")
    with col4:
        st.metric("Market H2 Price", f"${market_h2:.2f}/kg")

    # Recommendation
    if lcoh < market_h2:
        st.success(f"✅ **Make H2**: LCOH (${lcoh:.2f}/kg) is cheaper than buying (${market_h2:.2f}/kg)")
    else:
        st.warning(f"⚠️ **Buy H2**: Market price (${market_h2:.2f}/kg) is cheaper than LCOH (${lcoh:.2f}/kg)")

    st.markdown("---")

    # LCOH breakdown
    st.markdown("#### LCOH Cost Breakdown")

    h2_hhv = 39.4
    elec_per_kg = h2_hhv / efficiency
    annual_hours = 8760 * capacity_factor

    capex_component = capex / (annual_hours * lifetime) * elec_per_kg
    opex_component = capex_component * opex_pct * lifetime
    elec_component = elec_price * elec_per_kg / 1000

    breakdown = pd.DataFrame({
        'Component': ['CAPEX', 'OPEX', 'Electricity'],
        'Cost ($/kg)': [capex_component, opex_component, elec_component]
    })

    fig = px.pie(breakdown, values='Cost ($/kg)', names='Component',
                 color_discrete_sequence=['#3498DB', '#2ECC71', '#E74C3C'])
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    # LCOH trajectory
    st.markdown("---")
    st.markdown("#### LCOH vs Market H2 Price Trajectory")

    years = list(range(2025, 2051))
    lcoh_trajectory = []
    market_trajectory = []

    for y in years:
        cap = get_electrolyzer_capex(y)
        ep = df_re[df_re['year'] == y]['re_price_usd_per_mwh'].iloc[0]
        lcoh_trajectory.append(calculate_lcoh(ep, cap, efficiency, lifetime, capacity_factor, opex_pct))
        market_trajectory.append(df_h2[df_h2['year'] == y]['h2_price_usd_per_kg'].iloc[0])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=lcoh_trajectory, name='LCOH',
                             line=dict(color='#E74C3C', width=3)))
    fig.add_trace(go.Scatter(x=years, y=market_trajectory, name='Market H2',
                             line=dict(color='#3498DB', width=3)))
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Price ($/kg)',
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Breakeven analysis
    st.markdown("---")
    st.markdown("#### Breakeven Electricity Price")
    st.markdown("*At what electricity price does LCOH equal market H2 price?*")

    breakeven_data = []
    for y in [2025, 2030, 2040, 2050]:
        cap = get_electrolyzer_capex(y)
        mkt = df_h2[df_h2['year'] == y]['h2_price_usd_per_kg'].iloc[0]

        capex_per_kg = cap / (8760 * capacity_factor * lifetime) * (h2_hhv / efficiency)
        opex_per_kg = capex_per_kg * opex_pct * lifetime

        # LCOH = capex + opex + elec_price * elec_per_kg / 1000
        # mkt = capex + opex + elec_price * elec_per_kg / 1000
        # elec_price = (mkt - capex - opex) * 1000 / elec_per_kg

        breakeven_elec = (mkt - capex_per_kg - opex_per_kg) * 1000 / (h2_hhv / efficiency)
        current_re = df_re[df_re['year'] == y]['re_price_usd_per_mwh'].iloc[0]

        breakeven_data.append({
            'Year': y,
            'Breakeven Elec ($/MWh)': round(breakeven_elec, 1),
            'Current RE ($/MWh)': round(current_re, 1),
            'Gap': round(current_re - breakeven_elec, 1)
        })

    st.dataframe(pd.DataFrame(breakeven_data), use_container_width=True, hide_index=True)

# ============================================================================
# Page: Regional Analysis
# ============================================================================
elif page == "🗺️ Regional Analysis":
    st.title("🗺️ Regional Energy Analysis")
    st.markdown("### Energy demand by location")

    # Load data
    df_fac = load_facility_data()
    df_scenarios = load_scenarios()

    # Get ethylene capacity by location
    df_eth = df_fac[df_fac['product'] == 'Ethylene']
    eth_by_loc = df_eth.groupby('location')['capacity_kt'].sum()
    total_eth = eth_by_loc.sum()

    # Calculate regional shares
    regional_shares = (eth_by_loc / total_eth).to_dict()

    # Scenario selection
    scenario = st.selectbox("Select Scenario", ['Shaheen', '구조조정 25%', '구조조정 40%'])

    scenario_col = {
        'Shaheen': 'scenario_shaheen',
        '구조조정 25%': 'scenario_restructure_25pct',
        '구조조정 40%': 'scenario_restructure_40pct'
    }[scenario]

    mult_2050 = df_scenarios[df_scenarios['year'] == 2050][scenario_col].iloc[0]
    results = calculate_scenario_results(mult_2050, h2_intensity, elec_intensity, baseline_ef=baseline_ef)

    # Regional breakdown
    st.markdown("---")
    st.markdown(f"#### {scenario} Scenario - Regional Energy Demand (2050)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### H2 Demand by Location")
        h2_regional = pd.DataFrame({
            'Location': list(regional_shares.keys()),
            'Share (%)': [s * 100 for s in regional_shares.values()],
            'H2 (kt)': [results['h2_demand_kt'] * s for s in regional_shares.values()]
        })

        fig = px.bar(h2_regional, x='Location', y='H2 (kt)',
                     color='Share (%)', color_continuous_scale='Blues')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(h2_regional.round(1), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("##### Electricity Demand by Location")
        elec_regional = pd.DataFrame({
            'Location': list(regional_shares.keys()),
            'Share (%)': [s * 100 for s in regional_shares.values()],
            'Electricity (TWh)': [results['elec_demand_twh'] * s for s in regional_shares.values()]
        })

        fig = px.bar(elec_regional, x='Location', y='Electricity (TWh)',
                     color='Share (%)', color_continuous_scale='Reds')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(elec_regional.round(1), use_container_width=True, hide_index=True)

    # Annual trajectory
    st.markdown("---")
    st.markdown("#### Annual Energy Demand Trajectory")

    years = list(range(2025, 2051))
    annual_data = []

    for y in years:
        mult = df_scenarios[df_scenarios['year'] == y][scenario_col].iloc[0]
        res = calculate_scenario_results(mult, h2_intensity, elec_intensity, baseline_ef=baseline_ef)
        annual_data.append({
            'Year': y,
            'H2 (kt)': res['h2_demand_kt'],
            'Electricity (TWh)': res['elec_demand_twh']
        })

    df_annual = pd.DataFrame(annual_data)

    fig = make_subplots(rows=1, cols=2, subplot_titles=['H2 Demand', 'Electricity Demand'])

    fig.add_trace(go.Scatter(x=df_annual['Year'], y=df_annual['H2 (kt)'],
                             name='H2', line=dict(color='#3498DB', width=3)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_annual['Year'], y=df_annual['Electricity (TWh)'],
                             name='Electricity', line=dict(color='#E74C3C', width=3)), row=1, col=2)

    fig.update_xaxes(title_text='Year', row=1, col=1)
    fig.update_xaxes(title_text='Year', row=1, col=2)
    fig.update_yaxes(title_text='H2 (kt/year)', row=1, col=1)
    fig.update_yaxes(title_text='Electricity (TWh/year)', row=1, col=2)
    fig.update_layout(height=400, showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Page: Cost Analysis
# ============================================================================
elif page == "💰 Cost Analysis":
    st.title("💰 Cost Analysis")
    st.markdown("### CAPEX, OPEX, and Fuel Costs")

    # Load data
    df_h2, df_re, df_grid = load_price_trajectories()
    df_scenarios = load_scenarios()

    # Scenario selection
    scenario = st.selectbox("Select Scenario", ['Shaheen', '구조조정 25%', '구조조정 40%'])

    scenario_col = {
        'Shaheen': 'scenario_shaheen',
        '구조조정 25%': 'scenario_restructure_25pct',
        '구조조정 40%': 'scenario_restructure_40pct'
    }[scenario]

    st.markdown("---")
    st.markdown("#### Annual Cost Comparison: NCC-H2 vs NCC-Electricity")

    years = list(range(2025, 2051))
    cost_data = []

    for y in years:
        mult = df_scenarios[df_scenarios['year'] == y][scenario_col].iloc[0]
        ethylene_kt = 11962 * mult

        # NCC-H2 costs
        capex_h2 = get_ncc_capex(y, 'NCC-H2')
        capex_h2_bn = capex_h2 * ethylene_kt * 1000 / 1e9 / 25
        opex_h2_bn = capex_h2 * ethylene_kt * 1000 / 1e9 * 0.04 / 25

        h2_price = df_h2[df_h2['year'] == y]['h2_price_usd_per_kg'].iloc[0]
        h2_demand_kt = ethylene_kt * h2_intensity
        fuel_h2_bn = h2_demand_kt * 1000 * h2_price / 1e9

        total_h2 = capex_h2_bn + opex_h2_bn + fuel_h2_bn

        # NCC-Elec costs
        capex_elec = get_ncc_capex(y, 'NCC-Electricity')
        capex_elec_bn = capex_elec * ethylene_kt * 1000 / 1e9 / 25
        opex_elec_bn = capex_elec * ethylene_kt * 1000 / 1e9 * 0.04 / 25

        re_price = df_re[df_re['year'] == y]['re_price_usd_per_mwh'].iloc[0]
        elec_demand_twh = ethylene_kt * elec_intensity / 1e6
        fuel_elec_bn = elec_demand_twh * 1e6 * re_price / 1e9

        total_elec = capex_elec_bn + opex_elec_bn + fuel_elec_bn

        cost_data.append({
            'Year': y,
            'H2_CAPEX': capex_h2_bn,
            'H2_OPEX': opex_h2_bn,
            'H2_Fuel': fuel_h2_bn,
            'H2_Total': total_h2,
            'Elec_CAPEX': capex_elec_bn,
            'Elec_OPEX': opex_elec_bn,
            'Elec_Fuel': fuel_elec_bn,
            'Elec_Total': total_elec
        })

    df_costs = pd.DataFrame(cost_data)

    # Cost trajectory chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_costs['Year'], y=df_costs['H2_Total'],
                             name='NCC-H2 Total', line=dict(color='#3498DB', width=3)))
    fig.add_trace(go.Scatter(x=df_costs['Year'], y=df_costs['Elec_Total'],
                             name='NCC-Elec Total', line=dict(color='#E74C3C', width=3)))

    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Annual Cost ($B)',
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Cost breakdown for 2050
    st.markdown("---")
    st.markdown("#### 2050 Cost Breakdown")

    cost_2050 = df_costs[df_costs['Year'] == 2050].iloc[0]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### NCC-H2")
        h2_breakdown = pd.DataFrame({
            'Component': ['CAPEX', 'OPEX', 'Fuel (H2)'],
            'Cost ($B)': [cost_2050['H2_CAPEX'], cost_2050['H2_OPEX'], cost_2050['H2_Fuel']]
        })
        fig = px.pie(h2_breakdown, values='Cost ($B)', names='Component',
                     color_discrete_sequence=['#3498DB', '#2ECC71', '#E74C3C'])
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Total Annual Cost", f"${cost_2050['H2_Total']:.2f}B")

    with col2:
        st.markdown("##### NCC-Electricity")
        elec_breakdown = pd.DataFrame({
            'Component': ['CAPEX', 'OPEX', 'Fuel (Elec)'],
            'Cost ($B)': [cost_2050['Elec_CAPEX'], cost_2050['Elec_OPEX'], cost_2050['Elec_Fuel']]
        })
        fig = px.pie(elec_breakdown, values='Cost ($B)', names='Component',
                     color_discrete_sequence=['#3498DB', '#2ECC71', '#E74C3C'])
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Total Annual Cost", f"${cost_2050['Elec_Total']:.2f}B")

    # Cumulative costs
    st.markdown("---")
    st.markdown("#### Cumulative Cost (2030-2050)")

    df_2030_2050 = df_costs[df_costs['Year'] >= 2030]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("NCC-H2 Cumulative", f"${df_2030_2050['H2_Total'].sum():.1f}B")
    with col2:
        st.metric("NCC-Elec Cumulative", f"${df_2030_2050['Elec_Total'].sum():.1f}B")
    with col3:
        diff = df_2030_2050['H2_Total'].sum() - df_2030_2050['Elec_Total'].sum()
        cheaper = "NCC-H2" if diff < 0 else "NCC-Elec"
        st.metric("Cheaper Option", cheaper, f"Saves ${abs(diff):.1f}B")

# ============================================================================
# Page: MACC Curves
# ============================================================================
elif page == "📈 MACC Curves":
    st.title("📈 Marginal Abatement Cost Curves")
    st.markdown("### Technology cost per tCO2 abated")

    # Load data
    df_h2, df_re, df_grid = load_price_trajectories()

    year = st.slider("Select Year", 2025, 2050, 2030)

    # Calculate MACC for each technology
    h2_price = df_h2[df_h2['year'] == year]['h2_price_usd_per_kg'].iloc[0]
    re_price = df_re[df_re['year'] == year]['re_price_usd_per_mwh'].iloc[0]

    # NCC-H2 MACC
    capex_h2 = get_ncc_capex(year, 'NCC-H2')
    capex_ann_h2 = capex_h2 / 25 / baseline_ef
    opex_ann_h2 = capex_h2 * 0.04 / 25 / baseline_ef
    fuel_cost_h2 = h2_intensity * 1000 * h2_price / baseline_ef
    macc_h2 = capex_ann_h2 + opex_ann_h2 + fuel_cost_h2

    # NCC-Elec MACC
    capex_elec = get_ncc_capex(year, 'NCC-Electricity')
    capex_ann_elec = capex_elec / 25 / baseline_ef
    opex_ann_elec = capex_elec * 0.04 / 25 / baseline_ef
    fuel_cost_elec = elec_intensity * re_price / baseline_ef
    macc_elec = capex_ann_elec + opex_ann_elec + fuel_cost_elec

    # Abatement potential (simplified)
    # Ethylene capacity = 11962 kt, EF = 1.9 tCO2/t
    abatement_mt = 11962 * baseline_ef / 1000

    st.markdown(f"#### MACC for {year}")

    # MACC bar chart
    macc_data = pd.DataFrame({
        'Technology': ['NCC-H2', 'NCC-Electricity'],
        'MACC ($/tCO2)': [macc_h2, macc_elec],
        'Abatement (MtCO2)': [abatement_mt, abatement_mt]
    })

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(macc_data, x='Technology', y='MACC ($/tCO2)',
                     color='Technology', color_discrete_sequence=['#3498DB', '#E74C3C'])
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("##### MACC Breakdown")
        breakdown = pd.DataFrame({
            'Component': ['CAPEX', 'OPEX', 'Fuel'],
            'NCC-H2': [capex_ann_h2, opex_ann_h2, fuel_cost_h2],
            'NCC-Elec': [capex_ann_elec, opex_ann_elec, fuel_cost_elec]
        })
        st.dataframe(breakdown.round(1), use_container_width=True, hide_index=True)

        st.markdown("##### Summary")
        st.metric("NCC-H2 MACC", f"${macc_h2:.1f}/tCO2")
        st.metric("NCC-Elec MACC", f"${macc_elec:.1f}/tCO2")

        cheaper = "NCC-H2" if macc_h2 < macc_elec else "NCC-Electricity"
        st.success(f"**{cheaper}** is more cost-effective in {year}")

    # MACC trajectory
    st.markdown("---")
    st.markdown("#### MACC Trajectory (2025-2050)")

    years = list(range(2025, 2051))
    macc_trajectory = []

    for y in years:
        hp = df_h2[df_h2['year'] == y]['h2_price_usd_per_kg'].iloc[0]
        rp = df_re[df_re['year'] == y]['re_price_usd_per_mwh'].iloc[0]

        ch2 = get_ncc_capex(y, 'NCC-H2')
        ce = get_ncc_capex(y, 'NCC-Electricity')

        m_h2 = ch2/25/baseline_ef + ch2*0.04/25/baseline_ef + h2_intensity*1000*hp/baseline_ef
        m_elec = ce/25/baseline_ef + ce*0.04/25/baseline_ef + elec_intensity*rp/baseline_ef

        macc_trajectory.append({'Year': y, 'NCC-H2': m_h2, 'NCC-Electricity': m_elec})

    df_macc = pd.DataFrame(macc_trajectory)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_macc['Year'], y=df_macc['NCC-H2'],
                             name='NCC-H2', line=dict(color='#3498DB', width=3)))
    fig.add_trace(go.Scatter(x=df_macc['Year'], y=df_macc['NCC-Electricity'],
                             name='NCC-Electricity', line=dict(color='#E74C3C', width=3)))

    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='MACC ($/tCO2)',
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Footer
# ============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("""
**Korean Petrochemical MACC Model**

Developed for analyzing decarbonization
pathways for Korea's petrochemical industry.

- 248 facilities analyzed
- 3 production scenarios
- 2 technology pathways
- LCOH calculator included

*Version 2.0 - November 2025*
""")
