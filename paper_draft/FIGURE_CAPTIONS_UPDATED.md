# Updated Figure Captions for Paper

**Date**: 2025-11-11
**Status**: Updated to match new figure designs (especially Figure 3)

---

## Main Text Figures

### Figure 1: Cumulative Decarbonization Costs Across Six Scenarios (2025-2050)

Bar chart comparing cumulative costs for six scenarios combining three production pathways (Shaheen growth, 25% restructuring, 40% restructuring) with two technology routes (NCC-H₂, NCC-Electricity). **Key finding**: Technology pathway choice shows minimal cost difference (6-11% variation: $31.4B vs $33.3B for Shaheen scenario), while production pathway choice dominates total costs (58% variation: $31.4B to $13.0B for H₂ route). Both pathways appear economically viable based on cost metrics alone, setting up the paradox revealed in subsequent figures where similar costs mask divergent energy system demands.

---

### Figure 3: MACC Comparison for Hydrogen and Electricity Pathways (2050, Shaheen Scenario)

**NEW DESIGN**: Side-by-side horizontal bar MACC curves comparing (a) Hydrogen pathway and (b) Electricity pathway for the Shaheen growth scenario in 2050. Both panels show identical supporting technologies—RE PPA at $20/tCO₂ and Heat Pumps at $40/tCO₂—followed by primary NCC technologies: NCC-H₂ at $65/tCO₂ versus NCC-Electricity at $72/tCO₂. Total cumulative costs displayed in panel titles: $31.4B (H₂) vs $33.3B (Electricity). **Main title emphasizes**: "MACC Curves Show Similar Costs BUT Cannot Reveal Energy System Constraints." **Key message**: From conventional MACC perspective, both pathways appear economically viable with marginal cost difference of 10%. This similarity creates the paradox—technologies that are cost-competitive individually become infeasible at system level due to aggregate energy demands invisible to partial equilibrium analysis.

---

### Figure 4: Electricity Demand Trajectories by Scenario (2025-2050)

Bar chart showing annual electricity demand requirements for three scenarios in 2050: Shaheen (164.5 TWh), 25% Restructuring (98.9 TWh), and 40% Restructuring (85.9 TWh). Horizontal reference lines show Korea's total electricity consumption (558 TWh), 2036 renewable target (170 TWh), and competing sectoral demands (~150 TWh cumulative). **Critical finding**: Shaheen + NCC-Electricity pathway alone would consume 29.5% of current national grid and 96.8% of the 2036 renewable target—rendering the pathway physically infeasible given competing needs from transport (40 TWh), buildings (30 TWh), steel (50 TWh), and other industries (30 TWh). Red warning box highlights: "BINDING CONSTRAINT: Even 40% restructuring requires 51% of renewable target." Even aggressive capacity reduction cannot resolve the fundamental grid capacity bottleneck.

---

### Figure 5: Hydrogen Demand Trajectories by Scenario (2025-2050)

Bar chart showing annual hydrogen demand requirements for three scenarios in 2050: Shaheen (7.7 Mt H₂), 25% Restructuring (4.6 Mt H₂), and 40% Restructuring (4.0 Mt H₂). Horizontal reference lines show Korea's Hydrogen Economy Roadmap targets: total supply (27.9 Mt/yr), import capacity (22.9 Mt/yr, 82% of supply), and domestic production (3.0 Mt/yr). **Key finding**: All H₂ scenarios remain well within planned infrastructure capacity, representing 14-28% of total supply target with substantial margin for co-deployment in steel, cement, and transport sectors. Green success box highlights: "FEASIBLE: Substantial margin for co-deployment with other sectors." Import strategy (82% of supply via liquid H₂ or ammonia carriers) enables feasibility by accessing global renewable resources beyond Korea's domestic grid constraints. Unlike electricity pathways, hydrogen demand does not create binding system constraints.

---

### Figure 7: Baseline Emissions Structure (2025)

