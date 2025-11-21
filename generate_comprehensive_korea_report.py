"""
Generate Comprehensive Report for Korea Petrochemical Industry

This script creates a detailed analysis report including:
1. Industry overview and baseline emissions
2. Technology pathways and costs (MACC analysis)
3. Deployment scenarios and policy implications
4. Stranded asset analysis
5. Regional and sectoral impacts
6. Investment requirements and economic impacts
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime


class KoreaReportGenerator:
    """Comprehensive report generator for Korea petrochemical decarbonization"""

    def __init__(self, output_dir='outputs/comprehensive_korea_report'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("COMPREHENSIVE KOREA PETROCHEMICAL INDUSTRY REPORT")
        print("="*80)

        # Load all required data
        self.load_data()

    def load_data(self):
        """Load all necessary data files"""
        print("\n📁 Loading data...")

        # Module 1: Baseline
        self.df_baseline = pd.read_csv('outputs/module_01/baseline_2025_detailed.csv')
        self.df_bau = pd.read_csv('outputs/module_01/bau_trajectory_2025_2050.csv')
        self.df_by_product = pd.read_csv('outputs/module_01/emissions_by_product.csv')
        self.df_by_company = pd.read_csv('outputs/module_01/emissions_by_company.csv')
        self.df_by_location = pd.read_csv('outputs/module_01/emissions_by_location.csv')

        # Module 2: MACC
        self.df_macc = pd.read_csv('outputs/module_02/macc_annual_2025_2050.csv')

        # Module 4: Stranded Assets
        try:
            self.df_assets = pd.read_csv('outputs/module_04_stranded_assets/facility_assets_2025.csv')
            self.df_stranding_summary = pd.read_csv('outputs/module_04_stranded_assets/stranding_summary.csv')
            self.df_regional_stranding = pd.read_csv('outputs/module_04_stranded_assets/regional_stranding.csv')
            self.df_sectoral_stranding = pd.read_csv('outputs/module_04_stranded_assets/sectoral_stranding.csv')
            self.stranded_assets_available = True
        except FileNotFoundError:
            print("   ⚠️  Stranded asset data not found")
            self.stranded_assets_available = False

        # Scenario comparison
        try:
            self.df_scenarios = pd.read_csv('outputs/scenarios_comparison_6scenarios/summary.csv')
        except FileNotFoundError:
            print("   ⚠️  Scenario summary not found")
            self.df_scenarios = None

        print("   ✓ Data loaded successfully")

    def generate_executive_summary(self):
        """Generate executive summary section"""
        print("\n📝 Generating executive summary...")

        summary = {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'baseline_year': 2025,
            'target_year': 2050,
            'total_facilities': len(self.df_baseline),
            'baseline_emissions_mt': self.df_baseline['total_emissions_kt'].sum() / 1000,
            'total_capacity_kt': self.df_baseline['capacity_kt'].sum(),
            'num_companies': self.df_baseline['company'].nunique(),
            'num_locations': self.df_baseline['location'].nunique(),
        }

        # BAU projections
        bau_2050 = self.df_bau[self.df_bau['year'] == 2050].iloc[0]
        summary['bau_emissions_2050_mt'] = bau_2050['total_emissions_mt']
        summary['bau_growth_pct'] = ((bau_2050['total_emissions_mt'] / summary['baseline_emissions_mt']) - 1) * 100

        # Stranded assets (if available)
        if self.stranded_assets_available:
            summary['total_asset_value_billion'] = self.df_assets['book_value_musd'].sum() / 1000
            summary['avg_stranding_rate_pct'] = self.df_stranding_summary['stranding_rate_pct'].mean()

        # Technology costs (2050)
        macc_2050 = self.df_macc[self.df_macc['year'] == 2050]
        summary['ncc_h2_cost_2050'] = macc_2050[macc_2050['technology'] == 'NCC-H2']['total_cost_usd_per_tco2'].iloc[0]
        summary['ncc_elec_cost_2050'] = macc_2050[macc_2050['technology'] == 'NCC-Electricity']['total_cost_usd_per_tco2'].iloc[0]
        summary['re_ppa_cost_2050'] = macc_2050[macc_2050['technology'] == 'RE_PPA']['total_cost_usd_per_tco2'].iloc[0]

        self.exec_summary = summary
        return summary

    def create_industry_overview_section(self):
        """Create detailed industry overview"""
        print("\n📊 Creating industry overview...")

        overview = []

        # 1. Facility distribution
        overview.append({
            'category': 'Facility Distribution',
            'metric': 'By Product Group',
            'data': self.df_by_product[['product_group', 'n_facilities', 'emissions_mt']].to_dict('records')
        })

        # 2. Regional distribution
        overview.append({
            'category': 'Regional Distribution',
            'metric': 'By Location',
            'data': self.df_by_location[['location', 'n_facilities', 'emissions_mt', 'capacity_kt']].to_dict('records')
        })

        # 3. Company concentration
        top_10_companies = self.df_by_company.head(10)
        overview.append({
            'category': 'Market Concentration',
            'metric': 'Top 10 Companies',
            'data': top_10_companies[['company', 'emissions_mt', 'share_pct']].to_dict('records')
        })

        # 4. Age distribution (calculate from year_built if needed)
        if 'facility_age' not in self.df_baseline.columns and 'year_built' in self.df_baseline.columns:
            self.df_baseline['facility_age'] = 2025 - self.df_baseline['year_built']

        if 'facility_age' in self.df_baseline.columns:
            age_dist = self.df_baseline['facility_age'].describe().to_dict()
            overview.append({
                'category': 'Facility Age Distribution',
                'metric': 'Statistics',
                'data': age_dist
            })

        self.industry_overview = overview
        return overview

    def create_technology_analysis_section(self):
        """Analyze technology pathways"""
        print("\n🔬 Creating technology analysis...")

        # MACC cost evolution
        tech_analysis = {}

        for tech in ['NCC-H2', 'NCC-Electricity', 'RE_PPA', 'Heat_Pump']:
            df_tech = self.df_macc[self.df_macc['technology'] == tech]

            if len(df_tech) > 0:
                tech_analysis[tech] = {
                    'cost_2025': df_tech[df_tech['year'] == 2025]['total_cost_usd_per_tco2'].iloc[0],
                    'cost_2050': df_tech[df_tech['year'] == 2050]['total_cost_usd_per_tco2'].iloc[0],
                    'cost_reduction_pct': 0,
                    'abatement_potential_2050_mt': df_tech[df_tech['year'] == 2050]['abatement_potential_mtco2'].iloc[0],
                    'available_year': df_tech[df_tech['available'] == True]['year'].min() if any(df_tech['available']) else None,
                }

                # Calculate cost reduction
                if tech_analysis[tech]['cost_2025'] != 0:
                    tech_analysis[tech]['cost_reduction_pct'] = \
                        ((tech_analysis[tech]['cost_2025'] - tech_analysis[tech]['cost_2050']) /
                         abs(tech_analysis[tech]['cost_2025'])) * 100

        self.tech_analysis = tech_analysis
        return tech_analysis

    def create_stranded_asset_section(self):
        """Detailed stranded asset analysis"""
        if not self.stranded_assets_available:
            print("\n⚠️  Skipping stranded asset section (data not available)")
            return None

        print("\n💰 Creating stranded asset analysis...")

        stranded_analysis = {
            'summary': self.df_stranding_summary.to_dict('records'),
            'regional': self.df_regional_stranding.to_dict('records'),
            'sectoral': self.df_sectoral_stranding.to_dict('records'),
        }

        # Key insights
        stranded_analysis['insights'] = {
            'highest_risk_region': self.df_regional_stranding.sort_values('stranding_rate_pct', ascending=False).iloc[0]['location'],
            'highest_risk_sector': self.df_sectoral_stranding.sort_values('stranding_rate_pct', ascending=False).iloc[0]['product_group'],
            'total_at_risk_billion': self.df_stranding_summary['total_stranded_billion'].mean(),
        }

        self.stranded_analysis = stranded_analysis
        return stranded_analysis

    def create_investment_requirements_section(self):
        """Calculate total investment requirements"""
        print("\n💵 Creating investment analysis...")

        if self.df_scenarios is None:
            print("   ⚠️  No scenario data available")
            return None

        investment_analysis = []

        for _, scenario in self.df_scenarios.iterrows():
            # Calculate total retrofit investment from stranded asset analysis
            if self.stranded_assets_available:
                scenario_name = scenario['scenario_id']
                matching_stranding = self.df_stranding_summary[
                    self.df_stranding_summary['scenario'].str.contains(scenario_name, na=False)
                ]

                if len(matching_stranding) > 0:
                    retrofit_capex = matching_stranding.iloc[0]['retrofit_capex_billion']
                else:
                    retrofit_capex = None
            else:
                retrofit_capex = None

            investment_analysis.append({
                'scenario': scenario['scenario'],
                'production_pathway': scenario['production_pathway'],
                'technology': scenario['technology_pathway'],
                'emissions_reduction_mt': scenario['bau_emissions_2050_mt'] - scenario['emissions_2050_mt'],
                'emissions_reduction_pct': ((scenario['bau_emissions_2050_mt'] - scenario['emissions_2050_mt']) /
                                            scenario['bau_emissions_2050_mt']) * 100,
                'operational_cost_2050_billion': scenario['cost_2050_billion_usd'],
                'retrofit_capex_billion': retrofit_capex,
                'h2_consumption_kt': scenario.get('h2_consumption_kt', 0),
                'electricity_increase_twh': scenario.get('electricity_increase_twh', 0),
            })

        df_investment = pd.DataFrame(investment_analysis)
        self.investment_analysis = df_investment
        return df_investment

    def create_policy_recommendations(self):
        """Generate policy recommendations"""
        print("\n📋 Creating policy recommendations...")

        recommendations = []

        # 1. Technology support
        recommendations.append({
            'category': 'Technology Development',
            'priority': 'High',
            'recommendation': 'Accelerate R&D and deployment of NCC-H2 and electric cracking technologies',
            'rationale': f"NCC technologies can abate {self.df_macc[(self.df_macc['year']==2050) & (self.df_macc['technology'].isin(['NCC-H2', 'NCC-Electricity']))]['abatement_potential_mtco2'].sum():.1f} MtCO2/year by 2050",
            'implementation': 'Government R&D funding, pilot project support, technology demonstration programs'
        })

        # 2. Stranded asset management
        if self.stranded_assets_available:
            avg_stranding = self.df_stranding_summary['stranding_rate_pct'].mean()
            recommendations.append({
                'category': 'Asset Transition Support',
                'priority': 'High',
                'recommendation': 'Establish transition fund for stranded assets',
                'rationale': f"Average stranding rate of {avg_stranding:.1f}% requires financial support mechanisms",
                'implementation': 'Transition bonds, early retirement schemes, workforce retraining programs'
            })

        # 3. Regional coordination
        if hasattr(self, 'df_regional_stranding'):
            high_risk_regions = self.df_regional_stranding[
                self.df_regional_stranding['stranding_rate_pct'] > 150
            ]['location'].unique()

            recommendations.append({
                'category': 'Regional Policy',
                'priority': 'Medium',
                'recommendation': 'Targeted support for high-impact regions',
                'rationale': f"{len(high_risk_regions)} regions face stranding rates >150%",
                'implementation': 'Regional industrial transition plans, infrastructure investment'
            })

        # 4. Renewable energy infrastructure
        if self.df_scenarios is not None:
            max_re_need = self.df_scenarios['electricity_increase_twh'].max()
            recommendations.append({
                'category': 'Energy Infrastructure',
                'priority': 'High',
                'recommendation': 'Massive renewable energy capacity expansion',
                'rationale': f"Up to {max_re_need:.1f} TWh additional renewable electricity needed by 2050",
                'implementation': 'Grid expansion, offshore wind development, RE PPA frameworks'
            })

        # 5. H2 infrastructure
        if self.df_scenarios is not None:
            max_h2_need = self.df_scenarios['h2_consumption_kt'].max()
            recommendations.append({
                'category': 'Hydrogen Infrastructure',
                'priority': 'High',
                'recommendation': 'Develop national hydrogen supply infrastructure',
                'rationale': f"Up to {max_h2_need:.0f} kt/year green hydrogen required for NCC-H2 pathway",
                'implementation': 'Hydrogen production facilities, pipeline network, import terminals'
            })

        self.policy_recommendations = recommendations
        return recommendations

    def generate_report(self):
        """Generate complete report"""
        print("\n" + "="*80)
        print("GENERATING COMPREHENSIVE REPORT")
        print("="*80)

        # Generate all sections
        exec_summary = self.generate_executive_summary()
        industry_overview = self.create_industry_overview_section()
        tech_analysis = self.create_technology_analysis_section()
        stranded_analysis = self.create_stranded_asset_section()
        investment_analysis = self.create_investment_requirements_section()
        policy_recs = self.create_policy_recommendations()

        # Save comprehensive summary to CSV
        self._save_summary_tables()

        # Create final report document
        self._create_report_markdown()

        print("\n" + "="*80)
        print("✓ REPORT GENERATION COMPLETE")
        print("="*80)
        print(f"\nOutputs saved to: {self.output_dir}")

        return {
            'executive_summary': exec_summary,
            'industry_overview': industry_overview,
            'technology_analysis': tech_analysis,
            'stranded_assets': stranded_analysis,
            'investment_requirements': investment_analysis,
            'policy_recommendations': policy_recs,
        }

    def _save_summary_tables(self):
        """Save summary tables to CSV"""
        print("\n💾 Saving summary tables...")

        # Executive summary
        pd.DataFrame([self.exec_summary]).to_csv(
            self.output_dir / 'executive_summary.csv', index=False
        )

        # Technology analysis
        pd.DataFrame(self.tech_analysis).T.to_csv(
            self.output_dir / 'technology_analysis.csv'
        )

        # Investment requirements
        if self.investment_analysis is not None:
            self.investment_analysis.to_csv(
                self.output_dir / 'investment_requirements.csv', index=False
            )

        # Policy recommendations
        pd.DataFrame(self.policy_recommendations).to_csv(
            self.output_dir / 'policy_recommendations.csv', index=False
        )

    def _create_report_markdown(self):
        """Create detailed markdown report"""
        print("\n📄 Creating markdown report...")

        report_md = f"""# Korea Petrochemical Industry Decarbonization Report
