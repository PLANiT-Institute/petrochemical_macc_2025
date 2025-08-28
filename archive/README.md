# Archive Directory

This directory contains archived files from the Korean Petrochemical MACC model development process.

## Directory Structure

### `development_scripts/`
Contains development and debugging scripts used during model calibration:
- **Emission calculation fixes**: `fix_emission_calculation.py`, `add_process_emissions.py`
- **Baseline calibration**: `calibrate_baseline_consumption.py`, `update_emission_factors.py`
- **Target alignment**: `fix_emission_targets.py`, `fix_targets_corrected.py`
- **Alternative technology fixes**: `fix_alternative_technologies.py`
- **Old model versions**: `run_optimization_model*.py`, `baseline_comprehensive_analysis.py`
- **Debug scripts**: `debug_optimization_*.py`, `test_optimization_debug.py`

### `backup_data/`
Contains backup versions of the Excel database created during development:
- `Korea_Petrochemical_MACC_Database_BACKUP.xlsx`
- `Korea_Petrochemical_MACC_Database_BACKUP_ALT_TECH.xlsx`
- `Korea_Petrochemical_MACC_Database_BACKUP_CONSUMPTION.xlsx`
- `Korea_Petrochemical_MACC_Database_BACKUP_TARGETS.xlsx`

### `old_outputs/`
Contains log files and documentation from development process:
- `baseline_analysis.log`
- `baseline_output.log`
- `model_logic_review.md`
- `output.log`

## Active Files (Not Archived)

The following files remain active in the main directory:
- `run_baseline_quick.py` - Current baseline analysis
- `run_optimization_simple.py` - Current optimization model
- `data/Korea_Petrochemical_MACC_Database.xlsx` - Active database
- `baseline/` - Current baseline analysis results
- `outputs/` - Current model outputs

## Development History

The archived files document the model evolution from:
1. **Initial structure** - Technology band-based approach
2. **Data alignment issues** - Capacity mismatches, emission intensity problems
3. **Model restructuring** - Facility-based approach with specific Korean companies
4. **Emission calculation fixes** - Corrected from 853 tCO2/t to realistic 2.8 tCO2/t
5. **Final calibration** - Korean grid reality and process emissions

The current model achieves:
- ✅ Realistic emission intensity (2.8 tCO2/t, within 2.5-4.0 benchmark)
- ✅ 2030 Korean NDC target achievement (15% reduction)
- ✅ Facility-based structure with 8 Korean petrochemical companies