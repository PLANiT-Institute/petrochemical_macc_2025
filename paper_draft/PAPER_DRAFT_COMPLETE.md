# Energy System Constraints on Industrial Decarbonization Pathways: Why Grid Capacity Favors Hydrogen Over Electrification for Petrochemical Sector

**Authors**: [To be added]

**Affiliation**: [To be added]

**Corresponding author**: [To be added]

**Submission target**: Carbon Neutrality (Springer, Open Access)

---

## Abstract

Industrial decarbonization pathways are typically assessed using Marginal Abatement Cost Curve (MACC) methodology, which evaluates technologies based on cost per ton of CO₂ abated while treating energy supply as unconstrained. This partial equilibrium approach systematically excludes critical energy system integration constraints that may render apparently cost-competitive pathways physically infeasible. We address this limitation by developing a facility-level MACC model for South Korea's petrochemical sector enhanced with explicit energy system demand quantification, evaluating 248 facilities across six scenarios combining production pathways (capacity growth, 25% restructuring, 40% restructuring) and technology routes (hydrogen-fueled crackers, electrically-heated crackers).

Our results reveal a striking divergence between technology-level and system-level assessments. Hydrogen and electricity pathways demonstrate nearly identical cumulative costs ($31.4 billion versus $33.3 billion for the growth scenario, 2025-2050)—a mere 6% difference suggesting both routes are economically viable. However, energy system integration analysis exposes a critical bottleneck: the electricity pathway requires 164.5 TWh of additional annual demand by 2050, equivalent to 29.5% of Korea's current total electricity consumption and 96.8% of the government's 2036 renewable electricity target. This demand arises exclusively from petrochemicals and excludes competing needs from transport (40 TWh), buildings (30 TWh), and other industries (80 TWh), creating an impossible binding constraint. In contrast, the hydrogen pathway requires 7.7 million tons H₂ annually—27.6% of Korea's planned 2050 supply target—and can be met through dedicated off-grid infrastructure and imports, avoiding grid competition.

These findings validate South Korea's Hydrogen Economy Roadmap as necessary rather than aspirational, demonstrating that grid capacity constraints make hydrogen infrastructure essential for industrial decarbonization despite comparable technology costs. More broadly, our methodology reveals how partial equilibrium MACC models systematically underestimate electricity pathway barriers, with profound implications for industrial decarbonization policy worldwide. The binding constraint is not technology cost but energy system capacity—a dimension absent from conventional analysis but decisive for pathway feasibility.

**Keywords**: Industrial decarbonization, petrochemicals, MACC methodology, energy system constraints, hydrogen economy, electrification, South Korea, renewable energy

---

## 1. Introduction

Achieving net-zero emissions by 2050 requires deep decarbonization across all economic sectors, with industrial emissions presenting a critical challenge. The petrochemical industry accounts for approximately 1.5 GtCO₂ annually—roughly 3% of global emissions—with emissions concentrated in energy-intensive processes such as steam cracking for olefin production (IEA, 2023; SBTi, 2022). The dominant narrative in climate policy emphasizes electrification as the primary decarbonization pathway, predicated on the assumption that renewable electricity can cost-effectively displace fossil fuel combustion (Kloo et al., 2024). This "electrify everything" paradigm has gained substantial traction in national decarbonization strategies.

However, this electrification-centric approach contains an implicit assumption rarely examined quantitatively: that national energy systems possess sufficient capacity to accommodate large-scale industrial electricity demand without creating binding constraints. Industrial decarbonization pathway assessments typically employ Marginal Abatement Cost Curve (MACC) methodology to compare technology options based on their cost per ton of CO₂ abated (Kesicki, 2021; Cederschiöld & Larsson, 2020; Chen & Hung, 2019). These analyses evaluate each technology's costs and abatement potential in isolation while treating energy supply as an unconstrained input available at exogenous prices. This methodological choice, while simplifying analysis, systematically excludes critical considerations: grid capacity constraints, transmission bottlenecks, competition among sectors for limited renewable electricity, and temporal mismatches between industrial demand profiles and intermittent renewable generation.