## Comprehensive Analysis and Strategic Recommendations

**Report Date:** {self.exec_summary['report_date']}

---

## Executive Summary

### Industry Overview
- **Total Facilities:** {self.exec_summary['total_facilities']}
- **Total Capacity:** {self.exec_summary['total_capacity_kt']:,.0f} kt/year
- **Baseline Emissions (2025):** {self.exec_summary['baseline_emissions_mt']:.1f} MtCO2
- **BAU Projection (2050):** {self.exec_summary['bau_emissions_2050_mt']:.1f} MtCO2
- **Companies:** {self.exec_summary['num_companies']}
- **Locations:** {self.exec_summary['num_locations']}

### Key Findings

1. **Baseline Emissions:** Korea's petrochemical industry currently emits approximately {self.exec_summary['baseline_emissions_mt']:.1f} MtCO2 annually, expected to grow to {self.exec_summary['bau_emissions_2050_mt']:.1f} MtCO2 by 2050 under business-as-usual.

2. **Decarbonization Technologies:** Three main pathways are available:
   - **NCC-H2:** Hydrogen-based naphtha cracking (Cost: ${self.exec_summary['ncc_h2_cost_2050']:.0f}/tCO2 in 2050)
   - **NCC-Electricity:** Electric cracking (Cost: ${self.exec_summary['ncc_elec_cost_2050']:.0f}/tCO2 in 2050)
   - **RE PPA:** Renewable electricity procurement (Cost: ${self.exec_summary['re_ppa_cost_2050']:.0f}/tCO2 in 2050)

