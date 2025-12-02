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
def calculate_crf(discount_rate, lifetime):
    """
    Calculate Capital Recovery Factor (CRF)

    CRF = i(1+i)^n / ((1+i)^n - 1)

    Parameters:
    - discount_rate: Annual discount rate (e.g., 0.08 for 8%)
    - lifetime: Project lifetime in years

    Returns:
    - CRF value
    """
    i = discount_rate
    n = lifetime
    return (i * (1 + i)**n) / ((1 + i)**n - 1)


def calculate_lcoh(elec_price, capex, efficiency=0.70, lifetime=20, capacity_factor=0.90,
                   opex_pct=0.02, discount_rate=0.08, stack_replacement_cost=0.15, stack_lifetime=10):
    """
    Calculate Levelized Cost of Hydrogen (LCOH) using precise formula

    LCOH = (CAPEX × CRF + Fixed_OPEX + Stack_Replacement) / Annual_H2_Production + Variable_Electricity_Cost

    Parameters:
    - elec_price: Electricity price ($/MWh)
    - capex: Electrolyzer CAPEX ($/kW)
    - efficiency: Electrolyzer efficiency (HHV basis, 0.70 = 70%)
    - lifetime: System lifetime (years)
    - capacity_factor: Annual capacity factor
    - opex_pct: Fixed OPEX as % of CAPEX per year
    - discount_rate: WACC/discount rate for CRF calculation
    - stack_replacement_cost: Stack replacement as % of CAPEX
    - stack_lifetime: Years between stack replacements

    Returns:
    - Dictionary with LCOH breakdown in $/kg H2
    """
    # Constants
    H2_HHV = 39.4  # kWh/kg (Higher Heating Value of H2)
    HOURS_PER_YEAR = 8760

    # Electricity consumption per kg H2
    elec_per_kg_kwh = H2_HHV / efficiency  # kWh/kg H2

    # Annual operating hours
    operating_hours = HOURS_PER_YEAR * capacity_factor

    # H2 production per kW of electrolyzer capacity
    # 1 kW electrolyzer * operating_hours / elec_per_kg = kg H2/year/kW
    h2_per_kw_year = operating_hours / elec_per_kg_kwh  # kg H2/year per kW capacity

    # Capital Recovery Factor
    crf = calculate_crf(discount_rate, lifetime)

    # CAPEX component ($/kg H2)
    # CAPEX ($/kW) × CRF / H2 production (kg/kW/year)
    capex_component = (capex * crf) / h2_per_kw_year

    # Fixed OPEX component ($/kg H2)
    # OPEX ($/kW/year) / H2 production (kg/kW/year)
    fixed_opex_component = (capex * opex_pct) / h2_per_kw_year

    # Stack replacement component ($/kg H2) - annualized
    # Number of replacements over lifetime
    num_replacements = max(0, (lifetime // stack_lifetime) - 1)
    if num_replacements > 0:
        # NPV of stack replacements
        stack_npv = sum([stack_replacement_cost * capex / ((1 + discount_rate)**(stack_lifetime * (i+1)))
                         for i in range(int(num_replacements))])
        stack_component = (stack_npv * crf) / h2_per_kw_year
    else:
        stack_component = 0

    # Electricity cost component ($/kg H2)
    # elec_price ($/MWh) × elec_per_kg (kWh) / 1000
    elec_component = elec_price * elec_per_kg_kwh / 1000

    # Total LCOH
    lcoh = capex_component + fixed_opex_component + stack_component + elec_component

    return {
        'lcoh': lcoh,
        'capex_component': capex_component,
        'opex_component': fixed_opex_component,
        'stack_component': stack_component,
        'elec_component': elec_component,
        'elec_per_kg': elec_per_kg_kwh,
        'h2_per_kw_year': h2_per_kw_year,
        'crf': crf
    }

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
    """Get interpolated NCC technology CAPEX ($/t/yr capacity)"""
    if tech == 'NCC-H2':
        # Thunder Said Energy 2023: $1,700/t-C2H4/yr
        capex_schedule = {2025: 1700, 2030: 1300, 2040: 935, 2050: 780}
    else:  # NCC-Electricity
        # Toribio-Ramirez et al. 2025: $1,500/t-C2H4/yr
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


# ============================================================================
# Cost Calculation Functions (aligned with MODEL_DOCUMENTATION.md)
# ============================================================================
# Key parameters from the documentation (validated against literature)
BASELINE_EF = 1.9  # tCO2/ton ethylene (baseline combustion emissions)
H2_INTENSITY = 0.2  # ton H2/ton ethylene (Lummus Tech 2023: 200 kg/ton)
ELEC_INTENSITY = 5.0  # MWh/ton ethylene (BASF/SABIC/Linde 2024)
MWH_PER_TCO2_NCC_ELEC = 2.63  # MWh per tCO2 = 5.0 MWh/ton / 1.9 tCO2/ton
LIFETIME = 25  # years (technology lifetime)
OPEX_PCT = 0.04  # 4% of CAPEX


def calculate_macc(year, h2_price, re_price, tech='NCC-H2'):
    """
    Calculate MACC ($/tCO2) aligned with macc.py

    MACC = CAPEX_annual + OPEX_annual + Fuel_Cost_Diff

    Where:
    - CAPEX_annual = CAPEX / lifetime (simple, no CRF)
    - OPEX_annual = CAPEX * opex_pct / lifetime
    - Fuel_Cost_Diff = Fuel_cost_per_ton / abatement_per_ton
    """
    capex = get_ncc_capex(year, tech)

    # CAPEX and OPEX per tCO2 (from CAPEX $/t/yr)
    # CAPEX per ton ethylene = capex, divide by baseline EF to get per tCO2
    capex_ann_per_tco2 = capex / LIFETIME / BASELINE_EF  # $/tCO2/year
    opex_ann_per_tco2 = capex * OPEX_PCT / LIFETIME / BASELINE_EF  # $/tCO2/year

    if tech == 'NCC-H2':
        # H2 cost per ton ethylene
        h2_cost_per_ton = H2_INTENSITY * 1000 * h2_price  # $/ton ethylene
        fuel_cost_per_tco2 = h2_cost_per_ton / BASELINE_EF
    else:  # NCC-Electricity
        # Electricity cost per ton ethylene
        elec_cost_per_ton = ELEC_INTENSITY * re_price  # $/ton ethylene
        fuel_cost_per_tco2 = elec_cost_per_ton / BASELINE_EF

    macc = capex_ann_per_tco2 + opex_ann_per_tco2 + fuel_cost_per_tco2

    return {
        'macc': macc,
        'capex_ann': capex_ann_per_tco2,
        'opex_ann': opex_ann_per_tco2,
        'fuel_cost': fuel_cost_per_tco2
    }


def calculate_annual_cost(year, ethylene_kt, h2_price, re_price, tech='NCC-H2'):
    """
    Calculate annual costs aligned with MODEL_DOCUMENTATION.md

    Returns costs in $B/year

    Parameters:
    - H2_INTENSITY = 0.2 ton H2/ton ethylene
    - ELEC_INTENSITY = 5.0 MWh/ton ethylene
    """
    capex = get_ncc_capex(year, tech)  # $/t/yr capacity

    # CAPEX: Total investment amortized over lifetime
    # Total CAPEX = CAPEX ($/t/yr) * capacity (kt) * 1000 (t/kt)
    total_capex_musd = capex * ethylene_kt * 1000 / 1e6  # Million USD
    capex_ann_bn = total_capex_musd / LIFETIME / 1000  # $B/year

    # OPEX: % of total CAPEX
    opex_ann_bn = total_capex_musd * OPEX_PCT / LIFETIME / 1000  # $B/year

    if tech == 'NCC-H2':
        # H2 demand and cost
        h2_demand_kt = ethylene_kt * H2_INTENSITY
        fuel_cost_bn = h2_demand_kt * 1000 * h2_price / 1e9  # $B/year
    else:  # NCC-Electricity
        # Electricity demand = Ethylene (kt) * 5.0 MWh/ton / 1000 = TWh
        elec_demand_twh = ethylene_kt * ELEC_INTENSITY / 1000
        fuel_cost_bn = elec_demand_twh * re_price / 1000  # $B/year

    total_cost_bn = capex_ann_bn + opex_ann_bn + fuel_cost_bn

    return {
        'capex_ann_bn': capex_ann_bn,
        'opex_ann_bn': opex_ann_bn,
        'fuel_cost_bn': fuel_cost_bn,
        'total_ann_bn': total_cost_bn,
        'total_capex_musd': total_capex_musd
    }

def calculate_scenario_results(scenario_mult, h2_intensity=0.2, elec_intensity=5.0,
                               baseline_ethylene=11962, baseline_ef=1.9):
    """Calculate H2 and electricity demand for a production scenario

    Parameters (from MODEL_DOCUMENTATION.md):
    - h2_intensity: 0.2 ton H2/ton ethylene (Lummus Tech 2023)
    - elec_intensity: 5.0 MWh/ton ethylene (BASF/SABIC/Linde 2024)
    - baseline_ef: 1.9 tCO2/ton ethylene (baseline combustion emissions)

    Calculation:
    - H2 demand (kt) = Ethylene (kt) × H2 intensity
    - Electricity (TWh) = Ethylene (kt) × Elec intensity / 1000
    """
    ethylene_kt = baseline_ethylene * scenario_mult

    # H2 demand (kt) = Ethylene (kt) * H2 intensity
    h2_demand_kt = ethylene_kt * h2_intensity

    # BAU emissions (MtCO2) = Ethylene (kt) * baseline EF / 1000
    bau_emissions_mt = ethylene_kt * baseline_ef / 1000

    # Electricity demand (TWh) = Ethylene (kt) * Elec intensity (MWh/ton) / 1000
    elec_demand_twh = ethylene_kt * elec_intensity / 1000

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
     "🗺️ Regional Analysis", "💰 Cost Analysis", "📈 MACC Curves",
     "🔄 Facility Transition"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Model Parameters")

# Editable parameters in sidebar (defaults from MODEL_DOCUMENTATION.md)
h2_intensity = st.sidebar.slider("H2 Intensity (t/t C2H4)", 0.1, 0.4, 0.2, 0.01,
                                  help="Lummus Tech 2023: 0.2 ton H2/ton ethylene")
elec_intensity = st.sidebar.slider("Elec Intensity (MWh/t C2H4)", 4.0, 7.0, 5.0, 0.1,
                                    help="BASF/SABIC/Linde 2024: 5.0 MWh/ton")
baseline_ef = st.sidebar.slider("Baseline EF (tCO2/t C2H4)", 1.5, 2.5, 1.9, 0.1,
                                 help="Baseline combustion emissions")

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
    st.markdown("### Precise LCOH calculation with Capital Recovery Factor (CRF)")

    # Formula explanation
    with st.expander("📐 LCOH Formula Details"):
        st.markdown("""
        **Precise LCOH Formula:**

        ```
        LCOH = (CAPEX × CRF + Fixed_OPEX + Stack_Replacement) / H₂_Production + Electricity_Cost
        ```

        **Where:**
        - **CRF** = Capital Recovery Factor = `i(1+i)^n / ((1+i)^n - 1)`
        - **i** = Discount rate (WACC)
        - **n** = Project lifetime (years)
        - **H₂ Production** = Operating hours × Electrolyzer capacity / Electricity consumption per kg H₂
        - **Electricity per kg H₂** = H₂ HHV (39.4 kWh/kg) / Efficiency

        **Stack Replacement:**
        - Electrolyzers require stack replacement every ~10 years
        - Cost ~15% of original CAPEX, discounted to NPV
        """)

    # Load price data
    df_h2, df_re, df_grid = load_price_trajectories()

    # User inputs
    st.markdown("#### Electrolyzer Parameters")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        efficiency = st.slider("Efficiency (HHV)", 0.50, 0.85, 0.70, 0.01)
        lifetime = st.slider("Project Lifetime (years)", 15, 30, 20, 1)
    with col2:
        capacity_factor = st.slider("Capacity Factor", 0.50, 0.98, 0.90, 0.01)
        opex_pct = st.slider("Fixed OPEX (% of CAPEX/yr)", 0.01, 0.05, 0.02, 0.005)
    with col3:
        discount_rate = st.slider("Discount Rate (WACC)", 0.04, 0.12, 0.08, 0.01)
        stack_lifetime = st.slider("Stack Lifetime (years)", 7, 15, 10, 1)
    with col4:
        year = st.slider("Year", 2025, 2050, 2030)
        custom_elec_price = st.checkbox("Use Custom Electricity Price")

    if custom_elec_price:
        elec_price = st.slider("Electricity Price ($/MWh)", 30.0, 250.0, 100.0, 5.0)
    else:
        elec_price = df_re[df_re['year'] == year]['re_price_usd_per_mwh'].iloc[0]

    # Calculate LCOH with new precise formula
    capex = get_electrolyzer_capex(year)
    lcoh_result = calculate_lcoh(
        elec_price, capex, efficiency, lifetime, capacity_factor,
        opex_pct, discount_rate, stack_replacement_cost=0.15, stack_lifetime=stack_lifetime
    )
    lcoh = lcoh_result['lcoh']
    market_h2 = df_h2[df_h2['year'] == year]['h2_price_usd_per_kg'].iloc[0]

    st.markdown("---")
    st.markdown("#### Results")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Electrolyzer CAPEX", f"${capex:,.0f}/kW")
        st.metric("CRF", f"{lcoh_result['crf']:.4f}")
    with col2:
        st.metric("Electricity Price", f"${elec_price:.1f}/MWh")
        st.metric("Elec per kg H₂", f"{lcoh_result['elec_per_kg']:.1f} kWh")
    with col3:
        st.metric("**LCOH**", f"${lcoh:.2f}/kg",
                  delta=f"vs Market: ${lcoh - market_h2:+.2f}")
    with col4:
        st.metric("Market H2 Price", f"${market_h2:.2f}/kg")
        st.metric("H₂/kW/year", f"{lcoh_result['h2_per_kw_year']:.0f} kg")

    # Recommendation
    if lcoh < market_h2:
        st.success(f"✅ **Make H₂**: LCOH (${lcoh:.2f}/kg) is cheaper than buying (${market_h2:.2f}/kg)")
    else:
        st.warning(f"⚠️ **Buy H₂**: Market price (${market_h2:.2f}/kg) is cheaper than LCOH (${lcoh:.2f}/kg)")

    st.markdown("---")

    # LCOH breakdown
    st.markdown("#### LCOH Cost Breakdown")

    col1, col2 = st.columns([1, 1])

    with col1:
        breakdown = pd.DataFrame({
            'Component': ['CAPEX (annualized)', 'Fixed OPEX', 'Stack Replacement', 'Electricity'],
            'Cost ($/kg)': [
                lcoh_result['capex_component'],
                lcoh_result['opex_component'],
                lcoh_result['stack_component'],
                lcoh_result['elec_component']
            ]
        })

        fig = px.pie(breakdown, values='Cost ($/kg)', names='Component',
                     color_discrete_sequence=['#3498DB', '#2ECC71', '#9B59B6', '#E74C3C'])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("##### Cost Components")
        st.dataframe(breakdown.round(3), use_container_width=True, hide_index=True)

        st.markdown("##### Key Parameters")
        params_df = pd.DataFrame({
            'Parameter': ['Efficiency', 'Capacity Factor', 'Discount Rate', 'Lifetime', 'Stack Life'],
            'Value': [f"{efficiency:.0%}", f"{capacity_factor:.0%}", f"{discount_rate:.0%}",
                     f"{lifetime} years", f"{stack_lifetime} years"]
        })
        st.dataframe(params_df, use_container_width=True, hide_index=True)

    # LCOH trajectory
    st.markdown("---")
    st.markdown("#### LCOH vs Market H2 Price Trajectory")

    years = list(range(2025, 2051))
    lcoh_trajectory = []
    market_trajectory = []

    for y in years:
        cap = get_electrolyzer_capex(y)
        ep = df_re[df_re['year'] == y]['re_price_usd_per_mwh'].iloc[0]
        result = calculate_lcoh(ep, cap, efficiency, lifetime, capacity_factor,
                               opex_pct, discount_rate, 0.15, stack_lifetime)
        lcoh_trajectory.append(result['lcoh'])
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
    st.markdown("*At what electricity price does LCOH equal market H₂ price?*")

    H2_HHV = 39.4
    elec_per_kg = H2_HHV / efficiency

    breakeven_data = []
    for y in [2025, 2030, 2040, 2050]:
        cap = get_electrolyzer_capex(y)
        mkt = df_h2[df_h2['year'] == y]['h2_price_usd_per_kg'].iloc[0]

        # Calculate fixed costs using CRF
        crf = calculate_crf(discount_rate, lifetime)
        h2_per_kw_year = (8760 * capacity_factor) / elec_per_kg
        fixed_costs = (cap * crf + cap * opex_pct) / h2_per_kw_year

        # Add stack replacement
        num_replacements = max(0, (lifetime // stack_lifetime) - 1)
        if num_replacements > 0:
            stack_npv = sum([0.15 * cap / ((1 + discount_rate)**(stack_lifetime * (i+1)))
                             for i in range(int(num_replacements))])
            fixed_costs += (stack_npv * crf) / h2_per_kw_year

        # Breakeven: mkt = fixed_costs + elec_price * elec_per_kg / 1000
        breakeven_elec = (mkt - fixed_costs) * 1000 / elec_per_kg
        current_re = df_re[df_re['year'] == y]['re_price_usd_per_mwh'].iloc[0]

        breakeven_data.append({
            'Year': y,
            'Market H₂ ($/kg)': round(mkt, 2),
            'Fixed Costs ($/kg)': round(fixed_costs, 2),
            'Breakeven Elec ($/MWh)': round(max(0, breakeven_elec), 1),
            'Current RE ($/MWh)': round(current_re, 1),
            'Gap': round(current_re - max(0, breakeven_elec), 1)
        })

    st.dataframe(pd.DataFrame(breakeven_data), use_container_width=True, hide_index=True)

    st.info("**Note:** Negative breakeven prices indicate that even with free electricity, "
            "the CAPEX/OPEX costs exceed market H₂ price. Gap = Current RE - Breakeven (positive = RE too expensive)")

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
    st.markdown("### CAPEX, OPEX, and Fuel Costs (Aligned with MODEL_DOCUMENTATION.md)")

    # Show key parameters
    with st.expander("📐 Cost Calculation Parameters (from MODEL_DOCUMENTATION.md)"):
        st.markdown(f"""
        **Key Parameters (validated against literature):**
        - **Baseline EF**: {BASELINE_EF} tCO₂/ton ethylene
        - **H₂ Intensity**: {H2_INTENSITY} ton H₂/ton ethylene (Lummus Tech 2023)
        - **Elec Intensity**: {ELEC_INTENSITY} MWh/ton ethylene (BASF/SABIC/Linde 2024)
        - **Lifetime**: {LIFETIME} years
        - **OPEX**: {OPEX_PCT*100:.0f}% of CAPEX/year

        **CAPEX ($/t-C₂H₄/yr):**
        - NCC-H₂: $1,700 (2025) → $780 (2050) [Thunder Said Energy 2023]
        - NCC-Elec: $1,500 (2025) → $900 (2050) [Toribio-Ramirez 2025]

        **MACC Formula:**
        ```
        MACC ($/tCO₂) = CAPEX_ann + OPEX_ann + Fuel_Cost_Diff

        For NCC-H₂:
          Fuel_Cost = H₂_price ($/kg) × 0.2 (t H₂/t) × 1000 / 1.9 (tCO₂/t)

        For NCC-Elec:
          Fuel_Cost = RE_price ($/MWh) × 5.0 (MWh/t) / 1.9 (tCO₂/t)
        ```
        """)

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

        h2_price = df_h2[df_h2['year'] == y]['h2_price_usd_per_kg'].iloc[0]
        re_price = df_re[df_re['year'] == y]['re_price_usd_per_mwh'].iloc[0]

        # Use aligned cost calculation functions
        h2_costs = calculate_annual_cost(y, ethylene_kt, h2_price, re_price, 'NCC-H2')
        elec_costs = calculate_annual_cost(y, ethylene_kt, h2_price, re_price, 'NCC-Electricity')

        cost_data.append({
            'Year': y,
            'H2_CAPEX': h2_costs['capex_ann_bn'],
            'H2_OPEX': h2_costs['opex_ann_bn'],
            'H2_Fuel': h2_costs['fuel_cost_bn'],
            'H2_Total': h2_costs['total_ann_bn'],
            'H2_Total_CAPEX_MUSD': h2_costs['total_capex_musd'],
            'Elec_CAPEX': elec_costs['capex_ann_bn'],
            'Elec_OPEX': elec_costs['opex_ann_bn'],
            'Elec_Fuel': elec_costs['fuel_cost_bn'],
            'Elec_Total': elec_costs['total_ann_bn'],
            'Elec_Total_CAPEX_MUSD': elec_costs['total_capex_musd']
        })

    df_costs = pd.DataFrame(cost_data)

    # Calculate cumulative costs
    df_costs['H2_Cumulative'] = df_costs['H2_Total'].cumsum()
    df_costs['Elec_Cumulative'] = df_costs['Elec_Total'].cumsum()

    # Cost trajectory chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_costs['Year'], y=df_costs['H2_Total'],
                             name='NCC-H2 Annual', line=dict(color='#3498DB', width=3)))
    fig.add_trace(go.Scatter(x=df_costs['Year'], y=df_costs['Elec_Total'],
                             name='NCC-Elec Annual', line=dict(color='#E74C3C', width=3)))

    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Annual Cost ($B/year)',
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
            'Component': ['CAPEX (annualized)', 'OPEX', 'Fuel (H₂)'],
            'Cost ($B/yr)': [cost_2050['H2_CAPEX'], cost_2050['H2_OPEX'], cost_2050['H2_Fuel']]
        })
        fig = px.pie(h2_breakdown, values='Cost ($B/yr)', names='Component',
                     color_discrete_sequence=['#3498DB', '#2ECC71', '#E74C3C'])
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Annual Cost (2050)", f"${cost_2050['H2_Total']:.2f}B/yr")
        st.metric("Total CAPEX Investment", f"${cost_2050['H2_Total_CAPEX_MUSD']:,.0f}M")

    with col2:
        st.markdown("##### NCC-Electricity")
        elec_breakdown = pd.DataFrame({
            'Component': ['CAPEX (annualized)', 'OPEX', 'Fuel (Elec)'],
            'Cost ($B/yr)': [cost_2050['Elec_CAPEX'], cost_2050['Elec_OPEX'], cost_2050['Elec_Fuel']]
        })
        fig = px.pie(elec_breakdown, values='Cost ($B/yr)', names='Component',
                     color_discrete_sequence=['#3498DB', '#2ECC71', '#E74C3C'])
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Annual Cost (2050)", f"${cost_2050['Elec_Total']:.2f}B/yr")
        st.metric("Total CAPEX Investment", f"${cost_2050['Elec_Total_CAPEX_MUSD']:,.0f}M")

    # ========================================
    # ACCUMULATED COST ANALYSIS
    # ========================================
    st.markdown("---")
    st.markdown("### 📊 Accumulated (Cumulative) Cost Analysis")

    # Cumulative cost chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_costs['Year'], y=df_costs['H2_Cumulative'],
                             name='NCC-H2 Cumulative', line=dict(color='#3498DB', width=3),
                             fill='tozeroy', fillcolor='rgba(52, 152, 219, 0.2)'))
    fig.add_trace(go.Scatter(x=df_costs['Year'], y=df_costs['Elec_Cumulative'],
                             name='NCC-Elec Cumulative', line=dict(color='#E74C3C', width=3),
                             fill='tozeroy', fillcolor='rgba(231, 76, 60, 0.2)'))

    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Cumulative Cost ($B)',
        height=450,
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        title='Accumulated Costs Over Time (2025-2050)'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Cumulative cost table by periods
    st.markdown("#### Cumulative Costs by Period")

    periods = [
        ('2025-2030', 2025, 2030),
        ('2030-2040', 2030, 2040),
        ('2040-2050', 2040, 2050),
        ('2025-2050 (Total)', 2025, 2050)
    ]

    period_data = []
    for period_name, start, end in periods:
        df_period = df_costs[(df_costs['Year'] >= start) & (df_costs['Year'] <= end)]
        h2_cum = df_period['H2_Total'].sum()
        elec_cum = df_period['Elec_Total'].sum()
        diff = h2_cum - elec_cum
        cheaper = "NCC-H2" if diff < 0 else "NCC-Elec"
        period_data.append({
            'Period': period_name,
            'NCC-H2 ($B)': round(h2_cum, 2),
            'NCC-Elec ($B)': round(elec_cum, 2),
            'Difference ($B)': round(diff, 2),
            'Cheaper Option': cheaper
        })

    df_periods = pd.DataFrame(period_data)
    st.dataframe(df_periods, use_container_width=True, hide_index=True)

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total_h2 = df_costs['H2_Total'].sum()
    total_elec = df_costs['Elec_Total'].sum()
    diff = total_h2 - total_elec

    with col1:
        st.metric("NCC-H2 Total (2025-2050)", f"${total_h2:.1f}B")
    with col2:
        st.metric("NCC-Elec Total (2025-2050)", f"${total_elec:.1f}B")
    with col3:
        cheaper = "NCC-H2" if diff < 0 else "NCC-Elec"
        st.metric("Cheaper Option", cheaper)
    with col4:
        st.metric("Savings", f"${abs(diff):.1f}B")

    # Cost per tCO2 comparison
    st.markdown("---")
    st.markdown("#### MACC Comparison ($/tCO₂)")

    macc_data = []
    for y in [2025, 2030, 2040, 2050]:
        h2_price = df_h2[df_h2['year'] == y]['h2_price_usd_per_kg'].iloc[0]
        re_price = df_re[df_re['year'] == y]['re_price_usd_per_mwh'].iloc[0]

        h2_macc = calculate_macc(y, h2_price, re_price, 'NCC-H2')
        elec_macc = calculate_macc(y, h2_price, re_price, 'NCC-Electricity')

        macc_data.append({
            'Year': y,
            'H₂ Price ($/kg)': round(h2_price, 2),
            'RE Price ($/MWh)': round(re_price, 1),
            'NCC-H2 MACC ($/tCO₂)': round(h2_macc['macc'], 1),
            'NCC-Elec MACC ($/tCO₂)': round(elec_macc['macc'], 1),
            'Cheaper': 'NCC-H2' if h2_macc['macc'] < elec_macc['macc'] else 'NCC-Elec'
        })

    df_macc = pd.DataFrame(macc_data)
    st.dataframe(df_macc, use_container_width=True, hide_index=True)