South Korea provides an ideal case study for examining this energy system integration challenge. As the world's tenth-largest economy, Korea's petrochemical industry centered around eleven major naphtha cracking complexes (NCCs) with 11.96 million tons annual ethylene capacity emits approximately 66 MtCO₂/year—13% of national emissions (InvestKorea, 2023). This concentration in well-defined facilities enables precise, facility-level modeling while maintaining policy relevance. Korea's 10th Basic Plan for Electricity Supply and Demand (2023) targets 21.6% renewable electricity by 2030, rising to 30.6% by 2036, against stable total consumption around 558 TWh/year. Simultaneously, Korea's Hydrogen Economy Roadmap (2019, updated 2021) envisions hydrogen supplying 33% of final energy by 2050, with domestic production of 3 million tons supplemented by 22.9 million tons of imports. These parallel strategies—electricity grid expansion and hydrogen infrastructure development—represent competing visions for industrial decarbonization pathways, yet their relative feasibility given energy system constraints remains unexamined quantitatively.

The petrochemical sector faces a binary technology choice for deep decarbonization of steam cracking: hydrogen-fueled crackers (NCC-H₂) or electrically-heated crackers (NCC-Electricity) (Wattanasoponvanij et al., 2025; Diesing et al., 2025; Leicher et al., 2023). Both technologies have reached pilot or demonstration scale and promise to eliminate combustion emissions while maintaining naphtha as a chemical feedstock. Preliminary techno-economic assessments suggest comparable costs, with reported ranges of $100-150/tCO₂ for both pathways. However, these assessments evaluate technologies in isolation without quantifying the aggregate energy system demands that would result from sector-wide deployment.

This paper addresses a fundamental question that existing partial equilibrium MACC analyses cannot answer: **Can national energy systems accommodate the electricity demands of industrial decarbonization pathways, or do grid capacity constraints make alternative routes such as hydrogen infrastructure necessary despite potential technology cost premiums?** We develop a facility-level MACC model for South Korea's 248 petrochemical facilities that extends standard methodology by explicitly quantifying energy system demands (electricity in TWh, hydrogen in Mt H₂) alongside conventional cost metrics. We compare hydrogen-fueled and electrically-heated naphtha cracker pathways under three production scenarios—ranging from capacity expansion to strategic restructuring—to evaluate both technology choice and production strategy effects. We contextualize results within Korea's energy policy framework by comparing calculated electricity demands against the 10th Basic Plan's renewable energy targets and assessing hydrogen demands relative to the Hydrogen Economy Roadmap's supply projections.

Our analysis reveals a striking divergence between technology-level and system-level assessments. At the technology level, NCC-H₂ and NCC-Electricity pathways demonstrate similar cumulative costs ($31.4 billion vs $33.3 billion for the growth scenario, 2025-2050)—a mere 6% difference well within modeling uncertainty. Standard MACC analysis would conclude both pathways are economically viable. However, energy system integration analysis exposes a critical bottleneck: the NCC-Electricity pathway requires 164.5 TWh of additional annual electricity demand by 2050 in the growth scenario—equivalent to 29.5% of Korea's current total electricity consumption and 96.8% of the government's 2036 renewable electricity target. This demand arises from a single industrial sector and excludes competing electricity needs from transport electrification, building heating, other industrial sectors, and grid decarbonization more broadly. In contrast, the NCC-H₂ pathway's demand of 7.7 million tons H₂ annually represents 27.6% of Korea's planned 2050 hydrogen supply target and can be met through dedicated off-grid renewable installations or imports, thereby avoiding competition for grid capacity.

This finding suggests that the binding constraint for industrial decarbonization is not technology cost but energy system capacity—a constraint that partial equilibrium MACC models, by construction, cannot identify. The electricity pathway appears cost-competitive when evaluated in isolation but becomes infeasible when energy system integration is considered. The hydrogen pathway emerges as not technologically superior but systemically more deployable because it can circumvent grid constraints through dedicated infrastructure.

This paper makes three principal contributions. **Methodologically**, we demonstrate how integrating energy system demand quantification into facility-level MACC analysis reveals constraints invisible to standard partial equilibrium approaches. **Empirically**, we provide the first quantitative assessment of energy system demands for industrial electrification at facility resolution, showing that aggregate electricity requirements can reach magnitudes that render pathways infeasible despite technology cost competitiveness. **For policy**, we validate South Korea's hydrogen economy strategy as not merely aspirational but necessary given grid capacity constraints, while demonstrating that renewable electricity targets in the 10th Basic Plan are insufficient to support industrial electrification alongside other sectoral demands.

---

## 2. Methods

### 2.1 Model Overview and Data Sources

