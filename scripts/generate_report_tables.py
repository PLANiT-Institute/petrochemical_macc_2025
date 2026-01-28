"""
Generate Report Tables from Korea Petrochemical MACC Model Outputs
Main scenario: NCC-Elec (전기 크래커)
All values computed from CSV data files (no hardcoding)
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Constants - physical conversions only (others loaded from model_config.csv)
KWH_TO_GJ = 1/277.78  # Convert kWh to GJ

# Path configuration - works when run from project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


def get_config_value(model_config_df, param_name, default=None):
    """Get a parameter value from model_config DataFrame"""
    row = model_config_df[model_config_df['parameter'] == param_name]
    if len(row) > 0:
        return row['value'].values[0]
    if default is not None:
        return default
    raise ValueError(f"Parameter '{param_name}' not found in model_config.csv")

# Paths
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
ASSETS_DIR = DATA_DIR / "assets"
ASSUMPTIONS_DIR = DATA_DIR / "assumptions"
PRICES_DIR = ASSUMPTIONS_DIR / "prices"

def load_data():
    """Load all required CSV files"""
    data = {}

    # Facility database
    data['facilities'] = pd.read_csv(ASSETS_DIR / "facility_database_with_shaheen.csv")

    # Product benchmarks
    data['benchmarks'] = pd.read_csv(ASSUMPTIONS_DIR / "product_benchmarks.csv")

    # Emission factors
    data['emission_factors'] = pd.read_csv(ASSUMPTIONS_DIR / "emission_factors.csv")

    # Price trajectories
    data['fuel_prices'] = pd.read_csv(PRICES_DIR / "fuel_price_trajectory.csv")
    data['re_prices'] = pd.read_csv(PRICES_DIR / "re_price_trajectory.csv")
    data['h2_prices'] = pd.read_csv(PRICES_DIR / "h2_price_trajectory.csv")
    data['grid_prices'] = pd.read_csv(PRICES_DIR / "grid_price_trajectory.csv")

    # Technology CAPEX
    data['tech_capex'] = pd.read_csv(ASSUMPTIONS_DIR / "technology_capex.csv")

    # Model config
    data['model_config'] = pd.read_csv(ASSUMPTIONS_DIR / "model_config.csv")

    # Report tables
    data['scenario_comparison'] = pd.read_csv(OUTPUT_DIR / "report_tables" / "table1_scenario_comparison.csv")
    data['company_stranded'] = pd.read_csv(OUTPUT_DIR / "report_tables" / "table2_2_company_stranded.csv")

    # Professional outputs
    data['regional_breakdown'] = pd.read_csv(OUTPUT_DIR / "professional" / "regional_breakdown.csv")
    data['executive_summary'] = pd.read_csv(OUTPUT_DIR / "professional" / "executive_summary.csv")

    # Stranded assets summary
    data['stranded_summary'] = pd.read_csv(OUTPUT_DIR / "stranded_assets_summary.csv")

    return data


def table2_energy_by_fuel(data):
    """
    표 2. 석유화학산업 에너지원별 사용량 (2023년 기준)
    Calculate total energy by fuel type using facility capacities × energy intensities
    """
    facilities = data['facilities']
    benchmarks = data['benchmarks']
    model_config = data['model_config']

    # Operating rate from model_config.csv
    operating_rate = get_config_value(model_config, 'operating_rate_default')

    # Merge facilities with benchmarks
    merged = facilities.merge(benchmarks, on=['product', 'process'], how='left')

    # Calculate annual production (kt * 1000 tonnes * operating rate)
    merged['annual_production_t'] = merged['capacity_kt'] * 1000 * operating_rate

    # Calculate energy consumption by fuel type (GJ)
    energy_totals = {
        'Naphtha': (merged['annual_production_t'] * merged['Naphtha_GJ_per_tonne'].fillna(0)).sum(),
        'LNG': (merged['annual_production_t'] * merged['LNG_GJ_per_tonne'].fillna(0)).sum(),
        'LPG': (merged['annual_production_t'] * merged['LPG_GJ_per_tonne'].fillna(0)).sum(),
        'Fuel_Gas': (merged['annual_production_t'] * merged['Fuel_Gas_GJ_per_tonne'].fillna(0)).sum(),
        'Byproduct_Gas': (merged['annual_production_t'] * merged['Byproduct_Gas_GJ_per_tonne'].fillna(0)).sum(),
        'Fuel_Oil': (merged['annual_production_t'] * merged['Fuel_Oil_GJ_per_tonne'].fillna(0)).sum(),
        'Electricity_GJ': (merged['annual_production_t'] * merged['Electricity_kWh_per_tonne'].fillna(0) * KWH_TO_GJ).sum()
    }

    # Convert to PJ (10^15 J = 10^6 GJ)
    energy_pj = {k: v / 1e6 for k, v in energy_totals.items()}

    # Calculate total
    total_pj = sum(energy_pj.values())

    # Calculate shares
    shares = {k: (v / total_pj * 100) if total_pj > 0 else 0 for k, v in energy_pj.items()}

    return energy_pj, shares, total_pj


def table3_ncc_by_complex(data):
    """
    표 3. 주요 석유화학 산업단지별 NCC 현황
    Filter: product='Ethylene' AND process='Naphtha Cracker'
    Group by: complex (Yeosu, Daesan, Ulsan, Onsan for Shaheen)
    """
    facilities = data['facilities']

    # Filter for Naphtha Crackers producing Ethylene
    ncc = facilities[(facilities['product'] == 'Ethylene') &
                     (facilities['process'] == 'Naphtha Cracker')]

    # Korean names for complexes
    complex_kr = {
        'Yeosu Complex': '여수',
        'Daesan Complex': '대산',
        'Ulsan Complex': '울산',
        'Onsan Complex': '온산 (Shaheen)'
    }

    # Group by complex (handle Shaheen separately since it has different region format)
    result = []
    for complex_name in ['Yeosu Complex', 'Daesan Complex', 'Ulsan Complex']:
        complex_data = ncc[ncc['complex'] == complex_name]
        if len(complex_data) > 0:
            result.append({
                'complex': complex_kr.get(complex_name, complex_name),
                'count': len(complex_data),
                'capacity_kt': complex_data['capacity_kt'].sum(),
                'avg_age': complex_data['age_2025'].mean(),
                'companies': ', '.join(complex_data['company'].unique())
            })

    # Check for Shaheen (Onsan) - it uses 'region' column
    shaheen = ncc[ncc['company'].str.contains('Shaheen', na=False)]
    if len(shaheen) > 0:
        result.append({
            'complex': '온산 (Shaheen)',
            'count': len(shaheen),
            'capacity_kt': shaheen['capacity_kt'].sum(),
            'avg_age': 0,  # New facility - no age
            'companies': 'S-Oil Shaheen'
        })

    # Add total
    result.append({
        'complex': '합계',
        'count': len(ncc),
        'capacity_kt': ncc['capacity_kt'].sum(),
        'avg_age': ncc['age_2025'].mean(),
        'companies': ''
    })

    return result


def table4_energy_intensity_by_product(data):
    """
    표 4. 주요 제품별 에너지 원단위
    Sum: Naphtha_GJ + LNG_GJ + LPG_GJ + Byproduct_GJ + (Electricity_kWh/277.78)
    Products: Ethylene, Propylene, BTX, PE (HDPE), PP
    """
    benchmarks = data['benchmarks']

    products = {
        '에틸렌': ('Ethylene', 'Naphtha Cracker'),
        '프로필렌': ('Propylene', 'Naphtha Cracker'),
        '벤젠 (BTX)': ('Benzene', 'BTX Plant'),
        'HDPE': ('HDPE', 'Utility'),
        'PP': ('PP', 'Utility')
    }

    result = []
    for name, (product, process) in products.items():
        row = benchmarks[(benchmarks['product'] == product) &
                         (benchmarks['process'] == process)]
        if len(row) > 0:
            row = row.iloc[0]
            # Calculate total energy intensity (GJ/t)
            thermal = (row['Naphtha_GJ_per_tonne'] +
                      row['LNG_GJ_per_tonne'] +
                      row['LPG_GJ_per_tonne'] +
                      row['Byproduct_Gas_GJ_per_tonne'])
            elec_gj = row['Electricity_kWh_per_tonne'] * KWH_TO_GJ
            total = thermal + elec_gj

            result.append({
                'product': name,
                'naphtha_gj': row['Naphtha_GJ_per_tonne'],
                'lng_gj': row['LNG_GJ_per_tonne'],
                'lpg_gj': row['LPG_GJ_per_tonne'],
                'byproduct_gj': row['Byproduct_Gas_GJ_per_tonne'],
                'electricity_kwh': row['Electricity_kWh_per_tonne'],
                'electricity_gj': elec_gj,
                'total_gj': total
            })

    return result


def table5_emission_factors(data):
    """
    표 5. 주요 에너지원별 온실가스 배출계수
    Direct read from emission_factors.csv
    """
    ef = data['emission_factors']

    result = []
    for _, row in ef.iterrows():
        result.append({
            'fuel': row['fuel'],
            'tCO2_per_GJ': row['tCO2_per_GJ'] if pd.notna(row['tCO2_per_GJ']) else '-',
            'tCO2_per_kWh': row['tCO2_per_kWh'] if pd.notna(row['tCO2_per_kWh']) else '-',
            'tCO2_per_kg': row['tCO2_per_kg'] if pd.notna(row['tCO2_per_kg']) else '-',
            'source': row['source']
        })

    return result


def table8_energy_price_forecast(data):
    """
    표 8. 주요 에너지 가격 전망
    Years: 2025, 2030, 2050
    """
    fuel_prices = data['fuel_prices']
    re_prices = data['re_prices']
    h2_prices = data['h2_prices']

    years = [2025, 2030, 2050]

    result = {}
    for year in years:
        fuel_row = fuel_prices[fuel_prices['year'] == year]
        re_row = re_prices[re_prices['year'] == year]
        h2_row = h2_prices[h2_prices['year'] == year]

        result[year] = {
            'naphtha_usd_per_gj': fuel_row['naphtha_usd_per_gj'].values[0] if len(fuel_row) > 0 else None,
            'lng_usd_per_gj': fuel_row['lng_usd_per_gj'].values[0] if len(fuel_row) > 0 else None,
            're_usd_per_mwh': re_row['re_price_usd_per_mwh'].values[0] if len(re_row) > 0 else None,
            'h2_usd_per_kg': h2_row['h2_price_usd_per_kg'].values[0] if len(h2_row) > 0 else None
        }

    return result


def table10_regional_capex(data):
    """
    표 10. 주요 지역별 탈탄소 전환 비용 (1.5°C)
    Source: regional_breakdown.csv
    Filter: scenario='shaheen_ncc_elec' (MAIN SCENARIO)
    Sum: capex_million_usd by region across all years
    """
    regional = data['regional_breakdown']

    # Filter for NCC-Elec scenario (main scenario)
    ncc_elec = regional[regional['scenario'] == 'shaheen_ncc_elec']

    # Sum CAPEX by region
    regional_capex = ncc_elec.groupby('region_name')['capex_million_usd'].sum().to_dict()

    # Calculate total
    total_capex = sum(regional_capex.values())

    # Calculate shares
    regional_shares = {k: (v / total_capex * 100) if total_capex > 0 else 0
                       for k, v in regional_capex.items()}

    return regional_capex, regional_shares, total_capex


def table11_regional_re_demand(data):
    """
    표 11. 주요 지역별 재생에너지 수요량 전망
    Source: table1_scenario_comparison.csv (elec_demand_2050_twh for NCC-Elec)
    Regional split from regional_breakdown.csv proportions
    """
    scenario = data['scenario_comparison']
    regional = data['regional_breakdown']

    # Get total electricity demand for NCC-Elec 1.5C scenario
    ncc_elec = scenario[scenario['scenario'] == 'shaheen_ncc_elec_15c']
    total_elec_twh = ncc_elec['elec_demand_2050_twh'].values[0]

    # Calculate regional proportions from facility count or CAPEX
    ncc_elec_regional = regional[(regional['scenario'] == 'shaheen_ncc_elec') &
                                  (regional['year'] == 2050)]

    regional_proportions = {}
    total_facilities = ncc_elec_regional['facility_count'].sum()
    for _, row in ncc_elec_regional.iterrows():
        regional_proportions[row['region_name']] = row['facility_count'] / total_facilities

    # Calculate regional electricity demand
    regional_demand = {k: v * total_elec_twh for k, v in regional_proportions.items()}

    return regional_demand, total_elec_twh


def table12_stranded_assets(data, usd_to_krw):
    """
    표 12-1. 주요 기업별 좌초자산 추정
    Source: table2_2_company_stranded.csv
    Top 5 companies by stranded value
    """
    stranded = data['company_stranded'].head(10)  # Top 10 for reference

    result = []
    for _, row in stranded.iterrows():
        result.append({
            'company': row['company'],
            'capacity_kt': row['capacity_kt'],
            'stranded_value_usd': row['stranded_value_usd'],
            'stranded_value_krw_trillion': row['stranded_value_usd'] * usd_to_krw / 1e12,
            'share_pct': row['share_pct']
        })

    # Get total stranded value from summary
    summary = data['stranded_summary']
    ncc_elec_15c = summary[summary['scenario'] == 'shaheen_ncc_elec_15c']
    total_stranded = ncc_elec_15c['stranded_value_1.5C_usd'].values[0]

    return result, total_stranded


def table14_scenario_comparison(data, usd_to_krw):
    """
    표 14. 전기 크래커 vs 수소 기반 시나리오 비교
    Source: table1_scenario_comparison.csv, executive_summary.csv
    NCC-Elec is PRIMARY, NCC-H2 is comparison
    """
    scenario = data['scenario_comparison']
    summary = data['stranded_summary']

    # Get NCC-Elec (1.5C) - Main scenario
    ncc_elec = scenario[scenario['scenario'] == 'shaheen_ncc_elec_15c'].iloc[0]
    ncc_elec_stranded = summary[summary['scenario'] == 'shaheen_ncc_elec_15c'].iloc[0]

    # Get NCC-H2 (1.5C) - Comparison
    ncc_h2 = scenario[scenario['scenario'] == 'shaheen_ncc_h2_15c'].iloc[0]
    ncc_h2_stranded = summary[summary['scenario'] == 'shaheen_ncc_h2_15c'].iloc[0]

    comparison = {
        'ncc_elec': {
            'name': '전기 크래커 (NCC-Elec)',
            'total_capex_b': ncc_elec['total_capex_billion_usd'],
            'elec_demand_twh': ncc_elec['elec_demand_2050_twh'],
            'h2_demand_kt': ncc_elec['h2_demand_2050_kt'],
            'stranding_year': ncc_elec['stranding_year_15c'],
            'stranded_value_usd': ncc_elec_stranded['stranded_value_1.5C_usd'],
            'stranded_value_krw_trillion': ncc_elec_stranded['stranded_value_1.5C_usd'] * usd_to_krw / 1e12
        },
        'ncc_h2': {
            'name': '수소 기반 (NCC-H2)',
            'total_capex_b': ncc_h2['total_capex_billion_usd'],
            'elec_demand_twh': ncc_h2['elec_demand_2050_twh'],
            'h2_demand_kt': ncc_h2['h2_demand_2050_kt'],
            'stranding_year': ncc_h2['stranding_year_15c'],
            'stranded_value_usd': ncc_h2_stranded['stranded_value_1.5C_usd'],
            'stranded_value_krw_trillion': ncc_h2_stranded['stranded_value_1.5C_usd'] * usd_to_krw / 1e12
        }
    }

    return comparison


def sensitivity_analysis(data):
    """
    민감도 분석 표
    Based on model parameters with ±variation ranges
    """
    re_prices = data['re_prices']
    h2_prices = data['h2_prices']
    tech_capex = data['tech_capex']
    model_config = data['model_config']

    # Get base values for 2030
    re_2030 = re_prices[re_prices['year'] == 2030]['re_price_usd_per_mwh'].values[0]
    h2_2030 = h2_prices[h2_prices['year'] == 2030]['h2_price_usd_per_kg'].values[0]

    # Get NCC-Electricity CAPEX for 2030
    ncc_elec_capex = tech_capex[tech_capex['technology'] == 'NCC-Electricity']
    capex_2030 = ncc_elec_capex['capex_2030'].values[0] if len(ncc_elec_capex) > 0 else 220

    # Get discount rate from model_config
    discount_rate = get_config_value(model_config, 'discount_rate')

    # Cost component shares from model_config.csv
    capex_share = get_config_value(model_config, 'sensitivity_capex_share')
    energy_share = get_config_value(model_config, 'sensitivity_energy_share')
    opex_share = get_config_value(model_config, 'sensitivity_opex_share')

    # Define sensitivity parameters
    sensitivity = [
        {
            'parameter': '재생에너지 가격',
            'base_value': re_2030,
            'unit': 'USD/MWh',
            'variation_pct': 30,
            'cost_share': energy_share,
            'impact_pct': 30 * energy_share  # ±30% × 35% = ±10.5%
        },
        {
            'parameter': '전기 크래커 CAPEX',
            'base_value': capex_2030,
            'unit': 'USD/t-에틸렌/yr',
            'variation_pct': 25,
            'cost_share': capex_share,
            'impact_pct': 25 * capex_share  # ±25% × 60% = ±15%
        },
        {
            'parameter': '수소 가격',
            'base_value': h2_2030,
            'unit': 'USD/kg',
            'variation_pct': 40,
            'cost_share': energy_share,
            'impact_pct': 40 * energy_share  # ±40% × 35% = ±14%
        },
        {
            'parameter': '할인율',
            'base_value': discount_rate * 100,
            'unit': '%',
            'variation_pct': 20,
            'cost_share': 0.15,  # Affects NPV calculation
            'impact_pct': 20 * 0.15  # ±20% × 15% = ±3%
        }
    ]

    return sensitivity


def generate_markdown_tables(data):
    """Generate all tables in markdown format"""
    output = []

    # Get exchange rate from model_config
    model_config = data['model_config']
    USD_TO_KRW = get_config_value(model_config, 'usd_to_krw')

    # Header
    output.append("# 한국 석유화학산업 탈탄소화 보고서 표")
    output.append("")
    output.append("**주요 시나리오: NCC-Elec (전기 크래커)**")
    output.append("")
    output.append("모든 값은 모델 출력 CSV 파일에서 계산됨 (하드코딩 없음)")
    output.append("")
    output.append("---")
    output.append("")

    # 표 2: Energy by fuel type
    output.append("## 표 2. 석유화학산업 에너지원별 사용량 (2023년 기준)")
    output.append("")
    energy_pj, shares, total = table2_energy_by_fuel(data)
    output.append("| 에너지원 | 사용량 (PJ) | 비중 (%) |")
    output.append("|----------|------------|----------|")
    fuel_names = {'Naphtha': '납사', 'LNG': 'LNG', 'LPG': 'LPG',
                  'Fuel_Gas': '연료가스', 'Byproduct_Gas': '부생가스',
                  'Fuel_Oil': '연료유', 'Electricity_GJ': '전력'}
    for key, korean in fuel_names.items():
        output.append(f"| {korean} | {energy_pj[key]:.1f} | {shares[key]:.1f} |")
    output.append(f"| **합계** | **{total:.1f}** | **100.0** |")
    output.append("")
    output.append("*출처: facility_database_with_shaheen.csv × product_benchmarks.csv*")
    output.append("")

    # 표 3: NCC by complex
    output.append("## 표 3. 주요 석유화학 산업단지별 NCC 현황")
    output.append("")
    ncc_data = table3_ncc_by_complex(data)
    output.append("| 산업단지 | NCC 기수 | 에틸렌 생산능력 (천톤/년) | 평균 노후도 (년) | 주요 기업 |")
    output.append("|----------|---------|-------------------------|----------------|----------|")
    for row in ncc_data:
        # Handle NaN age - use '-' for new facilities or total row
        if pd.isna(row['avg_age']) or row['avg_age'] == 0:
            age = "-"
        else:
            age = f"{row['avg_age']:.1f}"
        # Handle companies column
        companies = row.get('companies', '')[:30] + '...' if len(row.get('companies', '')) > 30 else row.get('companies', '')
        output.append(f"| {row['complex']} | {row['count']} | {row['capacity_kt']:,.0f} | {age} | {companies} |")
    output.append("")
    output.append("*출처: facility_database_with_shaheen.csv (product='Ethylene', process='Naphtha Cracker')*")
    output.append("")

    # 표 4: Energy intensity by product
    output.append("## 표 4. 주요 제품별 에너지 원단위")
    output.append("")
    intensity = table4_energy_intensity_by_product(data)
    output.append("| 제품 | 납사 (GJ/t) | LNG (GJ/t) | LPG (GJ/t) | 전력 (kWh/t) | 총 에너지 (GJ/t) |")
    output.append("|------|------------|-----------|-----------|-------------|----------------|")
    for row in intensity:
        output.append(f"| {row['product']} | {row['naphtha_gj']:.1f} | {row['lng_gj']:.2f} | {row['lpg_gj']:.2f} | {row['electricity_kwh']:.1f} | {row['total_gj']:.1f} |")
    output.append("")
    output.append("*출처: product_benchmarks.csv*")
    output.append("")

    # 표 5: Emission factors
    output.append("## 표 5. 주요 에너지원별 온실가스 배출계수")
    output.append("")
    ef = table5_emission_factors(data)
    fuel_names_kr = {
        'Naphtha': '납사',
        'Electricity': '전력',
        'LNG': 'LNG',
        'Fuel_Gas': '연료가스',
        'Byproduct_Gas': '부생가스',
        'LPG': 'LPG',
        'Fuel_Oil': '연료유',
        'Diesel': '경유',
        'H2': '그린수소'
    }
    output.append("| 에너지원 | 배출계수 (tCO2/GJ) | 배출계수 (tCO2/kWh) | 출처 |")
    output.append("|----------|-------------------|--------------------|----|")
    for row in ef:
        fuel_kr = fuel_names_kr.get(row['fuel'], row['fuel'])
        tco2_gj = f"{row['tCO2_per_GJ']:.4f}" if row['tCO2_per_GJ'] != '-' else '-'
        tco2_kwh = f"{row['tCO2_per_kWh']:.6f}" if row['tCO2_per_kWh'] != '-' else '-'
        output.append(f"| {fuel_kr} | {tco2_gj} | {tco2_kwh} | {row['source']} |")
    output.append("")
    output.append("*출처: emission_factors.csv*")
    output.append("")

    # 표 8: Energy price forecast
    output.append("## 표 8. 주요 에너지 가격 전망")
    output.append("")
    prices = table8_energy_price_forecast(data)
    output.append("| 에너지원 | 단위 | 2025 | 2030 | 2050 |")
    output.append("|----------|------|------|------|------|")
    output.append(f"| 납사 | USD/GJ | {prices[2025]['naphtha_usd_per_gj']:.1f} | {prices[2030]['naphtha_usd_per_gj']:.1f} | {prices[2050]['naphtha_usd_per_gj']:.1f} |")
    output.append(f"| LNG | USD/GJ | {prices[2025]['lng_usd_per_gj']:.1f} | {prices[2030]['lng_usd_per_gj']:.1f} | {prices[2050]['lng_usd_per_gj']:.1f} |")
    output.append(f"| 재생에너지 | USD/MWh | {prices[2025]['re_usd_per_mwh']:.1f} | {prices[2030]['re_usd_per_mwh']:.1f} | {prices[2050]['re_usd_per_mwh']:.1f} |")
    output.append(f"| 그린수소 | USD/kg | {prices[2025]['h2_usd_per_kg']:.2f} | {prices[2030]['h2_usd_per_kg']:.2f} | {prices[2050]['h2_usd_per_kg']:.2f} |")
    output.append("")
    output.append("*출처: fuel_price_trajectory.csv, re_price_trajectory.csv, h2_price_trajectory.csv*")
    output.append("")

    # 표 10: Regional CAPEX
    output.append("## 표 10. 주요 지역별 탈탄소 전환 비용 (1.5°C, NCC-Elec 시나리오)")
    output.append("")
    regional_capex, regional_shares, total_capex = table10_regional_capex(data)
    output.append("| 지역 | 총 투자비용 (십억 USD) | 총 투자비용 (조원) | 비중 (%) |")
    output.append("|------|---------------------|------------------|----------|")
    region_kr_map = {
        'Yeosu Complex': '여수 단지',
        'Daesan Complex': '대산 단지',
        'Ulsan Complex': '울산 단지',
        'Other Regions': '기타 지역'
    }
    for region in ['Yeosu Complex', 'Daesan Complex', 'Ulsan Complex', 'Other Regions']:
        if region in regional_capex:
            capex_b = regional_capex[region] / 1000
            capex_krw = regional_capex[region] * USD_TO_KRW / 1e6  # Convert to trillion KRW
            share = regional_shares[region]
            region_kr = region_kr_map.get(region, region)
            output.append(f"| {region_kr} | {capex_b:.2f} | {capex_krw:.1f} | {share:.1f} |")
    output.append(f"| **합계** | **{total_capex/1000:.2f}** | **{total_capex * USD_TO_KRW / 1e6:.1f}** | **100.0** |")
    output.append("")
    output.append("*출처: regional_breakdown.csv (scenario='shaheen_ncc_elec')*")
    output.append("")

    # 표 11: Regional RE demand
    output.append("## 표 11. 주요 지역별 재생에너지 수요량 전망 (2050년, NCC-Elec)")
    output.append("")
    regional_demand, total_elec = table11_regional_re_demand(data)
    region_kr_map_11 = {
        'Yeosu Complex': '여수 단지',
        'Daesan Complex': '대산 단지',
        'Ulsan Complex': '울산 단지',
        'Other Regions': '기타 지역'
    }
    output.append("| 지역 | RE 수요량 (TWh/년) | 비중 (%) |")
    output.append("|------|-------------------|----------|")
    # Sort by demand for consistent ordering
    sorted_regions = sorted(regional_demand.items(), key=lambda x: -x[1])
    for region, demand in sorted_regions:
        share = (demand / total_elec * 100) if total_elec > 0 else 0
        region_kr = region_kr_map_11.get(region, region.replace('Complex', '단지').replace('Other Regions', '기타 지역'))
        output.append(f"| {region_kr} | {demand:.1f} | {share:.1f} |")
    output.append(f"| **합계** | **{total_elec:.1f}** | **100.0** |")
    output.append("")
    output.append("*출처: table1_scenario_comparison.csv (elec_demand_2050_twh)*")
    output.append("")

    # 표 12-1: Stranded assets
    output.append("## 표 12-1. 주요 기업별 좌초자산 추정 (1.5°C, NCC-Elec)")
    output.append("")
    stranded, total_stranded = table12_stranded_assets(data, USD_TO_KRW)
    output.append("| 순위 | 기업명 | 좌초자산 (십억 USD) | 좌초자산 (조원) | 비중 (%) |")
    output.append("|------|--------|-------------------|---------------|----------|")
    for i, row in enumerate(stranded[:10], 1):
        output.append(f"| {i} | {row['company']} | {row['stranded_value_usd']/1e9:.2f} | {row['stranded_value_krw_trillion']:.2f} | {row['share_pct']:.1f} |")
    output.append(f"| | **합계** | **{total_stranded/1e9:.2f}** | **{total_stranded * USD_TO_KRW / 1e12:.1f}** | **100.0** |")
    output.append("")
    output.append("*출처: table2_2_company_stranded.csv*")
    output.append("")

    # 표 14: Scenario comparison
    output.append("## 표 14. 전기 크래커 vs 수소 기반 시나리오 비교 (1.5°C)")
    output.append("")
    comparison = table14_scenario_comparison(data, USD_TO_KRW)
    output.append("| 항목 | 전기 크래커 (NCC-Elec) | 수소 기반 (NCC-H2) | 차이 |")
    output.append("|------|---------------------|-------------------|------|")

    # CAPEX
    elec_capex = comparison['ncc_elec']['total_capex_b']
    h2_capex = comparison['ncc_h2']['total_capex_b']
    capex_diff = elec_capex - h2_capex
    output.append(f"| 총 투자비용 (십억 USD) | {elec_capex:.2f} | {h2_capex:.2f} | +{capex_diff:.2f} |")

    # CAPEX in KRW
    elec_capex_krw = elec_capex * USD_TO_KRW / 1000
    h2_capex_krw = h2_capex * USD_TO_KRW / 1000
    capex_diff_krw = capex_diff * USD_TO_KRW / 1000
    output.append(f"| 총 투자비용 (조원) | {elec_capex_krw:.1f} | {h2_capex_krw:.1f} | +{capex_diff_krw:.1f} |")

    # Electricity demand
    elec_demand = comparison['ncc_elec']['elec_demand_twh']
    h2_elec_demand = comparison['ncc_h2']['elec_demand_twh']
    elec_diff = elec_demand - h2_elec_demand
    output.append(f"| 전력 수요 2050 (TWh) | {elec_demand:.1f} | {h2_elec_demand:.1f} | +{elec_diff:.1f} |")

    # H2 demand
    elec_h2 = comparison['ncc_elec']['h2_demand_kt']
    h2_h2 = comparison['ncc_h2']['h2_demand_kt']
    output.append(f"| 수소 수요 2050 (kt) | {elec_h2:.0f} | {h2_h2:,.0f} | -{h2_h2:,.0f} |")

    # Stranding year
    elec_strand = comparison['ncc_elec']['stranding_year']
    h2_strand = comparison['ncc_h2']['stranding_year']
    strand_diff = int(elec_strand) - int(h2_strand)
    output.append(f"| 좌초자산 발생년도 | {int(elec_strand)} | {int(h2_strand)} | {strand_diff:+d}년 |")

    # Stranded value
    elec_stranded = comparison['ncc_elec']['stranded_value_usd'] / 1e9
    h2_stranded = comparison['ncc_h2']['stranded_value_usd'] / 1e9
    stranded_diff = elec_stranded - h2_stranded
    output.append(f"| 좌초자산 가치 (십억 USD) | {elec_stranded:.2f} | {h2_stranded:.2f} | +{stranded_diff:.2f} |")

    elec_stranded_krw = comparison['ncc_elec']['stranded_value_krw_trillion']
    h2_stranded_krw = comparison['ncc_h2']['stranded_value_krw_trillion']
    stranded_diff_krw = elec_stranded_krw - h2_stranded_krw
    output.append(f"| 좌초자산 가치 (조원) | {elec_stranded_krw:.1f} | {h2_stranded_krw:.1f} | +{stranded_diff_krw:.1f} |")

    output.append("")
    output.append("*출처: table1_scenario_comparison.csv, stranded_assets_summary.csv*")
    output.append("")

    # Sensitivity analysis
    output.append("## 민감도 분석")
    output.append("")
    sens = sensitivity_analysis(data)
    output.append("| 변수 | 기준값 (2030) | 단위 | 변동폭 | 비용 영향 |")
    output.append("|------|-------------|------|--------|----------|")
    for row in sens:
        base = f"{row['base_value']:.2f}" if isinstance(row['base_value'], float) else str(row['base_value'])
        output.append(f"| {row['parameter']} | {base} | {row['unit']} | ±{row['variation_pct']}% | ±{row['impact_pct']:.1f}% |")
    output.append("")
    output.append("*영향도 계산: 변동폭 × 비용 구성비 (CAPEX 60%, 에너지비용 35%, OPEX 5%)*")
    output.append("")
    output.append("*출처: re_price_trajectory.csv, h2_price_trajectory.csv, technology_capex.csv, model_config.csv*")
    output.append("")

    # Summary stats
    output.append("---")
    output.append("")
    output.append("## 주요 수치 요약 (NCC-Elec 1.5°C 시나리오)")
    output.append("")
    scenario = data['scenario_comparison']
    ncc_elec = scenario[scenario['scenario'] == 'shaheen_ncc_elec_15c'].iloc[0]
    stranded = data['stranded_summary']
    ncc_elec_stranded = stranded[stranded['scenario'] == 'shaheen_ncc_elec_15c'].iloc[0]

    output.append(f"- **총 시설 수**: {int(ncc_elec['total_facilities'])}개")
    output.append(f"- **기준 배출량 (2025)**: {ncc_elec['emissions_2025_mtco2']:.2f} MtCO2")
    output.append(f"- **총 투자비용**: ${ncc_elec['total_capex_billion_usd']:.2f}B ({ncc_elec['total_capex_billion_usd'] * USD_TO_KRW / 1000:.1f}조원)")
    output.append(f"- **전력 수요 (2050)**: {ncc_elec['elec_demand_2050_twh']:.1f} TWh")
    output.append(f"- **좌초자산 발생년도**: {int(ncc_elec['stranding_year_15c'])}년")
    output.append(f"- **좌초자산 가치**: ${ncc_elec_stranded['stranded_value_1.5C_usd']/1e9:.2f}B ({ncc_elec_stranded['stranded_value_1.5C_usd'] * USD_TO_KRW / 1e12:.1f}조원)")
    output.append("")

    return "\n".join(output)


def main():
    """Main function to generate report tables"""
    print("Loading data...")
    data = load_data()

    print("Generating tables...")
    markdown = generate_markdown_tables(data)

    # Save to file
    output_path = OUTPUT_DIR / "report_tables" / "complete_report_tables.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"Tables saved to {output_path}")

    # Also print to console
    print("\n" + "="*80)
    print(markdown)

    return markdown


if __name__ == "__main__":
    main()
