# Paper Draft Plan for Carbon Neutrality Journal

**Target Journal**: Carbon Neutrality (Springer)
**Paper Type**: Original Research Article
**Target Length**: 8,000-10,000 words
**Date**: 2025-11-11

---

## Paper Title

**Proposed**:
"Comparative Techno-Economic Analysis of Carbon Neutrality Pathways for South Korea's Petrochemical Industry: Hydrogen versus Electrification Routes under Production Transition Scenarios"

**Alternative** (shorter):
"Carbon Neutrality Pathways for Korea's Petrochemical Industry: A Six-Scenario Comparative Analysis of Hydrogen and Electrification Routes"

---

## Critical Figures Required (8-10 total)

### **MUST HAVE Figures** (Priority 1):

1. **Figure 1: Baseline Emissions Structure (2025)**
   - Type: Stacked bar chart or Sankey diagram
   - Shows: 248 facilities by product group, process type, region
   - Data: From `outputs/module_01/baseline_2025_by_product.png`
   - Purpose: Establish problem scale (52 MtCO₂)

2. **Figure 2: Six-Scenario Cost Comparison (2050)**
   - Type: Grouped bar chart
   - Shows: Total cost for all 6 scenarios
   - X-axis: 3 production pathways (40%, 25%, Shaheen)
   - Groups: NCC-H₂ vs NCC-Elec
   - Data: Updated results from scenarios_comparison_6scenarios/
   - **KEY FIGURE** - Shows cost parity after H₂ update!

3. **Figure 3: Technology Pathway Comparison (Shaheen)**
   - Type: Side-by-side comparison charts
   - Left panel: NCC-H₂ (cost breakdown, H₂ demand)
   - Right panel: NCC-Elec (cost breakdown, electricity demand)
   - Purpose: Show infrastructure requirements

4. **Figure 4: MACC Curve Snapshots (2030 & 2050)**
   - Type: Classic MACC step chart
   - Shows: 4 technologies ranked by $/tCO₂
   - Two panels: 2030 and 2050 side-by-side
   - Data: `outputs/module_02/macc_curve_2030.png`, `macc_curve_2050.png`
   - Purpose: Show technology cost evolution

5. **Figure 5: Regional Renewable Energy Deployment (2025-2050)**
   - Type: Stacked area chart
   - Shows: RE deployment timeline for Ulsan, Yeosu, Daesan, Incheon
   - Stacks: NCC-Elec RE vs Grid→RE
   - Data: From regional analysis
   - Purpose: Show infrastructure build-out trajectory

6. **Figure 6: Scenario Deployment Timeline (Shaheen + NCC-Elec)**
   - Type: Stacked area chart showing abatement over time
   - Shows: Technology deployment 2025-2050
   - Stacks: Heat Pump, RE PPA, NCC-Elec
   - Y-axis: Cumulative abatement (Mt CO₂)
   - Purpose: Show transition pathway

### **SHOULD HAVE Figures** (Priority 2):

7. **Figure 7: Unit Abatement Cost Comparison**
   - Type: Box plot or violin plot
   - Shows: $/tCO₂ distribution across 6 scenarios
   - Groups: Production pathways
   - Colors: NCC-H₂ vs NCC-Elec
   - Purpose: Show cost stability despite scenario variation

8. **Figure 8: Hydrogen vs Electricity Infrastructure Trade-offs**
   - Type: Scatter plot
   - X-axis: H₂ demand (kt/yr)
   - Y-axis: Electricity demand (TWh/yr)
   - Points: 6 scenarios
   - Purpose: Show infrastructure implications

### **NICE TO HAVE Figures** (Priority 3):

9. **Figure 9: Sensitivity Analysis**
   - Type: Tornado diagram
   - Shows: Impact of key parameters (H₂ price, electricity price, CAPEX) on cost gap
   - Purpose: Show robustness of findings

