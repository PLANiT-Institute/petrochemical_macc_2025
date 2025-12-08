"""
Korea Petrochemical Net Zero - Regional Analysis
================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Korea Petrochemical Net Zero", page_icon="🏭", layout="wide")

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SCENARIOS_DIR = DATA_DIR / "scenarios"

# Scenario info
SCENARIOS = {
    'shaheen_ncc_h2': 'Shaheen + NCC-H2',
    'shaheen_ncc_electricity': 'Shaheen + NCC-Elec',
    'restructure_25pct_ncc_h2': 'Restructure 25% + NCC-H2',
    'restructure_25pct_ncc_electricity': 'Restructure 25% + NCC-Elec',
    'restructure_40pct_ncc_h2': 'Restructure 40% + NCC-H2',
    'restructure_40pct_ncc_electricity': 'Restructure 40% + NCC-Elec',
}

# Load scenario data
@st.cache_data
def load_scenarios():
    data = {}
    for sid, name in SCENARIOS.items():
        path = SCENARIOS_DIR / f"{sid}.csv"
        if path.exists():
            df = pd.read_csv(path)
            df['scenario'] = name
            data[sid] = df
    return data

@st.cache_data
def load_assumptions():
    data = {}
    try:
        data['tech'] = pd.read_csv(DATA_DIR / "technology_parameters.csv")
        data['h2'] = pd.read_csv(DATA_DIR / "h2_price_trajectory.csv")
        data['re'] = pd.read_csv(DATA_DIR / "re_price_trajectory.csv")
        data['grid'] = pd.read_csv(DATA_DIR / "grid_emission_trajectory.csv")
        data['fac'] = pd.read_csv(DATA_DIR / "facility_database_with_regions.csv")
    except Exception as e:
        st.error(f"Error: {e}")
    return data

scenarios = load_scenarios()
assumptions = load_assumptions()

# Sidebar
st.sidebar.title("🏭 Net Zero Dashboard")
page = st.sidebar.radio("Navigation", ["📋 Assumptions", "🗺️ Regional Transitions", "⚡ Energy Demand"])
st.sidebar.markdown("---")
st.sidebar.info(f"**Scenarios:** {len(scenarios)}\n\n**Period:** 2025-2050\n\n**NO CCS/CCUS**")

# ===================== ASSUMPTIONS =====================
if page == "📋 Assumptions":
    st.title("📋 Key Assumptions")

    # Technology CAPEX
    st.header("1. Technology CAPEX Learning Curve")
    if 'tech' in assumptions:
        tech = assumptions['tech']
        col1, col2 = st.columns(2)

        with col1:
            capex_data = []
            for _, r in tech.iterrows():
                if r['technology'] != 'RE_PPA':
                    for y in [2025, 2030, 2040, 2050]:
                        capex_data.append({'Technology': r['technology'].replace('_', ' '), 'Year': y, 'CAPEX': r[f'capex_{y}_musd_per_mtco2']})
            fig = px.line(pd.DataFrame(capex_data), x='Year', y='CAPEX', color='Technology', markers=True, title='CAPEX (M$/MtCO2)')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.dataframe(tech[['technology', 'applies_to', 'trl', 'available_year', 'capex_2025_musd_per_mtco2', 'capex_2050_musd_per_mtco2']], hide_index=True)

    st.markdown("---")

    # Prices
    st.header("2. Price Trajectories")
    col1, col2, col3 = st.columns(3)

    with col1:
        if 'h2' in assumptions:
            h2 = assumptions['h2']
            fig = px.line(h2, x='year', y='h2_price_usd_per_kg', title='Green H2 ($/kg)')
            fig.add_hline(y=2.0, line_dash="dash", line_color="green")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if 're' in assumptions:
            fig = px.line(assumptions['re'], x='year', y='re_price_usd_per_mwh', title='RE Price ($/MWh)')
            st.plotly_chart(fig, use_container_width=True)

    with col3:
        if 'grid' in assumptions:
            fig = px.area(assumptions['grid'], x='year', y='grid_ef_tco2_per_mwh', title='Grid EF (tCO2/MWh)')
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Facilities
    st.header("3. Facility Coverage")
    if 'fac' in assumptions:
        fac = assumptions['fac']
        col1, col2, col3 = st.columns(3)
        col1.metric("Facilities", len(fac))
        col2.metric("Capacity", f"{fac['capacity_kt'].sum():,.0f} kt")
        col3.metric("Regions", fac['location'].nunique())

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(fac.groupby('location')['capacity_kt'].sum().reset_index(), values='capacity_kt', names='location', title='By Region')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.bar(fac.groupby('product')['capacity_kt'].sum().reset_index(), x='product', y='capacity_kt', title='By Product', color='product')
            st.plotly_chart(fig, use_container_width=True)

# ===================== REGIONAL TRANSITIONS =====================
elif page == "🗺️ Regional Transitions":
    st.title("🗺️ Regional Transitions")

    if not scenarios:
        st.error("No scenario data. Check data/scenarios/ folder.")
    else:
        selected = st.multiselect("Select Scenarios", list(scenarios.keys()), default=list(scenarios.keys())[:2], format_func=lambda x: SCENARIOS[x])

        if selected:
            st.markdown("---")

            # Technology Deployment
            st.header("1. Technology Deployment")
            for sid in selected:
                df = scenarios[sid]
                st.subheader(f"📊 {SCENARIOS[sid]}")

                col1, col2 = st.columns(2)
                tech_cols = [c for c in ['ncc_abatement_kt', 'hp_abatement_kt', 're_ppa_abatement_kt'] if c in df.columns]

                with col1:
                    yearly = df.groupby('year')[tech_cols].sum().reset_index()
                    melted = yearly.melt(id_vars='year', var_name='Tech', value_name='kt')
                    melted['Tech'] = melted['Tech'].replace({'ncc_abatement_kt': 'NCC', 'hp_abatement_kt': 'Heat Pump', 're_ppa_abatement_kt': 'RE-PPA'})
                    fig = px.area(melted, x='year', y='kt', color='Tech', title='Technology Over Time (kt CO2)')
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    df_2050 = df[df['year'] == 2050]
                    reg = df_2050.groupby('region')[tech_cols].sum().reset_index()
                    reg_melt = reg.melt(id_vars='region', var_name='Tech', value_name='kt')
                    reg_melt['Tech'] = reg_melt['Tech'].replace({'ncc_abatement_kt': 'NCC', 'hp_abatement_kt': 'Heat Pump', 're_ppa_abatement_kt': 'RE-PPA'})
                    fig = px.bar(reg_melt, x='region', y='kt', color='Tech', title='Regional Mix 2050', barmode='stack')
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Emission Pathways
            st.header("2. Emission Pathways")
            for sid in selected:
                df = scenarios[sid]
                st.subheader(f"📊 {SCENARIOS[sid]}")

                col1, col2 = st.columns(2)

                with col1:
                    reg_yr = df.groupby(['year', 'region'])['actual_emissions_kt'].sum().reset_index()
                    fig = px.area(reg_yr, x='year', y='actual_emissions_kt', color='region', title='Emissions by Region (kt)')
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    total = df.groupby('year').agg({'bau_emissions_kt': 'sum', 'actual_emissions_kt': 'sum'}).reset_index()
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=total['year'], y=total['bau_emissions_kt']/1000, name='BAU', line=dict(color='red', dash='dash')))
                    fig.add_trace(go.Scatter(x=total['year'], y=total['actual_emissions_kt']/1000, name='Net Zero', fill='tozeroy', line=dict(color='green')))
                    fig.update_layout(title='BAU vs Net Zero (Mt CO2)', xaxis_title='Year', yaxis_title='Mt CO2')
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Summary Table
            st.header("3. Regional Summary (2050)")
            for sid in selected:
                df = scenarios[sid]
                df_2050 = df[df['year'] == 2050]

                summary = df_2050.groupby('region').agg({
                    'n_facilities': 'first',
                    'capacity_kt': 'first',
                    'bau_emissions_kt': 'sum',
                    'actual_emissions_kt': 'sum',
                    'elec_demand_mwh': 'sum'
                }).reset_index()
                summary['Reduction %'] = ((1 - summary['actual_emissions_kt'] / summary['bau_emissions_kt']) * 100).round(1)
                summary['Elec TWh'] = (summary['elec_demand_mwh'] / 1e6).round(2)

                st.subheader(f"📊 {SCENARIOS[sid]}")
                st.dataframe(summary[['region', 'n_facilities', 'capacity_kt', 'bau_emissions_kt', 'actual_emissions_kt', 'Reduction %', 'Elec TWh']], hide_index=True)

# ===================== ENERGY DEMAND =====================
elif page == "⚡ Energy Demand":
    st.title("⚡ Energy Demand")

    if not scenarios:
        st.error("No scenario data.")
    else:
        selected = st.multiselect("Select Scenarios", list(scenarios.keys()), default=list(scenarios.keys())[:2], format_func=lambda x: SCENARIOS[x])

        if selected:
            st.markdown("---")

            for sid in selected:
                df = scenarios[sid]
                st.subheader(f"⚡ {SCENARIOS[sid]}")

                col1, col2 = st.columns(2)

                with col1:
                    yearly = df.groupby('year')['elec_demand_mwh'].sum().reset_index()
                    yearly['TWh'] = yearly['elec_demand_mwh'] / 1e6
                    fig = px.area(yearly, x='year', y='TWh', title='Total Electricity (TWh)')
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    reg = df.groupby(['year', 'region'])['elec_demand_mwh'].sum().reset_index()
                    reg['TWh'] = reg['elec_demand_mwh'] / 1e6
                    fig = px.line(reg, x='year', y='TWh', color='region', title='By Region (TWh)')
                    st.plotly_chart(fig, use_container_width=True)

                # 2050 metrics
                df_2050 = df[df['year'] == 2050]
                total = df_2050['elec_demand_mwh'].sum() / 1e6
                cols = st.columns(5)
                cols[0].metric("Total 2050", f"{total:.1f} TWh")
                for i, (r, v) in enumerate(df_2050.groupby('region')['elec_demand_mwh'].sum().items()):
                    if i < 4:
                        cols[i+1].metric(r, f"{v/1e6:.2f} TWh")

                st.markdown("---")

# Footer
st.markdown("---")
st.caption("Korea Petrochemical Net Zero | 2024 | NO CCS/CCUS")
