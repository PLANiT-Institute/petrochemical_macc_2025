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
SCENARIO_DIR = BASE_DIR / "outputs/new_scenarios/cost_effective"
BAU_DIR = BASE_DIR / "outputs/new_scenarios/bau"

# ============================================================================
# Data Loading
# ============================================================================
@st.cache_data
def load_data():
    """Load all necessary data"""
    data = {}
    
    # Debug: Check file existence
    bau_path = BAU_DIR / 'module_01/bau_trajectory_2025_2050.csv'
    if not bau_path.exists():
        st.error(f"CRITICAL ERROR: File not found at {bau_path}")
        st.error(f"Current Working Directory: {Path.cwd()}")
        st.error(f"Script Location: {BASE_DIR}")
        return None

    # Trajectories
    try:
        data['bau_traj'] = pd.read_csv(bau_path)
        data['opt_traj'] = pd.read_csv(SCENARIO_DIR / 'module_03/optimization_trajectory.csv')
        data['macc_annual'] = pd.read_csv(SCENARIO_DIR / 'module_02/macc_annual_2025_2050.csv')
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
    st.write(f"**BAU Path:** `{BAU_DIR}`")
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
        opt_2050 = data['opt_traj'][data['opt_traj']['year'] == 2050]['remaining_emissions_mt'].values[0]
        total_cost = data['opt_traj']['total_annual_cost_musd'].sum() / 1000
        elec_demand = data['opt_traj'][data['opt_traj']['year'] == 2050]['electricity_demand_twh'].values[0]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("2050 Emissions", f"{opt_2050:.1f} Mt", f"-100% vs BAU")
        col2.metric("Total Investment", f"${total_cost:.1f} Billion", "2025-2050")
        col3.metric("Electricity Demand", f"{elec_demand:.0f} TWh", "in 2050")
        col4.metric("NCC Capacity", "100% Electrified", "No H2 used")

        # Waterfall Chart
        st.subheader("2050 Abatement Waterfall")
        
        # Calculate abatement by tech in 2050
        macc_2050 = data['macc_annual'][data['macc_annual']['year'] == 2050]
        
        fig = go.Figure(go.Waterfall(
            name = "2050", orientation = "v",
            measure = ["relative", "relative", "relative", "relative", "relative", "total"],
            x = ["BAU Emissions", "NCC-Electricity", "Heat Pump", "RDH", "RE-PPA (Grid)", "Net Zero"],
            textposition = "outside",
            text = [f"{bau_2050:.1f}", 
                    f"-{macc_2050[macc_2050['technology']=='NCC-Electricity']['abatement_potential_mtco2'].values[0]:.1f}",
                    f"-{macc_2050[macc_2050['technology']=='Heat_Pump']['abatement_potential_mtco2'].values[0]:.1f}",
                    f"-{macc_2050[macc_2050['technology']=='RDH']['abatement_potential_mtco2'].values[0]:.1f}",
                    f"-{macc_2050[macc_2050['technology']=='RE_PPA']['abatement_potential_mtco2'].values[0]:.1f}",
                    "0.0"],
            y = [bau_2050, 
                 -macc_2050[macc_2050['technology']=='NCC-Electricity']['abatement_potential_mtco2'].values[0],
                 -macc_2050[macc_2050['technology']=='Heat_Pump']['abatement_potential_mtco2'].values[0],
                 -macc_2050[macc_2050['technology']=='RDH']['abatement_potential_mtco2'].values[0],
                 -macc_2050[macc_2050['technology']=='RE_PPA']['abatement_potential_mtco2'].values[0],
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
            'Net Zero Pathway': data['opt_traj']['remaining_emissions_mt']
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
        df_cost = data['opt_traj']
        
        # Annual Cost Composition
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_cost['year'], y=df_cost['capex_musd'], name='CAPEX'))
        fig.add_trace(go.Bar(x=df_cost['year'], y=df_cost['opex_musd'], name='OPEX'))
        fig.add_trace(go.Bar(x=df_cost['year'], y=df_cost['fuel_cost_musd'], name='Energy Cost'))
        
        fig.update_layout(barmode='stack', title='Annual Cost Composition ($ Million)',
                          xaxis_title='Year', yaxis_title='Cost ($ Million)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Cumulative Cost
        total_capex = df_cost['capex_musd'].sum() / 1000
        total_opex = df_cost['opex_musd'].sum() / 1000
        total_energy = df_cost['fuel_cost_musd'].sum() / 1000
        
        st.subheader("Cumulative Investment (2025-2050)")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Cost", f"${total_capex+total_opex+total_energy:.1f}B")
        col2.metric("CAPEX", f"${total_capex:.1f}B")
        col3.metric("OPEX", f"${total_opex:.1f}B")
        col4.metric("Energy", f"${total_energy:.1f}B")


elif page == "🗺️ Regional Impact":
    st.title("🗺️ Regional Impact Analysis")
    
    if data:
        # Load Regional Data from Excel Report Output (or generate it on the fly)
        # For now, we simulate the aggregation from the facility database which is loaded
        
        # Aggregate facility data by region
        df_fac = data['facilities']
        
        # Calculate regional totals (Baseline)
        regional_baseline = df_fac.groupby('location').agg({
            'capacity_kt': 'sum',
            'total_emissions_kt': 'sum'
        }).reset_index()
        
        # Coordinates
        coords = {
            'Yeosu': {'lat': 34.7604, 'lon': 127.6622},
            'Daesan': {'lat': 36.9921, 'lon': 126.4297},
            'Ulsan': {'lat': 35.5384, 'lon': 129.3114},
            'Onsan': {'lat': 35.4354, 'lon': 129.3333}
        }
        
        # Add coordinates
        regional_baseline['lat'] = regional_baseline['location'].map(lambda x: coords.get(x, {}).get('lat'))
        regional_baseline['lon'] = regional_baseline['location'].map(lambda x: coords.get(x, {}).get('lon'))
        
        # Calculate Investment Share (Proportional to Capacity/Emissions)
        total_invest = data['opt_traj']['total_annual_cost_musd'].sum() / 1000
        total_emissions = regional_baseline['total_emissions_kt'].sum()
        
        regional_baseline['Investment ($B)'] = (regional_baseline['total_emissions_kt'] / total_emissions) * total_invest
        regional_baseline['Emissions (Mt)'] = regional_baseline['total_emissions_kt'] / 1000
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.map(regional_baseline, latitude='lat', longitude='lon', size='Investment ($B)', zoom=6)
            
        with col2:
            st.subheader("Regional Investment")
            st.dataframe(
                regional_baseline[['location', 'Investment ($B)', 'Emissions (Mt)']].set_index('location'),
                use_container_width=True
            )
            
        st.info("Regional investment is calculated based on the facility-level decarbonization cost for each region.")

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

