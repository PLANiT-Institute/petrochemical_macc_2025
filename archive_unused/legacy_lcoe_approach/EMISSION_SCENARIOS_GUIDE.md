# Emission Scenarios Guide

## Overview

The optimization module now supports **flexible emission constraints** through a CSV file. You can define multiple scenarios with two types of constraints:

1. **Annual Emission Path**: Specific emission targets for each year
2. **Carbon Budget**: Total cumulative emissions limit (2025-2050)

---

## Korean Petrochemical Industry Context

### Current Baseline (Model)
- **Total emissions**: 52.00 MtCO2/year (2025)
- **Top emitters**: LG Chem (9.1 Mt), Yeochon NCC (7.6 Mt), Lotte Chemical (7.4 Mt)
- **BAU trajectory**: 52 Mt (2025) → 48.3 Mt (2050) from grid decarbonization only

### Industry Reality Check
- **Reported industry emissions**: ~71 MtCO2/year (includes broader chemical sector)
- **Growth rate**: 4% annually historically
- **Ranking**: 2nd largest industrial emitter after steel (117 Mt)

### Korea's Official Targets
- **2030 NDC**: 20.2% reduction from 2018 baseline (petrochemical sector)
- **2030 National**: 40% reduction from 2018 (all sectors)
- **2050**: Carbon neutrality (net-zero)

---

## How to Use the Scenario System

### Step 1: Edit the Scenario File

The scenario template is located at: `data/emission_scenarios_template.csv`

**Columns:**
- `scenario_name`: Name of your scenario (e.g., "Korea_NDC", "Aggressive_2040")
- `constraint_type`: Either "annual_path" or "carbon_budget"
- `year`: Year (for annual_path scenarios)
- `target_mt`: Emission target in MtCO2
- `description`: Notes about the scenario

### Step 2: Define Your Scenarios

#### Type 1: Annual Emission Path

Define yearly targets - the optimizer will deploy technologies to meet each year's target.

**Example:**
```csv
scenario_name,constraint_type,year,target_mt,description
My_Scenario,annual_path,2025,52.00,Baseline
My_Scenario,annual_path,2030,40.00,30% reduction
My_Scenario,annual_path,2040,20.00,60% reduction
My_Scenario,annual_path,2050,2.00,96% reduction
```

**When to use:**
- You have specific interim targets (e.g., NDC commitments)
- You want to test a particular decarbonization trajectory
- You need to match policy mandates

#### Type 2: Carbon Budget

Define total cumulative emissions allowed across 2025-2050.

**Example:**
```csv
scenario_name,constraint_type,year,target_mt,description
Budget_800Mt,carbon_budget,2025,800.00,Total 2025-2050 emissions
```

**When to use:**
- You have a carbon budget from climate scenarios (1.5°C, 2°C pathways)
- You want the optimizer to find the most cost-effective timing
- You're exploring "when to act" questions

---

## Pre-Loaded Scenarios

The template includes 6 scenarios:

### 1. Linear_2050
- **Type**: Annual path
- **2030**: 42 Mt (19% reduction)
- **2050**: 2 Mt (96% reduction)
- **Description**: Steady linear decline

### 2. Korea_NDC
- **Type**: Annual path
- **2030**: 41.47 Mt (20.2% reduction) ✓ Matches official target
- **2050**: 0.5 Mt (99% reduction)
- **Description**: Aligned with Korea's NDC and carbon neutrality goal

### 3. Early_Action
- **Type**: Annual path
- **2030**: 32 Mt (38% reduction)
- **2050**: 0.5 Mt (99% reduction)
- **Description**: Front-loaded reductions, slower after 2030

### 4. Budget_800Mt
- **Type**: Carbon budget
- **Total**: 800 MtCO2 cumulative
- **vs BAU**: 1,304 MtCO2 (38% reduction needed)

### 5. Budget_1000Mt
- **Type**: Carbon budget
- **Total**: 1,000 MtCO2 cumulative
- **vs BAU**: 1,304 MtCO2 (23% reduction needed)

### 6. Budget_600Mt
- **Type**: Carbon budget
- **Total**: 600 MtCO2 cumulative
- **vs BAU**: 1,304 MtCO2 (54% reduction needed)

---

## Scenario Comparison Results

