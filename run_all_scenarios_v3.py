"""
6개 시나리오 실행 스크립트 (v3)
Run all 6 scenarios: 3 production levels × 2 technology pathways
- Production pathways: Shaheen, 구조조정 25%, 구조조정 40%
- Technology pathways: NCC-H2, NCC-Electricity
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
print("한국 석유화학 MACC 모델 - 6개 시나리오 실행")
print("3개 생산량 시나리오 × 2개 기술 경로")
print("="*80)
print()

# Load scenario data
df_scenarios = pd.read_csv('data/demand_growth_trajectory_scenarios.csv')

# Define production scenarios
production_scenarios = {
    'shaheen': {
        'name': 'Shaheen (성장)',
        'column': 'scenario_shaheen',
        'description': 'S-Oil Shaheen project (+1.8Mt, 2026), then fixed'
    },
    'restructure_25pct': {
        'name': '구조조정 25%',
        'column': 'scenario_restructure_25pct',
        'description': '2026: -3.7Mt (25% reduction), then fixed'
    },
    'restructure_40pct': {
        'name': '구조조정 40%',
        'column': 'scenario_restructure_40pct',
        'description': '2040: Gradual 40% reduction'
    }
}

# Define technology pathways
technology_pathways = {
    'ncc_h2': {
        'name': 'NCC-H2',
        'force_tech': 'NCC-H2',
        'description': 'Hydrogen-fueled cracker (0.2 ton H2/ton C2H4)'
    },
    'ncc_elec': {
        'name': 'NCC-Electricity',
        'force_tech': 'NCC-Electricity',
        'description': 'Electric cracker with renewable electricity (5.0 MWh/ton C2H4)'
    }
}

# Backup original demand growth file
original_file = Path('data/demand_growth_trajectory.csv')
backup_file = Path('data/demand_growth_trajectory_original_backup.csv')

if original_file.exists():
    shutil.copy(original_file, backup_file)
    print(f"✓ 원본 백업: {backup_file}")
    print()

# Run each scenario combination
results_summary = []

for prod_key, prod_info in production_scenarios.items():
    for tech_key, tech_info in technology_pathways.items():
        scenario_id = f"{prod_key}_{tech_key}"
        scenario_name = f"{prod_info['name']} + {tech_info['name']}"

        print("="*80)
        print(f"시나리오 실행: {scenario_name}")
        print(f"생산량: {prod_info['description']}")
        print(f"기술 경로: {tech_info['description']}")
        print("="*80)
        print()

        # Create scenario-specific demand growth file
        df_scenario = df_scenarios[['year', prod_info['column']]].copy()
        df_scenario.columns = ['year', 'cumulative_capacity_multiplier']
        df_scenario.to_csv('data/demand_growth_trajectory.csv', index=False)

        print(f"✓ 수요 성장 파일 업데이트: {prod_info['column']}")
        print(f"  2025: {df_scenario[df_scenario['year']==2025]['cumulative_capacity_multiplier'].iloc[0]:.3f}")
        print(f"  2030: {df_scenario[df_scenario['year']==2030]['cumulative_capacity_multiplier'].iloc[0]:.3f}")
        print(f"  2050: {df_scenario[df_scenario['year']==2050]['cumulative_capacity_multiplier'].iloc[0]:.3f}")
        print()

        # Create scenario-specific output directories
        output_base = Path('outputs') / f'scenarios_{scenario_id}'
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

            # Module 3: Optimization (with forced NCC technology)
            print(f">>> Module 3: Cost Optimization (Forcing {tech_info['name']})")
            opt_engine = CostOptimizerV2(
                baseline_output=str(output_dirs['baseline']),
                macc_output=str(output_dirs['macc']),
                output_dir=str(output_dirs['optimization']),
                force_ncc_technology=tech_info['force_tech']
            )
            opt_engine.run_complete_analysis()
            print("   ✓ Module 3 완료")
            print()

            # Extract key results
            df_deployment = pd.read_csv(output_dirs['optimization'] / 'policy_target_deployment.csv')
            df_2050 = df_deployment[df_deployment['year'] == 2050].iloc[0]

            results_summary.append({
                'scenario': scenario_name,
                'scenario_id': scenario_id,
                'production_pathway': prod_info['name'],
                'technology_pathway': tech_info['name'],
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

            print(f"✓ {scenario_name} 시나리오 완료")
            print(f"  2050 BAU 배출량: {df_2050['bau_mt']:.2f} MtCO2")
            print(f"  2050 실제 배출량: {df_2050['actual_emissions_mt']:.2f} MtCO2")
            print(f"  누적 CAPEX: ${df_2050['cumulative_capex_musd']/1000:.1f} billion USD")
            print(f"  NCC-H2: {df_2050['ncc_h2_mt']:.2f} Mt")
            print(f"  NCC-Electricity: {df_2050['ncc_elec_mt']:.2f} Mt")
            print()

        except Exception as e:
            print(f"   ✗ {scenario_name} 실행 중 오류:")
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
    print("시나리오 비교 요약 (6개 시나리오)")
    print("="*80)
    print()

    df_summary = pd.DataFrame(results_summary)

    # Save summary
    summary_path = Path('outputs/scenarios_comparison_6scenarios/summary.csv')
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    df_summary.to_csv(summary_path, index=False)

    print("2050년 시나리오 비교:")
    print()
    print(f"{'Scenario':<35s} {'Emissions':>10s} {'Cost (B$)':>10s} {'NCC-H2':>10s} {'NCC-Elec':>10s} {'RE PPA':>10s} {'Heat Pump':>12s}")
    print("-" * 110)

    for idx, row in df_summary.iterrows():
        print(f"{row['scenario']:<35s} {row['emissions_2050_mt']:>10.2f} {row['cost_2050_billion_usd']:>10.1f} {row['ncc_h2_mt']:>10.2f} {row['ncc_elec_mt']:>10.2f} {row['re_ppa_mt']:>10.2f} {row['heat_pump_mt']:>12.2f}")

    print()
    print(f"✓ 저장: {summary_path}")
    print()

print("="*80)
print("모든 시나리오 실행 완료 (6개)")
print("="*80)
print()
print("생성된 결과:")
for prod_key in production_scenarios.keys():
    for tech_key in technology_pathways.keys():
        scenario_id = f"{prod_key}_{tech_key}"
        output_base = Path('outputs') / f'scenarios_{scenario_id}'
        print(f"  - {scenario_id}: {output_base}/")
print()
print("다음 단계:")
print("  1. Streamlit 대시보드 업데이트")
print("  2. 한국어 Word 보고서 생성")
print()
