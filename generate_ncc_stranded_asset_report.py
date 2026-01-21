"""
NCC Stranded Asset Report Generator (Carbon Budget Perspective)
================================================================

좌초자산 정의: 탄소예산 초과 시점에서의 시설 잔존가치
- 1.5°C 경로: 더 엄격한 탄소예산, 조기 소진
- 2.0°C 경로: 상대적으로 여유로운 탄소예산

Generates 3 key report tables for NCC (Naphtha Cracker) stranded asset analysis:
1. Scenario Comparison Table
2. Stranded Asset Analysis (NCC only, Carbon Budget Perspective)
3. Technology Roadmap Table

CAPEX: $3,000/t for NCC facilities
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Configuration
OUTPUT_DIR = Path('outputs')
REPORT_DIR = OUTPUT_DIR / 'report_tables'
DATA_DIR = Path('data')

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Exchange rate
KRW_PER_USD = 1300

# NCC CAPEX ($/t-capacity/yr)
NCC_CAPEX = 3000
NCC_USEFUL_LIFE = 40

SCENARIO_NAMES_KR = {
    'shaheen_ncc_h2': '수소기반 전환 (NCC-H2)',
    'shaheen_ncc_elec': '전기화 전환 (NCC-Elec)',
}

REGION_NAMES_KR = {
    'Yeosu': '여수',
    'Daesan': '대산',
    'Ulsan': '울산',
    'Other': '기타',
}


def load_data():
    """Load required data"""
    results = pd.read_csv(OUTPUT_DIR / 'scenario_results.csv')
    stranded_summary = pd.read_csv(OUTPUT_DIR / 'stranded_assets_summary.csv')
    stranded_facilities = pd.read_csv(OUTPUT_DIR / 'stranded_assets_facilities.csv')

    # Load facility data to get year_built
    try:
        baseline_shaheen = pd.read_csv(DATA_DIR / 'facilities' / 'baseline_shaheen.csv')
    except:
        baseline_shaheen = None

    return results, stranded_summary, stranded_facilities, baseline_shaheen


def get_ncc_facilities(df):
    """Filter to NCC facilities only"""
    return df[df['process'] == 'Naphtha Cracker'].copy()


def generate_table1_scenario_comparison(df, stranded_summary):
    """
    Table 1: Scenario Comparison Table
    시나리오 비교표
    """
    print("\n" + "="*60)
    print("TABLE 1: SCENARIO COMPARISON / 시나리오 비교표")
    print("="*60)

    rows = []

    for scenario in df['scenario'].unique():
        scenario_df = df[df['scenario'] == scenario]
        ncc_df = get_ncc_facilities(scenario_df)

        # 2025 baseline
        baseline_2025 = scenario_df[scenario_df['year'] == 2025]
        ncc_baseline_2025 = ncc_df[ncc_df['year'] == 2025]

        # 2050 final
        final_2050 = scenario_df[scenario_df['year'] == 2050]

        # Emissions
        total_emissions_2025 = baseline_2025['emissions_tco2'].sum()
        total_emissions_2050 = final_2050['emissions_tco2'].sum()

        # Facility counts
        total_facilities = baseline_2025['facility_id'].nunique()
        ncc_facilities = ncc_baseline_2025['facility_id'].nunique()

        # Total CAPEX (deployment)
        deployed = scenario_df[scenario_df['tech_deployed'] == 1]
        total_capex = deployed['capex_usd'].sum()

        # Energy demands (2050)
        h2_demand_2050 = final_2050['h2_demand_t'].sum()
        elec_demand_2050 = final_2050['elec_demand_mwh'].sum()

        # Stranded asset info
        stranded_row = stranded_summary[stranded_summary['scenario'] == scenario]
        if len(stranded_row) > 0:
            stranding_year_15c = int(stranded_row['stranding_year_1.5C'].iloc[0])
            stranded_value_15c = stranded_row['stranded_value_1.5C_usd'].iloc[0]
        else:
            stranding_year_15c = None
            stranded_value_15c = 0

        rows.append({
            'scenario': scenario,
            'scenario_name_kr': SCENARIO_NAMES_KR.get(scenario, scenario),
            'production_pathway': 'Shaheen 프로젝트 포함',
            'ncc_technology': 'NCC-H2 (수소 연소)' if 'h2' in scenario else 'NCC-Elec (전기 크래커)',
            'total_facilities': total_facilities,
            'ncc_facilities': ncc_facilities,
            'emissions_2025_mtco2': total_emissions_2025 / 1e6,
            'emissions_2050_mtco2': total_emissions_2050 / 1e6,
            'total_capex_billion_usd': total_capex / 1e9,
            'total_capex_trillion_krw': (total_capex * KRW_PER_USD) / 1e12,
            'h2_demand_2050_kt': h2_demand_2050 / 1e3,
            'elec_demand_2050_twh': elec_demand_2050 / 1e6,
            'stranding_year_15c': stranding_year_15c,
            'stranded_value_15c_billion_usd': stranded_value_15c / 1e9,
        })

    result_df = pd.DataFrame(rows)
    result_df.to_csv(REPORT_DIR / 'table1_scenario_comparison.csv', index=False, encoding='utf-8-sig')

    # Print formatted table
    print("\n| 구분 | 수소기반 전환 (NCC-H2) | 전기화 전환 (NCC-Elec) |")
    print("|------|----------------------|----------------------|")

    h2_row = result_df[result_df['scenario'].str.contains('h2')].iloc[0] if len(result_df[result_df['scenario'].str.contains('h2')]) > 0 else None
    elec_row = result_df[result_df['scenario'].str.contains('elec')].iloc[0] if len(result_df[result_df['scenario'].str.contains('elec')]) > 0 else None

    if h2_row is not None and elec_row is not None:
        print(f"| **생산경로** | {h2_row['production_pathway']} | {elec_row['production_pathway']} |")
        print(f"| **NCC 전환기술** | {h2_row['ncc_technology']} | {elec_row['ncc_technology']} |")
        print(f"| **총 시설수** | {int(h2_row['total_facilities'])}개 | {int(elec_row['total_facilities'])}개 |")
        print(f"| **NCC 시설수** | {int(h2_row['ncc_facilities'])}개 | {int(elec_row['ncc_facilities'])}개 |")
        print(f"| **2025 배출량** | {h2_row['emissions_2025_mtco2']:.1f} MtCO2 | {elec_row['emissions_2025_mtco2']:.1f} MtCO2 |")
        print(f"| **2050 배출량** | {h2_row['emissions_2050_mtco2']:.1f} MtCO2 | {elec_row['emissions_2050_mtco2']:.1f} MtCO2 |")
        print(f"| **총 투자비** | ${h2_row['total_capex_billion_usd']:.1f}B | ${elec_row['total_capex_billion_usd']:.1f}B |")
        print(f"| **수소 수요 (2050)** | {h2_row['h2_demand_2050_kt']:,.0f} kt | {elec_row['h2_demand_2050_kt']:,.0f} kt |")
        print(f"| **전력 수요 (2050)** | {h2_row['elec_demand_2050_twh']:.1f} TWh | {elec_row['elec_demand_2050_twh']:.1f} TWh |")
        print(f"| **탄소예산 소진 (1.5°C)** | {int(h2_row['stranding_year_15c'])}년 | {int(elec_row['stranding_year_15c'])}년 |")

    return result_df


def generate_table2_stranded_assets(df, stranded_summary, stranded_facilities):
    """
    Table 2: Stranded Asset Analysis (NCC Facilities Only) - Carbon Budget Perspective
    좌초자산 분석표 (탄소예산 관점)
    """
    print("\n" + "="*60)
    print("TABLE 2: NCC STRANDED ASSET ANALYSIS (CARBON BUDGET)")
    print("좌초자산 = 탄소예산 초과 시점의 잔존 장부가치")
    print("="*60)

    # Filter to NCC facilities only
    ncc_stranded = stranded_facilities[stranded_facilities['process'] == 'Naphtha Cracker'].copy()

    # ----- 2-1: Scenario Summary (1.5C and 2.0C) -----
    print("\n### 2-1. 시나리오별 좌초자산 요약\n")

    summary_rows = []

    for _, row in stranded_summary.iterrows():
        scenario = row['scenario']
        scenario_name = SCENARIO_NAMES_KR.get(scenario, scenario)

        # Get NCC-only values for this scenario
        ncc_15c = ncc_stranded[(ncc_stranded['scenario'] == scenario) & (ncc_stranded['budget_scenario'] == '1.5C')]
        ncc_value_15c = ncc_15c['stranded_value_usd'].sum() if len(ncc_15c) > 0 else 0

        # For 2.0C, we need to recalculate - the stranded_facilities might only have 1.5C
        # Let's use the ratio from the overall summary
        total_15c = row['stranded_value_1.5C_usd']
        total_20c = row['stranded_value_2.0C_usd']
        ratio = (total_20c / total_15c) if total_15c > 0 else 0
        ncc_value_20c = ncc_value_15c * ratio

        summary_rows.append({
            'scenario': scenario,
            'scenario_name_kr': scenario_name,
            'stranding_year_15c': int(row['stranding_year_1.5C']),
            'ncc_stranded_15c_billion_usd': ncc_value_15c / 1e9,
            'ncc_stranded_15c_trillion_krw': (ncc_value_15c * KRW_PER_USD) / 1e12,
            'stranding_year_20c': int(row['stranding_year_2.0C']),
            'ncc_stranded_20c_billion_usd': ncc_value_20c / 1e9,
            'ncc_stranded_20c_trillion_krw': (ncc_value_20c * KRW_PER_USD) / 1e12,
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(REPORT_DIR / 'table2_1_stranded_summary.csv', index=False, encoding='utf-8-sig')

    print("| 시나리오 | 1.5°C 예산소진 | NCC 좌초자산 | 2.0°C 예산소진 | NCC 좌초자산 |")
    print("|---------|--------------|-------------|--------------|-------------|")

    for _, row in summary_df.iterrows():
        print(f"| {row['scenario_name_kr']} | {row['stranding_year_15c']}년 | ${row['ncc_stranded_15c_billion_usd']:.1f}B (₩{row['ncc_stranded_15c_trillion_krw']:.1f}조) | {row['stranding_year_20c']}년 | ${row['ncc_stranded_20c_billion_usd']:.1f}B (₩{row['ncc_stranded_20c_trillion_krw']:.1f}조) |")

    # ----- 2-2: Company Analysis -----
    print("\n### 2-2. 기업별 좌초자산 위험 (1.5°C 기준, Top 10)")

    # Use H2 scenario for company analysis
    h2_scenario = [s for s in ncc_stranded['scenario'].unique() if 'h2' in s]
    if h2_scenario:
        h2_ncc = ncc_stranded[(ncc_stranded['scenario'] == h2_scenario[0]) & (ncc_stranded['budget_scenario'] == '1.5C')]

        company_agg = h2_ncc.groupby('company').agg({
            'facility_id': 'count',
            'capacity_kt': 'sum',
            'stranded_value_usd': 'sum',
        }).reset_index()
        company_agg = company_agg.sort_values('stranded_value_usd', ascending=False)

        total_stranded = company_agg['stranded_value_usd'].sum()
        company_agg['share_pct'] = (company_agg['stranded_value_usd'] / total_stranded * 100) if total_stranded > 0 else 0

        print("\n| 순위 | 기업명 | NCC 시설수 | 생산능력 (kt/y) | 좌초자산 규모 | 비중 |")
        print("|-----|-------|-----------|----------------|--------------|------|")

        for i, (_, row) in enumerate(company_agg.head(10).iterrows(), 1):
            print(f"| {i} | {row['company']} | {int(row['facility_id'])} | {row['capacity_kt']*1000:,.0f} | ${row['stranded_value_usd']/1e9:.2f}B | {row['share_pct']:.1f}% |")

        company_agg.to_csv(REPORT_DIR / 'table2_2_company_stranded.csv', index=False, encoding='utf-8-sig')

    # ----- 2-3: Regional Distribution -----
    print("\n### 2-3. 지역별 좌초자산 분포 (1.5°C 기준)")

    if h2_scenario:
        region_agg = h2_ncc.groupby('location').agg({
            'facility_id': 'count',
            'stranded_value_usd': 'sum',
        }).reset_index()
        region_agg = region_agg.sort_values('stranded_value_usd', ascending=False)

        total_stranded_region = region_agg['stranded_value_usd'].sum()
        region_agg['share_pct'] = (region_agg['stranded_value_usd'] / total_stranded_region * 100) if total_stranded_region > 0 else 0

        # Map to Korean region names
        region_agg['region_kr'] = region_agg['location'].apply(
            lambda x: '여수' if 'Yeosu' in str(x) else (
                '대산' if 'Daesan' in str(x) else (
                    '울산/온산' if ('Ulsan' in str(x) or 'Onsan' in str(x)) else str(x)
                )
            )
        )

        # Aggregate by Korean region
        region_kr_agg = region_agg.groupby('region_kr').agg({
            'facility_id': 'sum',
            'stranded_value_usd': 'sum',
            'share_pct': 'sum',
        }).reset_index().sort_values('stranded_value_usd', ascending=False)

        print("\n| 지역 | NCC 시설수 | 좌초자산 규모 | 비중 |")
        print("|-----|-----------|--------------|------|")

        for _, row in region_kr_agg.iterrows():
            print(f"| {row['region_kr']} | {int(row['facility_id'])} | ${row['stranded_value_usd']/1e9:.1f}B | {row['share_pct']:.1f}% |")

        region_agg.to_csv(REPORT_DIR / 'table2_3_regional_stranded.csv', index=False, encoding='utf-8-sig')

    # Save NCC-only stranded facility details
    ncc_stranded.to_csv(REPORT_DIR / 'table2_ncc_facility_details.csv', index=False, encoding='utf-8-sig')

    return summary_df


def generate_table3_technology_roadmap(df):
    """
    Table 3: Technology Roadmap Table
    기술 로드맵표
    """
    print("\n" + "="*60)
    print("TABLE 3: TECHNOLOGY ROADMAP / 기술 로드맵표")
    print("="*60)

    ncc_df = get_ncc_facilities(df)

    # ----- 3-1: Annual Transition Plan -----
    print("\n### 3-1. 연도별 NCC 기술 전환 계획")

    key_years = [2025, 2030, 2035, 2040, 2045, 2050]

    roadmap_rows = []

    for scenario in ncc_df['scenario'].unique():
        scenario_df = ncc_df[ncc_df['scenario'] == scenario]
        scenario_name = SCENARIO_NAMES_KR.get(scenario, scenario)

        # Get facilities that deploy each year
        deployed = scenario_df[(scenario_df['tech_deployed'] == 1) & (scenario_df['technology'] != 'Baseline')]

        # Find first deployment year for each facility
        first_deploy = deployed.groupby('facility_id')['year'].min().reset_index()
        first_deploy.columns = ['facility_id', 'install_year']

        total_ncc = scenario_df[scenario_df['year'] == 2025]['facility_id'].nunique()

        for year in key_years:
            # Cumulative deployed by this year
            cumulative = first_deploy[first_deploy['install_year'] <= year]
            cumulative_count = len(cumulative)
            cumulative_pct = (cumulative_count / total_ncc * 100) if total_ncc > 0 else 0

            # New this period
            if year == 2025:
                new_count = len(first_deploy[first_deploy['install_year'] <= 2025])
            else:
                prev_year = key_years[key_years.index(year) - 1]
                new_this_period = first_deploy[(first_deploy['install_year'] > prev_year) & (first_deploy['install_year'] <= year)]
                new_count = len(new_this_period)

            # Get companies deploying this period
            if new_count > 0:
                if year == 2025:
                    new_fac_ids = first_deploy[first_deploy['install_year'] <= 2025]['facility_id'].tolist()
                else:
                    new_fac_ids = first_deploy[(first_deploy['install_year'] > prev_year) & (first_deploy['install_year'] <= year)]['facility_id'].tolist()

                new_data = scenario_df[scenario_df['facility_id'].isin(new_fac_ids)]
                top_companies = new_data.groupby('company')['facility_id'].nunique().sort_values(ascending=False).head(3)
                companies_str = ', '.join(top_companies.index.tolist())
            else:
                companies_str = '-'

            # CAPEX for NCC facilities deployed in this year
            year_df = scenario_df[(scenario_df['year'] == year) & (scenario_df['tech_deployed'] == 1)]
            annual_capex = year_df['capex_usd'].sum() / 1e9

            roadmap_rows.append({
                'scenario': scenario,
                'scenario_name_kr': scenario_name,
                'year': year,
                'new_facilities': new_count,
                'cumulative_facilities': cumulative_count,
                'total_ncc': total_ncc,
                'cumulative_pct': cumulative_pct,
                'annual_capex_billion_usd': annual_capex,
                'top_companies': companies_str,
            })

    roadmap_df = pd.DataFrame(roadmap_rows)
    roadmap_df.to_csv(REPORT_DIR / 'table3_1_annual_roadmap.csv', index=False, encoding='utf-8-sig')

    # Print for both scenarios
    for scenario_name in roadmap_df['scenario_name_kr'].unique():
        print(f"\n**{scenario_name}**\n")
        print("| 연도 | 신규 전환 | 누적 전환 | 전환율 | NCC CAPEX |")
        print("|-----|---------|---------|-------|-----------|")

        scenario_roadmap = roadmap_df[roadmap_df['scenario_name_kr'] == scenario_name]
        for _, row in scenario_roadmap.iterrows():
            print(f"| {int(row['year'])} | {int(row['new_facilities'])}개 | {int(row['cumulative_facilities'])}/{int(row['total_ncc'])} | {row['cumulative_pct']:.0f}% | ${row['annual_capex_billion_usd']:.1f}B |")

    # ----- 3-2: Technology Comparison -----
    print("\n### 3-2. 기술별 비교")

    tech_comparison = [
        {
            '구분': 'CAPEX ($/t-에틸렌/yr)',
            'NCC-H2 (수소)': '$350 (2025) → $180 (2050)',
            'NCC-Elec (전기)': '$280 (2025) → $150 (2050)',
        },
        {
            '구분': '에너지 수요',
            'NCC-H2 (수소)': '0.2 t-H2/t-에틸렌',
            'NCC-Elec (전기)': '5.0 MWh/t-에틸렌',
        },
        {
            '구분': '기술성숙도 (TRL)',
            'NCC-H2 (수소)': '7',
            'NCC-Elec (전기)': '6-7',
        },
        {
            '구분': '상용화 예상',
            'NCC-H2 (수소)': '2028-2030',
            'NCC-Elec (전기)': '2030-2032',
        },
        {
            '구분': '장점',
            'NCC-H2 (수소)': '고온 공정 적합, 연속운전',
            'NCC-Elec (전기)': '직접 탈탄소, 배출계수 연동',
        },
        {
            '구분': '단점',
            'NCC-H2 (수소)': '수소 인프라 필요',
            'NCC-Elec (전기)': '초기 그리드 배출 높음',
        },
    ]

    tech_df = pd.DataFrame(tech_comparison)
    tech_df.to_csv(REPORT_DIR / 'table3_2_technology_comparison.csv', index=False, encoding='utf-8-sig')

    print("\n| 구분 | NCC-H2 (수소) | NCC-Elec (전기) |")
    print("|-----|--------------|----------------|")
    for row in tech_comparison:
        print(f"| {row['구분']} | {row['NCC-H2 (수소)']} | {row['NCC-Elec (전기)']} |")

    return roadmap_df, tech_df


def generate_carbon_budget_analysis(stranded_summary, stranded_facilities):
    """
    Additional: Carbon Budget Impact Analysis
    탄소예산 영향 분석
    """
    print("\n" + "="*60)
    print("CARBON BUDGET ANALYSIS / 탄소예산 영향 분석")
    print("="*60)

    ncc_stranded = stranded_facilities[stranded_facilities['process'] == 'Naphtha Cracker']

    print("\n**좌초자산 정의**: 탄소예산 초과 시점에서 폐쇄되어야 하는 시설의 잔존 장부가치")
    print("\n**핵심 메시지**:")
    print("- 1.5°C 경로: 2028-2030년 탄소예산 소진 → 대규모 좌초자산 발생")
    print("- 2.0°C 경로: 2041-2050년 탄소예산 소진 → 시설 감가상각으로 좌초자산 감소")
    print()

    for _, row in stranded_summary.iterrows():
        scenario_name = SCENARIO_NAMES_KR.get(row['scenario'], row['scenario'])
        ncc_15c = ncc_stranded[(ncc_stranded['scenario'] == row['scenario']) & (ncc_stranded['budget_scenario'] == '1.5C')]
        ncc_value = ncc_15c['stranded_value_usd'].sum()

        print(f"**{scenario_name}**")
        print(f"  - 1.5°C: {int(row['stranding_year_1.5C'])}년 예산 소진, NCC 좌초자산 ${ncc_value/1e9:.1f}B (₩{ncc_value*KRW_PER_USD/1e12:.1f}조)")
        print(f"  - 2.0°C: {int(row['stranding_year_2.0C'])}년 예산 소진")
        print()


def main():
    """Main execution"""
    print("="*60)
    print("NCC STRANDED ASSET REPORT GENERATOR")
    print("(Carbon Budget Perspective)")
    print("="*60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"CAPEX: $3,000/t | Focus: NCC Only")

    # Load data
    df, stranded_summary, stranded_facilities, baseline_data = load_data()
    print(f"\nLoaded {len(df):,} rows from scenario results")
    print(f"Scenarios: {df['scenario'].unique().tolist()}")

    # Generate tables
    table1 = generate_table1_scenario_comparison(df, stranded_summary)
    table2 = generate_table2_stranded_assets(df, stranded_summary, stranded_facilities)
    table3 = generate_table3_technology_roadmap(df)

    # Additional analysis
    generate_carbon_budget_analysis(stranded_summary, stranded_facilities)

    print("\n" + "="*60)
    print("REPORT GENERATION COMPLETE")
    print("="*60)
    print(f"Output directory: {REPORT_DIR}")
    print("\nGenerated files:")
    print("  - table1_scenario_comparison.csv")
    print("  - table2_1_stranded_summary.csv")
    print("  - table2_2_company_stranded.csv")
    print("  - table2_3_regional_stranded.csv")
    print("  - table2_ncc_facility_details.csv")
    print("  - table3_1_annual_roadmap.csv")
    print("  - table3_2_technology_comparison.csv")


if __name__ == '__main__':
    main()
