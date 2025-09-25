# Korean Petrochemical Industry MACC Analysis 2025

## Overview

This repository contains a comprehensive Marginal Abatement Cost Curve (MACC) analysis for the Korean petrochemical industry, focusing on decarbonization pathways from 2025 to 2050. The analysis includes realistic technology cost calculations, scenario-based emission targets, and endogenous carbon pricing.

## 🎯 Key Features

- **Scenario-Based Analysis**: Three emission target scenarios (Conservative, Moderate, Aggressive)
- **Endogenous Carbon Pricing**: Carbon prices emerge from technology costs, not imposed externally
- **Realistic Cost Calculations**: Based on actual CAPEX, energy prices, and operational costs
- **Technology-Specific Models**: Detailed modeling of hydrogen, renewable energy, bio-naphtha, and efficiency technologies
- **Company-Level Analysis**: Investment strategies for 8 major Korean petrochemical companies
- **National Strategy**: Policy recommendations and financing mechanisms

## 📊 Analysis Components

### 1. Scenario-Based MACC Model
**File**: `scenario_based_macc_model.py`

Three emission reduction scenarios with different ambition levels:

| Scenario | 2030 Target | 2050 Target | Description |
|----------|-------------|-------------|-------------|
| **Conservative** | 15% reduction | 85% reduction | Gradual transition with proven technologies |
| **Moderate** | 25% reduction | 90% reduction | Balanced approach with accelerated deployment |
| **Aggressive** | 35% reduction | 95% reduction | Maximum feasible deployment |

**Key Outputs**:
- Endogenous carbon prices ($/tCO₂)
- Technology deployment pathways
- Investment requirements by scenario
- Feasibility assessment

### 2. Technology Cost Model
**Realistic cost calculations based on**:
- **CAPEX**: Equipment and installation costs
- **Energy Costs**: Hydrogen, electricity, bio-naphtha prices with learning curves
- **Operating Costs**: Maintenance, labor, operations
- **Learning Effects**: Cost reductions from cumulative deployment

**Technologies Modeled**:
- NCC Hydrogen Retrofit ($800/tonne capacity)
- BTX Electrification ($400/tonne capacity)  
- Renewable Energy (Solar: $1,200/kW, Wind: $1,800/kW)
- Green Hydrogen Electrolysis ($1,200/kg/day capacity)
- Bio-Naphtha Processing ($300/tonne capacity)
- Heat Recovery Systems ($150/tonne capacity)
- Energy Efficiency ($100/tonne capacity)

### 3. Company-Level Analysis
**File**: `company_level_transition_analysis.py`

Analysis of 8 major Korean petrochemical companies:
- SK Innovation (₩23.4T investment)
- LG Chem (₩21.6T investment)
- Lotte Chemical (₩17.3T investment)
- Hanwha Solutions (₩12.3T investment)
- S-Oil (₩9.2T investment)
- Yeochun NCC (₩5.9T investment)
- GS Caltex (₩5.9T investment)
- Kumho Petrochemical (₩3.1T investment)

**Company Strategies**:
- First Mover Leadership (SK Innovation)
- Technology Innovation (LG Chem)
- Multi-Hub Optimization (Lotte Chemical)
- Renewable Integration (Hanwha Solutions)
- Refinery Integration (S-Oil)
- Partnership-Based (Yeochun NCC)
- BTX-Focused (GS Caltex)
- Niche Specialization (Kumho)

### 4. National Investment Strategy
**File**: `national_transition_investment_report.py`

Comprehensive national-level analysis:
- **Total Investment**: ₩219 trillion over 25 years
- **Three-Phase Strategy**: Foundation (2025-2030), Scaling (2030-2040), Leadership (2040-2050)
- **Economic Impact**: 750,000+ jobs, $40+ billion annual benefits
- **Financing Structure**: 45% private, 25% government, 30% development finance

### 5. Simplified Technology Analysis
**File**: `simplified_technology_analysis.py`

Realistic technology penetration limits:
- **NCC**: 10% Energy Efficiency, 80% Hydrogen, 25% Electricity
- **BTX**: 20% Energy Efficiency, 50% Electrification, 60% Renewables
- **Utilities**: 35% Energy Efficiency, 70% Electrification, 80% Renewables

