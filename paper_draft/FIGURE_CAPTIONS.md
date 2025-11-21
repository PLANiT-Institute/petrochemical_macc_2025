# Figure Captions for Paper

## Main Text Figures

### Figure 1: Cumulative Decarbonization Costs Across Six Scenarios (2025-2050)

Bar chart comparing cumulative costs for six scenarios combining three production pathways (Shaheen growth, 25% restructuring, 40% restructuring) with two technology routes (NCC-H₂, NCC-Electricity). **Key finding**: Technology pathway choice shows minimal cost difference (6-11% variation: $31.4B vs $33.3B for Shaheen), while production pathway choice dominates total costs (58% variation: $31.4B to $13.0B for H₂ route). Error bars represent sensitivity to key parameters (H₂ price $2-6/kg, electricity price $40-80/MWh). Both pathways appear economically viable based on cost metrics alone, masking the binding energy system constraints revealed in Figure 4.

**Source**: Model output `/outputs/scenarios_comparison_6scenarios/summary.csv`

---

### Figure 3: Marginal Abatement Cost Curves for Shaheen Scenario (2030, 2040, 2050)

MACC curves showing technology cost evolution through learning effects for the Shaheen growth scenario. X-axis: cumulative abatement potential (MtCO₂); Y-axis: marginal cost ($/tCO₂). Each bar represents a technology: RE PPA (lowest cost, $15-25/tCO₂), Heat Pumps ($35-45/tCO₂), NCC-H₂ ($120→$65/tCO₂), NCC-Electricity ($135→$72/tCO₂). **Key observation**: Technology learning reduces both NCC options to similar costs by 2050 (~$70/tCO₂), with no clear "winner" emerging from cost competition. Parallel cost trajectories suggest both would deploy simultaneously absent system constraints. Learning rates of 15-18% per doubling of capacity are consistent with renewable energy technology experience.

**Source**: Model output `/outputs/scenarios_comparison_6scenarios/macc_curves/`

---

### Figure 4: Electricity Demand Trajectories by Scenario (2025-2050)

Line chart showing annual electricity demand requirements for six scenarios. **Critical finding**: Electricity pathways require 85.9-164.5 TWh/yr by 2050 depending on production scenario. Horizontal reference lines show Korea's total electricity consumption (558 TWh), 2036 renewable target (170 TWh), and competing sectoral demands (150 TWh cumulative). Shaheen + NCC-Electricity pathway (164.5 TWh) alone would consume 29.5% of current national grid and 96.8% of the 2036 renewable target—rendering the pathway physically infeasible given competing needs from transport (40 TWh), buildings (30 TWh), steel (50 TWh), and other industries (30 TWh). Even aggressive 40% restructuring requires 85.9 TWh (50.5% of renewable target). Shaded region indicates "feasible range" accounting for competing demands, showing all electricity pathways exceed system capacity.

**Source**: Model output `/outputs/scenarios_comparison_6scenarios/summary.csv`; Korea 10th Basic Plan (2023)

---

### Figure 5: Hydrogen Demand Trajectories by Scenario (2025-2050)

Line chart showing annual hydrogen demand requirements for six scenarios. Hydrogen pathways require 4.0-7.7 Mt H₂/yr by 2050 depending on production scenario. Horizontal reference lines show Korea's Hydrogen Economy Roadmap targets: domestic production (3.0 Mt/yr), imports (22.9 Mt/yr), and total supply (27.9 Mt/yr). **Key finding**: All H₂ scenarios remain well within planned infrastructure capacity, representing 14-28% of total supply target with substantial margin for co-deployment in steel, cement, heavy transport sectors. Shaheen + NCC-H₂ pathway (7.7 Mt) is 2.6× domestic production but only 28% of total supply when imports are included. Import strategy (82% of supply via liquid H₂ or ammonia carriers) enables feasibility by accessing global renewable resources beyond Korea's domestic constraints. Unlike electricity pathways, hydrogen demand does not create binding system constraints.

**Source**: Model output `/outputs/scenarios_comparison_6scenarios/summary.csv`; Korea Hydrogen Economy Roadmap (2019, updated 2021)

---

### Figure 7: Baseline Emissions Structure by Facility Type (2025)

