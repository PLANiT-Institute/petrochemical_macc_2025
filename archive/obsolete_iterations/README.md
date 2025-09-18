# Obsolete Iterations Archive

This directory contains all the intermediate iterations during baseline development.

## What's Archived Here:
- Multiple CI data calibration attempts
- Various emission calculation approaches  
- Different facility filtering methods
- Process mismatch debugging files
- BAU pathway variations

## Final Working Files (Keep):
- `data/korean_petrochemical_final_baseline.xlsx` - Final realistic baseline (49.9 Mt CO₂)
- `outputs/facility_emissions_final_realistic.csv` - Final emissions data
- `create_final_realistic_baseline.py` - Final calibration script

## Key Lessons Learned:
1. Process mismatch (P-X, O-X, M-X) was the major issue, not double counting
2. All facilities should be active (no artificial lifetime filtering)  
3. Energy intensities needed ~3.6x scaling to reach realistic levels
4. Final baseline: 49.9 Mt CO₂ aligns with industry knowledge

Archived: 2025-09-18