"""

        if self.stranded_assets_available:
            report_md += f"""
3. **Stranded Assets:** Total asset book value of ${self.exec_summary['total_asset_value_billion']:.1f}B at risk, with average stranding rate of {self.exec_summary['avg_stranding_rate_pct']:.1f}% across scenarios.
"""

        report_md += """
---

## 1. Industry Structure and Baseline

### 1.1 Facility Distribution

"""

        # Add product group table
        report_md += "#### By Product Group\n\n"
        report_md += self._df_to_markdown_table(self.df_by_product)

        report_md += "\n\n#### By Location\n\n"
        report_md += self._df_to_markdown_table(self.df_by_location)

        report_md += """

---

## 2. Technology Pathways and Costs

### 2.1 MACC Analysis Summary

"""

        # Add technology cost table
        tech_df = pd.DataFrame(self.tech_analysis).T
        report_md += self._df_to_markdown_table(tech_df)

        if self.stranded_assets_available:
            report_md += """

---

## 3. Stranded Asset Analysis

### 3.1 Summary by Scenario

"""
            report_md += self._df_to_markdown_table(self.df_stranding_summary)

            report_md += """

### 3.2 Regional Impact

"""
            # Group by location and show average
            regional_avg = self.df_regional_stranding.groupby('location').agg({
                'book_value_musd': 'mean',
                'total_stranded_musd': 'mean',
                'stranding_rate_pct': 'mean'
            }).reset_index()
            report_md += self._df_to_markdown_table(regional_avg)

        report_md += """

