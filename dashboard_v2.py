"""
MACC Analysis Dashboard - Korean Petrochemical Industry Decarbonization
Streamlit interactive dashboard with regional analysis and cost unit conversion
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Korean Petrochemical MACC Dashboard",
    page_icon="🏭",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load all data files"""
    try:
        data = {
            'macc': pd.read_csv('outputs/module_02/macc_annual_2025_2050.csv'),
            'cost_units': pd.read_csv('outputs/module_02/macc_cost_units_comparison.csv'),
            'regional_baseline': pd.read_csv('outputs/module_03/regional_baseline.csv'),
            'aggressive_deployment': pd.read_csv('outputs/module_03/Aggressive_regional_deployment.csv'),
            'moderate_deployment': pd.read_csv('outputs/module_03/Moderate_regional_deployment.csv'),
            'conservative_deployment': pd.read_csv('outputs/module_03/Conservative_regional_deployment.csv'),
        }
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

data = load_data()

if data is None:
    st.error("Failed to load data. Please ensure all output files exist.")
    st.stop()

# Main header
st.markdown('<div class="main-header">🏭 Korean Petrochemical Industry Decarbonization Dashboard</div>',
            unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Settings")
view_mode = st.sidebar.radio(
    "Select View",
    ["📊 Overview", "💰 Cost Analysis", "🗺️ Regional Analysis", "📈 Scenario Comparison", "🔬 Technology Deep Dive"]
)

# ============================================================================
# OVERVIEW TAB
# ============================================================================
if view_mode == "📊 Overview":
    st.header("📊 National Overview")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Baseline Emissions (2025)",
            "52.1 MtCO₂/year",
            help="Total emissions from 248 facilities"
        )

    with col2:
        st.metric(
            "Total Facilities",
            "248",
            help="Across 4 major clusters"
        )

    with col3:
        st.metric(
            "2050 Target (Aggressive)",
            "5.0 MtCO₂",
            "-90.4%",
            delta_color="inverse"
        )

    with col4:
        st.metric(
            "Required RE (2050)",
            "130 TWh",
            help="Additional renewable electricity needed"
        )

    st.markdown("---")

    # Baseline by region
    st.subheader("Regional Baseline Distribution")

    fig = px.bar(
        data['regional_baseline'].sort_values('emissions_mt', ascending=False).head(8),
        x='location',
        y='emissions_mt',
        title='2025 Baseline Emissions by Region',
        labels={'emissions_mt': 'Emissions (MtCO₂)', 'location': 'Region'},
        color='emissions_mt',
        color_continuous_scale='Reds'
    )
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 4 Clusters")
        top4 = data['regional_baseline'].sort_values('emissions_mt', ascending=False).head(4)
        total_emissions = data['regional_baseline']['emissions_mt'].sum()

        for idx, row in top4.iterrows():
            pct = (row['emissions_mt'] / total_emissions * 100)
            st.markdown(f"""
            **{row['location']}**
            - Emissions: {row['emissions_mt']:.2f} MtCO₂ ({pct:.1f}%)
            - Facilities: {int(row['num_facilities'])}
            - Energy: {row['energy_pj']:.1f} PJ
            """)

    with col2:
        st.subheader("Energy Distribution")
        fig_pie = px.pie(
            top4,
            values='energy_pj',
            names='location',
            title='Energy Consumption by Top 4 Clusters'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ============================================================================
# COST ANALYSIS TAB
# ============================================================================
elif view_mode == "💰 Cost Analysis":
    st.header("💰 Multi-Unit Cost Analysis")

    st.markdown("""
    **Why multiple units?**
    - **$/tCO₂**: Standard MACC metric for policy comparison
    - **$/ton ethylene**: Industry practitioners understand production costs
    - **₩/ton ethylene**: Korean stakeholders prefer local currency
    - **$/boe**: Energy economists compare with oil prices
    """)

    # Year selector
    selected_year = st.selectbox("Select Year", [2025, 2030, 2040, 2050])

    # Filter data
    df_year = data['cost_units'][data['cost_units']['Year'] == selected_year]

    # Display table
    st.subheader(f"Technology Costs in {selected_year}")

    # Format the dataframe
    df_display = df_year.copy()
    df_display['Cost ($/tCO2)'] = df_display['Cost ($/tCO2)'].apply(lambda x: f"${x:,.0f}")
    df_display['Cost ($/ton ethylene)'] = df_display['Cost ($/ton ethylene)'].apply(lambda x: f"${x:,.0f}")
    df_display['Cost (₩/ton ethylene)'] = df_display['Cost (₩/ton ethylene)'].apply(lambda x: f"₩{x:,.0f}")
    df_display['Cost ($/boe)'] = df_display['Cost ($/boe)'].apply(lambda x: f"${x:,.0f}")

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Cost evolution visualization
    st.subheader("Cost Evolution Across Years")

    cost_unit = st.radio(
        "Select Cost Unit",
        ["Cost ($/tCO2)", "Cost ($/ton ethylene)", "Cost (₩/ton ethylene)", "Cost ($/boe)"],
        horizontal=True
    )

    fig = go.Figure()

    for tech in data['cost_units']['Technology'].unique():
        df_tech = data['cost_units'][data['cost_units']['Technology'] == tech]
        fig.add_trace(go.Scatter(
            x=df_tech['Year'],
            y=df_tech[cost_unit],
            mode='lines+markers',
            name=tech,
            line=dict(width=3),
            marker=dict(size=10)
        ))

    fig.update_layout(
        title=f'Technology Cost Evolution: {cost_unit}',
        xaxis_title='Year',
        yaxis_title=cost_unit,
        hovermode='x unified',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Cost comparison insights
    st.subheader("💡 Key Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        **{selected_year} Electrification Pathway**
        - Heat Pump: {df_year[df_year['Technology']=='Heat_Pump']['Cost ($/ton ethylene)'].values[0]:.0f} $/ton
        - NCC-Elec: {df_year[df_year['Technology']=='NCC-Electricity']['Cost ($/ton ethylene)'].values[0]:.0f} $/ton
        - RE PPA: {df_year[df_year['Technology']=='RE_PPA']['Cost ($/ton ethylene)'].values[0]:.0f} $/ton
        """)

    with col2:
        st.markdown(f"""
        **{selected_year} Hydrogen Pathway**
        - NCC-H₂: {df_year[df_year['Technology']=='NCC-H2']['Cost ($/ton ethylene)'].values[0]:.0f} $/ton
        - Premium vs Electricity: {(df_year[df_year['Technology']=='NCC-H2']['Cost ($/ton ethylene)'].values[0] / df_year[df_year['Technology']=='NCC-Electricity']['Cost ($/ton ethylene)'].values[0]):.1f}x
        """)

# ============================================================================
# REGIONAL ANALYSIS TAB
# ============================================================================
elif view_mode == "🗺️ Regional Analysis":
    st.header("🗺️ Regional Technology Transition Analysis")

    # Scenario selector
    scenario = st.selectbox(
        "Select Scenario",
        ["Aggressive", "Moderate", "Conservative"]
    )

    deployment_key = f'{scenario.lower()}_deployment'
    df_deployment = data[deployment_key]

    # Filter to major clusters
    major_clusters = ['Daesan', 'Yeosu', 'Ulsan', 'Onsan']
    df_major = df_deployment[df_deployment['location'].isin(major_clusters)]

    # Overview metrics
    st.subheader(f"{scenario} Scenario - 2050 Regional Summary")

    cols = st.columns(4)
    for idx, location in enumerate(major_clusters):
        row = df_major[df_major['location'] == location].iloc[0]
        with cols[idx]:
            st.metric(
                location,
                f"{row['total_abatement_mt']:.1f} Mt",
                f"-{(row['total_abatement_mt'] / row['total_baseline_emissions_kt'] * 1000 * 100):.0f}%"
            )

    st.markdown("---")

    # Technology penetration heatmap
    st.subheader("Technology Penetration Rates by Region")

    tech_cols = [
        ('heat_pump_avg_pct', 'Heat Pump'),
        ('ncc_elec_avg_pct', 'NCC-Electricity'),
        ('ncc_h2_avg_pct', 'NCC-H₂'),
        ('re_ppa_avg_pct', 'RE PPA')
    ]

    heatmap_data = []
    for location in major_clusters:
        row = df_major[df_major['location'] == location].iloc[0]
        for col_name, tech_name in tech_cols:
            heatmap_data.append({
                'Region': location,
                'Technology': tech_name,
                'Penetration (%)': row[col_name]
            })

    df_heatmap = pd.DataFrame(heatmap_data)
    df_pivot = df_heatmap.pivot(index='Region', columns='Technology', values='Penetration (%)')

    fig = px.imshow(
        df_pivot,
        labels=dict(x="Technology", y="Region", color="Penetration (%)"),
        x=df_pivot.columns,
        y=df_pivot.index,
        color_continuous_scale='RdYlGn',
        aspect='auto',
        title=f'{scenario} Scenario - Technology Penetration Heatmap (2050)'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Detailed regional cards
    st.subheader("Regional Deep Dive")

    for location in major_clusters:
        row = df_major[df_major['location'] == location].iloc[0]
        baseline = data['regional_baseline'][data['regional_baseline']['location'] == location].iloc[0]

        with st.expander(f"🏭 {location} Cluster"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Baseline (2025)**")
                st.metric("Emissions", f"{baseline['emissions_mt']:.1f} Mt")
                st.metric("Facilities", f"{int(baseline['num_facilities'])}")
                st.metric("Energy", f"{baseline['energy_pj']:.0f} PJ")

            with col2:
                st.markdown("**2050 Deployment**")
                st.metric("Abatement", f"{row['total_abatement_mt']:.1f} Mt")
                st.metric("Residual", f"{row['total_emissions_2050_kt']/1000:.1f} Mt")
                reduction_pct = (row['total_abatement_mt'] / baseline['emissions_mt'] * 100)
                st.metric("Reduction", f"{reduction_pct:.0f}%")

            with col3:
                st.markdown("**Technology Mix**")
                st.write(f"Heat Pump: {row['heat_pump_num_facilities']:.0f} facilities")
                st.write(f"NCC-Elec: {row['ncc_elec_num_facilities']:.0f} facilities")
                st.write(f"NCC-H₂: {row['ncc_h2_num_facilities']:.0f} facilities")
                st.write(f"RE PPA: {row['re_ppa_num_facilities']:.0f} facilities")

# ============================================================================
# SCENARIO COMPARISON TAB
# ============================================================================
elif view_mode == "📈 Scenario Comparison":
    st.header("📈 Scenario Comparison")

    st.markdown("""
    Compare three deployment pathways:
    - **Conservative**: Gradual, mature technologies first
    - **Moderate**: Balanced deployment across all technologies
    - **Aggressive**: Rapid electrification and RE procurement
    """)

    # Aggregate scenario data
    scenarios_summary = []
    for scenario in ['Aggressive', 'Moderate', 'Conservative']:
        deployment_key = f'{scenario.lower()}_deployment'
        df = data[deployment_key]

        scenarios_summary.append({
            'Scenario': scenario,
            'Total Abatement (Mt)': df['total_abatement_mt'].sum(),
            'Residual 2050 (Mt)': df['total_emissions_2050_kt'].sum() / 1000,
            'Reduction (%)': (df['total_abatement_mt'].sum() / 52.1 * 100),
            'Heat Pump Facilities': df['heat_pump_num_facilities'].sum(),
            'NCC-Elec Facilities': df['ncc_elec_num_facilities'].sum(),
            'NCC-H₂ Facilities': df['ncc_h2_num_facilities'].sum(),
            'RE PPA Facilities': df['re_ppa_num_facilities'].sum(),
        })

    df_scenarios = pd.DataFrame(scenarios_summary)

    # Display comparison table
    st.subheader("Scenario Metrics (2050)")
    st.dataframe(df_scenarios.set_index('Scenario'), use_container_width=True)

    # Visualization
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df_scenarios,
            x='Scenario',
            y='Reduction (%)',
            title='Emission Reduction by Scenario',
            labels={'Reduction (%)': 'Reduction (%)'},
            color='Scenario',
            color_discrete_sequence=['#d62728', '#ff7f0e', '#2ca02c']
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            df_scenarios,
            x='Scenario',
            y='Residual 2050 (Mt)',
            title='Residual Emissions in 2050',
            labels={'Residual 2050 (Mt)': 'Emissions (Mt)'},
            color='Scenario',
            color_discrete_sequence=['#d62728', '#ff7f0e', '#2ca02c']
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Technology deployment comparison
    st.subheader("Technology Deployment by Scenario")

    tech_deployment = df_scenarios[['Scenario', 'Heat Pump Facilities', 'NCC-Elec Facilities',
                                     'NCC-H₂ Facilities', 'RE PPA Facilities']].set_index('Scenario')

    fig = go.Figure()
    for col in tech_deployment.columns:
        fig.add_trace(go.Bar(
            name=col.replace(' Facilities', ''),
            x=tech_deployment.index,
            y=tech_deployment[col]
        ))

    fig.update_layout(
        barmode='group',
        title='Number of Facilities by Technology and Scenario',
        xaxis_title='Scenario',
        yaxis_title='Number of Facilities',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TECHNOLOGY DEEP DIVE TAB
# ============================================================================
elif view_mode == "🔬 Technology Deep Dive":
    st.header("🔬 Technology Deep Dive")

    technology = st.selectbox(
        "Select Technology",
        ["Heat_Pump", "RE_PPA", "NCC-Electricity", "NCC-H2"]
    )

    tech_names = {
        'Heat_Pump': 'Industrial Heat Pump',
        'RE_PPA': 'Renewable Energy PPA',
        'NCC-Electricity': 'Electric Naphtha Cracker',
        'NCC-H2': 'Hydrogen Naphtha Cracker'
    }

    st.subheader(tech_names[technology])

    # Technology-specific data
    df_tech = data['macc'][data['macc']['technology'] == technology]
    df_cost_tech = data['cost_units'][data['cost_units']['Technology'] == technology]

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "2025 Cost",
            f"${df_tech[df_tech['year']==2025]['total_cost_usd_per_tco2'].values[0]:.0f}/tCO₂"
        )

    with col2:
        st.metric(
            "2050 Cost",
            f"${df_tech[df_tech['year']==2050]['total_cost_usd_per_tco2'].values[0]:.0f}/tCO₂",
            f"-{(1 - df_tech[df_tech['year']==2050]['total_cost_usd_per_tco2'].values[0] / df_tech[df_tech['year']==2025]['total_cost_usd_per_tco2'].values[0])*100:.0f}%"
        )

    with col3:
        st.metric(
            "2030 Abatement",
            f"{df_tech[df_tech['year']==2030]['abatement_potential_mtco2'].values[0]:.2f} Mt"
        )

    with col4:
        st.metric(
            "2050 Abatement",
            f"{df_tech[df_tech['year']==2050]['abatement_potential_mtco2'].values[0]:.2f} Mt"
        )

    # Cost breakdown over time
    st.subheader("Cost Breakdown Evolution")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_tech['year'],
        y=df_tech['capex_ann_usd_per_tco2'],
        name='CAPEX',
        stackgroup='one',
        fillcolor='#1f77b4'
    ))

    fig.add_trace(go.Scatter(
        x=df_tech['year'],
        y=df_tech['opex_ann_usd_per_tco2'],
        name='OPEX',
        stackgroup='one',
        fillcolor='#ff7f0e'
    ))

    fig.add_trace(go.Scatter(
        x=df_tech['year'],
        y=df_tech['fuel_cost_diff_usd_per_tco2'],
        name='Fuel Cost',
        stackgroup='one',
        fillcolor='#2ca02c'
    ))

    fig.update_layout(
        title=f'{tech_names[technology]} - Cost Component Evolution',
        xaxis_title='Year',
        yaxis_title='Cost ($/tCO₂)',
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Multi-unit cost evolution
    st.subheader("Multi-Unit Cost Comparison")

    units = ['Cost ($/tCO2)', 'Cost ($/ton ethylene)', 'Cost (₩/ton ethylene)', 'Cost ($/boe)']
    selected_units = st.multiselect("Select units to compare", units, default=units[:2])

    fig = go.Figure()

    for unit in selected_units:
        fig.add_trace(go.Scatter(
            x=df_cost_tech['Year'],
            y=df_cost_tech[unit],
            name=unit,
            mode='lines+markers',
            line=dict(width=3),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title=f'{tech_names[technology]} - Cost in Multiple Units',
        xaxis_title='Year',
        yaxis_title='Cost',
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>Korean Petrochemical Industry MACC Model v2.0 | Energy-Based Methodology</p>
    <p>📁 Data updated: 2025-10-19 | 🔬 Model: PLANiT Institute</p>
</div>
""", unsafe_allow_html=True)
