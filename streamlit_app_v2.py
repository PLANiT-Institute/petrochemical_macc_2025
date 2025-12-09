"""
Korea Petrochemical Net Zero Dashboard v2
=========================================
Clean, simple dashboard reading from outputs/scenario_results.csv
"""

import streamlit as st
import pandas as pd
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


# Load data
df = load_data()

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
    "Select Page",
    ["Overview", "MACC Curve", "Regional Analysis", "Facility Details"]
)

st.sidebar.markdown("---")

# Filters
st.sidebar.markdown("### Filters")

# Year
years = sorted(df['year'].unique())
selected_year = st.sidebar.select_slider("Year", options=years, value=2050)

# Scenario
scenarios = df['scenario'].unique().tolist()
selected_scenario = st.sidebar.selectbox(
    "Scenario",
    scenarios,
    format_func=lambda x: SCENARIO_NAMES.get(x, x)
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Facilities: {df['facility_id'].nunique()}")
st.sidebar.caption(f"Scenarios: {len(scenarios)}")
st.sidebar.caption("NO CCS/CCUS")

# =============================================================================
# PAGE: OVERVIEW
# =============================================================================
if page == "Overview":
    st.title("📊 Scenario Overview")
    st.markdown(f"**Scenario:** {SCENARIO_NAMES.get(selected_scenario, selected_scenario)} | **Year:** {selected_year}")

    # Filter data
    df_year = df[(df['scenario'] == selected_scenario) & (df['year'] == selected_year)]
    df_base = df[(df['scenario'] == selected_scenario) & (df['year'] == 2025)]

    # Key metrics
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)

    baseline_emissions = df_base['bau_emissions_tco2'].sum() / 1e6
    final_emissions = df_year['emissions_tco2'].sum() / 1e6
    total_abatement = df_year['abatement_tco2'].sum() / 1e6
    total_capex = df_year['capex_usd'].sum() / 1e9
    avg_mac = df_year['total_cost_usd'].sum() / df_year['abatement_tco2'].sum() if df_year['abatement_tco2'].sum() > 0 else 0

    col1.metric("Baseline (2025)", f"{baseline_emissions:.2f} Mt")
    col2.metric("Emissions", f"{final_emissions:.3f} Mt")
    col3.metric("Abatement", f"{total_abatement:.2f} Mt")
    col4.metric("CAPEX", f"${total_capex:.1f}B")
    col5.metric("Avg MAC", f"${avg_mac:.0f}/t")

    st.markdown("---")

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        # Emission trajectory
        st.subheader("Emission Trajectory")
        df_s = df[df['scenario'] == selected_scenario]
        yearly = df_s.groupby('year').agg({
            'bau_emissions_tco2': 'sum',
            'emissions_tco2': 'sum'
        }).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly['year'], y=yearly['bau_emissions_tco2'] / 1e6,
            name='BAU', line=dict(dash='dash', color='gray')
        ))
        fig.add_trace(go.Scatter(
            x=yearly['year'], y=yearly['emissions_tco2'] / 1e6,
            name='Net Zero', fill='tozeroy', line=dict(color='#27ae60')
        ))
        fig.update_layout(
            xaxis_title='Year', yaxis_title='Emissions (MtCO2)',
            height=400, legend=dict(orientation='h', y=1.1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Technology deployment
        st.subheader("Technology Deployment")
        tech_summary = df_year.groupby('technology').agg({
            'facility_id': 'nunique',
            'abatement_tco2': 'sum'
        }).reset_index()
        tech_summary.columns = ['Technology', 'Facilities', 'Abatement']
        tech_summary = tech_summary[tech_summary['Technology'] != 'None']
        tech_summary['Abatement (Mt)'] = tech_summary['Abatement'] / 1e6

        fig = px.bar(
            tech_summary, x='Technology', y='Abatement (Mt)',
            color='Technology', color_discrete_map=TECH_COLORS,
            text='Facilities'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Regional breakdown
    st.markdown("---")
    st.subheader("Regional Breakdown")

    regional = df_year.groupby('region').agg({
        'facility_id': 'nunique',
        'bau_emissions_tco2': 'sum',
        'abatement_tco2': 'sum',
        'capex_usd': 'sum',
        'elec_demand_mwh': 'sum',
        'h2_demand_t': 'sum'
    }).reset_index()

    regional.columns = ['Region', 'Facilities', 'BAU (tCO2)', 'Abatement (tCO2)',
                       'CAPEX ($)', 'Elec (MWh)', 'H2 (t)']
    regional['Abatement (Mt)'] = regional['Abatement (tCO2)'] / 1e6
    regional['CAPEX ($B)'] = regional['CAPEX ($)'] / 1e9
    regional['Elec (TWh)'] = regional['Elec (MWh)'] / 1e6
    regional['H2 (kt)'] = regional['H2 (t)'] / 1e3

    col1, col2, col3 = st.columns(3)

    with col1:
        fig = px.pie(regional, values='Abatement (Mt)', names='Region',
                    title='Abatement by Region', color='Region',
                    color_discrete_map=REGION_COLORS)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(regional, values='CAPEX ($B)', names='Region',
                    title='CAPEX by Region', color='Region',
                    color_discrete_map=REGION_COLORS)
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        fig = px.pie(regional, values='Elec (TWh)', names='Region',
                    title='Electricity by Region', color='Region',
                    color_discrete_map=REGION_COLORS)
        st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# PAGE: MACC CURVE
# =============================================================================
elif page == "MACC Curve":
    st.title("📈 Marginal Abatement Cost Curve")
    st.markdown(f"**Scenario:** {SCENARIO_NAMES.get(selected_scenario, selected_scenario)} | **Year:** {selected_year}")

    # Filter data
    df_year = df[(df['scenario'] == selected_scenario) & (df['year'] == selected_year)]
    df_macc = df_year[df_year['abatement_tco2'] > 0].copy()
    df_macc = df_macc.sort_values('mac_usd_per_tco2')
    df_macc['cumulative_abatement'] = df_macc['abatement_tco2'].cumsum() / 1e6

    st.markdown("---")

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Facilities with Abatement", len(df_macc))
    col2.metric("Total Abatement", f"{df_macc['abatement_tco2'].sum()/1e6:.2f} Mt")
    col3.metric("MAC Range", f"${df_macc['mac_usd_per_tco2'].min():.0f} - ${df_macc['mac_usd_per_tco2'].max():.0f}/t")

    st.markdown("---")

    # MACC Chart
    fig = go.Figure()

    for tech in df_macc['technology'].unique():
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
        barmode='stack',
        xaxis_title='Abatement (MtCO2)',
        yaxis_title='MAC ($/tCO2)',
        height=600,
        legend=dict(orientation='h', y=1.05)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Data table
    st.markdown("---")
    st.subheader("MACC Data Table")

    display_df = df_macc[[
        'facility_id', 'company', 'product', 'region', 'technology',
        'abatement_tco2', 'total_cost_usd', 'mac_usd_per_tco2'
    ]].copy()
    display_df.columns = ['ID', 'Company', 'Product', 'Region', 'Technology',
                         'Abatement (tCO2)', 'Total Cost ($)', 'MAC ($/tCO2)']

    st.dataframe(display_df, hide_index=True, use_container_width=True)


# =============================================================================
# PAGE: REGIONAL ANALYSIS
# =============================================================================
elif page == "Regional Analysis":
    st.title("🗺️ Regional Analysis")
    st.markdown(f"**Scenario:** {SCENARIO_NAMES.get(selected_scenario, selected_scenario)}")

    df_s = df[df['scenario'] == selected_scenario]
    regions = sorted(df_s['region'].unique())

    st.markdown("---")

    # Regional emission pathways
    st.subheader("Emission Pathways by Region")

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
                x=yearly['year'], y=yearly['bau_emissions_tco2'] / 1e6,
                name='BAU', line=dict(dash='dash', color='red')
            ))
            fig.add_trace(go.Scatter(
                x=yearly['year'], y=yearly['emissions_tco2'] / 1e6,
                name='Net Zero', fill='tozeroy',
                line=dict(color=REGION_COLORS.get(region, '#3498db'))
            ))
            fig.update_layout(
                title=region, height=300,
                xaxis_title='Year', yaxis_title='MtCO2',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Regional summary table
    st.subheader(f"Regional Summary ({selected_year})")

    df_year = df_s[df_s['year'] == selected_year]
    summary = df_year.groupby('region').agg({
        'facility_id': 'nunique',
        'capacity_tpy': 'sum',
        'bau_emissions_tco2': 'sum',
        'emissions_tco2': 'sum',
        'abatement_tco2': 'sum',
        'capex_usd': 'sum',
        'elec_demand_mwh': 'sum',
        'h2_demand_t': 'sum'
    }).reset_index()

    summary.columns = ['Region', 'Facilities', 'Capacity (t/y)', 'BAU (tCO2)',
                      'Emissions (tCO2)', 'Abatement (tCO2)', 'CAPEX ($)',
                      'Elec (MWh)', 'H2 (t)']

    # Format for display
    summary['Capacity (kt)'] = (summary['Capacity (t/y)'] / 1e3).round(0)
    summary['BAU (Mt)'] = (summary['BAU (tCO2)'] / 1e6).round(2)
    summary['Abatement (Mt)'] = (summary['Abatement (tCO2)'] / 1e6).round(2)
    summary['CAPEX ($B)'] = (summary['CAPEX ($)'] / 1e9).round(2)
    summary['Elec (TWh)'] = (summary['Elec (MWh)'] / 1e6).round(2)
    summary['H2 (kt)'] = (summary['H2 (t)'] / 1e3).round(1)
    summary['Reduction (%)'] = ((summary['Abatement (tCO2)'] / summary['BAU (tCO2)']) * 100).round(1)

    display_cols = ['Region', 'Facilities', 'Capacity (kt)', 'BAU (Mt)',
                   'Abatement (Mt)', 'Reduction (%)', 'CAPEX ($B)', 'Elec (TWh)', 'H2 (kt)']

    st.dataframe(summary[display_cols], hide_index=True, use_container_width=True)


# =============================================================================
# PAGE: FACILITY DETAILS
# =============================================================================
elif page == "Facility Details":
    st.title("🏢 Facility Details")
    st.markdown(f"**Scenario:** {SCENARIO_NAMES.get(selected_scenario, selected_scenario)} | **Year:** {selected_year}")

    # Filter data
    df_year = df[(df['scenario'] == selected_scenario) & (df['year'] == selected_year)]

    st.markdown("---")

    # Additional filters
    col1, col2, col3 = st.columns(3)

    with col1:
        regions = ['All'] + sorted(df_year['region'].unique().tolist())
        filter_region = st.selectbox("Region", regions)

    with col2:
        techs = ['All'] + sorted(df_year['technology'].unique().tolist())
        filter_tech = st.selectbox("Technology", techs)

    with col3:
        search = st.text_input("Search (company/product)")

    # Apply filters
    df_filtered = df_year.copy()
    if filter_region != 'All':
        df_filtered = df_filtered[df_filtered['region'] == filter_region]
    if filter_tech != 'All':
        df_filtered = df_filtered[df_filtered['technology'] == filter_tech]
    if search:
        mask = (
            df_filtered['company'].str.contains(search, case=False, na=False) |
            df_filtered['product'].str.contains(search, case=False, na=False)
        )
        df_filtered = df_filtered[mask]

    st.markdown("---")

    # Summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Facilities", len(df_filtered))
    col2.metric("Deployed", len(df_filtered[df_filtered['tech_deployed'] == 1]))
    col3.metric("Abatement", f"{df_filtered['abatement_tco2'].sum()/1e6:.2f} Mt")
    col4.metric("CAPEX", f"${df_filtered['capex_usd'].sum()/1e9:.2f}B")

    st.markdown("---")

    # Facility table
    display_df = df_filtered[[
        'facility_id', 'company', 'product', 'process', 'region', 'technology',
        'capacity_tpy', 'bau_emissions_tco2', 'abatement_tco2',
        'capex_usd', 'mac_usd_per_tco2', 'tech_deployed'
    ]].copy()

    display_df.columns = ['ID', 'Company', 'Product', 'Process', 'Region', 'Technology',
                         'Capacity (t/y)', 'BAU (tCO2)', 'Abatement (tCO2)',
                         'CAPEX ($)', 'MAC ($/tCO2)', 'Deployed']

    # Sort by abatement
    display_df = display_df.sort_values('Abatement (tCO2)', ascending=False)

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            'Capacity (t/y)': st.column_config.NumberColumn(format="%,.0f"),
            'BAU (tCO2)': st.column_config.NumberColumn(format="%,.0f"),
            'Abatement (tCO2)': st.column_config.NumberColumn(format="%,.0f"),
            'CAPEX ($)': st.column_config.NumberColumn(format="$%,.0f"),
            'MAC ($/tCO2)': st.column_config.NumberColumn(format="$%,.0f"),
            'Deployed': st.column_config.CheckboxColumn()
        }
    )

    st.caption(f"Showing {len(display_df)} facilities")


# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.caption("Korea Petrochemical Net Zero Analysis | NO CCS/CCUS")
