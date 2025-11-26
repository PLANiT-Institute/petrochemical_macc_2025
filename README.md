# Facility-Level MACC Model for Petrochemical Decarbonization

[![DOI](https://img.shields.io/badge/DOI-Pending-orange)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview

This repository contains the **facility-level Marginal Abatement Cost Curve (MACC) model** developed for the research paper:

> **"Beyond Partial Equilibrium: Why Technology Costs and Energy System Constraints Diverge in Industrial Decarbonization Pathways"**
> *Jinsu Park*
> Published in *Carbon Neutrality* (Springer Nature), 2025

The model analyzes decarbonization pathways for South Korea's petrochemical sector (248 facilities, 66.2 MtCO₂/year) and quantifies the divergence between technology costs and energy system feasibility for hydrogen vs. electricity pathways.

## Key Features

- **Facility-level resolution**: 248 petrochemical facilities across 11 naphtha cracker complexes
- **Energy demand quantification**: Explicit calculation of electricity (TWh) and hydrogen (Mt) demands
- **Technology portfolio**: NCC-H₂, NCC-Electricity, RE PPA, High-Temperature Heat Pumps
- **Scenario analysis**: 6 scenarios combining 3 production pathways × 2 technology routes
- **Learning curve modeling**: CAPEX projections with 15-20% learning rates
- **Policy integration**: Alignment with Korea's Hydrogen Economy Roadmap and renewable energy targets

## Repository Structure

```
petrochemical_macc_2025/
├── data/                           # Input parameters
│   ├── technology_parameters.csv   # Technology CAPEX, OPEX, efficiency
│   ├── energy_prices.csv          # Electricity, H₂, fuel price trajectories
│   └── policy_targets.csv         # Korea energy policy targets
│
├── modules/                        # Core model modules
│   ├── macc.py                    # MACC calculation engine
│   ├── energy_demand.py           # Aggregate energy demand quantification
│   └── scenario_runner.py         # Scenario execution framework
│
├── outputs/                        # Model results
│   ├── figures/                   # Publication-quality figures
│   ├── tables/                    # CSV result tables
│   └── sensitivity/               # Sensitivity analysis results
│
├── run_all_scenarios_v3.py        # Main execution script
├── generate_professional_figures.py  # Figure generation
└── README.md                       # This file
```

## Installation

### Requirements

- Python 3.8+
- pandas >= 1.3.0
- numpy >= 1.21.0
- matplotlib >= 3.4.0
- seaborn >= 0.11.0

### Setup

```bash
# Clone repository
git clone https://github.com/[your-username]/petrochemical_macc_2025.git
cd petrochemical_macc_2025

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run Full Scenario Analysis

```bash
python run_all_scenarios_v3.py
```

This executes all 6 scenarios (Shaheen/25%/40% restructuring × H₂/Electricity) and generates:
- MACC curves (2025-2050)
- Energy demand trajectories
- Cost summaries
- Sensitivity analysis results

### Generate Figures

```bash
python generate_professional_figures.py
```

Produces publication-quality figures:
- Figure 1: Cumulative decarbonization costs
- Figure 3: MACC comparison (H₂ vs Electricity)
- Figure 4: Energy demand trajectories
- Figure 5: Feasibility assessment
- Figure 7: Baseline emissions structure

### Key Parameters

Edit `data/technology_parameters.csv` to modify:

| Technology | Parameter | Baseline Value | Source |
|------------|-----------|----------------|--------|
| NCC-Electricity | Electricity intensity | 5.0 MWh/ton C₂H₄ | BASF/SABIC/Linde 2024 |
| NCC-H₂ | H₂ consumption | 0.56 ton H₂/ton C₂H₄ | Chen 2024, Gupta 2023 |
| RE PPA | Price trajectory | $70→$50/MWh (2025→2050) | IRENA 2024 |
| Heat Pump | COP | 4.0 | Kosmadakis 2020 |

## Key Results

### Technology Cost Parity
- **Shaheen scenario**: $31.4B (H₂) vs $33.3B (Electricity) — **6% difference**
- MACC convergence: $65/tCO₂ (H₂) vs $72/tCO₂ (Electricity) in 2050

### Energy System Divergence
- **Electricity pathway**: 164.5 TWh/year (97% of 2036 renewable target) — **INFEASIBLE**
- **Hydrogen pathway**: 7.7 Mt H₂/year (28% of 2050 target) — **FEASIBLE**

### Policy Implication
**Grid capacity, not technology cost, emerges as the binding constraint** for industrial decarbonization.

## Model Validation

| Metric | Model Output | Literature Range | Status |
|--------|--------------|------------------|--------|
| Baseline intensity (tCO₂/ton) | 2.26 | 2.0-2.5 | ✅ Validated |
| NCC-H₂ CAPEX | $1,550/t-C₂H₄ | $1,300-2,000 | ✅ Validated |
| NCC-Electricity CAPEX | $1,500/t-C₂H₄ | $1,200-1,800 | ✅ Validated |
| Total ethylene capacity | 11.96 Mt/year | KPIA 2023 | ✅ Validated |

## Citation

If you use this model in your research, please cite:

```bibtex
@article{Park2025MACC,
  title={Beyond Partial Equilibrium: Why Technology Costs and Energy System Constraints Diverge in Industrial Decarbonization Pathways},
  author={Park, Jinsu},
  journal={Carbon Neutrality},
  year={2025},
  publisher={Springer Nature},
  doi={[to-be-added]}
}
```

## Data Sources

- **Facility emissions**: Korea National Greenhouse Gas Inventory (2022)
- **Production capacity**: Korea Petrochemical Industry Association (KPIA, 2023)
- **Technology costs**: Literature review (Smith 2024, Jones 2023, Zhang 2022, Chen 2024)
- **Energy prices**: IRENA (2024), IEA (2023)
- **Policy targets**: Korea 10th Basic Plan for Electricity Supply and Demand (2023), Hydrogen Economy Roadmap (2021)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

**Jinsu Park**
Plan/It Institute
Seoul, South Korea
Email: jinsu@planit.institute

## Acknowledgments

Facility-level emissions data were obtained from Korea's National Greenhouse Gas Inventory (2022) and publicly available industrial complex reports. Technology cost parameters were validated against industry pilot plant data from BASF, SABIC, and Linde (2024).

## Version History

- **v1.0** (2025-01-XX): Initial release accompanying journal publication
  - Full 6-scenario analysis
  - Sensitivity analysis (±10% CAPEX, electricity price, H₂ efficiency)
  - Publication-quality figures
