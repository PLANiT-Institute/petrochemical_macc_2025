# Roadmap for Journal of Cleaner Production Submission

This document outlines the 5 key steps to prepare and submit a paper to the **Journal of Cleaner Production (JCP)** using the Petrochemical MACC model.

## Step 1: Experimental Design & Environment Setup
**Goal:** Freeze the code and data version used for the paper to ensure reproducibility.
- [ ] **Create a dedicated folder:** `paper_jcp` (Done).
- [ ] **Define Scenarios:** Explicitly define the scenarios to be compared (e.g., Baseline vs. Net Zero 2050, Tech Constraints).
- [ ] **Lock Dependencies:** Ensure `requirements.txt` captures the current environment.
- [ ] **Create Execution Script:** Develop `run_paper_experiment.py` to generate all consolidated data for the paper in one go.

## Step 2: Methodology & Data Draft
**Goal:** Write the "Materials and Methods" section, the core technical foundation.
- [ ] **Model Description:** Document the MAC (Marginal Abatement Cost) logic, including the objective function and constraints.
- [ ] **Data Sources:** List all data inputs (NCC facility capacities, feedstock prices, technology costs, emission factors).
- [ ] **Scenario Logic:** Explain the assumptions behind each scenario (e.g., carbon price trajectory, technology availability).
- [ ] **Validation:** Briefly describe how the model was validated or calibrated against historical data.

## Step 3: Core Results Generation
**Goal:** Produce high-quality, publication-ready figures and tables.
- [ ] **Abatement Cost Curves (MACC):** Generated for 2030, 2040, 2050 under different scenarios.
- [ ] **Transition Cost Analysis:** Total investment and operational cost comparisons.
- [ ] **Technological Mix:** Stacked area charts showing the evolution of technology adoption (e.g., SR vs. E-Furnace vs. Hydrogen).
- [ ] **Sensitivity Analysis:** (Optional but recommended) Tornado charts showing sensitivity to key parameters like electricity price.
- [ ] **Summary Tables:** Key metrics (Total Abatement, Avg Cost/ton) formatted for the manuscript.

## Step 4: Abstract & Narrative Structure
**Goal:** Craft the story and key arguments of the paper.
- [ ] **Title & Keywords:** Brainstorm title options and select 5-6 JCP-relevant keywords.
- [ ] **Abstract:** Write a structured abstract (Background, Methods, Results, Conclusions) within JCP word limits (usually ~200-300 words).
- [ ] **Introduction Outline:** Define the research gap (Why this paper? Why now?) and specific research questions.
- [ ] **Conclusion & Policy Implications:** Draft the "so what?" – what do these results mean for policymakers and industry leaders.

## Step 5: Manuscript Assembly & Formatting
**Goal:** Compile the full paper and prepare for submission.
- [ ] **Assemble Draft:** Combine all sections (Intro, Methods, Results, Discussion, Conclusion) into a single document.
- [ ] **Reference Management:** Ensure all citations are in place (using a consistent format).
- [ ] **Formatting Check:** Verify against JCP Guide for Authors (font, margins, section numbering, figure quality).
- [ ] **Cover Letter:** Draft a compelling cover letter to the editor.
- [ ] **Final Export:** Convert the Markdown/LaTeX draft to Word (if required) or PDF for submission.
