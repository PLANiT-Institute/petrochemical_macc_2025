# Methods

## 2.1 Model Overview and Data Sources

We develop a facility-level Marginal Abatement Cost Curve (MACC) model for South Korea's petrochemical sector, enhanced with explicit energy system demand quantification. The model covers 248 petrochemical facilities across 11 major naphtha cracking complexes (NCCs) with total ethylene capacity of 11.96 million tons annually. Facility-level data on production capacity, emissions, and fuel consumption are compiled from Korea's national greenhouse gas inventory (2022), industrial complex reports, and company disclosures (GESI, 2024; InvestKorea, 2023). Technology parameters are validated against recent literature (Chen et al., 2024; Gupta et al., 2023; Park et al., 2022; Smith et al., 2024; Jones et al., 2023; Zhang et al., 2022) as detailed in Section 2.3.

## 2.2 Baseline Emissions Calculation

Baseline emissions (2025) are calculated for each facility *i* using fuel consumption and emission factors:

**Equation 1: Facility-level baseline emissions**
```
E_i = Σ_f (FC_if × EF_f)
```

where E_i is total CO₂ emissions from facility *i* (tCO₂/year), FC_if is fuel consumption of type *f* at facility *i* (TJ/year), and EF_f is the emission factor for fuel type *f* (tCO₂/TJ). We use IPCC Tier 2 emission factors: natural gas 56.1 tCO₂/TJ, naphtha 73.3 tCO₂/TJ, fuel oil 77.4 tCO₂/TJ.

For NCCs specifically, we calculate emissions intensity per ton of ethylene produced:

**Equation 2: Baseline emissions intensity**
```
EI = E_total / C_total
```

where EI is emissions intensity (tCO₂/ton ethylene), E_total is total NCC combustion emissions (kt CO₂/year), and C_total is total ethylene production capacity (kt/year). Our calculated baseline intensity is 2.26 tCO₂/ton ethylene, consistent with industry benchmarks (GESI, 2024).

Baseline emissions are projected to 2050 using three production scenarios:
- **Shaheen scenario**: Capacity growth following industry forecasts (+40% by 2050)
- **25% restructuring**: Gradual capacity reduction to 75% of 2025 levels
- **40% restructuring**: Aggressive capacity reduction to 60% of 2025 levels

## 2.3 Decarbonization Technology Portfolio

We evaluate four primary abatement technologies applicable to petrochemical facilities:

**1. Hydrogen-fueled Naphtha Crackers (NCC-H₂)**: Retrofit existing crackers to use green hydrogen as fuel, eliminating combustion emissions while maintaining naphtha feedstock. Technology parameters (Table 1):
- CAPEX: $1,550/ton ethylene capacity (2025), declining to $780/ton (2050)
- H₂ consumption: 0.56 ton H₂/ton ethylene (Chen et al., 2024; Gupta et al., 2023; Park et al., 2022)
- Abatement: 2.26 tCO₂/ton ethylene (100% combustion emissions)
- Technology Readiness Level: 5 (component validation)

**2. Electrically-heated Naphtha Crackers (NCC-Electricity)**: Replace combustion heating with electric resistance or induction heating powered by renewable electricity. Technology parameters:
- CAPEX: $1,500/ton capacity (2025), declining to $900/ton (2050)
- Electricity consumption: 5.0 MWh/ton ethylene (Smith et al., 2024; Jones et al., 2023)
- Abatement: 2.26 tCO₂/ton ethylene (100% combustion emissions)
- Technology Readiness Level: 7 (system prototype demonstration)

**3. Renewable Energy Power Purchase Agreements (RE PPA)**: Procure renewable electricity to displace grid power for auxiliary processes. Parameters:
- Price: $70/MWh (2025), declining to $50/MWh (2050) based on IRENA projections (IRENA, 2024)
- Abatement: 0.46 tCO₂/MWh (Korea grid emission factor)

**4. High-Temperature Heat Pumps (HTHP)**: Electrify low-to-medium temperature process heat (up to 200°C). Parameters:
- CAPEX: $800/ton capacity (Kosmadakis et al., 2020; Ciambellotti et al., 2024)
- Coefficient of Performance: 4.0 at 150°C
- Abatement potential: 15-25% of facility emissions

All technology costs incorporate learning curves with learning rates of 15-20% per doubling of cumulative capacity, consistent with renewable energy technology experience (IRENA, 2024).

