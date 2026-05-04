# Energy Intensity Comparison Analysis

## Summary

This document compares our model's energy intensity values against literature sources.

## Key Findings

### 1. NCC Products (Ethylene, Propylene, Butadiene)

| Product | Our Model (GJ/t) | Literature (GJ/t) | Difference |
|---------|------------------|-------------------|------------|
| Ethylene | 40.31 | 14-29 | +38-188% |
| Propylene | 35.90 | 25-30 | +20-44% |
| Butadiene | 40.01 | 35-45 | Within range |

**Analysis:**
- Our model values are **higher than literature** for ethylene
- This is because our model includes ALL fuel inputs (Naphtha + LNG + Fuel Gas + Byproduct Gas)
- Literature often reports only the "Specific Energy Consumption" (SEC) for the main fuel source
- IEA reports 14-25 GJ/t as process energy, while full combustion energy is 35-45 GJ/t

**Sources:**
- LBNL (2008): 29.1 GJ/t ethylene - naphtha cracker best practice
- IEA (2018): 14-25 GJ/t - global average for steam crackers
- ACS (2023): 24.4-29.1 GJ/t - electric cracker comparison

### 2. BTX Products (Benzene, Toluene, Xylene)

| Product | Our Model (GJ/t) | Literature (GJ/t) | Difference |
|---------|------------------|-------------------|------------|
| Benzene | 6.39 | 1.5-4.0 | +60-326% |
| Toluene | 8.49 | 2.0-5.0 | +70-325% |
| Xylene | 10.23 | 2.5-5.5 | +86-309% |

**Analysis:**
- Our model values are **2-3x higher** than literature
- DOE (2006) reports ~2.4 MJ/kg for catalytic reforming
- Our model may be using allocated NCC co-product energy

**Sources:**
- DOE Industrial Technologies (2006): Catalytic reforming benchmarks
- Industry estimates: 2-5 GJ/t for aromatics extraction

### 3. Polymers (PP, HDPE, LDPE, PS, PVC)

| Product | Our Model (GJ/t) | Literature (GJ/t) | Scope Difference |
|---------|------------------|-------------------|------------------|
| PP | 0.005 | 73 | **Literature includes feedstock** |
| HDPE | 0.005 | 76 | **Literature includes feedstock** |
| LDPE | 0.007 | 83 | **Literature includes feedstock** |
| PS | 0.008 | 87 | **Literature includes feedstock** |
| PVC | 0.004 | 58 | **Literature includes feedstock** |

**Analysis:**
- **Critical difference in scope**: Our model only counts electricity for polymerization
- Literature values (PlasticsEurope Eco-profiles) are **cradle-to-gate** including:
  - Feedstock energy (~45 GJ/t for hydrocarbons)
  - Upstream monomer production
  - Polymerization process energy (~2-5 GJ/t)
- Our model correctly attributes upstream emissions to NCC/BTX facilities
- Polymer facilities in our model only add polymerization electricity (~1-2 kWh/t)

**Sources:**
- PlasticsEurope Eco-profiles (2014-2019): Comprehensive LCA data
- ACC (American Chemistry Council): VinylPlus sustainability reports

### 4. Intermediates (VCM, SM, TPA, EG, etc.)

| Product | Our Model (GJ/t) | Literature (GJ/t) | Notes |
|---------|------------------|-------------------|-------|
| VCM | 0.004 | 35 | Lit includes EDC production |
| SM | 0.004 | 58 | Lit includes ethylbenzene |
| TPA | 0.003 | 45 | Lit includes PX oxidation |
| EG | 0.003 | 25 | Lit includes EO production |

**Analysis:**
- Same scope difference as polymers
- Our model attributes energy to upstream chemical facilities
- Intermediate facilities only add process electricity

## Scope Clarification

### Our Model Approach:
```
Facility A (NCC): Produces ethylene → Energy: 40 GJ/t → Emissions: 2.0 tCO2/t
Facility B (Polymer): Converts ethylene to PE → Energy: 0.005 GJ/t → Emissions: 0.007 tCO2/t
```
- **Avoids double counting** by attributing energy at point of use
- Each facility's emissions reflect only its direct energy consumption

### Literature Approach (Cradle-to-gate):
```
PE production: All energy from oil extraction to final polymer = 76 GJ/t
```
- Includes feedstock energy (45 GJ/t)
- Includes all upstream process energy
- Useful for LCA but causes allocation challenges

## Recommendations

1. **NCC values are reasonable** when compared to full combustion energy literature
2. **BTX values may need review** - consider if allocation from NCC is correct
3. **Polymer values are correct** for our scope (facility-level direct energy)
4. **Document scope clearly** in any reporting to avoid confusion with LCA studies

## Data Sources Summary

| Source | Year | Products Covered | Scope |
|--------|------|------------------|-------|
| IEA Future of Petrochemicals | 2018 | Ethylene, Propylene | Process SEC |
| LBNL Best Practice | 2008 | Ethylene | Naphtha cracker SEC |
| ACS Ind. Eng. Chem. Res. | 2023 | Ethylene | Electric cracker |
| PlasticsEurope Eco-profiles | 2014-2019 | All polymers | Cradle-to-gate |
| DOE Industrial Technologies | 2006 | BTX aromatics | Process energy |
| ACC/VinylPlus | 2017 | PVC, VCM | Cradle-to-gate |
| IISRP | 2018 | Synthetic rubbers | Cradle-to-gate |
| ISOPA | 2017 | Isocyanates (MDI, TDI) | Cradle-to-gate |

## Conclusion

Our model uses **facility-level direct energy consumption** which is appropriate for:
- Emissions inventory and reporting
- Technology deployment analysis (where does abatement happen)
- Avoiding double-counting in facility aggregation

Literature values typically use **cradle-to-gate** scope which is appropriate for:
- Life Cycle Assessment (LCA)
- Product carbon footprinting
- Supply chain analysis

Both approaches are valid for their intended purposes.