10. **Figure 10: Cumulative Investment Timeline**
    - Type: Line chart
    - Shows: Cumulative CAPEX over time for 3 main scenarios
    - Purpose: Show investment timing

---

## Critical Tables Required (6-8 total)

### **MUST HAVE Tables** (Priority 1):

1. **Table 1: Six-Scenario Summary (Updated Results)**
   - Columns: Scenario | BAU Emissions | Total Cost | Unit Cost | H₂/Elec Demand
   - 6 rows (one per scenario)
   - **MOST IMPORTANT TABLE** - Shows new cost parity!
   - Location in paper: Results Section 4.3

2. **Table 2: Technology Parameter Summary**
   - Shows: All 4 technologies with CAPEX, OPEX, energy requirements, TRL
   - Include: OLD vs NEW values with literature sources
   - Purpose: Document parameter validation
   - Location: Methods Section 3.3

3. **Table 3: NCC-H₂ vs NCC-Electricity Comparison**
   - Rows: Cost, H₂/Elec demand, Infrastructure, TRL, Risk
   - Columns: NCC-H₂ | NCC-Elec | Assessment
   - Purpose: Direct pathway comparison
   - Location: Results Section 4.4

4. **Table 4: Regional Renewable Energy Requirements (2050)**
   - Rows: 4-5 major regions
   - Columns: NCC-Elec RE | Grid→RE | Total | % Share
   - Data: From Shaheen + NCC-Elec scenario
   - Location: Results Section 4.5

### **SHOULD HAVE Tables** (Priority 2):

5. **Table 5: Baseline Emissions by Sector (2025)**
   - Rows: Product groups (Olefins, Aromatics, etc.)
   - Columns: Facilities | Emissions | Fuel Mix
   - Purpose: Baseline characterization
   - Location: Results Section 4.1

6. **Table 6: MACC Snapshot (2030)**
   - Rows: 4 technologies
   - Columns: Abatement Potential | CAPEX component | OPEX component | Energy cost | Total ($/tCO₂)
   - Location: Results Section 4.2

7. **Table 7: Literature Parameter Comparison**
   - Shows: Your values vs literature ranges for each technology
   - Purpose: Validation transparency
   - Location: Methods or Appendix

8. **Table 8: Policy Milestones (Shaheen Scenarios)**
   - Rows: Years (2025, 2030, 2035, 2040, 2045, 2050)
   - Columns: Emissions | Tech deployment | Cumulative investment
   - Both NCC-H₂ and NCC-Elec pathways side-by-side

---

## Paper Structure (Detailed Outline)

### **Abstract** (350 words max)

**Structure**:
1. Background (2 sent): Korea petrochemical emissions, carbon neutrality goal
2. Objective (1 sent): Compare 6 scenarios (3 production × 2 technology)
3. Methods (3 sent): Facility-level MACC, 248 plants, 4 technologies, optimization
4. Results (4-5 sent):
   - Cost range $27.5-60B
   - NCC-H₂ and NCC-Elec have similar costs after literature validation
   - Regional infrastructure requirements
5. Conclusion (2 sent): NCC-Electricity recommended based on sustainability when costs are comparable

**Key numbers to include**:
- 248 facilities, 52 MtCO₂ baseline
- 6 scenarios: 3 production × 2 technology
- Cost range: $27.5-60B
- H₂ demand: 50-88 kt/yr (NCC-H₂ pathways)
- Electricity: 178-298 TWh/yr (NCC-Elec pathways)
- Unit cost stability: $774-873/tCO₂

---

### **1. Introduction** (~1,500 words)

**1.1 Background & Motivation** (3 paragraphs)
- Global petrochemical emissions (1.3 GtCO₂, 3-4% of global)
- Korea's position (52 MtCO₂, 7% national, world-class clusters)
- 2050 carbon neutrality commitment, 10th Basic Electricity Plan

