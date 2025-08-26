# Data Update Guidelines for Korean Petrochemical MACC Model

## Overview

This document provides guidelines for updating data in the Korean Petrochemical MACC (Marginal Abatement Cost Curve) model to ensure accuracy, consistency, and reliability of results.

## Data Structure

### Core Data Files

1. **`data/Korea_Petrochemical_MACC_Database.xlsx`** - Main database containing all model input data
2. **`update_excel_data.py`** - Script to regenerate the database with updated parameters

### Excel Database Sheets

#### 1. **TechBands_2023** (Baseline Data)
**Purpose**: 2023 baseline production and emission data by technology bands

**Key Columns**:
- `TechGroup`: Process type (NCC, BTX, C4)
- `Band`: Technology efficiency level (HT, MT, LT)
- `Activity_kt_product`: Production capacity (kt/year)
- `EmissionIntensity_tCO2_per_t`: Emission factor (tCO2/t product)
- `SEC_GJ_per_t`: Specific energy consumption (GJ/t)

**Update Frequency**: Annually or when major production changes occur
**Data Sources**: 
- Korean Ministry of Trade, Industry and Energy
- Korea Petrochemical Industry Association (KPIA)
- Company annual reports

#### 2. **RegionalFacilities** (Facility-Level Data)
**Purpose**: Regional facility capacity and characteristics

**Key Columns**:
- `FacilityID`: Unique facility identifier
- `Region`: Yeosu, Daesan, or Ulsan
- `Company`: Operating company name
- `[Process]_Capacity_kt_per_year`: Capacity by process (NCC, BTX, C4)
- `TechnicalReadiness_Level`: Technology maturity (1-9)
- `Infrastructure_Score`: Regional infrastructure rating

**Update Frequency**: Every 2-3 years or after major capacity expansions
**Data Sources**:
- Company investment announcements
- Government industrial statistics
- Industry association reports

#### 3. **AlternativeTechnologies** (Technology Options)
**Purpose**: Available alternative technologies and their characteristics

**Key Columns**:
- `TechID`: Technology identifier
- `TechGroup`: Applicable process (NCC, BTX, C4)
- `TechnologyCategory`: Technology type (E-cracker, Heat pump, etc.)
- `EmissionReduction_tCO2_per_t`: Abatement potential
- `MaxApplicability`: Maximum penetration rate (0-1)
- `CommercialYear`: Expected commercialization year
- `TechnicalReadiness`: TRL level (1-9)

**Update Frequency**: Semi-annually for emerging technologies
**Data Sources**:
- Technology roadmaps
- R&D project reports
- Pilot project results
- Technology vendor specifications

#### 4. **AlternativeCosts** (Technology Economics)
**Purpose**: Cost structure of alternative technologies

**Key Columns**:
- `CAPEX_Million_USD_per_kt_capacity`: Capital cost per unit capacity
- `OPEX_Delta_USD_per_t`: Operating cost change vs baseline
- `MaintenanceCost_Pct`: Annual maintenance cost as % of CAPEX

**Update Frequency**: Annually or when major cost updates available
**Data Sources**:
- Technology vendor quotes
- Engineering studies
- Demonstration project data
- Industry benchmarks

#### 5. **EmissionsTargets** (Policy Targets)
**Purpose**: National emission reduction targets

**Update Frequency**: When policy updates occur
**Data Sources**:
- Korean Green New Deal
- National Determined Contributions (NDC)
- Ministry announcements

## Data Update Process

### Step 1: Data Collection and Validation

1. **Gather Updated Data**:
   - Collect from official sources listed above
   - Cross-verify between multiple sources
   - Document data collection date and source

2. **Data Quality Checks**:
   - Verify units are consistent
   - Check for missing values
   - Validate ranges (e.g., TRL 1-9, shares 0-1)
   - Ensure facility capacity sums match regional totals

### Step 2: Update Parameters

1. **Baseline Production Data** (`TechBands_2023`):
   ```python
   # Update in update_excel_data.py
   bands_data = {
       'Activity_kt_product': [
           # Update with latest production statistics
           3500, 2800, 1200,  # NCC bands - UPDATE THESE
           1200, 800, 1100,   # BTX bands - UPDATE THESE
           450, 350, 200      # C4 bands - UPDATE THESE
       ],
       'EmissionIntensity_tCO2_per_t': [
           # Update with latest emission factors
           2.85, 1.23, 0.65,  # NCC - UPDATE THESE
           # ... continue for other processes
       ]
   }
   ```