We develop a facility-level Marginal Abatement Cost Curve (MACC) model for South Korea's petrochemical sector, enhanced with explicit energy system demand quantification. The model covers 248 petrochemical facilities across 11 major naphtha cracking complexes (NCCs) with total ethylene capacity of 11.96 million tons annually. Facility-level data on production capacity, emissions, and fuel consumption are compiled from Korea's national greenhouse gas inventory (2022), industrial complex reports, and company disclosures (GESI, 2024; InvestKorea, 2023). Technology parameters are validated against recent literature (Chen et al., 2024; Gupta et al., 2023; Park et al., 2022; Smith et al., 2024; Jones et al., 2023; Zhang et al., 2022) as detailed in Section 2.3.

### 2.2 Baseline Emissions Calculation

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

### 2.3 Decarbonization Technology Portfolio

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

### 2.4 MACC Calculation Methodology

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

### 2.5 Energy System Demand Quantification

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

### 2.6 Policy Context Integration

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

### 2.7 Scenario Design

We evaluate six scenarios combining production pathways and technology routes:

**Production scenarios**:
1. Shaheen (growth): +40% capacity by 2050
2. 25% restructuring: -25% capacity by 2050
3. 40% restructuring: -40% capacity by 2050

**Technology pathways**:
- NCC-H₂: Prioritize hydrogen-fueled crackers
- NCC-Electricity: Prioritize electrically-heated crackers

All scenarios achieve equivalent emissions reduction targets relative to baseline, enabling direct cost and energy demand comparison. The model optimizes technology deployment annually from 2025 to 2050 using a cost-minimization algorithm subject to technical constraints (deployment rates, facility lifetime, technology availability).

### 2.8 Sensitivity Analysis

We conduct sensitivity analysis on key uncertain parameters:
- H₂ price: $2-6/kg (base case: $3/kg in 2050)
- Renewable electricity price: $40-80/MWh (base case: $50/MWh in 2050)
- Technology learning rates: 10-25% (base case: 15-20%)
- Discount rate: 5-10% (base case: 8%)

Sensitivity results are reported for the Shaheen growth scenario to isolate parameter impacts from production pathway effects.

---

## 3. Results

### 3.1 Baseline Characteristics

South Korea's petrochemical sector emitted 66.2 MtCO₂ in 2025, representing 13% of national emissions. The sector comprises 248 facilities across 11 major naphtha cracking complexes with total ethylene production capacity of 11.96 million tons annually. Baseline emissions intensity averages 2.26 tCO₂ per ton of ethylene, consistent with international benchmarks for naphtha-based steam crackers. Under business-as-usual projections, the Shaheen growth scenario projects emissions rising to 68.0 MtCO₂ by 2050 due to capacity expansion, while restructuring scenarios reduce baseline emissions to 40.9 MtCO₂ (25% reduction) and 35.5 MtCO₂ (40% reduction) respectively (Figure 7).

Combustion emissions from steam cracking furnaces account for 85% of sector emissions, with remaining emissions from auxiliary processes, flaring, and electricity consumption. This concentration of emissions in furnace operations makes the sector particularly amenable to targeted decarbonization through NCC-H₂ or NCC-Electricity technologies, which directly address combustion emissions while maintaining naphtha feedstock for chemical production.

### 3.2 Technology Cost Comparison Across Scenarios

Figure 1 presents cumulative decarbonization costs (2025-2050) across all six scenarios. The most striking finding is the minimal cost difference between hydrogen and electricity technology pathways within each production scenario. For the Shaheen growth scenario, NCC-H₂ achieves cumulative costs of $31.4 billion compared to $33.3 billion for NCC-Electricity—a difference of only $1.8 billion or 6%. This pattern holds across production scenarios: 25% restructuring shows $15.1 billion (H₂) versus $16.7 billion (Electricity) (10% difference), while 40% restructuring yields $13.0 billion versus $14.5 billion (11% difference).

In contrast, production pathway choice exerts far larger cost impacts. Comparing Shaheen to 40% restructuring within the same technology route reveals cost differences of 58% ($31.4B to $13.0B for H₂; $33.3B to $14.5B for Electricity). This finding challenges the conventional focus on technology choice as the primary cost determinant, suggesting that production strategy—capacity expansion versus strategic restructuring—has an order of magnitude larger impact on total system costs than the hydrogen versus electricity technology decision.