**1.2 Literature Gap** (2 paragraphs)
- Previous studies: single pathway focus, aggregate sector-level
- Missing: facility-level comparative analysis, production scenarios
- Korea-specific gap: no comprehensive analysis with regional detail

**1.3 Research Questions** (1 paragraph)
1. What are facility-level baseline emissions and fuel balances?
2. How do hydrogen vs electricity pathways compare economically?
3. What is the cost-emissions tradeoff between production growth vs restructuring?
4. What are optimal strategies for Korea's 2050 carbon neutrality?

**1.4 Novel Contributions** (1 paragraph)
1. First facility-level (248 plants) comparative MACC for Korea
2. Systematic 6-scenario analysis (production × technology)
3. Energy-explicit methodology with transparent cost accounting
4. Regional RE deployment planning (Ulsan, Yeosu, Daesan, Incheon)

**1.5 Paper Roadmap** (1 paragraph)

---

### **2. Literature Review** (~2,000 words)

**[Can be largely copied from petrochem_review.tex]**

**2.1 Petrochemical Industry Decarbonization** (400 words)
- Global emissions and pathways (SBTi 2022, IEA 2023, Kloo 2024)
- Key studies and findings
- Technology options overview

**2.2 Asia-Pacific Petrochemical Decarbonization** (400 words)
- Regional context (GESI 2024, RMI 2022, Li 2023)
- Korea-specific situation (InvestKorea 2023)
- Infrastructure challenges

**2.3 Hydrogen versus Electrification Pathways** (400 words)
- Comparative analyses (Diesing 2025, Leicher 2023, Wattanasoponvanij 2025)
- Cost comparisons
- Infrastructure implications

**2.4 MACC Methodology in Industrial Applications** (400 words)
- MACC applications (Cederschiold 2020, Chen 2019 Taiwan, Kesicki 2021)
- Methodological considerations
- Best practices

**2.5 Korea's Carbon Neutrality Policy Context** (200 words)
- 2050 roadmap
- 10th Basic Electricity Plan
- K-ETS and industrial policies

**2.6 Research Gap & Study Positioning** (200 words)
- Gaps in existing literature
- How this study addresses them

---

### **3. Methodology** (~2,500 words)

**3.1 Overview** (200 words)
- 4-module framework: Baseline → MACC → Optimization → Analysis
- Energy-explicit approach
- Scenario framework overview

**3.2 Data Sources and Facility Inventory** (400 words)
- 248 facilities from KEEI 2023 statistics
- Energy intensities by process type
- Regional distribution
- Table 5: Baseline emissions by sector

**3.3 Technology Parameters** (500 words)
- 4 technologies: Heat Pump, RE PPA, NCC-Elec, NCC-H₂
- Literature validation (updated parameters)
- Table 2: Technology parameter summary
- Table 7: Literature comparison

**3.4 MACC Framework** (400 words)
- Energy-based cost formulation (keep existing equations from main.tex)
- Equations 1-5: Energy balance, abatement calculation, cost components
- Simple annualization approach (no discounting rationale)

**3.5 Scenario Design** (500 words) **[NEW SECTION]**
- **Production pathways**:
  - Shaheen (growth): Current capacity maintained, BAU growth to 2050
  - 25% restructuring: Capacity reduction, emissions 40.9 Mt by 2050
  - 40% restructuring: Deep capacity reduction, emissions 35.5 Mt by 2050
- **Technology pathways**:
  - NCC-Electricity: 100% RE-powered electric crackers
  - NCC-H₂: Green hydrogen-fueled crackers
- **6-scenario matrix**: 3 × 2 combinations
- Rationale for each scenario

**3.6 Optimization Model** (500 words)
- Linear programming formulation (keep from main.tex)
- Objective function: minimize undiscounted abatement cost
- Constraints: irreversibility, technology availability, mutual exclusivity
- Target: Net-zero by 2050 for each production pathway

---

### **4. Results** (~3,000 words)

