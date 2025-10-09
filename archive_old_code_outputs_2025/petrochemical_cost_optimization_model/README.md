# Korean Petrochemical Industry Cost Optimization Model

## Project Overview

This model implements a comprehensive cost optimization framework for the Korean petrochemical industry's transition from 2025 to 2050, designed to minimize the total NPV cost under emission constraints while showing facility-level technology deployment strategies.

## Project Structure

```
petrochemical_cost_optimization_model/
├── README.md                           # This file
├── data_sources/                       # Source data files
│   ├── Korean_Petrochemical_MACC_Model_English.xlsx  # Main database
│   └── korean_petrochemical_macc_enhanced.xlsx       # Enhanced version
├── step_01_baseline_analysis/          # BAU emission analysis (2025-2050)
│   ├── baseline_analyzer.py           # BAU pathway generation
│   └── baseline_analysis_report.xlsx  # Output results
├── step_02_macc_analysis/             # MACC curve generation
│   ├── macc_generator.py              # Technology cost analysis
│   └── macc_analysis_report.xlsx      # MACC curves & costs
├── step_03_cost_optimization/          # Cost-effective pathways
│   ├── cost_optimizer.py              # Optimization engine
│   └── optimization_results.xlsx      # Deployment strategies
├── step_04_financial_analysis/         # Deep financial analysis
│   ├── financial_analyzer.py          # Comprehensive financial model
│   └── financial_analysis_report.xlsx # Financial metrics
├── documentation/                      # Project documentation
│   ├── data_dictionary.md             # Data structure explanation
│   ├── methodology.md                 # Model methodology
│   └── validation_report.md           # Results validation
└── outputs/                           # Final integrated results
    ├── integrated_results.xlsx        # All results combined
    └── executive_summary.pdf          # Summary report
```

## Data Sources

### Main Database: Korean_Petrochemical_MACC_Model_English.xlsx
- **248 facilities** across Korean petrochemical industry
- **Facility-level data**: capacity, operation year, process type, location
- **Energy intensities**: consumption by fuel type and product
- **Emission factors**: tCO₂ per energy unit by source
- **Technology options**: Alternative low-carbon technologies
- **Cost data**: CAPEX/OPEX for technology deployment

### Enhanced Database: korean_petrochemical_macc_enhanced.xlsx
- Additional scenario configurations
- Temporal projections and growth factors
- Technology maturity assessments

## Fundamental Guidance Requirements

This model must satisfy the following requirements:

### Baseline Emissions (Target: 52 MtCO₂)
- Base oil production: 89% of total GHG
- NCC cracking processes: 46% of total GHG
- Direct emissions: 64% | Indirect: 34%
- By-product gases/oils: 70% of direct emissions
- Total energy consumption: 67.7 million toe
- Naphtha: 82.9% of total energy

### Technology Specifications
- **Bio-naphtha**: 10% energy reduction
- **NCC H2**: Hydrogen for naphtha cracking
- **NCC Electricity**: Electrification of cracking
- **Heat-pump**: Industrial heat pumps
- **Renewable Energy**: Solar and wind integration

### Emission Targets
- 2030: 25% reduction
- 2040: 50% reduction
- 2050: 75% reduction

## Analysis Steps

### Step 1: Baseline Emission Analysis
Generate business-as-usual emission projections without carbon constraints
- 50-year facility lifecycle analysis
- Growth scenario modeling
- Company and process emission shares

### Step 2: MACC Analysis
Develop marginal abatement cost curves for 2030, 2040, 2050
- Technology cost evolution
- Fuel price projections
- Abatement potential quantification

### Step 3: Cost Optimization
Optimize technology deployment to minimize NPV cost under emission constraints
- Facility-level technology selection
- Deployment timing optimization
- Cost-effective pathway generation

### Step 4: Financial Analysis
Deep financial analysis of sector transformation
- Investment requirements and financing
- Cash flow analysis and NPV calculations
- Risk assessment and sensitivity analysis
- Company-specific financial impacts
- Government policy cost-benefit analysis

## Key Outputs

1. **BAU vs Target vs Optimized Pathways**: Comprehensive comparison
2. **Facility-level Technology Deployment**: Specific recommendations per facility
3. **Financial Analysis**: Investment requirements, financing strategies, returns
4. **Policy Recommendations**: Government support mechanisms and costs

## Usage

Each step is designed to be run independently with embedded analysis and reporting:

```bash
# Step 1: Generate baseline analysis
python step_01_baseline_analysis/baseline_analyzer.py

# Step 2: Generate MACC curves
python step_02_macc_analysis/macc_generator.py

# Step 3: Optimize deployment
python step_03_cost_optimization/cost_optimizer.py

# Step 4: Financial analysis
python step_04_financial_analysis/financial_analyzer.py
```

## Model Validation

Results are validated against:
- Korean industry emission statistics
- Technology cost benchmarks
- Energy consumption data
- Financial sector requirements