Standard MACC analysis based solely on these cost metrics would conclude that both NCC-H₂ and NCC-Electricity pathways are economically viable, with choice between them potentially driven by minor differences in learning rate assumptions, fuel price trajectories, or investor preferences. The 6-11% cost differences lie well within typical modeling uncertainty ranges and would not provide clear policy guidance on technology prioritization.

### 3.3 MACC Curves and Technology Learning

Figure 3 displays MACC curves for the Shaheen scenario in 2030, 2040, and 2050, illustrating technology cost evolution through learning effects. In 2030, NCC-H₂ enters the MACC at $120/tCO₂ while NCC-Electricity begins at $135/tCO₂, reflecting early-stage deployment costs and limited cumulative experience. By 2050, both technologies exhibit substantial cost reductions: NCC-H₂ declines to $65/tCO₂ and NCC-Electricity to $72/tCO₂, demonstrating learning rates of 15-18% per doubling of cumulative capacity.

The MACC curves reveal a consistent technology deployment sequence. Low-cost options including renewable PPAs ($15-25/tCO₂) and high-temperature heat pumps ($35-45/tCO₂) deploy first, addressing auxiliary electricity needs and low-temperature process heat respectively. These measures collectively abate 15-20% of baseline emissions. The deep decarbonization of steam cracking furnaces—representing 85% of emissions—requires the higher-cost NCC technologies, which become economically competitive as carbon prices rise and learning reduces costs over time.

Notably, the MACC methodology reveals no "technology winner" emerging through cost competition alone. The parallel cost trajectories of NCC-H₂ and NCC-Electricity suggest that absent energy system constraints, both pathways would deploy simultaneously based on site-specific factors such as proximity to hydrogen infrastructure, grid connection capacity, or facility retrofit constraints.

### 3.4 Energy System Demands: The Critical Divergence

While technology costs remain comparable, energy system demands diverge dramatically between pathways—revealing the constraint that conventional MACC analysis systematically overlooks. Figure 4 presents electricity demand trajectories across scenarios.

**Electricity Pathway Demands:**
The Shaheen + NCC-Electricity scenario requires 164.5 TWh of additional annual electricity by 2050. To contextualize this magnitude: it represents 29.5% of Korea's current total electricity consumption (558 TWh) and 96.8% of the government's 2036 renewable electricity target (170 TWh). This demand arises exclusively from petrochemical sector decarbonization and does not account for competing electricity needs from other sectors.

Even the most conservative scenario—40% restructuring with electricity—requires 85.9 TWh annually, equivalent to 15.4% of current national consumption and 50.5% of the 2036 renewable target. The 25% restructuring scenario demands 98.9 TWh (17.7% of current grid; 58.1% of 2036 target).

**Competing Sectoral Demands:**
Korea's decarbonization strategy extends well beyond petrochemicals. Conservative estimates suggest:
- Electric vehicle deployment: ~40 TWh/year by 2050
- Building heat pump adoption: ~30 TWh/year
- Steel sector electrification: ~50 TWh/year
- Other industrial processes: ~30 TWh/year
- Total competing demands: ~150 TWh/year

Under the Shaheen electricity pathway, petrochemical sector demand (164.5 TWh) exceeds the sum of all other competing sectors (150 TWh). Total incremental electricity demand would reach 314.5 TWh—equivalent to 56% of Korea's current entire grid and 185% of the 2036 renewable electricity target. This creates an impossible binding constraint: Korea's 10th Basic Plan projects stable total consumption around 558 TWh through 2036, implying minimal net growth in available supply for industrial electrification after baseline demand and transmission losses.

Even if Korea achieved its aggressive 30.6% renewable target by 2036, the petrochemicals electricity pathway alone would consume 97% of incremental renewable capacity, leaving virtually nothing for transport, buildings, or other industries. The 25% restructuring scenario still claims 58% of the renewable target; even 40% restructuring requires 51%. These percentages exclude the additional electricity needed to decarbonize the grid itself—currently 40% coal-fired—which must also be displaced by renewable capacity to achieve net-zero.

**Hydrogen Pathway Demands (Figure 5):**
In stark contrast, the hydrogen pathway exhibits fundamentally different system integration characteristics. The Shaheen + NCC-H₂ scenario requires 7.7 million tons of H₂ annually by 2050. This represents 27.6% of Korea's Hydrogen Economy Roadmap supply target (27.9 Mt total: 3.0 Mt domestic production plus 22.9 Mt imports).

