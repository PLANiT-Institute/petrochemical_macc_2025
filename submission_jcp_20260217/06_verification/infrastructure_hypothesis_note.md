# Infrastructure Hypothesis Note

Hypothesis: pathway feasibility is constrained by infrastructure (grid + hydrogen supply) rather than static cost ordering alone.

Operational check per year:
- electricity_centered added_elec_twh > hydrogen_centered added_elec_twh
- hydrogen_centered h2_mt > 0
- electricity_centered h2_mt ~= 0

Result is recorded in `interpretation_flag` of `infrastructure_hypothesis_checks.csv`.