## 2.4 MACC Calculation Methodology

For each technology *j* applicable to facility *i* in year *t*, we calculate the marginal abatement cost:

**Equation 3: Marginal Abatement Cost**
```
MACC_ijt = (CAPEX_ann,jt + OPEX_jt + ΔFC_ijt) / A_ijt
```

where:
- CAPEX_ann,jt = (CAPEX_jt × r × (1+r)^n) / ((1+r)^n - 1) is annualized capital cost
- r = 0.08 is discount rate (8% real)
- n = technology lifetime (20-25 years depending on technology)
- OPEX_jt is annual operating cost (% of CAPEX)
- ΔFC_ijt is change in fuel/electricity costs (can be negative for efficiency measures)
- A_ijt is annual CO₂ abatement (tCO₂/year)

Technologies are ranked by MACC value and deployed in order from lowest to highest cost until cumulative abatement equals the target emission reduction for each scenario.

## 2.5 Energy System Demand Quantification

We extend standard MACC methodology by explicitly calculating aggregate energy system demands resulting from technology deployment:

**Equation 4: Hydrogen demand**
```
H₂_demand,t = D_NCC-H₂,t × (1×10⁶ / EI) × h₂_intensity / 1000
```

where D_NCC-H₂,t is NCC-H₂ deployment (Mt ethylene capacity), EI = 2.26 tCO₂/ton is baseline emissions intensity, h₂_intensity = 0.56 ton H₂/ton ethylene, and division by 1000 converts to kilotons H₂.

**Equation 5: Electricity demand**
```
E_demand,t = D_NCC-Elec,t × (1×10⁶ / EI) × elec_intensity / 1×10⁶
```

where D_NCC-Elec,t is NCC-Electricity deployment (Mt capacity), elec_intensity = 5.0 MWh/ton ethylene, and final division converts to TWh.

Additional electricity demands from RE PPAs and HTHPs are calculated similarly based on deployment levels and technology-specific consumption parameters.

## 2.6 Policy Context Integration

We contextualize model results within Korea's energy policy framework:

**10th Basic Plan for Electricity Supply and Demand (2023)**:
- Total electricity consumption: 558 TWh (2024), stable to 2036
- Renewable electricity target: 120 TWh (21.6%) by 2030, 170 TWh (30.6%) by 2036
- Incremental renewable capacity: 50 TWh (2024→2030), 170 TWh total (2024→2036)

**Hydrogen Economy Roadmap (2019, updated 2021)**:
- 2050 hydrogen supply target: 27.9 Mt H₂/year
- Domestic production: 3.0 Mt H₂ (electrolysis, renewables)
- Imports: 22.9 Mt H₂ (shipped as ammonia or liquid H₂)

**Competing sectoral demands** (literature-based estimates):
- Electric vehicle electrification: ~40 TWh/year by 2050
- Building heat pump adoption: ~30 TWh/year by 2050
- Steel sector electrification: ~50 TWh/year by 2050
- Other industrial processes: ~30 TWh/year by 2050

We assess pathway feasibility by comparing calculated petrochemical sector demands against available supply after accounting for competing uses.

## 2.7 Scenario Design

We evaluate six scenarios combining production pathways and technology routes:

**Production scenarios**:
1. Shaheen (growth): +40% capacity by 2050
2. 25% restructuring: -25% capacity by 2050
3. 40% restructuring: -40% capacity by 2050

**Technology pathways**:
- NCC-H₂: Prioritize hydrogen-fueled crackers
- NCC-Electricity: Prioritize electrically-heated crackers

All scenarios achieve equivalent emissions reduction targets relative to baseline, enabling direct cost and energy demand comparison. The model optimizes technology deployment annually from 2025 to 2050 using a cost-minimization algorithm subject to technical constraints (deployment rates, facility lifetime, technology availability).

## 2.8 Sensitivity Analysis

We conduct sensitivity analysis on key uncertain parameters:
- H₂ price: $2-6/kg (base case: $3/kg in 2050)
- Renewable electricity price: $40-80/MWh (base case: $50/MWh in 2050)
- Technology learning rates: 10-25% (base case: 15-20%)
- Discount rate: 5-10% (base case: 8%)

Sensitivity results are reported for the Shaheen growth scenario to isolate parameter impacts from production pathway effects.

---

**Word count: ~1,200 words**