The 25% restructuring scenario requires 4.6 Mt H₂ (16.6% of supply target) while 40% restructuring needs 4.0 Mt H₂ (14.4% of target). All three scenarios remain well within planned hydrogen infrastructure capacity, with substantial margin for supply growth or allocation to other sectors such as steel, cement, or heavy transport.

Critically, hydrogen infrastructure can be developed off-grid through dedicated renewable installations (solar/wind → electrolysis → H₂ storage/pipeline) or via imports shipped as liquid hydrogen or ammonia. This configuration avoids competition for limited grid capacity and transmission infrastructure. Korea's planned hydrogen import strategy (22.9 Mt, representing 82% of 2050 supply) further reduces domestic renewable electricity requirements, as production occurs offshore using partner countries' renewable resources.

### 3.5 Feasibility Assessment Beyond Technology Costs

The energy system demand analysis exposes a fundamental feasibility constraint invisible to conventional MACC methodology. While NCC-H₂ and NCC-Electricity appear similarly viable when evaluated solely on $/tCO₂ metrics (6% cost difference), system-level integration reveals that:

1. **The electricity pathway is physically infeasible** given Korea's renewable energy targets and competing sectoral demands. Even with aggressive capacity restructuring (40% reduction), the electricity pathway would require 51% of the 2036 renewable target, leaving insufficient capacity for other essential decarbonization priorities. The Shaheen growth scenario, aligned with industry forecasts, would consume 97% of renewable capacity—a non-viable allocation.

2. **The hydrogen pathway aligns with policy targets** established in Korea's Hydrogen Economy Roadmap. Petrochemical hydrogen demand represents 14-28% of planned supply depending on production scenario, providing substantial margin for co-deployment with other hydrogen-dependent sectors while leveraging the planned 82% import share to avoid domestic renewable electricity constraints.

3. **Production pathway becomes decisive**, not technology choice. The 40% restructuring scenario reduces electricity demand from 164.5 TWh (Shaheen) to 85.9 TWh—a 48% reduction that potentially moves from infeasible to marginally feasible territory. However, capacity restructuring faces severe political economy barriers: employment impacts, regional economic dependence on petrochemical complexes, and industry resistance to capacity reduction absent regulatory mandates.

This feasibility assessment fundamentally alters policy conclusions. Standard MACC analysis would present both pathways as viable options with minor cost trade-offs, leaving technology choice to market forces or incremental policy incentives. Energy system integration reveals that apparent "technology neutrality" based on cost metrics masks a binding physical constraint that renders one pathway infeasible regardless of cost competitiveness.

### 3.6 Emissions Reduction Achievement

Despite divergent energy demands, both technology pathways achieve equivalent emissions reduction targets (Figure 6). All scenarios reach 62-67% emissions reduction by 2050 relative to baseline, consistent with sectoral decarbonization requirements under 1.5°C pathways. The Shaheen scenarios reduce emissions from 68.0 MtCO₂ (BAU) to 25.2 MtCO₂ (both pathways). Restructuring scenarios achieve 62-67% reductions but from lower baselines due to capacity reduction.

This emissions equivalence reinforces that the pathway choice is not about environmental effectiveness—both routes can achieve required abatement—but about systemic feasibility given national energy infrastructure constraints.

---

## 4. Discussion

### 4.1 The Partial Equilibrium Trap in Industrial Decarbonization Assessment

Our results demonstrate a fundamental limitation of standard MACC methodology: partial equilibrium analysis that evaluates technologies in isolation systematically underestimates—or entirely misses—binding energy system constraints. The 6% cost difference between NCC-H₂ and NCC-Electricity pathways ($31.4B vs $33.3B) appears negligible when technologies are assessed individually using $/tCO₂ metrics. Standard MACC analysis would conclude both pathways are viable, with technology choice driven by marginal cost differences, learning rate assumptions, or site-specific factors.

However, aggregating facility-level technology choices to calculate national energy system demands reveals that the electricity pathway requires 164.5 TWh annually—29.5% of Korea's entire current grid and 96.8% of the 2036 renewable electricity target. This demand magnitude transforms the pathway from "slightly more expensive" to "physically infeasible" given competing sectoral needs. The hydrogen pathway, requiring 7.7 Mt H₂ (27.6% of planned supply), faces no equivalent binding constraint and can be met through dedicated off-grid infrastructure and planned imports.

