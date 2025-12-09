"""
Korea Petrochemical Net Zero - Regional Analysis Dashboard
==========================================================
Enhanced with: Technology Deployment, Emission Paths, Energy Demand by Region
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
OUTPUTS_DIR = BASE_DIR / "outputs"

# Scenario mapping
SCENARIOS = {
    'shaheen_ncc_h2': 'Shaheen + NCC-H2',
    'shaheen_ncc_electricity': 'Shaheen + NCC-전기화',
    'restructure_25pct_ncc_h2': '구조조정 25% + NCC-H2',
    'restructure_25pct_ncc_electricity': '구조조정 25% + NCC-전기화',
    'restructure_40pct_ncc_h2': '구조조정 40% + NCC-H2',
    'restructure_40pct_ncc_electricity': '구조조정 40% + NCC-전기화',
}

# Load data
@st.cache_data
def load_regional_data():
    """Load regional annual analysis from all scenarios"""
    all_data = []
    for sid in SCENARIOS.keys():
        path = OUTPUTS_DIR / f"scenario_{sid}" / "module_03_optimization" / "regional_annual_analysis.csv"
        if path.exists():
            df = pd.read_csv(path)
            df['scenario_id'] = sid
            df['scenario_name'] = SCENARIOS[sid]
            all_data.append(df)
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return None

@st.cache_data
def load_assumptions():
    data = {}
    try:
        data['fac'] = pd.read_csv(DATA_DIR / "facility_database_with_regions.csv")
        data['tech'] = pd.read_csv(DATA_DIR / "technology_parameters.csv")
        data['grid'] = pd.read_csv(DATA_DIR / "grid_emission_trajectory.csv")
    except Exception as e:
        st.warning(f"Some data files missing: {e}")
    return data

regional_df = load_regional_data()
assumptions = load_assumptions()

# Sidebar
st.sidebar.title("🏭 Net Zero Dashboard")
st.sidebar.markdown("**Korea Petrochemical Industry**")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", [
    "📊 Executive Summary",
    "🗺️ Regional Transitions",
    "⚡ Energy Demand",
    "📋 Assumptions"
])

st.sidebar.markdown("---")

# Scenario selector
if regional_df is not None:
    scenarios_available = regional_df['scenario_id'].unique().tolist()
    selected_scenario = st.sidebar.selectbox(
        "Scenario",
        scenarios_available,
        format_func=lambda x: SCENARIOS.get(x, x)
    )
else:
    selected_scenario = None
    st.sidebar.warning("No scenario data found")

st.sidebar.markdown("---")
st.sidebar.info("**Operating Rate:** 70%\n\n**Period:** 2025-2050\n\n**NO CCS/CCUS**")

# ==================== EXECUTIVE SUMMARY ====================
if page == "📊 Executive Summary":
    st.title("📊 Executive Summary")
    
    if regional_df is not None and selected_scenario:
        df = regional_df[regional_df['scenario_id'] == selected_scenario]
        
        # 2050 totals
        df_2050 = df[df['year'] == 2050]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("BAU 2050", f"{df_2050['bau_emissions_mt'].sum():.1f} Mt")
        col2.metric("Net 2050", f"{df_2050['actual_emissions_mt'].sum():.1f} Mt")
        col3.metric("Abatement", f"{df_2050['abatement_mt'].sum():.1f} Mt")
        col4.metric("Electricity", f"{df_2050['electricity_demand_twh'].sum():.1f} TWh")
        
        st.markdown("---")
        
        # Total emission path
        st.subheader("Total Emission Pathway")
        yearly = df.groupby('year').agg({
            'bau_emissions_mt': 'sum',
            'actual_emissions_mt': 'sum'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=yearly['year'], y=yearly['bau_emissions_mt'], name='BAU', line=dict(color='red', dash='dash', width=2)))
        fig.add_trace(go.Scatter(x=yearly['year'], y=yearly['actual_emissions_mt'], name='With Technology', fill='tozeroy', line=dict(color='green', width=2)))
        fig.update_layout(xaxis_title='Year', yaxis_title='Mt CO2', height=400)
        st.plotly_chart(fig, use_container_width=True)

# ==================== REGIONAL TRANSITIONS ====================
elif page == "🗺️ Regional Transitions":
    st.title("🗺️ Regional Transitions")
    st.markdown(f"**Scenario:** {SCENARIOS.get(selected_scenario, selected_scenario)}")
    
    if regional_df is not None and selected_scenario:
        df = regional_df[regional_df['scenario_id'] == selected_scenario]
        regions = sorted(df['location'].unique())
        
        # Filter to major regions (exclude small ones)
        major_regions = [r for r in regions if df[df['location'] == r]['bau_emissions_mt'].sum() > 0.5]
        
        st.markdown("---")
        
        # ===== 1. TECHNOLOGY DEPLOYMENT =====
        st.header("1. Technology Deployment by Region (Annual)")
        st.markdown("*Abatement achieved by each technology (Mt CO2)*")
        
        for region in major_regions:
            region_df = df[df['location'] == region]
            
            # Melt tech columns
            tech_data = region_df[['year', 'heat_pump_mt', 'ncc_h2_mt', 'ncc_elec_mt', 're_ppa_mt']].copy()
            tech_data = tech_data.groupby('year').sum().reset_index()
            tech_melted = tech_data.melt(id_vars='year', var_name='Technology', value_name='Mt CO2')
            tech_melted['Technology'] = tech_melted['Technology'].replace({
                'heat_pump_mt': 'Heat Pump',
                'ncc_h2_mt': 'NCC-H2',
                'ncc_elec_mt': 'NCC-Electricity',
                're_ppa_mt': 'RE-PPA'
            })
            
            fig = px.area(tech_melted, x='year', y='Mt CO2', color='Technology',
                         title=f'📍 {region}',
                         color_discrete_map={'Heat Pump': '#E67E22', 'NCC-H2': '#3498DB', 
                                            'NCC-Electricity': '#9B59B6', 'RE-PPA': '#27AE60'})
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # ===== 2. EMISSION REDUCTION PATH =====
        st.header("2. Emission Reduction Path by Region (Annual)")
        st.markdown("*BAU vs Actual emissions over time*")
        
        cols = st.columns(2)
        for i, region in enumerate(major_regions):
            with cols[i % 2]:
                region_df = df[df['location'] == region]
                yearly = region_df.groupby('year').agg({
                    'bau_emissions_mt': 'sum',
                    'actual_emissions_mt': 'sum'
                }).reset_index()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=yearly['year'], y=yearly['bau_emissions_mt'], 
                                        name='BAU', line=dict(color='red', dash='dash')))
                fig.add_trace(go.Scatter(x=yearly['year'], y=yearly['actual_emissions_mt'], 
                                        name='Net', fill='tozeroy', line=dict(color='green')))
                fig.update_layout(title=f'📍 {region}', xaxis_title='Year', yaxis_title='Mt CO2', height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # ===== 3. ENERGY DEMAND =====
        st.header("3. Energy Demand by Region (Annual)")
        st.markdown("*Total electricity demand including technology additions (TWh)*")
        
        cols = st.columns(2)
        for i, region in enumerate(major_regions):
            with cols[i % 2]:
                region_df = df[df['location'] == region]
                yearly = region_df.groupby('year')['electricity_demand_twh'].sum().reset_index()
                
                fig = px.area(yearly, x='year', y='electricity_demand_twh', 
                             title=f'📍 {region}')
                fig.update_traces(fillcolor='rgba(52, 152, 219, 0.5)', line_color='#3498DB')
                fig.update_layout(yaxis_title='TWh', height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Summary table
        st.header("4. Regional Summary (2050)")
        df_2050 = df[df['year'] == 2050]
        summary = df_2050.groupby('location').agg({
            'bau_emissions_mt': 'sum',
            'actual_emissions_mt': 'sum',
            'abatement_mt': 'sum',
            'heat_pump_mt': 'sum',
            'ncc_elec_mt': 'sum',
            're_ppa_mt': 'sum',
            'electricity_demand_twh': 'sum'
        }).reset_index()
        summary.columns = ['Region', 'BAU (Mt)', 'Net (Mt)', 'Abatement (Mt)', 
                          'Heat Pump', 'NCC-Elec', 'RE-PPA', 'Electricity (TWh)']
        st.dataframe(summary.round(2), hide_index=True, use_container_width=True)

# ==================== ENERGY DEMAND ====================
elif page == "⚡ Energy Demand":
    st.title("⚡ Energy Demand Analysis")
    
    if regional_df is not None and selected_scenario:
        df = regional_df[regional_df['scenario_id'] == selected_scenario]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Total Electricity Demand")
            yearly = df.groupby('year')['electricity_demand_twh'].sum().reset_index()
            fig = px.area(yearly, x='year', y='electricity_demand_twh', title='Total (TWh)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("By Region")
            yearly = df.groupby(['year', 'location'])['electricity_demand_twh'].sum().reset_index()
            fig = px.line(yearly, x='year', y='electricity_demand_twh', color='location', title='Regional (TWh)')
            st.plotly_chart(fig, use_container_width=True)
        
        # 2050 breakdown
        st.subheader("2050 Breakdown")
        df_2050 = df[df['year'] == 2050]
        fig = px.pie(df_2050, values='electricity_demand_twh', names='location', title='Electricity by Region (2050)')
        st.plotly_chart(fig, use_container_width=True)

# ==================== ASSUMPTIONS ====================
elif page == "📋 Assumptions":
    st.title("📋 Key Assumptions")
    
    st.markdown("""
    | Parameter | Value | Source |
    |-----------|-------|--------|
    | **Operating Rate** | 70% | Industry average (2023-2024) |
    | **Baseline Year** | 2025 | Current state |
    | **Target Year** | 2050 | Net Zero |
    | **2035 Target** | 30.4 Mt | NDC (24.5% reduction from 2018 @ 70%) |
    | **Grid EF 2050** | 0.0 tCO2/MWh | Full decarbonization |
    | **H2 Price 2050** | ~$2/kg | Cost reduction trajectory |
    """)
    
    st.markdown("---")
    
    if 'fac' in assumptions:
        st.subheader("Facility Coverage")
        fac = assumptions['fac']
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Facilities", len(fac))
        col2.metric("Total Capacity", f"{fac['capacity_kt'].sum():,.0f} kt")
        col3.metric("Regions", fac['location'].nunique())
        
        fig = px.pie(fac.groupby('location')['capacity_kt'].sum().reset_index(), 
                    values='capacity_kt', names='location', title='Capacity by Region')
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Korea Petrochemical Net Zero | 2024 | 70% Operating Rate | NO CCS/CCUS")
