"""
Korea Petrochemical Net Zero Dashboard
=======================================
Final verified version with regional and annual analysis
Full Technology Coverage: NCC-H2/Elec, RDH, Heat Pump, RE-PPA
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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data Paths - Absolute paths
BASE_DIR = Path("/Users/jinsupark/jinsu-coding/petrochemical_macc_2025")
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"

# ============================================================================
# Data Loading
# ============================================================================
@st.cache_data(ttl=300)
def load_data():
    """Load all necessary data"""
    data = {}

    # Core data files
    try:
        data['facilities'] = pd.read_csv(DATA_DIR / "facility_database_with_regions.csv")
        data['tech_params'] = pd.read_csv(DATA_DIR / "technology_parameters.csv")
        data['h2_prices'] = pd.read_csv(DATA_DIR / "h2_price_trajectory.csv")
        data['re_prices'] = pd.read_csv(DATA_DIR / "re_price_trajectory.csv")
        data['grid_ef'] = pd.read_csv(DATA_DIR / "grid_emission_trajectory.csv")
    except Exception as e:
        st.error(f"Error loading core data: {e}")
        return None

    # Scenario summary
    scenario_summary_path = OUTPUTS_DIR / "scenario_summary_final.csv"
    if scenario_summary_path.exists():
        data['scenarios'] = pd.read_csv(scenario_summary_path)
    else:
        data['scenarios'] = None

    # Load each scenario's data
    data['scenario_data'] = {}
    scenario_ids = [
        'shaheen_ncc_h2', 'shaheen_ncc_electricity',
        'restructure_25pct_ncc_h2', 'restructure_25pct_ncc_electricity',
        'restructure_40pct_ncc_h2', 'restructure_40pct_ncc_electricity'
    ]

    for scenario_id in scenario_ids:
        scenario_dir = OUTPUTS_DIR / f'scenario_{scenario_id}'
        if scenario_dir.exists():
            scenario_data = {}

            files = {
                'facilities': 'scenario_facilities.csv',
                'emissions': 'facility_emissions_2050.csv',
                'deployment': 'deployment_trajectory.csv',
                'regional': 'regional_summary_2050.csv',
                'annual': 'regional_annual_analysis.csv'
            }

            for key, filename in files.items():
                path = scenario_dir / filename
                if path.exists():
                    scenario_data[key] = pd.read_csv(path)

            data['scenario_data'][scenario_id] = scenario_data

    return data

# Load data
data = load_data()

# Scenario display names
SCENARIO_KOREAN = {
    'shaheen_ncc_h2': 'Shaheen (성장) + NCC-H2',
    'shaheen_ncc_electricity': 'Shaheen (성장) + NCC-전기화',
    'restructure_25pct_ncc_h2': '구조조정 25% + NCC-H2',
    'restructure_25pct_ncc_electricity': '구조조정 25% + NCC-전기화',
    'restructure_40pct_ncc_h2': '구조조정 40% + NCC-H2',
    'restructure_40pct_ncc_electricity': '구조조정 40% + NCC-전기화',
}

# ============================================================================
# Sidebar
# ============================================================================
st.sidebar.title("🏭 Net Zero Dashboard")
st.sidebar.markdown("**Korea Petrochemical Industry**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Executive Summary",
     "🔄 Scenario Comparison",
     "🏭 Facility Analysis",
     "📈 Emission Pathways",
     "💰 Cost & Investment",
     "⚡ Energy Requirements",
     "🗺️ Regional Analysis"]
)

st.sidebar.markdown("---")

# Scenario Selector
if page in ["🏭 Facility Analysis", "📈 Emission Pathways", "⚡ Energy Requirements", "🗺️ Regional Analysis"]:
    selected_scenario = st.sidebar.selectbox(
        "Select Scenario",
        list(SCENARIO_KOREAN.keys()),
        format_func=lambda x: SCENARIO_KOREAN[x]
    )
else:
    selected_scenario = None

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(
    "**Technology Coverage:**\n"
    "- NCC-H2/Elec: Naphtha Crackers (85%)\n"
    "- RDH: BTX Plants (80%)\n"
    "- Heat Pump: Low-temp heat\n"
    "- RE-PPA: Grid electricity\n\n"
    "**Key Assumptions:**\n"
    "- 50% CAPEX learning by 2050\n"
    "- Grid EF: 0.436→0.0 tCO2/MWh\n"
    "- H2: $4.58→$2.01/kg (LCOH)\n"
    "- NO CCS/CCUS"
)

# ============================================================================
# Page: Executive Summary
# ============================================================================
if page == "📊 Executive Summary":
    st.title("📊 Executive Summary: Korea Petrochemical Net Zero Pathways")

    if data and data.get('scenarios') is not None:
        scenarios_df = data['scenarios']

        # Key metrics
        st.subheader("Six Scenario Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### Production Pathways")
            st.markdown("""
            - **Shaheen (성장)**: +6 new facilities (S-Oil)
            - **구조조정 25%**: Retire 25% oldest NCC capacity
            - **구조조정 40%**: Retire 40% oldest NCC capacity
            """)

        with col2:
            st.markdown("### NCC Technology")
            st.markdown("""
            - **NCC-H2**: Green hydrogen furnaces
            - **NCC-Electricity**: Electric crackers (eFurnace)
            """)

        with col3:
            st.markdown("### Supporting Technologies")
            st.markdown("""
            - **RDH**: BTX reforming (Coolbrook)
            - **Heat Pump**: Low-temp heat (COP 4.0)
            - **RE-PPA**: 100% renewable grid
            """)

        st.markdown("---")

        # Summary Table
        st.subheader("Scenario Results Summary")

        cols = ['scenario', 'technology', 'n_facilities', 'n_ncc_facilities', 'bau_2050_mt', 'net_2050_mt', 'capex_billion_usd']
        if 'n_btx_facilities' in scenarios_df.columns:
            cols.insert(4, 'n_btx_facilities')

        display_df = scenarios_df[cols].copy()
        col_names = {
            'scenario': 'Production',
            'technology': 'Technology',
            'n_facilities': 'Facilities',
            'n_ncc_facilities': 'NCC',
            'n_btx_facilities': 'BTX',
            'bau_2050_mt': 'BAU 2050 (Mt)',
            'net_2050_mt': 'Net 2050 (Mt)',
            'capex_billion_usd': 'CAPEX ($B)'
        }
        display_df = display_df.rename(columns=col_names)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Emission Reduction")
            fig = go.Figure(data=[
                go.Bar(name='BAU 2050', x=scenarios_df['scenario'] + ' + ' + scenarios_df['technology'],
                       y=scenarios_df['bau_2050_mt'], marker_color='#E74C3C'),
                go.Bar(name='Net 2050', x=scenarios_df['scenario'] + ' + ' + scenarios_df['technology'],
                       y=scenarios_df['net_2050_mt'], marker_color='#27AE60')
            ])
            fig.update_layout(barmode='group', xaxis_tickangle=-45, height=400,
                            title='BAU vs Net Emissions (2050)')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Investment Comparison")
            fig = px.bar(scenarios_df,
                        x=scenarios_df['scenario'] + ' + ' + scenarios_df['technology'],
                        y='capex_billion_usd',
                        color='technology',
                        title='Total CAPEX by Scenario ($B)',
                        color_discrete_map={'NCC-H2': '#3498DB', 'NCC-Electricity': '#E74C3C'})
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)

        # Headline metrics
        st.markdown("---")
        st.subheader("Headline Numbers")

        col1, col2, col3, col4 = st.columns(4)

        min_capex = scenarios_df.loc[scenarios_df['capex_billion_usd'].idxmin()]
        max_capex = scenarios_df.loc[scenarios_df['capex_billion_usd'].idxmax()]

        col1.metric("Lowest CAPEX", f"${min_capex['capex_billion_usd']:.1f}B",
                   f"{min_capex['scenario']}")
        col2.metric("Highest CAPEX", f"${max_capex['capex_billion_usd']:.1f}B",
                   f"{max_capex['scenario']}")
        col3.metric("All Scenarios", "NET ZERO", "0.0 Mt by 2050")
        col4.metric("Technologies", "4 Types", "NO CCS/CCUS")

    else:
        st.error("Scenario data not loaded. Please run `python run_scenarios_final.py` first.")

# ============================================================================
# Page: Scenario Comparison
# ============================================================================
elif page == "🔄 Scenario Comparison":
    st.title("🔄 Detailed Scenario Comparison")

    if data and data.get('scenarios') is not None:
        scenarios_df = data['scenarios']

        # Abatement breakdown
        st.subheader("Abatement by Technology (2050)")

        abatement_data = []
        for _, row in scenarios_df.iterrows():
            label = f"{row['scenario']}\n{row['technology']}"
            abatement_data.append({'Scenario': label, 'Technology': 'NCC', 'Abatement': row['ncc_abatement_mt']})
            if 'rdh_abatement_mt' in row:
                abatement_data.append({'Scenario': label, 'Technology': 'RDH', 'Abatement': row['rdh_abatement_mt']})
            abatement_data.append({'Scenario': label, 'Technology': 'Heat Pump', 'Abatement': row['heat_pump_mt']})
            abatement_data.append({'Scenario': label, 'Technology': 'RE-PPA', 'Abatement': row['re_ppa_mt']})

        abatement_df = pd.DataFrame(abatement_data)
        fig = px.bar(abatement_df, x='Scenario', y='Abatement', color='Technology',
                    title='Abatement by Technology (Mt CO2)',
                    color_discrete_map={'NCC': '#3498DB', 'RDH': '#9B59B6',
                                       'Heat Pump': '#E67E22', 'RE-PPA': '#27AE60'})
        fig.update_layout(barmode='stack', xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Energy comparison
        st.subheader("Energy Requirements (2050)")

        col1, col2 = st.columns(2)

        with col1:
            h2_col = 'h2_demand_kt' if 'h2_demand_kt' in scenarios_df.columns else 'h2_kt'
            fig = px.bar(scenarios_df,
                        x=scenarios_df['scenario'] + ' + ' + scenarios_df['technology'],
                        y=h2_col,
                        title='Green H2 Demand (kt)',
                        color='technology')
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(scenarios_df,
                        x=scenarios_df['scenario'] + ' + ' + scenarios_df['technology'],
                        y='electricity_twh',
                        title='Electricity Demand (TWh)',
                        color='technology')
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Page: Emission Pathways
# ============================================================================
elif page == "📈 Emission Pathways":
    st.title("📈 Emission Pathways")

    if selected_scenario and data and selected_scenario in data['scenario_data']:
        scenario_data = data['scenario_data'][selected_scenario]

        st.subheader(f"Scenario: {SCENARIO_KOREAN[selected_scenario]}")

        if 'deployment' in scenario_data:
            deploy_df = scenario_data['deployment']

            # Emission trajectory
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=deploy_df['year'], y=deploy_df['bau_mt'],
                                    mode='lines', name='BAU', line=dict(color='red', width=2)))
            fig.add_trace(go.Scatter(x=deploy_df['year'], y=deploy_df['actual_emissions_mt'],
                                    mode='lines+markers', name='With Technology',
                                    line=dict(color='green', width=2)))
            fig.update_layout(title='Emission Pathway (2025-2050)',
                            xaxis_title='Year', yaxis_title='Mt CO2',
                            height=500)
            st.plotly_chart(fig, use_container_width=True)

            # Technology deployment
            st.subheader("Technology Deployment Timeline")

            tech_cols = [col for col in deploy_df.columns if 'deployed' in col and col != 'deployed_abatement_mt']
            if tech_cols:
                fig = go.Figure()
                colors = {'ncc_deployed_mt': '#3498DB', 'rdh_deployed_mt': '#9B59B6',
                         'heat_pump_deployed_mt': '#E67E22', 're_ppa_deployed_mt': '#27AE60'}
                names = {'ncc_deployed_mt': 'NCC', 'rdh_deployed_mt': 'RDH',
                        'heat_pump_deployed_mt': 'Heat Pump', 're_ppa_deployed_mt': 'RE-PPA'}
                for col in tech_cols:
                    fig.add_trace(go.Scatter(x=deploy_df['year'], y=deploy_df[col],
                                           mode='lines', name=names.get(col, col),
                                           line=dict(color=colors.get(col, 'gray'))))
                fig.update_layout(title='Cumulative Abatement by Technology (Mt CO2)',
                                xaxis_title='Year', yaxis_title='Mt CO2',
                                height=400)
                st.plotly_chart(fig, use_container_width=True)

        # Regional emissions
        if 'annual' in scenario_data:
            st.subheader("Regional Emission Pathways")
            annual_df = scenario_data['annual']

            regional_emissions = annual_df.groupby(['year', 'region']).agg({
                'bau_emissions_kt': 'sum',
                'actual_emissions_kt': 'sum'
            }).reset_index()

            fig = px.line(regional_emissions, x='year', y='actual_emissions_kt', color='region',
                         title='Net Emissions by Region (kt CO2)')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Page: Cost & Investment
# ============================================================================
elif page == "💰 Cost & Investment":
    st.title("💰 Cost & Investment Analysis")

    if data and data.get('scenarios') is not None:
        scenarios_df = data['scenarios']

        # CAPEX comparison
        st.subheader("Total CAPEX Comparison")

        fig = px.bar(scenarios_df,
                    x=scenarios_df['scenario'] + ' + ' + scenarios_df['technology'],
                    y='capex_billion_usd',
                    color='technology',
                    title='Total CAPEX by Scenario ($B)',
                    text='capex_billion_usd')
        fig.update_traces(texttemplate='$%{text:.1f}B', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)

        # CAPEX breakdown
        st.subheader("CAPEX Breakdown by Technology")
        st.markdown("*Based on 2040 deployment year with 50% learning curve*")

        # Calculate CAPEX breakdown
        capex_data = []
        for _, row in scenarios_df.iterrows():
            label = f"{row['scenario']} + {row['technology']}"
            tech = row['technology']

            # CAPEX per technology (using 2040 costs)
            ncc_cost = {'NCC-H2': 1105, 'NCC-Electricity': 975}[tech]
            rdh_cost = 585
            hp_cost = 520

            capex_data.append({'Scenario': label, 'Technology': tech,
                             'CAPEX': row['ncc_abatement_mt'] * ncc_cost / 1000})
            capex_data.append({'Scenario': label, 'Technology': 'RDH',
                             'CAPEX': row.get('rdh_abatement_mt', 0) * rdh_cost / 1000})
            capex_data.append({'Scenario': label, 'Technology': 'Heat Pump',
                             'CAPEX': row['heat_pump_mt'] * hp_cost / 1000})

        capex_breakdown = pd.DataFrame(capex_data)
        fig = px.bar(capex_breakdown, x='Scenario', y='CAPEX', color='Technology',
                    title='CAPEX Breakdown ($B)',
                    barmode='stack')
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Cost per tonne abated
        st.subheader("Cost Efficiency")
        scenarios_df['cost_per_tonne'] = scenarios_df['capex_billion_usd'] * 1000 / scenarios_df['bau_2050_mt']

        fig = px.bar(scenarios_df,
                    x=scenarios_df['scenario'] + ' + ' + scenarios_df['technology'],
                    y='cost_per_tonne',
                    color='technology',
                    title='CAPEX per tonne CO2 Abated ($/tCO2)')
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Page: Energy Requirements
# ============================================================================
elif page == "⚡ Energy Requirements":
    st.title("⚡ Energy Requirements")

    if selected_scenario and data and selected_scenario in data['scenario_data']:
        scenario_data = data['scenario_data'][selected_scenario]
        scenarios_df = data['scenarios']
        scenario_row = scenarios_df[scenarios_df['scenario_id'] == selected_scenario].iloc[0]

        st.subheader(f"Scenario: {SCENARIO_KOREAN[selected_scenario]}")

        col1, col2 = st.columns(2)

        h2_col = 'h2_demand_kt' if 'h2_demand_kt' in scenario_row else 'h2_kt'

        with col1:
            st.metric("Green H2 Demand (2050)", f"{scenario_row.get(h2_col, 0):,.0f} kt")
            st.metric("Electricity Demand (2050)", f"{scenario_row['electricity_twh']:.2f} TWh")

        with col2:
            st.metric("Grid EF 2050", "0.0 tCO2/MWh")
            st.metric("RE-PPA Coverage", "100%")

        # Energy trajectory
        if 'deployment' in scenario_data:
            deploy_df = scenario_data['deployment']

            if 'elec_demand_mwh' in deploy_df.columns:
                deploy_df['elec_twh'] = deploy_df['elec_demand_mwh'] / 1e6
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=deploy_df['year'], y=deploy_df['elec_twh'],
                                        mode='lines+markers', name='Electricity (TWh)'))
                fig.update_layout(title='Annual Electricity Demand', height=400)
                st.plotly_chart(fig, use_container_width=True)

        # Regional energy breakdown
        if 'annual' in scenario_data:
            st.subheader("Regional Energy Demand (2050)")
            annual_df = scenario_data['annual']
            year_2050 = annual_df[annual_df['year'] == 2050]

            if len(year_2050) > 0:
                regional_energy = year_2050.groupby('region')['elec_demand_mwh'].sum() / 1e6
                fig = px.pie(values=regional_energy.values, names=regional_energy.index,
                            title='Electricity Demand by Region (TWh)')
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Page: Regional Analysis
# ============================================================================
elif page == "🗺️ Regional Analysis":
    st.title("🗺️ Regional Analysis")

    if selected_scenario and data and selected_scenario in data['scenario_data']:
        scenario_data = data['scenario_data'][selected_scenario]

        st.subheader(f"Scenario: {SCENARIO_KOREAN[selected_scenario]}")

        if 'regional' in scenario_data:
            regional_df = scenario_data['regional']

            # Regional summary table
            st.subheader("Regional Summary (2050)")
            st.dataframe(regional_df, use_container_width=True, hide_index=True)

            # Regional charts
            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(regional_df, x='region', y='n_facilities',
                            title='Facilities by Region',
                            color='region')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.bar(regional_df, x='region', y='total_emissions_kt',
                            title='BAU Emissions by Region (kt CO2)',
                            color='region')
                st.plotly_chart(fig, use_container_width=True)

        if 'annual' in scenario_data:
            st.subheader("Regional Emission Pathways")
            annual_df = scenario_data['annual']

            regional_yearly = annual_df.groupby(['year', 'region']).agg({
                'bau_emissions_kt': 'sum',
                'actual_emissions_kt': 'sum',
                'elec_demand_mwh': 'sum'
            }).reset_index()

            # Annual Regional Analysis: Required Charts (Cost & Electricity)
            st.subheader("Regional Trends Over Time")
            col1, col2 = st.columns(2)
            
            # The column names in regional_annual_analysis.csv are:
            # location, capex_investment_musd, total_annual_cost_musd, electricity_demand_twh, year, scenario
            # Note: Renaming 'location' to 'region' might be needed depending on previous load mismatch,
            # but standardizing on 'location' as per CSV generation.
            
            # Check column names
            x_col = 'year'
            color_col = 'location' if 'location' in annual_df.columns else 'region'
            
            with col1:
                y_col = 'capex_investment_musd'
                fig = px.bar(annual_df, x=x_col, y=y_col, color=color_col,
                             title='Annual Regional Investment (Million USD)',
                             labels={'capex_investment_musd': 'Investment ($M)'})
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                y_col = 'electricity_demand_twh'
                fig = px.line(annual_df, x=x_col, y=y_col, color=color_col,
                              title='Annual Regional Electricity Demand (TWh)',
                              labels={'electricity_demand_twh': 'Demand (TWh)'})
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown(
    "**Korea Petrochemical Net Zero Pathway Analysis** | "
    "Data verified December 2024 | "
    "Full technology coverage - NO CCS/CCUS"
)
