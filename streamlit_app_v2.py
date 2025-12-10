"""
Korea Petrochemical Net Zero Dashboard v2
=========================================
Comprehensive dashboard with 6 pages:
1. Scenario Comparison - Summary cards, bar charts, MACC curve
2. Assumptions - All input data and parameters
3. Technology Details - Parameters, MACC evolution by year
4. Regional Transition Outlook - Regional metrics, H2 demand, regional MACCs
5. Facility-Level Results - Summaries and searchable table
6. Energy Infrastructure - Electricity and H2 demand by scenario
7. Documentation - Full methodology and assumptions documentation

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
DOCS_DIR = BASE_DIR / "docs"
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
def load_all_assumptions():
    """Load all input assumptions from data files"""
    assumptions = {}

    # Technology parameters (via symlink: technology_parameters.csv -> inputs/technology_capex.csv)
    try:
        assumptions['tech'] = pd.read_csv(DATA_DIR / "technology_parameters.csv")
    except:
        try:
            assumptions['tech'] = pd.read_csv(DATA_DIR / "inputs" / "technology_capex.csv")
        except:
            assumptions['tech'] = None

    # H2 Price trajectory
    try:
        assumptions['h2'] = pd.read_csv(DATA_DIR / "h2_price_trajectory.csv")
    except:
        try:
            assumptions['h2'] = pd.read_csv(DATA_DIR / "price_trajectories" / "h2_price_trajectory.csv")
        except:
            assumptions['h2'] = None

    # RE Price trajectory
    try:
        assumptions['re'] = pd.read_csv(DATA_DIR / "re_price_trajectory.csv")
    except:
        try:
            assumptions['re'] = pd.read_csv(DATA_DIR / "price_trajectories" / "re_price_trajectory.csv")
        except:
            assumptions['re'] = None

    # Grid emission trajectory
    try:
        assumptions['grid'] = pd.read_csv(DATA_DIR / "grid_emission_trajectory.csv")
    except:
        try:
            assumptions['grid'] = pd.read_csv(DATA_DIR / "price_trajectories" / "grid_emission_trajectory.csv")
        except:
            assumptions['grid'] = None

    # Emission factors
    try:
        assumptions['emission_factors'] = pd.read_csv(DATA_DIR / "emission_factors.csv")
    except:
        try:
            assumptions['emission_factors'] = pd.read_csv(DATA_DIR / "inputs" / "emission_factors.csv")
        except:
            assumptions['emission_factors'] = None

    # Fuel prices
    try:
        assumptions['fuel_prices'] = pd.read_csv(DATA_DIR / "fuel_price_trajectory.csv")
    except:
        try:
            assumptions['fuel_prices'] = pd.read_csv(DATA_DIR / "price_trajectories" / "fuel_price_trajectory.csv")
        except:
            assumptions['fuel_prices'] = None

    # Operating rates (Shaheen)
    try:
        assumptions['op_rate_shaheen'] = pd.read_csv(DATA_DIR / "demand_growth_trajectory_shaheen.csv")
    except:
        try:
            assumptions['op_rate_shaheen'] = pd.read_csv(DATA_DIR / "inputs" / "operating_rate_shaheen.csv")
        except:
            assumptions['op_rate_shaheen'] = None

    # Operating rates (Restructure 25%)
    try:
        assumptions['op_rate_restructure_25'] = pd.read_csv(DATA_DIR / "demand_growth_trajectory_restructure_25pct.csv")
    except:
        try:
            assumptions['op_rate_restructure_25'] = pd.read_csv(DATA_DIR / "inputs" / "operating_rate_restructure_25pct.csv")
        except:
            assumptions['op_rate_restructure_25'] = None

    # Operating rates (Restructure 40%)
    try:
        assumptions['op_rate_restructure_40'] = pd.read_csv(DATA_DIR / "demand_growth_trajectory_restructure_40pct.csv")
    except:
        try:
            assumptions['op_rate_restructure_40'] = pd.read_csv(DATA_DIR / "inputs" / "operating_rate_restructure_40pct.csv")
        except:
            assumptions['op_rate_restructure_40'] = None

    # Energy intensities (summary)
    try:
        ei_df = pd.read_csv(DATA_DIR / "energy_intensities.csv")
        assumptions['energy_intensities'] = ei_df
    except:
        try:
            ei_df = pd.read_csv(DATA_DIR / "inputs" / "energy_intensities.csv")
            assumptions['energy_intensities'] = ei_df
        except:
            assumptions['energy_intensities'] = None

    return assumptions


@st.cache_data
def load_documentation():
    """Load all documentation markdown files"""
    docs = {}
    doc_files = {
        'Assumptions & Methodology': 'ASSUMPTIONS_AND_METHODOLOGY.md',
        'Model Documentation': 'MODEL_DOCUMENTATION.md',
        'Model Flow': 'MODEL_FLOW.md',
        'Final Project Report': 'FINAL_PROJECT_REPORT.md',
        'Energy Intensity Sources': 'ENERGY_INTENSITY_SOURCES.md',
    }

    for name, filename in doc_files.items():
        filepath = DOCS_DIR / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    docs[name] = f.read()
            except Exception as e:
                docs[name] = f"Error loading {filename}: {str(e)}"
        else:
            docs[name] = f"File not found: {filename}"

    return docs


# Load data
df = load_data()
assumptions = load_all_assumptions()

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
    ["1. Scenario Comparison", "2. Assumptions", "3. Technology Details",
     "4. Regional Outlook", "5. Facility Results", "6. Energy Infrastructure",
     "7. Documentation"]
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

            # Create proper MACC bars (horizontal position based on cumulative abatement)
            x_start = 0
            for _, row in df_macc.iterrows():
                width = row['abatement_tco2'] / 1e6
                tech = row['technology']
                fig.add_trace(go.Bar(
                    x=[width],
                    y=[row['mac_usd_per_tco2']],
                    width=0.8,
                    name=tech,
                    marker_color=TECH_COLORS.get(tech, '#808080'),
                    showlegend=False,
                    hovertemplate=(
                        f'<b>{row["company"]}</b><br>'
                        f'Product: {row["product"]}<br>'
                        f'Region: {row["region"]}<br>'
                        f'Abatement: {width:.3f} Mt<br>'
                        f'MAC: ${row["mac_usd_per_tco2"]:.0f}/tCO2<extra></extra>'
                    ),
                    base=x_start
                ))
                x_start += width

            # Add legend entries
            for tech in df_macc['technology'].unique():
                fig.add_trace(go.Bar(
                    x=[None], y=[None],
                    name=tech,
                    marker_color=TECH_COLORS.get(tech, '#808080'),
                    showlegend=True
                ))

            fig.update_layout(
                title=f'MACC - {SCENARIO_NAMES.get(scenario, scenario)} ({selected_year})',
                barmode='stack',
                xaxis_title='Cumulative Abatement (MtCO2)',
                yaxis_title='MAC ($/tCO2)',
                height=500,
                legend=dict(orientation='h', y=1.1)
            )
            st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# PAGE 2: ASSUMPTIONS
# =============================================================================
elif page == "2. Assumptions":
    st.title("📋 Model Assumptions")

    st.markdown("""
    This page displays all input data and assumptions used in the model.
    Data sources are documented in `docs/ENERGY_INTENSITY_SOURCES.md`.
    """)

    # Emission Targets
    st.header("1. Emission Reduction Targets")

    target_df = pd.DataFrame([
        {'Year': year, 'Reduction Target (%)': target * 100, 'Note':
         'Baseline' if year == 2025 else
         'Korea Industry NDC' if year == 2035 else
         'Net Zero' if year == 2050 else
         'Interpolated'}
        for year, target in EMISSION_TARGETS.items()
    ])
    st.dataframe(target_df, hide_index=True, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(target_df, x='Year', y='Reduction Target (%)',
                     markers=True, title='Emission Reduction Trajectory')
        fig.add_hline(y=24.5, line_dash="dash", annotation_text="2035 NDC (24.5%)")
        fig.add_hline(y=100, line_dash="dash", annotation_text="Net Zero")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Technology Parameters
    st.header("2. Technology Parameters")

    if assumptions.get('tech') is not None:
        tech_df = assumptions['tech']

        # Display key parameters
        display_cols = ['technology', 'applies_to', 'trl', 'available_year',
                       'capex_2025_musd_per_mtco2', 'capex_2030_musd_per_mtco2',
                       'capex_2040_musd_per_mtco2', 'capex_2050_musd_per_mtco2',
                       'opex_pct_capex', 'lifetime_years']
        display_cols = [c for c in display_cols if c in tech_df.columns]

        st.dataframe(tech_df[display_cols], hide_index=True, use_container_width=True)

        # CAPEX learning curves
        st.subheader("Technology CAPEX Learning Curves")
        capex_data = []
        for _, row in tech_df.iterrows():
            tech_name = row['technology']
            for year in [2025, 2030, 2040, 2050]:
                col_name = f'capex_{year}_musd_per_mtco2'
                if col_name in row and pd.notna(row[col_name]):
                    capex_data.append({
                        'Technology': tech_name,
                        'Year': year,
                        'CAPEX (M$/MtCO2)': row[col_name]
                    })

        if capex_data:
            capex_df = pd.DataFrame(capex_data)
            fig = px.line(capex_df, x='Year', y='CAPEX (M$/MtCO2)', color='Technology',
                         markers=True, title='Technology CAPEX Learning Curves',
                         color_discrete_map=TECH_COLORS)
            st.plotly_chart(fig, use_container_width=True)

        # Additional tech parameters
        st.subheader("Technology-Specific Parameters")
        col1, col2 = st.columns(2)
        with col1:
            if 'cop' in tech_df.columns:
                hp_row = tech_df[tech_df['technology'] == 'Heat_Pump']
                if len(hp_row) > 0:
                    st.metric("Heat Pump COP", f"{hp_row['cop'].iloc[0]}")
            if 'h2_ton_per_ton_ethylene' in tech_df.columns:
                ncc_h2 = tech_df[tech_df['technology'] == 'NCC-H2']
                if len(ncc_h2) > 0 and pd.notna(ncc_h2['h2_ton_per_ton_ethylene'].iloc[0]):
                    st.metric("NCC-H2: H2 Consumption", f"{ncc_h2['h2_ton_per_ton_ethylene'].iloc[0]} t-H2/t-C2H4")
        with col2:
            if 'elec_mwh_per_ton_ethylene' in tech_df.columns:
                ncc_elec = tech_df[tech_df['technology'] == 'NCC-Electricity']
                if len(ncc_elec) > 0 and pd.notna(ncc_elec['elec_mwh_per_ton_ethylene'].iloc[0]):
                    st.metric("NCC-Elec: Electricity", f"{ncc_elec['elec_mwh_per_ton_ethylene'].iloc[0]} MWh/t-C2H4")
    else:
        st.warning("Technology parameters not loaded")

    st.markdown("---")

    # Energy Price Trajectories
    st.header("3. Energy Price Trajectories")

    col1, col2 = st.columns(2)

    with col1:
        # H2 prices
        if assumptions.get('h2') is not None:
            h2_df = assumptions['h2']
            fig = px.line(h2_df, x='year', y='h2_price_usd_per_kg',
                         markers=True, title='Green Hydrogen Price Trajectory')
            fig.update_yaxes(title='H2 Price ($/kg)')
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("H2 Price Data"):
                st.dataframe(h2_df[['year', 'h2_price_usd_per_kg']], hide_index=True)
        else:
            st.warning("H2 price trajectory not loaded")

    with col2:
        # RE prices
        if assumptions.get('re') is not None:
            re_df = assumptions['re']
            fig = px.line(re_df, x='year', y='re_price_usd_per_mwh',
                         markers=True, title='Renewable Electricity Price Trajectory')
            fig.update_yaxes(title='RE Price ($/MWh)')
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("RE Price Data"):
                st.dataframe(re_df[['year', 're_price_usd_per_mwh']], hide_index=True)
        else:
            st.warning("RE price trajectory not loaded")

    st.markdown("---")

    # Grid Emission Factor
    st.header("4. Grid Decarbonization Trajectory")

    if assumptions.get('grid') is not None:
        grid_df = assumptions['grid']

        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(grid_df, x='year', y='grid_ef_tco2_per_mwh',
                         markers=True, title='Korea Grid Emission Factor')
            fig.update_yaxes(title='Grid EF (tCO2/MWh)')
            fig.add_hline(y=0, line_dash="dash", annotation_text="Net Zero Grid")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("""
            **Key Milestones:**
            - 2025: 0.436 tCO2/MWh (current)
            - 2030: 0.349 tCO2/MWh
            - 2040: 0.140 tCO2/MWh
            - 2050: 0.000 tCO2/MWh (Net Zero Grid)

            **Source:** Korea 10th Basic Energy Plan targets
            """)

            with st.expander("Grid EF Data"):
                st.dataframe(grid_df, hide_index=True)
    else:
        st.warning("Grid emission trajectory not loaded")

    st.markdown("---")

    # Emission Factors
    st.header("5. Fuel Emission Factors")

    if assumptions.get('emission_factors') is not None:
        ef_df = assumptions['emission_factors']
        st.dataframe(ef_df, hide_index=True, use_container_width=True)

        # Bar chart
        ef_plot = ef_df[ef_df['tCO2_per_GJ'].notna()].copy()
        if len(ef_plot) > 0:
            fig = px.bar(ef_plot, x='fuel', y='tCO2_per_GJ',
                        title='Emission Factors by Fuel Type')
            fig.update_yaxes(title='Emission Factor (tCO2/GJ)')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Emission factors not loaded")

    st.markdown("---")

    # Operating Rate Trajectories
    st.header("6. Production Scenarios (Operating Rate)")

    op_rate_data = []

    if assumptions.get('op_rate_shaheen') is not None:
        for _, row in assumptions['op_rate_shaheen'].iterrows():
            op_rate_data.append({
                'Year': row['year'],
                'Scenario': 'Shaheen',
                'Capacity Multiplier': row.get('cumulative_capacity_multiplier', 1.0),
                'Operating Rate (%)': row.get('operating_rate_pct', 70)
            })

    if assumptions.get('op_rate_restructure_25') is not None:
        for _, row in assumptions['op_rate_restructure_25'].iterrows():
            op_rate_data.append({
                'Year': row['year'],
                'Scenario': 'Restructure 25%',
                'Capacity Multiplier': row.get('cumulative_capacity_multiplier', 1.0),
                'Operating Rate (%)': row.get('operating_rate_pct', 70)
            })

    if assumptions.get('op_rate_restructure_40') is not None:
        for _, row in assumptions['op_rate_restructure_40'].iterrows():
            op_rate_data.append({
                'Year': row['year'],
                'Scenario': 'Restructure 40%',
                'Capacity Multiplier': row.get('cumulative_capacity_multiplier', 1.0),
                'Operating Rate (%)': row.get('operating_rate_pct', 70)
            })

    if op_rate_data:
        op_df = pd.DataFrame(op_rate_data)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(op_df, x='Year', y='Capacity Multiplier', color='Scenario',
                         markers=True, title='Capacity Multiplier by Scenario')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.line(op_df, x='Year', y='Operating Rate (%)', color='Scenario',
                         markers=True, title='Operating Rate by Scenario')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Operating rate data not loaded")

    st.markdown("---")

    # Energy Intensity Summary
    st.header("7. Energy Intensity Summary")

    if assumptions.get('energy_intensities') is not None:
        ei_df = assumptions['energy_intensities']

        # Summary by process type
        process_summary = ei_df.groupby('process').agg({
            'Naphtha_GJ_per_tonne': 'mean',
            'Electricity_kWh_per_tonne': 'mean',
            'LNG_GJ_per_tonne': 'mean',
            'Fuel_Gas_GJ_per_tonne': 'mean'
        }).reset_index()

        st.subheader("Average Energy Intensity by Process")
        st.dataframe(process_summary, hide_index=True, use_container_width=True)

        with st.expander("Full Energy Intensity Data"):
            display_cols = ['product', 'process', 'company', 'location',
                          'Naphtha_GJ_per_tonne', 'Electricity_kWh_per_tonne',
                          'LNG_GJ_per_tonne', 'Fuel_Gas_GJ_per_tonne']
            display_cols = [c for c in display_cols if c in ei_df.columns]
            st.dataframe(ei_df[display_cols], hide_index=True, use_container_width=True)
    else:
        st.warning("Energy intensity data not loaded")

    st.markdown("---")
    st.caption("Data sources documented in docs/ENERGY_INTENSITY_SOURCES.md")


# =============================================================================
# PAGE 3: TECHNOLOGY DETAILS
# =============================================================================
elif page == "3. Technology Details":
    st.title("🔧 Technology Details")

    # Technology selector
    available_techs = df['technology'].dropna().unique().tolist()
    available_techs = [t for t in available_techs if t != 'None']
    selected_tech = st.selectbox("Select Technology", available_techs)

    st.markdown("---")

    # Technology parameters from Assumptions
    st.header("Technology Parameters")

    if assumptions.get('tech') is not None:
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
# PAGE 4: REGIONAL OUTLOOK
# =============================================================================
elif page == "4. Regional Outlook":
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

    # Regional MACC Curves (IMPROVED)
    st.header("Regional MACC Curves")

    for region in regions:
        df_r = df_s[(df_s['region'] == region) & (df_s['abatement_tco2'] > 0)].copy()
        df_r = df_r.sort_values('mac_usd_per_tco2')

        if len(df_r) > 0:
            fig = go.Figure()

            # Create proper MACC bars
            x_start = 0
            for _, row in df_r.iterrows():
                width = row['abatement_tco2'] / 1e6
                tech = row['technology']
                fig.add_trace(go.Bar(
                    x=[width],
                    y=[row['mac_usd_per_tco2']],
                    width=0.8,
                    name=tech,
                    marker_color=TECH_COLORS.get(tech, '#808080'),
                    showlegend=False,
                    hovertemplate=(
                        f'<b>{row["company"]}</b><br>'
                        f'Product: {row["product"]}<br>'
                        f'Abatement: {width:.3f} Mt<br>'
                        f'MAC: ${row["mac_usd_per_tco2"]:.0f}/tCO2<extra></extra>'
                    ),
                    base=x_start
                ))
                x_start += width

            # Add legend entries
            for tech in df_r['technology'].unique():
                fig.add_trace(go.Bar(
                    x=[None], y=[None],
                    name=tech,
                    marker_color=TECH_COLORS.get(tech, '#808080'),
                    showlegend=True
                ))

            total_abatement = df_r['abatement_tco2'].sum() / 1e6
            avg_mac = df_r['total_cost_usd'].sum() / df_r['abatement_tco2'].sum() if df_r['abatement_tco2'].sum() > 0 else 0

            fig.update_layout(
                title=f'{region} MACC - Total: {total_abatement:.2f} MtCO2, Avg MAC: ${avg_mac:.0f}/tCO2',
                barmode='stack',
                xaxis_title='Cumulative Abatement (MtCO2)',
                yaxis_title='MAC ($/tCO2)',
                height=400,
                legend=dict(orientation='h', y=1.1)
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Regional MAC by Year (NEW)
    st.header("Regional MAC by Year")

    mac_by_year_data = []
    for year in sorted(df['year'].unique()):
        df_y = df_full[df_full['year'] == year]
        for region in regions:
            df_r = df_y[(df_y['region'] == region) & (df_y['abatement_tco2'] > 0)]
            if len(df_r) > 0:
                total_cost = df_r['total_cost_usd'].sum()
                total_abatement = df_r['abatement_tco2'].sum()
                mac = total_cost / total_abatement if total_abatement > 0 else 0
                mac_by_year_data.append({
                    'Year': year,
                    'Region': region,
                    'MAC ($/tCO2)': mac,
                    'Abatement (MtCO2)': total_abatement / 1e6,
                    'Total Cost ($M)': total_cost / 1e6
                })

    if mac_by_year_data:
        mac_year_df = pd.DataFrame(mac_by_year_data)

        col1, col2 = st.columns(2)

        with col1:
            fig = px.line(mac_year_df, x='Year', y='MAC ($/tCO2)', color='Region',
                         markers=True, title='Average MAC by Region Over Time',
                         color_discrete_map=REGION_COLORS)
            fig.update_yaxes(title='MAC ($/tCO2)')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(mac_year_df, x='Year', y='Abatement (MtCO2)', color='Region',
                        title='Abatement by Region Over Time',
                        color_discrete_map=REGION_COLORS)
            st.plotly_chart(fig, use_container_width=True)

        # MAC table by year and region
        st.subheader("MAC Summary Table ($/tCO2)")
        mac_pivot = mac_year_df.pivot(index='Region', columns='Year', values='MAC ($/tCO2)')
        mac_pivot = mac_pivot.round(0)
        st.dataframe(mac_pivot, use_container_width=True)

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


# =============================================================================
# PAGE 5: FACILITY RESULTS
# =============================================================================
elif page == "5. Facility Results":
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
# PAGE 6: ENERGY INFRASTRUCTURE
# =============================================================================
elif page == "6. Energy Infrastructure":
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
# PAGE 7: DOCUMENTATION
# =============================================================================
elif page == "7. Documentation":
    st.title("📚 Documentation")
    st.markdown("Complete methodology and assumptions documentation for the Korea Petrochemical Net Zero model.")

    # Load documentation
    docs = load_documentation()

    # Document selector
    doc_names = list(docs.keys())
    selected_doc = st.selectbox(
        "Select Document",
        doc_names,
        index=0
    )

    st.markdown("---")

    # Quick navigation info
    with st.expander("📖 Document Overview", expanded=False):
        st.markdown("""
        | Document | Description |
        |----------|-------------|
        | **Assumptions & Methodology** | Complete assumptions, scenario definitions, technology parameters |
        | **Model Documentation** | Technical model summary with price trajectories and LCOH formula |
        | **Model Flow** | Data flow diagram and calculation methodology |
        | **Final Project Report** | Executive summary with key findings and results |
        | **Energy Intensity Sources** | Literature references for energy intensity values |
        """)

    # Display selected document
    if selected_doc in docs:
        st.markdown(docs[selected_doc])
    else:
        st.warning("Document not found.")

    # Download section
    st.markdown("---")
    st.subheader("📥 Download Documentation")

    col1, col2 = st.columns(2)

    with col1:
        if selected_doc in docs:
            st.download_button(
                label=f"Download {selected_doc}",
                data=docs[selected_doc],
                file_name=f"{selected_doc.replace(' ', '_').replace('&', 'and')}.md",
                mime="text/markdown"
            )

    with col2:
        # Download all as combined file
        all_docs_combined = "\n\n---\n\n".join([
            f"# {name}\n\n{content}" for name, content in docs.items()
        ])
        st.download_button(
            label="Download All Documentation",
            data=all_docs_combined,
            file_name="Korea_Petrochemical_NetZero_Documentation.md",
            mime="text/markdown"
        )


# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.caption("Korea Petrochemical Net Zero Analysis | Targets: 24.5% (2035), 100% (2050) | NO CCS/CCUS")
