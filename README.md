
# Korea Petrochemical MACC Model — Fixed Band Structure with Alternative Technologies

**Model Type:** Band-Based Marginal Abatement Cost Curve (MACC) optimization  
**Scope:** Korea petrochemical industry (Scope 1+2 emissions)  
**Timeline:** 2023–2050 (annual optimization)  
**Objective:** Minimize NPV of total system cost while meeting emissions targets

## 🎯 Model Philosophy

**Fixed Band Structure:** The model maintains realistic industrial constraints where temperature bands (HT/MT/LT) are determined by process physics and cannot transition between each other.

**Within-Band Substitution:** Alternative technologies can only substitute baseline technologies within the same temperature band, representing realistic industrial retrofit and replacement options.

## 🏗️ Core Model Structure

### Technology Bands (Fixed Baseline)

| Tech Group | Band | Process Description | Baseline Activity | Emission Intensity |
|------------|------|---------------------|------------------|-------------------|
| **NCC** (Naphtha Cracking Complex) | HT | Pyrolysis furnace (800°C+) | 3,500 kt/year | 2.85 tCO2/t |
| | MT | Distillation/reboilers (150-400°C) | 2,800 kt/year | 1.23 tCO2/t |
| | LT | Compression/refrigeration | 1,200 kt/year | 0.65 tCO2/t |
| **BTX** (Benzene, Toluene, Xylene) | HT | Catalytic reforming furnace | 1,200 kt/year | 1.52 tCO2/t |
| | MT | Separation columns | 800 kt/year | 0.89 tCO2/t |
| | LT | Product compression | 1,100 kt/year | 0.48 tCO2/t |
| **C4** (C4 Chemicals) | HT | Butadiene extraction | 450 kt/year | 2.21 tCO2/t |
| | MT | C4 fractionation | 350 kt/year | 0.98 tCO2/t |
| | LT | Product cooling | 200 kt/year | 0.54 tCO2/t |

**Total Baseline:** 18.7 MtCO2/year across 11,600 kt/year production

### Alternative Technologies (Band-Specific Substitution)

- **HT Alternatives:** E-cracker, H2-furnace (high-temperature processes)
- **MT Alternatives:** Heat pump, Electric heater (medium-temperature processes)  
- **LT Alternatives:** Heat pump, Electric motor (low-temperature, electricity-focused)

**Key Principle:** No HT→MT→LT transitions allowed; only baseline→alternative within each band.

## 🔧 Mathematical Formulation (Corrected)

### Sets
- \(T\): Years (2023-2050)
- \(I\): Alternative technologies  
- \(B\): Baseline bands (fixed capacity and emission intensity)

### Parameters
- \(Activity_b\): Fixed baseline activity in band \(b\) (kt/year)
- \(EI_b\): Fixed emission intensity in band \(b\) (tCO2/t)
- \(CAPEX_{i,t}\): Technology CAPEX (Million USD per kt/year capacity)
- \(OPEX_{i,t}\): Technology OPEX delta (USD per tonne production)
- \(Abate_{i,t}\): Abatement potential (tCO2 per tonne production)
- \(MaxApp_i\): Maximum applicability within target band

### Decision Variables (Corrected Scale Units)
- \(InstallCap_{i,t}\): New capacity installed (kt/year)
- \(TotalCap_{i,t}\): Total available capacity (kt/year)  
- \(Production_{i,t}\): Actual production (kt/year)
- \(Abatement_{i,t}\): Abatement achieved (tCO2/year)

### Key Constraints
1. **Fixed Band Capacity:** \(\sum_i Production_{i,t} \leq Activity_b \quad \forall b, t\)
2. **Capacity Evolution:** \(TotalCap_{i,t} = \sum_{\tau \leq t, t-\tau < Lifetime_i} InstallCap_{i,\tau}\)
3. **Production Limits:** \(Production_{i,t} \leq TotalCap_{i,t}\)
4. **Abatement Calculation:** \(Abatement_{i,t} = Production_{i,t} \times Abate_{i,t} \times 1000\)
5. **Emissions Targets:** \(\sum_i Abatement_{i,t} \geq Required_t\)

### Objective Function
Minimize NPV of total system cost:
\[\min \sum_t DF_t \left( \sum_i \left( InstallCap_{i,t} \times CAPEX_{i,t} \times CRF_i + Production_{i,t} \times OPEX_{i,t} / 1000 \right) \right)\]

---

## 🚀 Quick Start

