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
import os

# Page config
st.set_page_config(
    page_title="Korea Petrochemical Regional Analysis",
    page_icon="🗺️",
    layout="wide"
)

# Get absolute path
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = SCRIPT_DIR / "data"
OUTPUTS_DIR = SCRIPT_DIR / "outputs"

# ============================================================================
# Load Data Directly (no caching issues)
# ============================================================================
def load_all_data():
    """Load all data directly"""
    data = {
        'assumptions': {},
        'scenarios': {},
        'summary': None
    }

    # Load assumptions
    try:
        data['assumptions']['tech_params'] = pd.read_csv(DATA_DIR / "technology_parameters.csv")
        data['assumptions']['h2_prices'] = pd.read_csv(DATA_DIR / "h2_price_trajectory.csv")
        data['assumptions']['re_prices'] = pd.read_csv(DATA_DIR / "re_price_trajectory.csv")
        data['assumptions']['grid_ef'] = pd.read_csv(DATA_DIR / "grid_emission_trajectory.csv")
        data['assumptions']['facilities'] = pd.read_csv(DATA_DIR / "facility_database_with_regions.csv")
    except Exception as e:
        st.sidebar.error(f"Error loading assumptions: {e}")

    # Load scenario summary
    summary_file = OUTPUTS_DIR / "scenario_summary_final.csv"
    if summary_file.exists():
        data['summary'] = pd.read_csv(summary_file)

    # Load each scenario's regional data
    scenario_dirs = [
        ('shaheen_ncc_h2', 'Shaheen + NCC-H2'),
        ('shaheen_ncc_electricity', 'Shaheen + NCC-Elec'),
        ('restructure_25pct_ncc_h2', 'Restructure 25% + NCC-H2'),
        ('restructure_25pct_ncc_electricity', 'Restructure 25% + NCC-Elec'),
        ('restructure_40pct_ncc_h2', 'Restructure 40% + NCC-H2'),
        ('restructure_40pct_ncc_electricity', 'Restructure 40% + NCC-Elec'),
    ]

    for scenario_id, scenario_name in scenario_dirs:
        annual_file = OUTPUTS_DIR / f"scenario_{scenario_id}" / "annual_regional_trajectory.csv"
        if annual_file.exists():
            df = pd.read_csv(annual_file)
            df['scenario_id'] = scenario_id
            df['scenario_name'] = scenario_name
            data['scenarios'][scenario_id] = df

    return data

# Load data
data = load_all_data()

# Scenario names mapping
SCENARIO_NAMES = {
    'shaheen_ncc_h2': 'Shaheen + NCC-H2',
    'shaheen_ncc_electricity': 'Shaheen + NCC-Elec',
    'restructure_25pct_ncc_h2': 'Restructure 25% + NCC-H2',
    'restructure_25pct_ncc_electricity': 'Restructure 25% + NCC-Elec',
    'restructure_40pct_ncc_h2': 'Restructure 40% + NCC-H2',
    'restructure_40pct_ncc_electricity': 'Restructure 40% + NCC-Elec',
}

# ============================================================================
# Sidebar
# ============================================================================
st.sidebar.title("🗺️ Regional Analysis")
st.sidebar.markdown(f"**Loaded Scenarios:** {len(data['scenarios'])}")

page = st.sidebar.radio(
    "Select Page",
    ["📋 Assumptions", "🗺️ Regional Transitions", "⚡ Energy & Cost"]
)

st.sidebar.markdown("---")
st.sidebar.info("**Period:** 2025-2050\n\n**NO CCS/CCUS**")