---

## 4. Investment Requirements

"""
        if self.investment_analysis is not None:
            report_md += self._df_to_markdown_table(self.investment_analysis)

        report_md += """

---

## 5. Policy Recommendations

"""

        for i, rec in enumerate(self.policy_recommendations, 1):
            report_md += f"""
### {i}. {rec['category']} (Priority: {rec['priority']})

**Recommendation:** {rec['recommendation']}

**Rationale:** {rec['rationale']}

**Implementation:** {rec['implementation']}

"""

        report_md += """
---

## Conclusions

Korea's petrochemical industry faces a significant decarbonization challenge requiring coordinated action across technology development, policy support, and investment mobilization. The analysis demonstrates that:

1. Multiple technology pathways are available with decreasing costs over time
2. Substantial capital investment is required for facility retrofits and new infrastructure
3. Stranded asset risks require careful management and support mechanisms
4. Regional coordination is essential given geographic concentration of facilities
5. Policy interventions should prioritize early-stage technology deployment and transition support

**Next Steps:**
- Detailed facility-level transition planning
- Regional industrial strategy development
- Technology pilot programs
- Financial mechanism design
- Stakeholder engagement and coordination

---

*Report generated using MACC Model for Korea Petrochemical Industry*
"""

        # Save markdown report
        with open(self.output_dir / 'comprehensive_report.md', 'w', encoding='utf-8') as f:
            f.write(report_md)

        print(f"   ✓ Saved comprehensive_report.md")

    def _df_to_markdown_table(self, df):
        """Convert DataFrame to markdown table without tabulate dependency"""
        if df.empty:
            return "*No data available*\n"

        # Header
        cols = df.columns.tolist()
        header = "| " + " | ".join(str(c) for c in cols) + " |"
        separator = "| " + " | ".join("---" for _ in cols) + " |"

        # Rows
        rows = []
        for _, row in df.iterrows():
            row_str = "| " + " | ".join(str(v) for v in row.values) + " |"
            rows.append(row_str)

        return "\n".join([header, separator] + rows) + "\n"


def main():
    """Main execution"""
    generator = KoreaReportGenerator()
    results = generator.generate_report()

    print("\n" + "="*80)
    print("REPORT GENERATION COMPLETE")
    print("="*80)
    print("\nGenerated files:")
    print("   - executive_summary.csv")
    print("   - technology_analysis.csv")
    print("   - investment_requirements.csv")
    print("   - policy_recommendations.csv")
    print("   - comprehensive_report.md")


if __name__ == '__main__':
    main()
