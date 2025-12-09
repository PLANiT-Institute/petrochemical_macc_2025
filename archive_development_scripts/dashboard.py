"""
Korea Petrochemical Net Zero Dashboard
======================================
Assumptions & Regional Transition Analysis
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
    page_title="Korea Petrochemical Net Zero",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data Paths
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Scenario definitions
SCENARIOS = {
    'shaheen_ncc_h2': {
        'name': 'Shaheen + NCC-H2',
        'name_kr': 'Shaheen (성장) + NCC-H2',
        'production': 'Shaheen (Growth)',
        'technology': 'NCC-H2',
        'dir': 'scenario_shaheen_ncc_h2'
    },
    'shaheen_ncc_electricity': {
        'name': 'Shaheen + NCC-Elec',
        'name_kr': 'Shaheen (성장) + NCC-전기화',
        'production': 'Shaheen (Growth)',
        'technology': 'NCC-Electricity',
        'dir': 'scenario_shaheen_ncc_electricity'
    },
    'restructure_25pct_ncc_h2': {
        'name': 'Restructure 25% + NCC-H2',
        'name_kr': '구조조정 25% + NCC-H2',
        'production': 'Restructure 25%',
        'technology': 'NCC-H2',
        'dir': 'scenario_restructure_25pct_ncc_h2'
    },
    'restructure_25pct_ncc_electricity': {
        'name': 'Restructure 25% + NCC-Elec',
        'name_kr': '구조조정 25% + NCC-전기화',
        'production': 'Restructure 25%',
        'technology': 'NCC-Electricity',
        'dir': 'scenario_restructure_25pct_ncc_electricity'
    },
    'restructure_40pct_ncc_h2': {
        'name': 'Restructure 40% + NCC-H2',
        'name_kr': '구조조정 40% + NCC-H2',
        'production': 'Restructure 40%',
        'technology': 'NCC-H2',
        'dir': 'scenario_restructure_40pct_ncc_h2'
    },
    'restructure_40pct_ncc_electricity': {
        'name': 'Restructure 40% + NCC-Elec',
        'name_kr': '구조조정 40% + NCC-전기화',
        'production': 'Restructure 40%',
        'technology': 'NCC-Electricity',
        'dir': 'scenario_restructure_40pct_ncc_electricity'
    }
}

# ============================================================================
# Data Loading
# ============================================================================
@st.cache_data(ttl=300)
def load_assumptions():
    """Load assumption data"""
    data = {}

    try:
        data['tech_params'] = pd.read_csv(DATA_DIR / "technology_parameters.csv")
        data['h2_prices'] = pd.read_csv(DATA_DIR / "h2_price_trajectory.csv")
        data['re_prices'] = pd.read_csv(DATA_DIR / "re_price_trajectory.csv")
        data['grid_ef'] = pd.read_csv(DATA_DIR / "grid_emission_trajectory.csv")
        data['facilities'] = pd.read_csv(DATA_DIR / "facility_database_with_regions.csv")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

    return data

@st.cache_data(ttl=300)
def load_scenario_data():
    """Load all scenario regional trajectory data"""
    scenario_data = {}

    for scenario_id, info in SCENARIOS.items():
        scenario_dir = OUTPUTS_DIR / info['dir']
        annual_file = scenario_dir / 'annual_regional_trajectory.csv'

        if annual_file.exists():
            df = pd.read_csv(annual_file)
            df['scenario'] = scenario_id
            df['scenario_name'] = info['name']
            scenario_data[scenario_id] = df

    return scenario_data

@st.cache_data(ttl=300)
def load_scenario_summary():
    """Load scenario summary"""
    summary_file = OUTPUTS_DIR / "scenario_summary_final.csv"
    if summary_file.exists():
        return pd.read_csv(summary_file)
    return None

# Load data
assumptions = load_assumptions()
scenario_data = load_scenario_data()
scenario_summary = load_scenario_summary()

# ============================================================================
# Sidebar
# ============================================================================
st.sidebar.title("🏭 Net Zero Dashboard")
st.sidebar.markdown("**Korea Petrochemical Industry**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📋 Assumptions",
     "🔄 Scenario Comparison",
     "🗺️ Regional Transitions",
     "⚡ Energy Demand"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Analysis Period:** 2025-2050\n\n"
    "**Technologies:**\n"
    "- NCC-H2: Green H2 furnaces\n"
    "- NCC-Elec: Electric crackers\n"
    "- Heat Pump: Low-temp heat\n"
    "- RE-PPA: Renewable electricity\n\n"
    "**NO CCS/CCUS**"
)

# ============================================================================
# Page: Assumptions
# ============================================================================
if page == "📋 Assumptions":
    st.title("📋 Key Assumptions")

    if assumptions:
        # Technology Parameters
        st.header("1. Technology Parameters")

        tech_df = assumptions['tech_params']

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("CAPEX Learning Curve ($/tCO2)")

            # Prepare CAPEX data
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
            st.subheader("Technology Specifications")

            display_cols = ['technology', 'applies_to', 'trl', 'available_year',
                           'capex_2025_musd_per_mtco2', 'capex_2050_musd_per_mtco2']
            display_df = tech_df[display_cols].copy()
            display_df.columns = ['Technology', 'Application', 'TRL', 'Available',
                                 'CAPEX 2025', 'CAPEX 2050']
            st.dataframe(display_df, hide_index=True, use_container_width=True)

            st.markdown("""
            **Key Points:**
            - 50% CAPEX reduction by 2050 (learning curve)
            - Heat Pump: COP 4.0, available now
            - NCC technologies: Available from 2030
            - RE-PPA: No direct CAPEX (contract-based)
            """)

        st.markdown("---")

        # Price Trajectories
        st.header("2. Energy Price Trajectories")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Green Hydrogen Price")
            h2_df = assumptions['h2_prices']
            fig = px.line(h2_df, x='year', y='h2_price_usd_per_kg',
                         title='Green H2 LCOH ($/kg)',
                         labels={'h2_price_usd_per_kg': 'Price ($/kg)', 'year': 'Year'})
            fig.add_hline(y=2.0, line_dash="dash", line_color="green",
                         annotation_text="Target: $2/kg")
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"""
            - **2025:** ${h2_df.iloc[0]['h2_price_usd_per_kg']:.2f}/kg
            - **2050:** ${h2_df.iloc[-1]['h2_price_usd_per_kg']:.2f}/kg
            - **Decline:** {(1 - h2_df.iloc[-1]['h2_price_usd_per_kg']/h2_df.iloc[0]['h2_price_usd_per_kg'])*100:.0f}%
            """)

        with col2:
            st.subheader("Renewable Electricity Price")
            re_df = assumptions['re_prices']
            fig = px.line(re_df, x='year', y='re_price_usd_per_mwh',
                         title='RE PPA Price ($/MWh)',
                         labels={'re_price_usd_per_mwh': 'Price ($/MWh)', 'year': 'Year'})
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"""
            - **2025:** ${re_df.iloc[0]['re_price_usd_per_mwh']:.1f}/MWh
            - **2050:** ${re_df.iloc[-1]['re_price_usd_per_mwh']:.1f}/MWh
            - **Decline:** {(1 - re_df.iloc[-1]['re_price_usd_per_mwh']/re_df.iloc[0]['re_price_usd_per_mwh'])*100:.0f}%
            """)

        st.markdown("---")

        # Grid Emission Factor
        st.header("3. Grid Decarbonization")

        col1, col2 = st.columns([2, 1])

        with col1:
            grid_df = assumptions['grid_ef']
            fig = px.area(grid_df, x='year', y='grid_ef_tco2_per_mwh',
                         title='Grid Emission Factor Trajectory',
                         labels={'grid_ef_tco2_per_mwh': 'tCO2/MWh', 'year': 'Year'})
            fig.update_traces(fillcolor='rgba(231, 76, 60, 0.3)', line_color='#E74C3C')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Grid EF Assumptions")
            st.markdown(f"""
            | Year | EF (tCO2/MWh) |
            |------|---------------|
            | 2025 | {grid_df.iloc[0]['grid_ef_tco2_per_mwh']:.3f} |
            | 2030 | {grid_df[grid_df['year']==2030]['grid_ef_tco2_per_mwh'].values[0]:.3f} |
            | 2040 | {grid_df[grid_df['year']==2040]['grid_ef_tco2_per_mwh'].values[0]:.3f} |
            | 2050 | {grid_df.iloc[-1]['grid_ef_tco2_per_mwh']:.3f} |

            **Target:** Net-zero grid by 2050
            """)

        st.markdown("---")

        # Facility Overview
        st.header("4. Facility Coverage")

        fac_df = assumptions['facilities']

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Facilities", len(fac_df))
        with col2:
            st.metric("Total Capacity", f"{fac_df['capacity_kt'].sum():,.0f} kt")
        with col3:
            st.metric("Regions", fac_df['location'].nunique())

        col1, col2 = st.columns(2)

        with col1:
            # By region
            region_summary = fac_df.groupby('location').agg({
                'capacity_kt': 'sum',
                'product': 'count'
            }).reset_index()
            region_summary.columns = ['Region', 'Capacity (kt)', 'Facilities']

            fig = px.pie(region_summary, values='Capacity (kt)', names='Region',
                        title='Capacity by Region')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # By product
            product_summary = fac_df.groupby('product').agg({
                'capacity_kt': 'sum',
                'location': 'count'
            }).reset_index()
            product_summary.columns = ['Product', 'Capacity (kt)', 'Facilities']

            fig = px.bar(product_summary, x='Product', y='Capacity (kt)',
                        title='Capacity by Product', color='Product')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Page: Scenario Comparison
# ============================================================================
elif page == "🔄 Scenario Comparison":
    st.title("🔄 Scenario Comparison")

    if scenario_summary is not None:
        st.header("Six Scenarios Overview")

        # Scenario matrix explanation
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### Production Pathways
            | Pathway | Description |
            |---------|-------------|
            | **Shaheen (Growth)** | +6 new S-Oil facilities |
            | **Restructure 25%** | Retire 25% oldest NCC capacity |
            | **Restructure 40%** | Retire 40% oldest NCC capacity |
            """)

        with col2:
            st.markdown("""
            ### NCC Technology Options
            | Technology | Description |
            |------------|-------------|
            | **NCC-H2** | Green hydrogen furnaces |
            | **NCC-Electricity** | Electric crackers (eFurnace) |
            """)

        st.markdown("---")

        # Summary metrics
        st.header("Scenario Results")

        # Display table
        display_cols = ['scenario', 'technology', 'n_facilities', 'bau_2050_mt',
                       'net_2050_mt', 'capex_billion_usd', 'electricity_twh']
        if 'h2_kt' in scenario_summary.columns:
            display_cols.append('h2_kt')

        display_df = scenario_summary[display_cols].copy()
        display_df.columns = ['Production', 'Technology', 'Facilities', 'BAU 2050 (Mt)',
                             'Net 2050 (Mt)', 'CAPEX ($B)', 'Electricity (TWh)'] + \
                            (['H2 (kt)'] if 'h2_kt' in scenario_summary.columns else [])

        st.dataframe(display_df, hide_index=True, use_container_width=True)

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Total CAPEX by Scenario")
            fig = px.bar(scenario_summary,
                        x='scenario', y='capex_billion_usd',
                        color='technology',
                        barmode='group',
                        title='Investment Required ($B)',
                        color_discrete_map={'NCC-H2': '#3498DB', 'NCC-Electricity': '#E74C3C'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Electricity Demand (2050)")
            fig = px.bar(scenario_summary,
                        x='scenario', y='electricity_twh',
                        color='technology',
                        barmode='group',
                        title='Electricity Requirement (TWh)',
                        color_discrete_map={'NCC-H2': '#3498DB', 'NCC-Electricity': '#E74C3C'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        # Emission comparison
        st.subheader("Emission Reduction")

        fig = go.Figure()
        x_labels = scenario_summary['scenario'] + '<br>' + scenario_summary['technology']

        fig.add_trace(go.Bar(name='BAU 2050', x=x_labels, y=scenario_summary['bau_2050_mt'],
                            marker_color='#E74C3C'))
        fig.add_trace(go.Bar(name='Net 2050', x=x_labels, y=scenario_summary['net_2050_mt'],
                            marker_color='#27AE60'))

        fig.update_layout(barmode='group', title='BAU vs Net Zero Emissions (Mt CO2)',
                         height=450)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Scenario summary not found. Please run the scenario analysis first.")

# ============================================================================
# Page: Regional Transitions
# ============================================================================
elif page == "🗺️ Regional Transitions":
    st.title("🗺️ Regional Transitions")

    if scenario_data:
        # Scenario selector
        selected_scenarios = st.multiselect(
            "Select Scenarios to Compare",
            list(SCENARIOS.keys()),
            default=['shaheen_ncc_h2', 'restructure_40pct_ncc_h2'],
            format_func=lambda x: SCENARIOS[x]['name']
        )

        if selected_scenarios:
            st.markdown("---")

            # Technology Deployment by Region
            st.header("1. Technology Deployment by Region")

            for scenario_id in selected_scenarios:
                if scenario_id in scenario_data:
                    df = scenario_data[scenario_id]

                    st.subheader(f"📊 {SCENARIOS[scenario_id]['name']}")

                    # Aggregate by year and region
                    tech_cols = ['ncc_abatement_kt', 'rdh_abatement_kt', 'hp_abatement_kt', 're_ppa_abatement_kt']
                    available_cols = [c for c in tech_cols if c in df.columns]

                    col1, col2 = st.columns(2)

                    with col1:
                        # Stacked area by technology (total)
                        yearly = df.groupby('year')[available_cols].sum().reset_index()
                        yearly_melted = yearly.melt(id_vars='year', var_name='Technology', value_name='Abatement (kt)')
                        yearly_melted['Technology'] = yearly_melted['Technology'].map({
                            'ncc_abatement_kt': 'NCC',
                            'rdh_abatement_kt': 'RDH',
                            'hp_abatement_kt': 'Heat Pump',
                            're_ppa_abatement_kt': 'RE-PPA'
                        })

                        fig = px.area(yearly_melted, x='year', y='Abatement (kt)', color='Technology',
                                     title='Total Technology Deployment (kt CO2 abated)',
                                     color_discrete_map={'NCC': '#3498DB', 'RDH': '#9B59B6',
                                                        'Heat Pump': '#E67E22', 'RE-PPA': '#27AE60'})
                        fig.update_layout(height=350)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        # By region for 2050
                        df_2050 = df[df['year'] == 2050].copy()
                        if len(df_2050) > 0:
                            regional_2050 = df_2050.groupby('region')[available_cols].sum().reset_index()
                            regional_melted = regional_2050.melt(id_vars='region', var_name='Technology', value_name='Abatement (kt)')
                            regional_melted['Technology'] = regional_melted['Technology'].map({
                                'ncc_abatement_kt': 'NCC',
                                'rdh_abatement_kt': 'RDH',
                                'hp_abatement_kt': 'Heat Pump',
                                're_ppa_abatement_kt': 'RE-PPA'
                            })

                            fig = px.bar(regional_melted, x='region', y='Abatement (kt)', color='Technology',
                                        title='Regional Technology Mix (2050)',
                                        color_discrete_map={'NCC': '#3498DB', 'RDH': '#9B59B6',
                                                           'Heat Pump': '#E67E22', 'RE-PPA': '#27AE60'})
                            fig.update_layout(height=350)
                            st.plotly_chart(fig, use_container_width=True)

                    st.markdown("---")

            # Emission Pathways by Region
            st.header("2. Regional Emission Pathways")

            for scenario_id in selected_scenarios:
                if scenario_id in scenario_data:
                    df = scenario_data[scenario_id]

                    st.subheader(f"📊 {SCENARIOS[scenario_id]['name']}")

                    col1, col2 = st.columns(2)

                    with col1:
                        # BAU vs Actual emissions by region
                        regional_yearly = df.groupby(['year', 'region']).agg({
                            'actual_emissions_kt': 'sum'
                        }).reset_index()

                        fig = px.area(regional_yearly, x='year', y='actual_emissions_kt', color='region',
                                     title='Net Emissions by Region (kt CO2)',
                                     labels={'actual_emissions_kt': 'Emissions (kt)', 'year': 'Year'})
                        fig.update_layout(height=350)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        # Total trajectory
                        total_yearly = df.groupby('year').agg({
                            'bau_emissions_kt': 'sum',
                            'actual_emissions_kt': 'sum'
                        }).reset_index()

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=total_yearly['year'], y=total_yearly['bau_emissions_kt']/1000,
                                                mode='lines', name='BAU', line=dict(color='red', dash='dash')))
                        fig.add_trace(go.Scatter(x=total_yearly['year'], y=total_yearly['actual_emissions_kt']/1000,
                                                mode='lines', name='With Technology', line=dict(color='green')))
                        fig.update_layout(title='Total Emission Pathway (Mt CO2)',
                                         xaxis_title='Year', yaxis_title='Mt CO2', height=350)
                        st.plotly_chart(fig, use_container_width=True)

                    st.markdown("---")
    else:
        st.warning("No scenario data found. Please run the scenario analysis first.")

# ============================================================================
# Page: Energy Demand
# ============================================================================
elif page == "⚡ Energy Demand":
    st.title("⚡ Energy Demand Analysis")

    if scenario_data:
        # Scenario selector
        selected_scenarios = st.multiselect(
            "Select Scenarios to Compare",
            list(SCENARIOS.keys()),
            default=['shaheen_ncc_h2', 'shaheen_ncc_electricity'],
            format_func=lambda x: SCENARIOS[x]['name']
        )

        if selected_scenarios:
            st.markdown("---")

            # Electricity Demand
            st.header("1. Electricity Demand by Region")

            for scenario_id in selected_scenarios:
                if scenario_id in scenario_data:
                    df = scenario_data[scenario_id]

                    st.subheader(f"⚡ {SCENARIOS[scenario_id]['name']}")

                    col1, col2 = st.columns(2)

                    with col1:
                        # Total electricity trajectory
                        yearly_elec = df.groupby('year')['elec_demand_mwh'].sum().reset_index()
                        yearly_elec['elec_twh'] = yearly_elec['elec_demand_mwh'] / 1e6

                        fig = px.area(yearly_elec, x='year', y='elec_twh',
                                     title='Total Electricity Demand (TWh)',
                                     labels={'elec_twh': 'TWh', 'year': 'Year'})
                        fig.update_traces(fillcolor='rgba(52, 152, 219, 0.3)', line_color='#3498DB')
                        fig.update_layout(height=350)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        # By region
                        regional_elec = df.groupby(['year', 'region'])['elec_demand_mwh'].sum().reset_index()
                        regional_elec['elec_twh'] = regional_elec['elec_demand_mwh'] / 1e6

                        fig = px.line(regional_elec, x='year', y='elec_twh', color='region',
                                     title='Electricity Demand by Region (TWh)',
                                     labels={'elec_twh': 'TWh', 'year': 'Year'})
                        fig.update_layout(height=350)
                        st.plotly_chart(fig, use_container_width=True)

                    # 2050 breakdown
                    df_2050 = df[df['year'] == 2050]
                    if len(df_2050) > 0:
                        regional_2050 = df_2050.groupby('region')['elec_demand_mwh'].sum() / 1e6

                        col1, col2, col3, col4 = st.columns(4)
                        regions = regional_2050.index.tolist()
                        cols = [col1, col2, col3, col4]

                        for i, region in enumerate(regions[:4]):
                            with cols[i]:
                                st.metric(f"{region}", f"{regional_2050[region]:.2f} TWh")

                    st.markdown("---")

            # Comparison across scenarios
            st.header("2. Scenario Comparison (2050)")

            comparison_data = []
            for scenario_id in selected_scenarios:
                if scenario_id in scenario_data:
                    df = scenario_data[scenario_id]
                    df_2050 = df[df['year'] == 2050]

                    for region in df_2050['region'].unique():
                        region_data = df_2050[df_2050['region'] == region]
                        comparison_data.append({
                            'Scenario': SCENARIOS[scenario_id]['name'],
                            'Region': region,
                            'Electricity (TWh)': region_data['elec_demand_mwh'].sum() / 1e6,
                            'Emissions (kt)': region_data['actual_emissions_kt'].sum()
                        })

            if comparison_data:
                comparison_df = pd.DataFrame(comparison_data)

                col1, col2 = st.columns(2)

                with col1:
                    fig = px.bar(comparison_df, x='Region', y='Electricity (TWh)',
                                color='Scenario', barmode='group',
                                title='Regional Electricity Demand Comparison (2050)')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    fig = px.bar(comparison_df, x='Region', y='Emissions (kt)',
                                color='Scenario', barmode='group',
                                title='Regional Net Emissions Comparison (2050)')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No scenario data found. Please run the scenario analysis first.")

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown(
    "**Korea Petrochemical Net Zero Pathway Analysis** | "
    "Data verified December 2024 | "
    "Full technology coverage - NO CCS/CCUS"
)
