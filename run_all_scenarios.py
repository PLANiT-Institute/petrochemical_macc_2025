"""
3개 생산량 시나리오 실행 스크립트
Run all 3 production scenarios: Shaheen, Restructure 25%, Restructure 40%
"""

import pandas as pd
import shutil
from pathlib import Path
import subprocess
import sys

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
backup_file = Path('data/demand_growth_trajectory_original.csv')

if original_file.exists() and not backup_file.exists():
    shutil.copy(original_file, backup_file)
    print(f"✓ 원본 백업: {backup_file}")
    print()

# Run each scenario
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
    print()

    # Create scenario-specific output directories
    output_dirs = {
        'baseline': f'outputs/module_01_{scenario_info["output_suffix"]}',
        'macc': f'outputs/module_02_{scenario_info["output_suffix"]}',
        'optimization': f'outputs/module_03_{scenario_info["output_suffix"]}'
    }

    for output_dir in output_dirs.values():
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Module 1: Baseline
    print(">>> Module 1: Baseline Emissions & BAU Trajectory")
    try:
        # We'll use subprocess to ensure clean execution
        result = subprocess.run(
            [sys.executable, 'modules/baseline.py',
             '--output-dir', output_dirs['baseline']],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print("   ✓ Module 1 완료")
        else:
            print(f"   ⚠️ Module 1 경고: {result.stderr[:200]}")
    except Exception as e:
        print(f"   ⚠️ Module 1 실행 중 오류: {str(e)[:200]}")
    print()

    # Module 2: MACC
    print(">>> Module 2: MACC Calculation")
    try:
        result = subprocess.run(
            [sys.executable, 'modules/macc.py',
             '--baseline-dir', output_dirs['baseline'],
             '--output-dir', output_dirs['macc']],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print("   ✓ Module 2 완료")
        else:
            print(f"   ⚠️ Module 2 경고: {result.stderr[:200]}")
    except Exception as e:
        print(f"   ⚠️ Module 2 실행 중 오류: {str(e)[:200]}")
    print()

    # Module 3: Optimization
    print(">>> Module 3: Cost Optimization")
    try:
        result = subprocess.run(
            [sys.executable, 'modules/optimization_v2.py',
             '--baseline-dir', output_dirs['baseline'],
             '--macc-dir', output_dirs['macc'],
             '--output-dir', output_dirs['optimization']],
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.returncode == 0:
            print("   ✓ Module 3 완료")
        else:
            print(f"   ⚠️ Module 3 경고: {result.stderr[:200]}")
    except Exception as e:
        print(f"   ⚠️ Module 3 실행 중 오류: {str(e)[:200]}")
    print()

    print(f"✓ {scenario_info['name']} 시나리오 완료")
    print()

# Restore original file (use baseline scenario as default)
if backup_file.exists():
    # Use baseline (현재 모델) as default
    df_baseline = df_scenarios[['year', 'scenario_baseline']].copy()
    df_baseline.columns = ['year', 'cumulative_capacity_multiplier']
    df_baseline.to_csv('data/demand_growth_trajectory.csv', index=False)
    print(f"✓ 기본 수요 성장 파일 복원 (Baseline)")
    print()

# Create comparison summary
print("="*80)
print("시나리오 비교 요약 생성")
print("="*80)
print()

summary_data = []

for scenario_key, scenario_info in scenarios.items():
    output_dir = f'outputs/module_03_{scenario_info["output_suffix"]}'

    # Load policy target deployment
    try:
        df_deployment = pd.read_csv(f'{output_dir}/policy_target_deployment.csv')
        df_2050 = df_deployment[df_deployment['year'] == 2050].iloc[0]

        summary_data.append({
            'Scenario': scenario_info['name'],
            'Total_Emissions_2050_Mt': df_2050['total_emissions_mt'],
            'Total_Cost_Billion_USD': df_2050['cumulative_cost_musd'] / 1000,
            'NCC_H2_Deployed_Mt': df_2050.get('tech_ncc_h2_mt', 0),
            'NCC_Elec_Deployed_Mt': df_2050.get('tech_ncc_electricity_mt', 0),
            'RE_PPA_Deployed_Mt': df_2050.get('tech_re_ppa_mt', 0),
            'Heat_Pump_Deployed_Mt': df_2050.get('tech_heat_pump_mt', 0)
        })
    except Exception as e:
        print(f"   ⚠️ {scenario_info['name']} 결과 로드 실패: {str(e)[:100]}")

if summary_data:
    df_summary = pd.DataFrame(summary_data)

    # Save summary
    summary_path = Path('outputs/scenarios/all_scenarios_summary.csv')
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    df_summary.to_csv(summary_path, index=False)

    print("2050년 시나리오 비교:")
    print()
    print(df_summary.to_string(index=False))
    print()
    print(f"✓ 저장: {summary_path}")
    print()

print("="*80)
print("모든 시나리오 실행 완료")
print("="*80)
print()
print("생성된 결과:")
for scenario_key, scenario_info in scenarios.items():
    print(f"  - {scenario_info['name']}: outputs/module_03_{scenario_info['output_suffix']}/")
print()
print("다음 단계:")
print("  1. Streamlit 대시보드 업데이트")
print("  2. 한국어 Word 보고서 생성")
print()
