# Stranded Asset Analysis and Comprehensive Report - Summary

## Overview

This document summarizes the newly implemented stranded asset analysis module and comprehensive reporting system for Korea's petrochemical industry decarbonization model.

## New Features Implemented

### 1. Stranded Asset Analysis Module (`modules/stranded_assets.py`)

A complete stranded asset analysis framework that evaluates economic risks under decarbonization scenarios.

#### Key Components:

**A. Asset Valuation**
- Calculates book value for all 248 facilities based on:
  - Initial CAPEX (capital intensity by facility type)
  - Facility age and depreciation
  - Remaining useful life
- Total asset value at risk: **$15.9 billion**

**B. Stranding Risk Assessment**
Three types of asset stranding are identified:

1. **Premature Retirement** (>80% abatement required)
   - Facilities close before end of useful life
   - Loss = full book value
   - Average impact: $2.3B - $8.8B depending on scenario

2. **Forced Retrofit** (technology deployment required)
   - CAPEX investment for decarbonization technologies
   - NCC-H2, NCC-Electricity, Heat Pumps
   - Average impact: $10.7B - $22.3B depending on scenario

3. **Operational Stranding** (20-80% abatement)
   - Facilities continue but lose competitiveness
   - Reduced asset value (30% impairment)
   - Average impact: $1.6B - $3.4B depending on scenario

**C. Stranding Scenarios**
Analysis across 6 scenarios:
- Shaheen (growth) + NCC-H2: 188% stranding rate
- Shaheen (growth) + NCC-Electricity: 207% stranding rate
- Restructure 25% + NCC-H2: 114% stranding rate
- Restructure 25% + NCC-Electricity: 126% stranding rate
- Restructure 40% + NCC-H2: 105% stranding rate
- Restructure 40% + NCC-Electricity: 116% stranding rate

**Note:** Stranding rates >100% indicate that retrofit costs exceed original asset values.

#### Outputs:

**Files:**
- `facility_assets_2025.csv` - Asset valuation for all facilities
- `stranding_summary.csv` - Summary by scenario
- `regional_stranding.csv` - Regional breakdown
- `sectoral_stranding.csv` - Sectoral breakdown
- `facility_stranding_*.csv` - Facility-level detail per scenario

**Visualizations:**
- `stranded_assets_by_scenario.png` - Waterfall chart by scenario
- `regional_stranding_heatmap.png` - Geographic risk distribution
- `sectoral_stranded_assets.png` - Product group impacts

### 2. Comprehensive Report Generator (`generate_comprehensive_korea_report.py`)

An integrated reporting system that synthesizes all model outputs into actionable insights.

#### Report Sections:

**A. Executive Summary**
- Industry overview (248 facilities, 52 MtCO2, 100kt capacity)
- Key findings
- Technology costs and trajectories

**B. Industry Structure**
- Facility distribution by product group, location, company
- Market concentration analysis
- Age distribution

**C. Technology Pathways**
- MACC analysis summary
- Cost evolution (2025-2050)
- Abatement potential by technology:
  - NCC-H2: 26.8 Mt/year
  - NCC-Electricity: 24.5 Mt/year
  - RE PPA: 8.4 Mt/year
  - Heat Pump: 1.0 Mt/year

**D. Stranded Asset Analysis**
- Summary by scenario
- Regional impact (highest risk: Yeosu, Daesan, Onsan)
- Sectoral impact (highest risk: Olefins)

**E. Investment Requirements**
- Operational costs (2050): $13B - $33B/year
- Retrofit CAPEX: $11B - $22B total
- H2 infrastructure: up to 7,704 kt/year
- Electricity infrastructure: up to 165 TWh/year

**F. Policy Recommendations**
Five priority areas:
1. Technology Development (High priority)
2. Asset Transition Support (High priority)
3. Regional Policy (Medium priority)
4. Energy Infrastructure (High priority)
5. Hydrogen Infrastructure (High priority)

#### Outputs:

