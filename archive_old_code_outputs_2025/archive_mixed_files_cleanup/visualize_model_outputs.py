#!/usr/bin/env python3
"""
Comprehensive Visualization of Model Outputs
Visualize outputs from all three models: BAU, MACC, and Cost Optimization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

def load_and_visualize_model_outputs():
    """Load and visualize outputs from all three models"""

    output_dir = Path("organized_analysis/outputs")
    viz_dir = Path("model_output_visualizations")
    viz_dir.mkdir(exist_ok=True)

    # Set style
    plt.style.use('default')
    sns.set_palette("husl")

    print("🎨 CREATING COMPREHENSIVE MODEL OUTPUT VISUALIZATIONS")
    print("=" * 80)

    # ================================
    # MODEL 1: BAU EMISSION ANALYSIS
    # ================================
    print("\n📊 MODEL 1: BAU EMISSION ANALYSIS VISUALIZATION")

    try:
        # Load BAU data
        bau_summary = pd.read_csv(output_dir / "bau_pathway_summary_with_growth.csv")
        bau_detailed = pd.read_csv(output_dir / "bau_detailed_pathways_with_growth.csv")
        growth_comparison = pd.read_csv(output_dir / "growth_scenario_comparison_50yr.csv")

        # Create BAU visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('MODEL 1: BAU Emission Analysis Outputs', fontsize=16, fontweight='bold')

        # 1. Growth scenario comparison
        ax1 = axes[0,0]
        for col in ['+0.2% Growth_mtco2', 'Zero Growth_mtco2', '-0.2% Growth_mtco2']:
            if col in growth_comparison.columns:
                ax1.plot(growth_comparison['year'], growth_comparison[col],
                        label=col.replace('_mtco2', ''), linewidth=2, marker='o', markersize=3)
        ax1.set_title('BAU Emission Pathways by Growth Scenario (50-yr lifetime)')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Emissions (MtCO₂)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Facility lifetime comparison
        ax2 = axes[0,1]
        lifetime_data = bau_summary[bau_summary['growth_scenario'] == 'Zero Growth']
        lifetimes = lifetime_data['facility_lifetime'].values
        final_emissions = lifetime_data['final_2050_mtco2'].values
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        bars = ax2.bar(lifetimes, final_emissions, color=colors, alpha=0.7, width=5)
        ax2.set_title('2050 Final Emissions by Facility Lifetime')
        ax2.set_xlabel('Facility Lifetime (years)')
        ax2.set_ylabel('2050 Emissions (MtCO₂)')
        ax2.grid(True, alpha=0.3)
        # Add value labels
        for bar, emission in zip(bars, final_emissions):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{emission:.1f}', ha='center', va='bottom', fontweight='bold')

        # 3. Reduction percentages
        ax3 = axes[1,0]
        scenarios = bau_summary['growth_scenario'].unique()
        scenario_colors = {'Zero Growth': '#2C3E50', '+0.2% Growth': '#E74C3C', '-0.2% Growth': '#27AE60'}

        for scenario in scenarios:
            scenario_data = bau_summary[bau_summary['growth_scenario'] == scenario]
            ax3.plot(scenario_data['facility_lifetime'], scenario_data['reduction_percentage'],
                    marker='o', linewidth=2, label=scenario, color=scenario_colors.get(scenario, 'gray'))

        ax3.set_title('Emission Reduction % by 2050')
        ax3.set_xlabel('Facility Lifetime (years)')
        ax3.set_ylabel('Reduction from 2025 (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. Baseline vs targets
        ax4 = axes[1,1]
        baseline_2025 = bau_summary['baseline_2025_mtco2'].iloc[0]
        target_52mt = 52.0

        scenarios_plot = ['Current Baseline', 'Required Target']
        values_plot = [baseline_2025, target_52mt]
        colors_plot = ['#E74C3C', '#27AE60']

        bars = ax4.bar(scenarios_plot, values_plot, color=colors_plot, alpha=0.7)
        ax4.set_title('Baseline Calibration Issue')
        ax4.set_ylabel('Emissions (MtCO₂)')
        ax4.axhline(y=52, color='red', linestyle='--', alpha=0.7, label='Required: 52 MtCO₂')

        # Add value labels
        for bar, value in zip(bars, values_plot):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{value:.1f}', ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        plt.savefig(viz_dir / "model_1_bau_analysis.png", dpi=300, bbox_inches='tight')
        print(f"   ✅ Saved: {viz_dir}/model_1_bau_analysis.png")

        # BAU Summary Stats
        print(f"\n   📊 BAU MODEL SUMMARY:")
        print(f"      Baseline 2025: {baseline_2025:.1f} MtCO₂")
        print(f"      Required target: 52.0 MtCO₂")
        print(f"      Calibration gap: {((baseline_2025-52)/52*100):+.1f}%")
        print(f"      Scenarios analyzed: {len(bau_summary)}")

    except Exception as e:
        print(f"   ❌ Error visualizing BAU data: {e}")

    # ================================
    # MODEL 2: MACC ANALYSIS
    # ================================
    print("\n💰 MODEL 2: MACC ANALYSIS VISUALIZATION")

    try:
        # Load MACC data
        macc_2030 = pd.read_csv(output_dir / "macc_curve_2030.csv")
        macc_2040 = pd.read_csv(output_dir / "macc_curve_2040.csv")
        macc_2050 = pd.read_csv(output_dir / "macc_curve_2050.csv")
        fuel_costs = pd.read_csv(output_dir / "fuel_cost_projections.csv")

        # Create MACC visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('MODEL 2: MACC Analysis Outputs', fontsize=16, fontweight='bold')

        # 1. MACC curves by year
        ax1 = axes[0,0]
        macc_data = {
            '2030': macc_2030,
            '2040': macc_2040,
            '2050': macc_2050
        }
        colors = {'2030': '#FF6B6B', '2040': '#4ECDC4', '2050': '#45B7D1'}

        for year, data in macc_data.items():
            if not data.empty:
                ax1.step(data['cumulative_abatement'], data['cost_per_tco2'],
                        where='post', label=year, linewidth=2, color=colors[year])

        ax1.set_title('MACC Curves by Year')
        ax1.set_xlabel('Cumulative Abatement (tCO₂)')
        ax1.set_ylabel('Cost ($/tCO₂)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Technology abatement potential
        ax2 = axes[0,1]
        # Use 2040 as representative
        if not macc_2040.empty:
            tech_abatement = macc_2040['abatement_deployed'] / 1e6  # Convert to Mt
            ax2.bar(range(len(macc_2040)), tech_abatement,
                   color=plt.cm.viridis(np.linspace(0, 1, len(macc_2040))))
            ax2.set_title('Technology Abatement Potential (2040)')
            ax2.set_xlabel('Technology Index')
            ax2.set_ylabel('Abatement (MtCO₂)')
            ax2.set_xticks(range(len(macc_2040)))
            ax2.set_xticklabels(macc_2040['technology'], rotation=45, ha='right')
            ax2.grid(True, alpha=0.3)

        # 3. Fuel cost evolution
        ax3 = axes[1,0]
        key_fuels = ['natural_gas', 'green_hydrogen', 'bio_naphtha', 'renewable_electricity']
        fuel_subset = fuel_costs[fuel_costs['fuel_type'].isin(key_fuels)]

        for fuel in key_fuels:
            fuel_data = fuel_subset[fuel_subset['fuel_type'] == fuel]
            if not fuel_data.empty:
                years = [2030, 2040, 2050]
                costs = []
                for year in years:
                    year_data = fuel_data[fuel_data['year'] == year]
                    if not year_data.empty:
                        costs.append(year_data['cost_usd_per_unit'].iloc[0])
                    else:
                        costs.append(None)

                # Filter out None values
                valid_data = [(y, c) for y, c in zip(years, costs) if c is not None]
                if valid_data:
                    valid_years, valid_costs = zip(*valid_data)
                    ax3.plot(valid_years, valid_costs, marker='o', linewidth=2,
                            label=fuel.replace('_', ' ').title())

        ax3.set_title('Fuel Cost Evolution')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Cost ($/unit)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. Carbon price trajectory
        ax4 = axes[1,1]
        carbon_data = fuel_costs[fuel_costs['fuel_type'] == 'carbon_price']
        if not carbon_data.empty:
            years = carbon_data['year'].values
            prices = carbon_data['cost_usd_per_unit'].values
            ax4.plot(years, prices, marker='o', linewidth=3, color='red', label='Carbon Price')
            ax4.set_title('Carbon Price Trajectory')
            ax4.set_xlabel('Year')
            ax4.set_ylabel('Price ($/tCO₂)')
            ax4.grid(True, alpha=0.3)

            # Add value labels
            for year, price in zip(years, prices):
                ax4.annotate(f'${price:.0f}', (year, price), textcoords="offset points",
                           xytext=(0,10), ha='center', fontweight='bold')

        plt.tight_layout()
        plt.savefig(viz_dir / "model_2_macc_analysis.png", dpi=300, bbox_inches='tight')
        print(f"   ✅ Saved: {viz_dir}/model_2_macc_analysis.png")

        # MACC Summary Stats
        print(f"\n   💰 MACC MODEL SUMMARY:")
        print(f"      Technologies analyzed: {len(macc_2030)}")
        print(f"      2030 max cost: ${macc_2030['cost_per_tco2'].max():.0f}/tCO₂")
        print(f"      2050 carbon price: ${carbon_data[carbon_data['year']==2050]['cost_usd_per_unit'].iloc[0]:.0f}/tCO₂")
        print(f"      Total 2040 abatement: {macc_2040['abatement_deployed'].sum()/1e6:.1f} MtCO₂")

    except Exception as e:
        print(f"   ❌ Error visualizing MACC data: {e}")

    # ================================
    # MODEL 3: COST OPTIMIZATION
    # ================================
    print("\n⚖️ MODEL 3: COST OPTIMIZATION VISUALIZATION")

    try:
        # Load optimization data
        optimal_deploy = pd.read_csv(output_dir / "optimal_technology_deployments.csv")
        facility_deprec = pd.read_csv(output_dir / "facility_depreciation_analysis.csv")
        cost_summary = pd.read_csv(output_dir / "cost_analysis_executive_summary.csv")

        # Create optimization visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('MODEL 3: Cost Optimization Outputs', fontsize=16, fontweight='bold')

        # 1. Technology deployment by target
        ax1 = axes[0,0]
        targets = optimal_deploy['emission_target_pct'].unique()
        technologies = optimal_deploy['technology'].unique()

        # Focus on 2040 data
        deploy_2040 = optimal_deploy[optimal_deploy['year'] == 2040]

        target_positions = np.arange(len(targets))
        tech_colors = plt.cm.tab10(np.linspace(0, 1, len(technologies)))

        bottom = np.zeros(len(targets))

        for i, tech in enumerate(technologies):
            tech_deploy = []
            for target in targets:
                target_data = deploy_2040[(deploy_2040['emission_target_pct'] == target) &
                                        (deploy_2040['technology'] == tech)]
                if not target_data.empty:
                    tech_deploy.append(target_data['deployment_fraction'].iloc[0])
                else:
                    tech_deploy.append(0)

            ax1.bar(target_positions, tech_deploy, bottom=bottom,
                   label=tech, color=tech_colors[i], alpha=0.8)
            bottom += tech_deploy

        ax1.set_title('Technology Deployment by Emission Target (2040)')
        ax1.set_xlabel('Emission Reduction Target (%)')
        ax1.set_ylabel('Deployment Fraction')
        ax1.set_xticks(target_positions)
        ax1.set_xticklabels([f'{int(t)}%' for t in targets])
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)

        # 2. Stranded assets analysis
        ax2 = axes[0,1]
        # Top companies by stranded assets
        top_stranded = facility_deprec.nlargest(10, 'stranded_cost_musd_per_year')

        bars = ax2.barh(range(len(top_stranded)), top_stranded['stranded_cost_musd_per_year'])
        ax2.set_title('Top 10 Facilities: Stranded Asset Cost')
        ax2.set_xlabel('Stranded Cost (M$/year)')
        ax2.set_yticks(range(len(top_stranded)))
        ax2.set_yticklabels([f"{row['company'][:15]}..." if len(row['company']) > 15 else row['company']
                           for _, row in top_stranded.iterrows()], fontsize=8)
        ax2.grid(True, alpha=0.3)

        # 3. Cost evolution by year and target
        ax3 = axes[1,0]
        years = optimal_deploy['year'].unique()

        for target in [25.0, 50.0, 75.0]:
            target_costs = []
            for year in sorted(years):
                year_target_data = optimal_deploy[(optimal_deploy['year'] == year) &
                                                (optimal_deploy['emission_target_pct'] == target)]
                if not year_target_data.empty:
                    avg_cost = year_target_data['technology_cost_usd_per_tco2'].mean()
                    target_costs.append(avg_cost)
                else:
                    target_costs.append(None)

            # Filter valid data
            valid_data = [(y, c) for y, c in zip(sorted(years), target_costs) if c is not None]
            if valid_data:
                valid_years, valid_costs = zip(*valid_data)
                ax3.plot(valid_years, valid_costs, marker='o', linewidth=2,
                        label=f'{int(target)}% Target')

        ax3.set_title('Average Technology Cost by Target')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Cost ($/tCO₂)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. Cost summary breakdown
        ax4 = axes[1,1]

        # Extract key metrics from cost summary
        cost_metrics = cost_summary.set_index('Metric')['Value'].to_dict()

        # Create a summary chart
        summary_data = {
            'NPV Cost': float(cost_metrics.get('Optimized Pathway Total NPV (Billion USD)', 0)),
            'Stranded Assets': float(cost_metrics.get('Stranded Assets NPV (Billion USD)', 0)),
            'Total Abatement': float(cost_metrics.get('Total Abatement 2025-2050 (Mt CO₂)', 0)) / 100  # Scale for display
        }

        bars = ax4.bar(summary_data.keys(), summary_data.values(),
                      color=['#FF6B6B', '#FFA726', '#66BB6A'])
        ax4.set_title('Optimization Summary')
        ax4.set_ylabel('Value (Scaled)')
        ax4.grid(True, alpha=0.3)

        # Add value labels
        for bar, (key, value) in zip(bars, summary_data.items()):
            height = bar.get_height()
            if 'Abatement' in key:
                label = f'{value*100:.0f} Mt'
            else:
                label = f'${value:.1f}B'
            ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   label, ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        plt.savefig(viz_dir / "model_3_cost_optimization.png", dpi=300, bbox_inches='tight')
        print(f"   ✅ Saved: {viz_dir}/model_3_cost_optimization.png")

        # Optimization Summary Stats
        print(f"\n   ⚖️ OPTIMIZATION MODEL SUMMARY:")
        print(f"      Total NPV: ${float(cost_metrics.get('Optimized Pathway Total NPV (Billion USD)', 0)):.1f}B")
        print(f"      Cost reduction vs BAU: {cost_metrics.get('Cost Reduction vs BAU (%)', 'N/A')}")
        print(f"      Stranded assets: ${float(cost_metrics.get('Stranded Assets NPV (Billion USD)', 0)):.1f}B")
        print(f"      Total abatement: {float(cost_metrics.get('Total Abatement 2025-2050 (Mt CO₂)', 0)):.1f} MtCO₂")

    except Exception as e:
        print(f"   ❌ Error visualizing optimization data: {e}")

    # ================================
    # COMPREHENSIVE COMPARISON
    # ================================
    print("\n🔍 CREATING COMPREHENSIVE MODEL COMPARISON")

    try:
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('COMPREHENSIVE MODEL OUTPUT COMPARISON', fontsize=16, fontweight='bold')

        # 1. Baseline comparison
        ax1 = axes[0,0]
        baselines = {
            'Model 1 (BAU)': baseline_2025,
            'Required Target': 52.0,
            'Gap': abs(baseline_2025 - 52.0)
        }

        colors = ['#E74C3C', '#27AE60', '#F39C12']
        bars = ax1.bar(baselines.keys(), baselines.values(), color=colors, alpha=0.7)
        ax1.set_title('Baseline Calibration Comparison')
        ax1.set_ylabel('Emissions (MtCO₂)')
        ax1.axhline(y=52, color='red', linestyle='--', alpha=0.7)

        for bar, value in zip(bars, baselines.values()):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{value:.1f}', ha='center', va='bottom', fontweight='bold')

        # 2. Technology coverage
        ax2 = axes[0,1]

        # Technologies from guidance vs implemented
        required_techs = ['Bio-naphtha', 'NCC H2', 'NCC Electricity', 'Heat-pump', 'Renewable Energy']
        implemented_techs = list(macc_2030['technology'].unique()) if not macc_2030.empty else []

        tech_status = []
        for tech in required_techs:
            # Simple matching logic
            found = any(tech.lower().replace('-', '_') in impl_tech.lower() for impl_tech in implemented_techs)
            tech_status.append(1 if found else 0)

        colors = ['#27AE60' if status else '#E74C3C' for status in tech_status]
        bars = ax2.bar(required_techs, tech_status, color=colors, alpha=0.7)
        ax2.set_title('Technology Coverage vs Requirements')
        ax2.set_ylabel('Implemented (1=Yes, 0=No)')
        ax2.set_xticklabels(required_techs, rotation=45, ha='right')

        # 3. Model integration status
        ax3 = axes[1,0]

        integration_metrics = {
            'BAU→MACC': 0.5,  # Partial integration
            'MACC→Optimization': 0.3,  # Limited integration
            'Unified Framework': 0.2,  # Poor integration
            'Feedback Loops': 0.1   # Minimal feedback
        }

        bars = ax3.bar(integration_metrics.keys(), integration_metrics.values(),
                      color=plt.cm.RdYlGn(list(integration_metrics.values())), alpha=0.8)
        ax3.set_title('Model Integration Assessment')
        ax3.set_ylabel('Integration Level (0-1)')
        ax3.set_xticklabels(integration_metrics.keys(), rotation=45, ha='right')
        ax3.set_ylim(0, 1)

        # 4. Output quality assessment
        ax4 = axes[1,1]

        quality_metrics = {
            'Data Completeness': 0.8,
            'Baseline Accuracy': 0.3,  # Due to 52 vs 60.9 MtCO2 issue
            'Technology Spec': 0.6,
            'Cost Analysis': 0.9,
            'Integration': 0.3
        }

        theta = np.linspace(0, 2*np.pi, len(quality_metrics), endpoint=False)
        values = list(quality_metrics.values())
        theta = np.concatenate([theta, [theta[0]]])  # Complete the circle
        values = np.concatenate([values, [values[0]]])

        ax4 = plt.subplot(2, 2, 4, projection='polar')
        ax4.plot(theta, values, 'o-', linewidth=2, color='#4ECDC4')
        ax4.fill(theta, values, alpha=0.25, color='#4ECDC4')
        ax4.set_thetagrids(np.degrees(theta[:-1]), list(quality_metrics.keys()))
        ax4.set_ylim(0, 1)
        ax4.set_title('Model Quality Assessment', y=1.1)

        plt.tight_layout()
        plt.savefig(viz_dir / "comprehensive_model_comparison.png", dpi=300, bbox_inches='tight')
        print(f"   ✅ Saved: {viz_dir}/comprehensive_model_comparison.png")

    except Exception as e:
        print(f"   ❌ Error creating comprehensive comparison: {e}")

    # Final summary
    print(f"\n🎯 VISUALIZATION SUMMARY:")
    print(f"   📁 All visualizations saved to: {viz_dir}/")
    print(f"   📊 Model 1 (BAU): Baseline calibration issues identified")
    print(f"   💰 Model 2 (MACC): Technology costs and evolution mapped")
    print(f"   ⚖️ Model 3 (Optimization): Cost-effective pathways analyzed")
    print(f"   🔍 Integration gaps and quality issues highlighted")

    plt.show()

if __name__ == "__main__":
    load_and_visualize_model_outputs()