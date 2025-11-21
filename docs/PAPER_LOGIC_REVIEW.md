# Paper Logic Review for Carbon Neutrality Journal Submission

**Date**: 2025-11-10
**Author**: Jinsu Park (LSE MSc)
**Target Journal**: Carbon Neutrality (Springer)
**Paper Type**: Original Research Article

---

## Executive Summary

This document reviews the logic, structure, and alignment between:
1. **Existing LaTeX paper** (`latex_paper/main.tex`)
2. **Korean final report** (`outputs/FINAL_REPORT_KO.md`)
3. **Carbon Neutrality journal requirements**

**Key Finding**: Your existing paper has strong methodology but covers only ONE scenario (policy-target), while your Korean report analyzes SIX comprehensive scenarios. We need to update the paper to include the 6-scenario comparative analysis.

---

## 1. Current Paper vs. Korean Report: Gap Analysis

### Current Paper Scope (main.tex)
| Aspect | Current Coverage |
|--------|------------------|
| **Scenarios** | 1 scenario: "Policy-target" (linear 50%→90% reduction) |
| **Production pathway** | Fixed (no production variation) |
| **Technology pathways** | All 4 technologies (HP, RE PPA, NCC-Elec, NCC-H₂) |
| **Cost range** | $47.9B (single endpoint) |
| **Baseline year** | 2025: 52.0 MtCO₂ |
| **Target** | 2050: 5.2 MtCO₂ (90% reduction) |

### Korean Report Scope (FINAL_REPORT_KO.md)
| Aspect | Coverage |
|--------|----------|
| **Scenarios** | **6 scenarios** = 3 production × 2 technology pathways |
| **Production pathways** | (1) Shaheen (growth), (2) 25% restructuring, (3) 40% restructuring |
| **Technology pathways** | (1) NCC-Electricity, (2) NCC-H₂ |
| **Cost range** | $27.5B to $58.8B (wide range!) |
| **Baseline year** | 2025: 52.0 MtCO₂ → 2050 BAU: 62-68 MtCO₂ (varies by scenario) |
| **Target** | 2050: Net-zero (0 MtCO₂) |

### **Critical Gap**: Your paper analyzes 1 scenario, but Korean report has 6 comprehensive scenarios with richer policy insights!

---

## 2. Research Question Comparison

### Current Paper (main.tex) - 3 Questions
1. **Baseline**: What are facility-level emissions and fuel balances in 2025?
2. **Technology economics**: How do 4 technologies compare in $/tCO₂?
3. **Policy compliance**: Which deployment schedule satisfies linear reduction targets?

### Recommended for Carbon Neutrality - 4 Enhanced Questions
1. **Baseline**: What are facility-level emissions across 248 facilities? ✅ (keep)
2. **Technology pathways**: How do hydrogen vs. electricity pathways compare economically? 🆕 (expand)
3. **Production scenarios**: What is the cost-emissions tradeoff between production growth vs. restructuring? 🆕 (NEW!)
4. **Policy implications**: What are optimal strategies for Korea's 2050 carbon neutrality? ✅ (enhance)

---

## 3. Proposed Paper Logic Structure for Carbon Neutrality

### **Title** (Updated)
**Current**: "Decarbonization Pathways for the Korean Petrochemical Industry: A Marginal Abatement Cost Curve Analysis with Energy-Based Methodology"

**Recommended**: "Comparative Techno-Economic Analysis of Carbon Neutrality Pathways for South Korea's Petrochemical Industry: Hydrogen vs. Electrification Routes under Production Transition Scenarios"

**Why change?**
- Emphasizes **comparative** nature (6 scenarios)
- Highlights **hydrogen vs. electrification** (main finding)
- Mentions **production scenarios** (unique contribution)
- "Carbon neutrality" aligns with journal name

---

### **Abstract** (Restructure Required)

**Current abstract structure**:
- Background → Methods → Single scenario results → Conclusion
- 52 MtCO₂ baseline → Policy target → $47.9B cost

**Recommended abstract structure** (350 words max):

