"""
Korea Petrochemical Net Zero - Interactive Dashboard (SFOC Version)
====================================================================
Reads from outputs/scenario_results.csv (single long-format file)

Pages:
1. Scenario Comparison - Summary cards, bar charts, MACC curve
2. Technology Details - Parameters, MACC evolution
3. Regional Transition Outlook - Regional metrics, H2 demand, cost pathways
4. Facility-Level Results - Summaries and searchable table
5. Energy Infrastructure - Electricity and H2 demand by scenario
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Korea Petrochemical Net Zero", page_icon="🏭", layout="wide")

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

# Scenario display names
SCENARIO_NAMES = {
    'shaheen_ncc_h2': 'Shaheen + NCC-H2',
    'shaheen_ncc_elec': 'Shaheen + NCC-Elec',
    'restructure_25pct_ncc_h2': 'Restructure 25% + NCC-H2',
    'restructure_25pct_ncc_elec': 'Restructure 25% + NCC-Elec',
    'restructure_40pct_ncc_h2': 'Restructure 40% + NCC-H2',
    'restructure_40pct_ncc_elec': 'Restructure 40% + NCC-Elec',
}

# Technology colors
TECH_COLORS = {
    'Baseline': '#808080',
    'NCC-H2': '#2E86AB',
    'NCC-Electricity': '#A23B72',
    'RDH': '#F18F01',
    'Heat_Pump': '#C73E1D',
}

# Region colors
REGION_COLORS = {
    'Daesan': '#1f77b4',
    'Yeosu': '#ff7f0e',
    'Ulsan': '#2ca02c',
    'Other': '#d62728',
}


@st.cache_data(ttl=60)  # Cache expires after 60 seconds
def load_results():
    """Load scenario results from single CSV file - v2 (cache invalidated)"""
    results_file = OUTPUT_DIR / "scenario_results.csv"
    if results_file.exists():
        df = pd.read_csv(results_file)
        # Convert units for easier display
        df['bau_emissions_mt'] = df['bau_emissions_tco2'] / 1e6
        df['emissions_mt'] = df['emissions_tco2'] / 1e6
        df['abatement_mt'] = df['abatement_tco2'] / 1e6
        df['elec_twh'] = df['elec_demand_mwh'] / 1e6
        df['h2_mt'] = df['h2_demand_t'] / 1e6
        df['capex_b'] = df['capex_usd'] / 1e9
        df['total_cost_b'] = df['total_cost_usd'] / 1e9
        return df
    return None


@st.cache_data(ttl=60)
def load_assumptions():
    """Load input assumptions - v2"""
    data = {}
    try:
        data['tech'] = pd.read_csv(DATA_DIR / "technology_parameters.csv")
        data['h2'] = pd.read_csv(DATA_DIR / "h2_price_trajectory.csv")
        data['re'] = pd.read_csv(DATA_DIR / "re_price_trajectory.csv")
        data['grid'] = pd.read_csv(DATA_DIR / "grid_emission_trajectory.csv")
        data['fac'] = pd.read_csv(DATA_DIR / "facility_database_with_regions.csv")
    except Exception as e:
        st.error(f"Error loading assumptions: {e}")
    return data


@st.cache_data(ttl=60)
def load_regional_summaries():
    """Load pre-computed regional summary files (annual 2025-2050) - v2"""
    summaries = {}
    try:
        # Regional MAC summary
        mac_file = OUTPUT_DIR / "regional_mac_summary.csv"
        if mac_file.exists():
            summaries['mac'] = pd.read_csv(mac_file)

        # Regional abatement summary
        abatement_file = OUTPUT_DIR / "regional_abatement_summary.csv"
        if abatement_file.exists():
            summaries['abatement'] = pd.read_csv(abatement_file)
    except Exception as e:
        st.error(f"Error loading regional summaries: {e}")
    return summaries


def create_macc_figure(df_macc, scenario_name):
    """Create MACC curve figure"""
    fig = go.Figure()

    # Create step chart data
    x_vals = [0]
    y_vals = [df_macc['mac_usd_per_tco2'].iloc[0] if len(df_macc) > 0 else 0]

    for i, row in df_macc.iterrows():
        x_vals.append(row['cumulative_abatement_mtco2'])
        y_vals.append(row['mac_usd_per_tco2'])

    # Color by technology
    for tech in df_macc['technology'].unique():
        df_tech = df_macc[df_macc['technology'] == tech]
        fig.add_trace(go.Bar(
            x=df_tech['abatement_tco2'] / 1e6,
            y=df_tech['mac_usd_per_tco2'],
            name=tech,
            marker_color=TECH_COLORS.get(tech, '#808080'),
            customdata=df_tech[['facility_id', 'company', 'product', 'region']].values,
            hovertemplate='<b>%{customdata[1]}</b><br>' +
                          'Product: %{customdata[2]}<br>' +
                          'Region: %{customdata[3]}<br>' +
                          'Abatement: %{x:.3f} MtCO2<br>' +
                          'MAC: $%{y:.0f}/tCO2<extra></extra>'
        ))

    fig.update_layout(
        title=f'Marginal Abatement Cost Curve - {scenario_name} (2050)',
        xaxis_title='Abatement (MtCO2)',
        yaxis_title='Marginal Abatement Cost ($/tCO2)',
        barmode='stack',
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        height=500
    )

    return fig


def format_number(val, unit=''):
    """Format numbers for display"""
    if abs(val) >= 1e9:
        return f"${val/1e9:.1f}B{unit}"
    elif abs(val) >= 1e6:
        return f"{val/1e6:.2f}M{unit}"
    elif abs(val) >= 1e3:
        return f"{val/1e3:.1f}k{unit}"
    else:
        return f"{val:.2f}{unit}"


# Load data
df = load_results()
assumptions = load_assumptions()
regional_summaries = load_regional_summaries()

# ===================== SIDEBAR =====================
st.sidebar.title("🏭 Net Zero Dashboard")
st.sidebar.markdown("**Korea Petrochemical**")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "📑 Navigation",
    ["📊 Scenario Comparison", "🔧 Technology Details", "🗺️ Regional Outlook",
     "🏢 Facility Results", "⚡ Energy Infrastructure"]
)

st.sidebar.markdown("---")

# Global Filters
st.sidebar.markdown("### 🎛️ Filters")

# Clear cache button
if st.sidebar.button("🔄 Reload Data"):
    st.cache_data.clear()
    st.rerun()

if df is not None:
    # Year filter
    years = sorted(df['year'].unique())
    selected_year = st.sidebar.selectbox("Year", years, index=len(years)-1)

    # Scenario filter - DEFAULT TO ALL 6 SCENARIOS
    scenarios = df['scenario'].unique().tolist()
    selected_scenarios = st.sidebar.multiselect(
        "Scenarios",
        scenarios,
        default=scenarios,  # Show ALL scenarios by default
        format_func=lambda x: SCENARIO_NAMES.get(x, x)
    )

    # Region filter
    regions = ['All'] + sorted(df['region'].unique().tolist())
    selected_region = st.sidebar.selectbox("Region", regions)

    # Technology filter
    techs = ['All'] + sorted(df['technology'].unique().tolist())
    selected_tech = st.sidebar.selectbox("Technology", techs)

    st.sidebar.markdown("---")
    st.sidebar.info(f"**Data Summary**\n\n"
                   f"Scenarios: {len(scenarios)}\n\n"
                   f"Facilities: {df['facility_id'].nunique()}\n\n"
                   f"Period: 2025-2050 (Annual)\n\n"
                   f"**NO CCS/CCUS**")
else:
    st.sidebar.warning("No data loaded")
    selected_year = 2050
    selected_scenarios = []
    selected_region = 'All'
    selected_tech = 'All'

# Apply filters to create filtered dataframe
def filter_data(df, year=None, scenarios=None, region=None, tech=None):
    """Apply filters to dataframe"""
    filtered = df.copy()
    if year:
        filtered = filtered[filtered['year'] == year]
    if scenarios:
        filtered = filtered[filtered['scenario'].isin(scenarios)]
    if region and region != 'All':
        filtered = filtered[filtered['region'] == region]
    if tech and tech != 'All':
        filtered = filtered[filtered['technology'] == tech]
    return filtered


# ===================== PAGE 1: SCENARIO COMPARISON =====================
if page == "📊 Scenario Comparison":
    st.title("📊 Scenario Comparison")

    if df is None:
        st.error("No scenario data. Run `python run_scenarios.py` first.")
    elif not selected_scenarios:
        st.warning("Please select at least one scenario from the sidebar.")
    else:
        # Summary Cards
        st.header(f"Summary Metrics ({selected_year})")

        cols = st.columns(len(selected_scenarios))
        for i, scenario in enumerate(selected_scenarios):
            df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]
            df_base = df[(df['scenario'] == scenario) & (df['year'] == 2025)]

            with cols[i]:
                st.subheader(SCENARIO_NAMES.get(scenario, scenario))

                baseline = df_base['bau_emissions_tco2'].sum() / 1e6
                final = df_s['emissions_tco2'].sum() / 1e6
                abatement = df_s['abatement_tco2'].sum() / 1e6
                capex = df_s['capex_usd'].sum() / 1e9
                total_cost = df_s['total_cost_usd'].sum() / 1e9
                mac = df_s['total_cost_usd'].sum() / df_s['abatement_tco2'].sum() if df_s['abatement_tco2'].sum() > 0 else 0
                deployed = df_s[df_s['tech_deployed'] == 1]['facility_id'].nunique()

                st.metric("Baseline (2025)", f"{baseline:.2f} Mt")
                st.metric("Emissions", f"{final:.3f} Mt")
                st.metric("Abatement", f"{abatement:.2f} Mt")
                st.metric("Total CAPEX", f"${capex:.2f}B")
                st.metric("Total Cost", f"${total_cost:.2f}B")
                st.metric("Avg MAC", f"${mac:.0f}/tCO2")
                st.metric("Facilities Deployed", deployed)

        st.markdown("---")

        # Bar Chart Comparison
        st.header("Scenario Comparison")
        col1, col2 = st.columns(2)

        with col1:
            # Abatement comparison
            compare_data = []
            for scenario in selected_scenarios:
                df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]
                compare_data.append({
                    'Scenario': SCENARIO_NAMES.get(scenario, scenario),
                    'Abatement (MtCO2)': df_s['abatement_tco2'].sum() / 1e6,
                    'Total Cost ($B)': df_s['total_cost_usd'].sum() / 1e9
                })
            compare_df = pd.DataFrame(compare_data)

            fig = px.bar(compare_df, x='Scenario', y='Abatement (MtCO2)',
                        title='Total Abatement by Scenario', color='Scenario')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Cost comparison
            fig = px.bar(compare_df, x='Scenario', y='Total Cost ($B)',
                        title='Total Cost by Scenario', color='Scenario')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        # Technology deployment stacked bar
        st.subheader("Technology Deployment by Scenario")
        tech_data = []
        for scenario in selected_scenarios:
            df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]
            for tech in df_s['technology'].unique():
                df_t = df_s[df_s['technology'] == tech]
                deployed = df_t[df_t['tech_deployed'] == 1]['facility_id'].nunique()
                tech_data.append({
                    'Scenario': SCENARIO_NAMES.get(scenario, scenario),
                    'Technology': tech,
                    'Facilities': deployed
                })

        tech_df = pd.DataFrame(tech_data)
        fig = px.bar(tech_df, x='Scenario', y='Facilities', color='Technology',
                    title='Deployed Facilities by Technology',
                    color_discrete_map=TECH_COLORS)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # MACC Curve
        st.header("Marginal Abatement Cost Curve (MACC)")

        for scenario in selected_scenarios:
            df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]
            df_macc = df_s[df_s['abatement_tco2'] > 0].copy()
            df_macc = df_macc.sort_values('mac_usd_per_tco2')
            df_macc['cumulative_abatement_mtco2'] = df_macc['abatement_tco2'].cumsum() / 1e6

            if len(df_macc) > 0:
                fig = create_macc_figure(df_macc, SCENARIO_NAMES.get(scenario, scenario))
                st.plotly_chart(fig, use_container_width=True)


# ===================== PAGE 2: TECHNOLOGY DETAILS =====================
elif page == "🔧 Technology Details":
    st.title("🔧 Technology Details")

    # Technology Parameters
    st.header("Technology Parameters")

    if 'tech' in assumptions:
        tech = assumptions['tech']

        col1, col2 = st.columns(2)

        with col1:
            # CAPEX learning curve
            capex_data = []
            for _, r in tech.iterrows():
                if r['technology'] != 'RE_PPA':
                    for y in [2025, 2030, 2040, 2050]:
                        capex_data.append({
                            'Technology': r['technology'].replace('_', ' '),
                            'Year': y,
                            'CAPEX (M$/MtCO2)': r[f'capex_{y}_musd_per_mtco2']
                        })

            fig = px.line(pd.DataFrame(capex_data), x='Year', y='CAPEX (M$/MtCO2)',
                         color='Technology', markers=True,
                         title='Technology CAPEX Learning Curve')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Technology summary table
            display_cols = ['technology', 'applies_to', 'trl', 'available_year',
                          'capex_2025_musd_per_mtco2', 'capex_2050_musd_per_mtco2',
                          'opex_pct_capex', 'lifetime_years']
            display_df = tech[display_cols].copy()
            display_df.columns = ['Technology', 'Applies To', 'TRL', 'Available',
                                 'CAPEX 2025', 'CAPEX 2050', 'OPEX %', 'Lifetime']
            st.dataframe(display_df, hide_index=True, use_container_width=True)

    st.markdown("---")

    # Price Trajectories
    st.header("Price Trajectories")
    col1, col2, col3 = st.columns(3)

    with col1:
        if 'h2' in assumptions:
            fig = px.line(assumptions['h2'], x='year', y='h2_price_usd_per_kg',
                         title='Green H2 Price ($/kg)', markers=True)
            fig.add_hline(y=2.0, line_dash="dash", line_color="green",
                         annotation_text="$2/kg target")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if 're' in assumptions:
            fig = px.line(assumptions['re'], x='year', y='re_price_usd_per_mwh',
                         title='RE Price ($/MWh)', markers=True)
            st.plotly_chart(fig, use_container_width=True)

    with col3:
        if 'grid' in assumptions:
            fig = px.area(assumptions['grid'], x='year', y='grid_ef_tco2_per_mwh',
                         title='Grid Emission Factor (tCO2/MWh)')
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # MACC Evolution by Year
    if df is not None and selected_scenarios:
        st.header("MACC Evolution Over Time")

        selected_scenario_single = st.selectbox(
            "Select Scenario",
            selected_scenarios,
            format_func=lambda x: SCENARIO_NAMES.get(x, x)
        )

        # Calculate average MAC by technology over years
        mac_evolution = []
        for year in sorted(df['year'].unique()):
            df_y = df[(df['scenario'] == selected_scenario_single) & (df['year'] == year)]
            for tech in df_y['technology'].unique():
                df_t = df_y[df_y['technology'] == tech]
                total_abatement = df_t['abatement_tco2'].sum()
                total_cost = df_t['total_cost_usd'].sum()
                if total_abatement > 0:
                    mac_evolution.append({
                        'Year': year,
                        'Technology': tech,
                        'MAC ($/tCO2)': total_cost / total_abatement,
                        'Abatement (MtCO2)': total_abatement / 1e6
                    })

        mac_df = pd.DataFrame(mac_evolution)
        mac_df = mac_df[mac_df['Technology'] != 'None']

        col1, col2 = st.columns(2)

        with col1:
            fig = px.line(mac_df, x='Year', y='MAC ($/tCO2)', color='Technology',
                         title='MAC Evolution by Technology', markers=True,
                         color_discrete_map=TECH_COLORS)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.area(mac_df, x='Year', y='Abatement (MtCO2)', color='Technology',
                         title='Abatement by Technology Over Time',
                         color_discrete_map=TECH_COLORS)
            st.plotly_chart(fig, use_container_width=True)


# ===================== PAGE 3: REGIONAL OUTLOOK =====================
elif page == "🗺️ Regional Outlook":
    st.title("🗺️ Regional Transition Outlook")

    if df is None:
        st.error("No scenario data.")
    elif not selected_scenarios:
        st.warning("Please select at least one scenario.")
    else:
        # Regional metrics summary
        st.header(f"Regional Summary ({selected_year})")

        for scenario in selected_scenarios:
            st.subheader(f"📊 {SCENARIO_NAMES.get(scenario, scenario)}")
            df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]

            # Regional metrics cards
            regions = sorted(df_s['region'].unique())
            cols = st.columns(len(regions))

            for i, region in enumerate(regions):
                df_r = df_s[df_s['region'] == region]
                with cols[i]:
                    st.markdown(f"**{region}**")
                    st.metric("Abatement", f"{df_r['abatement_tco2'].sum()/1e6:.2f} Mt")
                    st.metric("CAPEX", f"${df_r['capex_usd'].sum()/1e9:.2f}B")
                    st.metric("Facilities", df_r['facility_id'].nunique())

            st.markdown("---")

        # Regional emission pathways
        st.header("Emission Pathways by Region")

        selected_scenario_single = st.selectbox(
            "Select Scenario for Regional View",
            selected_scenarios,
            format_func=lambda x: SCENARIO_NAMES.get(x, x),
            key="regional_scenario"
        )

        df_s = df[df['scenario'] == selected_scenario_single]
        regions = sorted(df_s['region'].unique())

        cols = st.columns(2)
        for i, region in enumerate(regions):
            with cols[i % 2]:
                reg_df = df_s[df_s['region'] == region]
                yearly = reg_df.groupby('year').agg({
                    'bau_emissions_tco2': 'sum',
                    'emissions_tco2': 'sum'
                }).reset_index()

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=yearly['year'],
                    y=yearly['bau_emissions_tco2'] / 1e6,
                    name='BAU', line=dict(dash='dash', color='red')
                ))
                fig.add_trace(go.Scatter(
                    x=yearly['year'],
                    y=yearly['emissions_tco2'] / 1e6,
                    name='Net Zero', fill='tozeroy',
                    line=dict(color=REGION_COLORS.get(region, '#808080'))
                ))
                fig.update_layout(title=f'{region} - Emission Pathway',
                                height=300, xaxis_title='Year', yaxis_title='MtCO2')
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # H2 demand by region
        st.header("H2 Demand by Region")

        h2_data = []
        for scenario in selected_scenarios:
            if 'h2' in scenario.lower():
                for year in sorted(df['year'].unique()):
                    df_y = df[(df['scenario'] == scenario) & (df['year'] == year)]
                    for region in df_y['region'].unique():
                        df_r = df_y[df_y['region'] == region]
                        h2_data.append({
                            'Scenario': SCENARIO_NAMES.get(scenario, scenario),
                            'Year': year,
                            'Region': region,
                            'H2 Demand (kt)': df_r['h2_demand_t'].sum() / 1e3
                        })

        if h2_data:
            h2_df = pd.DataFrame(h2_data)
            fig = px.line(h2_df, x='Year', y='H2 Demand (kt)', color='Region',
                         facet_col='Scenario', markers=True,
                         title='H2 Demand Trajectory by Region',
                         color_discrete_map=REGION_COLORS)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Cost pathways by region (using pre-computed annual data)
        st.header("Cost Pathways by Region (Annual 2025-2050)")

        if 'abatement' in regional_summaries:
            df_abate = regional_summaries['abatement']
            # Filter for selected scenarios
            df_cost = df_abate[df_abate['scenario'].isin(selected_scenarios)].copy()
            df_cost['Scenario'] = df_cost['scenario'].map(lambda x: SCENARIO_NAMES.get(x, x))
            df_cost['Total Cost ($M)'] = df_cost['capex_usd'] / 1e6

            fig = px.area(df_cost, x='year', y='Total Cost ($M)', color='region',
                         facet_col='Scenario', facet_col_wrap=2,
                         title='Cumulative Cost by Region (Annual)',
                         color_discrete_map=REGION_COLORS)
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Regional summary data not available. Run run_scenarios.py first.")

        st.markdown("---")

        # Regional MAC Curve by Scenario (2025-2050) - using pre-computed annual data
        st.header("Regional MAC Curves (Annual 2025-2050)")
        st.caption("Marginal Abatement Cost evolution by region - separate lines per region")

        if 'mac' in regional_summaries:
            df_mac = regional_summaries['mac']
            # Filter for selected scenarios and non-zero MAC
            df_mac_filtered = df_mac[
                (df_mac['scenario'].isin(selected_scenarios)) &
                (df_mac['mac_usd_per_tco2'] > 0)
            ].copy()
            df_mac_filtered['Scenario'] = df_mac_filtered['scenario'].map(lambda x: SCENARIO_NAMES.get(x, x))

            if len(df_mac_filtered) > 0:
                # Single scenario selector for detailed view
                mac_scenario = st.selectbox(
                    "Select Scenario for Regional MAC Detail",
                    selected_scenarios,
                    format_func=lambda x: SCENARIO_NAMES.get(x, x),
                    key="mac_scenario_select"
                )

                # Single scenario - clear separate lines per region
                df_mac_single = df_mac_filtered[df_mac_filtered['scenario'] == mac_scenario]
                fig = go.Figure()
                for region in ['Daesan', 'Yeosu', 'Ulsan', 'Other']:
                    df_r = df_mac_single[df_mac_single['region'] == region]
                    if len(df_r) > 0:
                        fig.add_trace(go.Scatter(
                            x=df_r['year'],
                            y=df_r['mac_usd_per_tco2'],
                            mode='lines+markers',
                            name=region,
                            line=dict(color=REGION_COLORS.get(region, '#808080'), width=2),
                            marker=dict(size=6)
                        ))
                fig.update_layout(
                    title=f'Regional MAC by Year - {SCENARIO_NAMES.get(mac_scenario, mac_scenario)}',
                    xaxis_title='Year',
                    yaxis_title='MAC ($/tCO2)',
                    legend_title='Region',
                    height=450,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)

                # All scenarios comparison (faceted)
                st.subheader("All Selected Scenarios - Regional MAC Comparison")
                fig = px.line(df_mac_filtered, x='year', y='mac_usd_per_tco2', color='region',
                             facet_col='Scenario', facet_col_wrap=2,
                             markers=True,
                             title='Regional MAC Evolution by Scenario (Annual 2025-2050)',
                             labels={'mac_usd_per_tco2': 'MAC ($/tCO2)', 'year': 'Year', 'region': 'Region'},
                             color_discrete_map=REGION_COLORS)
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

                # MAC Summary Table
                st.subheader("MAC Summary Table ($/tCO2) - 2050")
                mac_2050 = df_mac_filtered[df_mac_filtered['year'] == 2050].copy()
                if len(mac_2050) > 0:
                    mac_pivot = mac_2050.pivot(index='region', columns='Scenario', values='mac_usd_per_tco2')
                    st.dataframe(mac_pivot.style.format("{:.0f}"), use_container_width=True)

                # Heatmap for easier comparison
                st.subheader("MAC Comparison Heatmap (2050)")
                if len(mac_2050) > 0:
                    fig = px.imshow(mac_pivot,
                                   labels=dict(x="Scenario", y="Region", color="MAC ($/tCO2)"),
                                   title='Regional MAC by Scenario (2050)',
                                   color_continuous_scale='RdYlGn_r',
                                   text_auto='.0f')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Regional MAC summary data not available. Run run_scenarios.py first.")

        st.markdown("---")

        # Regional Total Abatement by Scenario (2025-2050) - using pre-computed annual data
        st.header("Regional Abatement Trajectories (Annual 2025-2050)")
        st.caption("Total CO2 abatement evolution by region - separate lines per region")

        if 'abatement' in regional_summaries:
            df_abate = regional_summaries['abatement']
            # Filter for selected scenarios
            df_abate_filtered = df_abate[df_abate['scenario'].isin(selected_scenarios)].copy()
            df_abate_filtered['Scenario'] = df_abate_filtered['scenario'].map(lambda x: SCENARIO_NAMES.get(x, x))

            if len(df_abate_filtered) > 0:
                # Single scenario selector for detailed view
                abate_scenario = st.selectbox(
                    "Select Scenario for Regional Abatement Detail",
                    selected_scenarios,
                    format_func=lambda x: SCENARIO_NAMES.get(x, x),
                    key="abate_scenario_select"
                )

                # Single scenario - clear separate lines per region
                df_abate_single = df_abate_filtered[df_abate_filtered['scenario'] == abate_scenario]
                fig = go.Figure()
                for region in ['Daesan', 'Yeosu', 'Ulsan', 'Other']:
                    df_r = df_abate_single[df_abate_single['region'] == region]
                    if len(df_r) > 0:
                        fig.add_trace(go.Scatter(
                            x=df_r['year'],
                            y=df_r['abatement_mt'],
                            mode='lines+markers',
                            name=region,
                            line=dict(color=REGION_COLORS.get(region, '#808080'), width=2),
                            marker=dict(size=6)
                        ))
                fig.update_layout(
                    title=f'Regional Abatement by Year - {SCENARIO_NAMES.get(abate_scenario, abate_scenario)}',
                    xaxis_title='Year',
                    yaxis_title='Abatement (MtCO2)',
                    legend_title='Region',
                    height=450,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)

                # All scenarios comparison (faceted) - Line chart
                st.subheader("All Selected Scenarios - Regional Abatement Comparison")
                fig = px.line(df_abate_filtered, x='year', y='abatement_mt', color='region',
                             facet_col='Scenario', facet_col_wrap=2,
                             markers=True,
                             title='Regional Abatement Trends by Scenario (Annual 2025-2050)',
                             labels={'abatement_mt': 'Abatement (MtCO2)', 'year': 'Year', 'region': 'Region'},
                             color_discrete_map=REGION_COLORS)
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

                # Summary table
                st.subheader("Abatement Summary by Region (2050)")
                abate_2050 = df_abate_filtered[df_abate_filtered['year'] == 2050].copy()
                if len(abate_2050) > 0:
                    abate_pivot = abate_2050.pivot(index='region', columns='Scenario', values='abatement_mt')
                    abate_pivot['Total'] = abate_pivot.sum(axis=1)
                    st.dataframe(abate_pivot.style.format("{:.2f}"), use_container_width=True)
        else:
            st.warning("Regional abatement summary data not available. Run run_scenarios.py first.")


# ===================== PAGE 4: FACILITY RESULTS =====================
elif page == "🏢 Facility Results":
    st.title("🏢 Facility-Level Results")

    if df is None:
        st.error("No scenario data.")
    elif not selected_scenarios:
        st.warning("Please select at least one scenario.")
    else:
        # Facility summary
        st.header(f"Facility Summary ({selected_year})")

        selected_scenario_single = st.selectbox(
            "Select Scenario",
            selected_scenarios,
            format_func=lambda x: SCENARIO_NAMES.get(x, x),
            key="facility_scenario"
        )

        df_filtered = filter_data(df, selected_year, [selected_scenario_single],
                                  selected_region, selected_tech)

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Facilities", df_filtered['facility_id'].nunique())
        col2.metric("Deployed", df_filtered[df_filtered['tech_deployed'] == 1]['facility_id'].nunique())
        col3.metric("Total Abatement", f"{df_filtered['abatement_tco2'].sum()/1e6:.2f} Mt")
        col4.metric("Total CAPEX", f"${df_filtered['capex_usd'].sum()/1e9:.2f}B")

        st.markdown("---")

        # Facility by region and technology
        st.subheader("Facilities by Region & Technology")

        fac_summary = df_filtered.groupby(['region', 'technology']).agg({
            'facility_id': 'nunique',
            'abatement_tco2': 'sum',
            'capex_usd': 'sum',
            'total_cost_usd': 'sum'
        }).reset_index()
        fac_summary.columns = ['Region', 'Technology', 'Facilities', 'Abatement (tCO2)',
                               'CAPEX ($)', 'Total Cost ($)']

        col1, col2 = st.columns(2)

        with col1:
            fig = px.sunburst(fac_summary, path=['Region', 'Technology'], values='Facilities',
                             title='Facilities by Region & Technology',
                             color='Technology', color_discrete_map=TECH_COLORS)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.treemap(fac_summary[fac_summary['Abatement (tCO2)'] > 0],
                            path=['Region', 'Technology'], values='Abatement (tCO2)',
                            title='Abatement by Region & Technology',
                            color='Technology', color_discrete_map=TECH_COLORS)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Searchable facility table
        st.header("Facility Details")

        # Search box
        search = st.text_input("🔍 Search (company, product, facility ID)", "")

        # Prepare display dataframe
        display_df = df_filtered[[
            'facility_id', 'company', 'product', 'process', 'region', 'technology',
            'capacity_tpy', 'bau_emissions_tco2', 'emissions_tco2', 'abatement_tco2',
            'capex_usd', 'total_cost_usd', 'mac_usd_per_tco2', 'tech_deployed'
        ]].copy()

        display_df.columns = [
            'Facility ID', 'Company', 'Product', 'Process', 'Region', 'Technology',
            'Capacity (t/y)', 'BAU Emissions (tCO2)', 'Emissions (tCO2)', 'Abatement (tCO2)',
            'CAPEX ($)', 'Total Cost ($)', 'MAC ($/tCO2)', 'Deployed'
        ]

        # Apply search filter
        if search:
            mask = (
                display_df['Company'].str.contains(search, case=False, na=False) |
                display_df['Product'].str.contains(search, case=False, na=False) |
                display_df['Facility ID'].str.contains(search, case=False, na=False)
            )
            display_df = display_df[mask]

        # Sort by abatement
        display_df = display_df.sort_values('Abatement (tCO2)', ascending=False)

        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                'Capacity (t/y)': st.column_config.NumberColumn(format="%,.0f"),
                'BAU Emissions (tCO2)': st.column_config.NumberColumn(format="%,.0f"),
                'Emissions (tCO2)': st.column_config.NumberColumn(format="%,.0f"),
                'Abatement (tCO2)': st.column_config.NumberColumn(format="%,.0f"),
                'CAPEX ($)': st.column_config.NumberColumn(format="$%,.0f"),
                'Total Cost ($)': st.column_config.NumberColumn(format="$%,.0f"),
                'MAC ($/tCO2)': st.column_config.NumberColumn(format="$%,.0f"),
                'Deployed': st.column_config.CheckboxColumn()
            }
        )

        st.caption(f"Showing {len(display_df)} facilities")


# ===================== PAGE 5: ENERGY INFRASTRUCTURE =====================
elif page == "⚡ Energy Infrastructure":
    st.title("⚡ Energy Infrastructure Requirements")

    if df is None:
        st.error("No scenario data.")
    elif not selected_scenarios:
        st.warning("Please select at least one scenario.")
    else:
        # Electricity demand comparison
        st.header("Electricity Demand")

        col1, col2 = st.columns(2)

        with col1:
            # Trajectory
            fig = go.Figure()
            for scenario in selected_scenarios:
                df_s = df[df['scenario'] == scenario]
                yearly = df_s.groupby('year')['elec_demand_mwh'].sum().reset_index()
                yearly['TWh'] = yearly['elec_demand_mwh'] / 1e6

                fig.add_trace(go.Scatter(
                    x=yearly['year'],
                    y=yearly['TWh'],
                    name=SCENARIO_NAMES.get(scenario, scenario),
                    mode='lines+markers'
                ))

            fig.update_layout(title='Electricity Demand Trajectory',
                            xaxis_title='Year', yaxis_title='Electricity (TWh)')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # By scenario bar chart (selected year)
            elec_data = []
            for scenario in selected_scenarios:
                df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]
                elec_data.append({
                    'Scenario': SCENARIO_NAMES.get(scenario, scenario),
                    'Electricity (TWh)': df_s['elec_demand_mwh'].sum() / 1e6
                })

            elec_df = pd.DataFrame(elec_data)
            fig = px.bar(elec_df, x='Scenario', y='Electricity (TWh)',
                        title=f'Electricity Demand ({selected_year})',
                        color='Scenario')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Hydrogen demand
        st.header("Hydrogen Demand")

        h2_scenarios = [s for s in selected_scenarios if 'h2' in s.lower()]

        if h2_scenarios:
            col1, col2 = st.columns(2)

            with col1:
                fig = go.Figure()
                for scenario in h2_scenarios:
                    df_s = df[df['scenario'] == scenario]
                    yearly = df_s.groupby('year')['h2_demand_t'].sum().reset_index()
                    yearly['Mt'] = yearly['h2_demand_t'] / 1e6

                    fig.add_trace(go.Scatter(
                        x=yearly['year'],
                        y=yearly['Mt'],
                        name=SCENARIO_NAMES.get(scenario, scenario),
                        mode='lines+markers'
                    ))

                fig.update_layout(title='Hydrogen Demand Trajectory',
                                xaxis_title='Year', yaxis_title='H2 Demand (Mt)')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                h2_data = []
                for scenario in h2_scenarios:
                    df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]
                    h2_data.append({
                        'Scenario': SCENARIO_NAMES.get(scenario, scenario),
                        'H2 Demand (Mt)': df_s['h2_demand_t'].sum() / 1e6
                    })

                h2_df = pd.DataFrame(h2_data)
                fig = px.bar(h2_df, x='Scenario', y='H2 Demand (Mt)',
                            title=f'H2 Demand ({selected_year})', color='Scenario')
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select H2-based scenarios to view hydrogen demand")

        st.markdown("---")

        # Regional breakdown
        st.header(f"Regional Energy Breakdown ({selected_year})")

        for scenario in selected_scenarios:
            st.subheader(SCENARIO_NAMES.get(scenario, scenario))
            df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]

            col1, col2 = st.columns(2)

            with col1:
                reg_elec = df_s.groupby('region')['elec_demand_mwh'].sum().reset_index()
                reg_elec['TWh'] = reg_elec['elec_demand_mwh'] / 1e6
                fig = px.pie(reg_elec, values='TWh', names='region',
                            title='Electricity by Region',
                            color='region', color_discrete_map=REGION_COLORS)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                if 'h2' in scenario.lower():
                    reg_h2 = df_s.groupby('region')['h2_demand_t'].sum().reset_index()
                    reg_h2['kt'] = reg_h2['h2_demand_t'] / 1e3
                    fig = px.pie(reg_h2, values='kt', names='region',
                                title='H2 Demand by Region',
                                color='region', color_discrete_map=REGION_COLORS)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("H2 demand not applicable for electric scenarios")

            # Summary metrics
            cols = st.columns(4)
            cols[0].metric("Total Electricity", f"{df_s['elec_demand_mwh'].sum()/1e6:.1f} TWh")
            cols[1].metric("Total H2", f"{df_s['h2_demand_t'].sum()/1e3:.0f} kt")
            cols[2].metric("Total Heat", f"{df_s['heat_demand_gj'].sum()/1e6:.1f} PJ")
            cols[3].metric("Total CAPEX", f"${df_s['capex_usd'].sum()/1e9:.2f}B")

            st.markdown("---")


# Footer
st.markdown("---")
st.caption("Korea Petrochemical Net Zero Analysis | 2025 | NO CCS/CCUS | SFOC")
