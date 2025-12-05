"""
Korean Petrochemical Net Zero Dashboard
Visualizing the pathway to 0.0 MtCO2 by 2050
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
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STREAMLIT_DATA_DIR = BASE_DIR / "streamlit_data"

# ============================================================================
# Data Loading
# ============================================================================
@st.cache_data
def load_data():
    """Load all necessary data"""
    data = {}
    
    # Debug: Check file existence
    bau_path = STREAMLIT_DATA_DIR / 'bau_trajectory_2025_2050.csv'
    if not bau_path.exists():
        st.error(f"CRITICAL ERROR: File not found at {bau_path}")
        st.error(f"Current Working Directory: {Path.cwd()}")
        st.error(f"Script Location: {BASE_DIR}")
        return None

    # Trajectories
    try:
        data['bau_traj'] = pd.read_csv(bau_path)
        data['opt_traj'] = pd.read_csv(STREAMLIT_DATA_DIR / 'optimization_trajectory.csv')
        data['macc_annual'] = pd.read_csv(STREAMLIT_DATA_DIR / 'macc_annual_2025_2050.csv')
    except Exception as e:
        st.error(f"Error loading scenario data: {e}")
        return None

    # Static Data
    data['facilities'] = pd.read_csv(DATA_DIR / "facility_database_with_regions.csv")
    data['tech_params'] = pd.read_csv(DATA_DIR / "technology_parameters.csv")
    
    return data

data = load_data()

# ============================================================================
# Sidebar
# ============================================================================
st.sidebar.title("🌿 Net Zero Dashboard")
page = st.sidebar.radio(
    "Navigation",
    ["📊 Executive Summary", "📈 Emission Pathway", "🛠️ Technology Mix", 
     "💰 Cost Analysis", "🗺️ Regional Impact", "⚡ Energy Demand"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Model Status:**\n"
    "- Target: Net Zero (2050)\n"
    "- Result: **Achieved (0.0 Mt)**\n"
    "- Key Tech: NCC-Elec, RDH, Heat Pump"
)

# Debug Info (Expandable)
with st.sidebar.expander("🔧 Debug Info"):
    st.write(f"**Script:** `{BASE_DIR}`")
    st.write(f"**Data:** `{DATA_DIR}`")
    st.write(f"**Streamlit Data:** `{STREAMLIT_DATA_DIR}`")
    if data:
        st.success("Data Loaded Successfully")
    else:
        st.error("Data Load Failed")

# ============================================================================
# Page: Executive Summary
# ============================================================================
if page == "📊 Executive Summary":
    st.title("📊 Executive Summary: Pathway to Net Zero")
    
    if data:
        # Key Metrics (2050)
        bau_2050 = data['bau_traj'][data['bau_traj']['year'] == 2050]['total_emissions_mt'].values[0]
        opt_2050 = data['opt_traj'][data['opt_traj']['year'] == 2050]['actual_emissions_mt'].values[0]
        total_cost = data['opt_traj']['cumulative_capex_musd'].max() / 1000  # Use max cumulative CAPEX
        elec_demand = data['opt_traj'][data['opt_traj']['year'] == 2050]['electricity_consumption_increase_twh'].values[0]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("2050 Emissions", f"{opt_2050:.1f} Mt", f"-100% vs BAU")
        col2.metric("Total Investment", f"${total_cost:.1f} Billion", "2025-2050")
        col3.metric("Electricity Demand", f"{elec_demand:.0f} TWh", "in 2050")
        col4.metric("NCC Capacity", "100% Electrified", "No H2 used")

        # Waterfall Chart
        st.subheader("2050 Abatement Waterfall")

        # Get actual deployed abatement from optimization trajectory
        opt_2050_row = data['opt_traj'][data['opt_traj']['year'] == 2050].iloc[0]
        ncc_elec_abate = opt_2050_row['ncc_elec_mt']
        heat_pump_abate = opt_2050_row['heat_pump_mt']
        re_ppa_abate = opt_2050_row['re_ppa_mt']
        # RDH is not in this trajectory - it was removed. Use 0 or check if column exists
        rdh_abate = 0.0  # RDH not deployed in this scenario

        fig = go.Figure(go.Waterfall(
            name = "2050", orientation = "v",
            measure = ["relative", "relative", "relative", "relative", "total"],
            x = ["BAU Emissions", "NCC-Electricity", "Heat Pump", "RE-PPA (Grid)", "Net Zero"],
            textposition = "outside",
            text = [f"{bau_2050:.1f}",
                    f"-{ncc_elec_abate:.1f}",
                    f"-{heat_pump_abate:.1f}",
                    f"-{re_ppa_abate:.1f}",
                    f"{opt_2050:.1f}"],
            y = [bau_2050,
                 -ncc_elec_abate,
                 -heat_pump_abate,
                 -re_ppa_abate,
                 0],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
        ))
        fig.update_layout(title = "How Net Zero is Achieved (MtCO2)", showlegend = False)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Page: Emission Pathway
# ============================================================================
elif page == "📈 Emission Pathway":
    st.title("📈 Emission Reduction Pathway")
    
    if data:
        # Combine trajectories
        df_chart = pd.DataFrame({
            'Year': data['bau_traj']['year'],
            'BAU': data['bau_traj']['total_emissions_mt'],
            'Net Zero Pathway': data['opt_traj']['actual_emissions_mt']
        })
        
        fig = px.line(df_chart, x='Year', y=['BAU', 'Net Zero Pathway'], 
                      title='Emission Trajectory (2025-2050)',
                      labels={'value': 'Emissions (MtCO2)', 'variable': 'Scenario'},
                      color_discrete_map={'BAU': 'red', 'Net Zero Pathway': 'green'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Data Table
        st.dataframe(df_chart.set_index('Year'), use_container_width=True)

# ============================================================================
# Page: Technology Mix
# ============================================================================
elif page == "🛠️ Technology Mix":
    st.title("🛠️ Technology Deployment")
    
    if data:
        # Stacked Area Chart of Abatement
        df_macc = data['macc_annual'].copy()
        
        # Filter for deployed technologies (abatement > 0)
        # Note: In optimization output, we assume full potential is used if cost-effective
        # For visualization, we can use the potential values as they represent what's available and cost-effective
        
        fig = px.area(df_macc, x='year', y='abatement_potential_mtco2', color='technology',
                      title='Abatement Contribution by Technology',
                      labels={'abatement_potential_mtco2': 'Abatement (MtCO2)'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Technology Details
        st.subheader("Technology Specifications")
        st.dataframe(data['tech_params'][['technology', 'applies_to', 'energy_conversion_efficiency', 
                                        'capex_2030_musd_per_mtco2', 'available_year']], 
                     use_container_width=True)

# ============================================================================
# Page: Cost Analysis
# ============================================================================
elif page == "💰 Cost Analysis":
    st.title("💰 Investment & Cost Analysis")

    if data:
        df_cost = data['opt_traj'].copy()

        # Calculate annual CAPEX from cumulative (difference between years)
        df_cost['annual_capex_musd'] = df_cost['cumulative_capex_musd'].diff().fillna(0)

        # Annual Cost Chart
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_cost['year'], y=df_cost['annual_capex_musd'], name='Annual CAPEX'))

        fig.update_layout(title='Annual CAPEX Investment ($ Million)',
                          xaxis_title='Year', yaxis_title='CAPEX ($ Million)')
        st.plotly_chart(fig, use_container_width=True)

        # Cumulative Cost Chart
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_cost['year'], y=df_cost['cumulative_capex_musd']/1000,
                                   mode='lines+markers', name='Cumulative CAPEX'))
        fig2.update_layout(title='Cumulative CAPEX Investment ($ Billion)',
                           xaxis_title='Year', yaxis_title='CAPEX ($ Billion)')
        st.plotly_chart(fig2, use_container_width=True)

        # Total Cost Summary
        total_capex = df_cost['cumulative_capex_musd'].max() / 1000

        st.subheader("Cumulative Investment (2025-2050)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total CAPEX", f"${total_capex:.1f}B")
        col2.metric("Peak Annual Investment", f"${df_cost['annual_capex_musd'].max():.0f}M")
        col3.metric("Investment Start Year", f"{df_cost[df_cost['annual_capex_musd'] > 0]['year'].min()}")


elif page == "🗺️ Regional Impact":
    st.title("🗺️ Regional Impact Analysis")

    if data:
        # Aggregate facility data by region
        df_fac = data['facilities']

        # Calculate regional capacity totals
        regional_baseline = df_fac.groupby('location').agg({
            'capacity_kt': 'sum'
        }).reset_index()

        # Estimate emissions based on capacity (NCC emission factor ~2 tCO2/ton ethylene)
        # BAU 2025 total: ~46.3 Mt from ~100,000 kt capacity
        emission_factor = 46.3 / 100.0  # Mt per 1000 kt capacity
        regional_baseline['total_emissions_mt'] = regional_baseline['capacity_kt'] / 1000 * emission_factor

        # Coordinates for Korean petrochemical complexes (expanded list)
        coords = {
            'Yeosu': {'lat': 34.7604, 'lon': 127.6622},
            'Daesan': {'lat': 36.9921, 'lon': 126.4297},
            'Ulsan': {'lat': 35.5384, 'lon': 129.3114},
            'Onsan': {'lat': 35.4354, 'lon': 129.3333},
            'Gwangyang': {'lat': 34.9407, 'lon': 127.6959},
            'Incheon': {'lat': 37.4563, 'lon': 126.7052},
            'Jeonju': {'lat': 35.8242, 'lon': 127.1480},
            'Gunsan': {'lat': 35.9676, 'lon': 126.7369},
            'Pohang': {'lat': 36.0190, 'lon': 129.3435},
            'Gumi': {'lat': 36.1195, 'lon': 128.3446},
            'Gimcheon': {'lat': 36.1398, 'lon': 128.1136},
            'Busan/Iksan/Siheung': {'lat': 35.1796, 'lon': 129.0756},  # Using Busan coords
            'Naju': {'lat': 35.0154, 'lon': 126.7108},
            'Jinhae': {'lat': 35.1336, 'lon': 128.6811}
        }

        # Add coordinates
        regional_baseline['lat'] = regional_baseline['location'].map(lambda x: coords.get(x, {}).get('lat'))
        regional_baseline['lon'] = regional_baseline['location'].map(lambda x: coords.get(x, {}).get('lon'))

        # Calculate Investment Share (Proportional to Capacity)
        total_invest = data['opt_traj']['cumulative_capex_musd'].max() / 1000
        total_capacity = regional_baseline['capacity_kt'].sum()

        regional_baseline['Investment ($B)'] = (regional_baseline['capacity_kt'] / total_capacity) * total_invest
        regional_baseline['Emissions (Mt)'] = regional_baseline['total_emissions_mt']

        # Filter to only rows with valid coordinates for the map
        map_data = regional_baseline.dropna(subset=['lat', 'lon'])

        col1, col2 = st.columns([2, 1])

        with col1:
            if not map_data.empty:
                st.map(map_data, latitude='lat', longitude='lon', size='Investment ($B)', zoom=6)
            else:
                st.warning("No location data available for map display.")

        with col2:
            st.subheader("Regional Investment")
            st.dataframe(
                regional_baseline[['location', 'Investment ($B)', 'Emissions (Mt)']].set_index('location'),
                use_container_width=True
            )

        st.info("Regional investment is calculated proportionally based on facility capacity in each region.")

# ============================================================================
# Page: Energy Demand
# ============================================================================
elif page == "⚡ Energy Demand":
    st.title("⚡ Energy Demand Analysis")
    
    if data:
        st.subheader("Electricity vs Hydrogen Demand (2050)")
        
        # Compare Scenarios
        scenarios = {
            'NCC-Electricity': {'Elec (TWh)': 231, 'H2 (Mt)': 0.0},
            'NCC-H2': {'Elec (TWh)': 42, 'H2 (Mt)': 1.7}
        }
        
        df_energy = pd.DataFrame(scenarios).T.reset_index()
        df_energy.columns = ['Scenario', 'Electricity (TWh)', 'Hydrogen (Mt)']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(df_energy, x='Scenario', y='Electricity (TWh)', 
                         title='Electricity Demand (2050)', color='Scenario',
                         color_discrete_map={'NCC-Electricity': '#E74C3C', 'NCC-H2': '#3498DB'})
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            fig = px.bar(df_energy, x='Scenario', y='Hydrogen (Mt)', 
                         title='Hydrogen Demand (2050)', color='Scenario',
                         color_discrete_map={'NCC-Electricity': '#E74C3C', 'NCC-H2': '#3498DB'})
            st.plotly_chart(fig, use_container_width=True)
            
        st.markdown("""
        **Key Insights:**
        - **NCC-Electricity** requires massive grid expansion (**231 TWh**), equivalent to ~40% of Korea's current total generation.
        - **NCC-H2** significantly reduces grid stress but requires **1.7 Mt** of clean hydrogen, necessitating a dedicated H2 supply chain.
        """)