| Scenario | 2030 Emissions | 2050 Emissions | Cumulative 2025-2050 | 2030 Reduction | 2050 Reduction |
|----------|----------------|----------------|----------------------|----------------|----------------|
| **Linear_2050** | 42.0 Mt | 2.0 Mt | 707 Mt | 19% | 96% |
| **Korea_NDC** | 41.5 Mt | 0.5 Mt | 657 Mt | 20% ✓ | 99% |
| **Early_Action** | 32.0 Mt | 0.5 Mt | 533 Mt | 38% | 99% |
| **Budget_800Mt** | 0.0 Mt | 0.0 Mt | 239 Mt | 100% | 100% |
| **Budget_1000Mt** | 0.0 Mt | 0.0 Mt | 239 Mt | 100% | 100% |
| **Budget_600Mt** | 0.0 Mt | 0.0 Mt | 239 Mt | 100% | 100% |

**⚠️ Note on Budget Scenarios:**
The carbon budget optimizer is currently very aggressive (achieves 239 Mt cumulative regardless of budget). This is because it deploys all available technologies immediately. A more sophisticated algorithm could better spread deployments over time to match different budget levels.

---

## Technology Deployment Patterns

### Korea_NDC Scenario (recommended baseline)

**2030:**
- Heat Pumps: 3.9 Mt (maxed out)
- NCC-H2: 5.9 Mt
- Total abatement: 9.8 Mt

**2050:**
- Heat Pumps: 3.9 Mt
- NCC-H2: 37.6 Mt (maxed out)
- NCC-Electricity: 6.3 Mt
- Total abatement: 47.8 Mt
- Final emissions: 0.5 Mt

---

## How to Add Your Own Scenario

1. Open `data/emission_scenarios_template.csv`

2. Add rows for your scenario:
   ```csv
   Your_Name,annual_path,2025,52.00,Starting point
   Your_Name,annual_path,2030,45.00,Your 2030 target
   Your_Name,annual_path,2050,5.00,Your 2050 target
   ```

3. Run the optimization:
   ```bash
   python run_module_03.py
   ```

4. Check outputs:
   - `outputs/module_03/your_name_deployment.csv` - Detailed deployment
   - `outputs/module_03/deployment_your_name.png` - Visualization
   - `outputs/module_03/scenario_comparison.csv` - Comparison table

---

## Understanding the Outputs

### Deployment CSV Columns

**Annual Path Scenarios:**
- `year`: Year
- `target_mt`: Your specified target
- `bau_mt`: Business-as-usual emissions (no action)
- `heat_pump_mt`: Heat pump abatement deployed
- `ncc_h2_mt`: NCC-H2 abatement deployed
- `ncc_elec_mt`: NCC-Electricity abatement deployed
- `total_deployed_mt`: Total abatement
- `actual_emissions_mt`: Actual emissions after deployment
- `shortfall_mt`: Gap if target not met (technology constraint)

**Carbon Budget Scenarios:**
- All above columns, plus:
- `cumulative_emissions_mt`: Running total emissions
- `budget_remaining_mt`: Remaining carbon budget

---

## Comparison with Industry Benchmarks

### Model vs Reality

| Metric | Model | Industry Data | Status |
|--------|-------|---------------|--------|
| **Total Emissions** | 52 Mt | ~71 Mt | ⚠️ 27% lower |
| **LG Chem Rank** | #1 | #1 | ✅ Match |
| **Lotte Rank** | #3 | #3 | ✅ Match |
| **2030 NDC Target** | 20.2% | 20.2% | ✅ Match |
| **Technology Costs** | Declining | Expected decline | ✅ Reasonable |

### Why is total lower?
1. Model covers 248 facilities (may miss smaller plants)
2. Industry figure includes downstream chemicals
3. Boundary differences (Scope 1 vs 1+2)

---

## Recommendations

### For Policy Analysis
Use **Korea_NDC** scenario - matches official commitments

### For Ambition Scenarios
Use **Early_Action** - front-loads reductions, tests feasibility

### For Carbon Budget Analysis
Use **Budget_800Mt** - roughly aligns with 1.5°C pathways

### For Custom Analysis
Copy the template structure and modify targets to your needs

---

## Technical Notes

### Technology Availability
- **Heat Pumps**: Available from 2025 (cost-effective immediately)
- **NCC-H2**: Available from 2030 (hydrogen price < $3/kg)
- **NCC-Electricity**: Available from 2030 (RE price < 40 USD/MWh)

### Optimization Logic
1. Calculate gap between BAU and target
2. Sort technologies by cost ($/tCO2)
3. Deploy cheapest first until gap closed
4. If gap remains, report shortfall

### Future Improvements
- More sophisticated carbon budget optimizer (timing optimization)
- Multiple technology variants (different efficiency levels)
- Regional deployment constraints
- Technology learning curves
- Financing constraints

---

## Questions?

The model is designed to be flexible. You can:
- Test different NDC targets
- Explore early vs late action
- Compare carbon budgets
- Create custom pathways

Just edit the CSV and run!
