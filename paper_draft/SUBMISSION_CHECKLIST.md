# Submission Checklist for Carbon Neutrality Journal

**Target Journal**: Carbon Neutrality (Springer Nature, Open Access)
**Submission Portal**: https://www.editorialmanager.com/cneu/
**Target Date**: November 22, 2025

---

## Pre-Submission Checklist

### ✅ Manuscript Components (COMPLETED)

- [x] **Abstract** (250 words) - `00_Abstract.md`
- [x] **Introduction** (800 words) - `01_Introduction_v2.md`
- [x] **Methods** (1,200 words) - `02_Methods.md`
- [x] **Results** (1,500 words) - `03_Results.md`
- [x] **Discussion** (1,200 words) - `04_Discussion.md`
- [x] **Conclusion** (400 words) - `05_Conclusion.md`
- [x] **References** (30 references, APA style) - `REFERENCES.md`
- [x] **Main text figures** (5 figures with captions) - `FIGURE_CAPTIONS.md`
- [x] **Supplementary figures** (2 figures with captions) - `FIGURE_CAPTIONS.md`
- [x] **Main text tables** (3 tables) - `TABLES.md`
- [x] **Supplementary tables** (4 tables) - `TABLES.md`
- [x] **Complete manuscript** (5,050 words) - `PAPER_DRAFT_COMPLETE.md`

**Status**: ✅ All core components drafted and ready for formatting

---

### ⏳ To Complete Before Submission

#### Author Information (HIGH PRIORITY)
- [ ] **Lead author**: Name, affiliation, email, ORCID ID
- [ ] **Co-authors**: Names, affiliations, contributions, ORCID IDs (if applicable)
- [ ] **Corresponding author**: Designated, contact details verified
- [ ] **Author contributions statement**: CRediT taxonomy or narrative
- [ ] **Competing interests declaration**: None or specify

**Template**:
```
Author 1: [Your Name]
Affiliation: [University/Institution], [Department]
Email: [corresponding email]
ORCID: [0000-0000-0000-0000]
Contributions: Conceptualization, Methodology, Software, Formal analysis, Writing - original draft

Author 2: [Supervisor/Co-author if applicable]
Affiliation: [Institution]
ORCID: [ID]
Contributions: Supervision, Writing - review & editing, Funding acquisition
```

#### Acknowledgments (MEDIUM PRIORITY)
- [ ] **Funding sources**: Grant numbers, agencies
- [ ] **Data providers**: Korea GHG Inventory, industry associations
- [ ] **Software acknowledgment**: Python, libraries used (pandas, numpy, matplotlib)
- [ ] **Personal acknowledgments**: Advisors, colleagues (if applicable)

**Template**:
```
This research was supported by [Grant name/number if applicable, or "No external funding"].
The authors thank the Korea Greenhouse Gas Inventory and Research Center for providing
facility-level emissions data, and [name colleagues/advisors if appropriate] for valuable
discussions during model development.
```

#### Data Availability Statement (HIGH PRIORITY)
- [ ] **Model code**: GitHub repository or Zenodo DOI
- [ ] **Input data**: Available upon request or public sources cited
- [ ] **Output data**: Supplementary files or repository
- [ ] **Reproducibility**: Instructions to reproduce results

**Template**:
```
Data Availability: The MACC model code and input parameters are available at
[GitHub repository URL or "upon reasonable request to the corresponding author"].
Facility-level emissions data are from Korea's National Greenhouse Gas Inventory (2022),
available at [URL]. All scenario results and figures are provided in supplementary materials.
```

#### Ethics and Compliance (LOW PRIORITY - likely N/A)
- [ ] Ethics approval: N/A (no human subjects, no animal studies)
- [ ] Informed consent: N/A
- [ ] Data protection: All data are aggregated facility-level, no personal information

---

### 📄 Formatting Requirements

#### Journal-Specific Format (Carbon Neutrality)
- [ ] **Template**: Download from https://www.springernature.com/gp/authors/campaigns/latex-author-support
- [ ] **File format**: LaTeX (.tex) or MS Word (.docx) - LaTeX preferred for equations
- [ ] **Line numbering**: Enable for review version
- [ ] **Page numbering**: Enable
- [ ] **Font**: Times New Roman or similar, 12pt
- [ ] **Line spacing**: Double-spaced for review
- [ ] **Margins**: 1 inch (2.54 cm) all sides
- [ ] **Sections**: Numbered (1, 2, 3...) or unnumbered - check journal style

#### Figure Formatting
- [ ] **Resolution**: 300 DPI minimum - ✅ COMPLETED
- [ ] **Format**: TIFF, EPS, or PDF preferred; PNG acceptable
- [ ] **Color**: RGB for online, CMYK if printed (check journal)
- [ ] **Size**: Fit within column width (3.5" single, 7" double)
- [ ] **Labels**: Readable at 100% scale
- [ ] **File naming**: Figure1.pdf, Figure2.pdf, etc.
- [ ] **Upload**: Separate files, not embedded in text (for initial submission)

