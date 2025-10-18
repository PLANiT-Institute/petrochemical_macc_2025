# Petrochemical MACC Model - Data-Driven Version

## 🎯 Overview

This is a **fully data-driven** Marginal Abatement Cost Curve (MACC) model for the Korean petrochemical industry.

**Key Principle**: All assumptions live in CSV/Excel files. Code is a pure data processor with **NO HARDCODED VALUES**.

---

## 📁 Data Structure

### Master Assumptions File
**`data/MACC_Model_Assumptions.xlsx`** contains all model assumptions in 13 sheets:

| Sheet | Content | Use Case |
|-------|---------|----------|
| **README** | User guide | How to update assumptions |
| **Model_Parameters** | Global settings | Discount rate, emission factors, energy specs |
| **Baseline_Emissions** | Process emissions | Product-specific baseline CO2 |
| **Technology_Energy** | Energy requirements | H2/electricity consumption by technology |
| **Technology_Costs** | CAPEX/OPEX | Technology cost trajectories |
| **H2_Prices** | Hydrogen prices | $/kg trajectory (2025-2050) |
| **RE_Prices** | Renewable energy prices | $/MWh trajectory |
| **Fuel_Prices** | Fossil fuel prices | Naphtha, LNG, electricity, etc. |
| **Grid_Emissions** | Grid emission factors | tCO2/MWh decarbonization pathway |
| **Facility_Applicability** | Technology mapping | Which tech applies to which product |
| **Heat_Pump_Detail** | Heat pump specs | COP, temperature ranges |
| **Demand_Growth** | Capacity growth | Production capacity multipliers |
| **Emission_Factors** | Emission factors | tCO2/GJ, tCO2/kWh by fuel type |

### Individual Data Files (CSV)
All data also available as individual CSV files in `data/` for programmatic access.

---

## 🔧 How to Use

### 1. Update Assumptions (User Workflow)

```bash
# Step 1: Open Excel file
open data/MACC_Model_Assumptions.xlsx

# Step 2: Update values in relevant sheets
# Example: Change H2 price in 2030
#   Go to "H2_Prices" sheet → Find year 2030 → Update value

# Step 3: Save Excel file

# Step 4: Run model
python run_all.py
```

**That's it!** No code changes needed.

### 2. Run Individual Modules

```python
# Module 1: Baseline Emissions
python run_module_01.py

# Module 2: MACC Analysis (Data-Driven)
python run_module_02.py

# Module 3: Optimization
python run_module_03.py

# Module 4: Financial Analysis
python run_module_04.py
```

### 3. Programmatic Data Access

```python
from modules.data_manager import DataManager

# Load all data
dm = DataManager('data')

# Get parameters
discount_rate = dm.get_parameter('discount_rate')
h2_consumption = dm.get_parameter('ncc_h2_consumption')

# Get prices
h2_price_2030 = dm.get_price(2030, 'h2')
re_price_2030 = dm.get_price(2030, 're')

# Get baseline emissions
ethylene_baseline = dm.get_baseline_emissions('Ethylene')
print(ethylene_baseline['total_emissions_tco2_per_ton'])

# Get applicable technologies
techs = dm.get_applicable_technologies('Ethylene')
print(techs)  # ['NCC-H2', 'NCC-Electricity', 'RE_PPA']
```

---

## 📊 Model Architecture

### Data Flow

```
┌─────────────────────────────────────────┐
│  MACC_Model_Assumptions.xlsx            │
│  (Master assumptions file)              │
│  - All parameters                       │
│  - All prices                           │
│  - All technology specs                 │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│  DataManager                            │
│  (modules/data_manager.py)              │
│  - Load & validate all data             │
│  - Provide convenient access methods    │
│  - No business logic                    │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│  MACCAnalyzer                           │
│  (modules/macc.py)                      │
│  - Calculate MACC                       │
│  - Uses DataManager for all values      │
│  - NO HARDCODED VALUES                  │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│  Results                                │
│  outputs/module_02/                     │
│  - MACC curves (CSV, PNG)               │
│  - Abatement potentials                 │
│  - Cost breakdowns                      │
└─────────────────────────────────────────┘
```

### Key Components

#### 1. DataManager (`modules/data_manager.py`)
- **Purpose**: Centralized data loading and validation
- **Features**:
  - Load all CSV/Excel files
  - Validate data consistency
  - Provide convenient access methods
  - NO business logic

