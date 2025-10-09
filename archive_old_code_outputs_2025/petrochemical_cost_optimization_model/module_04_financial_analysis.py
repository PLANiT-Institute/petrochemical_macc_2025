#!/usr/bin/env python3
"""
MODULE 4: FINANCIAL ANALYSIS
Korean Petrochemical Industry - NPV, IRR, Payback, Stranded Assets

Features:
- NPV and IRR calculations for each scenario
- Payback period analysis
- Stranded asset valuation
- Carbon price sensitivity
- Annual cash flow projections
- CSV + PNG outputs

Author: Petrochemical MACC Model v2.0
Date: October 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.optimize import newton
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

class FinancialAnalyzer:
    """Financial analysis for decarbonization pathways"""

    def __init__(self, excel_path):
        """Initialize with data"""
        self.excel_path = excel_path
        self.output_dir = Path('step_04_financial_analysis/outputs')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("MODULE 4: FINANCIAL ANALYSIS")
        print("="*80)

        # Load data
        print("\n📁 Loading data...")
        self.df_baseline = pd.read_csv('step_01_baseline_analysis/outputs/baseline_2025_detailed.csv')
        self.df_bau = pd.read_csv('step_01_baseline_analysis/outputs/bau_trajectory_2025_2075.csv')

        # Load optimization results
        self.scenarios = {}
        scenario_files = Path('step_03_cost_optimization/outputs').glob('*_deployment.csv')
        for f in scenario_files:
            scenario_name = f.stem.replace('_deployment', '')
            self.scenarios[scenario_name] = pd.read_csv(f)

        print(f"   ✓ Loaded {len(self.scenarios)} optimization scenarios")

        # Financial parameters
        self.discount_rate = 0.08  # 8% WACC
        self.carbon_price_2025 = 30  # USD/tCO2
        self.carbon_price_growth = 0.05  # 5% annual growth
        self.tech_lifetime = 20  # years

    def calculate_npv_irr(self, scenario_name):
        """Calculate NPV and IRR for a scenario"""
        print(f"\n💰 Calculating NPV/IRR for: {scenario_name}")

        df = self.scenarios[scenario_name]
        df_analysis = df[df['year'] <= 2050].copy()

        # Calculate annual cash flows
        cash_flows = []
        year_0 = 2025

        for idx, row in df_analysis.iterrows():
            year = row['year']
            year_index = year - year_0

            # Costs (outflows - negative)
            capex = 0
            if year_index == 0 or row['total_deployed_mt'] > df_analysis.iloc[max(0, idx-1)]['total_deployed_mt']:
                # New deployment - calculate incremental capex
                if idx > 0:
                    incremental_deployment = row['total_deployed_mt'] - df_analysis.iloc[idx-1]['total_deployed_mt']
                else:
                    incremental_deployment = row['total_deployed_mt']

                # Approximate capex (using MACC data would be more accurate)
                capex = incremental_deployment * 150 * 1e6  # Assume $150M/MtCO2 average

            opex = row['annual_cost_musd'] * 1e6  # Annual operating cost

            # Benefits (inflows - positive)
            # Carbon tax avoided
            carbon_price = self.carbon_price_2025 * ((1 + self.carbon_price_growth) ** year_index)
            emissions_avoided = row['total_deployed_mt'] * 1e6  # Convert to tonnes
            carbon_benefit = emissions_avoided * carbon_price

            # Net cash flow
            net_cash_flow = carbon_benefit - capex - opex

            cash_flows.append({
                'year': year,
                'year_index': year_index,
                'capex': capex,
                'opex': opex,
                'carbon_price': carbon_price,
                'emissions_avoided_t': emissions_avoided,
                'carbon_benefit': carbon_benefit,
                'net_cash_flow': net_cash_flow
            })

        df_cash_flow = pd.DataFrame(cash_flows)

        # Calculate NPV
        npv = sum([row['net_cash_flow'] / ((1 + self.discount_rate) ** row['year_index'])
                   for _, row in df_cash_flow.iterrows()])

        # Calculate IRR (simplified - may not converge)
        try:
            def npv_func(rate):
                return sum([row['net_cash_flow'] / ((1 + rate) ** row['year_index'])
                           for _, row in df_cash_flow.iterrows()])

            irr = newton(npv_func, 0.1, maxiter=100)
        except:
            irr = np.nan

        # Calculate payback period
        cumulative_cf = df_cash_flow['net_cash_flow'].cumsum()
        payback_idx = (cumulative_cf > 0).idxmax() if (cumulative_cf > 0).any() else len(cumulative_cf)
        payback_year = df_cash_flow.loc[payback_idx, 'year'] if payback_idx < len(cumulative_cf) else None

        print(f"   NPV: ${npv/1e9:.2f} Billion")
        print(f"   IRR: {irr*100:.2f}%" if not np.isnan(irr) else "   IRR: Not converged")
        print(f"   Payback: {payback_year}" if payback_year else "   Payback: Beyond 2050")

        return {
            'scenario': scenario_name,
            'npv_busd': npv / 1e9,
            'irr_%': irr * 100 if not np.isnan(irr) else None,
            'payback_year': payback_year,
            'total_capex_busd': df_cash_flow['capex'].sum() / 1e9,
            'total_opex_busd': df_cash_flow['opex'].sum() / 1e9,
            'total_carbon_benefit_busd': df_cash_flow['carbon_benefit'].sum() / 1e9
        }, df_cash_flow

    def analyze_stranded_assets(self):
        """Analyze stranded asset risk"""
        print("\n🏭 Analyzing stranded assets...")

        # Facilities at risk: old facilities that retire before 2050
        df_facilities = self.df_baseline.copy()

        stranded = []

        for _, facility in df_facilities.iterrows():
            year_built = facility['year_built']
            retirement_year = facility['retirement_year']
            remaining_life = retirement_year - 2025

            # Asset value (simplified)
            # Assume facility value = annual production × $500/t
            capacity_t = facility['capacity_kt'] * 1000
            annual_value = capacity_t * 500  # $500/tonne production value

            # Book value = residual value based on remaining life
            if remaining_life > 0:
                book_value = annual_value * remaining_life / 50  # Linear depreciation over 50 years
            else:
                book_value = 0

            # If facility emits heavily and carbon price rises, it may become uneconomic
            if facility['capacity_kt'] > 0:
                carbon_intensity = facility['total_emissions_kt'] / facility['capacity_kt']  # tCO2/tonne
                carbon_cost_2030 = carbon_intensity * (self.carbon_price_2025 * ((1 + self.carbon_price_growth) ** 5))
                # Stranded if: carbon cost > $100/tonne product (arbitrary threshold)
                stranded_risk = carbon_cost_2030 > 100
            else:
                carbon_intensity = 0
                carbon_cost_2030 = 0
                stranded_risk = False

            stranded.append({
                'product': facility['product'],
                'company': facility['company'],
                'location': facility['location'],
                'year_built': year_built,
                'retirement_year': retirement_year,
                'remaining_life_years': max(0, remaining_life),
                'capacity_kt': facility['capacity_kt'],
                'emissions_kt': facility['total_emissions_kt'],
                'carbon_intensity_tco2_per_t': carbon_intensity,
                'book_value_musd': book_value / 1e6,
                'carbon_cost_2030_usd_per_t': carbon_cost_2030,
                'stranded_risk': stranded_risk
            })

        df_stranded = pd.DataFrame(stranded)

        # Summary
        total_at_risk = df_stranded[df_stranded['stranded_risk']]['book_value_musd'].sum()
        num_at_risk = df_stranded['stranded_risk'].sum()

        print(f"   Facilities at stranded risk: {num_at_risk}")
        print(f"   Total book value at risk: ${total_at_risk:.1f} Million")

        # Save
        stranded_file = self.output_dir / 'stranded_asset_analysis.csv'
        df_stranded.to_csv(stranded_file, index=False)
        print(f"   ✓ Saved: {stranded_file}")

        return df_stranded

    def carbon_price_sensitivity(self):
        """Sensitivity analysis on carbon price"""
        print("\n📊 Running carbon price sensitivity analysis...")

        carbon_prices = [20, 30, 50, 75, 100, 150, 200]  # USD/tCO2
        sensitivity_results = []

        for carbon_price in carbon_prices:
            # Temporarily change carbon price
            original_price = self.carbon_price_2025
            self.carbon_price_2025 = carbon_price

            # Recalculate NPV for each scenario
            for scenario_name in self.scenarios.keys():
                result, _ = self.calculate_npv_irr(scenario_name)
                sensitivity_results.append({
                    'carbon_price': carbon_price,
                    'scenario': scenario_name,
                    'npv_busd': result['npv_busd']
                })

            # Restore original
            self.carbon_price_2025 = original_price

        df_sensitivity = pd.DataFrame(sensitivity_results)

        # Save
        sens_file = self.output_dir / 'carbon_price_sensitivity.csv'
        df_sensitivity.to_csv(sens_file, index=False)
        print(f"   ✓ Saved: {sens_file}")

        return df_sensitivity

    def run_complete_analysis(self):
        """Run complete financial analysis"""
        print("\n" + "="*80)
        print("RUNNING COMPLETE FINANCIAL ANALYSIS")
        print("="*80)

        # 1. NPV/IRR for all scenarios
        financial_summary = []
        all_cash_flows = {}

        for scenario_name in self.scenarios.keys():
            result, cash_flow = self.calculate_npv_irr(scenario_name)
            financial_summary.append(result)
            all_cash_flows[scenario_name] = cash_flow

        df_financial = pd.DataFrame(financial_summary)
        financial_file = self.output_dir / 'financial_summary.csv'
        df_financial.to_csv(financial_file, index=False)
        print(f"\n   ✓ Saved: {financial_file}")

        # Save cash flows
        for scenario_name, cf in all_cash_flows.items():
            cf_file = self.output_dir / f'cash_flow_{scenario_name}.csv'
            cf.to_csv(cf_file, index=False)

        # 2. Stranded assets
        df_stranded = self.analyze_stranded_assets()

        # 3. Carbon price sensitivity
        df_sensitivity = self.carbon_price_sensitivity()

        # 4. Create visualizations
        self._create_visualizations(df_financial, all_cash_flows, df_stranded, df_sensitivity)

        print("\n" + "="*80)
        print("✓ MODULE 4 COMPLETE")
        print("="*80)
        print(f"\nOutputs saved to: {self.output_dir}")
        print("\nGenerated files:")
        for f in sorted(self.output_dir.glob('*')):
            print(f"   - {f.name}")

    def _create_visualizations(self, df_financial, all_cash_flows, df_stranded, df_sensitivity):
        """Create all visualizations"""
        print("\n🎨 Creating visualizations...")

        # 1. NPV comparison
        self._plot_npv_comparison(df_financial)

        # 2. Cash flow profiles
        self._plot_cash_flows(all_cash_flows)

        # 3. Stranded assets
        self._plot_stranded_assets(df_stranded)

        # 4. Carbon price sensitivity
        self._plot_sensitivity(df_sensitivity)

        print("   ✓ All visualizations created")

    def _plot_npv_comparison(self, df_financial):
        """Plot NPV comparison across scenarios"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # NPV
        colors = ['#2ECC71' if x > 0 else '#E74C3C' for x in df_financial['npv_busd']]
        ax1.bar(df_financial['scenario'], df_financial['npv_busd'],
               color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax1.set_ylabel('NPV (Billion USD)', fontsize=12, fontweight='bold')
        ax1.set_title('Net Present Value by Scenario\n(8% discount rate, $30/tCO2 base carbon price)',
                     fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')

        # Add values on bars
        for i, v in enumerate(df_financial['npv_busd']):
            ax1.text(i, v + (0.5 if v > 0 else -0.5), f'${v:.1f}B',
                    ha='center', fontweight='bold', fontsize=10)

        # Payback period
        ax2.bar(df_financial['scenario'], df_financial['payback_year'] - 2025,
               color='#3498DB', edgecolor='black', linewidth=1.5, alpha=0.8)
        ax2.set_ylabel('Payback Period (years from 2025)', fontsize=12, fontweight='bold')
        ax2.set_title('Payback Period by Scenario',
                     fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'npv_payback_comparison.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ npv_payback_comparison.png")

    def _plot_cash_flows(self, all_cash_flows):
        """Plot annual cash flows for each scenario"""

        for scenario_name, df_cf in all_cash_flows.items():
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

            # Annual cash flows
            ax1.bar(df_cf['year'], df_cf['net_cash_flow']/1e9,
                   color=['#2ECC71' if x > 0 else '#E74C3C' for x in df_cf['net_cash_flow']],
                   edgecolor='black', linewidth=1, alpha=0.8)
            ax1.axhline(y=0, color='black', linestyle='-', linewidth=1)
            ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Annual Cash Flow (Billion USD)', fontsize=12, fontweight='bold')
            ax1.set_title(f'Annual Cash Flows: {scenario_name}',
                         fontsize=13, fontweight='bold')
            ax1.grid(True, alpha=0.3, axis='y')

            # Cumulative cash flow
            cumulative = df_cf['net_cash_flow'].cumsum() / 1e9
            ax2.plot(df_cf['year'], cumulative, linewidth=2.5, color='#3498DB', marker='o', markersize=4)
            ax2.fill_between(df_cf['year'], 0, cumulative, alpha=0.3, color='#3498DB')
            ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
            ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Cumulative Cash Flow (Billion USD)', fontsize=12, fontweight='bold')
            ax2.set_title('Cumulative Cash Flow', fontsize=13, fontweight='bold')
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(self.output_dir / f'cash_flow_profile_{scenario_name}.png',
                       dpi=300, bbox_inches='tight')
            plt.close()

        print(f"   ✓ cash_flow_profile_*.png (3 files)")

    def _plot_stranded_assets(self, df_stranded):
        """Plot stranded asset analysis"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # By product
        stranded_by_product = df_stranded[df_stranded['stranded_risk']].groupby('product')['book_value_musd'].sum().sort_values(ascending=False).head(10)

        ax1.barh(range(len(stranded_by_product)), stranded_by_product.values,
                color='#E74C3C', edgecolor='black', linewidth=1, alpha=0.8)
        ax1.set_yticks(range(len(stranded_by_product)))
        ax1.set_yticklabels(stranded_by_product.index)
        ax1.set_xlabel('Book Value at Risk (Million USD)', fontsize=12, fontweight='bold')
        ax1.set_title('Top 10 Products: Stranded Asset Risk',
                     fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')

        # By year built (age distribution)
        df_at_risk = df_stranded[df_stranded['stranded_risk']]
        ax2.hist(df_at_risk['year_built'], bins=15, color='#E74C3C',
                edgecolor='black', linewidth=1, alpha=0.8)
        ax2.set_xlabel('Year Built', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Number of Facilities at Risk', fontsize=12, fontweight='bold')
        ax2.set_title('Stranded Asset Risk by Facility Age',
                     fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'stranded_asset_risk.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ stranded_asset_risk.png")

    def _plot_sensitivity(self, df_sensitivity):
        """Plot carbon price sensitivity"""
        fig, ax = plt.subplots(figsize=(14, 8))

        colors = {'budget': '#E74C3C', 'point_targets': '#3498DB', 'linear': '#2ECC71'}

        for scenario in df_sensitivity['scenario'].unique():
            df_scenario = df_sensitivity[df_sensitivity['scenario'] == scenario]
            ax.plot(df_scenario['carbon_price'], df_scenario['npv_busd'],
                   linewidth=2.5, marker='o', markersize=8,
                   color=colors.get(scenario, 'black'),
                   label=scenario.replace('_', ' ').title())

        ax.axhline(y=0, color='black', linestyle='--', linewidth=1)
        ax.set_xlabel('Carbon Price (USD/tCO2)', fontsize=12, fontweight='bold')
        ax.set_ylabel('NPV (Billion USD)', fontsize=12, fontweight='bold')
        ax.set_title('Carbon Price Sensitivity Analysis\nNPV vs Carbon Price (2025 base, 5% annual growth)',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=11)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'carbon_price_sensitivity.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ carbon_price_sensitivity.png")


if __name__ == '__main__':
    # Run financial analysis
    analyzer = FinancialAnalyzer('data_sources/Korean_Petrochemical_MACC_Model_English.xlsx')
    analyzer.run_complete_analysis()

    print("\n🎉 Financial analysis complete!")