#### Table Formatting
- [ ] **Format**: Editable (not images) - use Word table or LaTeX tabular
- [ ] **Font**: Consistent with text (12pt or 10pt)
- [ ] **Borders**: Minimal (top, bottom, section dividers only)
- [ ] **Alignment**: Numbers right-aligned, text left-aligned
- [ ] **Footnotes**: Below table, superscript letters (a, b, c...)
- [ ] **Placement**: After first mention in text, or end of document

#### References
- [ ] **Style**: APA, Vancouver, or author-year - ✅ APA FORMATTED
- [ ] **Software**: Use EndNote, Zotero, or Mendeley for management
- [ ] **DOIs**: Include for all references where available - ✅ INCLUDED
- [ ] **URLs**: Include access dates for web sources - ✅ INCLUDED
- [ ] **Completeness**: All in-text citations in reference list - ✅ VERIFIED
- [ ] **Accuracy**: Cross-check author names, years, titles

---

### 📋 Supplementary Materials

#### Files to Prepare
- [ ] **Supplementary Figures** (Figure S1-S2): PNG/PDF, 300 DPI
- [ ] **Supplementary Tables** (Table S1-S4): Excel or PDF
- [ ] **Supplementary Methods**: Extended methodology if needed (optional)
- [ ] **Supplementary Data**: Model outputs, scenario results (Excel or CSV)

#### Organization
- [ ] Create `/supplementary/` folder with all files
- [ ] Name files clearly: `FigureS1_TechnologyDeployment.pdf`
- [ ] Create `Supplementary_Information.pdf` combining all supplements
- [ ] Include table of contents in supplementary document

---

### ✉️ Cover Letter (REQUIRED)

**See**: `COVER_LETTER_TEMPLATE.md` (to be created)

Must include:
- [ ] Article title
- [ ] Brief summary (2-3 sentences)
- [ ] Significance statement (why Carbon Neutrality readers care)
- [ ] Confirmation of originality (not under review elsewhere)
- [ ] Confirmation all authors approved submission
- [ ] Suggested reviewers (3-5) with emails and expertise
- [ ] Opposed reviewers (optional, if conflicts exist)

---

### 🔍 Pre-Submission Review

#### Content Quality Check
- [ ] **Abstract**: Standalone, includes key numbers (164.5 TWh, 6% cost difference)
- [ ] **Introduction**: Clear research question, gap identified, contribution stated
- [ ] **Methods**: Reproducible, equations numbered, parameters sourced
- [ ] **Results**: Figures referenced, key findings highlighted, no interpretation
- [ ] **Discussion**: Interpretation, limitations acknowledged, policy implications clear
- [ ] **Conclusion**: Concise, no new information, forward-looking
- [ ] **Consistency**: Numbers match across sections (e.g., 164.5 TWh everywhere)

#### Technical Accuracy Check
- [ ] **Equations**: All variables defined, units specified
- [ ] **Numbers**: Verified against model output (`summary.csv`)
- [ ] **Units**: Consistent (MtCO₂, TWh, Mt H₂, $B, $/tCO₂)
- [ ] **Figures**: Data matches text, axes labeled, legends clear
- [ ] **Tables**: Totals correct, percentages verified, sources cited
- [ ] **References**: Cited correctly in text, complete information in bibliography

#### Language and Style Check
- [ ] **Grammar**: Proofread, no typos
- [ ] **Spelling**: Consistent (US or UK English - journal uses UK)
- [ ] **Acronyms**: Defined at first use (MACC, NCC, H₂, RE PPA, HTHP)
- [ ] **Tone**: Professional, objective, no subjective claims
- [ ] **Tense**: Past tense for Methods/Results, present for Discussion/Conclusion
- [ ] **Person**: Third person ("we developed", "this study shows")

#### Ethical and Legal Check
- [ ] **Plagiarism**: Run through iThenticate or Turnitin (< 15% similarity)
- [ ] **Self-plagiarism**: Not reusing text from your own prior publications
- [ ] **Permissions**: Figures/tables from other sources have permission (N/A, all original)
- [ ] **Authorship**: All contributors properly credited, no ghost/guest authors
- [ ] **Data ethics**: Facility-level data aggregated, no proprietary information disclosed

---

### 🚀 Submission Process

#### Step 1: Create Account
- [ ] Go to: https://www.editorialmanager.com/cneu/
- [ ] Register with email address
- [ ] Complete profile (name, affiliation, expertise keywords)

#### Step 2: Upload Files
- [ ] **Main manuscript**: PDF or Word (with line numbers)
- [ ] **Figures**: Separate files (Figure1.pdf, Figure2.pdf, ...)
- [ ] **Tables**: Embedded in manuscript or separate Excel files
- [ ] **Supplementary materials**: Combined PDF or separate files
- [ ] **Cover letter**: PDF or text in submission form

