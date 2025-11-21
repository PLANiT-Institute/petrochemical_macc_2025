# Technology Parameter Update Log

**Date**: 2025-11-11
**Update Type**: Literature validation and correction
**Archive Location**: `archive_pre_literature_update_20251111/`

---

## Summary of Changes

| Technology | Parameter | OLD Value | NEW Value | Change | Source |
|------------|-----------|-----------|-----------|--------|--------|
| **Heat Pump** | CAPEX 2025 | $900 | **$800** | -11% | Kosmadakis 2020, Obrist 2023, Kloo 2024 |
| | TRL | 9 | **8** | -1 | Commercial but deployment stage |
| **NCC-H₂** | **H₂ consumption** | **0.2** | **0.56** | **+180%** 🚨 | Chen 2024, Gupta 2023, Park 2022 |
| | CAPEX 2025 | $1,725 | **$1,550** | -10% | Literature mean |
| | TRL | 7 | **5** | -2 | Pre-commercial status |
| **NCC-Electricity** | CAPEX 2030 | $1,560 | **$1,350** | -13% | Learning curve correction |
| | TRL | 6 | **7** | +1 | Pilots completed (BASF 2024) |
| **RE PPA** | No changes | - | - | - | Parameters validated |

---

## Critical Update: NCC-H₂ Hydrogen Consumption

### **THE KEY CHANGE**: H₂ 0.2 → 0.56 ton/ton ethylene

**Why this matters:**
- Literature consensus: 0.50-0.65 ton H₂/ton ethylene
- Your original 0.2 was **~65% too low**
- Under-estimated H₂ demand by ~180%

**Impact on scenarios:**
- Shaheen + NCC-H₂: H₂ demand 31.5 kt/yr → **88.2 kt/yr**
- Cost increase: **+$5-6B** for Shaheen scenario
- **Cost advantage of NCC-H₂ eliminated or reversed**

---

## Expected Impact on Results

### **Before Update** (H₂ = 0.2):
| Scenario | Cost | Status |
|----------|------|--------|
| Shaheen + NCC-H₂ | $53.9B | Cheapest H₂ option |
| Shaheen + NCC-Elec | $58.8B | More expensive |
| Gap | -$4.9B (-8.3%) | H₂ advantage |

### **After Update** (H₂ = 0.56):
| Scenario | Cost (Projected) | Status |
|----------|------------------|--------|
| Shaheen + NCC-H₂ | ~$59-60B | Similar to Elec |
| Shaheen + NCC-Elec | $58.8B | Potentially cheaper! |
| Gap | ~$0-1B | **Cost parity** 🎯 |

---

## Next Steps

1. ✅ Parameters updated in `data/technology_parameters.csv`
2. ⏳ Re-run all 6 scenarios: `python run_all_scenarios_v3.py`
3. ⏳ Compare old vs new results
4. ⏳ Update Korean report with new findings
5. ⏳ Update LaTeX paper with literature review + new results

---

## Validation

All parameter updates based on peer-reviewed literature (2020-2025):
- Heat Pump: 5 sources
- NCC-H₂: 4 sources
- NCC-Electricity: 4 sources + BASF pilot data
- RE PPA: IRENA 2024, BNEF 2024

**Total references**: 36 sources from literature review (petrochem_review.tex)

---

**Next**: Run `python run_all_scenarios_v3.py` to generate updated results
