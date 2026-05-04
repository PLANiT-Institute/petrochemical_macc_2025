# JCP Submission Package (Evidence-Locked)

## Package objective
This package upgrades the study to JCP submission level under a strict evidence policy:
- 243-facility scope
- infrastructure bottleneck hypothesis as primary research lens
- reproducible claim-to-data traceability

## Directory map
- `01_manuscript/`: manuscript files (draft + submission copy)
- `02_figures/`: main and supplementary figures
- `03_data/`: frozen source-of-truth data
- `04_reproducibility/`: run scripts and runbook
- `05_references/`: TeX/Bib and methodology references
- `06_verification/`: claim registry, checks, hypothesis tests, verification report
- `07_submission_docs/`: cover letter, highlights, statements, checklists

## Quick start
From package root (`submission_jcp_20260217`):

```bash
python3 06_verification/verify_submission_claims.py
```

Then review:
- `06_verification/verification_report.md`
- `06_verification/claim_checks.csv`
- `07_submission_docs/submission_file_list.md`
