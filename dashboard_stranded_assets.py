"""
Streamlit Dashboard for Stranded Asset Analysis
Simplified Emission-Path Driven Model

Focus: Pure retirement-based stranding from emission constraints
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path


# Page config
st.set_page_config(
    page_title="Stranded Asset Analysis",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .subtitle {
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load all stranded asset data"""
    data = {}

    base_dir = Path('outputs/module_04_stranded_assets_simple')

    try:
        # Load main files
        data['book_values'] = pd.read_csv(base_dir / 'facility_book_values.csv')
        data['summary_timeline'] = pd.read_csv(base_dir / 'stranding_summary_timeline.csv')
        data['summary_2050'] = pd.read_csv(base_dir / 'stranding_summary_2050.csv')

        # Load facility-level retirement details
        facility_files = list(base_dir.glob('facility_retirement_*.csv'))
        data['facility_details'] = {}
        for file in facility_files:
            scenario_name = file.stem.replace('facility_retirement_', '')
            data['facility_details'][scenario_name] = pd.read_csv(file)

        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def display_overview(data):
    """Display overview section"""
    st.markdown('<div class="main-header">🏭 Stranded Asset Analysis Dashboard</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Emission-Path Driven Retirement Model</div>',
                unsafe_allow_html=True)

    st.markdown("---")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    df_assets = data['book_values']
    df_2050 = data['summary_2050']

    total_book_value = df_assets['book_value_musd'].sum() / 1000  # Billion
    total_facilities = len(df_assets)
    avg_stranding = df_2050['stranded_book_value_billion'].mean()
    max_retired = df_2050['facilities_retired'].max()

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Book Value", f"${total_book_value:.1f}B")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Facilities", f"{total_facilities}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Avg Stranded (2050)", f"${avg_stranding:.1f}B")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Max Facilities Retired", f"{max_retired:.0f}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Methodology explanation
    with st.expander("ℹ️ Methodology", expanded=False):
        st.markdown("""
        ### Emission-Path Driven Retirement Model

        **Core Logic:**
        1. **Emission Target**: Each scenario has specific emission reduction targets (2030, 2040, 2050)
        2. **Retirement Decision**: If a facility must reduce emissions by >90%, it retires instead
        3. **Stranded Asset**: Book value of retired facilities = Stranded Asset Value

        **Assumptions:**
        - Facility lifetime: 30 years
        - Depreciation: Straight-line
        - Retirement threshold: 90% emission reduction required
        - No retrofit costs or operational losses included

        **Book Value Calculation:**
        ```
        Book Value = Initial CAPEX × (Remaining Life / Total Lifetime)
        ```

        **Capital Intensity (Million USD per kt capacity):**
        - Naphtha Cracker: $1.2M/kt
        - Aromatics: $0.8M/kt
        - Polymer: $0.6M/kt
        - Other: $0.4M/kt
        """)


