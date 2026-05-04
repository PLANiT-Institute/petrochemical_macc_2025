# JCP Submission Checklist (Transition Pathway Focus)

## 0) Core Framing Lock
- [ ] Main objective statement is consistent across title, abstract, introduction, and conclusions.
- [ ] Objective is stated as: "net-zero transition pathway and policy/finance strategy".
- [ ] MAC/MACC is described only as an analytical indicator, not the research goal.

## 1) Manuscript Files
- [ ] Final manuscript source: `paper_jcp/manuscript_draft.md`
- [ ] Methods source: `paper_jcp/methods_draft.md`
- [ ] Literature source: `paper_jcp/literature_review_draft.md`
- [ ] Submission DOCX: `paper_jcp/manuscript_journal_ready.docx`

## 2) Data and Reproducibility
- [ ] Scenario runner for paper is executable: `paper_jcp/run_paper_experiment.py`
- [ ] Consolidated results are attached: `paper_jcp/results/jcp_consolidated_results.csv`
- [ ] Data dependency documentation attached: `docs/DATA_SOURCES.md`, `docs/DATA_USAGE.md`
- [ ] Versioned requirements included: `requirements.txt`
- [ ] Reproducibility statement added to manuscript (code/data availability section).

## 3) Quantitative Consistency Checks
- [ ] 2030 investment number aligns with results table and text.
- [ ] 2050 total annual transition cost aligns with results table and text.
- [ ] 2050 abatement number aligns with results table and text.
- [ ] Facility coverage is consistent in all sections (resolve 39-major vs 243-facility wording).
- [ ] Cost metric definition is explicit (simple mean, weighted mean, or model-derived indicator).

## 4) Figures and Tables
- [ ] Every figure is cited in text and has a complete caption.
- [ ] Figure resolution and readability meet journal requirements.
- [ ] Table units are explicit (BUSD, MtCO2, USD/tCO2, etc.).
- [ ] Supplementary tables include scenario definitions and key parameter values.

## 5) Policy and Discussion Quality
- [ ] Policy implications are tied directly to model outputs (not generic claims).
- [ ] Infrastructure constraints and uncertainty ranges are quantified in the discussion.
- [ ] Limitations clearly state boundary exclusions and future work.

## 6) JCP Submission Package
- [ ] Cover letter prepared: `paper_jcp/cover_letter_jcp_draft.md`
- [ ] Highlights prepared (3-5 bullets, journal style).
- [ ] Suggested reviewers list prepared (with conflict-free rationale).
- [ ] Conflict of interest statement prepared.
- [ ] Author contribution (CRediT) statement prepared.
- [ ] Funding and acknowledgments finalized.

## 7) Final Pre-Submission Gate
- [ ] One-pass proofreading by a co-author.
- [ ] One-pass technical verification by model owner.
- [ ] One-pass formatting verification against JCP guide.
- [ ] Final files exported and checksums archived.