**4.1 Baseline Characterization** (400 words)
- 248 facilities, 52.0 MtCO₂ in 2025
- Figure 1: Baseline emissions structure
- Table 5: Emissions by product group
- Key insight: Olefins (steam crackers) = 90% of emissions

**4.2 Technology MACC Analysis** (500 words)
- Figure 4: MACC curves 2030 & 2050
- Table 6: MACC snapshot 2030
- Cost evolution 2025-2050
- Technology ranking: HP < RE PPA < NCC-Elec < NCC-H₂ (2030)
- Convergence by 2050

**4.3 Six-Scenario Comparison** (800 words) **[MAIN RESULTS]**
- **Table 1: Six-scenario summary** - THE KEY TABLE
- **Figure 2: Cost comparison** - THE KEY FIGURE
- Production pathway analysis:
  - 40% restructuring: $27.5-30.2B (lowest cost)
  - 25% restructuring: $32.2-35.4B (mid-range)
  - Shaheen (growth): $53.9-60B (highest cost, largest abatement)
- Technology pathway comparison:
  - NCC-H₂ and NCC-Elec show **cost parity** (updated finding!)
  - Cost gap <2% after H₂ consumption correction
  - Unit costs stable: $774-873/tCO₂ across scenarios

**Key finding**: Production scenarios matter MORE than technology choice for total cost

**4.4 Technology Pathway Comparison** (600 words) **[CRITICAL ANALYSIS]**
- Figure 3: NCC-H₂ vs NCC-Elec side-by-side
- Table 3: Direct comparison
- **Updated narrative with cost parity**:
  - Similar costs (~$58-60B for Shaheen)
  - Infrastructure trade-offs: 88 kt H₂ vs 298 TWh electricity
  - Supply chain considerations
  - Technology maturity (TRL 5 vs 7)
- **Conclusion**: When costs are equal, sustainability and infrastructure co-benefits favor NCC-Electricity

**4.5 Regional Renewable Energy Requirements** (400 words)
- Figure 5: Regional RE deployment timeline
- Table 4: 2050 regional requirements
- Major findings:
  - Ulsan: 74.5 TWh (~28 GW capacity needed)
  - Yeosu/Gwangyang: 67.6 TWh (~26 GW)
  - Daesan: 58.6 TWh (~22 GW)
  - Total: 317 TWh (~120 GW by 2050)

**4.6 Deployment Timeline Analysis** (300 words)
- Figure 6: Technology deployment pathway (Shaheen + NCC-Elec)
- Phased approach: RE PPA → NCC-Elec → Heat Pumps
- Investment timing and milestones

---

### **5. Discussion** (~2,000 words)

**5.1 Technology Pathway Trade-offs** (500 words)
- Cost parity finding (main result from updated parameters)
- Why NCC-Electricity despite similar cost:
  - Infrastructure co-benefits (RE useful beyond petrochemicals)
  - Supply chain security (domestic RE vs imported H₂)
  - Technology maturity (TRL 7 vs 5)
  - Long-term cost trajectory (electricity declining faster)
- When would NCC-H₂ be preferred?
  - If H₂ price < $2.5/kg
  - If electricity constraints persist
  - For hybrid/flexible operation

**5.2 Production Scenario Implications** (400 words)
- Economic impact of restructuring
- Global competitiveness considerations
- Employment and GDP effects
- Timing and transition management
- Political economy factors

**5.3 Policy Recommendations** (600 words)
- **Main recommendation**: Shaheen + NCC-Electricity
  - Despite highest cost, maintains production capacity
  - RE infrastructure benefits entire economy
  - Aligns with national energy transition
- **3-phase roadmap** (from Korean report):
  - Phase 1 (2025-2030): Pilots, early RE deployment
  - Phase 2 (2030-2040): Commercial scale-up, major RE build-out
  - Phase 3 (2040-2050): Complete transition, 120 GW RE
