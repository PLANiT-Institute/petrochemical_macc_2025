# Model Discussion for Academic Paper Preparation

**Status**: Project cleaned, NCC logic reviewed, ready for discussion
**Date**: 2025-10-29

---

## ✅ CLEANUP COMPLETE

### Archived Unused Files:
- **6 unused modules** → `archive_unused_20251029/modules/`
  - optimization.py (old version)
  - financial.py, sensitivity.py, sensitivity_corrected.py
  - regional_energy_tracker.py, visualizations.py

- **9 unused data files** → `archive_unused_20251029/data/`
  - Legacy files, output files, redundant data

### Clean Project Structure Now:

**Modules (6 files only)**:
```
modules/
├── __init__.py
├── baseline.py           # Module 1: Baseline calculation
├── macc.py              # Module 2: MACC analysis
├── optimization_v2.py    # Module 3: Cost optimization (corrected)
├── utils.py             # Shared utilities
└── data_manager.py      # Data loading
```

**Data (17 core files)**:
- facility_database.csv, energy_intensities.csv, emission_factors.csv
- technology_parameters.csv
- h2_price_trajectory.csv, re_price_trajectory.csv, fuel_price_trajectory.csv
- grid_emission_trajectory.csv, demand_growth_trajectory.csv
- emission_scenarios_clean.csv, heat_pump_applicability.csv
- Plus corrected versions and backups

**Total Model**: ~2,000 lines of code (very manageable for academic paper)

---

## 🔍 NCC LOGIC - DEEP REVIEW COMPLETED

Full analysis in: **docs/NCC_LOGIC_DEEP_REVIEW.md** (5,000+ words)

### Key Findings:

#### 1. ✅ What's Good (Keep As Is):
- **NCC identification** is simple and correct
- **Mutual exclusivity** is well-implemented
- **Industry-wide technology selection** is a reasonable simplification
- **Capital lock-in** assumption is realistic

#### 2. ⚠️ What Needs Discussion:

**A. Cost Calculation Methodology**

**Current approach**:
```python
MACC = CAPEX_annual + OPEX_annual + New_Fuel_Cost
```
Only counts cost of new fuel (H2 or RE electricity), does NOT subtract baseline fuel savings (LNG/fuel gas)

**Standard MACC approach**:
```python
MACC = CAPEX_annual + OPEX_annual + (New_Fuel_Cost - Baseline_Fuel_Cost)
```
Counts both new fuel cost AND savings from displaced fuels

**Impact if we change**:
- NCC technologies become $50-100/tCO2 cheaper
- More comparable to other MACC studies
- Better academic credibility

**Question**: Should we change to standard methodology?
- My recommendation: **YES** (for academic paper)

---

**B. Energy Balance Verification**

Found potential inconsistency:
- Model reports: 1.59 tCO2/ton abatement for NCC-Electricity
- My calculation: ~0.38 tCO2/ton abatement

**Need to verify**:
1. What does `baseline_data['total_emissions_tco2_per_ton']` actually return?
2. Is naphtha emission counted as feedstock or combustion?
3. Are the energy balance calculations internally consistent?

**Action**: I can trace through the code to verify (should take 30 minutes)

**Question**: Should I do this verification now?
- My recommendation: **YES** (critical for paper credibility)

---

**C. Facility vs Industry-Wide Technology Selection**

**Current**: All facilities choose SAME technology (industry-wide)
**Alternative**: Each facility chooses independently

**Trade-off**:
- Current: Simpler, easier to explain, realistic (standardization)
- Alternative: More detailed, captures heterogeneity, more complex

**Question**: Which approach for academic paper?
- My recommendation: **Keep current** (simplicity is good for reproducibility)

---

## 📋 DISCUSSION QUESTIONS

### Question 1: Model Framing for Paper

**Option A - "Simple & Transparent MACC Model"**
- Emphasize: Clarity, reproducibility, minimal assumptions
- Message: "Anyone can understand and replicate this model"
- Audience: Broad (engineers, economists, policymakers)

**Option B - "Comprehensive Facility-Level MACC"**
- Emphasize: Detail, 248 facilities, precision
- Message: "Most detailed petrochemical MACC model"
- Audience: Specialized (energy modelers, researchers)

**Which framing do you prefer?**
- My recommendation: **Option A** (higher impact, broader audience)

