"""
MODULE 4: STRANDED ASSET ANALYSIS
Calculate stranded assets for Korea's petrochemical industry under decarbonization scenarios

Stranded Asset Definition:
- Capital investments that lose economic value before the end of their expected useful life
- Due to policy changes, market shifts, or technological disruption (in this case: decarbonization)

Components:
1. Facility-level asset valuation (book value based on age and depreciation)
2. Stranding risk assessment (high-carbon vs low-carbon facilities)
3. Economic loss calculation (premature retirement or forced retrofit costs)
4. Regional and sectoral breakdown
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from .utils import save_csv_output, save_plot, identify_product_group, is_ncc_facility


class StrandedAssetAnalyzer:
    """
    Stranded Asset Analysis for Petrochemical Industry

    Methodology:
    1. Asset Valuation: Estimate book value based on facility age and capital intensity
    2. Stranding Scenarios: Calculate asset losses under different decarbonization pathways
    3. Retrofit vs Retirement: Compare costs of technology deployment vs facility closure
    4. Regional Impact: Assess geographic distribution of stranded assets
    """

    def __init__(self, baseline_output='outputs/module_01',
                 macc_output='outputs/module_02',
                 optimization_output='outputs/module_03',
                 data_dir='data',
                 output_dir='outputs/module_04_stranded_assets'):
        self.baseline_dir = Path(baseline_output)
        self.macc_dir = Path(macc_output)
        self.optimization_dir = Path(optimization_output)
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("MODULE 4: STRANDED ASSET ANALYSIS")
        print("="*80)

        # Load data
        print("\n📁 Loading data...")
        self.df_baseline = pd.read_csv(self.baseline_dir / 'baseline_2025_detailed.csv')
        self.df_macc = pd.read_csv(self.macc_dir / 'macc_annual_2025_2050.csv')
        self.df_tech_params = pd.read_csv(self.data_dir / 'technology_parameters.csv')

        print(f"   - Loaded {len(self.df_baseline)} facilities")
        print(f"   - Loaded MACC data for analysis")

        # Capital intensity assumptions (Million USD per kt capacity)
        # Based on industry benchmarks for Korean petrochemical facilities
        self.capex_intensity = {
            'Naphtha Cracker': 1.2,      # High capital intensity
            'Aromatics': 0.8,             # Medium-high
            'Polymer': 0.6,               # Medium
            'Other': 0.4                  # Lower intensity
        }

        # Facility lifetime and depreciation
        self.facility_lifetime = 30       # years (standard for petrochemical plants)
        self.depreciation_method = 'straight_line'

    def calculate_facility_assets(self, reference_year=2025):
        """
        Calculate book value of assets for each facility

        Book Value = Initial CAPEX × (1 - Age/Lifetime)
        Assumes straight-line depreciation
        """
        print(f"\n💰 Calculating facility asset values (Reference: {reference_year})...")

        df = self.df_baseline.copy()

        # Assign capital intensity based on process type
        df['capex_musd_per_kt'] = df['process'].map(self.capex_intensity)
        df['capex_musd_per_kt'] = df['capex_musd_per_kt'].fillna(self.capex_intensity['Other'])

        # Calculate initial capital investment
        df['initial_capex_musd'] = df['capacity_kt'] * df['capex_musd_per_kt']

        # Calculate facility age
        df['facility_age'] = reference_year - df['year_built']
        df['remaining_life'] = self.facility_lifetime - df['facility_age']
        df['remaining_life'] = df['remaining_life'].clip(lower=0)

        # Calculate book value (straight-line depreciation)
        df['book_value_musd'] = df['initial_capex_musd'] * (df['remaining_life'] / self.facility_lifetime)
        df['book_value_musd'] = df['book_value_musd'].clip(lower=0)

        # Depreciated amount
        df['depreciated_musd'] = df['initial_capex_musd'] - df['book_value_musd']

        # Stranding risk indicator (high emissions = high risk)
        # Normalized emission intensity (tCO2 per kt capacity)
        df['emission_intensity'] = df['total_emissions_kt'] / df['capacity_kt']
        emission_intensity_median = df['emission_intensity'].median()
        df['stranding_risk'] = df['emission_intensity'].apply(
            lambda x: 'High' if x > emission_intensity_median * 1.5 else
                     ('Medium' if x > emission_intensity_median * 0.7 else 'Low')
        )

        self.df_assets = df

        # Summary statistics
        total_assets = df['book_value_musd'].sum()
        total_initial = df['initial_capex_musd'].sum()
        avg_age = df['facility_age'].mean()

        print(f"   - Total initial CAPEX: ${total_initial:.1f} Billion")
        print(f"   - Total book value: ${total_assets:.1f} Billion")
        print(f"   - Average facility age: {avg_age:.1f} years")
        print(f"   - Facilities at risk (High): {(df['stranding_risk']=='High').sum()}")
        print(f"   - Facilities at risk (Medium): {(df['stranding_risk']=='Medium').sum()}")

        return df

    def calculate_stranding_scenarios(self, scenario_deployments):
        """
        Calculate stranded assets under different decarbonization scenarios

        Three types of asset stranding:
        1. Premature Retirement: Facility closes before end of life → book value lost
        2. Forced Retrofit: Technology deployment required → retrofit CAPEX
        3. Operational Stranding: Facility operates but loses competitiveness → partial loss

        Parameters:
        - scenario_deployments: Dict of {scenario_name: deployment_df}
        """
        print("\n🏭 Calculating stranded assets by scenario...")

        stranding_results = {}

        for scenario_name, df_deploy in scenario_deployments.items():
            print(f"\n   Analyzing: {scenario_name}")

            # Get 2050 deployment state
            deploy_2050 = df_deploy[df_deploy['year'] == 2050].iloc[0]

            # Load facility allocation if available
            # Try multiple possible paths
            allocation_file = None
            possible_paths = [
                self.optimization_dir / f'{scenario_name}/module_03_optimization/policy_target_facility_allocation_2050.csv',
                self.optimization_dir / f'{scenario_name.lower().replace(" ", "_")}_facility_allocation_2050.csv',
                Path(f'outputs/{scenario_name}/module_03_optimization/policy_target_facility_allocation_2050.csv'),
            ]

            for path in possible_paths:
                if path.exists():
                    allocation_file = path
                    break

            if allocation_file is None:
                print(f"   ⚠️  Allocation file not found for {scenario_name}, skipping...")
                continue

            try:
                df_allocation = pd.read_csv(allocation_file)

                # Merge with asset data
                df_strand = self.df_assets.merge(
                    df_allocation[['facility_id', 'tech_heat_pump_pct', 'tech_ncc_h2_pct',
                                  'tech_ncc_elec_pct', 'tech_re_ppa_pct', 'abatement_mt']],
                    left_index=True,
                    right_on='facility_id',
                    how='left'
                )

                # Calculate stranding for each facility
                df_strand = self._calculate_facility_stranding(df_strand, deploy_2050)

                stranding_results[scenario_name] = df_strand

            except FileNotFoundError:
                print(f"   ⚠️  Allocation file not found for {scenario_name}, skipping...")
                continue

        self.stranding_results = stranding_results
        return stranding_results

    def _calculate_facility_stranding(self, df, deploy_2050):
        """Calculate stranding for each facility"""

        # Type 1: Premature Retirement (facilities with >80% abatement or very high cost)
        # Assumption: If abatement > 80%, facility is likely to close rather than retrofit
        df['retirement_assumed'] = (df['abatement_mt'] / (df['total_emissions_kt']/1000) > 0.8) & (df['remaining_life'] > 5)

        # Loss from premature retirement = book value
        df['retirement_loss_musd'] = df.apply(
            lambda row: row['book_value_musd'] if row['retirement_assumed'] else 0, axis=1
        )

        # Type 2: Forced Retrofit (facilities with technology deployment)
        # Retrofit CAPEX = Technology CAPEX for deployed abatement
        # Get average technology costs from MACC data (2050)
        macc_2050 = self.df_macc[self.df_macc['year'] == 2050]

        # Average CAPEX per technology (annualized)
        tech_capex = {}
        for tech in ['Heat_Pump', 'NCC-H2', 'NCC-Electricity', 'RE_PPA']:
            tech_data = macc_2050[macc_2050['technology'] == tech]
            if len(tech_data) > 0:
                # Convert annualized CAPEX to total CAPEX (assume 20-year lifetime for tech)
                tech_capex[tech] = tech_data.iloc[0]['capex_ann_usd_per_tco2'] * 20
            else:
                tech_capex[tech] = 0

        # Calculate retrofit costs
        df['retrofit_capex_musd'] = 0.0

        # Heat Pump retrofit
        if 'tech_heat_pump_pct' in df.columns:
            hp_abatement_mt = df['emissions_naphtha_kt'] / 1000 * df['tech_heat_pump_pct'] / 100
            df['retrofit_capex_musd'] += hp_abatement_mt * tech_capex.get('Heat_Pump', 0) * 1e6 / 1e6  # Convert to MUSD

        # NCC-H2 retrofit
        if 'tech_ncc_h2_pct' in df.columns:
            h2_abatement_mt = df['emissions_naphtha_kt'] / 1000 * df['tech_ncc_h2_pct'] / 100
            df['retrofit_capex_musd'] += h2_abatement_mt * tech_capex.get('NCC-H2', 0) * 1e6 / 1e6

        # NCC-Electricity retrofit
        if 'tech_ncc_elec_pct' in df.columns:
            elec_abatement_mt = df['emissions_naphtha_kt'] / 1000 * df['tech_ncc_elec_pct'] / 100
            df['retrofit_capex_musd'] += elec_abatement_mt * tech_capex.get('NCC-Electricity', 0) * 1e6 / 1e6

        # RE_PPA has no CAPEX (contract-based)

        # Type 3: Operational Stranding (facilities that continue but with reduced value)
        # Assumption: Facilities with medium deployment (20-80%) lose 30% of value due to:
        # - Higher operating costs
        # - Carbon pricing exposure
        # - Competitive disadvantage
        df['operational_stranding'] = (df['abatement_mt'] / (df['total_emissions_kt']/1000) >= 0.2) & \
                                      (df['abatement_mt'] / (df['total_emissions_kt']/1000) < 0.8)

        df['operational_loss_musd'] = df.apply(
            lambda row: row['book_value_musd'] * 0.3 if row['operational_stranding'] else 0, axis=1
        )

        # Total stranded asset value
        df['total_stranded_musd'] = df['retirement_loss_musd'] + df['retrofit_capex_musd'] + df['operational_loss_musd']

        return df

    def create_stranding_summary(self):
        """Create summary of stranded assets across scenarios"""
        print("\n📊 Creating stranding summary...")

        summary = []

        for scenario_name, df_strand in self.stranding_results.items():
            summary.append({
                'scenario': scenario_name,
                'total_book_value_billion': df_strand['book_value_musd'].sum() / 1000,
                'retirement_loss_billion': df_strand['retirement_loss_musd'].sum() / 1000,
                'retrofit_capex_billion': df_strand['retrofit_capex_musd'].sum() / 1000,
                'operational_loss_billion': df_strand['operational_loss_musd'].sum() / 1000,
                'total_stranded_billion': df_strand['total_stranded_musd'].sum() / 1000,
                'stranding_rate_pct': (df_strand['total_stranded_musd'].sum() / df_strand['book_value_musd'].sum()) * 100,
                'facilities_retired': df_strand['retirement_assumed'].sum(),
                'facilities_retrofitted': (df_strand['retrofit_capex_musd'] > 0).sum(),
                'facilities_operational_loss': df_strand['operational_stranding'].sum(),
            })

        df_summary = pd.DataFrame(summary)

        print("\n" + "="*80)
        print("STRANDED ASSET SUMMARY")
        print("="*80)
        for _, row in df_summary.iterrows():
            print(f"\n{row['scenario']}:")
            print(f"   Total Book Value: ${row['total_book_value_billion']:.1f}B")
            print(f"   Total Stranded Assets: ${row['total_stranded_billion']:.1f}B ({row['stranding_rate_pct']:.1f}%)")
            print(f"      - Retirement Loss: ${row['retirement_loss_billion']:.1f}B")
            print(f"      - Retrofit CAPEX: ${row['retrofit_capex_billion']:.1f}B")
            print(f"      - Operational Loss: ${row['operational_loss_billion']:.1f}B")
            print(f"   Facilities Impacted:")
            print(f"      - Retired: {row['facilities_retired']:.0f}")
            print(f"      - Retrofitted: {row['facilities_retrofitted']:.0f}")
            print(f"      - Operational Loss: {row['facilities_operational_loss']:.0f}")

        self.df_stranding_summary = df_summary
        return df_summary

    def create_regional_breakdown(self):
        """Break down stranded assets by region"""
        print("\n🗺️  Creating regional breakdown...")

        if not self.stranding_results:
            print("   ⚠️  No stranding results to analyze")
            return None

        regional_results = {}

        for scenario_name, df_strand in self.stranding_results.items():
            regional = df_strand.groupby('location').agg({
                'book_value_musd': 'sum',
                'total_stranded_musd': 'sum',
                'retirement_loss_musd': 'sum',
                'retrofit_capex_musd': 'sum',
                'operational_loss_musd': 'sum',
                'capacity_kt': 'sum',
                'total_emissions_kt': 'sum',
            }).reset_index()

            regional['stranding_rate_pct'] = (regional['total_stranded_musd'] / regional['book_value_musd']) * 100
            regional['scenario'] = scenario_name

            regional_results[scenario_name] = regional

        # Combine all scenarios
        if regional_results:
            df_regional_all = pd.concat(regional_results.values(), ignore_index=True)
            self.df_regional_stranding = df_regional_all
            return df_regional_all
        else:
            print("   ⚠️  No regional data to aggregate")
            return None

    def create_sectoral_breakdown(self):
        """Break down stranded assets by product group"""
        print("\n🏭 Creating sectoral breakdown...")

        if not self.stranding_results:
            print("   ⚠️  No stranding results to analyze")
            return None

        sectoral_results = {}

        for scenario_name, df_strand in self.stranding_results.items():
            sectoral = df_strand.groupby('product_group').agg({
                'book_value_musd': 'sum',
                'total_stranded_musd': 'sum',
                'retirement_loss_musd': 'sum',
                'retrofit_capex_musd': 'sum',
                'operational_loss_musd': 'sum',
                'capacity_kt': 'sum',
                'total_emissions_kt': 'sum',
            }).reset_index()

            sectoral['stranding_rate_pct'] = (sectoral['total_stranded_musd'] / sectoral['book_value_musd']) * 100
            sectoral['scenario'] = scenario_name

            sectoral_results[scenario_name] = sectoral

        # Combine all scenarios
        if sectoral_results:
            df_sectoral_all = pd.concat(sectoral_results.values(), ignore_index=True)
            self.df_sectoral_stranding = df_sectoral_all
            return df_sectoral_all
        else:
            print("   ⚠️  No sectoral data to aggregate")
            return None

    def create_visualizations(self):
        """Create comprehensive visualizations"""
        print("\n🎨 Creating visualizations...")

        # 1. Stranded asset waterfall chart (by scenario)
        fig, ax = plt.subplots(figsize=(14, 8))

        scenarios = self.df_stranding_summary['scenario'].tolist()
        x_pos = np.arange(len(scenarios))
        width = 0.6

        retirement = self.df_stranding_summary['retirement_loss_billion'].values
        retrofit = self.df_stranding_summary['retrofit_capex_billion'].values
        operational = self.df_stranding_summary['operational_loss_billion'].values

        ax.bar(x_pos, retirement, width, label='Premature Retirement', color='#E74C3C', alpha=0.8)
        ax.bar(x_pos, retrofit, width, bottom=retirement, label='Retrofit CAPEX', color='#3498DB', alpha=0.8)
        ax.bar(x_pos, operational, width, bottom=retirement+retrofit, label='Operational Loss', color='#F39C12', alpha=0.8)

        ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
        ax.set_ylabel('Stranded Assets (Billion USD)', fontsize=13, fontweight='bold')
        ax.set_title('Stranded Asset Composition by Scenario', fontsize=15, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(scenarios, rotation=45, ha='right')
        ax.legend(loc='upper left', fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        save_plot(fig, self.output_dir / 'stranded_assets_by_scenario.png')

        # 2. Regional stranding heatmap
        if hasattr(self, 'df_regional_stranding'):
            pivot_data = self.df_regional_stranding.pivot(
                index='location', columns='scenario', values='stranding_rate_pct'
            )

            fig, ax = plt.subplots(figsize=(12, 8))
            sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Stranding Rate (%)'})
            ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
            ax.set_ylabel('Location', fontsize=13, fontweight='bold')
            ax.set_title('Regional Stranding Rate Heatmap', fontsize=15, fontweight='bold')
            plt.tight_layout()
            save_plot(fig, self.output_dir / 'regional_stranding_heatmap.png')

        # 3. Sectoral breakdown
        if hasattr(self, 'df_sectoral_stranding'):
            # Pick first scenario for detailed sectoral view
            first_scenario = self.df_sectoral_stranding['scenario'].iloc[0]
            df_sector = self.df_sectoral_stranding[self.df_sectoral_stranding['scenario'] == first_scenario]

            fig, ax = plt.subplots(figsize=(12, 7))

            x_pos = np.arange(len(df_sector))
            width = 0.6

            retirement = df_sector['retirement_loss_musd'].values / 1000
            retrofit = df_sector['retrofit_capex_musd'].values / 1000
            operational = df_sector['operational_loss_musd'].values / 1000

            ax.bar(x_pos, retirement, width, label='Premature Retirement', color='#E74C3C', alpha=0.8)
            ax.bar(x_pos, retrofit, width, bottom=retirement, label='Retrofit CAPEX', color='#3498DB', alpha=0.8)
            ax.bar(x_pos, operational, width, bottom=retirement+retrofit, label='Operational Loss', color='#F39C12', alpha=0.8)

            ax.set_xlabel('Product Group', fontsize=13, fontweight='bold')
            ax.set_ylabel('Stranded Assets (Billion USD)', fontsize=13, fontweight='bold')
            ax.set_title(f'Sectoral Stranded Assets: {first_scenario}', fontsize=15, fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(df_sector['product_group'], rotation=45, ha='right')
            ax.legend(loc='upper right', fontsize=11)
            ax.grid(True, alpha=0.3, axis='y')

            plt.tight_layout()
            save_plot(fig, self.output_dir / 'sectoral_stranded_assets.png')

    def save_outputs(self):
        """Save all analysis outputs"""
        print("\n💾 Saving outputs...")

        # Facility-level asset data
        save_csv_output(self.df_assets, self.output_dir / 'facility_assets_2025.csv',
                       f"({len(self.df_assets)} facilities)")

        # Stranding summary
        if hasattr(self, 'df_stranding_summary'):
            save_csv_output(self.df_stranding_summary, self.output_dir / 'stranding_summary.csv')

        # Regional breakdown
        if hasattr(self, 'df_regional_stranding'):
            save_csv_output(self.df_regional_stranding, self.output_dir / 'regional_stranding.csv')

        # Sectoral breakdown
        if hasattr(self, 'df_sectoral_stranding'):
            save_csv_output(self.df_sectoral_stranding, self.output_dir / 'sectoral_stranding.csv')

        # Facility-level stranding (for each scenario)
        for scenario_name, df_strand in self.stranding_results.items():
            filename = f'facility_stranding_{scenario_name.lower().replace(" ", "_")}.csv'
            save_csv_output(df_strand, self.output_dir / filename)

    def run_complete_analysis(self, scenario_deployments):
        """Run complete stranded asset analysis"""
        print("\n" + "="*80)
        print("RUNNING STRANDED ASSET ANALYSIS")
        print("="*80)

        # Step 1: Calculate facility assets
        self.calculate_facility_assets()

        # Step 2: Calculate stranding under scenarios
        self.calculate_stranding_scenarios(scenario_deployments)

        # Step 3: Create summaries
        self.create_stranding_summary()
        self.create_regional_breakdown()
        self.create_sectoral_breakdown()

        # Step 4: Visualizations
        self.create_visualizations()

        # Step 5: Save outputs
        self.save_outputs()

        print("\n" + "="*80)
        print("✓ MODULE 4 COMPLETE")
        print("="*80)
        print(f"\nOutputs saved to: {self.output_dir}")

        return {
            'assets': self.df_assets,
            'stranding_summary': self.df_stranding_summary,
            'regional_stranding': self.df_regional_stranding,
            'sectoral_stranding': self.df_sectoral_stranding,
        }