# ============================================================================
# Page: Assumptions
# ============================================================================
if page == "📋 Assumptions":
    st.title("📋 Key Assumptions")

    assumptions = data['assumptions']

    if assumptions:
        # Technology Parameters
        st.header("1. Technology Parameters & CAPEX Learning")

        if 'tech_params' in assumptions:
            tech_df = assumptions['tech_params']

            col1, col2 = st.columns(2)

            with col1:
                # CAPEX learning curve
                capex_data = []
                for _, row in tech_df.iterrows():
                    tech = row['technology']
                    if tech != 'RE_PPA':
                        for year in [2025, 2030, 2040, 2050]:
                            capex_data.append({
                                'Technology': tech.replace('_', ' '),
                                'Year': year,
                                'CAPEX (M$/MtCO2)': row[f'capex_{year}_musd_per_mtco2']
                            })

                capex_df = pd.DataFrame(capex_data)
                fig = px.line(capex_df, x='Year', y='CAPEX (M$/MtCO2)', color='Technology',
                             markers=True, title='CAPEX Learning Curve (50% decline by 2050)')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Technology Specifications")
                st.dataframe(tech_df[['technology', 'applies_to', 'trl', 'available_year',
                                     'capex_2025_musd_per_mtco2', 'capex_2050_musd_per_mtco2']],
                            hide_index=True, use_container_width=True)

        st.markdown("---")

        # Price Trajectories
        st.header("2. Price Trajectories")

        col1, col2, col3 = st.columns(3)

        with col1:
            if 'h2_prices' in assumptions:
                h2_df = assumptions['h2_prices']
                fig = px.line(h2_df, x='year', y='h2_price_usd_per_kg',
                             title='Green H2 Price ($/kg)')
                fig.add_hline(y=2.0, line_dash="dash", line_color="green",
                             annotation_text="$2/kg target")
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
                st.metric("2025 → 2050",
                         f"${h2_df.iloc[0]['h2_price_usd_per_kg']:.2f} → ${h2_df.iloc[-1]['h2_price_usd_per_kg']:.2f}")

        with col2:
            if 're_prices' in assumptions:
                re_df = assumptions['re_prices']
                fig = px.line(re_df, x='year', y='re_price_usd_per_mwh',
                             title='RE Electricity Price ($/MWh)')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
                st.metric("2025 → 2050",
                         f"${re_df.iloc[0]['re_price_usd_per_mwh']:.0f} → ${re_df.iloc[-1]['re_price_usd_per_mwh']:.0f}")

        with col3:
            if 'grid_ef' in assumptions:
                grid_df = assumptions['grid_ef']
                fig = px.area(grid_df, x='year', y='grid_ef_tco2_per_mwh',
                             title='Grid Emission Factor (tCO2/MWh)')
                fig.update_traces(fillcolor='rgba(231, 76, 60, 0.3)')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
                st.metric("2025 → 2050",
                         f"{grid_df.iloc[0]['grid_ef_tco2_per_mwh']:.3f} → {grid_df.iloc[-1]['grid_ef_tco2_per_mwh']:.3f}")

        st.markdown("---")

        # Facility Coverage
        st.header("3. Facility Coverage")

        if 'facilities' in assumptions:
            fac_df = assumptions['facilities']

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Facilities", len(fac_df))
            col2.metric("Total Capacity", f"{fac_df['capacity_kt'].sum():,.0f} kt")
            col3.metric("Regions", fac_df['location'].nunique())

            col1, col2 = st.columns(2)

            with col1:
                region_cap = fac_df.groupby('location')['capacity_kt'].sum().reset_index()
                fig = px.pie(region_cap, values='capacity_kt', names='location',
                            title='Capacity by Region')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                product_cap = fac_df.groupby('product')['capacity_kt'].sum().reset_index()
                fig = px.bar(product_cap, x='product', y='capacity_kt',
                            title='Capacity by Product', color='product')
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Page: Regional Transitions
# ============================================================================
elif page == "🗺️ Regional Transitions":
    st.title("🗺️ Regional Transitions")

    scenarios = data['scenarios']

    if not scenarios:
        st.error("No scenario data found!")
        st.write(f"Looking in: {OUTPUTS_DIR}")
        st.write("Available directories:")
        if OUTPUTS_DIR.exists():
            for d in OUTPUTS_DIR.iterdir():
                if d.is_dir() and 'scenario' in d.name:
                    st.write(f"  - {d.name}")
    else:
        # Scenario selector
        available_scenarios = list(scenarios.keys())
        selected = st.multiselect(
            "Select Scenarios",
            available_scenarios,
            default=available_scenarios[:2],
            format_func=lambda x: SCENARIO_NAMES.get(x, x)
        )

        if selected:
            st.markdown("---")

            # 1. Technology Deployment
            st.header("1. Technology Deployment by Region")

            for scenario_id in selected:
                df = scenarios[scenario_id]

                st.subheader(f"📊 {SCENARIO_NAMES[scenario_id]}")

                col1, col2 = st.columns(2)

                with col1:
                    # Total abatement by technology over time
                    tech_cols = ['ncc_abatement_kt', 'hp_abatement_kt', 're_ppa_abatement_kt']
                    if 'rdh_abatement_kt' in df.columns:
                        tech_cols.insert(1, 'rdh_abatement_kt')

                    yearly = df.groupby('year')[tech_cols].sum().reset_index()
                    yearly_melt = yearly.melt(id_vars='year', var_name='Tech', value_name='Abatement (kt)')
                    yearly_melt['Tech'] = yearly_melt['Tech'].str.replace('_abatement_kt', '').str.upper()
                    yearly_melt['Tech'] = yearly_melt['Tech'].replace({
                        'NCC': 'NCC', 'RDH': 'RDH', 'HP': 'Heat Pump', 'RE_PPA': 'RE-PPA'
                    })

                    fig = px.area(yearly_melt, x='year', y='Abatement (kt)', color='Tech',
                                 title='Technology Deployment Over Time (kt CO2 abated)')
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Regional breakdown in 2050
                    df_2050 = df[df['year'] == 2050]
                    regional = df_2050.groupby('region')[tech_cols].sum().reset_index()
                    regional_melt = regional.melt(id_vars='region', var_name='Tech', value_name='Abatement (kt)')
                    regional_melt['Tech'] = regional_melt['Tech'].str.replace('_abatement_kt', '').str.upper()
                    regional_melt['Tech'] = regional_melt['Tech'].replace({
                        'NCC': 'NCC', 'RDH': 'RDH', 'HP': 'Heat Pump', 'RE_PPA': 'RE-PPA'
                    })

                    fig = px.bar(regional_melt, x='region', y='Abatement (kt)', color='Tech',
                                title='Regional Technology Mix (2050)', barmode='stack')
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # 2. Emission Pathways
            st.header("2. Regional Emission Pathways")

            for scenario_id in selected:
                df = scenarios[scenario_id]

                st.subheader(f"📊 {SCENARIO_NAMES[scenario_id]}")

                col1, col2 = st.columns(2)

                with col1:
                    # Emissions by region over time
                    regional_yearly = df.groupby(['year', 'region'])['actual_emissions_kt'].sum().reset_index()

                    fig = px.area(regional_yearly, x='year', y='actual_emissions_kt', color='region',
                                 title='Net Emissions by Region (kt CO2)')
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # BAU vs Actual total
                    total = df.groupby('year').agg({
                        'bau_emissions_kt': 'sum',
                        'actual_emissions_kt': 'sum'
                    }).reset_index()

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=total['year'], y=total['bau_emissions_kt']/1000,
                                            name='BAU', line=dict(color='red', dash='dash')))
                    fig.add_trace(go.Scatter(x=total['year'], y=total['actual_emissions_kt']/1000,
                                            name='With Technology', line=dict(color='green'), fill='tozeroy'))
                    fig.update_layout(title='Total Emissions: BAU vs Net Zero (Mt CO2)',
                                     xaxis_title='Year', yaxis_title='Mt CO2', height=350)
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # 3. Regional Summary Table for 2050
            st.header("3. Regional Summary (2050)")

            for scenario_id in selected:
                df = scenarios[scenario_id]
                df_2050 = df[df['year'] == 2050]

                summary = df_2050.groupby('region').agg({
                    'n_facilities': 'first',
                    'capacity_kt': 'first',
                    'bau_emissions_kt': 'sum',
                    'actual_emissions_kt': 'sum',
                    'total_abatement_kt': 'sum',
                    'elec_demand_mwh': 'sum'
                }).reset_index()

                summary['elec_twh'] = summary['elec_demand_mwh'] / 1e6
                summary['reduction_pct'] = (1 - summary['actual_emissions_kt'] / summary['bau_emissions_kt']) * 100

                st.subheader(f"📊 {SCENARIO_NAMES[scenario_id]}")

                display_df = summary[['region', 'n_facilities', 'capacity_kt', 'bau_emissions_kt',
                                     'actual_emissions_kt', 'reduction_pct', 'elec_twh']].copy()
                display_df.columns = ['Region', 'Facilities', 'Capacity (kt)', 'BAU (kt)',
                                     'Net (kt)', 'Reduction %', 'Elec (TWh)']
                display_df['Reduction %'] = display_df['Reduction %'].round(1)
                display_df['Elec (TWh)'] = display_df['Elec (TWh)'].round(2)

                st.dataframe(display_df, hide_index=True, use_container_width=True)

