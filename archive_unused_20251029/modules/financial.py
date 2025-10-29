"""
MODULE 4: FINANCIAL ANALYSIS
Calculate NPV, IRR, payback periods
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.optimize import newton
from .utils import save_csv_output, save_plot

class FinancialAnalyzer:
    """Financial analysis - NPV, IRR, payback"""

    def __init__(self, optimization_output='outputs/module_03', output_dir='outputs/module_04'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("MODULE 4: FINANCIAL ANALYSIS")
        print("="*80)

        # Try to load deployment file (try different scenario names)
        deployment_file = None
        for scenario in ['conservative', 'moderate', 'aggressive', 'linear']:
            candidate = Path(optimization_output) / f'{scenario}_deployment.csv'
            if candidate.exists():
                deployment_file = candidate
                break

        if deployment_file is None:
            raise FileNotFoundError(f"No deployment file found in {optimization_output}")

        self.df_deployment = pd.read_csv(deployment_file)
        print(f"\n📁 Loaded deployment data from: {deployment_file.name}")

        # Discount rate for NPV/IRR calculation only (not for CAPEX annualization)
        self.discount_rate = 0.05  # 5% for financial analysis
        self.carbon_price_2025 = 50  # $/tCO2
        self.carbon_price_growth = 0.05

    def calculate_npv_irr(self):
        """Calculate NPV and IRR"""
        print("\n💰 Calculating NPV and IRR...")

        cash_flows = []
        for idx, row in self.df_deployment.iterrows():
            year = row['year']
            year_index = year - 2025

            # Carbon benefit
            carbon_price = self.carbon_price_2025 * ((1 + self.carbon_price_growth) ** year_index)
            carbon_benefit = row['total_deployed_mt'] * carbon_price * 1e6  # USD

            # Costs (simplified)
            capex = row['total_deployed_mt'] * 150 * 1e6  # $150M/MtCO2 average
            opex = capex * 0.03

            net_cash_flow = carbon_benefit - capex - opex

            cash_flows.append({
                'year': year,
                'year_index': year_index,
                'carbon_benefit_musd': carbon_benefit / 1e6,
                'capex_musd': capex / 1e6,
                'opex_musd': opex / 1e6,
                'net_cash_flow_musd': net_cash_flow / 1e6,
            })

        df_cash_flow = pd.DataFrame(cash_flows)

        # NPV
        npv = sum([row['net_cash_flow_musd'] / ((1 + self.discount_rate) ** row['year_index'])
                  for _, row in df_cash_flow.iterrows()])

        # IRR (simplified)
        try:
            irr = newton(lambda r: sum([row['net_cash_flow_musd'] / ((1 + r) ** row['year_index'])
                                       for _, row in df_cash_flow.iterrows()]), 0.1)
        except:
            irr = np.nan

        print(f"   ✓ NPV: ${npv:.2f} Million")
        print(f"   ✓ IRR: {irr*100:.2f}%")

        self.npv = npv
        self.irr = irr
        self.df_cash_flow = df_cash_flow

        return npv, irr

    def save_outputs(self):
        """Save outputs"""
        print("\n💾 Saving outputs...")

        summary = pd.DataFrame([{
            'npv_musd': self.npv,
            'irr_pct': self.irr * 100 if not np.isnan(self.irr) else np.nan,
        }])

        save_csv_output(summary, self.output_dir / 'financial_summary.csv')
        save_csv_output(self.df_cash_flow, self.output_dir / 'cash_flow_linear.csv')

    def run_complete_analysis(self):
        """Run complete financial analysis"""
        print("\n" + "="*80)
        print("RUNNING FINANCIAL ANALYSIS")
        print("="*80)

        self.calculate_npv_irr()
        self.save_outputs()

        print("\n✓ MODULE 4 COMPLETE")
        print(f"Outputs saved to: {self.output_dir}")
        return {'npv': self.npv, 'irr': self.irr}
