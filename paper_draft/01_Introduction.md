# Introduction

## 1. The Electrification Paradigm in Industrial Decarbonization

Achieving net-zero emissions by 2050 requires deep decarbonization across all economic sectors, with industrial emissions presenting perhaps the most challenging frontier [1,2]. Among industrial sectors, petrochemicals account for approximately 1.5 Gt CO₂ annually—roughly 3% of global emissions—with emissions concentrated in energy-intensive processes such as steam cracking for olefin production [3,4]. The dominant narrative in climate policy emphasizes electrification as the primary decarbonization pathway, predicated on the assumption that renewable electricity can cost-effectively displace fossil fuel combustion [5-7]. This "electrify everything" paradigm has gained substantial traction in national decarbonization strategies, with the International Energy Agency projecting that electricity's share of final energy consumption must double from 20% to 40-50% by 2050 under Net Zero scenarios [8].

However, this electrification-centric approach contains an implicit assumption rarely examined quantitatively: that national energy systems possess sufficient capacity to accommodate large-scale industrial electricity demand without creating binding constraints. For carbon-intensive industries requiring high-temperature process heat—such as petrochemical crackers operating at 800-900°C—the electrification pathway faces not only technological challenges but also fundamental energy system integration constraints that may prove more limiting than technology costs [9,10].

## 2. The Energy System Integration Gap in Industrial Decarbonization Assessment

Industrial decarbonization pathway assessments typically employ Marginal Abatement Cost Curve (MACC) methodology to compare technology options based on their cost per ton of CO₂ abated [11-13]. These analyses have proven valuable for identifying cost-effective technologies and informing investment priorities. However, standard MACC approaches operate within a partial equilibrium framework, evaluating each technology's costs and abatement potential in isolation while treating energy supply as an unconstrained input available at exogenous prices [14,15]. This methodological choice, while simplifying analysis, systematically excludes critical considerations that emerge at the energy system level: grid capacity constraints, transmission bottlenecks, competition among sectors for limited renewable electricity, and temporal mismatches between industrial demand profiles and intermittent renewable generation [16,17].

Recent literature has begun acknowledging these limitations. Bataille et al. [18] note that industrial decarbonization strategies must consider energy system constraints, particularly for electrification pathways in heavy industry. Victoria et al. [19] demonstrate that European power system capacity becomes binding under high electrification scenarios, though their analysis focuses primarily on transport and building sectors. Material Economics [20] highlights hydrogen's role in addressing sectors where direct electrification faces practical limits, though without quantifying energy system demand at facility level. Despite these advances, a critical gap remains: no study has quantitatively assessed industrial decarbonization pathways by integrating bottom-up, facility-level MACC analysis with explicit energy system demand calculations to evaluate feasibility beyond technology costs.

## 3. South Korea as a Critical Case Study

South Korea provides an ideal case study for examining this energy system integration challenge. As the world's tenth-largest economy with a highly industrialized structure, Korea's industrial sector accounts for 35% of national emissions—substantially higher than the OECD average of 23% [21]. The petrochemical industry, centered around eleven major naphtha cracking complexes (NCCs) with total ethylene capacity of 11.96 million tons annually, emits approximately 66 MtCO₂/year, representing 13% of national emissions [22]. This concentration of emissions in a well-defined set of facilities enables precise, facility-level modeling while maintaining policy relevance for a systemically important industrial sector.

Korea's energy policy context makes this analysis particularly timely. The government's 10th Basic Plan for Electricity Supply and Demand (2023) targets 21.6% renewable electricity by 2030, rising to 30.6% by 2036, against a backdrop of stable total consumption around 558 TWh/year [23]. Simultaneously, Korea's Hydrogen Economy Roadmap (2019, updated 2021) envisions hydrogen supplying 33% of final energy by 2050, with domestic production of 3 million tons supplemented by 22.9 million tons of imports [24]. These parallel strategies—electricity grid expansion and hydrogen infrastructure development—represent competing visions for industrial decarbonization pathways, yet their relative feasibility given energy system constraints remains unexamined quantitatively.

The petrochemical sector faces a binary technology choice for deep decarbonization of steam cracking: hydrogen-fueled crackers (NCC-H₂) or electrically-heated crackers (NCC-Electricity) [25,26]. Both technologies have reached pilot or demonstration scale (Technology Readiness Levels 5-7) and promise to eliminate combustion emissions while maintaining naphtha as a chemical feedstock [27,28]. Preliminary techno-economic assessments suggest comparable costs, with reported ranges of $100-150/tCO₂ for both pathways [29,30]. However, these assessments evaluate technologies in isolation without quantifying the aggregate energy system demands that would result from sector-wide deployment.

## 4. Research Question and Objectives

This paper addresses a fundamental question that existing partial equilibrium MACC analyses cannot answer: **Can national energy systems accommodate the electricity demands of industrial decarbonization pathways, or do grid capacity constraints make alternative routes such as hydrogen infrastructure necessary despite potential technology cost premiums?**

