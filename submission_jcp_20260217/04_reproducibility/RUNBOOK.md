# Reproducibility Runbook

## Scope
This runbook reproduces the claim-level evidence package used by the manuscript in `01_manuscript/`.

## Source-of-truth data
- `../03_data/jcp_consolidated_results.csv` (paper scenarios)
- `../03_data/scenario_results.csv` (full scenarios for infrastructure comparison)

## Commands
Run from `submission_jcp_20260217` root:

```bash
python3 06_verification/verify_submission_claims.py
python3 04_reproducibility/build_final_tex_pdf.py
```

## Generated outputs
- Final manuscript rendering:
  - `01_manuscript/manuscript_final_clean.md`
  - `01_manuscript/manuscript_final.tex`
  - `01_manuscript/manuscript_final.pdf`
- Claim mapping and checks:
  - `06_verification/claim_register.csv`
  - `06_verification/claim_checks.csv`
- Hypothesis checks:
  - `06_verification/infrastructure_hypothesis_checks.csv`
  - `06_verification/infrastructure_hypothesis_note.md`
- Summary tables:
  - `06_verification/table_main_cost_abatement_energy_2030_2040_2050.csv`
  - `06_verification/table_main_infrastructure_requirements_2050.csv`
- Reproducibility report:
  - `06_verification/verification_report.md`
- Main manuscript figures:
  - `02_figures/fig_main_added_electricity_trajectory.png`
  - `02_figures/fig_main_hydrogen_trajectory.png`
  - `02_figures/fig_main_infrastructure_tradeoff_2050.png`

## Notes
- Legacy MAC figures are preserved as supplementary diagnostics.
- The verification script enforces deterministic rerun checks.
- In this environment, LaTeX engines are unavailable, so the final PDF is rendered with `reportlab`.