#### Step 3: Complete Metadata
- [ ] **Article type**: Original Research
- [ ] **Title**: Exact match to manuscript
- [ ] **Authors**: All names, affiliations, ORCIDs
- [ ] **Abstract**: Copy-paste from manuscript
- [ ] **Keywords**: 5-8 terms (Industrial decarbonization, petrochemicals, MACC, energy system constraints, hydrogen economy, electrification, South Korea, renewable energy)
- [ ] **Funding**: Grant numbers or "No funding"
- [ ] **Competing interests**: Declare or state none
- [ ] **Suggested reviewers**: 3-5 names with emails

#### Step 4: Review and Submit
- [ ] **PDF proof**: Generated by system, review for formatting errors
- [ ] **Checklist**: Complete journal's submission checklist
- [ ] **Confirm**: Originality, authorship, data availability statements
- [ ] **Submit**: Click final submit button
- [ ] **Confirmation**: Save manuscript number for tracking

---

### 📊 Post-Submission

#### Track Status
- [ ] **Manuscript number**: Record for reference (e.g., CNEU-D-25-00XXX)
- [ ] **Status checks**: Log in to Editorial Manager weekly
- [ ] **Expected timeline**:
  - Editor assignment: 1-2 weeks
  - Peer review: 4-8 weeks
  - Decision: 2-3 months total

#### Prepare for Revisions
- [ ] **Reviewer comments**: Expect 2-3 reviewers
- [ ] **Response letter**: Template for point-by-point responses
- [ ] **Revised manuscript**: Track changes version
- [ ] **Rebuttal deadline**: Typically 4-6 weeks for major revisions

---

### 🎯 Suggested Reviewers

**Criteria**:
- Expertise in MACC, industrial decarbonization, energy systems, or petrochemicals
- Published in related journals (Energy Policy, Applied Energy, Renewable & Sustainable Energy Reviews)
- Not co-authors, not from same institution, no recent collaborations
- Mix of regions (Asia, Europe, North America) and career stages

**Potential reviewers** (to be confirmed):
1. **MACC methodology expert**: [Name], [Institution], [Email], Expertise: Industrial MACC models
2. **Energy systems expert**: [Name], [Institution], [Email], Expertise: Grid capacity planning, renewable integration
3. **Petrochemical decarbonization expert**: [Name], [Institution], [Email], Expertise: Chemical industry net-zero pathways
4. **Korea energy policy expert**: [Name], [Institution], [Email], Expertise: Asian energy transitions
5. **Hydrogen economy expert**: [Name], [Institution], [Email], Expertise: Industrial hydrogen applications

**Opposed reviewers** (if applicable):
- Anyone with competing research interests
- Collaborators from past 2 years
- Anyone at your institution

---

### 💰 Article Processing Charge (APC)

**Carbon Neutrality APC**: ~$1,690 USD (2024 rate, verify current)

**Waivers/Discounts**:
- [ ] Check if LSE provides institutional discount (Springer compact agreements)
- [ ] Early career researcher discount (some journals offer)
- [ ] Low-income country discount (not applicable for Korea affiliation)
- [ ] Request waiver if unfunded research (explain in cover letter)

**Timeline**: Invoice after acceptance, payment before publication

---

### 📅 Estimated Timeline

| Milestone | Date | Status |
|-----------|------|--------|
| Draft complete | Nov 11, 2025 | ✅ DONE |
| Formatting & finalization | Nov 12-16, 2025 | ⏳ IN PROGRESS |
| Internal review (advisor) | Nov 17-19, 2025 | ⏳ TODO |
| Final revisions | Nov 20-21, 2025 | ⏳ TODO |
| **SUBMISSION** | **Nov 22, 2025** | **TARGET** |
| Editor assignment | Dec 1, 2025 | Expected |
| Peer review complete | Jan 15, 2026 | Expected |
| First decision | Jan 30, 2026 | Expected |
| Revisions submitted | Mar 15, 2026 | Expected |
| Final decision | Apr 15, 2026 | Expected |
| **PUBLICATION** | **May 2026** | **GOAL** |

---

### ✅ Final Pre-Flight Check (Day Before Submission)

- [ ] Read entire manuscript aloud (catches errors)
- [ ] Verify all figures open correctly (not corrupted)
- [ ] Verify all tables formatted properly
- [ ] Check all hyperlinks work (DOIs, URLs)
- [ ] Ensure all files named correctly
- [ ] Save backup of all files (Dropbox, Google Drive)
- [ ] Confirm co-authors approved final version
- [ ] Sleep on it, submit next morning with fresh eyes

---

**Current Status**: 🟢 **READY FOR FORMATTING PHASE**

**Completion**: ~80% complete (content done, formatting needed)

**Next immediate action**: Fill in author information and create formatted manuscript in journal template.

Would you like me to create the cover letter template next?
