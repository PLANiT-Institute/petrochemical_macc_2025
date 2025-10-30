"""
Generate All Charts for Word Report
- Korean font support (AppleGothic for macOS)
- High-resolution PNG files
- Organized in dedicated folder
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

# Set Korean font for macOS
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False  # Fix minus sign display
sns.set_style("whitegrid")

class ReportChartGenerator:
    """Generate all charts for Word report"""

    def __init__(self):
        self.output_dir = Path('outputs/word_report/charts_for_report')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load data
        self.load_data()

    def load_data(self):
        """Load all necessary data"""
        # 6-scenario summary
        summary_path = Path('outputs/scenarios_comparison_6scenarios/summary.csv')
        if summary_path.exists():
            self.df_summary = pd.read_csv(summary_path)
            print(f"✅ Loaded summary: {len(self.df_summary)} scenarios")
        else:
            self.df_summary = None
            print("⚠️ Summary file not found")

        # Baseline data for company/regional analysis
        baseline_company = Path('outputs/scenarios_shaheen_ncc_h2/module_01_baseline/emissions_by_company.csv')
        baseline_region = Path('outputs/scenarios_shaheen_ncc_h2/module_01_baseline/emissions_by_location.csv')

        if baseline_company.exists():
            self.df_company_baseline = pd.read_csv(baseline_company)
            print(f"✅ Loaded company baseline: {len(self.df_company_baseline)} companies")
        else:
            self.df_company_baseline = None
            print("⚠️ Company baseline not found")

        if baseline_region.exists():
            self.df_region_baseline = pd.read_csv(baseline_region)
            print(f"✅ Loaded regional baseline: {len(self.df_region_baseline)} regions")
        else:
            self.df_region_baseline = None
            print("⚠️ Regional baseline not found")

        # Facility allocation for technology mix
        facility_path = Path('outputs/scenarios_shaheen_ncc_h2/module_03_optimization/policy_target_facility_allocation_2050.csv')
        if facility_path.exists():
            self.df_facility = pd.read_csv(facility_path)
            print(f"✅ Loaded facility allocation: {len(self.df_facility)} facilities")
        else:
            self.df_facility = None
            print("⚠️ Facility allocation not found")

    def chart_1_scenario_cost_comparison(self):
        """Chart 1: 6개 시나리오 비용 비교"""
        if self.df_summary is None:
            print("⚠️ Cannot generate Chart 1: No summary data")
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        # Prepare data
        scenarios = self.df_summary['scenario'].values
        costs = self.df_summary['cost_2050_billion_usd'].values

        # Color by technology pathway
        colors = []
        for scenario in scenarios:
            if 'NCC-H₂' in scenario or 'NCC-H2' in scenario:
                colors.append('#4ECDC4')  # Teal for H2
            else:
                colors.append('#FFE66D')  # Yellow for Electricity

        # Create bar chart
        bars = ax.bar(range(len(scenarios)), costs, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

        # Customize
        ax.set_ylabel('2050년 누적 비용 (십억 $)', fontsize=12, fontweight='bold')
        ax.set_title('6개 시나리오 비용 비교 (2025-2050 누적)', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(range(len(scenarios)))
        ax.set_xticklabels(scenarios, rotation=45, ha='right', fontsize=9)
        ax.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for i, (bar, cost) in enumerate(zip(bars, costs)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${cost:.1f}B',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#4ECDC4', edgecolor='black', label='NCC-H₂ 경로'),
            Patch(facecolor='#FFE66D', edgecolor='black', label='NCC-전기 경로')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

        plt.tight_layout()
        output_path = self.output_dir / '01_scenario_cost_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Chart 1 saved: {output_path}")

    def chart_2_company_abatement_top10(self):
        """Chart 2: 기업별 감축량 Top 10"""
        if self.df_company_baseline is None:
            print("⚠️ Cannot generate Chart 2: No company data")
            return

        fig, ax = plt.subplots(figsize=(10, 8))

        # Get top 10 companies
        df_top10 = self.df_company_baseline.nlargest(10, 'emissions_mt').copy()

        # Create horizontal bar chart
        y_pos = np.arange(len(df_top10))
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(df_top10)))

        bars = ax.barh(y_pos, df_top10['emissions_mt'], color=colors, edgecolor='black', linewidth=1.5)

        # Customize
        ax.set_yticks(y_pos)
        ax.set_yticklabels(df_top10['company'], fontsize=11)
        ax.set_xlabel('총 감축 잠재량 (Mt CO₂)', fontsize=12, fontweight='bold')
        ax.set_title('기업별 감축 잠재량 Top 10', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)

        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, df_top10['emissions_mt'])):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f' {value:.1f} Mt',
                   ha='left', va='center', fontsize=10, fontweight='bold')

        # Invert y-axis to show #1 at top
        ax.invert_yaxis()

        plt.tight_layout()
        output_path = self.output_dir / '02_company_abatement_top10.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Chart 2 saved: {output_path}")

    def chart_3_company_tech_mix_top10(self):
        """Chart 3: 기업별 기술 믹스 Top 10"""
        if self.df_facility is None or self.df_company_baseline is None:
            print("⚠️ Cannot generate Chart 3: No facility data")
            return

        # Get top 10 companies by baseline emissions
        top10_companies = self.df_company_baseline.nlargest(10, 'emissions_mt')['company'].values

        # Aggregate by company
        df_company_tech = self.df_facility[self.df_facility['company'].isin(top10_companies)].groupby('company').agg({
            'tech_heat_pump_pct': 'mean',
            'tech_ncc_h2_pct': 'mean',
            'tech_ncc_elec_pct': 'mean',
            'tech_re_ppa_pct': 'mean',
        }).reset_index()

        # Sort by same order as top 10
        df_company_tech['company'] = pd.Categorical(
            df_company_tech['company'],
            categories=top10_companies,
            ordered=True
        )
        df_company_tech = df_company_tech.sort_values('company')

        # Create stacked bar chart
        fig, ax = plt.subplots(figsize=(12, 6))

        companies = df_company_tech['company']
        heat_pump = df_company_tech['tech_heat_pump_pct']
        ncc_h2 = df_company_tech['tech_ncc_h2_pct']
        ncc_elec = df_company_tech['tech_ncc_elec_pct']
        re_ppa = df_company_tech['tech_re_ppa_pct']

        x = np.arange(len(companies))
        width = 0.6

        ax.bar(x, heat_pump, width, label='Heat Pump', color='#FF6B6B', edgecolor='black', linewidth=0.5)
        ax.bar(x, ncc_h2, width, bottom=heat_pump, label='NCC-H₂', color='#4ECDC4', edgecolor='black', linewidth=0.5)
        ax.bar(x, ncc_elec, width, bottom=heat_pump+ncc_h2, label='NCC-전기', color='#95E1D3', edgecolor='black', linewidth=0.5)
        ax.bar(x, re_ppa, width, bottom=heat_pump+ncc_h2+ncc_elec, label='RE_PPA', color='#FFE66D', edgecolor='black', linewidth=0.5)

        ax.set_ylabel('기술 적용률 (%)', fontsize=12, fontweight='bold')
        ax.set_title('기업별 기술 믹스 (Top 10)', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(companies, rotation=45, ha='right', fontsize=9)
        ax.legend(loc='upper right', fontsize=10, frameon=True, fancybox=True, shadow=True)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / '03_company_tech_mix_top10.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Chart 3 saved: {output_path}")

    def chart_4_regional_abatement(self):
        """Chart 4: 지역별 감축량 분포"""
        if self.df_region_baseline is None:
            print("⚠️ Cannot generate Chart 4: No regional data")
            return

        fig, ax = plt.subplots(figsize=(10, 6))

        # Sort by emissions
        df_sorted = self.df_region_baseline.sort_values('emissions_mt', ascending=False)

        # Create bar chart with gradient colors
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(df_sorted)))
        bars = ax.bar(df_sorted['location'], df_sorted['emissions_mt'],
                      color=colors, edgecolor='black', linewidth=1.5)

        ax.set_ylabel('총 감축 잠재량 (Mt CO₂)', fontsize=12, fontweight='bold')
        ax.set_title('지역별 감축 잠재량', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('지역', fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        # Add value labels and percentage
        total = df_sorted['emissions_mt'].sum()
        for bar, value in zip(bars, df_sorted['emissions_mt']):
            height = bar.get_height()
            pct = (value / total) * 100
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f} Mt\n({pct:.1f}%)',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        plt.tight_layout()
        output_path = self.output_dir / '04_regional_abatement.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Chart 4 saved: {output_path}")

    def chart_5_regional_share_donut(self):
        """Chart 5: 지역별 감축 비중 (도넛 차트)"""
        if self.df_region_baseline is None:
            print("⚠️ Cannot generate Chart 5: No regional data")
            return

        fig, ax = plt.subplots(figsize=(10, 8))

        # Sort by emissions
        df_sorted = self.df_region_baseline.sort_values('emissions_mt', ascending=False)

        # Create donut chart
        colors = ['#FF6B6B', '#4ECDC4', '#95E1D3', '#FFE66D', '#F38181', '#AA96DA']
        wedges, texts, autotexts = ax.pie(
            df_sorted['emissions_mt'],
            labels=df_sorted['location'],
            autopct='%1.1f%%',
            startangle=90,
            colors=colors[:len(df_sorted)],
            explode=[0.05] * len(df_sorted),
            wedgeprops=dict(width=0.5, edgecolor='black', linewidth=2)
        )

        # Style the text
        for text in texts:
            text.set_fontsize(12)
            text.set_fontweight('bold')

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')

        ax.set_title('지역별 감축 잠재량 분포', fontsize=14, fontweight='bold', pad=20)

        # Add legend with values
        legend_labels = [f'{loc}: {val:.1f} Mt' for loc, val in zip(df_sorted['location'], df_sorted['emissions_mt'])]
        ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)

        plt.tight_layout()
        output_path = self.output_dir / '05_regional_share_donut.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Chart 5 saved: {output_path}")

    def chart_6_regional_tech_mix(self):
        """Chart 6: 지역별 기술 믹스"""
        if self.df_facility is None:
            print("⚠️ Cannot generate Chart 6: No facility data")
            return

        # Aggregate by region
        df_region_tech = self.df_facility.groupby('location').agg({
            'tech_heat_pump_pct': 'mean',
            'tech_ncc_h2_pct': 'mean',
            'tech_ncc_elec_pct': 'mean',
            'tech_re_ppa_pct': 'mean',
            'abatement_mt': 'sum'
        }).reset_index()

        # Sort by total abatement
        df_region_tech = df_region_tech.sort_values('abatement_mt', ascending=False)

        # Create stacked bar chart
        fig, ax = plt.subplots(figsize=(10, 6))

        regions = df_region_tech['location']
        heat_pump = df_region_tech['tech_heat_pump_pct']
        ncc_h2 = df_region_tech['tech_ncc_h2_pct']
        ncc_elec = df_region_tech['tech_ncc_elec_pct']
        re_ppa = df_region_tech['tech_re_ppa_pct']

        x = np.arange(len(regions))
        width = 0.6

        ax.bar(x, heat_pump, width, label='Heat Pump', color='#FF6B6B', edgecolor='black', linewidth=0.5)
        ax.bar(x, ncc_h2, width, bottom=heat_pump, label='NCC-H₂', color='#4ECDC4', edgecolor='black', linewidth=0.5)
        ax.bar(x, ncc_elec, width, bottom=heat_pump+ncc_h2, label='NCC-전기', color='#95E1D3', edgecolor='black', linewidth=0.5)
        ax.bar(x, re_ppa, width, bottom=heat_pump+ncc_h2+ncc_elec, label='RE_PPA', color='#FFE66D', edgecolor='black', linewidth=0.5)

        ax.set_ylabel('기술 적용률 (%)', fontsize=12, fontweight='bold')
        ax.set_title('지역별 기술 믹스', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('지역', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(regions, fontsize=11)
        ax.legend(loc='upper right', fontsize=10, frameon=True, fancybox=True, shadow=True)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / '06_regional_tech_mix.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Chart 6 saved: {output_path}")

    def generate_all_charts(self):
        """Generate all charts"""
        print("="*80)
        print("📊 보고서용 차트 생성 중...")
        print("="*80)
        print()

        print("데이터 로딩 완료\n")

        print("차트 생성 중:")
        self.chart_1_scenario_cost_comparison()
        self.chart_2_company_abatement_top10()
        self.chart_3_company_tech_mix_top10()
        self.chart_4_regional_abatement()
        self.chart_5_regional_share_donut()
        self.chart_6_regional_tech_mix()

        print()
        print("="*80)
        print(f"✅ 모든 차트 생성 완료!")
        print(f"   저장 위치: {self.output_dir}")
        print(f"   생성된 파일: 6개 PNG")
        print("="*80)

        return self.output_dir

# Main execution
if __name__ == "__main__":
    generator = ReportChartGenerator()
    output_dir = generator.generate_all_charts()

    print()
    print("📁 생성된 파일 목록:")
    for i, file in enumerate(sorted(output_dir.glob('*.png')), 1):
        size_kb = file.stat().st_size / 1024
        print(f"   {i}. {file.name} ({size_kb:.1f} KB)")

    print()
    print("💡 사용 방법:")
    print("   1. Word 문서 열기: MACC_Model_Detailed_Report_20251030.docx")
    print("   2. 플레이스홀더 위치에 해당 PNG 파일 삽입")
    print("   3. 그림 크기 조정 (페이지 너비에 맞춤)")