2. **Facility Capacities** (`RegionalFacilities`):
   - Update capacity expansions/reductions
   - Add new facilities or remove decommissioned ones
   - Update company ownership changes

3. **Technology Data** (`AlternativeTechnologies`):
   - Update TRL levels based on demonstration progress
   - Adjust commercialization years
   - Add new emerging technologies

4. **Cost Data** (`AlternativeCosts`):
   - Update CAPEX based on latest vendor quotes
   - Adjust OPEX for fuel price changes
   - Update maintenance costs from operational experience

### Step 3: Database Regeneration

1. **Run Update Script**:
   ```bash
   python update_excel_data.py
   ```

2. **Verify Output**:
   - Check baseline emissions calculation
   - Verify all sheets are updated
   - Confirm formulas are working

### Step 4: Model Testing

1. **Run Model**:
   ```bash
   python run_model.py
   ```

2. **Sanity Checks**:
   - Baseline emissions should match expected total
   - Technology deployment patterns should be reasonable
   - Regional distributions should reflect capacity data
   - Cost curves should be monotonically increasing

3. **Compare Results**:
   - Compare with previous model run
   - Investigate major changes
   - Document significant differences

## Critical Data Sources

### Production and Emissions Data
- **Korea Petrochemical Industry Association (KPIA)**: Annual statistics
- **Korea Energy Agency**: Energy consumption data
- **Ministry of Environment**: Emission factors and regulations

### Technology and Cost Data
- **International Energy Agency (IEA)**: Technology roadmaps
- **IRENA**: Renewable energy and hydrogen costs
- **McKinsey Global Institute**: Industrial decarbonization reports
- **BloombergNEF**: Clean technology cost trends

### Facility and Regional Data
- **Korea Development Bank**: Industrial financing reports
- **Regional development agencies**: Infrastructure assessments
- **Company investor relations**: Capacity expansion announcements

## Data Quality Indicators

### Red Flags (Require Immediate Review)
- Baseline emissions change >20% without major industry changes
- Technology costs change >50% without clear justification
- New facilities appear without public announcements
- TRL levels decrease (technologies rarely move backward)

### Validation Metrics
- Total baseline emissions: ~18-20 MtCO2/year (cross-check with national inventory)
- Regional capacity distribution: Yeosu ~50%, Daesan ~30%, Ulsan ~20%
- Technology readiness: Average TRL should increase over time
- Cost effectiveness: Most heat pumps and electric motors should have negative LCOA

## Research Priorities for Data Improvement

### High Priority (Update Annually)
1. **Facility-specific emission factors**: Move from band averages to facility-specific data
2. **Real deployment constraints**: Beyond max applicability, consider practical ramp-up rates
3. **Regional cost variations**: Labor, electricity, infrastructure costs by region
4. **Learning curve effects**: Cost reduction as technologies scale up

### Medium Priority (Update Every 2-3 Years)
1. **Co-benefits quantification**: Air quality, job creation, energy security
2. **Infrastructure requirements**: Grid upgrades, hydrogen supply, CO2 transport
3. **Policy scenario modeling**: Carbon pricing, subsidies, regulations
4. **Technology interdependencies**: How one technology affects others

### Low Priority (Update as Available)
1. **Financing assumptions**: Interest rates, technology risk premiums
2. **Operational flexibility**: Part-load performance, seasonal variations
3. **End-of-life considerations**: Decommissioning costs, material recovery

## Contacts for Data Updates

### Government Agencies
- Ministry of Trade, Industry and Energy: Industrial statistics division
- Ministry of Environment: Climate policy division
- Korea Energy Agency: Industrial energy efficiency team

### Industry Associations
- Korea Petrochemical Industry Association (KPIA): Technical committee
- Korea Chemical Industry Council: Sustainability working group

### Research Institutions
- Korea Institute of Energy Research: Industrial decarbonization team
- Korea Environmental Institute: Climate policy analysis team

## Version Control

- Always maintain backup of previous database version
- Document all changes in change log with date and reason
- Tag model releases with database version used
- Archive results from each major update for historical comparison

---

**Last Updated**: 2025-01-26  
**Next Review Due**: 2025-07-26  
**Contact**: Model maintenance team