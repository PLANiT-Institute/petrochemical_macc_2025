# Archived Files - 20251029

These files were archived as part of model cleanup for academic publication.

## Archived Modules

- `optimization.py`: Old optimization (replaced by optimization_v2.py with mutual exclusivity fix)
- `financial.py`: Financial analysis module (not used in core model)
- `sensitivity.py`: Legacy sensitivity analysis
- `sensitivity_corrected.py`: Legacy sensitivity analysis
- `regional_energy_tracker.py`: Not used in current model
- `visualizations.py`: Not used in current model

## Archived Data Files

- `baseline_2025_detailed.csv`: Output file, not input data
- `baseline_process_emissions.csv`: Redundant or not used in current model
- `fuel_costs_baseline.csv`: Redundant or not used in current model
- `grid_price_trajectory.csv`: Redundant or not used in current model
- `ncc_lcoe_trajectory.csv`: Legacy LCOE approach (replaced by energy-based)
- `technology_energy_requirements.csv`: Redundant or not used in current model
- `facility_technology_applicability.csv`: Redundant or not used in current model
- `emission_scenarios_template.csv`: Template only
- `model_parameters.csv`: Redundant or not used in current model

## Core Files Retained

### Modules (6 files):
- baseline.py - Module 1: Baseline emission calculation
- macc.py - Module 2: MACC cost calculation
- optimization_v2.py - Module 3: Cost optimization (corrected version)
- utils.py - Shared utilities
- data_manager.py - Data loading and validation
- __init__.py - Package initialization

### Data Files (18 files):
- facility_database.csv - 248 facilities with capacities
- energy_intensities.csv - Energy consumption by product type
- emission_factors.csv - Emission factors (corrected)
- technology_parameters.csv - Technology costs and parameters
- h2_price_trajectory.csv - Hydrogen prices 2025-2050
- re_price_trajectory.csv - RE electricity prices 2025-2050
- fuel_price_trajectory.csv - Fossil fuel prices
- grid_emission_trajectory.csv - Grid decarbonization
- demand_growth_trajectory.csv - Capacity growth projections
- emission_scenarios_clean.csv - Policy scenarios
- heat_pump_applicability.csv - Heat pump applicability by product
- *_corrected.csv - Corrected versions (3 files)
- *_original_backup.csv - Original backups (3 files)

## Restoration

To restore archived files:
```bash
cp archive_unused_{timestamp}/modules/* modules/
cp archive_unused_{timestamp}/data/* data/
```