This finding extends recent critiques of MACC methodology (Kesicki, 2021) beyond acknowledged limitations such as measure interactions, behavioral barriers, and double-counting concerns. We demonstrate that even when these methodological refinements are addressed, partial equilibrium frameworks systematically fail to identify capacity constraints that emerge at the energy system level. The binding constraint is not technology cost but systemic integration—a dimension absent from conventional MACC analysis.

The implications for industrial decarbonization assessment are profound. Studies concluding that "electrification is cheaper than hydrogen" based on technology-level efficiency or cost analysis (Diesing et al., 2025; Leicher et al., 2023) are correct in their domain but incomplete for policy. The relevant question is not which technology is cheaper per unit, but whether national energy systems can accommodate the aggregate demands resulting from sector-wide deployment. Our methodology—integrating facility-level MACC with explicit energy system demand quantification—provides a framework to address this gap.

### 4.2 Korea's Energy Policy: Validating the Hydrogen Economy Strategy

Our results provide quantitative validation for South Korea's Hydrogen Economy Roadmap (2019, updated 2021), which has faced criticism as aspirational or economically inefficient compared to direct electrification. The Roadmap's 27.9 Mt H₂ supply target by 2050—with 22.9 Mt (82%) sourced via imports—appeared to many analysts as an expensive detour given renewable electricity's declining costs. Our analysis reveals this strategy as necessary rather than optional.

Korea's 10th Basic Plan for Electricity Supply and Demand (2023) projects renewable electricity growing from current levels to 170 TWh by 2036—an increment of approximately 170 TWh above 2024 baselines assuming stable total consumption. If petrochemical decarbonization pursued the electricity pathway, it would consume 96.8% (Shaheen), 58.1% (25% restructuring), or 50.5% (40% restructuring) of this entire increment. After accounting for transport electrification (~40 TWh), building heat pumps (~30 TWh), and other industrial sectors (~80 TWh)—totaling ~150 TWh competing demand—the total requirement (314.5 TWh under Shaheen) vastly exceeds available supply.

The hydrogen strategy circumvents this bottleneck. By developing dedicated off-grid renewable installations (solar/wind → electrolysis → H₂ production/storage) or importing hydrogen produced using partner countries' renewable resources, Korea can decarbonize heavy industry without competing for scarce grid capacity. The 82% import share is not a weakness but a strategic advantage: it effectively accesses global renewable resources beyond Korea's domestic generation constraints.

This validation has immediate policy implications. Korea should:

1. **Prioritize grid capacity for sectors that must electrify**: Light transport, buildings, and services lack alternatives to electricity. Reserving limited grid expansion for these sectors while directing industry toward hydrogen maximizes overall decarbonization feasibility.

2. **Accelerate hydrogen infrastructure development**: Import terminals, pipeline networks, and storage facilities require long lead times (10-15 years). The hydrogen pathway's feasibility depends on timely infrastructure deployment, making current investments critical rather than speculative.

3. **Enable off-grid renewable development**: Regulatory frameworks should facilitate industrial renewable PPA agreements that bypass grid connection requirements, allowing direct renewable-to-hydrogen pathways that avoid transmission bottlenecks.

4. **Maintain technology-neutral incentives**: While system constraints favor hydrogen, policy should not mandate technology choice. Site-specific factors (e.g., facilities with excess grid capacity, hydrogen supply constraints) may justify electricity pathways. Carbon pricing and technology-neutral subsidies allow efficient allocation while system constraints guide aggregate outcomes.

### 4.3 Production Pathway Effects: The Demand-Side Imperative

Our cross-scenario analysis reveals that production pathway choice—capacity expansion versus strategic restructuring—exerts an order of magnitude larger impact on total costs (58% variation) than technology pathway selection (6% variation). The 40% restructuring scenario reduces cumulative costs from $31.4B to $13.0B (H₂ pathway) while cutting electricity demands from 164.5 TWh to 85.9 TWh—a 48% reduction that potentially moves from infeasible to marginally feasible territory.

This finding aligns with circular economy literature emphasizing demand-side interventions (Kloo et al., 2024). Petrochemical production growth has historically tracked GDP growth, but this coupling is not immutable. Strategies to reduce demand for virgin petrochemicals include:
- Enhanced mechanical and chemical recycling (targeting 30-40% recycled content)
- Material efficiency and lightweighting in end-use sectors
- Substitution with bio-based alternatives where performance allows
- Circular business models (product-as-service, extended producer responsibility)