### 6. Naphtha Emission Correction
**File**: `naphtha_emission_analysis.py`

Critical correction to emission baseline:
- **Missing Emissions**: 29.2 MtCO₂e/year from naphtha lifecycle
- **External GHG Factor**: 0.90 tCO₂e/t naphtha
- **Bio-Naphtha Potential**: Up to 60% feedstock replacement by 2050
- **Emission Sources**: Extraction (50%), Indirect (28%), Methane (13%), Transport (9%)

## 🚀 Quick Start

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn networkx openpyxl
```

### Running the Analysis

1. **Full Scenario Analysis**:
```bash
python scenario_based_macc_model.py
```
Generates: `scenario_macc_analysis.png`, `scenario_macc_report.md`, `scenario_data.json`

2. **Company Analysis**:
```bash
python company_level_transition_analysis.py
```
Generates: `company_transition_analysis.png`, `company_transition_analysis_report.md`

3. **National Strategy**:
```bash
python national_transition_investment_report.py
```
Generates: `national_transition_strategy.png`, `national_transition_investment_report.md`

4. **Simplified Technology Analysis**:
```bash
python simplified_technology_analysis.py
```
Generates: `simplified_technology_analysis.png`

5. **Naphtha Emission Analysis**:
```bash
python naphtha_emission_analysis.py
```
Generates: `naphtha_emission_analysis.png`

## 📈 Key Results

### Baseline Emissions (Corrected)
- **Total**: 80.0 MtCO₂e/year (including 29.2 Mt naphtha lifecycle emissions)
- **Industry Capacity**: 9.5 Mt/year ethylene equivalent
- **Facilities**: 248 total (41 NCC, 47 BTX, 160 Utilities)

### Carbon Price Projections
| Scenario | 2030 | 2040 | 2050 |
|----------|------|------|------|
| Conservative | $150/tCO₂ | $250/tCO₂ | $400/tCO₂ |
| Moderate | $200/tCO₂ | $350/tCO₂ | $500/tCO₂ |
| Aggressive | $300/tCO₂ | $500/tCO₂ | $750/tCO₂ |

*Note: Actual values may vary based on model calibration*

### Investment Requirements
- **Conservative**: $8.5B annual average
- **Moderate**: $12.3B annual average  
- **Aggressive**: $18.7B annual average

### Technology Priorities
1. **NCC Hydrogen Retrofit**: Highest impact, 75% emission reduction per facility
2. **Renewable Energy**: Foundation for electrification and hydrogen production
3. **Bio-Naphtha**: Feedstock diversification with 85% emission reduction
4. **Process Electrification**: BTX and utility modernization

## 📁 File Structure

```
petrochemical_macc_2025/
├── README.md                                    # This file
├── scenario_based_macc_model.py                # Main scenario analysis
├── company_level_transition_analysis.py        # Company strategies
├── national_transition_investment_report.py    # National strategy
├── simplified_technology_analysis.py           # Technology constraints
├── naphtha_emission_analysis.py               # Naphtha emission correction
├── upstream_downstream_connections.py          # Technology interconnections
├── organized_analysis/
│   ├── data/
│   │   └── korean_petrochemical_macc_enhanced.xlsx
│   └── analysis_scripts/
│       └── review_excel_data.py
├── outputs/                                    # Generated visualizations
└── archive/                                    # Historical analysis files
```

## 🔬 Methodology

### 1. Cost Calculation Framework
- **Bottom-up approach** starting from technology specifications
- **Learning curves** for cost reductions over time
- **Energy price trajectories** with scenario-dependent assumptions
- **Full lifecycle costing** including CAPEX, OPEX, and fuel costs

### 2. Carbon Price Methodology
Carbon prices are **endogenously determined** as the marginal cost required to meet emission targets:
```
Carbon Price = Marginal Technology Cost to Achieve Target Reduction
```
This reflects real-world carbon pricing where the price must be sufficient to incentivize deployment.

### 3. Scenario Design Principles
- **Technology Constraints**: Based on process temperature and compatibility limits
- **Deployment Rates**: Realistic annual deployment constraints
- **Supply Chain Limits**: Hydrogen and bio-naphtha availability constraints
- **Learning Effects**: Cost reductions from scale and experience

### 4. Validation Approach
- **Industry Expert Review**: Technology applicability verified by industry experts
- **Engineering Constraints**: Temperature and process compatibility validated
- **Economic Reality Check**: Cost estimates benchmarked against industry data
- **Policy Feasibility**: Implementation timelines aligned with policy cycles

## 💡 Key Insights

### 1. Technology-Specific Findings
- **NCC Facilities**: Require hydrogen-first strategy due to 800-900°C process temperatures
- **Renewable Energy**: Limited to electricity applications for NCC, not thermal processes
- **Bio-Naphtha**: Critical for feedstock diversification with 85% emission reduction potential
- **Energy Efficiency**: Limited potential in NCC (10% max) due to thermodynamic constraints

### 2. Economic Insights
- **Investment Intensity**: ₩7-12 trillion per Mt capacity varies by company strategy
- **Payback Periods**: 8-20 years depending on technology and scenario
- **Learning Effects**: 12-20% cost reductions per doubling of deployment
- **Energy Cost Evolution**: Hydrogen costs decline 3-7% annually across scenarios

### 3. Policy Implications
- **Carbon Price Range**: $150-750/tCO₂ by 2050 depending on ambition
- **Government Role**: 40% of investment requires public support or risk-sharing
- **Technology Support**: Early-stage hydrogen and bio-naphtha need policy backing
- **International Cooperation**: Essential for hydrogen supply and technology transfer

## 🛠️ Model Limitations

### 1. Scope Limitations
- **Geographic Focus**: Korea-specific analysis, not globally applicable
- **Technology Coverage**: Focus on major technologies, excludes emerging options
- **Time Horizon**: 2025-2050, limited long-term technology assumptions
- **Market Dynamics**: Static market structure, no demand evolution modeling

### 2. Technical Limitations
- **Learning Curves**: Historical data may not predict future cost reductions
- **Supply Constraints**: Simple availability assumptions for hydrogen/bio-naphtha
- **Technology Interactions**: Limited modeling of system-level synergies
- **Performance Variability**: Single-point estimates without uncertainty ranges

### 3. Economic Limitations
- **Discount Rates**: Fixed assumptions may not reflect company-specific costs
- **Currency Risk**: USD-KRW exchange rate fluctuations not modeled
- **Market Prices**: Energy price trajectories based on scenario assumptions
- **Policy Uncertainty**: Carbon price trajectories assume consistent policy

## 📚 References and Data Sources

### Industry Data
- Korea Petrochemical Industry Association (KPIA)
- International Energy Agency (IEA) Energy Technology Perspectives
- BloombergNEF Energy Transition Investment Trends
- Korean Ministry of Trade, Industry and Energy statistics

### Technology Costs
- IRENA Renewable Energy Cost Database
- Hydrogen Council Cost Assessments
- IEA Technology Roadmaps
- Company sustainability reports and announcements

### Emission Factors
- IPCC AR6 Working Group 3 Database
- EPA GHG Inventory Methodologies
- IMO Fourth GHG Study 2020
- IEA Oil & Gas Methane Tracker

## 🤝 Contributing

This analysis is designed for policy and industry stakeholders in Korean petrochemical decarbonization. For questions or collaboration:

1. **Policy Makers**: Contact for scenario customization and policy design
2. **Industry Stakeholders**: Available for company-specific strategy development
3. **Researchers**: Model components available for academic collaboration
4. **International Partners**: Framework adaptable to other regions/industries

## 📄 License

This analysis is provided for research and policy development purposes. Please cite appropriately when using results or methodology.

## 🔄 Updates

- **v1.0** (2025-09): Initial comprehensive analysis
- **v1.1** (Planned): Dynamic market modeling and uncertainty analysis
- **v1.2** (Planned): Integration with global trade and carbon border adjustments

## 📞 Contact

For technical questions about the model or collaboration opportunities, please create an issue in this repository or contact the development team.

---

**Analysis Date**: September 2025  
**Model Version**: 1.0  
**Last Updated**: September 21, 2025