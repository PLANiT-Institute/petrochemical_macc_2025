# Input Data Usage Verification Table

## Summary

This document provides a reference table showing which input/assumption data files are used in the codebase. All 23 active data files in `/data/` are currently used. No orphaned files found.

---

## Data Usage Table

| File | Category | Used By | Status |
|------|----------|---------|--------|
| `facility_database_with_regions.csv` | Assets | DataLoader, run_scenarios, tests | ✅ Used |
| `facility_database_with_shaheen.csv` | Assets | DataLoader, professional_outputs | ✅ Used |
| `region_mapping.csv` | Assets | run_scenarios, DataLoader | ✅ Used |
| `carbon_budget_scenarios.csv` | Assumptions | DataLoader, run_scenarios | ✅ Used |
| `emission_factors.csv` | Assumptions | DataLoader, report_tables, emission_pathways | ✅ Used |
| `product_benchmarks.csv` | Assumptions | DataLoader, report_tables, tests | ✅ Used |
| `technology_parameters.csv` | Assumptions | DataLoader, capex_calculator, streamlit_app | ✅ Used |
| `technology_capex.csv` | Assumptions | DataLoader, capex_calculator, report_tables | ✅ Used |
| `asset_valuation_params.csv` | Assumptions | DataLoader, run_scenarios | ✅ Used |
| `stranded_asset_params.csv` | Assumptions | DataLoader, professional_outputs | ✅ Used |
| `kor_petro_spline_comparison.csv` | Assumptions | run_scenarios | ✅ Used |
| `model_config.csv` | Assumptions | DataLoader, capex_calculator, report_tables | ✅ Used |
| `heat_pump_applicability.csv` | Assumptions | DataLoader (optional) | ⚠️ Defined |
| `fuel_price_trajectory.csv` | Prices | DataLoader, run_scenarios, report_tables | ✅ Used |
| `grid_emission_trajectory.csv` | Prices | DataLoader, run_scenarios, streamlit_app | ✅ Used |
| `grid_price_trajectory.csv` | Prices | DataLoader, run_scenarios, report_tables | ✅ Used |
| `h2_price_trajectory.csv` | Prices | DataLoader, run_scenarios, streamlit_app | ✅ Used |
| `re_price_trajectory.csv` | Prices | DataLoader, run_scenarios, streamlit_app | ✅ Used |
| `demand_growth_trajectory_restructure_25pct.csv` | Scenarios | run_scenarios | ✅ Used |
| `demand_growth_trajectory_restructure_40pct.csv` | Scenarios | run_scenarios | ✅ Used |
| `demand_growth_trajectory_shaheen.csv` | Scenarios | run_scenarios | ✅ Used |
| `emission_targets.csv` | Scenarios | DataLoader (optional) | ⚠️ Defined |
| `scenario_definitions.csv` | Scenarios | run_scenarios | ✅ Used |

---

## Summary Statistics

| Category | Files | Status |
|----------|-------|--------|
| Assets | 3 | All Used |
| Assumptions | 10 | 9 Active, 1 Optional |
| Prices | 5 | All Used |
| Scenarios | 5 | 4 Active, 1 Optional |
| **Total** | **23** | **21 Active, 2 Optional** |

---

## Notes

- **✅ Used**: File is actively loaded and used in the model
- **⚠️ Defined**: File path is defined in DataLoader but may be optional or conditionally loaded

---

## Verification Commands

To verify data loading works:
```bash
python run_scenarios.py --help
```

To verify file references in codebase:
```bash
grep -r "filename.csv" --include="*.py" .
```
