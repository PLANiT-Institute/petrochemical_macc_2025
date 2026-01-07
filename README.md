# Korea Petrochemical Net Zero Pathway Analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview

A comprehensive **facility-level analysis tool** for evaluating decarbonization pathways for Korea's petrochemical industry (2025-2050).

### Key Results
- **237 baseline facilities** analyzed across 4 major complexes (100,066 kt/year capacity)
- **243 total facilities** with Shaheen project (+6 from 2026)
- **Baseline emissions: 47.0 MtCO2/year** at 70% operating rate (67.1 MtCO2 at 100%)
- All scenarios achieve **Net Zero by 2050**
- Investment range: **$21.8B - $41.7B** depending on scenario
- **No CCS/CCUS** - focus on electrification and green hydrogen

## Key Features

- **Facility-level resolution**: 237 baseline + 6 Shaheen (243 total with Shaheen project) across Yeosu, Daesan, Ulsan, and Other regions
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
│   ├── energy_intensities.csv
│   ├── emission_factors.csv
│   ├── h2_price_trajectory.csv
│   ├── re_price_trajectory.csv
│   ├── grid_emission_trajectory.csv
│   ├── fuel_price_trajectory.csv
│   └── demand_growth_trajectory.csv
│
├── modules/                        # Core calculation modules
│   └── utils.py                    # Consolidated core logic (DataLoader, Calculators)
│
├── outputs/                        # Simulation results
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
├── run_scenarios.py               # Main scenario runner
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
python run_scenarios.py
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
| 1 | Shaheen + NCC-H2 | Growth (+6 facilities, 243 total from 2026) | Green H2 furnaces |
| 2 | Shaheen + NCC-Elec | Growth (+6 facilities, 243 total from 2026) | Electric crackers |
| 3 | Restructure 25% + NCC-H2 | -25% NCC capacity (237 baseline) | Green H2 furnaces |
| 4 | Restructure 25% + NCC-Elec | -25% NCC capacity (237 baseline) | Electric crackers |
| 5 | Restructure 40% + NCC-H2 | -40% NCC capacity (237 baseline) | Green H2 furnaces |
| 6 | Restructure 40% + NCC-Elec | -40% NCC capacity (237 baseline) | Electric crackers |

## Key Assumptions

| Parameter | 2025 | 2050 | Unit |
|-----------|------|------|------|
| RE Electricity | 65 | 30 | $/MWh |
| Green H2 Price* | 4.58 | 2.01 | $/kg |
| Grid EF | 0.436 | 0.000 | tCO2/MWh |
| Heat Pump COP | 4.0 | 4.0 | - |
| CAPEX Learning | - | -50% | % |

*H₂ price is calculated from RE price via LCOH formula (linked)

### H₂ Price - RE Price Linkage (LCOH)

Green hydrogen price is dynamically calculated from renewable electricity price:

```
LCOH = (Electrolyzer CAPEX × CRF + OPEX) / H2_Production + Electricity_Cost

Key parameters:
- Electrolyzer CAPEX: $1,000/kW (2025) → $500/kW (2050)
- Efficiency: 70% (2025) → 75% (2050)
- Capacity Factor: 90%
```

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

- **v1.2** (December 10, 2024): Fixed restructure scenario bug; Updated investment figures; Created unified facility_master.csv
- **v1.1** (December 10, 2024): Documentation synchronized with data files; Added LCOH formula; Corrected Grid EF (0.0 by 2050)
- **v1.0** (December 2024): Final release with 6 scenarios, regional analysis, and client reporting
