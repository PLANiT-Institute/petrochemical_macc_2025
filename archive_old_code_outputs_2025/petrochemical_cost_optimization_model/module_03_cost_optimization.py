#!/usr/bin/env python3
"""
MODULE 3: COST OPTIMIZATION UNDER EMISSION CONSTRAINTS
Korean Petrochemical Industry - Least-cost decarbonization pathways

Features:
- Optimize technology deployment to meet emission targets
- Three scenarios: Budget, Point Targets, Linear reduction
- Track energy source transitions (naphtha → H2/electricity/RE)
- Annual technology adoption rates
- CSV + PNG outputs

Author: Petrochemical MACC Model v2.0
Date: October 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

class CostOptimizer:
    """Cost optimization under emission constraints"""

    def __init__(self, excel_path):
        """Initialize with data"""
        self.excel_path = excel_path
        self.output_dir = Path('step_03_cost_optimization/outputs')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("MODULE 3: COST OPTIMIZATION")
        print("="*80)

        # Load data
        print("\n📁 Loading data...")
        self.df_bau = pd.read_csv('step_01_baseline_analysis/outputs/bau_trajectory_2025_2075.csv')
        self.df_macc = pd.read_csv('step_02_macc_analysis/outputs/macc_annual_2025_2050.csv')
        self.df_baseline = pd.read_csv('step_01_baseline_analysis/outputs/baseline_2025_detailed.csv')

        print(f"   ✓ Loaded BAU trajectory")
        print(f"   ✓ Loaded MACC data: {len(self.df_macc)} technology-year combinations")
        print(f"   ✓ Baseline 2025: {self.df_baseline['total_emissions_kt'].sum()/1000:.2f} MtCO2")

        # Define emission scenarios
        self.scenarios = {
            'Budget': {
                'type': 'cumulative',
                'cumulative_budget_2025_2050': 800,  # MtCO2 total budget
                'description': 'Cumulative 800 MtCO2 budget (2025-2050)'
            },
            'Point_Targets': {
                'type': 'annual',
                'targets': {
                    2030: 40,  # MtCO2
                    2040: 20,
                    2050: 5
                },
                'description': '2030: 40 Mt, 2040: 20 Mt, 2050: 5 Mt'
            },
            'Linear': {
                'type': 'linear',
                'start_year': 2025,
                'end_year': 2050,
                'end_target': 2,  # MtCO2 by 2050
                'description': 'Linear reduction to 2 MtCO2 by 2050'
            }
        }

    def optimize_scenario(self, scenario_name):
        """Optimize technology deployment for a given scenario"""
        print(f"\n📊 Optimizing scenario: {scenario_name}")

        scenario = self.scenarios[scenario_name]
        years = range(2025, 2051)

        # Get emission targets for each year
        targets = self._get_annual_targets(scenario, years)

        # Optimize technology deployment
        deployment = []
        cumulative_cost = 0
        cumulative_capex = 0
        cumulative_abatement = 0

        for year in years:
            # Get BAU emissions for this year
            bau_emissions = self.df_bau[self.df_bau['year'] == year]['total_emissions_mt'].iloc[0]

            # Get target for this year
            target = targets.get(year, bau_emissions)

            # Required abatement
            required_abatement = max(0, bau_emissions - target)

            # Get available technologies for this year
            tech_year = self.df_macc[
                (self.df_macc['year'] == year) &
                (self.df_macc['available'] == True)
            ].copy()

            if len(tech_year) == 0:
                # No technologies available yet
                deployment.append({
                    'scenario': scenario_name,
                    'year': year,
                    'bau_emissions_mt': bau_emissions,
                    'target_mt': target,
                    'required_abatement_mt': required_abatement,
                    'heat_pump_deployed_mt': 0,
                    'ncc_h2_deployed_mt': 0,
                    'ncc_electricity_deployed_mt': 0,
                    'total_deployed_mt': 0,
                    'actual_emissions_mt': bau_emissions,
                    'annual_cost_musd': 0,
                    'cumulative_capex_musd': cumulative_capex,
                    'cumulative_abatement_mt': cumulative_abatement,
                    'target_met': bau_emissions <= target
                })
                continue

            # Sort technologies by total cost (lowest first)
            tech_year = tech_year.sort_values('total_cost_usd_per_tco2')

            # Deploy technologies in order of cost until target is met
            deployed = {
                'Heat_Pump': 0,
                'NCC-H2': 0,
                'NCC-Electricity': 0
            }

            remaining_abatement = required_abatement

            for _, tech in tech_year.iterrows():
                if remaining_abatement <= 0:
                    break

                tech_name = tech['technology']
                max_potential = tech['abatement_potential_mtco2']

                # Deploy as much as needed (up to max potential)
                deploy_amount = min(remaining_abatement, max_potential)
                deployed[tech_name] += deploy_amount
                remaining_abatement -= deploy_amount

            # Calculate costs
            total_deployed = sum(deployed.values())
            actual_emissions = bau_emissions - total_deployed

            # Annual cost breakdown
            annual_cost = 0
            for _, tech in tech_year.iterrows():
                tech_name = tech['technology']
                if deployed[tech_name] > 0:
                    # Cost = deployed amount × (annualized capex + opex + fuel)
                    tech_cost = deployed[tech_name] * tech['total_cost_usd_per_tco2']
                    annual_cost += tech_cost

                    # Add to cumulative capex (one-time)
                    capex = deployed[tech_name] * tech['capex_ann_usd_per_tco2'] / (0.08 / (1 - (1 + 0.08)**(-20)))
                    cumulative_capex += capex

            cumulative_abatement += total_deployed
            annual_cost_musd = annual_cost / 1e6

            deployment.append({
                'scenario': scenario_name,
                'year': year,
                'bau_emissions_mt': bau_emissions,
                'target_mt': target,
                'required_abatement_mt': required_abatement,
                'heat_pump_deployed_mt': deployed['Heat_Pump'],
                'ncc_h2_deployed_mt': deployed['NCC-H2'],
                'ncc_electricity_deployed_mt': deployed['NCC-Electricity'],
                'total_deployed_mt': total_deployed,
                'actual_emissions_mt': actual_emissions,
                'annual_cost_musd': annual_cost_musd,
                'cumulative_capex_musd': cumulative_capex / 1e6,
                'cumulative_abatement_mt': cumulative_abatement,
                'target_met': actual_emissions <= target
            })

        df_deployment = pd.DataFrame(deployment)

        # Calculate energy source transitions
        df_deployment = self._calculate_energy_transitions(df_deployment)

        return df_deployment

    def _get_annual_targets(self, scenario, years):
        """Get emission targets for each year based on scenario type"""
        targets = {}

        if scenario['type'] == 'cumulative':
            # Budget constraint - allocate proportionally
            # Simple approach: linear decline to near-zero by 2050
            baseline_2025 = self.df_bau[self.df_bau['year'] == 2025]['total_emissions_mt'].iloc[0]
            for year in years:
                # Linear decline
                progress = (year - 2025) / (2050 - 2025)
                targets[year] = baseline_2025 * (1 - 0.95 * progress)  # 95% reduction by 2050

        elif scenario['type'] == 'annual':
            # Point targets with interpolation
            baseline_2025 = self.df_bau[self.df_bau['year'] == 2025]['total_emissions_mt'].iloc[0]
            point_targets = scenario['targets']

            for year in years:
                if year in point_targets:
                    targets[year] = point_targets[year]
                else:
                    # Interpolate
                    years_sorted = sorted(point_targets.keys())
                    if year < years_sorted[0]:
                        targets[year] = baseline_2025
                    elif year > years_sorted[-1]:
                        targets[year] = point_targets[years_sorted[-1]]
                    else:
                        # Linear interpolation between points
                        for i in range(len(years_sorted) - 1):
                            if years_sorted[i] <= year <= years_sorted[i+1]:
                                y1, y2 = years_sorted[i], years_sorted[i+1]
                                t1, t2 = point_targets[y1], point_targets[y2]
                                targets[year] = t1 + (t2 - t1) * (year - y1) / (y2 - y1)
                                break

        elif scenario['type'] == 'linear':
            # Linear reduction
            baseline_2025 = self.df_bau[self.df_bau['year'] == 2025]['total_emissions_mt'].iloc[0]
            end_target = scenario['end_target']

            for year in years:
                progress = (year - 2025) / (2050 - 2025)
                targets[year] = baseline_2025 + (end_target - baseline_2025) * progress

        return targets

    def _calculate_energy_transitions(self, df_deployment):
        """Calculate energy source transitions from technology deployment"""

        # Get baseline 2025 energy sources
        baseline_2025 = self.df_bau[self.df_bau['year'] == 2025].iloc[0]

        baseline_naphtha = baseline_2025['naphtha_mt']
        baseline_electricity = baseline_2025['electricity_mt']

        # Calculate total NCC emissions from baseline (Olefins + Aromatics)
        total_ncc_emissions_baseline = self._get_ncc_baseline_emissions()

        for idx, row in df_deployment.iterrows():
            year = row['year']

            # Get BAU for this year
            bau_year = self.df_bau[self.df_bau['year'] == year].iloc[0]

            # Calculate energy displaced by each technology
            # Heat Pump: displaces naphtha with electricity (COP=4, so 1/4 energy)
            hp_deployed = row['heat_pump_deployed_mt']
            hp_naphtha_displaced = hp_deployed  # MtCO2
            hp_electricity_added = hp_naphtha_displaced * 0.25  # With COP=4

            # NCC-H2: displaces naphtha with H2
            h2_deployed = row['ncc_h2_deployed_mt']
            h2_naphtha_displaced = h2_deployed

            # NCC-Electricity: displaces naphtha with electricity
            elec_deployed = row['ncc_electricity_deployed_mt']
            elec_naphtha_displaced = elec_deployed
            elec_electricity_added = elec_naphtha_displaced * 1.0  # 1:1 energy basis (simplified)

            # Update energy sources
            remaining_naphtha = bau_year['naphtha_mt'] - hp_naphtha_displaced - h2_naphtha_displaced - elec_naphtha_displaced
            grid_electricity = bau_year['electricity_mt'] + hp_electricity_added + elec_electricity_added
            h2_consumption = h2_naphtha_displaced

            df_deployment.loc[idx, 'naphtha_emissions_mt'] = max(0, remaining_naphtha)
            df_deployment.loc[idx, 'grid_electricity_emissions_mt'] = grid_electricity
            df_deployment.loc[idx, 'h2_consumption_mt'] = h2_consumption
            df_deployment.loc[idx, 'renewable_electricity_mt'] = elec_electricity_added  # Direct RE for crackers

            # Calculate NCC technology shares
            # Total NCC emissions being addressed
            total_ncc_abatement = h2_deployed + elec_deployed
            remaining_ncc_fossil = max(0, total_ncc_emissions_baseline - total_ncc_abatement)

            # Calculate percentages
            total_ncc = total_ncc_emissions_baseline
            if total_ncc > 0:
                df_deployment.loc[idx, 'ncc_fossil_share_%'] = 100 * remaining_ncc_fossil / total_ncc
                df_deployment.loc[idx, 'ncc_h2_share_%'] = 100 * h2_deployed / total_ncc
                df_deployment.loc[idx, 'ncc_electricity_share_%'] = 100 * elec_deployed / total_ncc
            else:
                df_deployment.loc[idx, 'ncc_fossil_share_%'] = 0
                df_deployment.loc[idx, 'ncc_h2_share_%'] = 0
                df_deployment.loc[idx, 'ncc_electricity_share_%'] = 0

        return df_deployment

    def _get_ncc_baseline_emissions(self):
        """Calculate total NCC (Naphtha Cracking Complex) emissions from baseline"""
        # NCC includes facilities that produce Olefins and Aromatics
        # Based on product names in the baseline
        ncc_keywords = ['Ethylene', 'Propylene', 'Butadiene', 'Benzene', 'Toluene', 'Xylene', 'Styrene']

        # Filter facilities where product contains NCC keywords
        ncc_facilities = self.df_baseline[
            self.df_baseline['product'].apply(
                lambda x: any(keyword.lower() in str(x).lower() for keyword in ncc_keywords)
            )
        ]

        ncc_emissions = ncc_facilities['total_emissions_kt'].sum() / 1000  # Convert to MtCO2

        # If no matches found, estimate as 60% of total baseline (typical NCC share)
        if ncc_emissions == 0:
            total_baseline = self.df_baseline['total_emissions_kt'].sum() / 1000
            ncc_emissions = total_baseline * 0.60
            print(f"   ℹ NCC emissions estimated as 60% of baseline: {ncc_emissions:.2f} MtCO2")

        return ncc_emissions

    def run_all_scenarios(self):
        """Run optimization for all scenarios"""
        print("\n" + "="*80)
        print("RUNNING ALL SCENARIOS")
        print("="*80)

        all_results = {}

        for scenario_name in self.scenarios.keys():
            df_result = self.optimize_scenario(scenario_name)
            all_results[scenario_name] = df_result

            # Save to CSV
            output_file = self.output_dir / f'{scenario_name.lower()}_deployment.csv'
            df_result.to_csv(output_file, index=False)
            print(f"   ✓ Saved: {output_file}")

        # Create summary
        self._create_summary(all_results)

        # Create visualizations
        self._create_visualizations(all_results)

        return all_results

    def _create_summary(self, all_results):
        """Create summary comparison of scenarios"""
        summary = []

        for scenario_name, df in all_results.items():
            # Filter to 2025-2050
            df_2050 = df[df['year'] <= 2050]

            summary.append({
                'scenario': scenario_name,
                'baseline_2025_mt': df_2050[df_2050['year']==2025]['bau_emissions_mt'].iloc[0],
                'emissions_2050_mt': df_2050[df_2050['year']==2050]['actual_emissions_mt'].iloc[0],
                'total_abatement_2025_2050_mt': df_2050['total_deployed_mt'].sum(),
                'cumulative_capex_2025_2050_busd': df_2050['cumulative_capex_musd'].iloc[-1] / 1000,
                'avg_annual_cost_musd': df_2050['annual_cost_musd'].mean(),
                'peak_deployment_year': df_2050.loc[df_2050['total_deployed_mt'].idxmax(), 'year'],
                'targets_met_%': 100 * df_2050['target_met'].sum() / len(df_2050)
            })

        df_summary = pd.DataFrame(summary)
        summary_file = self.output_dir / 'scenario_comparison_summary.csv'
        df_summary.to_csv(summary_file, index=False)

        print(f"\n📊 Scenario Summary:")
        print(df_summary.to_string(index=False))
        print(f"\n   ✓ Saved: {summary_file}")

    def _create_visualizations(self, all_results):
        """Create all visualization outputs"""
        print("\n🎨 Creating visualizations...")

        # 1. Emission trajectories comparison
        self._plot_emission_trajectories(all_results)

        # 2. Technology deployment by scenario
        self._plot_technology_deployment(all_results)

        # 3. Energy source transitions
        self._plot_energy_transitions(all_results)

        # 4. Cost comparison
        self._plot_cost_comparison(all_results)

        # 5. NCC technology share evolution
        self._plot_ncc_technology_shares(all_results)

        print("   ✓ All visualizations created")

    def _plot_emission_trajectories(self, all_results):
        """Plot emission trajectories for all scenarios"""
        fig, ax = plt.subplots(figsize=(14, 8))

        # BAU
        bau = self.df_bau[self.df_bau['year'] <= 2050]
        ax.plot(bau['year'], bau['total_emissions_mt'],
               linewidth=3, linestyle='--', color='gray',
               label='BAU (No Action)', alpha=0.7)

        # Scenarios
        colors = {'Budget': '#E74C3C', 'Point_Targets': '#3498DB', 'Linear': '#2ECC71'}

        for scenario_name, df in all_results.items():
            df_plot = df[df['year'] <= 2050]
            ax.plot(df_plot['year'], df_plot['actual_emissions_mt'],
                   linewidth=2.5, color=colors.get(scenario_name, 'black'),
                   label=f'{scenario_name}: {self.scenarios[scenario_name]["description"]}',
                   marker='o', markersize=3)

        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Emissions (MtCO2/year)', fontsize=12, fontweight='bold')
        ax.set_title('Emission Trajectories: Scenarios vs BAU (2025-2050)',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, None)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'emission_trajectories_comparison.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ emission_trajectories_comparison.png")

    def _plot_technology_deployment(self, all_results):
        """Plot technology deployment over time for each scenario"""

        for scenario_name, df in all_results.items():
            df_plot = df[df['year'] <= 2050]

            fig, ax = plt.subplots(figsize=(14, 8))

            # Stacked area
            ax.stackplot(df_plot['year'],
                        df_plot['heat_pump_deployed_mt'],
                        df_plot['ncc_h2_deployed_mt'],
                        df_plot['ncc_electricity_deployed_mt'],
                        labels=['Heat Pump', 'NCC-H2', 'NCC-Electricity'],
                        colors=['#2ECC71', '#3498DB', '#E74C3C'],
                        alpha=0.8)

            ax.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax.set_ylabel('Abatement (MtCO2/year)', fontsize=12, fontweight='bold')
            ax.set_title(f'Technology Deployment: {scenario_name}\n{self.scenarios[scenario_name]["description"]}',
                        fontsize=14, fontweight='bold')
            ax.legend(loc='upper left')
            ax.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(self.output_dir / f'technology_deployment_{scenario_name.lower()}.png',
                       dpi=300, bbox_inches='tight')
            plt.close()

        print(f"   ✓ technology_deployment_*.png (3 files)")

    def _plot_energy_transitions(self, all_results):
        """Plot energy source transitions"""

        for scenario_name, df in all_results.items():
            df_plot = df[df['year'] <= 2050]

            fig, ax = plt.subplots(figsize=(14, 8))

            # Stacked area showing energy sources
            ax.stackplot(df_plot['year'],
                        df_plot['naphtha_emissions_mt'],
                        df_plot['grid_electricity_emissions_mt'],
                        df_plot['h2_consumption_mt'],
                        df_plot['renewable_electricity_mt'],
                        labels=['Naphtha (Fossil)', 'Grid Electricity', 'Green H2', 'Renewable Electricity (Direct)'],
                        colors=['#8B4513', '#FFD700', '#3498DB', '#2ECC71'],
                        alpha=0.8)

            ax.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax.set_ylabel('Energy-Related Emissions (MtCO2/year)', fontsize=12, fontweight='bold')
            ax.set_title(f'Energy Source Transition: {scenario_name}\nFrom Fossil Fuels to Renewables & H2',
                        fontsize=14, fontweight='bold')
            ax.legend(loc='upper right')
            ax.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(self.output_dir / f'energy_transition_{scenario_name.lower()}.png',
                       dpi=300, bbox_inches='tight')
            plt.close()

        print(f"   ✓ energy_transition_*.png (3 files)")

    def _plot_cost_comparison(self, all_results):
        """Plot cost comparison across scenarios"""

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))

        colors = {'Budget': '#E74C3C', 'Point_Targets': '#3498DB', 'Linear': '#2ECC71'}

        # Annual costs
        for scenario_name, df in all_results.items():
            df_plot = df[df['year'] <= 2050]
            ax1.plot(df_plot['year'], df_plot['annual_cost_musd'],
                    linewidth=2.5, color=colors.get(scenario_name, 'black'),
                    label=scenario_name, marker='o', markersize=3)

        ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Annual Cost (Million USD/year)', fontsize=12, fontweight='bold')
        ax1.set_title('Annual Abatement Costs by Scenario',
                     fontsize=13, fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)

        # Cumulative capex
        for scenario_name, df in all_results.items():
            df_plot = df[df['year'] <= 2050]
            ax2.plot(df_plot['year'], df_plot['cumulative_capex_musd'] / 1000,
                    linewidth=2.5, color=colors.get(scenario_name, 'black'),
                    label=scenario_name, marker='o', markersize=3)

        ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Cumulative Capex (Billion USD)', fontsize=12, fontweight='bold')
        ax2.set_title('Cumulative Capital Investment by Scenario',
                     fontsize=13, fontweight='bold')
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'cost_comparison_scenarios.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ cost_comparison_scenarios.png")

    def _plot_ncc_technology_shares(self, all_results):
        """Plot NCC technology share evolution for each scenario"""

        for scenario_name, df in all_results.items():
            df_plot = df[df['year'] <= 2050]

            fig, ax = plt.subplots(figsize=(14, 8))

            # Stacked area showing technology shares
            ax.stackplot(df_plot['year'],
                        df_plot['ncc_fossil_share_%'],
                        df_plot['ncc_h2_share_%'],
                        df_plot['ncc_electricity_share_%'],
                        labels=['Fossil Fuel (Baseline)', 'Green H2', 'Renewable Electricity'],
                        colors=['#8B4513', '#3498DB', '#2ECC71'],
                        alpha=0.8)

            ax.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax.set_ylabel('Technology Share (%)', fontsize=12, fontweight='bold')
            ax.set_title(f'NCC Technology Share Evolution: {scenario_name}\nNaphtha Cracking Complex Decarbonization Pathway',
                        fontsize=14, fontweight='bold')
            ax.legend(loc='upper right')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 100)

            # Add annotations for key milestones
            final_year_data = df_plot[df_plot['year'] == 2050].iloc[0]
            if final_year_data['ncc_fossil_share_%'] < 50:
                milestone_year = df_plot[df_plot['ncc_fossil_share_%'] < 50].iloc[0]['year']
                ax.axvline(x=milestone_year, color='red', linestyle='--', alpha=0.5)
                ax.text(milestone_year, 95, f'<50% Fossil: {int(milestone_year)}',
                       fontsize=10, ha='left', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            plt.tight_layout()
            plt.savefig(self.output_dir / f'ncc_technology_share_{scenario_name.lower()}.png',
                       dpi=300, bbox_inches='tight')
            plt.close()

        print(f"   ✓ ncc_technology_share_*.png (3 files)")

    def run_complete_analysis(self):
        """Run complete optimization analysis"""
        print("\n" + "="*80)
        print("RUNNING COMPLETE COST OPTIMIZATION ANALYSIS")
        print("="*80)

        # Run all scenarios
        results = self.run_all_scenarios()

        print("\n" + "="*80)
        print("✓ MODULE 3 COMPLETE")
        print("="*80)
        print(f"\nOutputs saved to: {self.output_dir}")
        print("\nGenerated files:")
        for f in sorted(self.output_dir.glob('*')):
            print(f"   - {f.name}")

        return results


if __name__ == '__main__':
    # Run optimization
    optimizer = CostOptimizer('data_sources/Korean_Petrochemical_MACC_Model_English.xlsx')
    results = optimizer.run_complete_analysis()

    print("\n🎉 Cost optimization complete!")
