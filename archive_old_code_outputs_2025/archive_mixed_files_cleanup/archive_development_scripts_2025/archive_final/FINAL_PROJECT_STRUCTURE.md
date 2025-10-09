# Korean Petrochemical MACC - Final Project Structure

## Essential Files (Current Working Directory)

### Core Scripts
- `emission_pathway_analysis.py` - Main emission pathway analysis (25 & 30-year facility lifetimes)
- `create_korea_scale_baseline.py` - Creates Korea-scale 52 Mt CO₂ baseline
- `generate_updated_macc.py` - Generates MACC curve visualization
- `update_korea_scale_macc.py` - Updates MACC for 52 Mt baseline
- `MACC_ANALYSIS_SUMMARY.md` - Complete analysis documentation

### Data (Essential)
- `data/korean_petrochemical_macc_optimization.xlsx` - **Primary optimization database**
  - Contains: source facilities, CI data, CI2 emission factors, MACC Template, TechOptions
  - Baseline: 52.0 Mt CO₂ (Korea-scale)
  - Technologies: 16 alternatives (no CCS, includes heat pump)

### Outputs (Essential)
- `outputs/facility_emissions_korea_scale_final.csv` - Korea-scale facility emissions
- `outputs/korean_petrochemical_macc_curve_updated.png` - Final MACC curve visualization
- `outputs/korean_petrochemical_macc_curve_updated.pdf` - MACC curve (publication ready)
- `outputs/macc_analysis_updated.csv` - Complete MACC technology data
- `outputs/bau_emission_pathway_25yr_final.csv` - 25-year facility lifetime BAU pathway
- `outputs/bau_emission_pathway_30yr_final.csv` - 30-year facility lifetime BAU pathway
- `outputs/bau_emission_pathways_final.png` - BAU pathway visualization
- `outputs/facility_emissions_final_realistic.csv` - Realistic facility emissions
- `outputs/facility_retirement_schedule.csv` - Facility retirement timeline
- `outputs/retirement_by_year.csv` - Annual retirement summary

## Korea-Scale Baseline Summary (52.0 Mt CO₂)

### Chain Breakdown
- **Olefins**: 26.5 Mt CO₂ (Ethylene 17.0, Propylene 8.0, Butadiene 1.5)
- **Aromatics**: 14.5 Mt CO₂ (P-X 8.0, Benzene 3.0, Others 3.5)
- **Polymers**: 7.0 Mt CO₂ (polymerization utilities only)
- **Chlor-vinyls**: 4.0 Mt CO₂ (EDC/VCM/PVC, SM, etc.)

### MACC Technologies (16 total)
1. **Energy Efficiency Package** (EE_001): -$69/tCO₂, 15.6 Mt CO₂/year
2. **Industrial Heat Pump Systems** (HP_001): $10/tCO₂, 7.8 Mt CO₂/year
3. **Process Intensification** (TPA_001): $171/tCO₂, 1.0 Mt CO₂/year
4. **Heat Integration & Recovery** (PE_002): $209/tCO₂, 2.6 Mt CO₂/year
5. **Bio-ethylene** (ETH_003): $254/tCO₂, 7.8 Mt CO₂/year
6. **Bio-propylene** (PROP_002): $264/tCO₂, 6.2 Mt CO₂/year
7. **Methanol-to-Olefins** (ETH_004): $359/tCO₂, 7.8 Mt CO₂/year
8. **Advanced Catalysts** (PE_001): $361/tCO₂, 2.6 Mt CO₂/year
9. **Electric Propane Dehydrogenation** (PROP_001): $388/tCO₂, 6.2 Mt CO₂/year
10. **Electric Heating Polymerization** (PP_001): $405/tCO₂, 2.1 Mt CO₂/year
11. **Green Hydrogen Boilers** (H2_001): $503/tCO₂, 13.0 Mt CO₂/year
12. **Bio-based p-Xylene** (PX_001): $520/tCO₂, 1.6 Mt CO₂/year
13. **Electric Steam Cracking** (ETH_001): $579/tCO₂, 7.8 Mt CO₂/year
14. **Green H2 Steam Cracking** (ETH_002): $795/tCO₂, 7.8 Mt CO₂/year
15. **Electric Reforming** (BTX_001): $1,167/tCO₂, 4.2 Mt CO₂/year
16. **Bio-aromatics from Lignin** (BTX_002): $1,594/tCO₂, 4.2 Mt CO₂/year

**Total Abatement Potential**: 98.3 Mt CO₂/year

## Archived Files

### Archive Structure
- `archive/non_essential_code/` - Development and calibration scripts
- `archive/non_essential_data/` - Intermediate data files and directories
- `archive/non_essential_outputs/` - Draft outputs and iterations
- `archive/obsolete_iterations/` - Baseline development iterations
- `archive/legacy_model/` - Original optimization model (Pyomo)

### Key Lessons Learned (from archived iterations)
1. Process mismatch (P-X, O-X, M-X) was the major issue, not double counting
2. All facilities should be active (no artificial lifetime filtering)  
3. Energy intensities needed ~3.6x scaling to reach realistic levels
4. Final Korea-scale baseline: 52.0 Mt CO₂ aligns with industry knowledge

## Next Steps for Optimization Model
1. Use `korean_petrochemical_macc_optimization.xlsx` as input
2. Implement cost-effective emission pathway planning
3. Target Korean petrochemical emission goals:
   - 2030: 35.0 Mt CO₂ (30% reduction)
   - 2040: 15.0 Mt CO₂ (70% reduction)  
   - 2050: 2.5 Mt CO₂ (95% reduction)

---
*Final structure created: September 2025*
*Ready for optimization model development*