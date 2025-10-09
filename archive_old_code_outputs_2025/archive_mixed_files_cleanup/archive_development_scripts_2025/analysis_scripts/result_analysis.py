#!/usr/bin/env python3
"""
Result Analysis and Interpretation for Korean Petrochemical MACC Study
Comprehensive analysis of optimization results and strategic insights
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime

class MACCResultAnalyzer:
    def __init__(self, results_dir=None):
        """
        Initialize Result Analyzer

        Args:
            results_dir: Directory containing optimization results
        """
        if results_dir is None:
            results_dir = "/Users/jinsupark/jinsu-coding/petrochemical_macc_2025/organized_analysis/outputs"

        self.results_dir = Path(results_dir)
        self.baseline_data = None
        self.optimization_data = None
        self.scenario_comparison = None
        self.technology_ranking = None

        # Load all available results
        self._load_results()

    def _load_results(self):
        """Load all optimization results from files"""
        print("📁 Loading optimization results...")

        try:
            # Load complete results JSON
            json_path = self.results_dir / "complete_optimization_results.json"
            if json_path.exists():
                with open(json_path, 'r') as f:
                    complete_data = json.load(f)
                    self.baseline_data = complete_data.get('baseline', {})
                    self.optimization_data = complete_data.get('optimization', {})
                print(f"   ✅ Loaded complete results from {json_path}")

            # Load summary CSV
            summary_path = self.results_dir / "macc_optimization_summary.csv"
            if summary_path.exists():
                self.scenario_comparison = pd.read_csv(summary_path)
                print(f"   ✅ Loaded scenario summary from {summary_path}")

            # Load baseline CSV
            baseline_path = self.results_dir / "baseline_emissions_costs.csv"
            if baseline_path.exists():
                baseline_df = pd.read_csv(baseline_path)
                print(f"   ✅ Loaded baseline data from {baseline_path}")

        except Exception as e:
            print(f"⚠️  Warning loading results: {str(e)}")

    def analyze_baseline_performance(self):
        """Analyze baseline emission and cost performance"""
        print("\n🏭 BASELINE PERFORMANCE ANALYSIS")
        print("=" * 60)

        if not self.baseline_data or 'facility_results' not in self.baseline_data:
            print("❌ No baseline data available")
            return None

        facilities_df = pd.DataFrame(self.baseline_data['facility_results'])

        # Overall statistics
        total_emissions = facilities_df['emissions_tco2'].sum()
        total_costs = facilities_df['fuel_cost_usd'].sum()
        avg_emission_intensity = facilities_df['emission_intensity'].mean()
        avg_cost_intensity = facilities_df['cost_intensity'].mean()

        print(f"📊 INDUSTRY TOTALS:")
        print(f"   Total Emissions: {total_emissions:,.0f} tCO2/year")
        print(f"   Total Fuel Costs: ${total_costs:,.0f}/year")
        print(f"   Number of Facilities: {len(facilities_df)}")
        print(f"   Average Emission Intensity: {avg_emission_intensity:.2f} tCO2/t product")
        print(f"   Average Cost Intensity: ${avg_cost_intensity:.2f}/t product")

        # Process type analysis
        process_analysis = facilities_df.groupby('process_type').agg({
            'emissions_tco2': ['count', 'sum', 'mean'],
            'fuel_cost_usd': ['sum', 'mean'],
            'capacity': 'sum',
            'emission_intensity': 'mean',
            'cost_intensity': 'mean'
        }).round(2)

        print(f"\n🏭 BY PROCESS TYPE:")
        print(process_analysis)

        # Top emitters
        top_emitters = facilities_df.nlargest(10, 'emissions_tco2')[['facility', 'process_type', 'emissions_tco2', 'capacity']]
        print(f"\n🎯 TOP 10 EMITTERS:")
        print(top_emitters.to_string(index=False))

        # Emission intensity distribution
        print(f"\n📈 EMISSION INTENSITY DISTRIBUTION:")
        intensity_stats = facilities_df['emission_intensity'].describe()
        print(f"   Min: {intensity_stats['min']:.3f} tCO2/t")
        print(f"   Mean: {intensity_stats['mean']:.3f} tCO2/t")
        print(f"   Median: {intensity_stats['50%']:.3f} tCO2/t")
        print(f"   Max: {intensity_stats['max']:.3f} tCO2/t")

        return {
            'total_emissions': total_emissions,
            'total_costs': total_costs,
            'facilities_df': facilities_df,
            'process_analysis': process_analysis
        }

    def analyze_scenario_comparison(self):
        """Compare optimization scenarios"""
        print("\n🎯 SCENARIO COMPARISON ANALYSIS")
        print("=" * 60)

        if self.scenario_comparison is None:
            print("❌ No scenario comparison data available")
            return None

        df = self.scenario_comparison.copy()

        # Calculate key metrics
        df['cost_per_tco2_abated'] = df['total_cost_musd'] * 1e6 / df['achieved_reduction_tco2']
        df['investment_intensity'] = df['total_cost_musd'] / df['target_reduction_pct']

        print("📊 SCENARIO PERFORMANCE COMPARISON:")
        display_cols = ['scenario', 'target_reduction_pct', 'achieved_reduction_tco2',
                       'total_cost_musd', 'marginal_cost_usd_per_tco2', 'technologies_deployed']
        print(df[display_cols].to_string(index=False, float_format='%.1f'))

        # Economic efficiency analysis
        print(f"\n💰 ECONOMIC EFFICIENCY:")
        efficiency_df = df[['scenario', 'marginal_cost_usd_per_tco2', 'cost_per_tco2_abated', 'investment_intensity']]
        print(efficiency_df.to_string(index=False, float_format='%.1f'))

        # Feasibility assessment
        print(f"\n⚖️  FEASIBILITY ASSESSMENT:")
        for _, scenario in df.iterrows():
            feasibility = "High" if scenario['marginal_cost_usd_per_tco2'] < 200 else \
                         "Medium" if scenario['marginal_cost_usd_per_tco2'] < 500 else "Low"
            print(f"   {scenario['scenario']}: {feasibility} feasibility (${scenario['marginal_cost_usd_per_tco2']:.0f}/tCO2)")

        return df

    def analyze_technology_performance(self):
        """Analyze individual technology performance across scenarios"""
        print("\n🔧 TECHNOLOGY PERFORMANCE ANALYSIS")
        print("=" * 60)

        if not self.optimization_data or 'scenarios' not in self.optimization_data:
            print("❌ No optimization scenario data available")
            return None

        # Collect technology deployment data across all scenarios
        tech_deployment = {}

        for scenario_name, scenario_data in self.optimization_data['scenarios'].items():
            if 'macc_curve' in scenario_data:
                for tech in scenario_data['macc_curve']:
                    tech_name = tech['technology']
                    if tech_name not in tech_deployment:
                        tech_deployment[tech_name] = {
                            'cost_per_tco2': tech['cost_per_tco2'],
                            'scenarios_used': [],
                            'total_abatement': 0,
                            'total_cost': 0
                        }

                    tech_deployment[tech_name]['scenarios_used'].append(scenario_name)
                    tech_deployment[tech_name]['total_abatement'] += tech['abatement_deployed_tco2']
                    tech_deployment[tech_name]['total_cost'] += tech['total_cost_usd']

        # Create technology ranking
        tech_ranking = []
        for tech_name, data in tech_deployment.items():
            tech_ranking.append({
                'technology': tech_name,
                'cost_per_tco2': data['cost_per_tco2'],
                'scenarios_count': len(data['scenarios_used']),
                'total_abatement_mtco2': data['total_abatement'] / 1e6,
                'total_cost_musd': data['total_cost'] / 1e6,
                'utilization_rate': len(data['scenarios_used']) / len(self.optimization_data['scenarios']) * 100
            })

        tech_df = pd.DataFrame(tech_ranking).sort_values('cost_per_tco2')

        print("🏆 TECHNOLOGY RANKING BY COST:")
        display_cols = ['technology', 'cost_per_tco2', 'scenarios_count', 'total_abatement_mtco2', 'utilization_rate']
        print(tech_df[display_cols].head(15).to_string(index=False, float_format='%.1f'))

        # Most frequently deployed technologies
        frequent_techs = tech_df.nlargest(10, 'utilization_rate')
        print(f"\n📈 MOST FREQUENTLY DEPLOYED TECHNOLOGIES:")
        for _, tech in frequent_techs.iterrows():
            print(f"   {tech['technology']}: {tech['utilization_rate']:.0f}% scenarios, ${tech['cost_per_tco2']:.0f}/tCO2")

        # Cost-effective technologies
        cost_effective = tech_df[tech_df['cost_per_tco2'] < 300].nlargest(10, 'total_abatement_mtco2')
        print(f"\n💡 MOST COST-EFFECTIVE TECHNOLOGIES (<$300/tCO2):")
        for _, tech in cost_effective.iterrows():
            print(f"   {tech['technology']}: ${tech['cost_per_tco2']:.0f}/tCO2, {tech['total_abatement_mtco2']:.1f} MtCO2 total")

        self.technology_ranking = tech_df
        return tech_df

    def create_comprehensive_visualization(self):
        """Create comprehensive result visualization"""
        print("\n📊 Creating comprehensive visualization...")

        fig = plt.figure(figsize=(20, 16))
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)

        # Color palette
        colors = plt.cm.Set3(np.linspace(0, 1, 12))

        # Plot 1: Scenario cost comparison (top-left, spanning 2 columns)
        ax1 = fig.add_subplot(gs[0, 0:2])
        if self.scenario_comparison is not None:
            scenarios = self.scenario_comparison['scenario']
            marginal_costs = self.scenario_comparison['marginal_cost_usd_per_tco2']
            bars1 = ax1.bar(scenarios, marginal_costs, color=colors[:len(scenarios)], alpha=0.8)
            ax1.set_ylabel('Marginal Cost ($/tCO₂)')
            ax1.set_title('Marginal Abatement Cost by Scenario', fontweight='bold')
            ax1.tick_params(axis='x', rotation=45)

            # Add value labels on bars
            for bar, value in zip(bars1, marginal_costs):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                        f'${value:.0f}', ha='center', va='bottom', fontweight='bold')

        # Plot 2: Total investment by scenario (top-right, spanning 2 columns)
        ax2 = fig.add_subplot(gs[0, 2:4])
        if self.scenario_comparison is not None:
            total_costs = self.scenario_comparison['total_cost_musd']
            bars2 = ax2.bar(scenarios, total_costs, color=colors[:len(scenarios)], alpha=0.8)
            ax2.set_ylabel('Total Investment (Million $)')
            ax2.set_title('Total Investment Requirements', fontweight='bold')
            ax2.tick_params(axis='x', rotation=45)

            # Add value labels on bars
            for bar, value in zip(bars2, total_costs):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                        f'${value:.0f}M', ha='center', va='bottom', fontweight='bold')

        # Plot 3: MACC Curve (second row, full width)
        ax3 = fig.add_subplot(gs[1, :])
        if self.optimization_data and '50pct' in self.optimization_data.get('scenarios', {}):
            macc_data = self.optimization_data['scenarios']['50pct'].get('macc_curve', [])
            if macc_data:
                x_vals = [0]
                y_vals = [0]
                cumulative_abatement = 0

                for tech in macc_data[:15]:  # Show first 15 technologies
                    x_vals.append(cumulative_abatement / 1e6)
                    y_vals.append(tech['cost_per_tco2'])
                    cumulative_abatement += tech['abatement_deployed_tco2']
                    x_vals.append(cumulative_abatement / 1e6)
                    y_vals.append(tech['cost_per_tco2'])

                ax3.step(x_vals, y_vals, where='post', linewidth=3, color='navy')
                ax3.fill_between(x_vals, 0, y_vals, alpha=0.3, color='lightblue', step='post')
                ax3.set_xlabel('Cumulative Abatement (MtCO₂/year)')
                ax3.set_ylabel('Cost ($/tCO₂)')
                ax3.set_title('MACC Curve - 50% Reduction Scenario', fontweight='bold', fontsize=14)
                ax3.grid(True, alpha=0.3)

        # Plot 4: Baseline emissions by process type (third row, left)
        ax4 = fig.add_subplot(gs[2, 0:2])
        if self.baseline_data and 'facility_results' in self.baseline_data:
            facilities_df = pd.DataFrame(self.baseline_data['facility_results'])
            process_emissions = facilities_df.groupby('process_type')['emissions_tco2'].sum().sort_values(ascending=True)

            bars4 = ax4.barh(process_emissions.index, process_emissions.values / 1e6, color=colors[:len(process_emissions)])
            ax4.set_xlabel('Emissions (MtCO₂/year)')
            ax4.set_title('Baseline Emissions by Process Type', fontweight='bold')

            # Add value labels
            for i, (bar, value) in enumerate(zip(bars4, process_emissions.values)):
                ax4.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                        f'{value/1e6:.1f}', ha='left', va='center')

        # Plot 5: Technology utilization (third row, right)
        ax5 = fig.add_subplot(gs[2, 2:4])
        if self.technology_ranking is not None:
            top_techs = self.technology_ranking.nlargest(10, 'utilization_rate')
            tech_names = [name[:25] + '...' if len(name) > 25 else name for name in top_techs['technology']]

            bars5 = ax5.barh(tech_names, top_techs['utilization_rate'], color=colors[:len(top_techs)])
            ax5.set_xlabel('Utilization Rate (%)')
            ax5.set_title('Technology Utilization Across Scenarios', fontweight='bold')

            # Add value labels
            for bar, value in zip(bars5, top_techs['utilization_rate']):
                ax5.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                        f'{value:.0f}%', ha='left', va='center')

        # Plot 6: Abatement potential vs cost (fourth row, left)
        ax6 = fig.add_subplot(gs[3, 0:2])
        if self.technology_ranking is not None:
            scatter_data = self.technology_ranking[self.technology_ranking['total_abatement_mtco2'] > 0.1]  # Filter small values
            scatter = ax6.scatter(scatter_data['total_abatement_mtco2'],
                                scatter_data['cost_per_tco2'],
                                s=scatter_data['utilization_rate']*3,
                                alpha=0.7, c=range(len(scatter_data)), cmap='viridis')
            ax6.set_xlabel('Total Abatement Potential (MtCO₂)')
            ax6.set_ylabel('Cost ($/tCO₂)')
            ax6.set_title('Technology Abatement vs Cost (bubble size = utilization)', fontweight='bold')
            ax6.grid(True, alpha=0.3)

        # Plot 7: Investment timeline (fourth row, right)
        ax7 = fig.add_subplot(gs[3, 2:4])
        if self.scenario_comparison is not None:
            scenarios_pct = self.scenario_comparison['target_reduction_pct']
            annual_investment = self.scenario_comparison['total_cost_musd'] / 25  # Assuming 25-year timeline

            ax7.plot(scenarios_pct, annual_investment, 'o-', linewidth=3, markersize=8, color='red')
            ax7.set_xlabel('Emission Reduction Target (%)')
            ax7.set_ylabel('Annual Investment (Million $/year)')
            ax7.set_title('Annual Investment Requirements', fontweight='bold')
            ax7.grid(True, alpha=0.3)

            # Add value labels
            for x, y in zip(scenarios_pct, annual_investment):
                ax7.text(x, y + 20, f'${y:.0f}M', ha='center', va='bottom', fontweight='bold')

        plt.suptitle('Korean Petrochemical MACC Analysis - Comprehensive Results',
                    fontsize=18, fontweight='bold', y=0.98)

        # Save the visualization
        output_path = self.results_dir / "comprehensive_macc_analysis.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   Saved comprehensive analysis to: {output_path}")

        plt.show()

    def generate_strategic_insights(self):
        """Generate strategic insights and recommendations"""
        print("\n💡 STRATEGIC INSIGHTS AND RECOMMENDATIONS")
        print("=" * 80)

        insights = []

        # Cost analysis insights
        if self.scenario_comparison is not None:
            min_cost_scenario = self.scenario_comparison.loc[self.scenario_comparison['marginal_cost_usd_per_tco2'].idxmin()]
            max_cost_scenario = self.scenario_comparison.loc[self.scenario_comparison['marginal_cost_usd_per_tco2'].idxmax()]

            insights.append(f"🎯 COST EFFICIENCY:")
            insights.append(f"   • Most cost-effective scenario: {min_cost_scenario['scenario']} at ${min_cost_scenario['marginal_cost_usd_per_tco2']:.0f}/tCO₂")
            insights.append(f"   • Highest cost scenario: {max_cost_scenario['scenario']} at ${max_cost_scenario['marginal_cost_usd_per_tco2']:.0f}/tCO₂")
            insights.append(f"   • Cost escalation: {max_cost_scenario['marginal_cost_usd_per_tco2'] / min_cost_scenario['marginal_cost_usd_per_tco2']:.1f}x increase for higher targets")

        # Technology insights
        if self.technology_ranking is not None:
            low_cost_techs = self.technology_ranking[self.technology_ranking['cost_per_tco2'] < 200]
            high_impact_techs = self.technology_ranking.nlargest(5, 'total_abatement_mtco2')

            insights.append(f"\n🔧 TECHNOLOGY PRIORITIES:")
            insights.append(f"   • Low-cost technologies (<$200/tCO₂): {len(low_cost_techs)} available")
            insights.append(f"   • Highest impact technology: {high_impact_techs.iloc[0]['technology']} ({high_impact_techs.iloc[0]['total_abatement_mtco2']:.1f} MtCO₂)")

            # Most versatile technologies (used in most scenarios)
            versatile_techs = self.technology_ranking.nlargest(3, 'utilization_rate')
            insights.append(f"   • Most versatile technologies:")
            for _, tech in versatile_techs.iterrows():
                insights.append(f"     - {tech['technology']}: {tech['utilization_rate']:.0f}% scenarios, ${tech['cost_per_tco2']:.0f}/tCO₂")

        # Economic feasibility insights
        if self.baseline_data:
            total_baseline_cost = self.baseline_data.get('total_fuel_cost', 0)
            if total_baseline_cost > 0 and self.scenario_comparison is not None:
                moderate_scenario = self.scenario_comparison[self.scenario_comparison['scenario'] == '50pct']
                if not moderate_scenario.empty:
                    abatement_investment = moderate_scenario.iloc[0]['total_cost_musd'] * 1e6
                    annual_investment = abatement_investment / 25  # 25-year timeline
                    investment_ratio = annual_investment / total_baseline_cost

                    insights.append(f"\n💰 ECONOMIC FEASIBILITY:")
                    insights.append(f"   • Annual baseline fuel cost: ${total_baseline_cost:,.0f}")
                    insights.append(f"   • Annual investment needed (50% scenario): ${annual_investment:,.0f}")
                    insights.append(f"   • Investment as % of fuel costs: {investment_ratio*100:.1f}%")

        # Policy recommendations
        insights.append(f"\n📋 POLICY RECOMMENDATIONS:")

        if self.scenario_comparison is not None:
            feasible_scenarios = self.scenario_comparison[self.scenario_comparison['marginal_cost_usd_per_tco2'] < 300]
            if not feasible_scenarios.empty:
                max_feasible = feasible_scenarios['target_reduction_pct'].max()
                insights.append(f"   • Economically feasible target: Up to {max_feasible}% reduction (<$300/tCO₂)")

            high_ambition = self.scenario_comparison[self.scenario_comparison['target_reduction_pct'] >= 75]
            if not high_ambition.empty:
                min_high_cost = high_ambition['marginal_cost_usd_per_tco2'].min()
                insights.append(f"   • High ambition (75%+) requires: ${min_high_cost:.0f}+/tCO₂ carbon pricing")

        insights.append(f"   • Technology support priorities:")
        insights.append(f"     - Early deployment of cost-effective technologies (<$200/tCO₂)")
        insights.append(f"     - R&D investment for high-cost technologies (>$500/tCO₂)")
        insights.append(f"     - Infrastructure development for hydrogen and renewable energy")

        insights.append(f"\n🎯 IMPLEMENTATION STRATEGY:")
        insights.append(f"   • Phase 1 (2025-2030): Deploy low-hanging fruit technologies")
        insights.append(f"   • Phase 2 (2030-2040): Scale up proven technologies with policy support")
        insights.append(f"   • Phase 3 (2040-2050): Deploy advanced technologies as costs decrease")

        # Print all insights
        for insight in insights:
            print(insight)

        return insights

    def create_executive_summary(self):
        """Create executive summary report"""
        print("\n📋 GENERATING EXECUTIVE SUMMARY")
        print("=" * 60)

        summary_data = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'baseline_performance': {},
            'scenario_analysis': {},
            'technology_assessment': {},
            'strategic_recommendations': []
        }

        # Baseline performance
        if self.baseline_data:
            summary_data['baseline_performance'] = {
                'total_emissions_mtco2': self.baseline_data.get('total_emissions', 0) / 1e6,
                'total_fuel_cost_musd': self.baseline_data.get('total_fuel_cost', 0) / 1e6,
                'number_of_facilities': len(self.baseline_data.get('facility_results', []))
            }

        # Scenario analysis
        if self.scenario_comparison is not None:
            summary_data['scenario_analysis'] = {
                'scenarios_analyzed': len(self.scenario_comparison),
                'cost_range_usd_per_tco2': {
                    'min': float(self.scenario_comparison['marginal_cost_usd_per_tco2'].min()),
                    'max': float(self.scenario_comparison['marginal_cost_usd_per_tco2'].max())
                },
                'investment_range_musd': {
                    'min': float(self.scenario_comparison['total_cost_musd'].min()),
                    'max': float(self.scenario_comparison['total_cost_musd'].max())
                }
            }

        # Technology assessment
        if self.technology_ranking is not None:
            summary_data['technology_assessment'] = {
                'total_technologies': len(self.technology_ranking),
                'cost_effective_count': len(self.technology_ranking[self.technology_ranking['cost_per_tco2'] < 200]),
                'top_technology': {
                    'name': self.technology_ranking.iloc[0]['technology'],
                    'cost': float(self.technology_ranking.iloc[0]['cost_per_tco2'])
                }
            }

        # Save executive summary
        summary_path = self.results_dir / "executive_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary_data, f, indent=2)

        print(f"✅ Executive summary saved to: {summary_path}")
        return summary_data

    def run_comprehensive_analysis(self):
        """Run complete result analysis workflow"""
        print("🚀 RUNNING COMPREHENSIVE RESULT ANALYSIS")
        print("=" * 80)

        # Step 1: Analyze baseline
        baseline_analysis = self.analyze_baseline_performance()

        # Step 2: Compare scenarios
        scenario_analysis = self.analyze_scenario_comparison()

        # Step 3: Analyze technologies
        technology_analysis = self.analyze_technology_performance()

        # Step 4: Generate insights
        strategic_insights = self.generate_strategic_insights()

        # Step 5: Create visualizations
        self.create_comprehensive_visualization()

        # Step 6: Create executive summary
        executive_summary = self.create_executive_summary()

        print(f"\n✅ COMPREHENSIVE ANALYSIS COMPLETE")
        print(f"📊 Results available in: {self.results_dir}")
        print(f"🎯 Key insight: Korean petrochemical industry can achieve significant emission reductions")
        print(f"   with costs ranging from ${scenario_analysis['marginal_cost_usd_per_tco2'].min():.0f}-{scenario_analysis['marginal_cost_usd_per_tco2'].max():.0f}/tCO₂")

def main():
    """Main execution function"""
    print("📊 KOREAN PETROCHEMICAL MACC RESULT ANALYSIS")
    print("=" * 80)

    try:
        # Initialize analyzer
        analyzer = MACCResultAnalyzer()

        # Run comprehensive analysis
        analyzer.run_comprehensive_analysis()

    except Exception as e:
        print(f"❌ Error in result analysis: {str(e)}")
        raise

if __name__ == "__main__":
    main()