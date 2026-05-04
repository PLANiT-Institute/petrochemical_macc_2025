# Korea Petrochemical MACC Model

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Marginal Abatement Cost Curve (MACC) model for Korea's petrochemical industry decarbonization (2025-2050).

## Overview

This model analyzes facility-level decarbonization pathways for Korea's petrochemical sector using:
- **Science-based carbon budgets** (1.5°C and 2.0°C pathways)
- **Technology cost optimization** (LCOA-based deployment)
- **Stranded asset analysis** from carbon budget perspective

### Key Results (v0.5)

| Metric | Value |
|--------|-------|
| Total Facilities | 243 (with Shaheen project) |
| Baseline Emissions (2025) | 59.2 MtCO2/year |
| Carbon Pathways | 1.5°C and 2.0°C |
| Technologies | NCC-H2, NCC-Electricity, RDH, Heat Pump |
| Target | Net Zero by 2050 |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run scenario analysis
python3 run_scenarios.py

# 3. Generate outputs (figures, CSVs, reports)
python3 generate_outputs.py

# 4. Launch interactive dashboard
streamlit run streamlit_app.py
```

## Project Structure

```
petrochemical_macc_2025/
├── data/
│   ├── assets/                    # Facility databases
│   ├── assumptions/               # Technology & price parameters
│   │   ├── kor_petro_spline_comparison.csv  # Carbon budget pathways
│   │   └── technology_capex.csv   # Technology costs
│   └── scenarios/                 # Scenario definitions
│
├── modules/                       # Core calculation modules
│   ├── data_loader.py             # Data loading & validation
│   ├── capex_calculator.py        # CAPEX & MAC calculations
│   └── utils.py                   # Utility functions
│
├── outputs/                       # Generated results
│   ├── scenario_results.csv       # Main combined results
│   ├── figures/                   # Visualizations
│   ├── professional/              # Stakeholder reports
│   └── report_tables/             # Detailed tables
│
├── docs/                          # Documentation
│   ├── ASSUMPTIONS_AND_METHODOLOGY.md
│   ├── DATA_SOURCES.md
│   └── MODEL_FLOW.md
│
├── run_scenarios.py               # Main scenario runner
├── generate_outputs.py            # Output generator (figures + CSVs)
└── streamlit_app.py               # Interactive dashboard
```

## Scenarios

The model runs 4 scenarios combining technology options with carbon pathways:

| Scenario | NCC Technology | Carbon Pathway |
|----------|----------------|----------------|
| shaheen_ncc_h2_15c | NCC-H2 (Hydrogen) | 1.5°C |
| shaheen_ncc_h2_20c | NCC-H2 (Hydrogen) | 2.0°C |
| shaheen_ncc_elec_15c | NCC-Electricity | 1.5°C |
| shaheen_ncc_elec_20c | NCC-Electricity | 2.0°C |

### Carbon Budget Pathways

Based on science-aligned emission reduction pathways:

| Year | 1.5°C Pathway | 2.0°C Pathway |
|------|---------------|---------------|
| 2025 | 100.0% | 100.0% |
| 2030 | 81.8% | 156.3% (overshoot) |
| 2040 | 40.9% | 78.2% |
| 2050 | 0.0% | 0.0% |

The 2.0°C pathway allows temporary overshoot (emissions above 2025 baseline) in early years.

## How It Works

1. **Data Input**: Load facility database, technology parameters, price trajectories
2. **Baseline Calculation**: Calculate emissions for each facility based on energy intensity
3. **Technology Selection**: Select optimal technology based on Levelized Cost of Abatement (LCOA)
4. **Gap Analysis**: Compare current emissions to carbon budget target each year
5. **Cost Optimization**: Deploy technologies to meet targets at minimum cost
6. **Stranded Assets**: Calculate asset stranding when carbon budget is exhausted

## Data Files

### Key Input Files

| File | Description |
|------|-------------|
| `facility_database_with_shaheen.csv` | 243 facilities with capacity and location |
| `technology_parameters.csv` | Technology efficiency and availability |
| `technology_capex.csv` | Technology costs ($/t-product/yr) |
| `kor_petro_spline_comparison.csv` | Carbon budget pathways (1.5°C, 2.0°C) |
| `scenario_definitions.csv` | Scenario configurations |

### Output Files

| File | Description |
|------|-------------|
| `scenario_results.csv` | Facility-level annual results (all scenarios) |
| `stranded_assets_summary.csv` | Stranded asset analysis by scenario |
| `regional_mac_summary.csv` | Regional MAC curves |

## Running the Model

### Basic Usage

```bash
# Run all scenarios
python3 run_scenarios.py

# Generate all outputs
python3 generate_outputs.py

# Generate only figures
python3 generate_outputs.py --figures

# Generate only CSVs
python3 generate_outputs.py --csv
```

### Dashboard

```bash
streamlit run streamlit_app.py
```

The dashboard provides:
- Emission pathway visualizations
- Technology deployment timelines
- Regional analysis
- MACC curves
- Stranded asset analysis

## Key Assumptions

| Parameter | 2025 | 2050 | Unit |
|-----------|------|------|------|
| RE Electricity | 65 | 30 | $/MWh |
| Green H2 Price | 4.58 | 2.01 | $/kg |
| Grid Emission Factor | 0.436 | 0.000 | tCO2/MWh |
| Discount Rate | 8% | 8% | - |

See `docs/ASSUMPTIONS_AND_METHODOLOGY.md` for complete methodology.

## Technologies

| Technology | Application | Available | CAPEX 2025 |
|------------|-------------|-----------|------------|
| Heat Pump | Low-temp heat (<165°C) | 2025 | $100/t-product |
| NCC-H2 | Naphtha cracker furnaces | 2030 | $350/t-ethylene |
| NCC-Electricity | Electric crackers | 2030 | $280/t-ethylene |
| RDH | High-temp BTX | 2026 | $200/t-BTX |
| RE-PPA | Grid electricity | 2025 | - |

## License

MIT License - See [LICENSE](LICENSE)

## Authors

PLANiT, Seoul, South Korea

## Version History

- **v0.5** (January 2026): Integrated science-based carbon budget pathways (1.5°C/2.0°C)
- **v0.4** (January 2026): Consolidated output generation, improved stranded asset analysis
- **v1.2** (December 2024): Fixed restructure scenario bug
- **v1.0** (December 2024): Initial release with 6 scenarios
