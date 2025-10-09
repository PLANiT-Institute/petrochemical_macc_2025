# Archive Contents (October 2025)

This directory contains old code and outputs that are not related to the current project structure.

## Archived Items:

### 1. `petrochemical_cost_optimization_model/`
- Old version of the model with different structure
- Contains modules 01-04 in old format
- Multiple documentation files (MD files)
- Old output directories (step_01-04, integrated_outputs_v2)
- Legacy Python scripts (integrated_model_v2.py, module_XX_*.py)

### 2. `archive_mixed_files_cleanup/`
- Previously archived files from earlier cleanup
- Contains old visualizations and PNG files
- Legacy model scripts
- Old analysis outputs

### 3. `extract_data_from_excel.py`
- Standalone script for extracting data from Excel
- No longer needed as data is now in CSV format

### 4. `create_data_files.py`
- Script for creating data files
- Functionality now integrated into main modules

## Current Project Structure:

The current project now uses:
- `modules/` folder with clean class-based modules
- `run_module_XX.py` scripts at root level
- `data/` folder with CSV files
- `outputs/` folder for all results
- Core documentation files at root level

## Reason for Archiving:

These files were archived to clean up the project structure and focus on the production-ready v2.0 architecture with:
- All calculations in Python (no Excel dependencies)
- Clean modular design
- Real facility data from 60+ Korean companies
- Validated results matching ESG reports
