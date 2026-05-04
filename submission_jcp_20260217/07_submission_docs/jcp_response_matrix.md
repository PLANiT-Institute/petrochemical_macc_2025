# JCP Response Matrix (Claim-to-Evidence)

| claim_id | Manuscript location | Claim summary | Evidence file | Verification rule |
|---|---|---|---|---|
| C01 | Abstract, Methods | Coverage: 243 facilities, 2025-2050 | `03_data/jcp_consolidated_results.csv` | `nunique(facility_id)==243`, year range check |
| C02 | Abstract, Results | S2 2030 cost = 7.273 BUSD/yr | `06_verification/claim_checks.csv` | scenario-year sum of `total_cost_usd` / 1e9 |
| C03 | Abstract, Results | S2 2030 abatement = 1.902 MtCO2/yr | `06_verification/claim_checks.csv` | scenario-year sum of `abatement_tco2` / 1e6 |
| C04 | Abstract, Results | S2 2050 cost = 25.043 BUSD/yr | `06_verification/claim_checks.csv` | scenario-year sum of `total_cost_usd` / 1e9 |
| C05 | Abstract, Results | S2 2050 abatement = 51.505 MtCO2/yr | `06_verification/claim_checks.csv` | scenario-year sum of `abatement_tco2` / 1e6 |
| C06 | Abstract, Results | Elec-centered 2050 added electricity = 146.034 TWh/yr | `06_verification/infrastructure_hypothesis_checks.csv` | mean(`*_elec_*`, 2050, `added_elec_twh`) |
| C07 | Abstract, Results | H2-centered 2050 hydrogen demand = 4.546 Mt/yr | `06_verification/infrastructure_hypothesis_checks.csv` | mean(`*_h2_*`, 2050, `h2_mt`) |
| C08 | Abstract, Results | H2-centered 2050 added electricity = 32.380 TWh/yr | `06_verification/infrastructure_hypothesis_checks.csv` | mean(`*_h2_*`, 2050, `added_elec_twh`) |
| C09 | Results | S3-S2 2050 cost premium = 16.994 BUSD/yr | `06_verification/claim_checks.csv` | `S3 total_cost_busd - S2 total_cost_busd` |