Two-panel figure showing (a) emissions by facility type and (b) emissions by source for the 248-facility baseline. Total sector emissions: 66.2 MtCO₂/yr (13% of Korea's national total). Panel (a) shows Naphtha Cracking Complexes (NCCs) account for 85% of emissions, with downstream facilities (polyethylene, polypropylene, aromatics) contributing 15%. Panel (b) shows emission sources: combustion from steam cracking furnaces (85%), electricity (8%), flaring (4%), process emissions (3%). **Implication**: Concentration of emissions in NCC combustion justifies focus on furnace decarbonization technologies (NCC-H₂, NCC-Electricity) as primary abatement strategy. High concentration in three major complexes (Ulsan, Yeosu, Daesan: 70% of capacity) simplifies infrastructure deployment planning.

---

## Supplementary Figures

### Figure S1: Technology Deployment Mix by Scenario (2050)

Three pie charts showing technology deployment breakdown for hydrogen pathway scenarios in 2050: Shaheen + H₂ (42.8 Mt total abatement), 25% Restructuring + H₂ (23.3 Mt), and 40% Restructuring + H₂ (23.7 Mt). Each pie shows capacity allocation across four technologies: NCC-H₂ (dominant, 72-68%), RE PPA (19-23%), Heat Pumps (8-9%). **Observation**: Technology mix is remarkably consistent across scenarios despite different production pathways, with NCC-H₂ consistently capturing 70-75% of deployment. This consistency reinforces that cost-optimal technology choices converge regardless of production pathway, and that differences in energy system demands (not technology mix) drive feasibility divergence between hydrogen and electricity routes.

---

### Figure S2: Emissions Trajectories by Scenario (2025-2050)

Line chart showing annual emissions for all scenarios compared to business-as-usual baselines. Three dashed BAU trajectories diverge based on production pathway: Shaheen (68.0 MtCO₂ by 2050), 25% restructuring (40.9 MtCO₂), 40% restructuring (35.5 MtCO₂). Solid decarbonization pathway (bold red line) shows all scenarios converge to similar endpoints: Shaheen reaches 25.2 MtCO₂ (63% reduction), 25% restructuring reaches 15.6 MtCO₂ (62% reduction), 40% restructuring reaches 11.8 MtCO₂ (67% reduction). **Key message**: Both hydrogen and electricity technology pathways achieve equivalent environmental outcomes—emissions reduction is not the differentiator between pathways. Pathway choice is determined by systemic feasibility (energy system capacity constraints), not environmental effectiveness or emissions reduction potential.

---

## For LaTeX Manuscript

Use these captions in the figure environment:

```latex
\begin{figure}[htbp]
\centering
\caption{\textbf{Cumulative Decarbonization Costs Across Six Scenarios (2025-2050).}
Bar chart showing technology pathway costs (H₂ vs Electricity) across three production
scenarios. Technology choice shows 6-11% cost variation while production pathway choice
shows 58% variation. Both technology pathways appear economically viable based on cost
metrics, setting up the paradox where similar costs mask divergent energy demands.}
\label{fig:costs}
\end{figure}

\begin{figure}[htbp]
\centering
\caption{\textbf{MACC Comparison for Hydrogen and Electricity Pathways (2050).}
Side-by-side comparison of marginal abatement cost curves for (a) hydrogen pathway
($31.4B total) and (b) electricity pathway ($33.3B total) in Shaheen scenario. Both
show identical supporting technologies (RE PPA $20/tCO₂$, Heat Pumps $40/tCO₂$) with
primary NCC technologies at $65/tCO₂$ (H₂) vs $72/tCO₂$ (Electricity). Conventional
MACC analysis suggests both pathways viable, but cannot reveal energy system constraints.}
\label{fig:macc}
\end{figure}

\begin{figure}[htbp]
\centering
\caption{\textbf{Electricity Demand Requirements (2050).}
Annual electricity demands by scenario: 164.5 TWh (Shaheen), 98.9 TWh (25% restructuring),
85.9 TWh (40% restructuring). Reference lines show Korea's grid (558 TWh), 2036 renewable
target (170 TWh), and competing sectors (150 TWh). Shaheen pathway consumes 97% of
renewable target, rendering electricity pathway physically infeasible given competing
sectoral demands.}
\label{fig:electricity}
\end{figure}

\begin{figure}[htbp]
\centering
\caption{\textbf{Hydrogen Demand Requirements (2050).}
Annual hydrogen demands by scenario: 7.7 Mt (Shaheen), 4.6 Mt (25% restructuring),
4.0 Mt (40% restructuring). Reference lines show Korea's H₂ targets: 27.9 Mt total
supply (3.0 Mt domestic, 22.9 Mt imports). All scenarios remain within 14-28% of
supply target with substantial margin for co-deployment. Import strategy avoids
grid constraints.}
\label{fig:hydrogen}
\end{figure}

\begin{figure}[htbp]
\centering
\caption{\textbf{Baseline Emissions Structure (2025).}
Two-panel breakdown showing (a) emissions by facility type: NCCs 85%, downstream 15%;
and (b) emissions by source: combustion 85%, electricity 8%, flaring 4%, process 3%.
Total sector: 66.2 MtCO₂/yr (13% of national emissions). Concentration in NCC combustion
justifies focus on furnace decarbonization technologies.}
\label{fig:baseline}
\end{figure}
```

---

## Key Changes from Previous Version

1. **Figure 3**: Completely updated to describe NEW DESIGN (side-by-side comparison, not time series)
2. **All captions**: Emphasize the narrative arc (costs similar → but demands diverge → electricity infeasible, hydrogen feasible)
3. **Added main title**: Each caption starts with key message
4. **LaTeX format**: Provided ready-to-paste figure environments with labels

---

**Total: 7 figures** (5 main text, 2 supplementary)
**All captions now match the actual generated figures**