# ============================================================================
# Page: MACC Curves
# ============================================================================
elif page == "📈 MACC Curves":
    st.title("📈 Marginal Abatement Cost Curves")
    st.markdown("### Technology cost per tCO₂ abated (Aligned with MODEL_DOCUMENTATION.md)")

    # Load data
    df_h2, df_re, df_grid = load_price_trajectories()

    year = st.slider("Select Year", 2025, 2050, 2030)

    # Calculate MACC using aligned function
    h2_price = df_h2[df_h2['year'] == year]['h2_price_usd_per_kg'].iloc[0]
    re_price = df_re[df_re['year'] == year]['re_price_usd_per_mwh'].iloc[0]

    h2_macc = calculate_macc(year, h2_price, re_price, 'NCC-H2')
    elec_macc = calculate_macc(year, h2_price, re_price, 'NCC-Electricity')

    # Abatement potential (simplified)
    # Ethylene capacity = 11962 kt, EF = 1.9 tCO2/t
    abatement_mt = 11962 * BASELINE_EF / 1000

    st.markdown(f"#### MACC for {year}")

    # MACC bar chart
    macc_data = pd.DataFrame({
        'Technology': ['NCC-H2', 'NCC-Electricity'],
        'MACC ($/tCO₂)': [h2_macc['macc'], elec_macc['macc']],
        'Abatement (MtCO₂)': [abatement_mt, abatement_mt]
    })

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(macc_data, x='Technology', y='MACC ($/tCO₂)',
                     color='Technology', color_discrete_sequence=['#3498DB', '#E74C3C'])
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("##### MACC Breakdown ($/tCO₂)")
        breakdown = pd.DataFrame({
            'Component': ['CAPEX (annualized)', 'OPEX', 'Fuel Cost'],
            'NCC-H2': [h2_macc['capex_ann'], h2_macc['opex_ann'], h2_macc['fuel_cost']],
            'NCC-Elec': [elec_macc['capex_ann'], elec_macc['opex_ann'], elec_macc['fuel_cost']]
        })
        st.dataframe(breakdown.round(1), use_container_width=True, hide_index=True)

        st.markdown("##### Summary")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("NCC-H2 MACC", f"${h2_macc['macc']:.1f}/tCO₂")
        with col_b:
            st.metric("NCC-Elec MACC", f"${elec_macc['macc']:.1f}/tCO₂")

        cheaper = "NCC-H2" if h2_macc['macc'] < elec_macc['macc'] else "NCC-Electricity"
        st.success(f"**{cheaper}** is more cost-effective in {year}")

        # Show input prices
        st.markdown("##### Input Prices")
        st.write(f"- H₂ Price: ${h2_price:.2f}/kg")
        st.write(f"- RE Price: ${re_price:.1f}/MWh")

    # MACC trajectory
    st.markdown("---")
    st.markdown("#### MACC Trajectory (2025-2050)")

    years = list(range(2025, 2051))
    macc_trajectory = []

    for y in years:
        hp = df_h2[df_h2['year'] == y]['h2_price_usd_per_kg'].iloc[0]
        rp = df_re[df_re['year'] == y]['re_price_usd_per_mwh'].iloc[0]

        h2_m = calculate_macc(y, hp, rp, 'NCC-H2')
        elec_m = calculate_macc(y, hp, rp, 'NCC-Electricity')

        macc_trajectory.append({
            'Year': y,
            'NCC-H2': h2_m['macc'],
            'NCC-Electricity': elec_m['macc']
        })

    df_macc_traj = pd.DataFrame(macc_trajectory)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_macc_traj['Year'], y=df_macc_traj['NCC-H2'],
                             name='NCC-H2', line=dict(color='#3498DB', width=3)))
    fig.add_trace(go.Scatter(x=df_macc_traj['Year'], y=df_macc_traj['NCC-Electricity'],
                             name='NCC-Electricity', line=dict(color='#E74C3C', width=3)))

    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='MACC ($/tCO₂)',
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    # MACC data table
    st.markdown("---")
    st.markdown("#### MACC Data Table")

    macc_table = []
    for y in [2025, 2030, 2035, 2040, 2045, 2050]:
        hp = df_h2[df_h2['year'] == y]['h2_price_usd_per_kg'].iloc[0]
        rp = df_re[df_re['year'] == y]['re_price_usd_per_mwh'].iloc[0]

        h2_m = calculate_macc(y, hp, rp, 'NCC-H2')
        elec_m = calculate_macc(y, hp, rp, 'NCC-Electricity')

        macc_table.append({
            'Year': y,
            'H₂ Price ($/kg)': round(hp, 2),
            'RE Price ($/MWh)': round(rp, 1),
            'NCC-H2 MACC': round(h2_m['macc'], 1),
            'NCC-Elec MACC': round(elec_m['macc'], 1),
            'Difference': round(h2_m['macc'] - elec_m['macc'], 1),
            'Cheaper': 'NCC-H2' if h2_m['macc'] < elec_m['macc'] else 'NCC-Elec'
        })

    st.dataframe(pd.DataFrame(macc_table), use_container_width=True, hide_index=True)

