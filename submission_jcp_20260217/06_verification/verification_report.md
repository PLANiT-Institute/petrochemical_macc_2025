# Verification Report for JCP Submission Package

## 1) Evidence lock

- Source-of-truth files: `03_data/jcp_consolidated_results.csv`, `03_data/scenario_results.csv`
- Manuscript claims are linked by claim IDs (`C01`-`C09`).

## 2) Claim checks

- PASS: **9/9**
- Detailed file: `claim_checks.csv`
- Claim register: `claim_register.csv`

| claim_id | expected | actual | tolerance | unit | status |
|---|---:|---:|---:|---|---|
| C01 | 243.000 | 243.000 | 0.000 | count | PASS |
| C02 | 7.273 | 7.273 | 0.100 | BUSD/yr | PASS |
| C03 | 1.902 | 1.902 | 0.100 | MtCO2/yr | PASS |
| C04 | 25.043 | 25.043 | 0.100 | BUSD/yr | PASS |
| C05 | 51.505 | 51.505 | 0.100 | MtCO2/yr | PASS |
| C06 | 146.034 | 146.034 | 0.500 | TWh/yr | PASS |
| C07 | 4.546 | 4.546 | 0.020 | Mt/yr | PASS |
| C08 | 32.380 | 32.380 | 0.500 | TWh/yr | PASS |
| C09 | 16.994 | 16.994 | 0.100 | BUSD/yr | PASS |

## 3) Hypothesis-centric infrastructure checks

- File: `infrastructure_hypothesis_checks.csv`
- 2050 electricity-centered added electricity demand: **146.034 TWh/yr**
- 2050 hydrogen-centered hydrogen demand: **4.546 Mt/yr**
- 2050 hydrogen-centered added electricity demand: **32.380 TWh/yr**
- Interpretation: infrastructure requirements are first-order transition constraints.

## 4) Main manuscript anchor values

- S2 2030: cost **7.273 BUSD/yr**, abatement **1.902 MtCO2/yr**
- S2 2050: cost **25.043 BUSD/yr**, abatement **51.505 MtCO2/yr**

## 5) Reproducibility

- Deterministic rerun check: **PASS**
- Run command: `python3 06_verification/verify_submission_claims.py`

## 6) Generated outputs

- `claim_register.csv`
- `claim_checks.csv`
- `paper_yearly_summary.csv`
- `full_yearly_summary.csv`
- `infrastructure_hypothesis_checks.csv`
- `infrastructure_hypothesis_note.md`
- `table_main_cost_abatement_energy_2030_2040_2050.csv`
- `table_main_infrastructure_requirements_2050.csv`