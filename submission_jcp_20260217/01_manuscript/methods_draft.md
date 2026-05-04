# Materials and Methods

## 3.1 Study scope and system boundary

The analysis uses facility-level simulation outputs covering **243 facilities** from **2025 to 2050** (`jcp_consolidated_results.csv` and `scenario_results.csv`). Scope 1 and Scope 2 emissions are included in the transition optimization boundary. Scope 3 emissions are excluded from optimization and handled as a limitation item.

## 3.2 Source data and single-truth policy

Two datasets are treated as source-of-truth inputs:

1. `03_data/jcp_consolidated_results.csv` for paper scenarios (S1/S2/S3)
2. `03_data/scenario_results.csv` for full scenario-set infrastructure comparison

All manuscript claims are mapped to these files through claim IDs and deterministic aggregation rules.

## 3.3 Scenario framework

### Paper scenarios (primary)
- **S1_Baseline_Trends**
- **S2_NetZero_HighAmbition**
- **S3_Tech_Constraints**

### Full scenarios (supporting infrastructure comparison)
- `shaheen_ncc_elec_*` (electricity-centered group)
- `shaheen_ncc_h2_*` (hydrogen-centered group)

## 3.4 Transition metrics and units

The manuscript reports four primary metrics:

- `total_cost_usd` -> BUSD/yr
- `abatement_tco2` -> MtCO2/yr
- `added_elec_mwh` -> TWh/yr
- `h2_demand_t` -> Mt/yr

MAC (`mac_usd_per_tco2`) is retained as a diagnostic indicator and is not used as the decision objective in this manuscript framing.

## 3.5 Aggregation and verification rules

### 3.5.1 Aggregation
For each scenario-year, values are summed across facilities.

### 3.5.2 Facility-count consistency rule
For the full scenario file, `facility_id == "0.0"` is treated as an artifact row and excluded from facility-count checks when counting unique facilities. Cost/abatement/infrastructure aggregates are still computed from scenario-year sums.

### 3.5.3 Claim pass criteria
Absolute error tolerance:

- Cost: ±0.10 BUSD
- Abatement: ±0.10 MtCO2
- Electricity demand: ±0.50 TWh
- Hydrogen demand: ±0.02 Mt

A claim is `PASS` when `abs(actual - expected) <= tolerance`.

## 3.6 Reproducibility workflow

Run from package root (`submission_jcp_20260217`):

```bash
python3 06_verification/verify_submission_claims.py
```

Generated outputs:

- `06_verification/claim_register.csv`
- `06_verification/claim_checks.csv`
- `06_verification/infrastructure_hypothesis_checks.csv`
- `06_verification/paper_yearly_summary.csv`
- `06_verification/full_yearly_summary.csv`
- `06_verification/verification_report.md`

## 3.7 Explicitly excluded from core evidence claims

The current submission package does not use unexecuted Monte Carlo or undocumented expert-validation outputs as evidence-bearing claims. Any such analyses are treated as future work unless executable artifacts are added.