---

### Question 2: Methodological Changes

**Should we make these changes before writing paper?**

1. **Cost Methodology**: Change to standard MACC (include fuel savings)
   - Impact: NCC tech $50-100/tCO2 cheaper
   - Effort: 2 hours to update + rerun model
   - My vote: **YES**

2. **Energy Balance Verification**: Trace through calculations
   - Impact: Ensure consistency, fix any errors
   - Effort: 1 hour analysis
   - My vote: **YES**

3. **Facility-Level Selection**: Replace industry-wide with facility-level
   - Impact: More detail, more complex
   - Effort: 4-6 hours to implement + rerun
   - My vote: **NO** (unnecessary complexity)

---

### Question 3: Paper Structure

**Preliminary Outline**:

1. **Introduction**
   - Problem: Korea petrochemical decarbonization
   - Gap: No comprehensive MACC model for sector
   - Contribution: First detailed facility-level MACC

2. **Methodology**
   - Energy-based MACC approach (not LCOE)
   - Three-module structure (Baseline → MACC → Optimization)
   - Key simplifications and assumptions

3. **Data**
   - 248 facilities, 4 technologies
   - Data sources (all cited, IEA/IRENA/IPCC)
   - Corrections applied (this is actually a strength!)

4. **Results**
   - Baseline: 66.2 MtCO2 (corrected)
   - Technology costs and selection
   - Optimal pathway: $30.4B investment, 38% reduction

5. **Policy Implications**
   - Target revision needed (90% → 35-40%)
   - Electricity infrastructure priority
   - No hydrogen infrastructure needed

6. **Discussion**
   - Comparison to other studies
   - Sensitivity to key assumptions
   - Limitations

**Does this structure make sense?**
- Anything missing?
- Any sections to emphasize/de-emphasize?

---

### Question 4: Transparency vs Complexity

**Transparency**: Show all data, all assumptions, all code
- Pro: Maximum reproducibility
- Con: Paper may seem "too simple"

**Sophistication**: Add complexity (stochastic, dynamic programming, etc.)
- Pro: Looks more sophisticated
- Con: Less reproducible, harder to understand

**Where do you want to be on this spectrum?**
- My recommendation: **80% transparency, 20% sophistication**
  - Show: All data sources, clear methodology
  - Downplay: Implementation details, algorithm complexity
  - Add: One sensitivity analysis to show robustness

---

## 🎯 PROPOSED NEXT STEPS

### Immediate (Today):
1. **Discuss**: Your answers to questions above
2. **Decide**: Which methodological changes to make
3. **Verify**: Energy balance (if you agree)

### Short-term (This Week):
4. **Update model** (if changes needed): Implement agreed changes
5. **Rerun model**: With final methodology
6. **Validate results**: Ensure everything consistent

### Medium-term (Next Week):
7. **Write methodology**: Clear explanation of model
8. **Create figures**: Publication-quality visualizations
9. **Draft paper**: Introduction + methodology sections

---

## 📄 DOCUMENTS READY FOR YOUR REVIEW

1. **NCC_LOGIC_DEEP_REVIEW.md** (5,000+ words)
   - Detailed analysis of NCC logic
   - Identifies issues and simplification opportunities
   - Specific questions for discussion

2. **MODEL_STRUCTURE_FOR_PAPER.md**
   - Clean model structure documentation
   - Ready to adapt for methodology section
   - Lists all core files and their purposes

3. **FINAL_COMPREHENSIVE_REPORT_2025_10_29.docx** (35+ pages)
   - Complete results with corrected data
   - Can be adapted for results section

4. **DATA_VALIDATION_REPORT_2025_10_29.md** (26 pages)
   - All data sources cited
   - Can be adapted for data section

---

## 💬 LET'S DISCUSS!

I'm ready to discuss any of these topics:
1. Cost methodology - should we change?
2. NCC logic - is it simple enough?
3. Paper framing - transparency vs sophistication?
4. Next steps - what should we prioritize?

**What would you like to discuss first?**

Key questions:
- Do you want to change the cost methodology to include fuel savings?
- Should I verify the energy balance calculations?
- What's your preferred framing for the academic paper?
- Any concerns about the current NCC logic?

I'm here to help make this model as clear and publishable as possible! 🚀
