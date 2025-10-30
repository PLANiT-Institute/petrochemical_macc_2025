"""
한국 석유화학 MACC 분석 - 3개 생산 시나리오 대시보드
Korean Petrochemical MACC Analysis - 3 Production Scenarios Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Korean Petrochemical Scenarios",
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
    .scenario-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_scenario_data():
    """Load scenario comparison data"""
    try:
        # Scenario summary
        df_summary = pd.read_csv('outputs/scenarios_comparison/summary.csv')

        # Individual scenario MACC data
        scenarios = {
            'shaheen': pd.read_csv('outputs/scenarios_shaheen/module_02_macc/macc_annual_2025_2050.csv'),
            'restructure_25pct': pd.read_csv('outputs/scenarios_restructure_25pct/module_02_macc/macc_annual_2025_2050.csv'),
            'restructure_40pct': pd.read_csv('outputs/scenarios_restructure_40pct/module_02_macc/macc_annual_2025_2050.csv'),
        }

        # BAU trajectories
        bau = {
            'shaheen': pd.read_csv('outputs/scenarios_shaheen/module_01_baseline/bau_trajectory_2025_2050.csv'),
            'restructure_25pct': pd.read_csv('outputs/scenarios_restructure_25pct/module_01_baseline/bau_trajectory_2025_2050.csv'),
            'restructure_40pct': pd.read_csv('outputs/scenarios_restructure_40pct/module_01_baseline/bau_trajectory_2025_2050.csv'),
        }

        return df_summary, scenarios, bau
    except Exception as e:
        st.error(f"데이터 로딩 오류 / Error loading data: {e}")
        return None, None, None

df_summary, scenario_macc, scenario_bau = load_scenario_data()

if df_summary is None:
    st.error("Failed to load scenario data. Please run scenarios first.")
    st.stop()

# Main header
st.markdown('<div class="main-header">🏭 한국 석유화학 산업 탈탄소화 시나리오</div>',
            unsafe_allow_html=True)
st.markdown('<div style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Korean Petrochemical Industry Decarbonization Scenarios</div>',
            unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ 설정 / Settings")
view_mode = st.sidebar.radio(
    "View / 보기 선택",
    ["📊 시나리오 비교 / Scenario Comparison", "📈 MACC 곡선 / MACC Curves", "💰 비용 분석 / Cost Analysis", "🔋 전력 모델 / Electricity Model"]
)

# ============================================================================
# SCENARIO COMPARISON
# ============================================================================
if view_mode == "📊 시나리오 비교 / Scenario Comparison":
    st.header("📊 3개 생산 시나리오 비교")
    st.markdown("### 2050년 결과 비교 / 2050 Results Comparison")

    # Key metrics
    col1, col2, col3 = st.columns(3)

    scenarios_list = [
        {"name": "Shaheen (성장)", "key": "shaheen", "color": "#1f77b4"},
        {"name": "구조조정 25%", "key": "restructure_25pct", "color": "#ff7f0e"},
        {"name": "구조조정 40%", "key": "restructure_40pct", "color": "#2ca02c"}
    ]

    for col, scenario in zip([col1, col2, col3], scenarios_list):
        row = df_summary[df_summary['scenario_key'] == scenario['key']].iloc[0]

        with col:
            st.markdown(f'<div class="scenario-card">', unsafe_allow_html=True)
            st.markdown(f"### {scenario['name']}")
            st.metric("BAU 배출량 (2050)", f"{row['bau_emissions_2050_mt']:.1f} MtCO₂")
            st.metric("실제 배출량 (2050)", f"{row['emissions_2050_mt']:.1f} MtCO₂")
            st.metric("누적 비용", f"${row['cost_2050_billion_usd']:.1f}B")
            st.markdown("---")
            st.markdown("**기술 배치 / Technology Deployment (2050)**")
            st.write(f"• NCC-H₂: {row['ncc_h2_mt']:.1f} Mt")
            st.write(f"• RE PPA: {row['re_ppa_mt']:.1f} Mt")
            st.write(f"• Heat Pump: {row['heat_pump_mt']:.1f} Mt")
            st.write(f"• H₂ 소비량: {row['h2_consumption_kt']:.0f} kt/yr")
            st.markdown('</div>', unsafe_allow_html=True)

    # BAU Trajectory Comparison
    st.markdown("---")
    st.markdown("### BAU 배출량 전망 비교 / BAU Emissions Trajectory Comparison")

    fig_bau = go.Figure()

    for scenario in scenarios_list:
        df_bau = scenario_bau[scenario['key']]
        fig_bau.add_trace(go.Scatter(
            x=df_bau['year'],
            y=df_bau['total_emissions_mtco2'],
            mode='lines+markers',
            name=scenario['name'],
            line=dict(color=scenario['color'], width=3),
            marker=dict(size=6)
        ))

    fig_bau.update_layout(
        title="BAU 배출량 전망 (2025-2050)",
        xaxis_title="연도 / Year",
        yaxis_title="배출량 / Emissions (MtCO₂/year)",
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )

    st.plotly_chart(fig_bau, use_container_width=True)

    # Cost Comparison
    st.markdown("---")
    st.markdown("### 비용 비교 / Cost Comparison (2050)")

    fig_cost = go.Figure()

    fig_cost.add_trace(go.Bar(
        x=[s['name'] for s in scenarios_list],
        y=[df_summary[df_summary['scenario_key'] == s['key']]['cost_2050_billion_usd'].iloc[0] for s in scenarios_list],
        marker_color=[s['color'] for s in scenarios_list],
        text=[f"${df_summary[df_summary['scenario_key'] == s['key']]['cost_2050_billion_usd'].iloc[0]:.1f}B" for s in scenarios_list],
        textposition='outside'
    ))

    fig_cost.update_layout(
        title="2050년 누적 비용 / 2050 Cumulative Cost",
        yaxis_title="비용 / Cost (Billion USD)",
        height=400,
        template='plotly_white'
    )

    st.plotly_chart(fig_cost, use_container_width=True)

# ============================================================================
# MACC CURVES
# ============================================================================
elif view_mode == "📈 MACC 곡선 / MACC Curves":
    st.header("📈 MACC 곡선 (Marginal Abatement Cost Curves)")

    # Select scenario
    scenario_names = {
        'shaheen': 'Shaheen (성장)',
        'restructure_25pct': '구조조정 25%',
        'restructure_40pct': '구조조정 40%'
    }

    selected_scenario_key = st.selectbox(
        "시나리오 선택 / Select Scenario",
        list(scenario_names.keys()),
        format_func=lambda x: scenario_names[x]
    )

    # Select year
    year = st.slider("연도 선택 / Select Year", 2025, 2050, 2030, 5)

    # Filter data
    df_macc = scenario_macc[selected_scenario_key]
    df_year = df_macc[df_macc['year'] == year].copy()

    # Sort by MACC cost
    df_year = df_year.sort_values('total_cost_usd_per_tco2')
    df_year['cumulative_abatement'] = df_year['abatement_potential_mtco2'].cumsum()

    # Create MACC curve
    fig_macc = go.Figure()

    # Color map for technologies
    tech_colors = {
        'NCC-H2': '#2ca02c',
        'NCC-Electricity': '#1f77b4',
        'Heat_Pump': '#ff7f0e',
        'RE_PPA': '#9467bd'
    }

    for idx, row in df_year.iterrows():
        x_start = row['cumulative_abatement'] - row['abatement_potential_mtco2']
        x_end = row['cumulative_abatement']

        fig_macc.add_trace(go.Scatter(
            x=[x_start, x_end, x_end, x_start, x_start],
            y=[0, 0, row['total_cost_usd_per_tco2'], row['total_cost_usd_per_tco2'], 0],
            fill='toself',
            fillcolor=tech_colors.get(row['technology'], '#gray'),
            line=dict(color='white', width=1),
            name=row['technology'],
            hovertemplate=f"<b>{row['technology']}</b><br>" +
                         f"MACC: ${row['total_cost_usd_per_tco2']:.2f}/tCO₂<br>" +
                         f"Abatement: {row['abatement_potential_mtco2']:.2f} MtCO₂<br>" +
                         "<extra></extra>",
            showlegend=True
        ))

    fig_macc.update_layout(
        title=f"MACC Curve - {scenario_names[selected_scenario_key]} ({year})",
        xaxis_title="누적 감축량 / Cumulative Abatement (MtCO₂/year)",
        yaxis_title="한계 감축 비용 / Marginal Abatement Cost (USD/tCO₂)",
        hovermode='closest',
        height=600,
        template='plotly_white'
    )

    st.plotly_chart(fig_macc, use_container_width=True)

    # Technology details table
    st.markdown("### 기술별 상세 정보 / Technology Details")

    display_cols = ['technology', 'abatement_potential_mtco2', 'total_cost_usd_per_tco2',
                    'capex_ann_usd_per_tco2', 'opex_ann_usd_per_tco2', 'fuel_cost_diff_usd_per_tco2']

    if all(col in df_year.columns for col in display_cols):
        st.dataframe(
            df_year[display_cols].round(2),
            use_container_width=True,
            hide_index=True
        )

# ============================================================================
# COST ANALYSIS
# ============================================================================
elif view_mode == "💰 비용 분석 / Cost Analysis":
    st.header("💰 비용 분석 (Cost Analysis)")

    # Select scenario
    scenario_names = {
        'shaheen': 'Shaheen (성장)',
        'restructure_25pct': '구조조정 25%',
        'restructure_40pct': '구조조정 40%'
    }

    selected_scenario_key = st.selectbox(
        "시나리오 선택 / Select Scenario",
        list(scenario_names.keys()),
        format_func=lambda x: scenario_names[x]
    )

    df_macc = scenario_macc[selected_scenario_key]

    # Cost evolution over time by technology
    st.markdown("### 기술별 MACC 비용 추이 / MACC Cost Evolution by Technology")

    fig_cost_evolution = go.Figure()

    tech_colors = {
        'NCC-H2': '#2ca02c',
        'NCC-Electricity': '#1f77b4',
        'Heat_Pump': '#ff7f0e',
        'RE_PPA': '#9467bd'
    }

    for tech in df_macc['technology'].unique():
        df_tech = df_macc[df_macc['technology'] == tech]
        fig_cost_evolution.add_trace(go.Scatter(
            x=df_tech['year'],
            y=df_tech['total_cost_usd_per_tco2'],
            mode='lines+markers',
            name=tech,
            line=dict(color=tech_colors.get(tech, '#gray'), width=3),
            marker=dict(size=8)
        ))

    fig_cost_evolution.update_layout(
        xaxis_title="연도 / Year",
        yaxis_title="MACC 비용 / MACC Cost (USD/tCO₂)",
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )

    st.plotly_chart(fig_cost_evolution, use_container_width=True)

    # Abatement potential evolution
    st.markdown("### 기술별 감축 잠재력 추이 / Abatement Potential Evolution")

    fig_abatement = go.Figure()

    for tech in df_macc['technology'].unique():
        df_tech = df_macc[df_macc['technology'] == tech]
        fig_abatement.add_trace(go.Scatter(
            x=df_tech['year'],
            y=df_tech['abatement_potential_mtco2'],
            mode='lines+markers',
            name=tech,
            line=dict(color=tech_colors.get(tech, '#gray'), width=3),
            marker=dict(size=8),
            stackgroup='one'
        ))

    fig_abatement.update_layout(
        xaxis_title="연도 / Year",
        yaxis_title="감축 잠재력 / Abatement Potential (MtCO₂/year)",
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )

    st.plotly_chart(fig_abatement, use_container_width=True)

# ============================================================================
# ELECTRICITY MODEL
# ============================================================================
elif view_mode == "🔋 전력 모델 / Electricity Model":
    st.header("🔋 전력 모델 (Electricity Model)")

    st.markdown("""
    ### 전력 모델 개요 / Electricity Model Overview

    **2가지 전력 유형 / Two Types of Electricity:**

    1. **계통 전력 (Grid Electricity)**
       - 가격: $80-100/MWh (한국 산업용 전력 요금)
       - 배출계수: 0.436 → 0.070 tCO₂/MWh (2025 → 2050)
       - 출처: 한국전력거래소 요금 구조
       - 적용: NCC-Electricity, Heat Pump이 기본적으로 사용

    2. **재생에너지 (Renewable Electricity)**
       - 가격: $129-191/MWh (PPA 계약)
       - 배출계수: 0.0 tCO₂/MWh (탄소 중립)
       - 출처: Excel assumption 데이터
       - 적용: RE_PPA 기술로 Grid → RE 전환 가능

    **중요 변경사항 / Key Changes:**
    - NCC-Electricity: 계통 전력 사용 (이전: 재생에너지로 잘못 설정)
    - Grid EF: 현실적 감소 경로 (이전: 2050년 0으로 잘못 설정)
    - 모든 전력 비용 및 배출량 계산 수정 완료
    """)

    # Load price trajectories
    df_grid_price = pd.read_csv('data/grid_price_trajectory.csv')
    df_re_price = pd.read_csv('data/re_price_trajectory.csv')
    df_grid_ef = pd.read_csv('data/grid_emission_trajectory.csv')

    # Price comparison
    st.markdown("### 전력 가격 비교 / Electricity Price Comparison")

    fig_price = go.Figure()

    fig_price.add_trace(go.Scatter(
        x=df_grid_price['year'],
        y=df_grid_price['grid_price_usd_per_mwh'],
        mode='lines+markers',
        name='Grid Electricity',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))

    fig_price.add_trace(go.Scatter(
        x=df_re_price['year'],
        y=df_re_price['re_price_usd_per_mwh'],
        mode='lines+markers',
        name='Renewable Electricity',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=8)
    ))

    fig_price.update_layout(
        xaxis_title="연도 / Year",
        yaxis_title="전력 가격 / Electricity Price (USD/MWh)",
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )

    st.plotly_chart(fig_price, use_container_width=True)

    # Emission factor
    st.markdown("### 계통 전력 배출계수 / Grid Electricity Emission Factor")

    fig_ef = go.Figure()

    fig_ef.add_trace(go.Scatter(
        x=df_grid_ef['year'],
        y=df_grid_ef['grid_ef_tco2_per_mwh'],
        mode='lines+markers',
        name='Grid EF',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(255, 127, 14, 0.2)'
    ))

    fig_ef.update_layout(
        xaxis_title="연도 / Year",
        yaxis_title="배출계수 / Emission Factor (tCO₂/MWh)",
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )

    st.plotly_chart(fig_ef, use_container_width=True)

    # Key milestones
    st.markdown("### 주요 시점 / Key Milestones")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**2025 (현재 / Current)**")
        st.write(f"• Grid: ${df_grid_price[df_grid_price['year']==2025]['grid_price_usd_per_mwh'].iloc[0]:.0f}/MWh")
        st.write(f"• RE: ${df_re_price[df_re_price['year']==2025]['re_price_usd_per_mwh'].iloc[0]:.2f}/MWh")
        st.write(f"• Grid EF: {df_grid_ef[df_grid_ef['year']==2025]['grid_ef_tco2_per_mwh'].iloc[0]:.3f} tCO₂/MWh")

    with col2:
        st.markdown("**2050 (목표 / Target)**")
        st.write(f"• Grid: ${df_grid_price[df_grid_price['year']==2050]['grid_price_usd_per_mwh'].iloc[0]:.0f}/MWh")
        st.write(f"• RE: ${df_re_price[df_re_price['year']==2050]['re_price_usd_per_mwh'].iloc[0]:.2f}/MWh")
        st.write(f"• Grid EF: {df_grid_ef[df_grid_ef['year']==2050]['grid_ef_tco2_per_mwh'].iloc[0]:.3f} tCO₂/MWh")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    🏭 한국 석유화학 산업 탈탄소화 MACC 분석<br>
    Korean Petrochemical Industry Decarbonization MACC Analysis<br>
    Updated with corrected electricity model (Grid + Renewable)
</div>
""", unsafe_allow_html=True)
