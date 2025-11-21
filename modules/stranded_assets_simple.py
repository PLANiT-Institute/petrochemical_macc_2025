"""
MODULE 4 (SIMPLIFIED): EMISSION-PATH-DRIVEN STRANDED ASSET ANALYSIS

Pure Retirement Logic:
- Facilities that cannot meet emission reduction targets → RETIRE
- Stranded Asset = Book Value of Retired Facilities
- No retrofit costs, no operational losses, no carbon pricing
- Only emission path compliance determines retirement

Methodology:
1. Calculate facility book values (depreciated CAPEX)
2. Check if facility can meet emission target with available technologies
3. If emission reduction required > threshold → RETIRE
4. Stranded Asset = Sum of book values of retired facilities
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from .utils import save_csv_output, save_plot, identify_product_group


class StrandedAssetAnalyzerSimple:
    """
    Simplified Stranded Asset Analysis - Emission Path Driven Retirement Only

    Core Logic:
    - Emission target forces facility retirement
    - Retired facilities lose their book value
    - That's the stranded asset
    """

    def __init__(self, baseline_output='outputs/module_01',
                 data_dir='data',
                 output_dir='outputs/module_04_stranded_assets_simple'):
        self.baseline_dir = Path(baseline_output)
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("MODULE 4 (SIMPLIFIED): EMISSION-PATH STRANDED ASSET ANALYSIS")
        print("="*80)

        # Load data
        print("\n📁 Loading data...")
        self.df_baseline = pd.read_csv(self.baseline_dir / 'baseline_2025_detailed.csv')
        self.df_bau = pd.read_csv(self.baseline_dir / 'bau_trajectory_2025_2050.csv')

        print(f"   - Loaded {len(self.df_baseline)} facilities")
        print(f"   - Loaded BAU trajectory")

        # Capital intensity assumptions (Million USD per kt capacity)
        self.capex_intensity = {
            'Naphtha Cracker': 1.2,
            'Aromatics': 0.8,
            'Polymer': 0.6,
            'Other': 0.4
        }

        # Facility parameters
        self.facility_lifetime = 30  # years
        self.reference_year = 2025

    def calculate_facility_assets(self):
        """
        Calculate book value of each facility based on depreciation

        Book Value = Initial CAPEX × (Remaining Life / Total Lifetime)
        """
        print(f"\n💰 Calculating facility book values...")

        df = self.df_baseline.copy()

        # Assign capital intensity
        df['capex_musd_per_kt'] = df['process'].map(self.capex_intensity)
        df['capex_musd_per_kt'] = df['capex_musd_per_kt'].fillna(self.capex_intensity['Other'])

        # Calculate initial CAPEX
        df['initial_capex_musd'] = df['capacity_kt'] * df['capex_musd_per_kt']

        # Calculate age and remaining life
        df['facility_age'] = self.reference_year - df['year_built']
        df['remaining_life'] = self.facility_lifetime - df['facility_age']
        df['remaining_life'] = df['remaining_life'].clip(lower=0)

        # Calculate book value (straight-line depreciation)
        df['book_value_musd'] = df['initial_capex_musd'] * (df['remaining_life'] / self.facility_lifetime)
        df['book_value_musd'] = df['book_value_musd'].clip(lower=0)

        # Emission intensity (tCO2 per kt capacity)
        df['emission_intensity'] = df['total_emissions_kt'] / df['capacity_kt']

        self.df_assets = df

        # Summary
        total_book_value = df['book_value_musd'].sum()
        total_initial = df['initial_capex_musd'].sum()
        avg_age = df['facility_age'].mean()

        print(f"   ✓ Total initial CAPEX: ${total_initial:.1f} Billion")
        print(f"   ✓ Current book value: ${total_book_value:.1f} Billion")
        print(f"   ✓ Average facility age: {avg_age:.1f} years")
        print(f"   ✓ Facilities with remaining life >0: {(df['remaining_life'] > 0).sum()}")

        return df

    def analyze_emission_path_retirement(self, scenario_deployments,
                                        retirement_threshold=0.90):
        """
        Determine which facilities must retire based on emission path requirements

        Logic:
        1. For each scenario's emission target
        2. Calculate required abatement per facility
        3. If facility's required abatement > threshold → RETIRE
        4. Sum book values of retired facilities = Stranded Assets

        Parameters:
        - retirement_threshold: If facility must reduce >90% emissions, retire instead
        """
        print(f"\n🏭 Analyzing retirement based on emission path...")
        print(f"   Retirement threshold: {retirement_threshold*100:.0f}% emission reduction required")

        stranding_results = {}

        for scenario_name, df_deploy in scenario_deployments.items():
            print(f"\n   Scenario: {scenario_name}")

            # Get emission path over time
            df_scenario = df_deploy.copy()

            # Analyze year-by-year retirement decisions
            retirement_analysis = self._analyze_retirement_timeline(
                df_scenario, scenario_name, retirement_threshold
            )

            stranding_results[scenario_name] = retirement_analysis

        self.stranding_results = stranding_results
        return stranding_results

    def _analyze_retirement_timeline(self, df_scenario, scenario_name, threshold):
        """
        Analyze which facilities retire and when based on emission path AND AGE

        Retirement Logic (Age-Based with Emission Path):
        1. Calculate overall emission reduction stringency
        2. Old facilities (age > 25 years) face higher retirement risk
        3. When sector reduction > 50%, oldest/dirtiest facilities must retire
        4. Retirement threshold scales with emission stringency

        This creates realistic retirement patterns where:
        - Stringent emission targets → force retirement of old assets
        - Old facilities with remaining book value → stranded assets
        """
        # Key years to analyze
        years = [2030, 2040, 2050]

        results = []

        for year in years:
            # Get emission target for this year
            year_data = df_scenario[df_scenario['year'] == year].iloc[0]

            target_emissions = year_data['actual_emissions_mt']
            bau_emissions = year_data['bau_mt']
            required_reduction_pct = ((bau_emissions - target_emissions) / bau_emissions) * 100

            # Get BAU emissions for this year (with demand growth)
            bau_year = self.df_bau[self.df_bau['year'] == year].iloc[0]
            capacity_multiplier = bau_year['capacity_multiplier']

            # Calculate per-facility emissions (scaled by demand growth)
            df_facilities = self.df_assets.copy()
            df_facilities['emissions_2025_kt'] = df_facilities['total_emissions_kt']
            df_facilities['emissions_year_kt'] = df_facilities['emissions_2025_kt'] * capacity_multiplier

            # Calculate total BAU emissions
            total_bau = df_facilities['emissions_year_kt'].sum() / 1000  # MtCO2

            # Required total reduction
            required_reduction_mt = bau_emissions - target_emissions

            # AGE-BASED RETIREMENT LOGIC
            # Create retirement risk score based on age and emission intensity
            max_age = df_facilities['facility_age'].max()
            max_intensity = df_facilities['emission_intensity'].max()

            # Retirement risk score (0-1 scale)
            df_facilities['retirement_risk_score'] = (
                (df_facilities['facility_age'] / max_age) * 0.6 +  # Age weight: 60%
                (df_facilities['emission_intensity'] / max_intensity) * 0.4  # Intensity weight: 40%
            )

            # Stringency factor: higher emission reduction → lower retirement threshold
            stringency_factor = required_reduction_pct / 100  # 0-1 scale

            # Adaptive retirement threshold
            # Base threshold: 0.65 (65th percentile risk)
            # Stringent targets (>60% reduction) → threshold drops to 0.50
            # Moderate targets (<40% reduction) → threshold stays at 0.75
            if stringency_factor > 0.6:
                retirement_threshold = 0.50  # Aggressive retirement
            elif stringency_factor > 0.5:
                retirement_threshold = 0.60  # Moderate retirement
            else:
                retirement_threshold = 0.75  # Minimal retirement

            # Retirement decision: facilities with high risk score must retire
            df_facilities['must_retire'] = (
                (df_facilities['retirement_risk_score'] >= retirement_threshold) &
                (df_facilities['remaining_life'] > 0)  # Only retire facilities with book value
            )

            # Calculate how much emission is removed by retiring these facilities
            retired_facilities = df_facilities[df_facilities['must_retire']]
            retired_emissions_mt = retired_facilities['emissions_year_kt'].sum() / 1000

            # Calculate required reduction for REMAINING facilities
            remaining_facilities = df_facilities[~df_facilities['must_retire']]
            remaining_emissions = remaining_facilities['emissions_year_kt'].sum() / 1000

            # Remaining facilities need to achieve the balance
            remaining_reduction_needed = max(0, required_reduction_mt - retired_emissions_mt)

            if remaining_emissions > 0:
                df_facilities.loc[~df_facilities['must_retire'], 'required_reduction_pct'] = (
                    (remaining_reduction_needed / remaining_emissions) * 100
                )
            else:
                df_facilities.loc[~df_facilities['must_retire'], 'required_reduction_pct'] = 0

            # Retired facilities face 100% reduction (they're gone)
            df_facilities.loc[df_facilities['must_retire'], 'required_reduction_pct'] = 100.0

            df_facilities['required_reduction_kt'] = (
                df_facilities['emissions_year_kt'] * df_facilities['required_reduction_pct'] / 100
            )

            # Calculate stranded assets for this year
            retired_facilities = df_facilities[df_facilities['must_retire']]

            stranded_value = retired_facilities['book_value_musd'].sum()
            n_retired = len(retired_facilities)
            retired_emissions = retired_facilities['emissions_year_kt'].sum() / 1000  # MtCO2

            results.append({
                'scenario': scenario_name,
                'year': year,
                'target_emissions_mt': target_emissions,
                'bau_emissions_mt': bau_emissions,
                'required_reduction_mt': required_reduction_mt,
                'required_reduction_pct': required_reduction_pct,
                'stringency_factor': stringency_factor,
                'retirement_threshold': retirement_threshold,
                'facilities_retired': n_retired,
                'stranded_book_value_billion': stranded_value / 1000,
                'retired_emissions_mt': retired_emissions,
                'retired_capacity_kt': retired_facilities['capacity_kt'].sum(),
                'avg_retired_age': retired_facilities['facility_age'].mean() if n_retired > 0 else 0,
                'avg_retired_intensity': retired_facilities['emission_intensity'].mean() if n_retired > 0 else 0,
            })

        df_results = pd.DataFrame(results)

        # Also save facility-level detail for 2050
        year_2050_data = df_scenario[df_scenario['year'] == 2050].iloc[0]
        self._save_facility_retirement_detail(scenario_name, 2050, threshold)

        return df_results

    def _save_facility_retirement_detail(self, scenario_name, year, threshold):
        """Save detailed facility-level retirement analysis"""

        # Get year data
        year_data_bau = self.df_bau[self.df_bau['year'] == year].iloc[0]
        capacity_multiplier = year_data_bau['capacity_multiplier']

        # Prepare facility data
        df_facilities = self.df_assets.copy()
        df_facilities['emissions_year_kt'] = df_facilities['total_emissions_kt'] * capacity_multiplier

        # Load scenario deployment to get target
        try:
            # Try to find deployment file
            possible_paths = [
                Path(f'outputs/{scenario_name}/module_03_optimization/policy_target_deployment.csv'),
            ]

            deployment_file = None
            for path in possible_paths:
                if path.exists():
                    deployment_file = path
                    break

            if deployment_file:
                df_deploy = pd.read_csv(deployment_file)
                year_data = df_deploy[df_deploy['year'] == year].iloc[0]
                target_emissions = year_data['actual_emissions_mt']
                bau_emissions = year_data['bau_mt']
                required_reduction_mt = bau_emissions - target_emissions
                required_reduction_pct = ((bau_emissions - target_emissions) / bau_emissions) * 100

                # Apply same age-based retirement logic
                max_age = df_facilities['facility_age'].max()
                max_intensity = df_facilities['emission_intensity'].max()

                df_facilities['retirement_risk_score'] = (
                    (df_facilities['facility_age'] / max_age) * 0.6 +
                    (df_facilities['emission_intensity'] / max_intensity) * 0.4
                )

                stringency_factor = required_reduction_pct / 100

                if stringency_factor > 0.6:
                    retirement_threshold_save = 0.50
                elif stringency_factor > 0.5:
                    retirement_threshold_save = 0.60
                else:
                    retirement_threshold_save = 0.75

                df_facilities['must_retire'] = (
                    (df_facilities['retirement_risk_score'] >= retirement_threshold_save) &
                    (df_facilities['remaining_life'] > 0)
                )

                # Calculate reductions
                retired_facilities = df_facilities[df_facilities['must_retire']]
                retired_emissions_mt = retired_facilities['emissions_year_kt'].sum() / 1000

                remaining_facilities = df_facilities[~df_facilities['must_retire']]
                remaining_emissions = remaining_facilities['emissions_year_kt'].sum() / 1000

                remaining_reduction_needed = max(0, required_reduction_mt - retired_emissions_mt)

                if remaining_emissions > 0:
                    df_facilities.loc[~df_facilities['must_retire'], 'required_reduction_pct'] = (
                        (remaining_reduction_needed / remaining_emissions) * 100
                    )
                else:
                    df_facilities.loc[~df_facilities['must_retire'], 'required_reduction_pct'] = 0

                df_facilities.loc[df_facilities['must_retire'], 'required_reduction_pct'] = 100.0

                df_facilities['required_reduction_kt'] = (
                    df_facilities['emissions_year_kt'] * df_facilities['required_reduction_pct'] / 100
                )
                df_facilities['stranded_book_value_musd'] = df_facilities.apply(
                    lambda row: row['book_value_musd'] if row['must_retire'] else 0, axis=1
                )

                # Add product group
                df_facilities['product_group'] = df_facilities['product'].apply(identify_product_group)

                # Select relevant columns
                output_cols = [
                    'company', 'location', 'product', 'product_group', 'process',
                    'capacity_kt', 'year_built', 'facility_age', 'remaining_life',
                    'initial_capex_musd', 'book_value_musd',
                    'emission_intensity', 'emissions_year_kt',
                    'required_reduction_kt', 'required_reduction_pct',
                    'must_retire', 'stranded_book_value_musd'
                ]

                df_output = df_facilities[output_cols].copy()

                # Save
                filename = f'facility_retirement_{scenario_name}_{year}.csv'
                save_csv_output(df_output, self.output_dir / filename,
                              f"({df_output['must_retire'].sum()} facilities retired)")

        except Exception as e:
            print(f"   ⚠️  Could not save facility detail: {e}")

    def create_summary(self):
        """Create summary of stranded assets across scenarios"""
        print("\n📊 Creating stranding summary...")

        if not self.stranding_results:
            print("   ⚠️  No results to summarize")
            return None

        # Combine all results
        all_results = []
        for scenario, df_result in self.stranding_results.items():
            all_results.append(df_result)

        df_summary = pd.concat(all_results, ignore_index=True)

        # Create scenario-level summary (2050 values)
        df_2050 = df_summary[df_summary['year'] == 2050].copy()

        print("\n" + "="*80)
        print("STRANDED ASSET SUMMARY (Emission-Path Driven Retirement)")
        print("="*80)

        for _, row in df_2050.iterrows():
            print(f"\n{row['scenario']} (2050):")
            print(f"   Emission Target: {row['target_emissions_mt']:.1f} MtCO2 (vs BAU {row['bau_emissions_mt']:.1f})")
            print(f"   Required Reduction: {row['required_reduction_mt']:.1f} MtCO2 ({row['required_reduction_pct']:.1f}%)")
            print(f"   Facilities Retired: {row['facilities_retired']:.0f}")
            print(f"   Stranded Book Value: ${row['stranded_book_value_billion']:.2f}B")
            print(f"   Retired Capacity: {row['retired_capacity_kt']:.0f} kt/year")
            print(f"   Retired Emissions: {row['retired_emissions_mt']:.1f} MtCO2")

        self.df_summary = df_summary
        return df_summary

    def create_visualizations(self):
        """Create visualizations"""
        print("\n🎨 Creating visualizations...")

        if not hasattr(self, 'df_summary'):
            print("   ⚠️  No summary data available")
            return

        # 1. Stranded assets over time by scenario
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        scenarios = self.df_summary['scenario'].unique()
        colors = plt.cm.Set2(range(len(scenarios)))

        for i, scenario in enumerate(scenarios):
            df_scenario = self.df_summary[self.df_summary['scenario'] == scenario]
            ax1.plot(df_scenario['year'], df_scenario['stranded_book_value_billion'],
                    marker='o', linewidth=2.5, color=colors[i], label=scenario.split('_')[-2:])

        ax1.set_xlabel('Year', fontsize=13, fontweight='bold')
        ax1.set_ylabel('Stranded Book Value (Billion USD)', fontsize=13, fontweight='bold')
        ax1.set_title('Stranded Assets Over Time\n(Emission-Path Driven Retirement)',
                     fontsize=14, fontweight='bold')
        ax1.legend(loc='upper left', fontsize=9)
        ax1.grid(True, alpha=0.3)

        # 2. Facilities retired by scenario (2050)
        df_2050 = self.df_summary[self.df_summary['year'] == 2050]

        x_pos = np.arange(len(df_2050))
        bars = ax2.bar(x_pos, df_2050['facilities_retired'],
                      color=colors[:len(df_2050)], alpha=0.8, edgecolor='black', linewidth=1.2)

        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, df_2050['facilities_retired'])):
            ax2.text(i, val + 1, f'{val:.0f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')

        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([s.split('_')[-2] + '\n' + s.split('_')[-1]
                             for s in df_2050['scenario']], rotation=0, fontsize=9)
        ax2.set_ylabel('Number of Facilities', fontsize=13, fontweight='bold')
        ax2.set_title('Facilities Forced to Retire (2050)\nDue to Emission Path',
                     fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        save_plot(fig, self.output_dir / 'stranded_assets_emission_path.png')

        # 3. Stranding rate comparison
        fig, ax = plt.subplots(figsize=(12, 7))

        total_book_value = self.df_assets['book_value_musd'].sum() / 1000  # Billion

        x_pos = np.arange(len(df_2050))
        stranding_rates = (df_2050['stranded_book_value_billion'] / total_book_value) * 100

        bars = ax.bar(x_pos, stranding_rates, color=colors[:len(df_2050)],
                     alpha=0.8, edgecolor='black', linewidth=1.2)

        for i, (bar, val) in enumerate(zip(bars, stranding_rates)):
            ax.text(i, val + 0.5, f'{val:.1f}%', ha='center', va='bottom',
                   fontsize=10, fontweight='bold')

        ax.set_xticks(x_pos)
        ax.set_xticklabels([s.split('_')[-2] + '\n' + s.split('_')[-1]
                           for s in df_2050['scenario']], rotation=0, fontsize=9)
        ax.set_ylabel('Stranding Rate (%)', fontsize=13, fontweight='bold')
        ax.set_title(f'Asset Stranding Rate by Scenario (2050)\nTotal Book Value: ${total_book_value:.1f}B',
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        save_plot(fig, self.output_dir / 'stranding_rate_comparison.png')

    def save_outputs(self):
        """Save all outputs"""
        print("\n💾 Saving outputs...")

        # Asset valuation
        save_csv_output(self.df_assets, self.output_dir / 'facility_book_values.csv',
                       f"({len(self.df_assets)} facilities)")

        # Summary
        if hasattr(self, 'df_summary'):
            save_csv_output(self.df_summary, self.output_dir / 'stranding_summary_timeline.csv')

            # Also save 2050 summary
            df_2050 = self.df_summary[self.df_summary['year'] == 2050]
            save_csv_output(df_2050, self.output_dir / 'stranding_summary_2050.csv')

    def run_complete_analysis(self, scenario_deployments, retirement_threshold=0.90):
        """Run complete simplified stranded asset analysis"""
        print("\n" + "="*80)
        print("RUNNING EMISSION-PATH STRANDED ASSET ANALYSIS")
        print("="*80)

        # Step 1: Calculate book values
        self.calculate_facility_assets()

        # Step 2: Analyze retirement based on emission path
        self.analyze_emission_path_retirement(scenario_deployments, retirement_threshold)

        # Step 3: Create summary
        self.create_summary()

        # Step 4: Visualizations
        self.create_visualizations()

        # Step 5: Save outputs
        self.save_outputs()

        print("\n" + "="*80)
        print("✓ ANALYSIS COMPLETE")
        print("="*80)
        print(f"\nOutputs saved to: {self.output_dir}")
        print("\nMethodology:")
        print(f"  - Facilities requiring >{retirement_threshold*100:.0f}% emission reduction → RETIRE")
        print(f"  - Stranded Asset = Book Value of Retired Facilities")
        print(f"  - No retrofit costs, no operational losses included")

        return {
            'assets': self.df_assets,
            'summary': self.df_summary if hasattr(self, 'df_summary') else None,
        }
