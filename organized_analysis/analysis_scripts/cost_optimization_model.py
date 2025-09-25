#!/usr/bin/env python3
"""
Cost Optimization Model for Korean Petrochemical MACC Analysis
Implements cost optimization framework using CI, CI2, and MACC matrices
"""

import pandas as pd
import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

class MACCCostOptimizer:
    def __init__(self, excel_path):
        """
        Initialize MACC Cost Optimizer with Excel data

        Args:
            excel_path: Path to corrected MACC Excel model
        """
        self.excel_path = excel_path
        self.ci_df = None
        self.ci2_df = None
        self.macc_df = None
        self.facilities_df = None
        self.baseline_emissions = {}
        self.optimization_results = {}

        # Load data
        self._load_excel_data()

    def _load_excel_data(self):
        """Load all required data from Excel file"""
        try:
            print("📊 Loading Excel data for cost optimization...")

            # Load CI matrix (consumption intensities)
            self.ci_df = pd.read_excel(self.excel_path, sheet_name='CI_Corrected', index_col=0)
            print(f"   CI Matrix: {self.ci_df.shape}")

            # Load CI2 matrix (emission factors)
            self.ci2_df = pd.read_excel(self.excel_path, sheet_name='CI2_Corrected', index_col=0)
            print(f"   CI2 Matrix: {self.ci2_df.shape}")

            # Load MACC template (technology costs)
            self.macc_df = pd.read_excel(self.excel_path, sheet_name='MACC_Template_Corrected', index_col=0)
            print(f"   MACC Template: {self.macc_df.shape}")

            # Load facility data
            self.facilities_df = pd.read_excel(self.excel_path, sheet_name='SOURCE', index_col=0)
            print(f"   Facilities: {self.facilities_df.shape}")

        except Exception as e:
            print(f"❌ Error loading Excel data: {str(e)}")
            raise

    def calculate_baseline_costs(self):
        """Calculate baseline emission costs and fuel costs"""
        print("\n💰 CALCULATING BASELINE COSTS")
        print("=" * 60)

        baseline_results = {}

        # Extract emission factors from CI2
        emission_factors = {
            'LNG': self.ci2_df.loc['LNG_tCO2_per_GJ', 'Value'] if 'LNG_tCO2_per_GJ' in self.ci2_df.index else 0.0564,
            'Coal': self.ci2_df.loc['Coal_tCO2_per_GJ', 'Value'] if 'Coal_tCO2_per_GJ' in self.ci2_df.index else 0.0946,
            'Heavy_Oil': self.ci2_df.loc['Heavy_Oil_tCO2_per_GJ', 'Value'] if 'Heavy_Oil_tCO2_per_GJ' in self.ci2_df.index else 0.0773,
            'Naphtha_Feedstock': self.ci2_df.loc['Naphtha_Feedstock_tCO2_per_GJ', 'Value'] if 'Naphtha_Feedstock_tCO2_per_GJ' in self.ci2_df.index else 0.0207,
            'Electricity': self.ci2_df.loc['Electricity_tCO2_per_kWh', 'Value'] if 'Electricity_tCO2_per_kWh' in self.ci2_df.index else 0.000424
        }

        print("🔥 Emission Factors (tCO2/GJ or tCO2/kWh):")
        for fuel, factor in emission_factors.items():
            print(f"   {fuel}: {factor:.6f}")

        # Calculate facility-level baseline emissions and costs
        total_emissions = 0
        total_fuel_cost = 0
        facility_results = []

        # Fuel prices ($/GJ or $/kWh)
        fuel_prices = {
            'LNG': 12.0,        # $/GJ
            'Coal': 4.0,        # $/GJ
            'Heavy_Oil': 15.0,  # $/GJ
            'Naphtha_Feedstock': 18.0,  # $/GJ
            'Electricity': 0.12  # $/kWh
        }

        for facility_idx, facility in self.facilities_df.iterrows():
            facility_name = facility_idx
            process_type = facility.get('process_type', 'Unknown')
            capacity = facility.get('capacity_t_per_year', 0)

            if capacity == 0:
                continue

            # Get product from facility mapping
            product = self._map_facility_to_product(process_type)

            if product not in self.ci_df.index:
                continue

            product_row = self.ci_df.loc[product]

            facility_emissions = 0
            facility_fuel_cost = 0

            # Calculate emissions and costs for each fuel type
            fuel_consumption_map = {
                'LNG': 'LNG_GJ_per_t',
                'Coal': 'Coal_GJ_per_t',
                'Heavy_Oil': 'Heavy_Oil_GJ_per_t',
                'Naphtha_Feedstock': 'Naphtha_Feedstock_GJ_per_t',
                'Electricity': 'Electricity_kWh_per_t'
            }

            for fuel, consumption_col in fuel_consumption_map.items():
                if consumption_col in product_row.index:
                    consumption_per_t = product_row[consumption_col]
                    if pd.notna(consumption_per_t) and consumption_per_t > 0:
                        # Total consumption for facility
                        total_consumption = consumption_per_t * capacity

                        # Emissions
                        fuel_emissions = total_consumption * emission_factors[fuel]
                        facility_emissions += fuel_emissions

                        # Fuel costs
                        fuel_cost = total_consumption * fuel_prices[fuel]
                        facility_fuel_cost += fuel_cost

            facility_results.append({
                'facility': facility_name,
                'process_type': process_type,
                'product': product,
                'capacity': capacity,
                'emissions_tco2': facility_emissions,
                'fuel_cost_usd': facility_fuel_cost,
                'emission_intensity': facility_emissions / capacity if capacity > 0 else 0,
                'cost_intensity': facility_fuel_cost / capacity if capacity > 0 else 0
            })

            total_emissions += facility_emissions
            total_fuel_cost += facility_fuel_cost

        baseline_results['total_emissions'] = total_emissions
        baseline_results['total_fuel_cost'] = total_fuel_cost
        baseline_results['facility_results'] = facility_results
        baseline_results['emission_factors'] = emission_factors
        baseline_results['fuel_prices'] = fuel_prices

        print(f"\n📊 BASELINE COST SUMMARY:")
        print(f"   Total Emissions: {total_emissions:,.0f} tCO2/year")
        print(f"   Total Fuel Cost: ${total_fuel_cost:,.0f}/year")
        print(f"   Average Cost: ${total_fuel_cost/total_emissions:.2f}/tCO2")

        self.baseline_emissions = baseline_results
        return baseline_results

    def create_macc_curve(self, target_reduction_pct=50):
        """
        Create MACC curve by optimizing technology deployment

        Args:
            target_reduction_pct: Target emission reduction percentage (0-100)
        """
        print(f"\n📈 CREATING MACC CURVE (Target: {target_reduction_pct}% reduction)")
        print("=" * 70)

        if not self.baseline_emissions:
            self.calculate_baseline_costs()

        baseline_emissions = self.baseline_emissions['total_emissions']
        target_reduction = baseline_emissions * (target_reduction_pct / 100)

        print(f"   Baseline Emissions: {baseline_emissions:,.0f} tCO2/year")
        print(f"   Target Reduction: {target_reduction:,.0f} tCO2/year")

        # Extract technology data from MACC template
        technologies = []
        for tech_idx, tech in self.macc_df.iterrows():
            if pd.notna(tech.get('Cost_USD_per_tCO2', 0)) and tech.get('Cost_USD_per_tCO2', 0) > 0:
                tech_data = {
                    'name': tech_idx,
                    'cost_per_tco2': tech.get('Cost_USD_per_tCO2', 0),
                    'max_abatement_mtco2': tech.get('Max_Abatement_Potential_MtCO2_per_year', 0),
                    'capex_musd': tech.get('CAPEX_MUSD', 0),
                    'applicable_processes': tech.get('Applicable_Processes', '').split(',') if pd.notna(tech.get('Applicable_Processes', '')) else []
                }
                technologies.append(tech_data)

        # Sort technologies by cost (merit order)
        technologies = sorted(technologies, key=lambda x: x['cost_per_tco2'])

        print(f"\n🔧 Available Technologies: {len(technologies)}")
        for i, tech in enumerate(technologies[:10]):  # Show first 10
            print(f"   {i+1}. {tech['name']}: ${tech['cost_per_tco2']:.0f}/tCO2, {tech['max_abatement_mtco2']:.1f} Mt potential")

        # Build MACC curve by selecting technologies in merit order
        macc_curve = []
        cumulative_abatement = 0
        cumulative_cost = 0

        for tech in technologies:
            if cumulative_abatement >= target_reduction:
                break

            # Calculate deployment for this technology
            remaining_need = target_reduction - cumulative_abatement
            available_abatement = min(tech['max_abatement_mtco2'] * 1e6, remaining_need)  # Convert Mt to t

            if available_abatement > 0:
                tech_cost = available_abatement * tech['cost_per_tco2']

                macc_curve.append({
                    'technology': tech['name'],
                    'cost_per_tco2': tech['cost_per_tco2'],
                    'abatement_deployed_tco2': available_abatement,
                    'total_cost_usd': tech_cost,
                    'cumulative_abatement_tco2': cumulative_abatement + available_abatement,
                    'cumulative_cost_usd': cumulative_cost + tech_cost
                })

                cumulative_abatement += available_abatement
                cumulative_cost += tech_cost

        # Calculate marginal cost
        if cumulative_abatement > 0:
            marginal_cost = cumulative_cost / cumulative_abatement
        else:
            marginal_cost = 0

        results = {
            'target_reduction_pct': target_reduction_pct,
            'target_reduction_tco2': target_reduction,
            'achieved_reduction_tco2': cumulative_abatement,
            'achievement_pct': (cumulative_abatement / target_reduction * 100) if target_reduction > 0 else 0,
            'total_cost_usd': cumulative_cost,
            'marginal_cost_usd_per_tco2': marginal_cost,
            'technologies_deployed': len(macc_curve),
            'macc_curve': macc_curve
        }

        print(f"\n💡 MACC OPTIMIZATION RESULTS:")
        print(f"   Target: {target_reduction:,.0f} tCO2 ({target_reduction_pct}%)")
        print(f"   Achieved: {cumulative_abatement:,.0f} tCO2 ({results['achievement_pct']:.1f}%)")
        print(f"   Total Cost: ${cumulative_cost:,.0f}")
        print(f"   Marginal Cost: ${marginal_cost:.0f}/tCO2")
        print(f"   Technologies Used: {len(macc_curve)}")

        return results

    def optimize_multiple_scenarios(self, reduction_targets=[10, 25, 50, 75, 90]):
        """Optimize for multiple emission reduction scenarios"""
        print(f"\n🎯 MULTI-SCENARIO OPTIMIZATION")
        print("=" * 60)

        scenario_results = {}

        for target in reduction_targets:
            print(f"\n--- Scenario: {target}% Reduction ---")
            result = self.create_macc_curve(target_reduction_pct=target)
            scenario_results[f"{target}pct"] = result

        # Create summary
        summary_data = []
        for scenario, result in scenario_results.items():
            summary_data.append({
                'scenario': scenario,
                'target_reduction_pct': result['target_reduction_pct'],
                'achieved_reduction_tco2': result['achieved_reduction_tco2'],
                'total_cost_musd': result['total_cost_usd'] / 1e6,
                'marginal_cost_usd_per_tco2': result['marginal_cost_usd_per_tco2'],
                'technologies_deployed': result['technologies_deployed']
            })

        summary_df = pd.DataFrame(summary_data)

        print(f"\n📊 SCENARIO SUMMARY:")
        print(summary_df.to_string(index=False, float_format='%.1f'))

        self.optimization_results = {
            'scenarios': scenario_results,
            'summary': summary_df
        }

        return scenario_results

    def _map_facility_to_product(self, process_type):
        """Map facility process type to CI matrix product"""
        mapping = {
            'NCC': 'Ethylene',
            'BTX': 'Benzene',
            'Aromatics': 'Benzene',
            'Utilities': 'Steam',
            'Steam': 'Steam',
            'Power': 'Electricity_Production'
        }

        for key, value in mapping.items():
            if key in process_type:
                return value

        return 'Ethylene'  # Default

    def visualize_macc_curve(self, scenario_results=None, save_path=None):
        """Create MACC curve visualization"""
        if scenario_results is None:
            scenario_results = self.optimization_results.get('scenarios', {})

        if not scenario_results:
            print("❌ No optimization results to visualize")
            return

        print("\n📊 Creating MACC curve visualization...")

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Korean Petrochemical MACC Analysis - Cost Optimization Results', fontsize=16, fontweight='bold')

        # Plot 1: MACC Curve for 50% scenario
        if '50pct' in scenario_results:
            macc_data = scenario_results['50pct']['macc_curve']
            if macc_data:
                x_vals = [0]
                y_vals = [0]
                cumulative_abatement = 0

                for tech in macc_data:
                    x_vals.append(cumulative_abatement)
                    y_vals.append(tech['cost_per_tco2'])
                    cumulative_abatement += tech['abatement_deployed_tco2']
                    x_vals.append(cumulative_abatement)
                    y_vals.append(tech['cost_per_tco2'])

                ax1.plot(np.array(x_vals)/1e6, y_vals, 'b-', linewidth=2)
                ax1.fill_between(np.array(x_vals)/1e6, 0, y_vals, alpha=0.3)
                ax1.set_xlabel('Cumulative Abatement (MtCO₂/year)')
                ax1.set_ylabel('Cost ($/tCO₂)')
                ax1.set_title('MACC Curve - 50% Reduction Scenario')
                ax1.grid(True, alpha=0.3)

        # Plot 2: Marginal costs by scenario
        scenarios = []
        marginal_costs = []
        for scenario, result in scenario_results.items():
            scenarios.append(scenario.replace('pct', '%'))
            marginal_costs.append(result['marginal_cost_usd_per_tco2'])

        ax2.bar(scenarios, marginal_costs, color='green', alpha=0.7)
        ax2.set_xlabel('Reduction Scenario')
        ax2.set_ylabel('Marginal Cost ($/tCO₂)')
        ax2.set_title('Marginal Abatement Costs by Scenario')
        ax2.tick_params(axis='x', rotation=45)

        # Plot 3: Total investment by scenario
        total_costs = [result['total_cost_usd']/1e9 for result in scenario_results.values()]
        ax3.bar(scenarios, total_costs, color='orange', alpha=0.7)
        ax3.set_xlabel('Reduction Scenario')
        ax3.set_ylabel('Total Investment (Billion $)')
        ax3.set_title('Total Investment Requirements')
        ax3.tick_params(axis='x', rotation=45)

        # Plot 4: Technology deployment
        if '50pct' in scenario_results:
            macc_data = scenario_results['50pct']['macc_curve']
            if macc_data:
                tech_names = [tech['technology'][:20] + '...' if len(tech['technology']) > 20 else tech['technology'] for tech in macc_data[:10]]
                tech_abatement = [tech['abatement_deployed_tco2']/1e6 for tech in macc_data[:10]]

                ax4.barh(tech_names, tech_abatement, color='purple', alpha=0.7)
                ax4.set_xlabel('Abatement Deployed (MtCO₂/year)')
                ax4.set_title('Technology Deployment - 50% Scenario')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"   Saved to: {save_path}")
        else:
            save_path = "/Users/jinsupark/jinsu-coding/petrochemical_macc_2025/organized_analysis/outputs/macc_cost_optimization.png"
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"   Saved to: {save_path}")

        plt.show()

    def export_results(self, output_dir=None):
        """Export optimization results to files"""
        if output_dir is None:
            output_dir = Path("/Users/jinsupark/jinsu-coding/petrochemical_macc_2025/organized_analysis/outputs")
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(exist_ok=True)

        print(f"\n💾 EXPORTING RESULTS to {output_dir}")
        print("=" * 50)

        # Export baseline results
        if self.baseline_emissions:
            baseline_df = pd.DataFrame(self.baseline_emissions['facility_results'])
            baseline_path = output_dir / "baseline_emissions_costs.csv"
            baseline_df.to_csv(baseline_path, index=False)
            print(f"   Baseline: {baseline_path}")

        # Export scenario summary
        if 'summary' in self.optimization_results:
            summary_path = output_dir / "macc_optimization_summary.csv"
            self.optimization_results['summary'].to_csv(summary_path, index=False)
            print(f"   Summary: {summary_path}")

        # Export detailed MACC curves
        for scenario, result in self.optimization_results.get('scenarios', {}).items():
            if result['macc_curve']:
                macc_df = pd.DataFrame(result['macc_curve'])
                macc_path = output_dir / f"macc_curve_{scenario}.csv"
                macc_df.to_csv(macc_path, index=False)
                print(f"   MACC {scenario}: {macc_path}")

        # Export complete results as JSON
        json_path = output_dir / "complete_optimization_results.json"
        export_data = {
            'baseline': self.baseline_emissions,
            'optimization': self.optimization_results
        }

        # Convert numpy types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        # Clean data for JSON export
        import json
        with open(json_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=convert_numpy)
        print(f"   Complete: {json_path}")

        print("✅ Export complete!")