**Files:**
- `comprehensive_report.md` - Full markdown report
- `executive_summary.csv` - Key metrics
- `technology_analysis.csv` - Technology comparison
- `investment_requirements.csv` - Investment breakdown
- `policy_recommendations.csv` - Policy guidance

## Usage

### Running Stranded Asset Analysis

```bash
python run_module_04_stranded_assets.py
```

This will:
1. Calculate facility asset values
2. Analyze stranding under all scenarios
3. Create regional and sectoral breakdowns
4. Generate visualizations

### Generating Comprehensive Report

```bash
python generate_comprehensive_korea_report.py
```

This will:
1. Load all model outputs (baseline, MACC, optimization, stranded assets)
2. Generate executive summary and key insights
3. Create detailed analysis sections
4. Save CSV summaries and markdown report

## Key Insights

### 1. Stranded Asset Risk is Substantial
- Average stranding rate: **142.6%** across scenarios
- Total at risk: **$15.9B** in book value
- **$11B - $22B** additional retrofit investment required

### 2. Regional Concentration
High-risk regions (>150% stranding rate):
- **Yeosu**: 172% stranding rate, 87 facilities
- **Daesan**: 165% stranding rate, 57 facilities
- **Onsan**: 172% stranding rate, 14 facilities

### 3. Technology Pathways
- **NCC-Electricity** is most cost-effective by 2050 ($174/tCO2)
- **NCC-H2** requires massive H2 infrastructure (7,700 kt/year)
- **RE PPA** offers quick wins but limited abatement potential

### 4. Investment Scale
- **Operational costs**: $13-33B/year by 2050
- **Retrofit CAPEX**: $11-22B total
- **Infrastructure**: Massive renewable energy and H2 capacity needed

### 5. Policy Imperative
- Early action reduces stranded asset risk
- Coordinated regional support essential
- Technology development funding critical
- Transition support mechanisms required

## Model Structure

The complete model now includes:

1. **Module 1: Baseline** - Emissions inventory and BAU trajectory
2. **Module 2: MACC** - Technology costs and abatement potential
3. **Module 3: Optimization** - Cost-optimal deployment pathways
4. **Module 4: Stranded Assets** - Economic risk assessment (NEW)
5. **Comprehensive Report** - Integrated analysis and recommendations (NEW)

## Next Steps for Users

1. **Review comprehensive report** (`outputs/comprehensive_korea_report/comprehensive_report.md`)
2. **Analyze facility-level risks** (facility_stranding_*.csv files)
3. **Assess regional impacts** (regional_stranding.csv)
4. **Evaluate policy options** (policy_recommendations.csv)
5. **Customize scenarios** (modify scenario files and re-run)

## Data Requirements

The model requires:
- ✅ Facility database (248 facilities)
- ✅ Energy intensities
- ✅ Technology parameters
- ✅ Price trajectories
- ✅ Emission factors
- ✅ Scenario definitions

All data files are in `data/` directory.

## Validation and Quality Checks

The model includes:
- ✅ Baseline validation (52 MtCO2 matches known industry emissions)
- ✅ Technology cost benchmarking (literature-validated)
- ✅ Stranded asset methodology (industry-standard depreciation)
- ✅ Facility-level consistency checks
- ✅ Regional aggregation validation

## Contact and Support

For questions about:
- **Model methodology**: See individual module documentation
- **Stranded asset calculations**: Review `modules/stranded_assets.py`
- **Report generation**: Review `generate_comprehensive_korea_report.py`
- **Data sources**: See `data/` directory and LITERATURE_REVIEW_ANALYSIS.md

## References

The stranded asset methodology is based on:
- IEA World Energy Outlook 2024
- IRENA Stranded Assets and Renewables (2017)
- Carbon Tracker Initiative methodology
- Industry standard depreciation methods
- Korean petrochemical industry benchmarks

---

**Model Version**: 1.0
**Last Updated**: 2025-11-19
**Total Lines of Code**: ~3,000+ (stranded assets + reporting)
