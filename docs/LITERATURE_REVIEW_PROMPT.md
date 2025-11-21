# Literature Review Prompt for Technology Cost Updates

**Date**: 2025-11-10
**Purpose**: Research latest technology costs and parameters for petrochemical decarbonization
**Target**: Feed updated data into MACC model and academic paper for Carbon Neutrality journal

---

## Prompt to Give to Another AI

```
I am preparing an academic paper on petrochemical industry decarbonization for South Korea
targeting the journal "Carbon Neutrality" (Springer). I need you to conduct a comprehensive
literature review to update technology cost parameters and find recent academic references.

## PART 1: Technology Cost Parameter Review

Please research and provide UPDATED cost parameters for the following four decarbonization
technologies for petrochemical plants. Search for peer-reviewed papers, technical reports,
and industry studies published between 2020-2025.

### Technologies to Research:

1. **Industrial Heat Pumps (High-Temperature)**
   - Application: Replace fossil fuel combustion for process heat (<165°C) in BTX plants
   - Current assumptions: CAPEX $900/ton CO2 (2025), COP 4.0, lifetime 20 years
   - Find: Latest CAPEX costs, OPEX%, COP values, lifetime, learning rates

2. **Renewable Energy Power Purchase Agreements (RE PPA)**
   - Application: Grid electricity → 100% renewable electricity for all facilities
   - Current assumptions: No CAPEX (contract-based), price trajectory declining to $50/MWh by 2050
   - Find: Latest PPA price trends in South Korea/Asia, offshore vs. onshore wind costs

3. **Electric Naphtha Cracker (NCC-Electricity)**
   - Application: Electrify naphtha cracking process with 100% renewable electricity
   - Current assumptions: CAPEX $1,500/ton/yr capacity (2025), electricity consumption 5.0 MWh/ton ethylene
   - Technology: Electric steam cracking (e-cracker), plasma cracking, or similar
   - Find: Latest pilot projects, CAPEX estimates, electricity consumption, TRL level, commercial readiness

4. **Hydrogen-Fired Naphtha Cracker (NCC-H₂)**
   - Application: Replace fossil fuel combustion with green hydrogen in cracking furnaces
   - Current assumptions: CAPEX $1,700/ton/yr capacity (2025), H₂ consumption 0.56 ton H₂/ton ethylene
   - Find: Latest pilot projects, CAPEX estimates, hydrogen consumption rates, retrofit vs. greenfield costs

### Required Output Format for PART 1:

For EACH technology, provide:

```latex
\subsection{Technology Name}

\paragraph{Recent Studies:}
\begin{itemize}
    \item \textbf{Author et al. (Year)}: Brief finding - Cost: \$XXX, Parameter: YYY \citep{AuthorYear}
    \item \textbf{Author et al. (Year)}: Brief finding - Cost: \$XXX, Parameter: YYY \citep{AuthorYear}
    \item ... (at least 3-5 recent sources)
\end{itemize}

\paragraph{Updated Parameter Recommendations:}
\begin{table}[h]
\centering
\begin{tabular}{lcc}
\toprule
\textbf{Parameter} & \textbf{Current Study} & \textbf{Literature Range} \\
\midrule
CAPEX (2025, \$/ton/yr) & XXX & YYY--ZZZ \\
OPEX (\% of CAPEX) & X.X & Y.Y--Z.Z \\
Lifetime (years) & XX & YY--ZZ \\
Energy intensity & X.X & Y.Y--Z.Z \\
Technology Readiness Level & X & Y--Z \\
\bottomrule
\end{tabular}
\caption{Parameter comparison: [Technology Name]}
\end{table}

\paragraph{Key Insights:}
- [What does literature suggest about cost trends?]
- [Any pilot projects or commercial deployments?]
- [Regional variations (Asia vs. Europe vs. US)?]
```

---

## PART 2: Petrochemical Decarbonization Literature Review

Please search for and summarize recent academic papers (2020-2025) on the following topics:

### Topic Areas:

1. **Petrochemical Industry Decarbonization (General)**
   - Global or regional studies on petrochemical sector carbon neutrality
   - MACC applications to chemical industry
   - Technology pathways for steam crackers (ethylene/propylene production)

2. **Asia-Pacific Petrochemical Studies**
   - Korea-specific studies (if any)
   - China, Japan, Singapore petrochemical decarbonization
   - Regional energy transition challenges

3. **Hydrogen vs. Electrification in Chemical Sector**
   - Comparative techno-economic analysis
   - Infrastructure requirements (H₂ pipelines, electrolysers, renewable electricity)
   - Cost projections and learning curves

4. **MACC Methodology Applications**
   - Recent MACC studies for industrial sectors
   - Energy system modeling approaches
   - Facility-level vs. sector-level modeling

5. **Carbon Neutrality Policy (Korea)**
   - Korea's 2050 carbon neutrality roadmap
   - 10th Basic Electricity Plan
   - Industrial decarbonization policies

### Required Output Format for PART 2:

```latex
\section{Literature Review}