def main():
    """Main execution function"""
    print("🚀 KOREAN PETROCHEMICAL MACC COST OPTIMIZATION")
    print("=" * 80)

    # Initialize optimizer
    excel_path = "/Users/jinsupark/jinsu-coding/petrochemical_macc_2025/organized_analysis/data/Korean_Petrochemical_MACC_Model_Corrected_with_Naphtha.xlsx"

    try:
        optimizer = MACCCostOptimizer(excel_path)

        # Calculate baseline costs
        baseline_results = optimizer.calculate_baseline_costs()

        # Optimize multiple scenarios
        scenario_results = optimizer.optimize_multiple_scenarios()

        # Create visualizations
        optimizer.visualize_macc_curve()

        # Export results
        optimizer.export_results()

        print(f"\n✅ COST OPTIMIZATION COMPLETE")
        print(f"🎯 Key Results:")
        print(f"   - Baseline Emissions: {baseline_results['total_emissions']:,.0f} tCO2/year")
        print(f"   - Baseline Fuel Cost: ${baseline_results['total_fuel_cost']:,.0f}/year")
        print(f"   - Scenarios Analyzed: {len(scenario_results)}")
        print(f"   - Results exported to organized_analysis/outputs/")

    except Exception as e:
        print(f"❌ Error in cost optimization: {str(e)}")
        raise

if __name__ == "__main__":
    main()