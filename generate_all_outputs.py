#!/usr/bin/env python3
"""
Master output generation pipeline.

Runs all model scripts in dependency order (tier 0 → 1 → 2 → 3),
reporting success/failure for each step.

Usage:
    python generate_all_outputs.py                    # Full run
    python generate_all_outputs.py --skip-scenarios    # Skip run_scenarios.py
    python generate_all_outputs.py --scenarios NAME    # Pass specific scenarios to run_scenarios.py
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

# (tier, script_path_relative_to_project, description, required)
PIPELINE = [
    (-1, "scripts/calculate_hydrogen_price.py",          "Calculate hydrogen price (LCOH)", True),
    (0, "run_scenarios.py",                              "Run scenario simulations",       True),
    (0, "scripts/analysis_energy_emission.py",           "Baseline energy/emission analysis", True),
    (0, "scripts/generate_price_scenario_figure.py",     "Price scenario figure",          True),
    (1, "scripts/generate_professional_outputs.py",      "Professional CSV outputs",       True),
    (1, "scripts/generate_ncc_stranded_asset_report.py", "NCC stranded asset report",      True),
    (1, "scripts/generate_macc_visualizations.py",       "MACC visualizations",            True),
    (1, "scripts/generate_emission_pathways.py",         "Emission pathway analysis",      True),
    (1, "scripts/generate_outputs.py",                   "General outputs",                True),
    (2, "scripts/generate_professional_figures.py",      "Professional figures",           True),
    (2, "scripts/generate_report_data.py",               "Report data & figures",          True),
    (2, "scripts/create_stranded_asset_visualizations.py", "Stranded asset visualizations", True),
    (3, "scripts/generate_report_tables.py",             "Report tables (Markdown)",       False),
]

PROJECT_ROOT = Path(__file__).resolve().parent


def run_script(script_rel: str, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    script_path = PROJECT_ROOT / script_rel
    cmd = [sys.executable, str(script_path)]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(cmd, cwd=str(PROJECT_ROOT))


def main():
    parser = argparse.ArgumentParser(
        description="Master pipeline: regenerate all model outputs in dependency order."
    )
    parser.add_argument(
        "--skip-scenarios",
        action="store_true",
        help="Skip run_scenarios.py (use existing scenario_results.csv)",
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        metavar="NAME",
        help="Scenario names to pass through to run_scenarios.py",
    )
    args = parser.parse_args()

    # Group steps by tier
    tiers: dict[int, list] = {}
    for tier, script, desc, required in PIPELINE:
        tiers.setdefault(tier, []).append((script, desc, required))

    results: list[tuple[str, str, bool]] = []  # (script, description, success)
    overall_start = time.time()

    for tier_num in sorted(tiers):
        print(f"\n{'='*60}")
        print(f"  TIER {tier_num}")
        print(f"{'='*60}")

        for script, desc, required in tiers[tier_num]:
            # Handle --skip-scenarios
            if script == "run_scenarios.py" and args.skip_scenarios:
                print(f"\n  [SKIP] {desc}  ({script})")
                results.append((script, desc, True))
                continue

            # Build extra args for run_scenarios
            extra_args = None
            if script == "run_scenarios.py" and args.scenarios:
                extra_args = ["--scenarios"] + args.scenarios

            label = "required" if required else "optional"
            print(f"\n  [{label.upper()}] {desc}  ({script})")
            print(f"  {'-'*50}")

            step_start = time.time()
            try:
                result = run_script(script, extra_args)
                success = result.returncode == 0
            except Exception as exc:
                print(f"  ERROR: {exc}")
                success = False

            elapsed = time.time() - step_start
            status = "OK" if success else "FAIL"
            print(f"  -> {status}  ({elapsed:.1f}s)")
            results.append((script, desc, success))

    # Final summary
    total_elapsed = time.time() - overall_start
    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")

    failed = []
    for script, desc, success in results:
        icon = "+" if success else "X"
        print(f"  [{icon}] {desc}")
        if not success:
            failed.append(desc)

    print(f"\n  Total time: {total_elapsed:.1f}s")
    if failed:
        print(f"\n  FAILED ({len(failed)}):")
        for f in failed:
            print(f"    - {f}")
        sys.exit(1)
    else:
        print("\n  All steps completed successfully.")


if __name__ == "__main__":
    main()