# ============================================================================
# Page: Facility Transition
# ============================================================================
elif page == "🔄 Facility Transition":
    st.title("🔄 Facility Transition Timeline")
    st.markdown("### How 248 Facilities Transition to Clean Technology")

    # Load facility data
    df_fac = load_facility_data()

    # Key stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Facilities", len(df_fac))
    with col2:
        st.metric("Average Age (2025)", f"{df_fac['age_2025'].mean():.1f} years")
    with col3:
        past_40 = len(df_fac[df_fac['age_2025'] > 40])
        st.metric("Past 40-yr Lifespan", past_40)
    with col4:
        oldest = df_fac['year_built'].min()
        st.metric("Oldest Facility", f"{oldest} ({2025-oldest} yrs)")

    st.markdown("---")

    # Transition assumption selection
    st.markdown("#### Transition Assumptions")
    col1, col2 = st.columns(2)

    with col1:
        lifespan = st.slider("Facility Lifespan (years)", 30, 50, 40, 5)
        st.info(f"Facilities retire after {lifespan} years of operation")

    with col2:
        transition_tech = st.selectbox(
            "Transition Technology",
            ["NCC-H2 (Hydrogen Cracker)", "NCC-Electricity (Electric Cracker)", "Mixed (Optimized)"]
        )

    # Calculate retirement years based on selected lifespan
    df_fac['retirement_year'] = df_fac['year_built'] + lifespan
    df_fac['retirement_year'] = df_fac['retirement_year'].clip(lower=2025)

    st.markdown("---")

    # Retirement timeline by complex
    st.markdown("#### Cumulative Retirement Timeline by Complex")

    years = list(range(2025, 2061))
    complex_order = ['Ulsan Complex', 'Yeosu Complex', 'Daesan Complex', 'Other Regions']
    complex_colors = {
        'Ulsan Complex': '#E74C3C',
        'Yeosu Complex': '#3498DB',
        'Daesan Complex': '#2ECC71',
        'Other Regions': '#9B59B6'
    }

    retirement_data = []
    for y in years:
        row = {'Year': y}
        for complex_name in complex_order:
            subset = df_fac[df_fac['complex'] == complex_name]
            retired = len(subset[subset['retirement_year'] <= y])
            row[complex_name] = retired
        row['Total'] = len(df_fac[df_fac['retirement_year'] <= y])
        retirement_data.append(row)

    df_retirement = pd.DataFrame(retirement_data)

    # Stacked area chart
    fig = go.Figure()
    for complex_name in complex_order:
        fig.add_trace(go.Scatter(
            x=df_retirement['Year'],
            y=df_retirement[complex_name],
            name=complex_name,
            mode='lines',
            stackgroup='one',
            line=dict(color=complex_colors[complex_name])
        ))

    fig.add_hline(y=248, line_dash="dash", line_color="black",
                  annotation_text="Total: 248 facilities")
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Cumulative Facilities Retired/Transitioned',
        height=450,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Key milestones
    st.markdown("---")
    st.markdown("#### Key Transition Milestones")

    milestones = []
    for pct in [25, 50, 75, 100]:
        target = int(248 * pct / 100)
        year_reached = df_retirement[df_retirement['Total'] >= target]['Year'].min()
        milestones.append({
            'Milestone': f"{pct}% Transitioned",
            'Facilities': target,
            'Year Reached': year_reached if pd.notna(year_reached) else '>2060'
        })

    st.dataframe(pd.DataFrame(milestones), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Annual transition schedule
    st.markdown("#### Annual Transition Schedule (First 15 years)")

    # Calculate new retirements per year
    annual_schedule = []
    for y in range(2025, 2041):
        new_retirements = len(df_fac[df_fac['retirement_year'] == y])
        cum_retired = len(df_fac[df_fac['retirement_year'] <= y])
        remaining = 248 - cum_retired
        annual_schedule.append({
            'Year': y,
            'New Transitions': new_retirements,
            'Cumulative': cum_retired,
            'Remaining': remaining,
            'Progress (%)': round(cum_retired / 248 * 100, 1)
        })

    df_schedule = pd.DataFrame(annual_schedule)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(df_schedule, x='Year', y='New Transitions',
                     color='New Transitions', color_continuous_scale='Reds')
        fig.update_layout(height=350, title='New Transitions per Year')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.line(df_schedule, x='Year', y='Cumulative',
                      markers=True, line_shape='linear')
        fig.add_hline(y=248, line_dash="dash", line_color="gray")
        fig.update_layout(height=350, title='Cumulative Transitions')
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_schedule, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Capacity transition
    st.markdown("#### Capacity Transition by Process Type")

    # Filter NCC products
    ncc_products = ['Ethylene', 'Propylene', 'Butadiene']
    df_ncc = df_fac[df_fac['product'].isin(ncc_products)]

    capacity_transition = []
    for y in range(2025, 2056, 5):
        ncc_retired_cap = df_ncc[df_ncc['retirement_year'] <= y]['capacity_kt'].sum()
        ncc_total_cap = df_ncc['capacity_kt'].sum()
        btx_retired_cap = df_fac[df_fac['process'] == 'BTX Plant'][df_fac['retirement_year'] <= y]['capacity_kt'].sum()
        btx_total_cap = df_fac[df_fac['process'] == 'BTX Plant']['capacity_kt'].sum()

        capacity_transition.append({
            'Year': y,
            'NCC Transitioned (kt)': round(ncc_retired_cap),
            'NCC Total (kt)': round(ncc_total_cap),
            'NCC (%)': round(ncc_retired_cap / ncc_total_cap * 100, 1) if ncc_total_cap > 0 else 0,
            'BTX Transitioned (kt)': round(btx_retired_cap),
            'BTX Total (kt)': round(btx_total_cap),
            'BTX (%)': round(btx_retired_cap / btx_total_cap * 100, 1) if btx_total_cap > 0 else 0
        })

    df_cap_trans = pd.DataFrame(capacity_transition)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_cap_trans['Year'], y=df_cap_trans['NCC (%)'],
                         name='NCC Facilities', marker_color='#E74C3C'))
    fig.add_trace(go.Bar(x=df_cap_trans['Year'], y=df_cap_trans['BTX (%)'],
                         name='BTX Facilities', marker_color='#3498DB'))
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Capacity Transitioned (%)',
        barmode='group',
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_cap_trans, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Facility detail table
    st.markdown("#### Facility Transition Detail")

    show_filter = st.selectbox("Filter by", ["All", "Ulsan Complex", "Yeosu Complex", "Daesan Complex", "Other Regions"])

    if show_filter == "All":
        df_display = df_fac
    else:
        df_display = df_fac[df_fac['complex'] == show_filter]

    # Sort by retirement year
    df_display = df_display.sort_values('retirement_year')

    # Select columns to display
    display_cols = ['product', 'company', 'location', 'complex', 'capacity_kt',
                    'year_built', 'age_2025', 'retirement_year']
    df_display = df_display[display_cols].copy()
    df_display.columns = ['Product', 'Company', 'Location', 'Complex', 'Capacity (kt)',
                          'Year Built', 'Age (2025)', 'Transition Year']

    st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)

    # Summary stats
    st.markdown("---")
    st.markdown("#### Summary Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### By Complex")
        complex_summary = df_fac.groupby('complex').agg({
            'capacity_kt': 'sum',
            'product': 'count',
            'age_2025': 'mean'
        }).round(1)
        complex_summary.columns = ['Capacity (kt)', 'Facilities', 'Avg Age']
        st.dataframe(complex_summary, use_container_width=True)

    with col2:
        st.markdown("##### By Process")
        process_summary = df_fac.groupby('process').agg({
            'capacity_kt': 'sum',
            'product': 'count',
            'age_2025': 'mean'
        }).round(1)
        process_summary.columns = ['Capacity (kt)', 'Facilities', 'Avg Age']
        st.dataframe(process_summary, use_container_width=True)

    with col3:
        st.markdown("##### Transition Technology Impact")
        total_capacity = df_ncc['capacity_kt'].sum()
        h2_demand = total_capacity * 0.56  # kt H2
        elec_demand = total_capacity * 5.0 / 1000  # TWh

        tech_impact = pd.DataFrame({
            'Metric': ['Total NCC Capacity', 'H₂ Demand (NCC-H2)', 'Elec Demand (NCC-Elec)'],
            'Value': [f"{total_capacity:,.0f} kt", f"{h2_demand:,.0f} kt/yr", f"{elec_demand:,.1f} TWh/yr"]
        })
        st.dataframe(tech_impact, use_container_width=True, hide_index=True)

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
- LCOH calculator with CRF
- Facility transition timeline

*Version 2.1 - November 2025*
""")
