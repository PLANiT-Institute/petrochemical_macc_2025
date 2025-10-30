"""
Generate summary comparison from completed scenario runs
"""

import pandas as pd
from pathlib import Path

print("="*80)
print("시나리오 비교 요약 생성")
print("="*80)
print()

# Define scenarios
scenarios = {
    'shaheen': {
        'name': 'Shaheen (성장)',
        'output_suffix': 'shaheen',
    },
    'restructure_25pct': {
        'name': '구조조정 25%',
        'output_suffix': 'restructure_25pct',
    },
    'restructure_40pct': {
        'name': '구조조정 40%',
        'output_suffix': 'restructure_40pct',
    }
}

# Collect results
results_summary = []

for scenario_key, scenario_info in scenarios.items():
    output_base = Path('outputs') / f'scenarios_{scenario_info["output_suffix"]}'
    deployment_file = output_base / 'module_03_optimization' / 'policy_target_deployment.csv'

    if deployment_file.exists():
        df_deployment = pd.read_csv(deployment_file)
        df_2050 = df_deployment[df_deployment['year'] == 2050].iloc[0]

        results_summary.append({
            'scenario': scenario_info['name'],
            'scenario_key': scenario_key,
            'bau_emissions_2050_mt': df_2050['bau_mt'],
            'emissions_2050_mt': df_2050['actual_emissions_mt'],
            'abatement_2050_mt': df_2050['bau_mt'] - df_2050['actual_emissions_mt'],
            'cost_2050_billion_usd': df_2050['cumulative_capex_musd'] / 1000,
            'ncc_h2_mt': df_2050['ncc_h2_mt'],
            'ncc_elec_mt': df_2050['ncc_elec_mt'],
            're_ppa_mt': df_2050['re_ppa_mt'],
            'heat_pump_mt': df_2050['heat_pump_mt'],
            'h2_consumption_kt': df_2050['h2_consumption_kt'],
            'electricity_increase_twh': df_2050['electricity_consumption_increase_twh']
        })

        print(f"✓ {scenario_info['name']}:")
        print(f"  2050 BAU 배출량: {df_2050['bau_mt']:.2f} MtCO2")
        print(f"  2050 실제 배출량: {df_2050['actual_emissions_mt']:.2f} MtCO2")
        print(f"  2050 감축량: {df_2050['bau_mt'] - df_2050['actual_emissions_mt']:.2f} MtCO2")
        print(f"  누적 CAPEX: ${df_2050['cumulative_capex_musd']/1000:.1f} billion USD")
        print()
    else:
        print(f"✗ {scenario_info['name']}: 결과 파일 없음")
        print()

if results_summary:
    print("="*80)
    print("2050년 시나리오 비교")
    print("="*80)
    print()

    df_summary = pd.DataFrame(results_summary)

    # Save summary
    summary_path = Path('outputs/scenarios_comparison/summary.csv')
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    df_summary.to_csv(summary_path, index=False)

    print("시나리오별 2050년 결과:")
    print()
    print(f"{'Scenario':<20s} {'BAU (Mt)':>12s} {'Actual (Mt)':>12s} {'Abatement':>12s} {'CAPEX (B$)':>12s} {'NCC-H2':>10s} {'NCC-Elec':>10s}")
    print("-" * 100)

    for idx, row in df_summary.iterrows():
        print(f"{row['scenario']:<20s} {row['bau_emissions_2050_mt']:>12.2f} {row['emissions_2050_mt']:>12.2f} {row['abatement_2050_mt']:>12.2f} {row['cost_2050_billion_usd']:>12.1f} {row['ncc_h2_mt']:>10.2f} {row['ncc_elec_mt']:>10.2f}")

    print()
    print(f"✓ 저장: {summary_path}")
    print()

    # Additional details
    print("="*80)
    print("에너지 전환 상세 (2050)")
    print("="*80)
    print()
    print(f"{'Scenario':<20s} {'H2 수요 (kt)':>15s} {'전력 증가 (TWh)':>18s} {'RE PPA (Mt)':>15s} {'Heat Pump (Mt)':>16s}")
    print("-" * 100)

    for idx, row in df_summary.iterrows():
        print(f"{row['scenario']:<20s} {row['h2_consumption_kt']:>15.1f} {row['electricity_increase_twh']:>18.2f} {row['re_ppa_mt']:>15.2f} {row['heat_pump_mt']:>16.2f}")

    print()

print("="*80)
print("요약 생성 완료")
print("="*80)
