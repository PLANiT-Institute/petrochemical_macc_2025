"""
Korean Petrochemical Net Zero Dashboard
Complete 6-Scenario Analysis with Facility-Level Transitions
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

# Data Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"

# ============================================================================
# Data Loading
# ============================================================================
@st.cache_data
def load_data():
    """Load all necessary data including 6 scenarios"""
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
        st.warning("Scenario summary not found. Run run_scenarios_complete.py first.")
        data['scenarios'] = None

    # Load each scenario's facility data
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

            fac_path = scenario_dir / 'scenario_facilities.csv'
            if fac_path.exists():
                scenario_data['facilities'] = pd.read_csv(fac_path)

            emissions_path = scenario_dir / 'facility_emissions_2050.csv'
            if emissions_path.exists():
                scenario_data['emissions'] = pd.read_csv(emissions_path)

            deploy_path = scenario_dir / 'deployment_trajectory.csv'
            if deploy_path.exists():
                scenario_data['deployment'] = pd.read_csv(deploy_path)

            data['scenario_data'][scenario_id] = scenario_data

    return data

data = load_data()

# Scenario display names
SCENARIO_NAMES = {
    'shaheen_ncc_h2': 'Shaheen (Growth) + NCC-H2',
    'shaheen_ncc_electricity': 'Shaheen (Growth) + NCC-Electricity',
    'restructure_25pct_ncc_h2': 'Restructure 25% + NCC-H2',
    'restructure_25pct_ncc_electricity': 'Restructure 25% + NCC-Electricity',
    'restructure_40pct_ncc_h2': 'Restructure 40% + NCC-H2',
    'restructure_40pct_ncc_electricity': 'Restructure 40% + NCC-Electricity',
}

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
     "🏭 Facility Transitions",
     "📈 Emission Pathways",
     "🛠️ Technology & Learning Curves",
     "💰 Cost & Investment",
     "⚡ Energy Requirements",
     "🗺️ Regional Analysis"]
)

st.sidebar.markdown("---")

# Scenario Selector (for detailed views)
if page in ["🏭 Facility Transitions", "📈 Emission Pathways", "⚡ Energy Requirements"]:
    selected_scenario = st.sidebar.selectbox(
        "Select Scenario",
        list(SCENARIO_NAMES.keys()),
        format_func=lambda x: SCENARIO_KOREAN[x]
    )
else:
    selected_scenario = None

st.sidebar.markdown("---")
st.sidebar.info(
    "**Data Sources:**\n"
    "- PLANiT Institute Analysis\n"
    "- IRENA, IEA WEO 2024\n"
    "- KPIA Industry Data\n\n"
    "**Key Assumptions:**\n"
    "- 50% CAPEX decline by 2050\n"
    "- LCOH-based H2 pricing\n"
    "- Grid decarbonization path"
)

# ============================================================================
# Page: Executive Summary
# ============================================================================
if page == "📊 Executive Summary":
    st.title("📊 Executive Summary: Korea Petrochemical Net Zero Pathways")

    if data and data.get('scenarios') is not None:
        scenarios_df = data['scenarios']

        # Key metrics comparison
        st.subheader("Six Scenario Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### Production Pathways")
            st.markdown("""
            - **Shaheen (성장)**: S-Oil expansion, +6 new facilities
            - **구조조정 25%**: Retire oldest 25% NCC capacity
            - **구조조정 40%**: Retire oldest 40% NCC capacity
            """)

        with col2:
            st.markdown("### Technology Pathways")
            st.markdown("""
            - **NCC-H2**: Green hydrogen for crackers
            - **NCC-Electricity**: Direct electrification
            """)

        with col3:
            st.markdown("### Common Technologies")
            st.markdown("""
            - Heat Pump for low-temp heat
            - RE-PPA for grid emissions
            - 50% learning curve (all tech)
            """)

        st.markdown("---")

        # Summary Table
        st.subheader("Scenario Results Summary")

        summary_display = scenarios_df[['scenario', 'technology', 'n_facilities', 'n_ncc_facilities',
                                        'ncc_capacity_kt', 'bau_2050_mt', 'net_2050_mt', 'capex_billion_usd']].copy()
        summary_display.columns = ['Production', 'Technology', 'Total Facilities', 'NCC Facilities',
                                   'NCC Capacity (kt)', 'BAU 2050 (Mt)', 'Net 2050 (Mt)', 'CAPEX ($B)']

        # Format numbers
        summary_display['NCC Capacity (kt)'] = summary_display['NCC Capacity (kt)'].apply(lambda x: f"{x:,.0f}")
        summary_display['BAU 2050 (Mt)'] = summary_display['BAU 2050 (Mt)'].apply(lambda x: f"{x:.1f}")
        summary_display['Net 2050 (Mt)'] = summary_display['Net 2050 (Mt)'].apply(lambda x: f"{x:.1f}")
        summary_display['CAPEX ($B)'] = summary_display['CAPEX ($B)'].apply(lambda x: f"${x:.1f}")

        st.dataframe(summary_display, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Key Findings
        st.subheader("Key Findings")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Emission Reduction")

            # BAU vs Net comparison chart
            fig = go.Figure()

            for idx, row in scenarios_df.iterrows():
                scenario_label = f"{row['scenario']}\n{row['technology']}"
                fig.add_trace(go.Bar(
                    name=scenario_label,
                    x=[scenario_label],
                    y=[row['bau_2050_mt']],
                    marker_color='lightcoral',
                    showlegend=False
                ))
                fig.add_trace(go.Bar(
                    name=scenario_label,
                    x=[scenario_label],
                    y=[row['net_2050_mt']],
                    marker_color='green',
                    showlegend=False
                ))

            # Simpler approach - grouped bar
            fig = go.Figure(data=[
                go.Bar(name='BAU 2050', x=scenarios_df['scenario'] + ' + ' + scenarios_df['technology'],
                       y=scenarios_df['bau_2050_mt'], marker_color='indianred'),
                go.Bar(name='Net 2050', x=scenarios_df['scenario'] + ' + ' + scenarios_df['technology'],
                       y=scenarios_df['net_2050_mt'], marker_color='seagreen')
            ])
            fig.update_layout(barmode='group', title='BAU vs Net Emissions by Scenario (2050)',
                             xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Investment Comparison")

            fig = px.bar(scenarios_df,
                        x=scenarios_df['scenario'] + ' + ' + scenarios_df['technology'],
                        y='capex_billion_usd',
                        color='technology',
                        title='Total CAPEX by Scenario ($B)',
                        color_discrete_map={'NCC-H2': '#3498DB', 'NCC-Electricity': '#E74C3C'})
            fig.update_layout(xaxis_tickangle=-45, height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

        # Headline metrics
        st.markdown("---")
        st.subheader("Headline Numbers")

        col1, col2, col3, col4 = st.columns(4)

        min_capex = scenarios_df['capex_billion_usd'].min()
        max_capex = scenarios_df['capex_billion_usd'].max()
        avg_abatement = scenarios_df['ncc_abatement_mt'].mean()

        col1.metric("Lowest CAPEX", f"${min_capex:.1f}B",
                   f"구조조정 40% + NCC-H2")
        col2.metric("Highest CAPEX", f"${max_capex:.1f}B",
                   f"Shaheen + NCC-Elec")
        col3.metric("Avg NCC Abatement", f"{avg_abatement:.1f} Mt",
                   "per scenario")
        col4.metric("All Scenarios", "Net Zero Ready",
                   "3.9 Mt residual")
    else:
        st.error("Scenario data not loaded. Please run run_scenarios_complete.py first.")

# ============================================================================
# Page: Scenario Comparison
# ============================================================================
elif page == "🔄 Scenario Comparison":
    st.title("🔄 Detailed Scenario Comparison")

    if data and data.get('scenarios') is not None:
        scenarios_df = data['scenarios']

        # Production Pathway Comparison
        st.subheader("1. Production Pathway Impact")

        col1, col2 = st.columns(2)

        with col1:
            # Facility count comparison
            facility_data = scenarios_df.groupby('scenario').agg({
                'n_facilities': 'first',
                'n_ncc_facilities': 'first',
                'ncc_capacity_kt': 'first'
            }).reset_index()

            fig = go.Figure(data=[
                go.Bar(name='Total Facilities', x=facility_data['scenario'],
                       y=facility_data['n_facilities'], marker_color='steelblue'),
                go.Bar(name='NCC Facilities', x=facility_data['scenario'],
                       y=facility_data['n_ncc_facilities'], marker_color='coral')
            ])
            fig.update_layout(barmode='group', title='Facility Count by Production Pathway')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # NCC Capacity comparison
            fig = px.bar(facility_data, x='scenario', y='ncc_capacity_kt',
                        title='NCC Capacity by Production Pathway (kt)',
                        color='scenario',
                        color_discrete_sequence=['#2E86AB', '#A23B72', '#F18F01'])
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Technology Pathway Comparison
        st.subheader("2. Technology Pathway Comparison")

        col1, col2 = st.columns(2)

        with col1:
            # H2 vs Electricity CAPEX
            h2_scenarios = scenarios_df[scenarios_df['technology'] == 'NCC-H2']
            elec_scenarios = scenarios_df[scenarios_df['technology'] == 'NCC-Electricity']

            fig = go.Figure()
            fig.add_trace(go.Bar(name='NCC-H2', x=h2_scenarios['scenario'],
                                y=h2_scenarios['capex_billion_usd'], marker_color='#3498DB'))
            fig.add_trace(go.Bar(name='NCC-Electricity', x=elec_scenarios['scenario'],
                                y=elec_scenarios['capex_billion_usd'], marker_color='#E74C3C'))
            fig.update_layout(barmode='group', title='CAPEX: H2 vs Electricity Pathway ($B)')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Energy requirements
            energy_data = []
            for _, row in scenarios_df.iterrows():
                if row['technology'] == 'NCC-H2':
                    energy_data.append({
                        'Scenario': row['scenario'],
                        'Technology': 'NCC-H2',
                        'H2 Demand (kt)': row['h2_kt'],
                        'Electricity (TWh)': row['electricity_twh']
                    })
                else:
                    energy_data.append({
                        'Scenario': row['scenario'],
                        'Technology': 'NCC-Electricity',
                        'H2 Demand (kt)': 0,
                        'Electricity (TWh)': row['electricity_twh']
                    })

            energy_df = pd.DataFrame(energy_data)

            fig = px.bar(energy_df, x='Scenario', y='H2 Demand (kt)',
                        color='Technology', barmode='group',
                        title='Hydrogen Demand by Scenario (kt)',
                        color_discrete_map={'NCC-H2': '#3498DB', 'NCC-Electricity': '#E74C3C'})
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Abatement Breakdown
        st.subheader("3. Abatement Breakdown by Technology")

        abatement_data = []
        for _, row in scenarios_df.iterrows():
            label = f"{row['scenario']}\n{row['technology']}"
            abatement_data.append({
                'Scenario': label,
                'NCC Abatement': row['ncc_abatement_mt'],
                'Heat Pump': row['heat_pump_mt'],
                'RE-PPA': row['re_ppa_mt']
            })

        abatement_df = pd.DataFrame(abatement_data)

        fig = go.Figure()
        fig.add_trace(go.Bar(name='NCC Technology', x=abatement_df['Scenario'],
                            y=abatement_df['NCC Abatement'], marker_color='#2ECC71'))
        fig.add_trace(go.Bar(name='Heat Pump', x=abatement_df['Scenario'],
                            y=abatement_df['Heat Pump'], marker_color='#F39C12'))
        fig.add_trace(go.Bar(name='RE-PPA', x=abatement_df['Scenario'],
                            y=abatement_df['RE-PPA'], marker_color='#9B59B6'))
        fig.update_layout(barmode='stack', title='Abatement by Technology (Mt CO2)',
                         xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Scenario data not loaded.")

# ============================================================================
# Page: Facility Transitions
# ============================================================================
elif page == "🏭 Facility Transitions":
    st.title("🏭 Facility Transition Details")

    if selected_scenario and data.get('scenario_data'):
        scenario_data = data['scenario_data'].get(selected_scenario, {})

        st.subheader(f"Scenario: {SCENARIO_KOREAN[selected_scenario]}")

        if scenario_data.get('facilities') is not None:
            facilities = scenario_data['facilities']

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)

            n_total = len(facilities)
            n_ncc = len(facilities[facilities['process'] == 'Naphtha Cracker'])
            total_cap = facilities['capacity_kt'].sum()
            ncc_cap = facilities[facilities['process'] == 'Naphtha Cracker']['capacity_kt'].sum()

            col1.metric("Total Facilities", n_total)
            col2.metric("NCC Facilities", n_ncc)
            col3.metric("Total Capacity", f"{total_cap:,.0f} kt")
            col4.metric("NCC Capacity", f"{ncc_cap:,.0f} kt")

            st.markdown("---")

            # NCC Facilities List
            st.subheader("NCC Facilities in This Scenario")

            ncc_fac = facilities[facilities['process'] == 'Naphtha Cracker'].copy()
            ncc_fac = ncc_fac.sort_values('capacity_kt', ascending=False)

            display_cols = ['product', 'company', 'location', 'capacity_kt', 'year_built', 'age_2025']
            ncc_display = ncc_fac[display_cols].copy()
            ncc_display.columns = ['Product', 'Company', 'Location', 'Capacity (kt)', 'Year Built', 'Age (2025)']

            st.dataframe(ncc_display, use_container_width=True, hide_index=True)

            # Age Distribution Chart
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("NCC Age Distribution")
                fig = px.histogram(ncc_fac, x='age_2025', nbins=10,
                                  title='NCC Facility Age Distribution',
                                  labels={'age_2025': 'Age in 2025 (years)'})
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("NCC Capacity by Company")
                company_cap = ncc_fac.groupby('company')['capacity_kt'].sum().sort_values(ascending=False)
                fig = px.pie(values=company_cap.values, names=company_cap.index,
                            title='NCC Capacity Share by Company')
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Deployment Trajectory
            if scenario_data.get('deployment') is not None:
                st.subheader("Deployment Trajectory (2025-2050)")

                deploy = scenario_data['deployment']

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=deploy['year'], y=deploy['bau_mt'],
                                        mode='lines', name='BAU Emissions',
                                        line=dict(color='indianred', width=2, dash='dash')))
                fig.add_trace(go.Scatter(x=deploy['year'], y=deploy['actual_emissions_mt'],
                                        mode='lines+markers', name='Actual Emissions',
                                        line=dict(color='seagreen', width=3)))
                fig.update_layout(title='Emission Trajectory',
                                 xaxis_title='Year', yaxis_title='Emissions (Mt CO2)')
                st.plotly_chart(fig, use_container_width=True)

                # Show deployment data table
                deploy_display = deploy[['year', 'bau_mt', 'deployed_abatement_mt', 'actual_emissions_mt', 'grid_ef']].copy()
                deploy_display.columns = ['Year', 'BAU (Mt)', 'Abatement (Mt)', 'Net (Mt)', 'Grid EF']
                st.dataframe(deploy_display, use_container_width=True, hide_index=True)

            st.markdown("---")

            # Top Emitters
            if scenario_data.get('emissions') is not None:
                st.subheader("Top 20 Facilities by 2050 Emissions")

                emissions = scenario_data['emissions'].sort_values('total_emissions_kt', ascending=False).head(20)

                display_cols = ['product', 'company', 'location', 'capacity_kt', 'total_emissions_kt']
                emissions_display = emissions[display_cols].copy()
                emissions_display.columns = ['Product', 'Company', 'Location', 'Capacity (kt)', 'Emissions 2050 (kt)']

                st.dataframe(emissions_display, use_container_width=True, hide_index=True)
        else:
            st.warning("Facility data not found for this scenario. Run run_scenarios_complete.py first.")
    else:
        st.info("Select a scenario from the sidebar to view facility details.")

# ============================================================================
# Page: Emission Pathways
# ============================================================================
elif page == "📈 Emission Pathways":
    st.title("📈 Emission Reduction Pathways")

    if selected_scenario and data.get('scenario_data'):
        scenario_data = data['scenario_data'].get(selected_scenario, {})

        st.subheader(f"Scenario: {SCENARIO_KOREAN[selected_scenario]}")

        if scenario_data.get('deployment') is not None:
            deploy = scenario_data['deployment']

            # Main trajectory chart
            fig = go.Figure()

            # BAU line
            fig.add_trace(go.Scatter(
                x=deploy['year'], y=deploy['bau_mt'],
                mode='lines', name='BAU Scenario',
                line=dict(color='indianred', width=2, dash='dash'),
                fill='tozeroy', fillcolor='rgba(205,92,92,0.2)'
            ))

            # Actual emissions
            fig.add_trace(go.Scatter(
                x=deploy['year'], y=deploy['actual_emissions_mt'],
                mode='lines+markers', name='Net Zero Pathway',
                line=dict(color='seagreen', width=3),
                marker=dict(size=8)
            ))

            # 2035 target line
            fig.add_hline(y=43.5, line_dash="dot", line_color="orange",
                         annotation_text="2035 Target (43.5 Mt)")

            fig.update_layout(
                title='Emission Trajectory: BAU vs Net Zero Pathway',
                xaxis_title='Year',
                yaxis_title='Emissions (Mt CO2)',
                hovermode='x unified',
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # Key milestones
            col1, col2, col3, col4 = st.columns(4)

            emissions_2025 = deploy[deploy['year'] == 2025]['actual_emissions_mt'].values[0]
            emissions_2035 = deploy[deploy['year'] == 2035]['actual_emissions_mt'].values[0]
            emissions_2050 = deploy[deploy['year'] == 2050]['actual_emissions_mt'].values[0]
            bau_2050 = deploy[deploy['year'] == 2050]['bau_mt'].values[0]

            col1.metric("2025 Emissions", f"{emissions_2025:.1f} Mt")
            col2.metric("2035 Emissions", f"{emissions_2035:.1f} Mt",
                       f"{'✓ Target Met' if emissions_2035 <= 43.5 else '✗ Above Target'}")
            col3.metric("2050 Emissions", f"{emissions_2050:.1f} Mt")
            col4.metric("Total Abatement", f"{bau_2050 - emissions_2050:.1f} Mt", "vs BAU 2050")

            st.markdown("---")

            # Grid decarbonization impact
            st.subheader("Grid Decarbonization Impact")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=deploy['year'], y=deploy['grid_ef'],
                mode='lines+markers', name='Grid Emission Factor',
                line=dict(color='purple', width=2)
            ))
            fig.update_layout(
                title='Grid Emission Factor Trajectory (tCO2/MWh)',
                xaxis_title='Year',
                yaxis_title='tCO2/MWh'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Deployment data not found for this scenario.")
    else:
        st.info("Select a scenario from the sidebar to view emission pathways.")

# ============================================================================
# Page: Technology & Learning Curves
# ============================================================================
elif page == "🛠️ Technology & Learning Curves":
    st.title("🛠️ Technology Parameters & Learning Curves")

    if data:
        # Technology Parameters
        st.subheader("1. Technology Specifications")

        tech_params = data['tech_params']

        display_cols = ['technology', 'applies_to', 'capex_2025_musd_per_mtco2',
                       'capex_2050_musd_per_mtco2', 'available_year']
        tech_display = tech_params[display_cols].copy()
        tech_display.columns = ['Technology', 'Applies To', 'CAPEX 2025 ($M/MtCO2)',
                               'CAPEX 2050 ($M/MtCO2)', 'Available Year']

        st.dataframe(tech_display, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Learning Curves (50% decline)
        st.subheader("2. CAPEX Learning Curves (50% Decline by 2050)")

        years = list(range(2025, 2051))

        fig = go.Figure()

        colors = {'Heat_Pump': '#F39C12', 'NCC-H2': '#3498DB',
                 'NCC-Electricity': '#E74C3C', 'RDH': '#2ECC71'}

        for _, row in tech_params.iterrows():
            tech = row['technology']
            if row['capex_2025_musd_per_mtco2'] > 0:
                capex_2025 = row['capex_2025_musd_per_mtco2']
                capex_2050 = row['capex_2050_musd_per_mtco2']

                # Linear interpolation
                capex_traj = [capex_2025 - (capex_2025 - capex_2050) * (y - 2025) / 25 for y in years]

                fig.add_trace(go.Scatter(
                    x=years, y=capex_traj,
                    mode='lines+markers', name=tech,
                    line=dict(color=colors.get(tech, 'gray'), width=2),
                    marker=dict(size=4)
                ))

        fig.update_layout(
            title='Technology CAPEX Trajectory (50% Decline)',
            xaxis_title='Year',
            yaxis_title='CAPEX ($M per Mt CO2 abated)',
            hovermode='x unified',
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # H2 Price Trajectory (LCOH-based)
        st.subheader("3. Hydrogen Price Trajectory (LCOH-based)")

        h2_prices = data['h2_prices']

        col1, col2 = st.columns([2, 1])

        with col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=h2_prices['year'], y=h2_prices['h2_price_usd_per_kg'],
                mode='lines+markers', name='H2 Price',
                line=dict(color='#3498DB', width=3),
                marker=dict(size=6)
            ))
            fig.update_layout(
                title='Green Hydrogen Price (LCOH Calculation)',
                xaxis_title='Year',
                yaxis_title='$/kg H2',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**LCOH Assumptions:**")
            st.markdown("""
            - RE Price: $65 → $30/MWh
            - Electrolyzer: $1000 → $500/kW
            - Efficiency: 70% → 75%
            - Capacity Factor: 25%
            - Lifetime: 20 years
            """)

            st.markdown("**Key Milestones:**")
            h2_2025 = h2_prices[h2_prices['year'] == 2025]['h2_price_usd_per_kg'].values[0]
            h2_2030 = h2_prices[h2_prices['year'] == 2030]['h2_price_usd_per_kg'].values[0]
            h2_2050 = h2_prices[h2_prices['year'] == 2050]['h2_price_usd_per_kg'].values[0]

            st.metric("2025", f"${h2_2025:.2f}/kg")
            st.metric("2030", f"${h2_2030:.2f}/kg")
            st.metric("2050", f"${h2_2050:.2f}/kg", f"-{(1-h2_2050/h2_2025)*100:.0f}%")

        st.markdown("---")

        # RE Price Trajectory
        st.subheader("4. Renewable Energy Price Trajectory")

        re_prices = data['re_prices']

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=re_prices['year'], y=re_prices['re_price_usd_per_mwh'],
            mode='lines+markers', name='RE Price',
            line=dict(color='#2ECC71', width=3),
            marker=dict(size=6),
            fill='tozeroy', fillcolor='rgba(46,204,113,0.2)'
        ))
        fig.update_layout(
            title='Renewable Energy PPA Price (Korea)',
            xaxis_title='Year',
            yaxis_title='$/MWh',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Data not loaded.")

# ============================================================================
# Page: Cost & Investment
# ============================================================================
elif page == "💰 Cost & Investment":
    st.title("💰 Investment Analysis")

    if data and data.get('scenarios') is not None:
        scenarios_df = data['scenarios']

        # Total CAPEX Comparison
        st.subheader("1. Total CAPEX by Scenario")

        fig = px.bar(scenarios_df,
                    x='scenario_id', y='capex_billion_usd',
                    color='technology',
                    title='Total CAPEX Investment ($B)',
                    labels={'capex_billion_usd': 'CAPEX ($B)', 'scenario_id': 'Scenario'},
                    color_discrete_map={'NCC-H2': '#3498DB', 'NCC-Electricity': '#E74C3C'})
        fig.update_layout(xaxis_tickangle=-45, height=450)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Cost per tonne abated
        st.subheader("2. Cost Effectiveness Analysis")

        scenarios_df['cost_per_tonne'] = scenarios_df['capex_billion_usd'] * 1000 / scenarios_df['ncc_abatement_mt']

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(scenarios_df,
                        x='scenario_id', y='cost_per_tonne',
                        color='technology',
                        title='CAPEX per Tonne Abated ($M/Mt)',
                        color_discrete_map={'NCC-H2': '#3498DB', 'NCC-Electricity': '#E74C3C'})
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Scatter: CAPEX vs Abatement
            fig = px.scatter(scenarios_df,
                           x='ncc_abatement_mt', y='capex_billion_usd',
                           color='technology', size='n_ncc_facilities',
                           hover_name='scenario_id',
                           title='CAPEX vs Abatement',
                           labels={'ncc_abatement_mt': 'NCC Abatement (Mt)',
                                  'capex_billion_usd': 'CAPEX ($B)'},
                           color_discrete_map={'NCC-H2': '#3498DB', 'NCC-Electricity': '#E74C3C'})
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Investment Summary Table
        st.subheader("3. Investment Summary")

        investment_summary = scenarios_df[['scenario', 'technology', 'capex_billion_usd',
                                           'ncc_abatement_mt', 'cost_per_tonne']].copy()
        investment_summary.columns = ['Production', 'Technology', 'CAPEX ($B)',
                                      'Abatement (Mt)', 'Cost ($/tCO2)']
        investment_summary['CAPEX ($B)'] = investment_summary['CAPEX ($B)'].apply(lambda x: f"${x:.1f}")
        investment_summary['Abatement (Mt)'] = investment_summary['Abatement (Mt)'].apply(lambda x: f"{x:.1f}")
        investment_summary['Cost ($/tCO2)'] = investment_summary['Cost ($/tCO2)'].apply(lambda x: f"${x:.0f}")

        st.dataframe(investment_summary, use_container_width=True, hide_index=True)

        # Key insights
        st.markdown("---")
        st.subheader("Key Insights")

        min_cost = scenarios_df.loc[scenarios_df['cost_per_tonne'].idxmin()]
        max_cost = scenarios_df.loc[scenarios_df['cost_per_tonne'].idxmax()]

        col1, col2 = st.columns(2)

        with col1:
            st.success(f"""
            **Most Cost-Effective:**
            {min_cost['scenario']} + {min_cost['technology']}
            ${min_cost['cost_per_tonne']:.0f}/tCO2 abated
            """)

        with col2:
            st.warning(f"""
            **Highest Cost:**
            {max_cost['scenario']} + {max_cost['technology']}
            ${max_cost['cost_per_tonne']:.0f}/tCO2 abated
            """)
    else:
        st.error("Scenario data not loaded.")

# ============================================================================
# Page: Energy Requirements
# ============================================================================
elif page == "⚡ Energy Requirements":
    st.title("⚡ Energy Requirements Analysis")

    if data and data.get('scenarios') is not None:
        scenarios_df = data['scenarios']

        st.subheader("1. Energy Demand by Scenario")

        col1, col2 = st.columns(2)

        with col1:
            # Hydrogen demand
            h2_scenarios = scenarios_df[scenarios_df['technology'] == 'NCC-H2'].copy()
            h2_scenarios['h2_mt'] = h2_scenarios['h2_kt'] / 1000

            fig = px.bar(h2_scenarios, x='scenario', y='h2_mt',
                        title='Hydrogen Demand (NCC-H2 Scenarios)',
                        labels={'h2_mt': 'H2 Demand (Mt)', 'scenario': 'Production Pathway'},
                        color='scenario',
                        color_discrete_sequence=['#3498DB', '#2980B9', '#1ABC9C'])
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Electricity demand
            elec_scenarios = scenarios_df[scenarios_df['technology'] == 'NCC-Electricity'].copy()

            fig = px.bar(elec_scenarios, x='scenario', y='electricity_twh',
                        title='Additional Electricity Demand (NCC-Electricity)',
                        labels={'electricity_twh': 'Electricity (TWh)', 'scenario': 'Production Pathway'},
                        color='scenario',
                        color_discrete_sequence=['#E74C3C', '#C0392B', '#D35400'])
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Comparison: H2 vs Electricity
        st.subheader("2. Technology Pathway Comparison")

        if selected_scenario:
            scenario_data = data['scenario_data'].get(selected_scenario, {})

            st.markdown(f"**Selected: {SCENARIO_KOREAN[selected_scenario]}**")

            scenario_row = scenarios_df[scenarios_df['scenario_id'] == selected_scenario]
            if len(scenario_row) > 0:
                row = scenario_row.iloc[0]

                col1, col2, col3 = st.columns(3)

                col1.metric("Technology", row['technology'])

                if row['technology'] == 'NCC-H2':
                    col2.metric("H2 Demand", f"{row['h2_kt']/1000:.2f} Mt")
                    col3.metric("Electricity for H2", "Included in LCOH")
                else:
                    col2.metric("H2 Demand", "0 Mt")
                    col3.metric("Electricity Demand", f"{row['electricity_twh']:.1f} TWh")

        st.markdown("---")

        # Energy infrastructure requirements
        st.subheader("3. Infrastructure Implications")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### NCC-H2 Pathway")
            st.markdown("""
            **Requirements:**
            - Green H2 production facilities
            - H2 storage and distribution
            - Electrolyzer capacity: ~50-100 GW

            **Advantages:**
            - Lower grid stress
            - Flexibility in H2 sourcing
            - Potential for imports
            """)

        with col2:
            st.markdown("#### NCC-Electricity Pathway")
            st.markdown("""
            **Requirements:**
            - Massive grid expansion
            - Additional 200-300 TWh/year
            - ~40% of current Korea generation

            **Advantages:**
            - Simpler technology
            - No H2 infrastructure needed
            - Higher efficiency (direct use)
            """)
    else:
        st.error("Scenario data not loaded.")

# ============================================================================
# Page: Regional Analysis
# ============================================================================
elif page == "🗺️ Regional Analysis":
    st.title("🗺️ Regional Impact Analysis")

    if data:
        facilities = data['facilities']

        # Regional summary
        st.subheader("1. Facility Distribution by Region")

        regional = facilities.groupby('location').agg({
            'capacity_kt': 'sum',
            'product': 'count'
        }).reset_index()
        regional.columns = ['Region', 'Total Capacity (kt)', 'Facility Count']
        regional = regional.sort_values('Total Capacity (kt)', ascending=False)

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(regional.head(10), x='Region', y='Total Capacity (kt)',
                        title='Top 10 Regions by Capacity',
                        color='Total Capacity (kt)',
                        color_continuous_scale='Blues')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(regional.head(8), values='Total Capacity (kt)', names='Region',
                        title='Capacity Distribution (Top 8 Regions)')
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # NCC by region
        st.subheader("2. NCC Facilities by Region")

        ncc_facilities = facilities[facilities['process'] == 'Naphtha Cracker']
        ncc_regional = ncc_facilities.groupby('location').agg({
            'capacity_kt': 'sum',
            'product': 'count'
        }).reset_index()
        ncc_regional.columns = ['Region', 'NCC Capacity (kt)', 'NCC Count']
        ncc_regional = ncc_regional.sort_values('NCC Capacity (kt)', ascending=False)

        fig = px.bar(ncc_regional, x='Region', y='NCC Capacity (kt)',
                    title='NCC Capacity by Region',
                    color='NCC Count',
                    color_continuous_scale='Reds')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Regional data table
        st.subheader("3. Complete Regional Summary")

        st.dataframe(regional, use_container_width=True, hide_index=True)

        # Map placeholder
        st.subheader("4. Geographic Distribution")

        coords = {
            'Yeosu': {'lat': 34.7604, 'lon': 127.6622},
            'Daesan': {'lat': 36.9921, 'lon': 126.4297},
            'Ulsan': {'lat': 35.5384, 'lon': 129.3114},
            'Onsan': {'lat': 35.4354, 'lon': 129.3333},
            'Gwangyang': {'lat': 34.9407, 'lon': 127.6959},
            'Incheon': {'lat': 37.4563, 'lon': 126.7052},
        }

        map_data = []
        for _, row in regional.iterrows():
            if row['Region'] in coords:
                map_data.append({
                    'lat': coords[row['Region']]['lat'],
                    'lon': coords[row['Region']]['lon'],
                    'size': row['Total Capacity (kt)'] / 1000
                })

        if map_data:
            map_df = pd.DataFrame(map_data)
            st.map(map_df, latitude='lat', longitude='lon', size='size', zoom=6)
        else:
            st.info("Map data not available for all regions.")
    else:
        st.error("Data not loaded.")

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
Korea Petrochemical Net Zero Analysis | PLANiT Institute | 2025<br>
Data Sources: KPIA, IRENA, IEA WEO 2024 | All scenarios assume 50% CAPEX learning curve
</div>
""", unsafe_allow_html=True)