\subsection{Petrochemical Industry Decarbonization}

Global petrochemical industry emits approximately 1.3 GtCO\textsubscript{2} annually
\citep{IEA2020}. Recent studies have explored various decarbonization pathways...

\textbf{Key Studies:}
\begin{itemize}
    \item \citet{AuthorYear}: [1-2 sentence summary of findings]
    \item \citet{AuthorYear}: [1-2 sentence summary of findings]
    \item ... (list 5-8 key papers per subsection)
\end{itemize}

[Continue with 2-3 paragraphs synthesizing the literature]

\subsection{Asia-Pacific Petrochemical Decarbonization}

[Same structure as above]

\subsection{Hydrogen versus Electrification Pathways}

[Same structure as above]

\subsection{MACC Methodology in Industrial Applications}

[Same structure as above]

\subsection{Korea's Carbon Neutrality Policy Context}

[Same structure as above]

\subsection{Research Gap}

Despite extensive literature on petrochemical decarbonization, several gaps remain:
\begin{itemize}
    \item No comprehensive facility-level analysis for Korea (248 facilities)
    \item Limited systematic comparison of production scenarios (growth vs. restructuring)
    \item Insufficient regional renewable energy deployment planning
    \item Lack of hydrogen vs. electrification comparative framework at national scale
\end{itemize}

This study addresses these gaps by...
```

---

## PART 3: Bibliography in BibTeX Format

Please provide ALL cited references in BibTeX format ready to paste into `references.bib` file.

### Required Format:

```bibtex
@article{AuthorYear,
    author = {Last, First and Last, First},
    title = {Full Paper Title},
    journal = {Journal Name},
    year = {2024},
    volume = {XX},
    number = {X},
    pages = {XXX--XXX},
    doi = {10.XXXX/XXXXX}
}

@techreport{IEA2024,
    author = {{International Energy Agency}},
    title = {Report Title},
    institution = {IEA},
    year = {2024},
    url = {https://...}
}

... (continue for all references)
```

---

## PART 4: Key Data Summary Tables

Please create summary tables comparing technology costs across different studies:

```latex
\begin{table}[htbp]
\centering
\caption{Electric Naphtha Cracker Cost Estimates from Recent Literature}
\label{tab:lit_ncc_elec_costs}
\begin{tabular}{lcccl}
\toprule
\textbf{Source} & \textbf{Year} & \textbf{CAPEX} & \textbf{Electricity} & \textbf{Region} \\
 & & \textbf{(\$/ton/yr)} & \textbf{(MWh/ton)} & \\
\midrule
Current Study & 2025 & 1,500 & 5.0 & Korea \\
Author et al. \citep{Ref1} & 2024 & 1,200--1,800 & 4.5--5.5 & Europe \\
Author et al. \citep{Ref2} & 2023 & 1,400--1,600 & 4.8--5.2 & Global \\
Author et al. \citep{Ref3} & 2022 & 1,100--2,000 & 4.0--6.0 & Asia \\
\midrule
\textbf{Literature Mean} & & \textbf{1,425} & \textbf{5.0} & \\
\bottomrule
\end{tabular}
\end{table}

[Create similar tables for NCC-H₂, Heat Pumps, and RE PPA]
```

---

## Search Instructions

**Databases to search:**
- Google Scholar (scholar.google.com)
- Web of Science
- Scopus
- ScienceDirect (Elsevier)
- Springer Link (since target journal is Springer)
- Taylor & Francis Online
- IEA Publications (www.iea.org)
- IRENA Publications (www.irena.org)
- Korean Energy Economics Institute (KEEI) - if available in English

**Keywords to use:**
- "petrochemical decarbonization"
- "naphtha cracker" + "hydrogen" OR "electrification"
- "marginal abatement cost curve" + "chemical industry"
- "industrial heat pump" + "high temperature"
- "electric cracker" OR "e-cracker"
- "Korea carbon neutrality"
- "ethylene production" + "carbon neutrality"

**Prioritize:**
- Peer-reviewed journal articles (2022-2025)
- Technical reports from IEA, IRENA, OECD (2020-2025)
- Industry reports from McKinsey, BCG, Hydrogen Council (2021-2025)
- Pilot project announcements (BASF, Dow, LG Chem, etc.)

**Minimum target:**
- At least 30-40 total references
- At least 5-8 references per technology
- At least 10 references on petrochemical decarbonization
- At least 5 references on Korea-specific policy/energy context

---

## Validation Requirements

For each cost parameter update, please provide:
1. **Source credibility**: Journal impact factor or report author authority
2. **Geographic relevance**: Is it applicable to Korea/Asia?
3. **Time relevance**: How recent is the data (prefer 2023-2025)?
4. **Consistency check**: Does it align with other sources?
5. **Uncertainty range**: What is the cost range across studies?

---

## Deliverable Checklist

Please confirm you will provide:
- [ ] Technology cost update tables (4 technologies) in LaTeX format
- [ ] Literature review text (5 subsections) in LaTeX format
- [ ] Complete BibTeX entries for all references (30-40 entries)
- [ ] Comparison tables showing cost ranges across studies (4 tables)
- [ ] Executive summary of key findings and recommendations
- [ ] Flagged discrepancies or uncertainties in cost estimates

---

## Expected Output Structure

```
=== PART 1: TECHNOLOGY COST UPDATES ===
[LaTeX formatted subsections for 4 technologies]

=== PART 2: LITERATURE REVIEW ===
[LaTeX formatted Section 2 text with 5 subsections]

=== PART 3: BIBTEX BIBLIOGRAPHY ===
[Complete .bib entries]

=== PART 4: COST COMPARISON TABLES ===
[4 LaTeX tables comparing literature costs]

=== PART 5: EXECUTIVE SUMMARY ===
Key Findings:
- Technology X: Cost range $A-B, recommended update: $C
- Technology Y: ...
Main Recommendations:
- Update parameter X from A to B based on [sources]
- Keep parameter Y (well-supported by recent literature)
Uncertainties:
- Technology Z has wide cost range ($A-B), need sensitivity analysis
```

---

## Special Notes for the AI Researcher

1. **Focus on CAPEX updates**: Capital costs are most uncertain and impactful
2. **Asia-Pacific context**: Prioritize studies relevant to Korean/Asian conditions
3. **Recent data only**: Prefer 2022-2025 publications (technology costs change rapidly)
4. **Distinguish**: Retrofit vs. greenfield costs (important for NCC technologies)
5. **Learning curves**: Note if studies mention cost reduction trajectories to 2030/2050
6. **Pilot projects**: Mention any commercial pilots or demonstrations (validates TRL)

Thank you! Please provide the output in the structured format above.
```

---

## How to Use This Prompt

1. **Copy the entire prompt** above (from "I am preparing..." to the end)
2. **Paste it into another AI** (ChatGPT, Claude, Perplexity, etc.)
3. **Wait for the comprehensive response** (may take several minutes)
4. **Save the output** to a file (e.g., `LITERATURE_REVIEW_OUTPUT.md`)
5. **Bring it back to me** and I will:
   - Validate the data against your current model
   - Integrate the LaTeX sections into your paper
   - Update the technology parameters CSV files
   - Create comparison tables showing old vs. new values
   - Flag any major discrepancies requiring sensitivity analysis

---

## What You'll Get Back

The other AI should deliver:

1. ✅ **4 technology subsections** in LaTeX (ready to paste into paper)
2. ✅ **Complete Literature Review section** (~2,000 words in LaTeX)
3. ✅ **30-40 BibTeX references** (paste into `references.bib`)
4. ✅ **4 cost comparison tables** (LaTeX format)
5. ✅ **Executive summary** with update recommendations

---

## Timeline

- **Research time**: 30-60 minutes (depending on AI)
- **Your review time**: 15-30 minutes
- **My integration time**: 1-2 hours to update model and paper

Total: **2-4 hours** to have fully updated literature review and technology costs!

---

Ready to use this prompt? Let me know when you have the output from the other AI!


