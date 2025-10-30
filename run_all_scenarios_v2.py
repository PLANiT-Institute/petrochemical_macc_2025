"""
3개 생산량 시나리오 실행 스크립트 (v2)
Run all 3 production scenarios by directly importing modules
"""

import pandas as pd
import shutil
from pathlib import Path
import sys

# Add modules to path
sys.path.insert(0, str(Path.cwd()))

from modules.baseline import BaselineAnalyzer
from modules.macc import MACCAnalyzer
from modules.optimization_v2 import CostOptimizerV2

print("="*80)
print("한국 석유화학 MACC 모델 - 3개 시나리오 실행")
print("="*80)
print()

# Load scenario data
df_scenarios = pd.read_csv('data/demand_growth_trajectory_scenarios.csv')

# Define scenarios
scenarios = {
    'shaheen': {
        'name': 'Shaheen (성장)',
        'column': 'scenario_shaheen',
        'output_suffix': 'shaheen',
        'description': 'S-Oil Shaheen project (+1.8Mt, 2026), then fixed'
    },
    'restructure_25pct': {
        'name': '구조조정 25%',
        'column': 'scenario_restructure_25pct',
        'output_suffix': 'restructure_25pct',
        'description': '2026: -3.7Mt (25% reduction), then fixed'
    },
    'restructure_40pct': {
        'name': '구조조정 40%',
        'column': 'scenario_restructure_40pct',
        'output_suffix': 'restructure_40pct',
        'description': '2040: Gradual 40% reduction'
    }
}

# Backup original demand growth file
original_file = Path('data/demand_growth_trajectory.csv')
backup_file = Path('data/demand_growth_trajectory_original_backup.csv')

if original_file.exists():
    shutil.copy(original_file, backup_file)
    print(f"✓ 원본 백업: {backup_file}")
    print()

# Run each scenario
results_summary = []

for scenario_key, scenario_info in scenarios.items():
    print("="*80)
    print(f"시나리오 실행: {scenario_info['name']}")
    print(f"설명: {scenario_info['description']}")
    print("="*80)
    print()

    # Create scenario-specific demand growth file
    df_scenario = df_scenarios[['year', scenario_info['column']]].copy()
    df_scenario.columns = ['year', 'cumulative_capacity_multiplier']
    df_scenario.to_csv('data/demand_growth_trajectory.csv', index=False)

    print(f"✓ 수요 성장 파일 업데이트: {scenario_info['column']}")
    print(f"  2025: {df_scenario[df_scenario['year']==2025]['cumulative_capacity_multiplier'].iloc[0]:.3f}")
    print(f"  2030: {df_scenario[df_scenario['year']==2030]['cumulative_capacity_multiplier'].iloc[0]:.3f}")
    print(f"  2050: {df_scenario[df_scenario['year']==2050]['cumulative_capacity_multiplier'].iloc[0]:.3f}")
    print()

    # Create scenario-specific output directories
    output_base = Path('outputs') / f'scenarios_{scenario_info["output_suffix"]}'
    output_dirs = {
        'baseline': output_base / 'module_01_baseline',
        'macc': output_base / 'module_02_macc',
        'optimization': output_base / 'module_03_optimization'
    }

    for output_dir in output_dirs.values():
        output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Module 1: Baseline
        print(">>> Module 1: Baseline Emissions & BAU Trajectory")
        baseline_engine = BaselineAnalyzer(
            data_dir='data',
            output_dir=str(output_dirs['baseline'])
        )
        baseline_engine.run_complete_analysis()
        print("   ✓ Module 1 완료")
        print()

        # Module 2: MACC
        print(">>> Module 2: MACC Calculation")
        macc_engine = MACCAnalyzer(
            baseline_output=str(output_dirs['baseline']),
            data_dir='data',
            output_dir=str(output_dirs['macc'])
        )
        macc_engine.run_complete_analysis()
        print("   ✓ Module 2 완료")
        print()

        # Module 3: Optimization
        print(">>> Module 3: Cost Optimization")
        opt_engine = CostOptimizerV2(
            baseline_output=str(output_dirs['baseline']),
            macc_output=str(output_dirs['macc']),
            output_dir=str(output_dirs['optimization'])
        )
        opt_engine.run_complete_analysis()
        print("   ✓ Module 3 완료")
        print()

        # Extract key results
        df_deployment = pd.read_csv(output_dirs['optimization'] / 'policy_target_deployment.csv')
        df_2050 = df_deployment[df_deployment['year'] == 2050].iloc[0]

        results_summary.append({
            'scenario': scenario_info['name'],
            'scenario_key': scenario_key,
            'bau_emissions_2050_mt': df_2050['bau_mt'],
            'emissions_2050_mt': df_2050['actual_emissions_mt'],
            'cost_2050_billion_usd': df_2050['cumulative_capex_musd'] / 1000,
            'ncc_h2_mt': df_2050['ncc_h2_mt'],
            'ncc_elec_mt': df_2050['ncc_elec_mt'],
            're_ppa_mt': df_2050['re_ppa_mt'],
            'heat_pump_mt': df_2050['heat_pump_mt'],
            'h2_consumption_kt': df_2050['h2_consumption_kt'],
            'electricity_increase_twh': df_2050['electricity_consumption_increase_twh']
        })

        print(f"✓ {scenario_info['name']} 시나리오 완료")
        print(f"  2050 BAU 배출량: {df_2050['bau_mt']:.2f} MtCO2")
        print(f"  2050 실제 배출량: {df_2050['actual_emissions_mt']:.2f} MtCO2")
        print(f"  누적 CAPEX: ${df_2050['cumulative_capex_musd']/1000:.1f} billion USD")
        print()

    except Exception as e:
        print(f"   ✗ {scenario_info['name']} 실행 중 오류:")
        print(f"      {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        continue

# Restore original file
if backup_file.exists():
    shutil.copy(backup_file, original_file)
    print(f"✓ 원본 수요 성장 파일 복원")
    print()

# Create comparison summary
if results_summary:
    print("="*80)
    print("시나리오 비교 요약")
    print("="*80)
    print()

    df_summary = pd.DataFrame(results_summary)

    # Save summary
    summary_path = Path('outputs/scenarios_comparison/summary.csv')
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    df_summary.to_csv(summary_path, index=False)

    print("2050년 시나리오 비교:")
    print()
    print(f"{'Scenario':<20s} {'Emissions (Mt)':>15s} {'Cost (B$)':>12s} {'NCC-H2':>10s} {'NCC-Elec':>10s} {'RE PPA':>10s} {'Heat Pump':>12s}")
    print("-" * 100)

    for idx, row in df_summary.iterrows():
        print(f"{row['scenario']:<20s} {row['emissions_2050_mt']:>15.2f} {row['cost_2050_billion_usd']:>12.1f} {row['ncc_h2_mt']:>10.2f} {row['ncc_elec_mt']:>10.2f} {row['re_ppa_mt']:>10.2f} {row['heat_pump_mt']:>12.2f}")

    print()
    print(f"✓ 저장: {summary_path}")
    print()

print("="*80)
print("모든 시나리오 실행 완료")
print("="*80)
print()
print("생성된 결과:")
for scenario_key, scenario_info in scenarios.items():
    output_base = Path('outputs') / f'scenarios_{scenario_info["output_suffix"]}'
    print(f"  - {scenario_info['name']}: {output_base}/")
print()
print("다음 단계:")
print("  1. Streamlit 대시보드 업데이트")
print("  2. 한국어 Word 보고서 생성")
print()