```
[Background - 2 sentences]
South Korea's petrochemical sector emitted 52.0 MtCO₂ in 2025 across 248 facilities,
accounting for 7% of national emissions. Achieving carbon neutrality by 2050 requires
evaluating both technological pathways and production strategies.

[Objective - 1 sentence]
This study compares six decarbonization scenarios combining three production pathways
(growth, 25% restructuring, 40% restructuring) with two technology routes
(hydrogen-based vs. electricity-based naphtha crackers).

[Methods - 3 sentences]
We construct a facility-level Marginal Abatement Cost Curve (MACC) model covering
248 plants with detailed energy balances. Four mitigation technologies are evaluated:
industrial heat pumps, renewable power purchase agreements (RE PPA), electric
naphtha crackers (NCC-Electricity), and hydrogen-fired crackers (NCC-H₂).
Linear programming optimization determines least-cost deployment schedules for
each scenario from 2025 to 2050.

[Key Results - 4-5 sentences]
Under the growth scenario (Shaheen), achieving carbon neutrality requires
$53.9B (NCC-H₂) to $58.8B (NCC-Electricity) by 2050. Production restructuring
substantially reduces costs: 25% capacity reduction cuts costs to $32.2-35.4B,
while 40% reduction achieves $27.5-30.2B. NCC-H₂ pathways are 8-10% cheaper than
NCC-Electricity across all scenarios, but the electricity pathway offers superior
long-term sustainability. Regional analysis shows Ulsan, Yeosu, and Daesan require
combined 200 TWh/yr renewable capacity or 24 kt/yr green hydrogen infrastructure.

[Conclusion - 2 sentences]
Hydrogen pathways minimize near-term costs, but electricity pathways align better
with national energy transition goals despite higher initial investment.
The 6-10% cost premium for electrification is justified by infrastructure
co-benefits and elimination of hydrogen supply chain risks.
```

---

## 4. Paper Structure Logic Flow

### **Recommended Structure** (aligned with Carbon Neutrality format)

#### **1. Introduction** (~1,500 words)
**Current**: Adequate but needs expansion

**Add**:
- Korea's 2050 carbon neutrality commitment (government policy context)
- Industrial decarbonization challenges specific to petrochemicals
- **Research gap**: Previous studies focus on single pathways; no comprehensive comparison of production × technology scenarios
- **Novel contribution**: First facility-level (248 plants) comparative analysis of 6 scenarios for Korean petrochemicals

**Logic flow**:
1. Global petrochemical emissions context (1.3 GtCO₂)
2. Korea's importance (52 MtCO₂, 7% national emissions)
3. Policy context (2050 carbon neutrality, 10th Basic Electricity Plan)
4. Literature gap → Research questions → Paper contribution
5. Paper roadmap

#### **2. Literature Review** 🆕 (NEW SECTION - ~1,000 words)
**Why add?** Carbon Neutrality expects contextualization

**Content**:
- Petrochemical decarbonization studies (global: IEA, McKinsey; Asia-Pacific)
- MACC methodology applications in industry
- Hydrogen vs. electrification debates in chemical sector
- Previous Korea-specific studies (if any)
- **Gap**: No comprehensive scenario comparison for Korea

#### **3. Methodology** (~2,500 words)
**Current structure is excellent** - keep and enhance:

**3.1 Data Sources and Facility Inventory**
- ✅ Keep current data provenance table
- 🆕 Add: Production scenario definitions (Shaheen, 25%, 40%)

**3.2 MACC Framework**
- ✅ Keep equations 1-5
- ✅ Energy-based formulation (your strength!)

**3.3 Technology Parameters**
- ✅ Keep current table
- 🆕 Add: Comparison logic for NCC-H₂ vs NCC-Elec

**3.4 Scenario Design** 🆕 (NEW)
- **Production scenarios**:
  - Shaheen: BAU growth (2025: 52 Mt → 2050: 68 Mt before mitigation)
  - Restructuring 25%: Capacity reduction (2050: 40.9 Mt BAU)
  - Restructuring 40%: Deep reduction (2050: 35.5 Mt BAU)

- **Technology pathways**:
  - NCC-Electricity: 100% RE-powered electric crackers
  - NCC-H₂: Green hydrogen-fueled crackers

- **6 scenario matrix**: 3 × 2 = 6 combinations

**3.5 Optimization Model**
- ✅ Keep current linear programming formulation
- 🆕 Modify: Instead of fixed policy target, optimize for net-zero by 2050 under each scenario

#### **4. Results** (~3,000 words)
**Current**: Only 1 scenario → **Expand to 6 scenarios**