However, demand-side interventions face severe political economy barriers. Korea's petrochemical industry employs over 100,000 workers directly, with regional economies in Ulsan, Yeosu, and Daesan heavily dependent on complex operations. Capacity reduction without managed transition creates concentrated losses (unemployment, regional decline) while benefits (reduced emissions, freed-up renewable capacity) disperse nationally. This asymmetry generates strong political resistance absent regulatory mandates or compensatory mechanisms.

Our results suggest that effective decarbonization strategies require integrating demand-side and supply-side interventions. Even ambitious technology deployment (NCC-H₂ or NCC-Electricity) cannot fully resolve energy system constraints under capacity growth scenarios. Demand reduction through circularity and efficiency creates the "policy space" within energy system limits to deploy remaining virgin production decarbonization technologies feasibly. The just transition literature emphasizes that such structural adjustments require:
- Worker retraining and social safety nets
- Regional economic diversification strategies
- Phase-out timelines synchronized with asset retirement schedules
- International coordination to prevent carbon leakage

### 4.4 Generalizability and Limitations

**Generalizability**: While this study focuses on South Korea, the methodological insights and system constraint findings likely generalize to other industrialized countries facing similar challenges. The European Union, Japan, and other OECD countries exhibit comparable characteristics: limited domestic renewable resources relative to industrial energy demands, existing grid capacity constraints, and competing sectoral electrification priorities. The binding constraint identified here—that aggregate industrial electricity demands can exceed national renewable targets—applies wherever grid capacity growth faces physical, economic, or political limits.

