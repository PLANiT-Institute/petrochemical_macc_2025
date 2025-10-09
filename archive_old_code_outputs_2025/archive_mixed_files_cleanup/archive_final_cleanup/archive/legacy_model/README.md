# Legacy MACC Model Archive

This directory contains the original MACC optimization model implementation.

## Files:
- `solver.py`: Main CLI interface for legacy model
- `model_pyomo.py`: Pyomo optimization model builder
- `data_io.py`: Excel data loading and processing utilities

## Key Logic Preserved:
- Technology deployment optimization with ramp constraints
- Stock accounting over technology lifetime
- Emissions target constraints with optional slack
- NPV cost minimization objective
- Mutual exclusivity and coupling constraints

## Usage Pattern:
```python
from data_io import read_excel, baseline_total_mt, targets_map, build_timeseries, parse_links
from model_pyomo import build_model, solve_model

# Load data
sheets = read_excel(excel_file)
baseline_mt = baseline_total_mt(sheets)
years_all, tmap = targets_map(sheets, None)
tech_ids, params = build_timeseries(sheets, years, ramp_default=0.2)
groups, depends = parse_links(sheets)

# Build and solve model
m = build_model(years, baseline_mt, tmap, tech_ids, params, groups, depends)
solver_used, results = solve_model(m, solver="auto")
```

Archived on: 2025-09-18