**Proposed structure**:

**4.1 Baseline Characterization** (✅ keep)
- 248 facilities, product mix, regional distribution
- ✅ Keep Table: Product group energy mix
- ✅ Keep Figure: Emissions by product

**4.2 Technology MACC Analysis** (✅ keep + enhance)
- ✅ Keep: MACC 2030 snapshot (Table)
- ✅ Keep: Cost evolution 2025-2050 (Figure)
- 🆕 Add: Side-by-side comparison NCC-H₂ vs NCC-Elec

**4.3 Scenario Comparison** 🆕 (MAJOR NEW SECTION)
This is the **heart** of your contribution!

**Table: Six-Scenario Summary** (from Korean report Table 3.1)
| Rank | Scenario | BAU 2050 (Mt) | Abatement (Mt) | Total Cost (2050) | Unit Cost ($/tCO₂) |
|------|----------|---------------|----------------|-------------------|-------------------|
| 1 | 40% + NCC-H₂ | 35.5 | 35.5 | $27.5B | $774 |
| 2 | 40% + NCC-Elec | 35.5 | 35.5 | $30.2B | $850 |
| 3 | 25% + NCC-H₂ | 40.9 | 40.9 | $32.2B | $787 |
| 4 | 25% + NCC-Elec | 40.9 | 40.9 | $35.4B | $866 |
| 5 | Shaheen + NCC-H₂ | 68.0 | 68.0 | $53.9B | $792 |
| 6 | Shaheen + NCC-Elec | 68.0 | 68.0 | $58.8B | $864 |

**Key findings**:
- Production restructuring reduces costs more than technology choice
- NCC-H₂ consistently 8-10% cheaper than NCC-Elec
- Unit abatement costs remarkably stable ($774-$866/tCO₂)

**4.4 Technology Pathway Comparison** 🆕
**Table: NCC-H₂ vs NCC-Electricity Comparison**
| Metric | NCC-H₂ | NCC-Electricity | Winner |
|--------|---------|-----------------|--------|
| Average 2050 cost | $37.9B | $41.5B | H₂ |
| Cost difference | - | +9.5% | H₂ |
| H₂ requirement | 24 kt/yr | 0 | Elec |
| Electricity increase | 0.005 TWh | 228 TWh | H₂ |
| Long-term outlook | Stable | Declining costs | Uncertain |

**4.5 Regional Renewable Energy Requirements** 🆕
**Table: Regional RE Deployment 2050** (Shaheen + NCC-Elec)
| Region | NCC-Elec RE (TWh) | Grid→RE (TWh) | Total (TWh) | Share |
|--------|-------------------|---------------|-------------|-------|
| Yeosu/Gwangyang | 62.8 | 4.8 | 67.6 | 21.3% |
| Ulsan | 72.3 | 2.2 | 74.5 | 23.5% |
| Daesan | 55.2 | 3.4 | 58.6 | 18.5% |
| Incheon | 19.4 | 1.0 | 20.4 | 6.4% |
| Others | 88.5 | 7.7 | 96.2 | 30.3% |
| **Total** | **298.2** | **19.1** | **317.3** | **100%** |

#### **5. Discussion** (~2,000 words)
**Current**: Adequate but needs expansion

**5.1 Technology Pathway Tradeoffs**
- Cost vs. sustainability: Why NCC-Elec despite higher cost?
- Infrastructure implications (298 TWh RE vs 24 kt H₂)
- Technology maturity and risk

**5.2 Production Scenario Implications**
- Economic impact of restructuring (jobs, GDP)
- Global competitiveness considerations
- Timing and transition pathways

**5.3 Policy Recommendations** 🆕
From Korean report Section 7:
- **Main scenario**: Shaheen + NCC-Electricity
- **Rationale**: Despite $4.9B premium, RE infrastructure benefits entire economy
- **3-phase roadmap**: 2025-2030 (pilots), 2030-2040 (scale-up), 2040-2050 (completion)
- Government support needs

**5.4 Comparison with International Studies**
- How do your costs compare with EU, US, China petrochemical decarbonization?
- Korea-specific factors (energy import dependence, manufacturing export economy)

#### **6. Limitations** (~500 words)
✅ Keep current section, add:
- No consideration of circular economy (chemical recycling)
- Static demand assumption (no demand reduction scenarios)
- Technology learning rates uncertainty