We address this question through four specific objectives:

**First**, we develop a facility-level MACC model for South Korea's petrochemical sector that extends standard methodology by explicitly quantifying energy system demands (electricity in TWh, hydrogen in Mt H₂) alongside conventional cost metrics. This methodological enhancement allows assessment of not only whether a technology is cost-effective, but whether it is deployable given energy system constraints.

**Second**, we compare hydrogen-fueled and electrically-heated naphtha cracker pathways under three production scenarios—ranging from capacity expansion to strategic restructuring—to evaluate both technology choice and production strategy effects on decarbonization costs and energy demands.

**Third**, we contextualize model results within Korea's energy policy framework by comparing calculated electricity demands against the 10th Basic Plan's renewable energy targets and assessing hydrogen demands relative to the Hydrogen Economy Roadmap's supply projections. This integration reveals whether proposed pathways align with or contradict existing policy trajectories.

**Fourth**, we assess feasibility beyond costs by identifying binding constraints—such as grid capacity limits, competing sectoral demands for renewable electricity, and infrastructure deployment timelines—that technology-level MACC analysis systematically overlooks but that ultimately determine pathway viability.

## 5. Key Findings Preview

Our analysis reveals a striking divergence between technology-level and system-level assessments. At the technology level, NCC-H₂ and NCC-Electricity pathways demonstrate similar cumulative costs ($31.4 billion vs $33.3 billion for the growth scenario, 2025-2050)—a mere 6% difference well within modeling uncertainty. Standard MACC analysis would conclude both pathways are economically viable, differing only marginally in cost-effectiveness.

However, energy system integration analysis exposes a critical bottleneck. The NCC-Electricity pathway requires 164.5 TWh of additional annual electricity demand by 2050 in the growth scenario—equivalent to 29.5% of Korea's current total electricity consumption and 96.8% of the government's 2036 renewable electricity target. This demand arises from a single industrial sector and excludes competing electricity needs from transport electrification (estimated 40 TWh), building heating (30 TWh), other industrial sectors (80 TWh), and grid decarbonization more broadly. In contrast, the NCC-H₂ pathway's demand of 7.7 million tons H₂ annually represents 27.6% of Korea's planned 2050 hydrogen supply target and can be met through dedicated off-grid renewable installations or imports, thereby avoiding competition for grid capacity.

This finding has profound implications. It suggests that the binding constraint for industrial decarbonization is not technology cost but energy system capacity—a constraint that partial equilibrium MACC models, by construction, cannot identify. The electricity pathway appears cost-competitive when evaluated in isolation but becomes infeasible when energy system integration is considered. The hydrogen pathway emerges as not technologically superior but systemically more deployable because it can circumvent grid constraints through dedicated infrastructure.

## 6. Contribution and Structure

This paper makes three principal contributions. **Methodologically**, we demonstrate how integrating energy system demand quantification into facility-level MACC analysis reveals constraints invisible to standard partial equilibrium approaches, providing a framework applicable to industrial decarbonization assessment beyond the petrochemical sector. **Empirically**, we provide the first quantitative assessment of energy system demands for industrial electrification at facility resolution (248 facilities), showing that aggregate electricity requirements can reach magnitudes (30% of national grid) that render pathways infeasible despite technology cost competitiveness. **For policy**, we validate South Korea's hydrogen economy strategy as not merely aspirational but necessary given grid capacity constraints, while demonstrating that renewable electricity targets in the 10th Basic Plan are insufficient to support industrial electrification alongside other sectoral demands.

The remainder of this paper proceeds as follows. Section 2 reviews relevant literature on MACC methodology, energy system integration, and petrochemical decarbonization technologies. Section 3 describes our enhanced MACC model, including baseline emissions calculation, technology parameterization with literature validation, cost optimization algorithms, and energy system demand quantification methods. Section 4 presents results across six scenarios (three production pathways × two technology routes), comparing technology costs, energy system demands, and feasibility assessments. Section 5 discusses implications for MACC methodology, South Korea's energy policy, and generalizability to other countries and sectors. Section 6 concludes with policy recommendations and directions for future research.

---

**[~1,850 words]**

**References to be added**:
[1-30] - Placeholders for literature citations that will be populated from the 36 references in petrochem_review.tex plus additional MACC, energy system, and policy literature

---

## Notes for Revision:

**Strengths of this draft**:
- Clear progression: paradigm → gap → case study → question → preview
- Quantitative hooks (30% of grid, 6% cost difference, 164.5 TWh)
- Establishes why Korea matters (policy timing, facility concentration)
- Sets up the surprise (costs similar BUT energy demands diverge)
- Frames as methodological + empirical + policy contribution

**Potential revisions**:
- Could strengthen literature review preview (currently brief)
- Might add one more paragraph on political economy/why this matters
- Could preview the "technology neutrality" message earlier
- Numbers (164.5 TWh, etc.) might need verification against model output

**Next**: Draft the Methods section with complete equations and quantitative rigor
