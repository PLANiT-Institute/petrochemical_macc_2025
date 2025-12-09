# Korea Petrochemical Net Zero Pathway Analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview

A comprehensive **facility-level analysis tool** for evaluating decarbonization pathways for Korea's petrochemical industry (2025-2050).

### Key Results
- **256 facilities** analyzed across 4 major complexes (104,762 kt/year capacity)
- All scenarios achieve **Net Zero by 2050**
- Investment range: **$13.4B - $22.1B** depending on scenario
- **No CCS/CCUS** - focus on electrification and green hydrogen

## Key Features

- **Facility-level resolution**: 256 petrochemical facilities across Yeosu, Daesan, Ulsan, and Other regions
- **6 scenarios**: 3 production pathways × 2 NCC technology options
- **Technology portfolio**: NCC-H₂, NCC-Electricity, Heat Pump, RE-PPA, RDH
- **Interactive dashboard**: Streamlit-based visualization
- **Client reports**: Automated Excel generation

## Repository Structure

```
petrochemical_macc_2025/
├── data/                           # Input data
│   ├── scenarios/                  # Scenario results (for Streamlit)
│   ├── facility_database_with_regions.csv
│   ├── technology_parameters.csv
│   ├── h2_price_trajectory.csv
│   ├── re_price_trajectory.csv
│   └── grid_emission_trajectory.csv
│
├── modules/                        # Core calculation modules
│   ├── baseline.py                 # Baseline emission calculations
│   ├── macc.py                     # MACC curve generation
│   ├── optimization_v2.py          # Scenario optimization
│   ├── data_manager.py             # Data loading utilities
│   └── utils.py                    # Helper functions
│
├── docs/                           # Documentation
│   ├── ASSUMPTIONS_AND_METHODOLOGY.md
│   ├── MODEL_DOCUMENTATION.md
│   └── paper.pdf
│
├── reports/                        # Client deliverables
│   └── Korea_Petrochemical_NetZero_Analysis_YYYYMMDD.xlsx
│
├── streamlit_app.py               # Interactive dashboard
├── run_all_scenarios_v3.py        # Main scenario runner
├── generate_client_excel.py       # Excel report generator
└── requirements.txt               # Dependencies
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Run Scenario Analysis
```bash
python run_all_scenarios_v3.py
```

### 2. Generate Excel Report
```bash
python generate_client_excel.py
```

### 3. Launch Dashboard
```bash
streamlit run streamlit_app.py
```

## Scenarios

| # | Scenario | Production Pathway | NCC Technology |
|---|----------|-------------------|----------------|
| 1 | Shaheen + NCC-H2 | Growth (+6 facilities) | Green H2 furnaces |
| 2 | Shaheen + NCC-Elec | Growth (+6 facilities) | Electric crackers |
| 3 | Restructure 25% + NCC-H2 | -25% NCC capacity | Green H2 furnaces |
| 4 | Restructure 25% + NCC-Elec | -25% NCC capacity | Electric crackers |
| 5 | Restructure 40% + NCC-H2 | -40% NCC capacity | Green H2 furnaces |
| 6 | Restructure 40% + NCC-Elec | -40% NCC capacity | Electric crackers |

## Key Assumptions

| Parameter | 2025 | 2050 | Unit |
|-----------|------|------|------|
| Green H2 Price | 4.58 | 2.01 | $/kg |
| RE Electricity | 65 | 30 | $/MWh |
| Grid EF | 0.436 | 0.000 | tCO2/MWh |
| Heat Pump COP | 4.0 | 4.0 | - |
| CAPEX Learning | - | -50% | % |

See `docs/ASSUMPTIONS_AND_METHODOLOGY.md` for complete details.

## Technologies

| Technology | Application | Available |
|------------|-------------|-----------|
| **Heat Pump** | Low-temp heat (<165°C) | 2025 |
| **NCC-H2** | Naphtha cracker furnaces | 2030 |
| **NCC-Electricity** | Electric crackers (eFurnace) | 2030 |
| **RE-PPA** | All grid electricity | 2025 |
| **RDH** | High-temp BTX (Coolbrook) | 2026 |

## Dashboard

The Streamlit dashboard provides:
- **Assumptions page**: Technology CAPEX, price trajectories, facility coverage
- **Regional Transitions**: Emission pathways and technology deployment by region
- **Energy Demand**: Electricity requirements by region and scenario

## License

MIT License - See [LICENSE](LICENSE)

## Contact

**PLANiT**
Seoul, South Korea

## Version History

- **v1.0** (December 2024): Final release with 6 scenarios, regional analysis, and client reporting