#### **7. Conclusion** (~500 words)
**Restructure to emphasize 6-scenario findings**:
1. Restate research gap and contribution
2. Key finding 1: Production scenarios matter MORE than technology choice for total cost
3. Key finding 2: NCC-H₂ cheaper short-term, but NCC-Elec recommended for sustainability
4. Key finding 3: Regional RE deployment plan critical (120 GW by 2050)
5. Policy implications: Hybrid approach + phased transition
6. Future research directions

---

## 5. Key Changes Required

### **Major Additions**
1. ✅ **Literature Review section** (new)
2. ✅ **Scenario Design subsection** in Methods
3. ✅ **Six-scenario comparison** in Results (main contribution!)
4. ✅ **Regional analysis** tables and discussion
5. ✅ **Policy recommendations** subsection

### **Content to Update**
1. **Abstract**: Rewrite to reflect 6 scenarios (not 1)
2. **Title**: Include "comparative" and "production scenarios"
3. **Introduction**: Add research gap about lack of comparative scenario studies
4. **Results tables**: Replace single-scenario tables with 6-scenario comparison
5. **Figures**: Add scenario comparison charts from Korean report

### **Content to Keep**
1. ✅ Energy-based MACC formulation (Equations 1-5) - **This is your strength!**
2. ✅ Facility-level baseline (Table 1)
3. ✅ Technology parameters (Table 2)
4. ✅ Data provenance methodology
5. ✅ Implementation and verification section

---

## 6. Data/Figures Alignment

### **Tables Needed** (from Korean report)
1. ✅ Baseline by product group (already have)
2. 🆕 **Six-scenario summary** (Korean Table 3.1) - **CRITICAL**
3. 🆕 **NCC-H₂ vs NCC-Elec comparison** (Korean Table 4.1)
4. 🆕 **Regional RE deployment** (Korean Table 5.1)
5. ✅ MACC snapshot (already have)

### **Figures Needed**
1. ✅ Baseline emissions by product (already have)
2. ✅ Cost evolution 2025-2050 (already have)
3. 🆕 **Scenario cost comparison** (bar chart: 6 scenarios)
4. 🆕 **Technology pathway breakdown** (Shaheen scenario: NCC-H₂ vs NCC-Elec)
5. 🆕 **Regional RE timeline** (stacked area chart: 4 regions 2025-2050)

### **Data Files to Generate**
```
outputs/
├── scenario_comparison_6scenarios/
│   ├── summary.csv                    # For Table: 6 scenarios
│   ├── technology_pathway_comparison.csv  # For Table: H₂ vs Elec
│   └── regional_re_2050.csv          # For Table: Regional RE
```

---

## 7. Alignment with Carbon Neutrality Journal

### **Journal Requirements** ✅ Check
| Requirement | Status | Notes |
|-------------|--------|-------|
| Original research | ✅ Yes | First comprehensive 6-scenario Korea petrochemical study |
| Carbon neutrality focus | ✅ Yes | Directly addresses 2050 net-zero pathways |
| Multi-disciplinary | ✅ Yes | Energy systems + economics + policy |
| Policy relevance | ✅ Yes | Korea 2050 carbon neutrality strategy |
| Data transparency | ✅ Yes | All data and code available |
| Word limit (8,000-10,000) | ⚠️ Check | Current ~6,500 words; with additions will be ~9,000 |
| Abstract ≤350 words | ✅ Yes | Will revise to 330 words |
| References ≥30 | ⚠️ Need more | Current ~15; need to add 15-20 more |

### **Strengths for Carbon Neutrality**
1. ✅ **Facility-level granularity** (248 plants) - rare in literature
2. ✅ **Energy-explicit methodology** - transparent, reproducible
3. ✅ **Comprehensive scenario analysis** - 6 scenarios
4. ✅ **Policy-relevant** - directly supports Korea's carbon neutrality planning
5. ✅ **Regional insights** - Ulsan, Yeosu, Daesan deployment plans
6. ✅ **Open science** - all data/code available

---

## 8. Novelty Statement (for Reviewers)

**What makes this paper novel?**

1. **First comprehensive facility-level MACC for Korean petrochemicals**
   - Previous studies: Aggregate sector-level or global models
   - This study: 248 individual facilities with energy balances