### Prerequisites
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Solver: GLPK (recommended) or other linear programming solvers
```

### Run Models

#### 1. Baseline Analysis (Pre-Analysis Tool)
```bash
python baseline_analysis.py
```
**Outputs:** `baseline_analysis/`
- Baseline emissions by source and band
- Marginal abatement costs for all technologies  
- MACC curves for 2030, 2040, 2050
- Production shares and emission intensity analysis

#### 2. Fixed Band MACC Model (Main Model)
```bash
python corrected_band_model.py
```
**Outputs:** `outputs_fixed_bands/`
- Band-level deployment summary
- Emission pathways by source over time
- Technological change timeline with adoption patterns
- Investment phase analysis and visualizations

### Output Files Generated

#### 📊 **Core Results**
- `fixed_band_baseline.csv` - Fixed baseline structure (9 bands)
- `band_level_summary.csv` - Alternative technology penetration by band
- `emission_pathways_by_source.csv` - **NEW: Emission pathways by each band and technology**
- `technological_changes_timeline.csv` - **NEW: Technology adoption patterns and maturity**

#### 📈 **Visualizations**  
- `fixed_band_analysis.png` - Band deployment and emission reductions
- `technology_adoption_analysis.png` - **NEW: Technology market penetration curves**
- `macc_curve_*.png` - Marginal abatement cost curves by year

---

## 📋 Data Structure (Excel Input)

**File:** `data/Korea_Petrochemical_MACC_Database.xlsx`

### Core Sheets
- **`TechBands_2023`** - Fixed baseline band structure (HT/MT/LT)
- **`AlternativeTechnologies`** - Band-specific alternative technologies (NO CCUS)
- **`AlternativeCosts`** - Technology CAPEX/OPEX with proper scale units
- **`RegionalConstraints`** - Korea-specific energy prices and policies
- **`EmissionsTargets`** - National emissions reduction targets

### Technology Categories
- **E-cracker / H2-furnace** (HT): High-temperature process alternatives
- **Heat pump / Electric heater** (MT): Medium-temperature alternatives  
- **Heat pump / Electric motor** (LT): Low-temperature, electrification-focused

**Commercial Years:** 2023-2035 (realistic deployment timeline)

---

## 🎯 Model Results Overview

### Target Achievement
- **2030:** 100.0% target achieved (early deployment of mature technologies)
- **2040:** 72.9% target achieved (scaling phase challenges)  
- **2050:** 49.9% target achieved (deep decarbonization gap)

### Technology Deployment Pattern
- **LT Technologies:** Full penetration by 2030 (heat pumps, electric motors)
- **MT Technologies:** High penetration (60-90% emission reduction)
- **HT Technologies:** Moderate penetration (constrained by high costs and low TRL)

### Key Insights
1. **Mature low-temperature alternatives** drive early emission reductions
2. **High-temperature breakthrough technologies** are essential but face deployment barriers
3. **Fixed band structure** provides realistic industrial constraints
4. **Within-band substitution** represents achievable retrofit strategies

---

## 🔧 Technical Features

### Model Corrections Implemented
✅ **Fixed Band Structure** - No unrealistic HT↔MT↔LT transitions  
✅ **Corrected Scale Units** - Proper capacity vs production separation  
✅ **Band-Specific Constraints** - Each band maintains fixed baseline capacity  
✅ **Realistic Technology Targeting** - Alternatives target specific baseline bands  
✅ **Comprehensive Output Tracking** - Emission pathways and technology adoption

### Analysis Tools
- **Pre-analysis baseline assessment** with MACC curve projection
- **Technology adoption timeline** with market penetration tracking  
- **Investment phase analysis** (demonstration → scaling → saturation)
- **Emission source tracking** by band and technology over time

---

## 📁 Project Structure

```
petrochemical_macc_2025/
├── data/
│   └── Korea_Petrochemical_MACC_Database.xlsx    # Input data
├── baseline_analysis.py                          # Pre-analysis tool  
├── corrected_band_model.py                       # Main MACC model
├── petrochem/lib/                                # Core model library
├── outputs_fixed_bands/                          # Model results
├── baseline_analysis/                            # Baseline analysis results
└── README.md                                     # This file
```

## 📖 References

- **Model Philosophy:** Band-based industrial process modeling
- **Technology Classification:** Temperature-based process categorization  
- **Scale Units:** Industrial capacity planning with proper unit consistency
- **Alternative Technologies:** Within-band substitution reflecting retrofit reality
