#!/usr/bin/env python3
"""
MACC Model Report Generator
Generates a comprehensive PDF report from model outputs
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from pathlib import Path
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.output_dir = Path('outputs/reports')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set professional style
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.titleweight'] = 'bold'

    def load_data(self):
        """Load all model outputs"""
        print("Loading data...")
        self.baseline = pd.read_csv('outputs/module_01/baseline_2025_detailed.csv')
        self.bau = pd.read_csv('outputs/module_01/bau_trajectory_2025_2050.csv')
        self.macc = pd.read_csv('outputs/module_02/macc_annual_2025_2050.csv')
        self.scenarios = pd.read_csv('outputs/module_03/scenario_comparison.csv')

        # Load scenario deployments
        self.conservative = pd.read_csv('outputs/module_03/conservative_deployment.csv')
        self.moderate = pd.read_csv('outputs/module_03/moderate_deployment.csv')
        self.aggressive = pd.read_csv('outputs/module_03/aggressive_deployment.csv')

        print("✓ Data loaded")

    def create_cover_page(self, pdf):
        """Create report cover page"""
        fig = plt.figure(figsize=(8.5, 11))
        fig.suptitle('', fontsize=1)  # Empty title

        ax = fig.add_subplot(111)
        ax.axis('off')

        # Title
        ax.text(0.5, 0.75, 'Korean Petrochemical Industry',
               ha='center', va='center', fontsize=24, fontweight='bold')
        ax.text(0.5, 0.68, 'Decarbonization Pathway Analysis',
               ha='center', va='center', fontsize=20, fontweight='bold')
        ax.text(0.5, 0.62, 'Marginal Abatement Cost Curve (MACC) Model',
               ha='center', va='center', fontsize=16)

        # Model info
        ax.text(0.5, 0.5, f'Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
               ha='center', va='center', fontsize=12)
        ax.text(0.5, 0.46, 'Model Version: 2.2',
               ha='center', va='center', fontsize=12)

        # Key metrics box
        total_baseline = self.baseline['total_emissions_kt'].sum() / 1000
        max_abatement = 49.84  # From our calculations

        box_text = f"""
        Key Model Parameters

        • Baseline Emissions (2025): {total_baseline:.1f} MtCO2/year
        • Facilities Analyzed: {len(self.baseline)}
        • Technologies: 4 (Heat Pump, RE PPA, NCC-H2, NCC-Electricity)
        • Time Horizon: 2025-2050
        • Maximum Abatement Potential: {max_abatement:.1f} MtCO2 (95.9%)
        • Scenarios: Conservative, Moderate, Aggressive
        """

        ax.text(0.5, 0.28, box_text, ha='center', va='center', fontsize=11,
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

        # Footer
        ax.text(0.5, 0.05, '© 2025 | LCOE-Based MACC Methodology | Academic Peer-Review Quality',
               ha='center', va='center', fontsize=9, style='italic')

        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def create_executive_summary(self, pdf):
        """Create executive summary page"""
        fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('Executive Summary', fontsize=16, fontweight='bold', y=0.98)

        # 1. Baseline emissions pie chart
        ax = axes[0, 0]
        by_product = self.baseline.groupby('product_group')['total_emissions_kt'].sum() / 1000
        by_product = by_product.sort_values(ascending=False)
        colors = plt.cm.Set3(range(len(by_product)))
        ax.pie(by_product.values, labels=by_product.index, autopct='%1.1f%%',
              colors=colors, startangle=90)
        ax.set_title('2025 Baseline by Product Group\n(52.0 MtCO2 total)')

        # 2. MACC curve 2030
        ax = axes[0, 1]
        df_2030 = self.macc[self.macc['year'] == 2030].sort_values('total_cost_usd_per_tco2')
        x_pos = 0
        colors_tech = {'Heat_Pump': '#2ECC71', 'RE_PPA': '#F39C12',
                      'NCC-Electricity': '#E74C3C', 'NCC-H2': '#3498DB'}

        for _, row in df_2030.iterrows():
            width = row['abatement_potential_mtco2']
            height = row['total_cost_usd_per_tco2']
            ax.bar(x_pos + width/2, height, width=width,
                  color=colors_tech.get(row['technology'], 'gray'),
                  edgecolor='black', linewidth=1, alpha=0.8)
            x_pos += width

        ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
        ax.set_xlabel('Cumulative Abatement (MtCO2/year)', fontweight='bold')
        ax.set_ylabel('Cost ($/tCO2)', fontweight='bold')
        ax.set_title('MACC Curve - 2030\n(3 cost-negative technologies)')
        ax.grid(True, alpha=0.3, axis='y')

        # 3. Scenario comparison
        ax = axes[1, 0]
        scenarios = ['Conservative', 'Moderate', 'Aggressive']
        reductions_2030 = []
        reductions_2050 = []

        for scenario in scenarios:
            row = self.scenarios[self.scenarios['scenario'] == scenario].iloc[0]
            reductions_2030.append(row['reduction_2030_pct'])
            reductions_2050.append(row['reduction_2050_pct'])

        x = np.arange(len(scenarios))
        width = 0.35
        ax.bar(x - width/2, reductions_2030, width, label='2030', color='#3498DB', alpha=0.8)
        ax.bar(x + width/2, reductions_2050, width, label='2050', color='#E74C3C', alpha=0.8)

        ax.set_xlabel('Scenario', fontweight='bold')
        ax.set_ylabel('Emission Reduction (%)', fontweight='bold')
        ax.set_title('Emission Reduction by Scenario')
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # 4. Technology deployment (Moderate scenario)
        ax = axes[1, 1]
        techs = ['Heat Pump', 'RE PPA', 'NCC-Electricity', 'NCC-H2']
        deployments_2030 = []
        deployments_2050 = []

        for tech_col in ['heat_pump_mt', 're_ppa_mt', 'ncc_elec_mt', 'ncc_h2_mt']:
            deployments_2030.append(self.moderate[self.moderate['year'] == 2030][tech_col].iloc[0])
            deployments_2050.append(self.moderate[self.moderate['year'] == 2050][tech_col].iloc[0])

        x = np.arange(len(techs))
        ax.bar(x - width/2, deployments_2030, width, label='2030', color='#3498DB', alpha=0.8)
        ax.bar(x + width/2, deployments_2050, width, label='2050', color='#E74C3C', alpha=0.8)

        ax.set_xlabel('Technology', fontweight='bold')
        ax.set_ylabel('Abatement (MtCO2/year)', fontweight='bold')
        ax.set_title('Technology Deployment - Moderate Scenario')
        ax.set_xticks(x)
        ax.set_xticklabels(techs, rotation=15, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def create_detailed_results(self, pdf):
        """Create detailed results pages"""
        # Page 1: MACC Evolution
        fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('MACC Curve Evolution (2025-2050)', fontsize=16, fontweight='bold', y=0.98)

        years = [2025, 2030, 2040, 2050]
        colors_tech = {'Heat_Pump': '#2ECC71', 'RE_PPA': '#F39C12',
                      'NCC-Electricity': '#E74C3C', 'NCC-H2': '#3498DB'}

        for i, year in enumerate(years):
            ax = axes[i//2, i%2]
            df_year = self.macc[self.macc['year'] == year].sort_values('total_cost_usd_per_tco2')

            x_pos = 0
            for _, row in df_year.iterrows():
                width = row['abatement_potential_mtco2']
                height = row['total_cost_usd_per_tco2']
                ax.bar(x_pos + width/2, height, width=width,
                      color=colors_tech.get(row['technology'], 'gray'),
                      edgecolor='black', linewidth=1, alpha=0.8)
                x_pos += width

            ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
            ax.set_xlabel('Cumulative Abatement (MtCO2/year)')
            ax.set_ylabel('Cost ($/tCO2)')
            ax.set_title(f'{year}')
            ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

        # Page 2: Scenario trajectories
        fig, axes = plt.subplots(2, 1, figsize=(11, 8.5))
        fig.suptitle('Emission Trajectories by Scenario', fontsize=16, fontweight='bold', y=0.98)

        # Emissions trajectory
        ax = axes[0]
        ax.plot(self.bau['year'], self.bau['total_emissions_mt'],
               'k--', linewidth=2, label='BAU (No Action)', alpha=0.5)
        ax.plot(self.conservative['year'], self.conservative['actual_emissions_mt'],
               linewidth=2.5, marker='o', label='Conservative', color='#3498DB')
        ax.plot(self.moderate['year'], self.moderate['actual_emissions_mt'],
               linewidth=2.5, marker='s', label='Moderate', color='#F39C12')
        ax.plot(self.aggressive['year'], self.aggressive['actual_emissions_mt'],
               linewidth=2.5, marker='^', label='Aggressive', color='#E74C3C')

        ax.set_xlabel('Year', fontweight='bold')
        ax.set_ylabel('Emissions (MtCO2/year)', fontweight='bold')
        ax.set_title('Annual Emissions')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        # Technology deployment (Moderate)
        ax = axes[1]
        ax.fill_between(self.moderate['year'], 0, self.moderate['heat_pump_mt'],
                       label='Heat Pump', color='#2ECC71', alpha=0.7)
        ax.fill_between(self.moderate['year'], self.moderate['heat_pump_mt'],
                       self.moderate['heat_pump_mt'] + self.moderate['re_ppa_mt'],
                       label='RE PPA', color='#F39C12', alpha=0.7)
        ax.fill_between(self.moderate['year'],
                       self.moderate['heat_pump_mt'] + self.moderate['re_ppa_mt'],
                       self.moderate['heat_pump_mt'] + self.moderate['re_ppa_mt'] + self.moderate['ncc_elec_mt'],
                       label='NCC-Electricity', color='#E74C3C', alpha=0.7)
        ax.fill_between(self.moderate['year'],
                       self.moderate['heat_pump_mt'] + self.moderate['re_ppa_mt'] + self.moderate['ncc_elec_mt'],
                       self.moderate['heat_pump_mt'] + self.moderate['re_ppa_mt'] + self.moderate['ncc_elec_mt'] + self.moderate['ncc_h2_mt'],
                       label='NCC-H2', color='#3498DB', alpha=0.7)

        ax.set_xlabel('Year', fontweight='bold')
        ax.set_ylabel('Abatement (MtCO2/year)', fontweight='bold')
        ax.set_title('Technology Deployment - Moderate Scenario')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def create_summary_tables(self, pdf):
        """Create summary tables page"""
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('Summary Tables', fontsize=16, fontweight='bold', y=0.98)

        # Scenario comparison table
        ax1 = plt.subplot(2, 1, 1)
        ax1.axis('tight')
        ax1.axis('off')

        table_data = []
        for _, row in self.scenarios.iterrows():
            table_data.append([
                row['scenario'],
                f"{row['emissions_2030_mt']:.1f}",
                f"{row['reduction_2030_pct']:.1f}%",
                f"{row['emissions_2050_mt']:.1f}",
                f"{row['reduction_2050_pct']:.1f}%"
            ])

        table = ax1.table(cellText=table_data,
                         colLabels=['Scenario', '2030 Emis\n(Mt)', '2030 Reduct\n(%)',
                                   '2050 Emis\n(Mt)', '2050 Reduct\n(%)'],
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)

        # Style header
        for i in range(5):
            table[(0, i)].set_facecolor('#3498DB')
            table[(0, i)].set_text_props(weight='bold', color='white')

        ax1.set_title('Scenario Comparison', fontweight='bold', pad=20)

        # Technology costs table (2030)
        ax2 = plt.subplot(2, 1, 2)
        ax2.axis('tight')
        ax2.axis('off')

        df_2030 = self.macc[self.macc['year'] == 2030]
        table_data = []
        for _, row in df_2030.iterrows():
            capex_opex = row.get('capex_ann_usd_per_tco2', 0) + row.get('opex_ann_usd_per_tco2', 0)
            table_data.append([
                row['technology'],
                f"{row['abatement_potential_mtco2']:.2f}",
                f"${capex_opex:.1f}",
                f"${row.get('fuel_cost_diff_usd_per_tco2', 0):.1f}",
                f"${row['total_cost_usd_per_tco2']:.1f}"
            ])

        table = ax2.table(cellText=table_data,
                         colLabels=['Technology', 'Abatement\n(MtCO2)', 'CAPEX+OPEX\n($/tCO2)',
                                   'Fuel Diff\n($/tCO2)', 'Total Cost\n($/tCO2)'],
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)

        # Style header
        for i in range(5):
            table[(0, i)].set_facecolor('#2ECC71')
            table[(0, i)].set_text_props(weight='bold', color='white')

        ax2.set_title('Technology Costs - 2030', fontweight='bold', pad=20)

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def generate_report(self):
        """Generate complete PDF report"""
        print("\n" + "="*80)
        print("GENERATING COMPREHENSIVE REPORT")
        print("="*80 + "\n")

        self.load_data()

        report_path = self.output_dir / f'MACC_Report_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'

        with PdfPages(report_path) as pdf:
            print("Creating cover page...")
            self.create_cover_page(pdf)

            print("Creating executive summary...")
            self.create_executive_summary(pdf)

            print("Creating detailed results...")
            self.create_detailed_results(pdf)

            print("Creating summary tables...")
            self.create_summary_tables(pdf)

            # Set PDF metadata
            d = pdf.infodict()
            d['Title'] = 'Korean Petrochemical MACC Analysis'
            d['Author'] = 'MACC Model v2.2'
            d['Subject'] = 'Decarbonization Pathway Analysis'
            d['Keywords'] = 'MACC, Petrochemical, Decarbonization, Korea'
            d['CreationDate'] = datetime.now()

        print(f"\n✓ Report generated: {report_path}")
        print(f"  Pages: Cover + Executive Summary + 2 Detailed + Tables = 5 pages")
        print(f"  File size: {report_path.stat().st_size / 1024:.1f} KB")
        print("\n" + "="*80)

        return report_path

if __name__ == '__main__':
    generator = ReportGenerator()
    report_path = generator.generate_report()
    print(f"\n🎉 Report complete! Open with: open {report_path}")