2. **Systematic comparison of production × technology scenarios**
   - Previous studies: Single pathway analysis
   - This study: 3 production × 2 technology = 6 scenarios

3. **Energy-explicit methodology without discounting**
   - Previous studies: LCOE or NPV-based (black-box assumptions)
   - This study: Transparent energy flow accounting + simple annualization

4. **Regional renewable energy deployment planning**
   - Previous studies: National aggregate targets
   - This study: City-level RE requirements (Ulsan, Yeosu, Daesan, Incheon)

5. **Hydrogen vs. electrification comparative framework**
   - Previous studies: Evaluate one or the other
   - This study: Direct cost-benefit comparison with infrastructure implications

---

## 9. Critical Success Factors

### **To Maximize Acceptance Probability**:

1. ✅ **Strong literature review** - cite 30+ papers (current ~15)
   - Add: Asian petrochemical studies (China, Japan, Singapore)
   - Add: Recent MACC applications (2023-2025 papers)
   - Add: Hydrogen economy literature (IEA, IRENA reports)

2. ✅ **Clear positioning of contribution**
   - Emphasize "first facility-level 6-scenario comparison for Korea"
   - Highlight policy relevance to Carbon Neutrality journal mission

3. ✅ **High-quality figures**
   - Professional charts (ggplot2 or matplotlib with publication theme)
   - Color-blind friendly palettes
   - High-resolution (300 DPI minimum)

4. ✅ **Transparent methodology**
   - Keep energy-explicit formulation (your strength!)
   - Add data availability statement
   - Mention GitHub repository (if open-sourcing)

5. ✅ **Policy implications section**
   - Carbon Neutrality journal values actionable insights
   - 3-phase roadmap from Korean report is excellent

---

## 10. Action Items Priority

### **HIGH PRIORITY** (Must do for submission)
1. ⬜ Rewrite abstract to reflect 6 scenarios
2. ⬜ Add scenario design subsection (Section 3.4)
3. ⬜ Create 6-scenario comparison table (Results 4.3)
4. ⬜ Add technology pathway comparison (Results 4.4)
5. ⬜ Add regional RE analysis (Results 4.5)
6. ⬜ Expand literature review to 30+ references
7. ⬜ Update title to include "comparative" and "scenarios"

### **MEDIUM PRIORITY** (Strengthen paper)
1. ⬜ Add Literature Review section (Section 2)
2. ⬜ Create scenario comparison figures (3 new figures)
3. ⬜ Add policy recommendations subsection
4. ⬜ Expand discussion section
5. ⬜ Add international comparison in discussion

### **LOW PRIORITY** (Nice to have)
1. ⬜ Sensitivity analysis appendix
2. ⬜ Additional regional charts
3. ⬜ Technology learning curve discussion

---

## 11. Timeline Estimate

**Optimistic (2 weeks)**:
- Week 1: Update content (sections 1-4)
- Week 2: Finalize figures, references, polish

**Realistic (3-4 weeks)**:
- Week 1-2: Major content additions (6 scenarios, lit review)
- Week 3: Figures, tables, references
- Week 4: Revisions, proofreading, formatting

**Conservative (6 weeks)**:
- Week 1-3: Content development + peer feedback
- Week 4-5: Revisions and figure refinement
- Week 6: Final polish and submission prep

---

## 12. Next Steps

1. **Review this logic document** - Do you agree with the 6-scenario approach?
2. **Decide on title** - Approve new title or suggest alternative?
3. **Start with abstract** - Shall we draft the new 350-word abstract together?
4. **Generate missing data** - Run scripts to create scenario comparison CSVs?
5. **Literature search** - Need help finding relevant papers for lit review?

---

## Conclusion

Your existing paper has **excellent methodology** (energy-explicit MACC), but it currently analyzes only 1 scenario while your Korean report contains **6 comprehensive scenarios** with much richer insights.

**Recommendation**: Update the paper to reflect the 6-scenario analysis. This will:
- ✅ Strengthen novelty (first comprehensive scenario comparison)
- ✅ Increase policy relevance (production vs. technology tradeoffs)
- ✅ Better fit Carbon Neutrality journal's mission
- ✅ Provide more actionable insights for policymakers

The core methodology is already strong - we just need to expand the **scope** to match your Korean report findings.

**Ready to proceed?** Let me know which section you'd like to start with!
