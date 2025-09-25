# Organized Korean Petrochemical MACC Analysis

## Project Structure

```
organized_analysis/
├── analysis_scripts/           # Core analysis modules
│   ├── basic_emission_analysis.py      # Emission calculation framework
│   ├── cost_optimization_model.py      # MACC cost optimization
│   ├── result_analysis.py              # Results interpretation
│   └── review_excel_data.py            # Excel data review utilities
├── data/                      # Input data files
│   └── Korean_Petrochemical_MACC_Model_Corrected_with_Naphtha.xlsx
├── outputs/                   # Generated results and visualizations
└── archive_old/              # Archived files from reorganization

## Quick Start

### 1. Basic Emission Analysis
```python
from analysis_scripts.basic_emission_analysis import EmissionAnalyzer

analyzer = EmissionAnalyzer('data/Korean_Petrochemical_MACC_Model_Corrected_with_Naphtha.xlsx')
baseline_results = analyzer.calculate_baseline_emissions()
analyzer.create_emission_visualization()
```

### 2. Cost Optimization
```python
from analysis_scripts.cost_optimization_model import MACCCostOptimizer

optimizer = MACCCostOptimizer('data/Korean_Petrochemical_MACC_Model_Corrected_with_Naphtha.xlsx')
scenario_results = optimizer.optimize_multiple_scenarios()
optimizer.visualize_macc_curve()
```

### 3. Result Analysis
```python
from analysis_scripts.result_analysis import MACCResultAnalyzer

analyzer = MACCResultAnalyzer('outputs/')
analyzer.run_comprehensive_analysis()
```

## Key Features

- **Internalized Naphtha Emissions**: Includes 0.90 tCO₂e/t external GHG factor
- **Three-Matrix Framework**: CI (consumption), CI2 (emission factors), MACC (technology costs)
- **Multi-Scenario Optimization**: 10%, 25%, 50%, 75%, 90% reduction targets
- **Comprehensive Visualization**: MACC curves, cost comparisons, technology rankings

## Data Model

The analysis is based on three key matrices in Excel:
1. **CI Matrix**: Fuel consumption intensities (GJ/t, kWh/t) for 55 products
2. **CI2 Matrix**: Emission factors (tCO₂/GJ, tCO₂/kWh) for all fuel types including naphtha
3. **MACC Matrix**: Technology costs and abatement potential for 23+ technologies

## Results

All results are exported to the `outputs/` directory including:
- CSV files with detailed calculations
- PNG visualizations
- JSON files with complete results
- Executive summary reports