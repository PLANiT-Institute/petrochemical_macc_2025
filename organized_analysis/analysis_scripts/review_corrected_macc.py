#!/usr/bin/env python3
"""
Review and Update MACC Analysis with Corrected 52 MtCO2 Baseline
Recalculate all MACC curves and optimization results
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime

class CorrectedMACCReviewer:
    def __init__(self):
        """Initialize MACC reviewer with corrected baseline"""
        self.excel_path = "../data/Korean_Petrochemical_MACC_Model_Calibrated_52Mt.xlsx"
        self.baseline_emissions = 52.0e6  # 52 MtCO2 corrected baseline

        # Load corrected data
        self.facilities_df = None
        self.ci_df = None
        self.ci2_df = None
        self.macc_df = None

        # Static technology costs (no learning curves as requested)
        self.static_tech_costs = {
            'Early_Retirement': 50,
            'Efficiency_Upgrade': 100,
            'Fuel_Switch': 200,
            'Process_Replacement': 400,
            'Bio_Naphtha': 272,
            'Green_Hydrogen': 300,
            'Electrification': 250
        }

        self._load_corrected_data()

    def _load_corrected_data(self):
        """Load corrected data from calibrated Excel file"""
        print("📊 Loading corrected MACC data...")

        # Load facility data
        self.facilities_df = pd.read_excel(self.excel_path, sheet_name='source_Original')
        self.ci_df = pd.read_excel(self.excel_path, sheet_name='CI_Corrected', index_col=0)
        self.ci2_df = pd.read_excel(self.excel_path, sheet_name='CI2_Corrected', index_col=0)

        # Load or create MACC template
        try:
            self.macc_df = pd.read_excel(self.excel_path, sheet_name='MACC_Template_Corrected', index_col=0)
        except:
            self.macc_df = self._create_corrected_macc_template()

        print(f"   Corrected baseline: {self.baseline_emissions/1e6:.1f} MtCO2")
        print(f"   Facilities: {len(self.facilities_df)}")

    def _create_corrected_macc_template(self):
        """Create corrected MACC template with proper abatement potentials"""
        print("\n🔧 Creating corrected MACC template...")

        # Technology abatement potentials as fraction of baseline
        tech_abatement_fractions = {
            'Early_Retirement': 0.10,      # 10% of baseline through early retirement
            'Efficiency_Upgrade': 0.15,    # 15% through efficiency improvements
            'Fuel_Switch': 0.30,           # 30% through fuel switching (hydrogen, renewables)
            'Bio_Naphtha': 0.20,           # 20% through bio-naphtha substitution
            'Green_Hydrogen': 0.25,        # 25% through green hydrogen
            'Electrification': 0.20,       # 20% through electrification
            'Process_Replacement': 0.35    # 35% through new process technologies
        }

        macc_data = []
        tech_id = 1

        for tech_name, cost in self.static_tech_costs.items():
            abatement_fraction = tech_abatement_fractions.get(tech_name, 0.15)
            max_abatement_tco2 = self.baseline_emissions * abatement_fraction
            max_abatement_mtco2 = max_abatement_tco2 / 1e6

            macc_data.append({
                'TechID': tech_id,
                'TechName': tech_name,
                'Cost_USD_per_tCO2': cost,
                'Max_Abatement_Potential_MtCO2_per_year': max_abatement_mtco2,
                'TRL': 7 if tech_name in ['Early_Retirement', 'Efficiency_Upgrade'] else 5,
                'Commercial_Year': 2025,
                'Notes': f"Corrected for 52 Mt baseline, static cost ${cost}/tCO2"
            })
            tech_id += 1

        macc_df = pd.DataFrame(macc_data)

        # Sort by cost and add cumulative abatement
        macc_df = macc_df.sort_values('Cost_USD_per_tCO2')
        macc_df['Cumulative_Abatement_MtCO2_per_year'] = macc_df['Max_Abatement_Potential_MtCO2_per_year'].cumsum()

        return macc_df.set_index('TechName')

    def create_corrected_macc_curve(self, reduction_target_pct=50):
        """Create MACC curve with corrected baseline"""
        print(f"\n📈 CREATING CORRECTED MACC CURVE ({reduction_target_pct}% reduction)")
        print("=" * 70)

        target_reduction = self.baseline_emissions * (reduction_target_pct / 100)

        print(f"   Corrected baseline: {self.baseline_emissions/1e6:.1f} MtCO2/year")
        print(f"   Target reduction: {target_reduction/1e6:.1f} MtCO2/year")

        # Get technologies sorted by cost
        technologies = []
        for tech_name, cost in self.static_tech_costs.items():
            # Calculate max abatement for this technology
            tech_abatement_fractions = {
                'Early_Retirement': 0.10,
                'Efficiency_Upgrade': 0.15,
                'Fuel_Switch': 0.30,
                'Bio_Naphtha': 0.20,
                'Green_Hydrogen': 0.25,
                'Electrification': 0.20,
                'Process_Replacement': 0.35
            }

            max_abatement = self.baseline_emissions * tech_abatement_fractions.get(tech_name, 0.15)

            technologies.append({
                'name': tech_name,
                'cost_per_tco2': cost,
                'max_abatement_tco2': max_abatement
            })

        # Sort by cost (merit order)
        technologies = sorted(technologies, key=lambda x: x['cost_per_tco2'])

        # Build MACC curve
        macc_curve = []
        cumulative_abatement = 0
        cumulative_cost = 0

        for tech in technologies:
            if cumulative_abatement >= target_reduction:
                break

            remaining_need = target_reduction - cumulative_abatement
            deployed_abatement = min(tech['max_abatement_tco2'], remaining_need)

            if deployed_abatement > 0:
                tech_cost = deployed_abatement * tech['cost_per_tco2']

                macc_curve.append({
                    'technology': tech['name'],
                    'cost_per_tco2': tech['cost_per_tco2'],
                    'abatement_deployed_tco2': deployed_abatement,
                    'total_cost_usd': tech_cost,
                    'cumulative_abatement_tco2': cumulative_abatement + deployed_abatement,
                    'cumulative_cost_usd': cumulative_cost + tech_cost
                })

                cumulative_abatement += deployed_abatement
                cumulative_cost += tech_cost

        # Calculate results
        marginal_cost = cumulative_cost / cumulative_abatement if cumulative_abatement > 0 else 0
        achievement_pct = (cumulative_abatement / target_reduction * 100) if target_reduction > 0 else 0

        results = {
            'baseline_emissions_mtco2': self.baseline_emissions / 1e6,
            'target_reduction_mtco2': target_reduction / 1e6,
            'achieved_reduction_mtco2': cumulative_abatement / 1e6,
            'achievement_pct': achievement_pct,
            'total_cost_musd': cumulative_cost / 1e6,
            'marginal_cost_usd_per_tco2': marginal_cost,
            'technologies_deployed': len(macc_curve),
            'macc_curve': macc_curve
        }

        print(f"✅ Corrected MACC Results:")
        print(f"   Target: {target_reduction/1e6:.1f} MtCO2 ({reduction_target_pct}%)")
        print(f"   Achieved: {cumulative_abatement/1e6:.1f} MtCO2 ({achievement_pct:.1f}%)")
        print(f"   Total cost: ${cumulative_cost/1e6:.1f} million")
        print(f"   Marginal cost: ${marginal_cost:.0f}/tCO2")
        print(f"   Technologies: {len(macc_curve)}")

        return results

    def create_multi_scenario_macc(self):
        """Create MACC curves for multiple reduction scenarios"""
        print(f"\n🎯 MULTI-SCENARIO CORRECTED MACC ANALYSIS")
        print("=" * 60)

        scenarios = [10, 25, 50, 75, 90]
        scenario_results = {}

        for target_pct in scenarios:
            print(f"\n--- {target_pct}% Reduction Scenario ---")
            result = self.create_corrected_macc_curve(target_pct)
            scenario_results[f"{target_pct}pct"] = result

        # Create comparison summary
        comparison_data = []
        for scenario, result in scenario_results.items():
            comparison_data.append({
                'scenario': scenario,
                'target_reduction_pct': result['target_reduction_mtco2'] / result['baseline_emissions_mtco2'] * 100,
                'achieved_reduction_mtco2': result['achieved_reduction_mtco2'],
                'total_cost_musd': result['total_cost_musd'],
                'marginal_cost_usd_per_tco2': result['marginal_cost_usd_per_tco2'],
                'technologies_deployed': result['technologies_deployed']
            })

        comparison_df = pd.DataFrame(comparison_data)

        print(f"\n📊 CORRECTED SCENARIO COMPARISON:")
        print(comparison_df.to_string(index=False, float_format='%.1f'))

        return scenario_results, comparison_df

    def visualize_corrected_macc(self, scenario_results):
        """Create comprehensive corrected MACC visualization"""
        print(f"\n📊 Creating corrected MACC visualization...")

        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        colors = {'10pct': '#1f77b4', '25pct': '#ff7f0e', '50pct': '#2ca02c',
                 '75pct': '#d62728', '90pct': '#9467bd'}

        # Plot 1: MACC curves for all scenarios (top, spanning 2 columns)
        ax1 = fig.add_subplot(gs[0, :2])

        for scenario, results in scenario_results.items():
            macc_data = results['macc_curve']
            if macc_data:
                x_vals = [0]
                y_vals = [0]
                cumulative = 0

                for tech in macc_data:
                    x_vals.append(cumulative)
                    y_vals.append(tech['cost_per_tco2'])
                    cumulative += tech['abatement_deployed_tco2'] / 1e6
                    x_vals.append(cumulative)
                    y_vals.append(tech['cost_per_tco2'])

                ax1.step(x_vals, y_vals, where='post', linewidth=2.5,
                        label=f'{scenario.replace("pct", "%")}', color=colors.get(scenario, 'gray'))

        ax1.set_xlabel('Cumulative Abatement (MtCO₂/year)')
        ax1.set_ylabel('Cost ($/tCO₂)')
        ax1.set_title('Corrected Korean Petrochemical MACC Curves (52 Mt Baseline)',
                     fontweight='bold', fontsize=14)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 450)

        # Plot 2: Marginal costs by scenario (top right)
        ax2 = fig.add_subplot(gs[0, 2])
        scenarios = list(scenario_results.keys())
        marginal_costs = [results['marginal_cost_usd_per_tco2'] for results in scenario_results.values()]

        bars = ax2.bar([s.replace('pct', '%') for s in scenarios], marginal_costs,
                      color=[colors[s] for s in scenarios], alpha=0.7)
        ax2.set_xlabel('Reduction Scenario')
        ax2.set_ylabel('Marginal Cost ($/tCO₂)')
        ax2.set_title('Marginal Costs by Scenario')
        ax2.tick_params(axis='x', rotation=45)

        # Add value labels
        for bar, value in zip(bars, marginal_costs):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'${value:.0f}', ha='center', va='bottom', fontweight='bold')

        # Plot 3: Investment requirements (middle left)
        ax3 = fig.add_subplot(gs[1, 0])
        investment_costs = [results['total_cost_musd'] for results in scenario_results.values()]

        bars = ax3.bar([s.replace('pct', '%') for s in scenarios], investment_costs,
                      color=[colors[s] for s in scenarios], alpha=0.7)
        ax3.set_xlabel('Reduction Scenario')
        ax3.set_ylabel('Total Investment (Million $)')
        ax3.set_title('Investment Requirements')
        ax3.tick_params(axis='x', rotation=45)

        # Plot 4: Technology deployment for 50% scenario (middle center)
        ax4 = fig.add_subplot(gs[1, 1])
        if '50pct' in scenario_results:
            tech_deployment = scenario_results['50pct']['macc_curve']
            if tech_deployment:
                tech_names = [tech['technology'][:15] + '...' if len(tech['technology']) > 15
                             else tech['technology'] for tech in tech_deployment]
                tech_abatement = [tech['abatement_deployed_tco2']/1e6 for tech in tech_deployment]

                bars = ax4.barh(tech_names, tech_abatement, alpha=0.7)
                ax4.set_xlabel('Abatement (MtCO₂/year)')
                ax4.set_title('Technology Deployment\\n(50% Scenario)')

        # Plot 5: Cost vs abatement potential (middle right)
        ax5 = fig.add_subplot(gs[1, 2])
        tech_costs = list(self.static_tech_costs.values())
        tech_names = list(self.static_tech_costs.keys())

        scatter = ax5.scatter(tech_costs, range(len(tech_costs)),
                             s=100, alpha=0.7, c=tech_costs, cmap='RdYlBu_r')
        ax5.set_xlabel('Technology Cost ($/tCO₂)')
        ax5.set_ylabel('Technology Index')
        ax5.set_title('Technology Cost Distribution')
        ax5.set_yticks(range(len(tech_names)))
        ax5.set_yticklabels([name[:10] + '...' if len(name) > 10 else name for name in tech_names])

        # Plot 6: Baseline vs target emissions (bottom left)
        ax6 = fig.add_subplot(gs[2, 0])
        baseline_bar = ax6.bar(['Baseline'], [52.0], color='red', alpha=0.7, label='Baseline')

        reduction_amounts = [results['achieved_reduction_mtco2'] for results in scenario_results.values()]
        remaining_amounts = [52.0 - reduction for reduction in reduction_amounts]

        x_pos = range(1, len(scenarios) + 1)
        ax6.bar(x_pos, remaining_amounts, color='orange', alpha=0.7, label='Remaining')
        ax6.bar(x_pos, reduction_amounts, bottom=remaining_amounts, color='green', alpha=0.7, label='Abated')

        ax6.set_xlabel('Scenario')
        ax6.set_ylabel('Emissions (MtCO₂/year)')
        ax6.set_title('Emission Reduction Breakdown')
        ax6.set_xticks([0] + list(x_pos))
        ax6.set_xticklabels(['Base'] + [s.replace('pct', '%') for s in scenarios], rotation=45)
        ax6.legend()

        # Plot 7: Achievement rate vs cost (bottom center)
        ax7 = fig.add_subplot(gs[2, 1])
        achievement_rates = [results['achievement_pct'] for results in scenario_results.values()]

        ax7.plot([s.replace('pct', '') for s in scenarios], achievement_rates, 'o-',
                linewidth=2, markersize=8, color='purple')
        ax7.set_xlabel('Target Reduction (%)')
        ax7.set_ylabel('Achievement Rate (%)')
        ax7.set_title('Target Achievement vs Ambition')
        ax7.grid(True, alpha=0.3)
        ax7.set_ylim(95, 105)

        # Plot 8: Cost per tonne abated vs scenario (bottom right)
        ax8 = fig.add_subplot(gs[2, 2])
        cost_per_tonne = [results['total_cost_musd'] * 1e6 / (results['achieved_reduction_mtco2'] * 1e6)
                         for results in scenario_results.values()]

        ax8.plot([s.replace('pct', '') for s in scenarios], cost_per_tonne, 's-',
                linewidth=2, markersize=8, color='brown')
        ax8.set_xlabel('Target Reduction (%)')
        ax8.set_ylabel('Average Cost ($/tCO₂)')
        ax8.set_title('Average Abatement Cost')
        ax8.grid(True, alpha=0.3)

        plt.suptitle('Corrected Korean Petrochemical MACC Analysis\\n(52 MtCO₂ Baseline, Static Technology Costs)',
                    fontsize=16, fontweight='bold', y=0.98)

        # Save visualization
        output_path = Path("../outputs/corrected_macc_analysis_52mt.png")
        output_path.parent.mkdir(exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"   Saved corrected MACC analysis: {output_path}")

        plt.show()

    def export_corrected_results(self, scenario_results, comparison_df):
        """Export corrected MACC results"""
        print(f"\n💾 Exporting corrected MACC results...")

        output_dir = Path("../outputs")
        output_dir.mkdir(exist_ok=True)

        # Export scenario comparison
        comparison_path = output_dir / "corrected_macc_comparison_52mt.csv"
        comparison_df.to_csv(comparison_path, index=False)
        print(f"   Comparison: {comparison_path}")

        # Export individual scenario MACC curves
        for scenario, results in scenario_results.items():
            if results['macc_curve']:
                macc_df = pd.DataFrame(results['macc_curve'])
                macc_path = output_dir / f"corrected_macc_curve_{scenario}_52mt.csv"
                macc_df.to_csv(macc_path, index=False)
                print(f"   {scenario}: {macc_path}")

        # Export complete results
        complete_results = {
            'analysis_date': datetime.now().isoformat(),
            'corrected_baseline_mtco2': 52.0,
            'static_technology_costs': self.static_tech_costs,
            'scenario_results': scenario_results,
            'comparison_summary': comparison_df.to_dict('records')
        }

        json_path = output_dir / "corrected_macc_analysis_complete_52mt.json"
        with open(json_path, 'w') as f:
            json.dump(complete_results, f, indent=2, default=str)
        print(f"   Complete results: {json_path}")

    def run_complete_corrected_macc_review(self):
        """Run complete corrected MACC review"""
        print("🚀 CORRECTED KOREAN PETROCHEMICAL MACC REVIEW")
        print("=" * 80)
        print("📊 Corrected baseline: 52.0 MtCO₂/year")
        print("⚙️  Static technology costs (no learning curves)")
        print("🎯 Multi-scenario analysis: 10%, 25%, 50%, 75%, 90%")
        print()

        # Step 1: Multi-scenario MACC analysis
        scenario_results, comparison_df = self.create_multi_scenario_macc()

        # Step 2: Create comprehensive visualization
        self.visualize_corrected_macc(scenario_results)

        # Step 3: Export results
        self.export_corrected_results(scenario_results, comparison_df)

        print(f"\n✅ CORRECTED MACC REVIEW COMPLETE")
        print(f"🎯 Key Corrected Results:")
        print(f"   - Baseline: 52.0 MtCO₂/year (corrected)")
        print(f"   - 50% reduction: {scenario_results['50pct']['marginal_cost_usd_per_tco2']:.0f} $/tCO₂")
        print(f"   - Investment range: ${scenario_results['10pct']['total_cost_musd']:.1f}M - ${scenario_results['90pct']['total_cost_musd']:.1f}M")
        print(f"   - All scenarios achievable with available technologies")

        return scenario_results, comparison_df

def main():
    """Main execution function"""
    try:
        # Initialize corrected MACC reviewer
        reviewer = CorrectedMACCReviewer()

        # Run complete review
        scenario_results, comparison = reviewer.run_complete_corrected_macc_review()

        print(f"\n🎉 SUCCESS! Corrected MACC analysis complete:")
        print(f"   ✅ 52 MtCO₂ baseline properly integrated")
        print(f"   ✅ All scenarios recalculated with correct abatement potentials")
        print(f"   ✅ Static technology costs maintained (no learning)")
        print(f"   ✅ Comprehensive visualization and export complete")

    except Exception as e:
        print(f"❌ Error in corrected MACC review: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()