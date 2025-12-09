"""
Korea Petrochemical Net Zero Dashboard v2
=========================================
Comprehensive dashboard with 5 pages:
1. Scenario Comparison - Summary cards, bar charts, MACC curve
2. Technology Details - Parameters, MACC evolution by year
3. Regional Transition Outlook - Regional metrics, H2 demand, cost pathways
4. Facility-Level Results - Summaries and searchable table
5. Energy Infrastructure - Electricity and H2 demand by scenario

Reads from outputs/scenario_results.csv
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Korea Petrochemical Net Zero",
    page_icon="🏭",
    layout="wide"
)

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = BASE_DIR / "outputs" / "scenario_results.csv"

# Scenario names
SCENARIO_NAMES = {
    'shaheen_ncc_h2': 'Shaheen + NCC-H2',
    'shaheen_ncc_elec': 'Shaheen + NCC-Elec',
    'restructure_25pct_ncc_h2': 'Restructure 25% + NCC-H2',
    'restructure_25pct_ncc_elec': 'Restructure 25% + NCC-Elec',
    'restructure_40pct_ncc_h2': 'Restructure 40% + NCC-H2',
    'restructure_40pct_ncc_elec': 'Restructure 40% + NCC-Elec',
}

# Emission targets
EMISSION_TARGETS = {
    2025: 0.000,
    2030: 0.150,
    2035: 0.245,  # Korea industry NDC
    2040: 0.500,
    2045: 0.750,
    2050: 1.000,  # Net Zero
}

# Colors
TECH_COLORS = {
    'None': '#95a5a6',
    'NCC-H2': '#3498db',
    'NCC-Electricity': '#9b59b6',
    'RDH': '#e67e22',
    'Heat_Pump': '#e74c3c',
}

REGION_COLORS = {
    'Daesan': '#1abc9c',
    'Yeosu': '#3498db',
    'Ulsan': '#9b59b6',
    'Other': '#e74c3c',
}


@st.cache_data
def load_data():
    """Load scenario results"""
    if OUTPUT_FILE.exists():
        return pd.read_csv(OUTPUT_FILE)
    return None


@st.cache_data
def load_assumptions():
    """Load input assumptions"""
    data = {}
    try:
        data['tech'] = pd.read_csv(DATA_DIR / "technology_parameters.csv")
        data['h2'] = pd.read_csv(DATA_DIR / "h2_price_trajectory.csv")
        data['re'] = pd.read_csv(DATA_DIR / "re_price_trajectory.csv")
        data['grid'] = pd.read_csv(DATA_DIR / "grid_emission_trajectory.csv")
    except Exception as e:
        st.error(f"Error loading assumptions: {e}")
    return data


# Load data
df = load_data()
assumptions = load_assumptions()

# Check if data loaded
if df is None:
    st.error("No data found. Please run `python run_scenarios.py` first.")
    st.stop()

# =============================================================================
# SIDEBAR
# =============================================================================
st.sidebar.title("🏭 Korea Petrochemical")
st.sidebar.markdown("**Net Zero Dashboard**")
st.sidebar.markdown("---")

# Page selection
page = st.sidebar.radio(
    "📑 Select Page",
    ["1. Scenario Comparison", "2. Technology Details", "3. Regional Outlook",
     "4. Facility Results", "5. Energy Infrastructure"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Filters")

# Year
years = sorted(df['year'].unique())
selected_year = st.sidebar.select_slider("Year", options=years, value=2050)

# Scenario (multi-select for comparison)
scenarios = df['scenario'].unique().tolist()
selected_scenarios = st.sidebar.multiselect(
    "Scenarios",
    scenarios,
    default=scenarios[:2],
    format_func=lambda x: SCENARIO_NAMES.get(x, x)
)

if not selected_scenarios:
    selected_scenarios = [scenarios[0]]

st.sidebar.markdown("---")

# Info box
total_facilities = df['facility_id'].nunique()
shaheen_facilities = df[df['scenario'].str.contains('shaheen')]['facility_id'].nunique()
st.sidebar.info(
    f"**Data Summary**\n\n"
    f"Total Facilities: {total_facilities}\n\n"
    f"Shaheen: +6 facilities\n\n"
    f"Targets: 24.5% (2035), 100% (2050)\n\n"
    f"**NO CCS/CCUS**"
)


# =============================================================================
# PAGE 1: SCENARIO COMPARISON
# =============================================================================
if page == "1. Scenario Comparison":
    st.title("📊 Scenario Comparison")

    # Summary cards
    st.header(f"Summary Metrics ({selected_year})")

    cols = st.columns(len(selected_scenarios))
    for i, scenario in enumerate(selected_scenarios):
        df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]
        df_base = df[(df['scenario'] == scenario) & (df['year'] == 2025)]

        with cols[i]:
            st.subheader(SCENARIO_NAMES.get(scenario, scenario))

            baseline = df_base['bau_emissions_tco2'].sum() / 1e6
            emissions = df_s['emissions_tco2'].sum() / 1e6
            abatement = df_s['abatement_tco2'].sum() / 1e6
            total_cost = df_s['total_cost_usd'].sum() / 1e9
            total_capex = df_s['capex_usd'].sum() / 1e9
            mac = df_s['total_cost_usd'].sum() / df_s['abatement_tco2'].sum() if df_s['abatement_tco2'].sum() > 0 else 0
            deployed = df_s[df_s['tech_deployed'] == 1]['facility_id'].nunique()

            st.metric("Baseline (2025)", f"{baseline:.2f} Mt")
            st.metric("Emissions", f"{emissions:.2f} Mt")
            st.metric("Abatement", f"{abatement:.2f} Mt")
            st.metric("Total CAPEX", f"${total_capex:.1f}B")
            st.metric("Avg MAC", f"${mac:.0f}/tCO2")
            st.metric("Facilities Deployed", deployed)

    st.markdown("---")

    # Bar chart comparison
    st.header("Scenario Comparison")
    col1, col2 = st.columns(2)

    compare_data = []
    for scenario in selected_scenarios:
        df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]
        compare_data.append({
            'Scenario': SCENARIO_NAMES.get(scenario, scenario),
            'Abatement (MtCO2)': df_s['abatement_tco2'].sum() / 1e6,
            'Total Cost ($B)': df_s['total_cost_usd'].sum() / 1e9,
            'CAPEX ($B)': df_s['capex_usd'].sum() / 1e9,
        })
    compare_df = pd.DataFrame(compare_data)

    with col1:
        fig = px.bar(compare_df, x='Scenario', y='Abatement (MtCO2)',
                    title='Total Abatement by Scenario', color='Scenario')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(compare_df, x='Scenario', y='CAPEX ($B)',
                    title='Total CAPEX by Scenario', color='Scenario')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Technology deployment stacked bar
    st.subheader("Technology Deployment by Scenario")
    tech_data = []
    for scenario in selected_scenarios:
        df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]
        for tech in df_s['technology'].dropna().unique():
            if tech != 'None':
                df_t = df_s[df_s['technology'] == tech]
                deployed = df_t[df_t['tech_deployed'] == 1]['facility_id'].nunique()
                abatement = df_t['abatement_tco2'].sum() / 1e6
                tech_data.append({
                    'Scenario': SCENARIO_NAMES.get(scenario, scenario),
                    'Technology': tech,
                    'Facilities': deployed,
                    'Abatement (Mt)': abatement
                })

    if tech_data:
        tech_df = pd.DataFrame(tech_data)
        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(tech_df, x='Scenario', y='Facilities', color='Technology',
                        title='Deployed Facilities by Technology',
                        color_discrete_map=TECH_COLORS)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(tech_df, x='Scenario', y='Abatement (Mt)', color='Technology',
                        title='Abatement by Technology',
                        color_discrete_map=TECH_COLORS)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # MACC Curve
    st.header("Marginal Abatement Cost Curve (MACC)")

    for scenario in selected_scenarios:
        df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]
        df_macc = df_s[df_s['abatement_tco2'] > 0].copy()
        df_macc = df_macc.sort_values('mac_usd_per_tco2')
        df_macc['cumulative_abatement'] = df_macc['abatement_tco2'].cumsum() / 1e6

        if len(df_macc) > 0:
            fig = go.Figure()

            for tech in df_macc['technology'].dropna().unique():
                df_tech = df_macc[df_macc['technology'] == tech]
                fig.add_trace(go.Bar(
                    x=df_tech['abatement_tco2'] / 1e6,
                    y=df_tech['mac_usd_per_tco2'],
                    name=tech,
                    marker_color=TECH_COLORS.get(tech, '#808080'),
                    hovertemplate=(
                        '<b>%{customdata[0]}</b><br>'
                        'Product: %{customdata[1]}<br>'
                        'Region: %{customdata[2]}<br>'
                        'Abatement: %{x:.3f} Mt<br>'
                        'MAC: $%{y:.0f}/tCO2<extra></extra>'
                    ),
                    customdata=df_tech[['company', 'product', 'region']].values
                ))

            fig.update_layout(
                title=f'MACC - {SCENARIO_NAMES.get(scenario, scenario)} ({selected_year})',
                barmode='stack',
                xaxis_title='Abatement (MtCO2)',
                yaxis_title='MAC ($/tCO2)',
                height=500,
                legend=dict(orientation='h', y=1.05)
            )
            st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# PAGE 2: TECHNOLOGY DETAILS
# =============================================================================
elif page == "2. Technology Details":
    st.title("🔧 Technology Details")

    # Technology selector
    available_techs = df['technology'].dropna().unique().tolist()
    available_techs = [t for t in available_techs if t != 'None']
    selected_tech = st.selectbox("Select Technology", available_techs)

    st.markdown("---")

    # Technology parameters from Assumptions
    st.header("Technology Parameters")

    if 'tech' in assumptions:
        tech_df = assumptions['tech']
        tech_row = tech_df[tech_df['technology'].str.contains(selected_tech.split('-')[0], case=False)]

        if len(tech_row) > 0:
            tech_row = tech_row.iloc[0]
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("TRL", f"{tech_row.get('trl', 'N/A')}")
            col2.metric("Available Year", f"{int(tech_row.get('available_year', 2025))}")
            col3.metric("Lifetime", f"{int(tech_row.get('lifetime_years', 25))} years")
            col4.metric("OPEX (% CAPEX)", f"{tech_row.get('opex_pct_capex', 3)}%")

            # CAPEX trajectory
            st.subheader("CAPEX Learning Curve")
            capex_data = []
            for year in [2025, 2030, 2040, 2050]:
                capex_data.append({
                    'Year': year,
                    'CAPEX (M$/MtCO2)': tech_row.get(f'capex_{year}_musd_per_mtco2', 0)
                })

            fig = px.line(pd.DataFrame(capex_data), x='Year', y='CAPEX (M$/MtCO2)',
                         markers=True, title=f'{selected_tech} CAPEX Trajectory')
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # MACC Evolution by Year
    st.header("MACC Evolution Over Time")

    scenario_single = st.selectbox(
        "Select Scenario for MACC Evolution",
        selected_scenarios,
        format_func=lambda x: SCENARIO_NAMES.get(x, x)
    )

    mac_evolution = []
    for year in sorted(df['year'].unique()):
        df_y = df[(df['scenario'] == scenario_single) & (df['year'] == year) & (df['technology'] == selected_tech)]
        if len(df_y) > 0:
            total_abatement = df_y['abatement_tco2'].sum()
            total_cost = df_y['total_cost_usd'].sum()
            deployed = df_y[df_y['tech_deployed'] == 1]['facility_id'].nunique()
            if total_abatement > 0:
                mac_evolution.append({
                    'Year': year,
                    'MAC ($/tCO2)': total_cost / total_abatement,
                    'Abatement (MtCO2)': total_abatement / 1e6,
                    'Facilities Deployed': deployed
                })

    if mac_evolution:
        mac_df = pd.DataFrame(mac_evolution)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(mac_df, x='Year', y='MAC ($/tCO2)', markers=True,
                         title=f'{selected_tech} - MAC Evolution')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(mac_df, x='Year', y='Abatement (MtCO2)',
                        title=f'{selected_tech} - Abatement by Year')
            st.plotly_chart(fig, use_container_width=True)

    # Note for RDH
    if selected_tech == 'RDH':
        st.info("**Note:** RDH (RotoDynamic Heater) applies to BTX facilities where Heat Pump is not applicable due to high temperature requirements (>165°C).")


# =============================================================================
# PAGE 3: REGIONAL OUTLOOK
# =============================================================================
elif page == "3. Regional Outlook":
    st.title("🗺️ Regional Transition Outlook")

    # Regional metrics summary
    st.header(f"Regional Summary ({selected_year})")

    scenario_single = st.selectbox(
        "Select Scenario",
        selected_scenarios,
        format_func=lambda x: SCENARIO_NAMES.get(x, x),
        key="regional_scenario"
    )

    df_s = df[(df['scenario'] == scenario_single) & (df['year'] == selected_year)]
    regions = sorted(df_s['region'].unique())

    # Metrics by region
    cols = st.columns(len(regions))
    for i, region in enumerate(regions):
        df_r = df_s[df_s['region'] == region]
        with cols[i]:
            st.markdown(f"**{region}**")
            st.metric("Abatement", f"{df_r['abatement_tco2'].sum()/1e6:.2f} Mt")
            st.metric("CAPEX", f"${df_r['capex_usd'].sum()/1e9:.2f}B")
            mac = df_r['total_cost_usd'].sum() / df_r['abatement_tco2'].sum() if df_r['abatement_tco2'].sum() > 0 else 0
            st.metric("MAC", f"${mac:.0f}/t")
            st.metric("Facilities", df_r['facility_id'].nunique())

    st.markdown("---")

    # H2 demand by region
    st.header("H2 Demand by Region")

    h2_data = []
    df_full = df[df['scenario'] == scenario_single]
    for year in sorted(df['year'].unique()):
        df_y = df_full[df_full['year'] == year]
        for region in regions:
            df_r = df_y[df_y['region'] == region]
            h2_data.append({
                'Year': year,
                'Region': region,
                'H2 Demand (kt)': df_r['h2_demand_t'].sum() / 1e3
            })

    h2_df = pd.DataFrame(h2_data)
    fig = px.line(h2_df, x='Year', y='H2 Demand (kt)', color='Region',
                 markers=True, title='H2 Demand Trajectory by Region',
                 color_discrete_map=REGION_COLORS)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Cost pathway by region
    st.header("Cost Pathways by Region")

    cost_data = []
    for year in sorted(df['year'].unique()):
        df_y = df_full[df_full['year'] == year]
        for region in regions:
            df_r = df_y[df_y['region'] == region]
            cost_data.append({
                'Year': year,
                'Region': region,
                'Total Cost ($M)': df_r['total_cost_usd'].sum() / 1e6,
                'CAPEX ($M)': df_r['capex_usd'].sum() / 1e6
            })

    cost_df = pd.DataFrame(cost_data)
    fig = px.area(cost_df, x='Year', y='Total Cost ($M)', color='Region',
                 title='Total Cost by Region Over Time',
                 color_discrete_map=REGION_COLORS)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Regional MACC curves
    st.header("Regional MACC Curves")

    col1, col2 = st.columns(2)
    for i, region in enumerate(regions):
        df_r = df_s[(df_s['region'] == region) & (df_s['abatement_tco2'] > 0)]
        df_r = df_r.sort_values('mac_usd_per_tco2')

        if len(df_r) > 0:
            with [col1, col2][i % 2]:
                fig = go.Figure()
                for tech in df_r['technology'].dropna().unique():
                    df_t = df_r[df_r['technology'] == tech]
                    fig.add_trace(go.Bar(
                        x=df_t['abatement_tco2'] / 1e6,
                        y=df_t['mac_usd_per_tco2'],
                        name=tech,
                        marker_color=TECH_COLORS.get(tech, '#808080')
                    ))
                fig.update_layout(
                    title=f'{region} MACC',
                    barmode='stack',
                    xaxis_title='Abatement (Mt)',
                    yaxis_title='MAC ($/tCO2)',
                    height=350,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# PAGE 4: FACILITY RESULTS
# =============================================================================
elif page == "4. Facility Results":
    st.title("🏢 Facility-Level Results")

    # Summary
    st.header("Facility Summary")

    scenario_single = st.selectbox(
        "Select Scenario",
        selected_scenarios,
        format_func=lambda x: SCENARIO_NAMES.get(x, x),
        key="facility_scenario"
    )

    df_s = df[(df['scenario'] == scenario_single) & (df['year'] == selected_year)]

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    total_fac = df_s['facility_id'].nunique()
    deployed_fac = df_s[df_s['tech_deployed'] == 1]['facility_id'].nunique()
    not_deployed = total_fac - deployed_fac

    col1.metric("Total Facilities", total_fac)
    col2.metric("Deployed", deployed_fac)
    col3.metric("Not Deployed", not_deployed)

    # Shaheen note
    if 'shaheen' in scenario_single:
        col4.metric("Shaheen Additions", "+6")
    else:
        col4.metric("Base Facilities", "237")

    st.markdown("---")

    # Breakdown by region
    st.subheader("Facilities by Region")
    region_summary = df_s.groupby('region').agg({
        'facility_id': 'nunique',
        'tech_deployed': 'sum',
        'abatement_tco2': 'sum',
        'capex_usd': 'sum'
    }).reset_index()
    region_summary.columns = ['Region', 'Total', 'Deployed', 'Abatement (tCO2)', 'CAPEX ($)']
    region_summary['Abatement (Mt)'] = region_summary['Abatement (tCO2)'] / 1e6
    region_summary['CAPEX ($B)'] = region_summary['CAPEX ($)'] / 1e9

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(region_summary, values='Total', names='Region',
                    title='Facilities by Region', color='Region',
                    color_discrete_map=REGION_COLORS)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(region_summary, x='Region', y=['Total', 'Deployed'],
                    title='Deployed vs Total by Region', barmode='group')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Allocation by technology
    st.subheader("Allocation by Technology")
    tech_summary = df_s[df_s['technology'] != 'None'].groupby('technology').agg({
        'facility_id': 'nunique',
        'abatement_tco2': 'sum',
        'capex_usd': 'sum'
    }).reset_index()
    tech_summary.columns = ['Technology', 'Facilities', 'Abatement (tCO2)', 'CAPEX ($)']

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(tech_summary, values='Facilities', names='Technology',
                    title='Facilities by Technology', color='Technology',
                    color_discrete_map=TECH_COLORS)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(tech_summary, values='Abatement (tCO2)', names='Technology',
                    title='Abatement by Technology', color='Technology',
                    color_discrete_map=TECH_COLORS)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Searchable facility table
    st.header("Facility Details")

    col1, col2, col3 = st.columns(3)
    with col1:
        filter_region = st.selectbox("Filter by Region", ['All'] + sorted(df_s['region'].unique().tolist()))
    with col2:
        filter_tech = st.selectbox("Filter by Technology", ['All'] + sorted(df_s['technology'].dropna().unique().tolist()))
    with col3:
        search = st.text_input("Search (company/product)")

    # Apply filters
    display_df = df_s.copy()
    if filter_region != 'All':
        display_df = display_df[display_df['region'] == filter_region]
    if filter_tech != 'All':
        display_df = display_df[display_df['technology'] == filter_tech]
    if search:
        mask = (
            display_df['company'].str.contains(search, case=False, na=False) |
            display_df['product'].str.contains(search, case=False, na=False)
        )
        display_df = display_df[mask]

    # Format table
    display_cols = ['facility_id', 'company', 'product', 'region', 'technology',
                   'capacity_tpy', 'bau_emissions_tco2', 'abatement_tco2',
                   'capex_usd', 'mac_usd_per_tco2', 'tech_deployed', 'install_year']
    display_cols = [c for c in display_cols if c in display_df.columns]

    display_df = display_df[display_cols].sort_values('abatement_tco2', ascending=False)

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            'capacity_tpy': st.column_config.NumberColumn('Capacity (t/y)', format="%,.0f"),
            'bau_emissions_tco2': st.column_config.NumberColumn('BAU (tCO2)', format="%,.0f"),
            'abatement_tco2': st.column_config.NumberColumn('Abatement (tCO2)', format="%,.0f"),
            'capex_usd': st.column_config.NumberColumn('CAPEX ($)', format="$%,.0f"),
            'mac_usd_per_tco2': st.column_config.NumberColumn('MAC ($/tCO2)', format="$%,.0f"),
            'tech_deployed': st.column_config.CheckboxColumn('Deployed'),
            'install_year': st.column_config.NumberColumn('Install Year', format="%d"),
        }
    )
    st.caption(f"Showing {len(display_df)} facilities")


# =============================================================================
# PAGE 5: ENERGY INFRASTRUCTURE
# =============================================================================
elif page == "5. Energy Infrastructure":
    st.title("⚡ Energy Infrastructure")

    # Electricity demand by scenario
    st.header("Electricity Demand")

    col1, col2 = st.columns(2)

    with col1:
        # Trajectory
        elec_data = []
        for scenario in selected_scenarios:
            df_s = df[df['scenario'] == scenario]
            for year in sorted(df['year'].unique()):
                df_y = df_s[df_s['year'] == year]
                elec_data.append({
                    'Year': year,
                    'Scenario': SCENARIO_NAMES.get(scenario, scenario),
                    'Electricity (TWh)': df_y['elec_demand_mwh'].sum() / 1e6
                })

        elec_df = pd.DataFrame(elec_data)
        fig = px.line(elec_df, x='Year', y='Electricity (TWh)', color='Scenario',
                     markers=True, title='Electricity Demand Trajectory')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Bar for selected year
        elec_year = []
        for scenario in selected_scenarios:
            df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]
            elec_year.append({
                'Scenario': SCENARIO_NAMES.get(scenario, scenario),
                'Electricity (TWh)': df_s['elec_demand_mwh'].sum() / 1e6
            })

        fig = px.bar(pd.DataFrame(elec_year), x='Scenario', y='Electricity (TWh)',
                    title=f'Electricity Demand ({selected_year})', color='Scenario')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # H2 demand by scenario
    st.header("Hydrogen Demand")

    h2_scenarios = [s for s in selected_scenarios if 'h2' in s.lower()]

    if h2_scenarios:
        col1, col2 = st.columns(2)

        with col1:
            h2_data = []
            for scenario in h2_scenarios:
                df_s = df[df['scenario'] == scenario]
                for year in sorted(df['year'].unique()):
                    df_y = df_s[df_s['year'] == year]
                    h2_data.append({
                        'Year': year,
                        'Scenario': SCENARIO_NAMES.get(scenario, scenario),
                        'H2 (Mt)': df_y['h2_demand_t'].sum() / 1e6
                    })

            h2_df = pd.DataFrame(h2_data)
            fig = px.line(h2_df, x='Year', y='H2 (Mt)', color='Scenario',
                         markers=True, title='H2 Demand Trajectory')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            h2_year = []
            for scenario in h2_scenarios:
                df_s = df[(df['scenario'] == scenario) & (df['year'] == selected_year)]
                h2_year.append({
                    'Scenario': SCENARIO_NAMES.get(scenario, scenario),
                    'H2 (Mt)': df_s['h2_demand_t'].sum() / 1e6
                })

            fig = px.bar(pd.DataFrame(h2_year), x='Scenario', y='H2 (Mt)',
                        title=f'H2 Demand ({selected_year})', color='Scenario')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select H2-based scenarios to view hydrogen demand")

    st.markdown("---")

    # Required capacity and % of Korea total
    st.header("Infrastructure Requirements")

    scenario_single = selected_scenarios[0]
    df_s = df[(df['scenario'] == scenario_single) & (df['year'] == selected_year)]

    elec_twh = df_s['elec_demand_mwh'].sum() / 1e6
    h2_mt = df_s['h2_demand_t'].sum() / 1e6

    # Korea total electricity: ~600 TWh/year (2023)
    KOREA_ELEC_TWH = 600
    # Korea H2 target: ~3 Mt by 2050
    KOREA_H2_TARGET = 3.0

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Electricity")
        st.metric("Demand", f"{elec_twh:.1f} TWh")
        st.metric("% of Korea Total", f"{elec_twh/KOREA_ELEC_TWH*100:.1f}%")
        st.caption(f"Based on Korea electricity consumption ~{KOREA_ELEC_TWH} TWh/year")

    with col2:
        st.subheader("Green Hydrogen")
        st.metric("Demand", f"{h2_mt:.3f} Mt")
        if h2_mt > 0:
            st.metric("% of Korea H2 Target", f"{h2_mt/KOREA_H2_TARGET*100:.1f}%")
            # Electricity for H2: ~50 kWh/kg H2
            elec_for_h2 = h2_mt * 1e6 * 50 / 1e6  # TWh
            st.metric("Electricity for H2 Production", f"{elec_for_h2:.1f} TWh")
        st.caption(f"Based on Korea H2 target ~{KOREA_H2_TARGET} Mt by 2050")

    st.markdown("---")

    # Regional breakdown
    st.header("Regional Energy Breakdown")

    region_energy = df_s.groupby('region').agg({
        'elec_demand_mwh': 'sum',
        'h2_demand_t': 'sum'
    }).reset_index()
    region_energy['Electricity (TWh)'] = region_energy['elec_demand_mwh'] / 1e6
    region_energy['H2 (kt)'] = region_energy['h2_demand_t'] / 1e3

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(region_energy, values='Electricity (TWh)', names='region',
                    title='Electricity by Region', color='region',
                    color_discrete_map=REGION_COLORS)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(region_energy, values='H2 (kt)', names='region',
                    title='H2 Demand by Region', color='region',
                    color_discrete_map=REGION_COLORS)
        st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.caption("Korea Petrochemical Net Zero Analysis | Targets: 24.5% (2035), 100% (2050) | NO CCS/CCUS")
