"""
Korea Petrochemical Net Zero - Regional Analysis Dashboard
==========================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Korea Petrochemical Regional Analysis",
    page_icon="🗺️",
    layout="wide"
)

# Get path relative to script
SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR / "data"
SCENARIOS_DIR = DATA_DIR / "scenarios"

# Scenario definitions
SCENARIO_INFO = {
    'shaheen_ncc_h2': {'name': 'Shaheen + NCC-H2', 'production': 'Shaheen (Growth)', 'tech': 'NCC-H2'},
    'shaheen_ncc_electricity': {'name': 'Shaheen + NCC-Elec', 'production': 'Shaheen (Growth)', 'tech': 'NCC-Electricity'},
    'restructure_25pct_ncc_h2': {'name': 'Restructure 25% + NCC-H2', 'production': 'Restructure 25%', 'tech': 'NCC-H2'},
    'restructure_25pct_ncc_electricity': {'name': 'Restructure 25% + NCC-Elec', 'production': 'Restructure 25%', 'tech': 'NCC-Electricity'},
    'restructure_40pct_ncc_h2': {'name': 'Restructure 40% + NCC-H2', 'production': 'Restructure 40%', 'tech': 'NCC-H2'},
    'restructure_40pct_ncc_electricity': {'name': 'Restructure 40% + NCC-Elec', 'production': 'Restructure 40%', 'tech': 'NCC-Electricity'},
}

# ============================================================================
# Data Loading
# ============================================================================
@st.cache_data
def load_assumptions():
    """Load assumption data files"""
    data = {}
    try:
        data['tech_params'] = pd.read_csv(DATA_DIR / "technology_parameters.csv")
        data['h2_prices'] = pd.read_csv(DATA_DIR / "h2_price_trajectory.csv")
        data['re_prices'] = pd.read_csv(DATA_DIR / "re_price_trajectory.csv")
        data['grid_ef'] = pd.read_csv(DATA_DIR / "grid_emission_trajectory.csv")
        data['facilities'] = pd.read_csv(DATA_DIR / "facility_database_with_regions.csv")
    except Exception as e:
        st.error(f"Error loading assumptions: {e}")
    return data

@st.cache_data
def load_scenarios():
    """Load scenario data from data/scenarios folder"""
    scenarios = {}

    for scenario_id, info in SCENARIO_INFO.items():
        file_path = SCENARIOS_DIR / f"{scenario_id}.csv"
        if file_path.exists():
            df = pd.read_csv(file_path)
            df['scenario_id'] = scenario_id
            df['scenario_name'] = info['name']
            scenarios[scenario_id] = df

    return scenarios

@st.cache_data
def load_summary():
    """Load scenario summary"""
    summary_path = DATA_DIR / "scenario_summary.csv"
    if summary_path.exists():
        return pd.read_csv(summary_path)
    return None

# Load all data
assumptions = load_assumptions()
scenarios = load_scenarios()
summary = load_summary()

# ============================================================================
# Sidebar
# ============================================================================
st.sidebar.title("🗺️ Regional Analysis")
st.sidebar.markdown(f"**Scenarios loaded:** {len(scenarios)}")

page = st.sidebar.radio(
    "Navigation",
    ["📋 Assumptions", "🗺️ Regional Transitions", "⚡ Energy Demand"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Period:** 2025-2050\n\n"
    "**Technologies:**\n"
    "- NCC-H2/Elec\n"
    "- Heat Pump\n"
    "- RE-PPA\n\n"
    "**NO CCS/CCUS**"
)

# ============================================================================
# Page: Assumptions
# ============================================================================
if page == "📋 Assumptions":
    st.title("📋 Key Assumptions")

    # 1. Technology Parameters
    st.header("1. Technology CAPEX Learning Curve")

    if 'tech_params' in assumptions:
        tech_df = assumptions['tech_params']

        col1, col2 = st.columns(2)

        with col1:
            capex_data = []
            for _, row in tech_df.iterrows():
                tech = row['technology']
                if tech != 'RE_PPA':
                    for year in [2025, 2030, 2040, 2050]:
                        capex_data.append({
                            'Technology': tech.replace('_', ' '),
                            'Year': year,
                            'CAPEX': row[f'capex_{year}_musd_per_mtco2']
                        })

            capex_df = pd.DataFrame(capex_data)
            fig = px.line(capex_df, x='Year', y='CAPEX', color='Technology',
                         markers=True, title='CAPEX Trajectory (M$/MtCO2)')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Technology Specifications")
            display_df = tech_df[['technology', 'applies_to', 'trl', 'available_year',
                                 'capex_2025_musd_per_mtco2', 'capex_2050_musd_per_mtco2']].copy()
            display_df.columns = ['Technology', 'Application', 'TRL', 'Available', 'CAPEX 2025', 'CAPEX 2050']
            st.dataframe(display_df, hide_index=True, use_container_width=True)

            st.markdown("""
            **Key Points:**
            - **50% CAPEX decline** by 2050 (learning curve)
            - Heat Pump available now (TRL 9)
            - NCC technologies from 2030 (TRL 7-8)
            """)

    st.markdown("---")

    # 2. Price Trajectories
    st.header("2. Energy Price Trajectories")

    col1, col2, col3 = st.columns(3)

    with col1:
        if 'h2_prices' in assumptions:
            h2_df = assumptions['h2_prices']
            fig = px.line(h2_df, x='year', y='h2_price_usd_per_kg', title='Green H2 ($/kg)')
            fig.add_hline(y=2.0, line_dash="dash", line_color="green", annotation_text="$2/kg target")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.metric("2025 → 2050", f"${h2_df.iloc[0]['h2_price_usd_per_kg']:.2f} → ${h2_df.iloc[-1]['h2_price_usd_per_kg']:.2f}")

    with col2:
        if 're_prices' in assumptions:
            re_df = assumptions['re_prices']
            fig = px.line(re_df, x='year', y='re_price_usd_per_mwh', title='RE Electricity ($/MWh)')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.metric("2025 → 2050", f"${re_df.iloc[0]['re_price_usd_per_mwh']:.0f} → ${re_df.iloc[-1]['re_price_usd_per_mwh']:.0f}")

    with col3:
        if 'grid_ef' in assumptions:
            grid_df = assumptions['grid_ef']
            fig = px.area(grid_df, x='year', y='grid_ef_tco2_per_mwh', title='Grid EF (tCO2/MWh)')
            fig.update_traces(fillcolor='rgba(231, 76, 60, 0.3)')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.metric("2025 → 2050", f"{grid_df.iloc[0]['grid_ef_tco2_per_mwh']:.3f} → 0.000")

    st.markdown("---")

    # 3. Facility Coverage
    st.header("3. Facility Coverage by Region")

    if 'facilities' in assumptions:
        fac_df = assumptions['facilities']

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Facilities", len(fac_df))
        col2.metric("Total Capacity", f"{fac_df['capacity_kt'].sum():,.0f} kt")
        col3.metric("Regions", fac_df['location'].nunique())

        col1, col2 = st.columns(2)

        with col1:
            region_cap = fac_df.groupby('location')['capacity_kt'].sum().reset_index()
            fig = px.pie(region_cap, values='capacity_kt', names='location', title='Capacity by Region')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            product_cap = fac_df.groupby('product')['capacity_kt'].sum().reset_index()
            fig = px.bar(product_cap, x='product', y='capacity_kt', title='Capacity by Product', color='product')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Page: Regional Transitions
# ============================================================================
elif page == "🗺️ Regional Transitions":
    st.title("🗺️ Regional Transitions")

    if not scenarios:
        st.error("No scenario data found!")
        st.info(f"Looking for CSV files in: `{SCENARIOS_DIR}`")
    else:
        # Scenario selector
        selected = st.multiselect(
            "Select Scenarios to Compare",
            list(scenarios.keys()),
            default=list(scenarios.keys())[:2],
            format_func=lambda x: SCENARIO_INFO[x]['name']
        )

        if selected:
            st.markdown("---")

            # 1. Technology Deployment
            st.header("1. Technology Deployment")

            for scenario_id in selected:
                df = scenarios[scenario_id]
                st.subheader(f"📊 {SCENARIO_INFO[scenario_id]['name']}")

                col1, col2 = st.columns(2)

                # Get available tech columns
                tech_cols = [c for c in ['ncc_abatement_kt', 'rdh_abatement_kt', 'hp_abatement_kt', 're_ppa_abatement_kt']
                            if c in df.columns]

                with col1:
                    # Technology over time
                    yearly = df.groupby('year')[tech_cols].sum().reset_index()
                    yearly_melt = yearly.melt(id_vars='year', var_name='Tech', value_name='Abatement (kt)')
                    yearly_melt['Tech'] = yearly_melt['Tech'].replace({
                        'ncc_abatement_kt': 'NCC',
                        'rdh_abatement_kt': 'RDH',
                        'hp_abatement_kt': 'Heat Pump',
                        're_ppa_abatement_kt': 'RE-PPA'
                    })

                    fig = px.area(yearly_melt, x='year', y='Abatement (kt)', color='Tech',
                                 title='Technology Deployment Over Time')
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Regional mix in 2050
                    df_2050 = df[df['year'] == 2050]
                    regional = df_2050.groupby('region')[tech_cols].sum().reset_index()
                    regional_melt = regional.melt(id_vars='region', var_name='Tech', value_name='Abatement (kt)')
                    regional_melt['Tech'] = regional_melt['Tech'].replace({
                        'ncc_abatement_kt': 'NCC',
                        'rdh_abatement_kt': 'RDH',
                        'hp_abatement_kt': 'Heat Pump',
                        're_ppa_abatement_kt': 'RE-PPA'
                    })

                    fig = px.bar(regional_melt, x='region', y='Abatement (kt)', color='Tech',
                                title='Regional Technology Mix (2050)', barmode='stack')
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # 2. Emission Pathways
            st.header("2. Emission Pathways by Region")

            for scenario_id in selected:
                df = scenarios[scenario_id]
                st.subheader(f"📊 {SCENARIO_INFO[scenario_id]['name']}")

                col1, col2 = st.columns(2)

                with col1:
                    # Regional emissions over time
                    regional_yearly = df.groupby(['year', 'region'])['actual_emissions_kt'].sum().reset_index()
                    fig = px.area(regional_yearly, x='year', y='actual_emissions_kt', color='region',
                                 title='Net Emissions by Region (kt CO2)')
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # BAU vs Actual
                    total = df.groupby('year').agg({
                        'bau_emissions_kt': 'sum',
                        'actual_emissions_kt': 'sum'
                    }).reset_index()

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=total['year'], y=total['bau_emissions_kt']/1000,
                                            name='BAU', line=dict(color='red', dash='dash')))
                    fig.add_trace(go.Scatter(x=total['year'], y=total['actual_emissions_kt']/1000,
                                            name='Net Zero', line=dict(color='green'), fill='tozeroy'))
                    fig.update_layout(title='BAU vs Net Zero (Mt CO2)', height=350,
                                     xaxis_title='Year', yaxis_title='Mt CO2')
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # 3. Summary Table
            st.header("3. Regional Summary (2050)")

            for scenario_id in selected:
                df = scenarios[scenario_id]
                df_2050 = df[df['year'] == 2050]

                summary_table = df_2050.groupby('region').agg({
                    'n_facilities': 'first',
                    'capacity_kt': 'first',
                    'bau_emissions_kt': 'sum',
                    'actual_emissions_kt': 'sum',
                    'elec_demand_mwh': 'sum'
                }).reset_index()

                summary_table['Reduction %'] = ((1 - summary_table['actual_emissions_kt'] / summary_table['bau_emissions_kt']) * 100).round(1)
                summary_table['Elec (TWh)'] = (summary_table['elec_demand_mwh'] / 1e6).round(2)

                display = summary_table[['region', 'n_facilities', 'capacity_kt', 'bau_emissions_kt',
                                        'actual_emissions_kt', 'Reduction %', 'Elec (TWh)']].copy()
                display.columns = ['Region', 'Facilities', 'Capacity (kt)', 'BAU (kt)', 'Net (kt)', 'Reduction %', 'Elec (TWh)']

                st.subheader(f"📊 {SCENARIO_INFO[scenario_id]['name']}")
                st.dataframe(display, hide_index=True, use_container_width=True)

# ============================================================================
# Page: Energy Demand
# ============================================================================
elif page == "⚡ Energy Demand":
    st.title("⚡ Energy Demand by Region")

    if not scenarios:
        st.error("No scenario data found!")
    else:
        selected = st.multiselect(
            "Select Scenarios",
            list(scenarios.keys()),
            default=list(scenarios.keys())[:2],
            format_func=lambda x: SCENARIO_INFO[x]['name']
        )

        if selected:
            st.markdown("---")

            for scenario_id in selected:
                df = scenarios[scenario_id]
                st.subheader(f"⚡ {SCENARIO_INFO[scenario_id]['name']}")

                col1, col2 = st.columns(2)

                with col1:
                    # Total electricity
                    yearly = df.groupby('year')['elec_demand_mwh'].sum().reset_index()
                    yearly['TWh'] = yearly['elec_demand_mwh'] / 1e6

                    fig = px.area(yearly, x='year', y='TWh', title='Total Electricity Demand (TWh)')
                    fig.update_traces(fillcolor='rgba(52, 152, 219, 0.5)')
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # By region
                    regional = df.groupby(['year', 'region'])['elec_demand_mwh'].sum().reset_index()
                    regional['TWh'] = regional['elec_demand_mwh'] / 1e6

                    fig = px.line(regional, x='year', y='TWh', color='region',
                                 title='Electricity by Region (TWh)')
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)

                # 2050 metrics
                df_2050 = df[df['year'] == 2050]
                total_twh = df_2050['elec_demand_mwh'].sum() / 1e6

                cols = st.columns(5)
                cols[0].metric("Total 2050", f"{total_twh:.1f} TWh")

                regional_2050 = df_2050.groupby('region')['elec_demand_mwh'].sum() / 1e6
                for i, (region, twh) in enumerate(regional_2050.items()):
                    if i < 4:
                        cols[i+1].metric(region, f"{twh:.2f} TWh")

                st.markdown("---")

            # Cross-scenario comparison
            st.header("Cross-Scenario Comparison (2050)")

            comparison = []
            for scenario_id in selected:
                df = scenarios[scenario_id]
                df_2050 = df[df['year'] == 2050]

                for region in df_2050['region'].unique():
                    r = df_2050[df_2050['region'] == region]
                    comparison.append({
                        'Scenario': SCENARIO_INFO[scenario_id]['name'],
                        'Region': region,
                        'Electricity (TWh)': r['elec_demand_mwh'].sum() / 1e6
                    })

            comp_df = pd.DataFrame(comparison)

            fig = px.bar(comp_df, x='Region', y='Electricity (TWh)', color='Scenario',
                        barmode='group', title='Regional Electricity Comparison')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Korea Petrochemical Net Zero | December 2024 | NO CCS/CCUS")