Stacked bar chart showing emissions breakdown by facility type and emission source for the 248-facility baseline. Total sector emissions: 66.2 MtCO₂/yr (13% of Korea's national total). **Breakdown**: Naphtha cracking complexes (NCCs) account for 56.3 MtCO₂ (85%), with combustion emissions from steam cracking furnaces dominating (48.9 MtCO₂, 74% of total). Downstream facilities (polyethylene, polypropylene, aromatics) contribute 9.9 MtCO₂ (15%). Pie chart inset shows emission sources: combustion (85%), electricity (8%), flaring (4%), process emissions (3%). **Implication**: Concentration of emissions in NCC combustion justifies focus on furnace decarbonization technologies (NCC-H₂, NCC-Electricity) as primary abatement strategy. High concentration in three major complexes (Ulsan, Yeosu, Daesan: 70% of capacity) simplifies infrastructure deployment planning.

**Source**: Korea National GHG Inventory (2022); model baseline calculation

---

## Supplementary Figures

### Figure 2: Technology Deployment Mix by Scenario (2050)

Pie charts showing technology deployment breakdown for each of six scenarios in 2050. Each pie shows capacity allocation (Mt ethylene equivalent) across four technologies: NCC-H₂/NCC-Electricity (dominant, 70-75%), RE PPA (20-22%), Heat Pumps (8-10%), remaining baseline (<5%). **Observation**: Technology mix is remarkably similar across scenarios, with primary technology (H₂ vs Electricity) consistently capturing 70-75% of deployment. This similarity reinforces that cost-optimal technology choice converges regardless of production pathway, and that differences in energy system demands (not technology mix) drive feasibility divergence. Provides visual confirmation that all scenarios achieve deep decarbonization (>60% reduction) through similar technology portfolios.

**Source**: Model output `/outputs/scenarios_comparison_6scenarios/technology_deployment/`

---

### Figure 6: Emissions Trajectories by Scenario (2025-2050)

Line chart showing annual emissions for six scenarios compared to business-as-usual baselines. BAU trajectories diverge based on production pathway: Shaheen (68.0 MtCO₂), 25% restructuring (40.9 MtCO₂), 40% restructuring (35.5 MtCO₂) by 2050. All decarbonization scenarios converge to similar endpoints regardless of technology pathway: Shaheen scenarios reach 25.2 MtCO₂ (63% reduction), 25% restructuring reaches 15.6 MtCO₂ (62% reduction), 40% restructuring reaches 11.8 MtCO₂ (67% reduction). **Key message**: Both technology pathways achieve equivalent environmental outcomes—emissions reduction is not the differentiator. Pathway choice is determined by systemic feasibility (energy system capacity constraints), not environmental effectiveness. Shaded regions show uncertainty bounds from sensitivity analysis.

**Source**: Model output `/outputs/scenarios_comparison_6scenarios/emissions_trajectories/`

---

## Figure Specifications

**All figures**:
- Resolution: 300 DPI minimum
- Format: PNG (for review), PDF (for final submission)
- Color scheme: Colorblind-friendly palette (blue-orange for H₂ vs Electricity comparisons)
- Font: Arial or Helvetica, 10-12pt for labels, 8-10pt for axis labels
- Size: Single column (3.5 inches width) or double column (7 inches width) as appropriate

**Color coding consistency**:
- NCC-H₂ pathways: Blue (#1f77b4)
- NCC-Electricity pathways: Orange (#ff7f0e)
- RE PPA: Green (#2ca02c)
- Heat Pumps: Purple (#9467bd)
- Baseline/BAU: Gray (#7f7f7f)
- Reference lines (policy targets): Red dashed (#d62728)

**Data availability**: All figure data available in `/outputs/paper_figures/` and `/outputs/scenarios_comparison_6scenarios/`

---

## Figure Placement Recommendations

**Main text**:
- Figure 1: Early Results section (3.2) - establishes cost comparison
- Figure 3: Mid Results section (3.3) - shows MACC methodology
- Figure 4: Key Results section (3.4) - **main finding on electricity constraint**
- Figure 5: Key Results section (3.4) - hydrogen alternative feasibility
- Figure 7: Early Results section (3.1) - provides baseline context

**Supplementary**:
- Figure 2: Technology deployment details
- Figure 6: Emissions trajectories validation

**Suggested figure order in text**:
1. Figure 7 (baseline) - context
2. Figure 1 (costs) - main result #1: costs close
3. Figure 3 (MACC) - methodology validation
4. Figure 4 (electricity) - **main result #2: demand huge**
5. Figure 5 (hydrogen) - alternative pathway feasible

This ordering builds narrative: baseline → costs appear similar → methodology sound → but demands diverge → hydrogen feasible.

---

**Total: 7 figures** (5 main text, 2 supplementary)
