
# Korea Petrochem — Cost-Effective Emissions Pathway (Pyomo LP, NPV)

**Scope:** Pure petrochem (Scope 1+2). **Years:** 2023–2050 (annual).  
**Goal:** Minimize **NPV of total system cost** while meeting **annual emissions targets**, with vintaging, ramp, start-year, caps, mutual exclusivity, and coupling rules.

---

## Mathematical formulation

Sets: years \(t \in T\), technologies \(i \in I\)

Parameters (per \(i,t\)): `activity[i,t]`, `cap[i,t]` \(\in [0,1]\), `abat[i,t]` (tCO₂/activity),  
`capex[i,t]`, `fixed[i,t]`, `var[i,t]`, lifetimes `life[i]`, commercialization `start[i]`, ramp `ramp[i]`.  
Annual required abatement \(req_t = \max(0, Baseline - Target_t)\cdot 10^6\).  
Discount factor \(DF_t = 1/(1+r)^{t-t_0}\).

Decision variables:  
- `build[i,t] ≥ 0` (annual new share), `share[i,t] ≥ 0` (in-service share), `a[i,t] ≥ 0` (abatement),  
- optional `shortfall[t] ≥ 0` (diagnostic), penalized heavily.

Constraints:  
1. **Vintaging:** \(share_{i,t} = \sum_{\tau\le t, \; t-\tau < life_i} build_{i,\tau}\)  
2. **Start-year:** \(t < start_i \Rightarrow build_{i,t} = 0\)  
3. **Ramp:** \(build_{i,t} \le ramp_i\)  
4. **Max adoption:** \(share_{i,t} \le cap_{i,t}\)  
5. **Abatement:** \(a_{i,t} = share_{i,t}\cdot activity_{i,t}\cdot abat_{i,t}\)  
6. **Targets:** \(\sum_i a_{i,t} + shortfall_t \ge req_t\)  
7. **Mutual exclusivity (groups \(G\)):** \(\sum_{i\in G} share_{i,t} \le 1\)  
8. **Coupling:** \(share_{primary,t} \le share_{secondary,t}\)

Objective (NPV):  
\[\min \sum_t DF_t\left(\sum_i \big(\tfrac{capex_{i,t}}{life_i}+fixed_{i,t}+var_{i,t}\big)\cdot share_{i,t}\cdot activity_{i,t} \;+\; M\cdot shortfall_t \right)\]

Default \(M=10^{15}\) KRW/tCO₂ → shortfalls effectively disallowed.

---

## Install & run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Solver: HiGHS (pip) preferred, or GLPK/ CBC installed system-wide.
python -m petrochem.solver --excel examples/kr_petchem_netzero_model_validated_v14.xlsx \
  --discount-rate 0.05 --allow-slack --slack-penalty 1e15 --plots
# Options:
#   --years 2023 2050  # range or explicit list
#   --no-slack         # enforce feasibility; no shortfall var
#   --ramp-default 0.2 # if missing in Excel
#   --solver highs|glpk|cbc|auto
```
Outputs in `outputs/`: `summary.csv`, `plan_{year}.csv`, `cost_curve_{year}.png`.

---

## Excel schema (inputs)

- `Emissions_Target(Year, Target_MtCO2e)`
- `Baseline_Assumptions(Parameter, Value)` with `Total_Scope1plus2_MtCO2e_2023` or a `Baseline_2023` sheet with Scope1/2 columns
- `MACC_Template(TechID, Ref_Year, Eligible_Activity_Volume, Max_Adoption_Share, Abatement_tCO2_per_activity, Cost_* …)`
- Optional `TechOptions(TechID, Lifetime_years, StartYear_Commercial, RampUpSharePerYear)`
- Optional `TechLinks(RuleType, PrimaryTech, SecondaryTech)` for `MutuallyExclusive` or `Coupling` rules

Interpolation is linear across missing years (e.g., if only 2030/2040/2050 are given).