#### 2. MACCAnalyzer (`modules/macc.py`)
- **Purpose**: Calculate MACC curves
- **Data Source**: 100% from DataManager
- **Key Calculations**:
  - Baseline emissions (from data)
  - Technology costs (from data)
  - Energy requirements (from data)
  - Abatement potential

#### 3. Data Files
- **Location**: `data/` directory
- **Format**: CSV and Excel
- **Validation**: Automatic consistency checks

---

## 🔑 Key Assumptions (All Configurable)

### Energy Parameters
| Parameter | Value | Unit | Source File |
|-----------|-------|------|-------------|
| H2 LHV | 120 | MJ/kg | model_parameters.csv |
| NCC-H2 consumption | 0.20 | ton H2/ton C2H4 | model_parameters.csv |
| NCC-Electricity consumption | 3.0 | MWh/ton C2H4 | model_parameters.csv |
| Heat Pump COP | 4.0 | - | model_parameters.csv |

### Emission Factors
| Fuel | Value | Unit | Source File |
|------|-------|------|-------------|
| Fossil fuels | 0.0149 | tCO2/GJ | model_parameters.csv |
| Green H2 | 0.0 | tCO2/kg | model_parameters.csv |
| Grid (2025) | 0.45 | tCO2/MWh | grid_emission_trajectory.csv |
| Grid (2050) | 0.25 | tCO2/MWh | grid_emission_trajectory.csv |

### Prices (2025)
| Energy Source | Value | Unit | Source File |
|---------------|-------|------|-------------|
| H2 | $12.00 | /kg | h2_price_trajectory.csv |
| RE | $58.00 | /MWh | re_price_trajectory.csv |
| Naphtha | $15.00 | /GJ | fuel_price_trajectory.csv |
| LNG | $12.00 | /GJ | fuel_price_trajectory.csv |
| Electricity | $0.10 | /kWh | fuel_price_trajectory.csv |

### Baseline Emissions
| Product | Naphtha Fuel | Total Fuel | Emissions | Source File |
|---------|--------------|------------|-----------|-------------|
| Ethylene | 105.47 GJ/t | 116.70 GJ/t | 1.739 tCO2/t | baseline_process_emissions.csv |
| Propylene | 92.35 GJ/t | 102.67 GJ/t | 1.530 tCO2/t | baseline_process_emissions.csv |

---

## 📈 Results Summary (2025 vs 2050)

### 2025 MACC Results
| Technology | Cost ($/tCO2) | Abatement (MtCO2) | Key Driver |
|------------|---------------|-------------------|------------|
| RE_PPA | -$105 | 7.21 | Cheaper RE vs grid |
| NCC-Electricity | $805 | 4.65 | Grid EF still high |
| NCC-H2 | $1,450 | 20.20 | Expensive H2 |

### 2050 MACC Results
| Technology | Cost ($/tCO2) | Abatement (MtCO2) | Key Driver |
|------------|---------------|-------------------|------------|
| RE_PPA | -$340 | 8.36 | Much cheaper RE |
| NCC-H2 | $299 | 26.02 | H2 price drops 80% |
| NCC-Electricity | $321 | 15.23 | Cleaner grid |

**Key Insight**: H2 becomes cost-competitive by 2050 due to price reduction from $12/kg → $2.4/kg

---

## 🏭 Facility Integration (248 Facilities)

### Facility-Technology Mapping

The model automatically determines applicable technologies for each of 248 facilities:

```python
from modules.data_manager import DataManager

dm = DataManager('data')

# Example: What technologies apply to each product?
for product in ['Ethylene', 'Propylene', 'Benzene', 'LDPE']:
    techs = dm.get_applicable_technologies(product)
    print(f"{product}: {techs}")

# Output:
# Ethylene: ['NCC-H2', 'NCC-Electricity', 'RE_PPA']
# Propylene: ['NCC-H2', 'NCC-Electricity', 'RE_PPA']
# Benzene: ['Heat_Pump', 'RE_PPA']
# LDPE: ['Heat_Pump', 'RE_PPA']
```

### Technology Applicability Rules
Defined in: `data/facility_technology_applicability.csv`