# ============================================================================
# Page: Energy & Cost
# ============================================================================
elif page == "⚡ Energy & Cost":
    st.title("⚡ Energy Demand Analysis")

    scenarios = data['scenarios']

    if not scenarios:
        st.error("No scenario data found!")
    else:
        available_scenarios = list(scenarios.keys())
        selected = st.multiselect(
            "Select Scenarios",
            available_scenarios,
            default=available_scenarios[:2],
            format_func=lambda x: SCENARIO_NAMES.get(x, x)
        )

        if selected:
            st.markdown("---")

            # 1. Electricity Demand
            st.header("1. Electricity Demand by Region")

            for scenario_id in selected:
                df = scenarios[scenario_id]

                st.subheader(f"⚡ {SCENARIO_NAMES[scenario_id]}")

                col1, col2 = st.columns(2)

                with col1:
                    # Total electricity over time
                    yearly_elec = df.groupby('year')['elec_demand_mwh'].sum().reset_index()
                    yearly_elec['TWh'] = yearly_elec['elec_demand_mwh'] / 1e6

                    fig = px.area(yearly_elec, x='year', y='TWh',
                                 title='Total Electricity Demand (TWh)')
                    fig.update_traces(fillcolor='rgba(52, 152, 219, 0.5)')
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # By region
                    regional_elec = df.groupby(['year', 'region'])['elec_demand_mwh'].sum().reset_index()
                    regional_elec['TWh'] = regional_elec['elec_demand_mwh'] / 1e6

                    fig = px.line(regional_elec, x='year', y='TWh', color='region',
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

            # 2. Scenario Comparison
            st.header("2. Cross-Scenario Comparison (2050)")

            comparison = []
            for scenario_id in selected:
                df = scenarios[scenario_id]
                df_2050 = df[df['year'] == 2050]

                for region in df_2050['region'].unique():
                    r_data = df_2050[df_2050['region'] == region]
                    comparison.append({
                        'Scenario': SCENARIO_NAMES[scenario_id],
                        'Region': region,
                        'Electricity (TWh)': r_data['elec_demand_mwh'].sum() / 1e6,
                        'Emissions (kt)': r_data['actual_emissions_kt'].sum(),
                        'Abatement (kt)': r_data['total_abatement_kt'].sum()
                    })

            comp_df = pd.DataFrame(comparison)

            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(comp_df, x='Region', y='Electricity (TWh)', color='Scenario',
                            barmode='group', title='Regional Electricity Comparison')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.bar(comp_df, x='Region', y='Abatement (kt)', color='Scenario',
                            barmode='group', title='Regional Abatement Comparison')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.caption("Korea Petrochemical Net Zero Analysis | December 2024 | NO CCS/CCUS")