- **Government support needs**:
  - RE infrastructure investment (120 GW)
  - NCC-Electricity R&D and commercialization
  - Carbon pricing and green finance
  - Industrial transition support (employment, SMEs)

**5.4 Comparison with International Studies** (400 words)
- How costs compare with EU, US, China studies
- Korea-specific factors (energy import dependence, manufacturing economy)
- Transferability to other countries

**5.5 Uncertainty and Sensitivities** (100 words)
- Key uncertainties: H₂ price, electricity costs, technology learning
- Need for adaptive policy framework

---

### **6. Limitations** (~500 words)

**[Keep existing + add new items]**

1. Simple annualization without discounting (WACC 5-8% would change ordering)
2. Deterministic price trajectories (no stochastic modeling)
3. No spatial constraints (pipeline routing, grid capacity)
4. Feedstock emissions excluded (focus on combustion only)
5. No circular economy pathways (chemical recycling)
6. Static demand assumption (no demand reduction scenarios)
7. **H₂ consumption uncertainty** (0.50-0.65 range, used 0.56 mean)
8. Technology learning rates uncertain (CAPEX ±30%)

---

### **7. Conclusion** (~500 words)

**[Rewrite to emphasize updated findings]**

**7.1 Summary of Findings** (3 paragraphs)
1. Six-scenario analysis shows cost range $27.5-60B
2. **NCC-H₂ and NCC-Elec have similar costs** after literature validation (~$58-60B for Shaheen)
3. **Key insight**: When costs are comparable, sustainability considerations favor NCC-Electricity
4. Regional infrastructure planning critical: 120 GW RE by 2050

**7.2 Main Contributions** (1 paragraph)
- First comprehensive facility-level 6-scenario analysis for Korea
- Literature-validated parameters increase credibility
- Energy-explicit methodology ensures transparency
- Regional deployment planning provides actionable roadmap

**7.3 Policy Implications** (1 paragraph)
- NCC-Electricity pathway recommended despite similar cost
- Requires coordinated policy: RE build-out + technology support + finance
- 3-phase transition roadmap provided

**7.4 Future Research** (1 paragraph)
- Integration with circular economy
- Hybrid H₂/electricity pathways
- Spatial optimization with network constraints
- Stochastic modeling for price uncertainty

---

## Supporting Materials

### **Supplementary Information** (separate file)
1. Complete facility database (248 facilities)
2. Detailed technology parameters with all sources
3. Sensitivity analysis results
4. Regional breakdown tables
5. Python code and data repository link

### **Data Availability Statement**
"All data generated during this study are included in the supplementary information files. The complete dataset, Python code, and analysis scripts are available at [GitHub repository] under [license]."

---

## References Target

**Minimum**: 30-40 references
**Breakdown**:
- Petrochemical decarbonization: 8-10
- Technology parameters: 12-15
- MACC methodology: 4-5
- Asia-Pacific/Korea context: 5-7
- Policy and energy systems: 5-7

**All 36 references from petrochem_review.tex can be used!**

---

## Writing Timeline

**Phase 1** (Days 1-2): Structure & draft
- Set up LaTeX structure
- Write Abstract, Introduction, Methods
- Insert literature review from petrochem_review.tex

**Phase 2** (Days 3-4): Results & figures
- Wait for scenario re-runs to complete
- Generate all figures
- Write Results section with updated numbers

**Phase 3** (Days 5-6): Discussion & polish
- Write Discussion section
- Complete Conclusion
- Proofread entire paper

**Phase 4** (Day 7): Final review
- Check all cross-references
- Validate all numbers
- Format for submission

**Total**: 7 days for complete draft

---

## Next Immediate Steps

1. ✅ Wait for scenario re-runs to complete (~30-60 min)
2. ⏳ Generate all critical figures (Figures 1-8)
3. ⏳ Create all critical tables (Tables 1-8)
4. ⏳ Set up new LaTeX structure
5. ⏳ Begin writing draft sections

---

**Ready to start when scenario results are available!**