| Product Group | NCC-H2 | NCC-Elec | Heat Pump | RE PPA |
|---------------|--------|----------|-----------|--------|
| Olefins (Ethylene, Propylene) | ✓ | ✓ | ✗ | ✓ |
| Aromatics (Benzene, Toluene) | ✗ | ✗ | ✓ | ✓ |
| Polymers (LDPE, HDPE, PP) | ✗ | ✗ | ✓ | ✓ |
| All others | ✗ | ✗ | ✓ | ✓ |

---

## ✅ Data Validation

The DataManager automatically validates:

1. **Completeness**
   - All required parameters present
   - No missing critical values
   - All years covered in trajectories

2. **Consistency**
   - Year ranges match across files
   - Products exist in all relevant files
   - Units are consistent

3. **Reasonableness** (warnings only)
   - Prices within expected ranges
   - Emission factors positive
   - Energy consumption values realistic

### Run Validation

```python
from modules.data_manager import DataManager

dm = DataManager('data')
# Validation runs automatically on init
# Errors raised if critical issues found
# Warnings printed for suspicious values
```

---

## 🚀 Quick Start Examples

### Example 1: Change H2 Price Scenario

```excel
# In MACC_Model_Assumptions.xlsx, H2_Prices sheet:
# Change 2050 H2 price from $2.40/kg to $5.00/kg

# Save and run:
python run_module_02.py

# Result: NCC-H2 MACC increases accordingly
```

### Example 2: Update Emission Factors

```excel
# In MACC_Model_Assumptions.xlsx, Model_Parameters sheet:
# Change green_h2_emission_factor from 0.0 to 0.5 tCO2/kg

# Save and run:
python run_module_02.py

# Result: H2 abatement potential decreases
```

### Example 3: Add New Technology

```excel
# In MACC_Model_Assumptions.xlsx:
# 1. Add row to Technology_Energy sheet
# 2. Add row to Technology_Costs sheet
# 3. Update Facility_Applicability

# No code changes needed!
```

---

## 📖 Documentation Files

- **`README_DATA_DRIVEN.md`** (this file) - User guide
- **`docs/DATA_DRIVEN_REFACTORING_PLAN.md`** - Technical implementation plan
- **`data/MACC_Model_Assumptions.xlsx`** - README sheet with instructions

---

## 🛠️ For Developers

### Adding New Data Files

1. Create CSV file in `data/`
2. Add loading logic to `DataManager._load_all_data()`
3. Add validation to `DataManager._validate_data()`
4. Add getter method for convenient access
5. Update Excel file with new sheet

### Code Principles

1. **NO HARDCODED VALUES** - Everything from data files
2. **Use DataManager** - Don't load CSV directly in business logic
3. **Validate Early** - Check data on load, not during calculation
4. **Document Sources** - Add literature references in data files

---

## 📊 File Summary

### Data Files (All in `data/`)
- ✓ `MACC_Model_Assumptions.xlsx` - Master assumptions (13 sheets)
- ✓ `model_parameters.csv` - Global parameters
- ✓ `baseline_process_emissions.csv` - Process baseline emissions
- ✓ `technology_energy_requirements.csv` - Tech energy specs
- ✓ `facility_technology_applicability.csv` - Tech-product mapping
- ✓ `facility_database.csv` - 248 facilities
- ✓ `energy_intensities.csv` - Energy use by facility
- ✓ All existing price/emission trajectory files

### Code Files
- ✓ `modules/data_manager.py` - Centralized data management
- ✓ `modules/macc.py` - MACC calculation (data-driven)
- ✓ `modules/utils.py` - Utility functions
- ✓ `run_module_02.py` - Run MACC analysis

---

## 🎓 Best Practices

### For Users (Non-Programmers)

1. **Always update Excel file** - Don't edit CSV directly
2. **Document your changes** - Add notes in Excel cells
3. **Keep backups** - Save dated versions of assumptions file
4. **Validate results** - Check if outputs make sense

### For Developers

1. **Never hardcode** - If you find yourself typing a number, put it in data
2. **Use DataManager** - Don't bypass centralized data loading
3. **Add validation** - Check new data for consistency
4. **Update docs** - Keep README and Excel comments current

---

## 🤝 Support

For questions or issues:
1. Check Excel file README sheet
2. Review `docs/DATA_DRIVEN_REFACTORING_PLAN.md`
3. Contact model maintainers

---

**Version**: 2.0 (Data-Driven)
**Last Updated**: 2025-10-17
**Maintained by**: [Your Team]