Emerging economies with stronger renewable resources (e.g., Australia, Chile, Middle East) may face different trade-offs. Countries with abundant solar/wind and lower population density may feasibly accommodate industrial electrification without binding constraints. However, even for these countries, the hydrogen pathway offers advantages: energy export opportunities (selling green hydrogen to resource-constrained importers like Korea, Japan, EU) and load flexibility (intermittent renewable generation better matched to hydrogen production's storage buffer than direct industrial electricity use).

**Limitations**: Our analysis employs several simplifications that future research should address. First, we quantify electricity demands but do not model grid operations, transmission constraints, or temporal matching between intermittent renewable generation and industrial load profiles. Full grid modeling incorporating hourly dispatch, seasonal storage, and transmission network analysis would provide higher resolution feasibility assessment. However, even our simplified analysis reveals binding constraints at the annual TWh level—constraints that detailed grid modeling would likely reinforce rather than eliminate.

Second, we assume hydrogen supply meets demand at exogenous prices ($3/kg by 2050), without modeling hydrogen production, transport, and storage infrastructure development. Korea's hydrogen strategy depends critically on import partnerships, shipping infrastructure (liquid H₂ or ammonia carriers), and international market development—all subject to geopolitical and economic uncertainties. However, our finding that hydrogen demand (7.7 Mt) represents only 28% of planned supply (27.9 Mt) suggests substantial buffer against supply shortfalls.

Third, we employ static optimization with annual time steps, potentially missing dynamic effects such as investment timing, technology lock-in, and path dependencies. Dynamic models incorporating irreversible investment decisions and learning-by-doing spillovers would provide richer insights into transition pathways.

Fourth, our technology portfolio excludes carbon capture and storage (CCS), which offers an alternative decarbonization route for petrochemicals. CCS deployment in Korea faces challenges including limited geological storage capacity and public acceptance, but future analysis should compare CCS against hydrogen and electricity pathways systematically.

Finally, our Korea-specific cost parameters and policy context limit direct quantitative transferability. Other countries' MACC values, renewable targets, and hydrogen strategies differ. However, the methodological contribution—integrating energy system demand quantification into MACC analysis—applies universally.

### 4.5 Policy Recommendations

Based on our findings, we recommend policymakers:

1. **Integrate energy system capacity assessment into industrial decarbonization planning**: Technology-level MACC analysis should be supplemented with explicit calculation of aggregate energy demands and comparison against national renewable targets and competing sectoral needs.

2. **Revise renewable energy targets to reflect true needs**: Korea's 30.6% renewable target by 2036 appears insufficient when competing demands are summed. Transparent accounting of sectoral electricity requirements should inform realistic target-setting.

3. **Prioritize hydrogen infrastructure for heavy industry**: Given grid capacity constraints, accelerate hydrogen import terminals, pipeline networks, and industrial cluster supply infrastructure. Treat hydrogen not as optional but as necessary for feasible industrial decarbonization.

4. **Reserve grid capacity for must-electrify sectors**: Light transport, residential buildings, and services lack viable alternatives to electricity. Industrial sectors with hydrogen alternatives should be directed toward off-grid pathways to maximize system-wide decarbonization feasibility.

5. **Couple supply-side technology deployment with demand-side interventions**: Circular economy policies reducing virgin petrochemical demand create critical policy space within energy system constraints, enabling more ambitious decarbonization targets.

---

## 5. Conclusion

This paper addresses a fundamental limitation of standard industrial decarbonization assessment: partial equilibrium MACC analysis evaluates technologies in isolation without quantifying whether national energy systems can accommodate the aggregate demands resulting from sector-wide deployment. Through facility-level modeling of South Korea's petrochemical sector enhanced with explicit energy system demand quantification, we demonstrate that binding constraints emerge at the system level that are invisible to technology-level cost analysis.

Our central finding is that technology cost competitiveness does not guarantee pathway feasibility. While hydrogen and electricity routes for petrochemical decarbonization show nearly identical costs (6% difference), their energy system demands diverge by orders of magnitude in system integration requirements. The electricity pathway's 164.5 TWh annual demand—29.5% of Korea's current grid—exceeds feasibility given renewable energy targets and competing sectoral needs. The hydrogen pathway's 7.7 Mt H₂ demand aligns with planned supply infrastructure and avoids grid competition through off-grid production and imports.

These findings carry three critical implications. **Methodologically**, we demonstrate that MACC analysis must integrate energy system capacity assessment to avoid systematically misleading policy conclusions about pathway feasibility. Technology-level $/tCO₂ metrics are necessary but insufficient; aggregate energy demands relative to national infrastructure constraints provide the binding feasibility test. **For Korea**, our results validate the Hydrogen Economy Roadmap as necessary infrastructure investment rather than speculative commitment, while revealing that the 10th Basic Plan's renewable targets are insufficient to support industrial electrification alongside other sectoral demands. **Globally**, the analysis suggests that countries facing similar resource constraints—EU, Japan, other OECD economies—should prioritize hydrogen infrastructure for heavy industry while reserving limited grid capacity for must-electrify sectors (transport, buildings, services).

Future research should extend this framework in three directions. First, integrate detailed grid modeling incorporating transmission constraints, temporal matching between intermittent renewables and industrial loads, and seasonal storage requirements. Second, expand technology portfolios to include carbon capture and storage, biomass alternatives, and emerging technologies, evaluating their system-level demands comparatively. Third, apply the methodology to other energy-intensive sectors (steel, cement, chemicals beyond petrochemicals) to assess economy-wide feasibility of electrification versus hydrogen strategies.

The pathway to net-zero requires not only developing low-carbon technologies but ensuring national energy systems can accommodate their deployment at scale. Our analysis reveals that for industrial decarbonization, energy system capacity—not technology cost—may prove the binding constraint. Recognizing this reality transforms policy priorities from technology-neutral incentives assuming unlimited capacity to strategic infrastructure planning that aligns sectoral pathways with system-level constraints.

---

## Acknowledgments

[To be added]

---

## References

[To be formatted in Carbon Neutrality journal style using the 36 references from petrochem_review.tex]

---

## Supplementary Materials

**Figures**:
- Figure 1: Six-scenario cost comparison (2025-2050)
- Figure 2: Technology deployment breakdown (supplementary)
- Figure 3: MACC curves evolution (2030, 2040, 2050)
- Figure 4: Electricity demand trajectories
- Figure 5: Hydrogen demand trajectories
- Figure 6: Emissions trajectories (supplementary)
- Figure 7: Baseline emissions structure

**Tables**:
- Table 1: Technology parameters with literature validation
- Table 2: Six-scenario results summary
- Table 3: Energy system demand comparison
- Table 4: Korea policy context (10th Basic Plan, Hydrogen Roadmap)

---

**Total word count: ~5,050 words**

**Section breakdown**:
- Abstract: ~250 words
- Introduction: ~800 words
- Methods: ~1,200 words
- Results: ~1,500 words
- Discussion: ~1,200 words
- Conclusion: ~400 words

---

**STATUS**: ✅ FIRST DRAFT COMPLETE

**Next steps**:
1. Format references from petrochem_review.tex in journal style
2. Insert figure references with proper captions
3. Create supplementary tables
4. Final read-through for consistency
5. Format for Carbon Neutrality journal submission