def display_timeline_analysis(data):
    """Display stranding timeline"""
    st.header("📈 Stranded Assets Over Time")

    df_timeline = data['summary_timeline']

    # Timeline chart
    fig = go.Figure()

    scenarios = df_timeline['scenario'].unique()
    colors = px.colors.qualitative.Set2

    for i, scenario in enumerate(scenarios):
        df_scenario = df_timeline[df_timeline['scenario'] == scenario]

        # Extract scenario label (last two parts)
        label = ' + '.join(scenario.split('_')[-2:]).upper()

        fig.add_trace(go.Scatter(
            x=df_scenario['year'],
            y=df_scenario['stranded_book_value_billion'],
            mode='lines+markers',
            name=label,
            line=dict(width=3, color=colors[i % len(colors)]),
            marker=dict(size=10, color=colors[i % len(colors)]),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Year: %{x}<br>' +
                         'Stranded: $%{y:.2f}B<extra></extra>'
        ))

    fig.update_layout(
        title="Stranded Book Value by Scenario (2030-2050)",
        xaxis_title="Year",
        yaxis_title="Stranded Book Value (Billion USD)",
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Show data table
    with st.expander("📊 View Timeline Data", expanded=False):
        st.dataframe(df_timeline, use_container_width=True)


def display_scenario_comparison(data):
    """Display scenario comparison for 2050"""
    st.header("⚖️ Scenario Comparison (2050)")

    df_2050 = data['summary_2050']

    col1, col2 = st.columns(2)

    with col1:
        # Stranded value comparison
        fig = go.Figure()

        scenario_labels = [' + '.join(s.split('_')[-2:]).upper()
                          for s in df_2050['scenario']]

        fig.add_trace(go.Bar(
            x=scenario_labels,
            y=df_2050['stranded_book_value_billion'],
            marker_color='indianred',
            text=df_2050['stranded_book_value_billion'].round(2),
            textposition='outside',
            texttemplate='$%{text}B',
            hovertemplate='<b>%{x}</b><br>Stranded: $%{y:.2f}B<extra></extra>'
        ))

        fig.update_layout(
            title="Stranded Book Value by Scenario",
            yaxis_title="Stranded Assets (Billion USD)",
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Facilities retired comparison
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=scenario_labels,
            y=df_2050['facilities_retired'],
            marker_color='steelblue',
            text=df_2050['facilities_retired'].astype(int),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Retired: %{y}<extra></extra>'
        ))

        fig.update_layout(
            title="Facilities Forced to Retire",
            yaxis_title="Number of Facilities",
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    # Stranding rate
    total_book_value = data['book_values']['book_value_musd'].sum() / 1000
    df_2050['stranding_rate_pct'] = (df_2050['stranded_book_value_billion'] / total_book_value) * 100

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=scenario_labels,
        y=df_2050['stranding_rate_pct'],
        marker_color='darkorange',
        text=df_2050['stranding_rate_pct'].round(1),
        textposition='outside',
        texttemplate='%{text}%',
        hovertemplate='<b>%{x}</b><br>Stranding Rate: %{y:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        title=f"Asset Stranding Rate (Total Book Value: ${total_book_value:.1f}B)",
        yaxis_title="Stranding Rate (%)",
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Summary table
    st.subheader("📋 Summary Table")

    display_df = df_2050[[
        'scenario', 'target_emissions_mt', 'required_reduction_pct',
        'facilities_retired', 'stranded_book_value_billion',
        'retired_capacity_kt', 'retired_emissions_mt'
    ]].copy()

    display_df['scenario'] = display_df['scenario'].apply(
        lambda x: ' + '.join(x.split('_')[-2:]).upper()
    )

    display_df.columns = [
        'Scenario', 'Target (MtCO2)', 'Reduction (%)',
        'Retired Facilities', 'Stranded ($B)',
        'Retired Cap. (kt)', 'Retired Emis. (Mt)'
    ]

    st.dataframe(
        display_df.style.format({
            'Target (MtCO2)': '{:.1f}',
            'Reduction (%)': '{:.1f}',
            'Retired Facilities': '{:.0f}',
            'Stranded ($B)': '${:.2f}',
            'Retired Cap. (kt)': '{:.0f}',
            'Retired Emis. (Mt)': '{:.1f}'
        }),
        use_container_width=True
    )


def display_facility_analysis(data):
    """Display facility-level analysis"""
    st.header("🏭 Facility-Level Retirement Analysis")

    # Scenario selector
    facility_details = data['facility_details']
    scenario_options = list(facility_details.keys())

    if not scenario_options:
        st.warning("No facility-level data available")
        return

    selected_scenario = st.selectbox(
        "Select Scenario:",
        scenario_options,
        format_func=lambda x: ' + '.join(x.split('_')[-2:]).upper()
    )

    df_facilities = facility_details[selected_scenario]

    # Summary stats
    col1, col2, col3, col4 = st.columns(4)

    n_retired = df_facilities['must_retire'].sum()
    stranded_value = df_facilities['stranded_book_value_musd'].sum() / 1000
    retired_capacity = df_facilities[df_facilities['must_retire']]['capacity_kt'].sum()
    retired_emissions = df_facilities[df_facilities['must_retire']]['emissions_year_kt'].sum() / 1000

    col1.metric("Facilities Retired", f"{n_retired}")
    col2.metric("Stranded Value", f"${stranded_value:.2f}B")
    col3.metric("Retired Capacity", f"{retired_capacity:.0f} kt")
    col4.metric("Retired Emissions", f"{retired_emissions:.1f} Mt")

    st.markdown("---")

    # Visualizations
    col1, col2 = st.columns(2)

    with col1:
        # Retirement by product group
        retired_by_group = df_facilities[df_facilities['must_retire']].groupby('product_group').agg({
            'must_retire': 'count',
            'stranded_book_value_musd': 'sum'
        }).reset_index()
        retired_by_group.columns = ['product_group', 'n_retired', 'stranded_musd']
        retired_by_group['stranded_billion'] = retired_by_group['stranded_musd'] / 1000

        fig = px.bar(
            retired_by_group,
            x='product_group',
            y='n_retired',
            title="Retired Facilities by Product Group",
            labels={'product_group': 'Product Group', 'n_retired': 'Facilities Retired'},
            color='n_retired',
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Retirement by location
        retired_by_loc = df_facilities[df_facilities['must_retire']].groupby('location').agg({
            'must_retire': 'count',
            'stranded_book_value_musd': 'sum'
        }).reset_index()
        retired_by_loc.columns = ['location', 'n_retired', 'stranded_musd']
        retired_by_loc['stranded_billion'] = retired_by_loc['stranded_musd'] / 1000
        retired_by_loc = retired_by_loc.sort_values('n_retired', ascending=True).tail(10)

        fig = px.bar(
            retired_by_loc,
            x='n_retired',
            y='location',
            orientation='h',
            title="Retired Facilities by Location (Top 10)",
            labels={'location': 'Location', 'n_retired': 'Facilities Retired'},
            color='n_retired',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Detailed facility table
    st.subheader("📋 Retired Facilities Detail")

    retired_facilities = df_facilities[df_facilities['must_retire']].copy()

    if len(retired_facilities) > 0:
        display_cols = [
            'company', 'location', 'product', 'product_group',
            'capacity_kt', 'year_built', 'facility_age',
            'book_value_musd', 'emission_intensity',
            'required_reduction_pct', 'stranded_book_value_musd'
        ]

        retired_facilities_display = retired_facilities[display_cols].copy()
        retired_facilities_display.columns = [
            'Company', 'Location', 'Product', 'Group',
            'Capacity (kt)', 'Year Built', 'Age (years)',
            'Book Value ($M)', 'Emis. Intensity (tCO2/kt)',
            'Required Reduction (%)', 'Stranded ($M)'
        ]

        st.dataframe(
            retired_facilities_display.style.format({
                'Capacity (kt)': '{:.0f}',
                'Age (years)': '{:.0f}',
                'Book Value ($M)': '${:.1f}',
                'Emis. Intensity (tCO2/kt)': '{:.2f}',
                'Required Reduction (%)': '{:.1f}',
                'Stranded ($M)': '${:.1f}'
            }),
            use_container_width=True,
            height=400
        )

        # Download button
        csv = retired_facilities_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Retired Facilities CSV",
            data=csv,
            file_name=f"retired_facilities_{selected_scenario}.csv",
            mime="text/csv"
        )
    else:
        st.info("No facilities retired in this scenario")


def display_asset_distribution(data):
    """Display book value distribution analysis"""
    st.header("💰 Asset Distribution Analysis")

    df_assets = data['book_values']

    col1, col2 = st.columns(2)

    with col1:
        # Book value by product group
        by_group = df_assets.groupby('product_group').agg({
            'book_value_musd': 'sum',
            'capacity_kt': 'sum'
        }).reset_index()
        by_group['book_value_billion'] = by_group['book_value_musd'] / 1000
        by_group = by_group.sort_values('book_value_billion', ascending=False)

        fig = px.pie(
            by_group,
            values='book_value_billion',
            names='product_group',
            title="Book Value Distribution by Product Group",
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Book value by location
        by_location = df_assets.groupby('location').agg({
            'book_value_musd': 'sum',
            'capacity_kt': 'sum'
        }).reset_index()
        by_location['book_value_billion'] = by_location['book_value_musd'] / 1000
        by_location = by_location.sort_values('book_value_billion', ascending=False).head(10)

        fig = px.bar(
            by_location,
            x='book_value_billion',
            y='location',
            orientation='h',
            title="Book Value by Location (Top 10)",
            labels={'location': 'Location', 'book_value_billion': 'Book Value ($B)'},
            color='book_value_billion',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Age distribution
    st.subheader("📊 Facility Age and Book Value")

    fig = px.scatter(
        df_assets,
        x='facility_age',
        y='book_value_musd',
        size='capacity_kt',
        color='product_group',
        hover_data=['company', 'location', 'product'],
        title="Facility Age vs Book Value (size = capacity)",
        labels={
            'facility_age': 'Facility Age (years)',
            'book_value_musd': 'Book Value (Million USD)',
            'product_group': 'Product Group'
        }
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)


def main():
    """Main dashboard function"""

    # Load data
    data = load_data()

    if data is None:
        st.error("Failed to load data. Please ensure stranded asset analysis has been run.")
        st.info("Run: `python run_stranded_assets_simple.py`")
        return

    # Sidebar
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio(
        "Select Page:",
        ["Overview", "Timeline Analysis", "Scenario Comparison",
         "Facility Analysis", "Asset Distribution"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Model Information")
    st.sidebar.info("""
    **Stranded Asset Model**

    Emission-path driven retirement:
    - Threshold: 90% reduction
    - Pure retirement logic
    - No retrofit/carbon price

    **Book Value Calculation:**
    - 30-year lifetime
    - Straight-line depreciation
    """)

    # Display selected page
    display_overview(data)

    if page == "Overview":
        pass  # Already displayed
    elif page == "Timeline Analysis":
        display_timeline_analysis(data)
    elif page == "Scenario Comparison":
        display_scenario_comparison(data)
    elif page == "Facility Analysis":
        display_facility_analysis(data)
    elif page == "Asset Distribution":
        display_asset_distribution(data)


if __name__ == "__main__":
    main()
