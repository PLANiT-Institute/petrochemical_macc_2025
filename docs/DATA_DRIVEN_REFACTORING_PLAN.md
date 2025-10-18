# Data-Driven Model Refactoring Plan

## Objective
Transform the MACC model from hardcoded values to a fully data-driven approach where:
1. **All assumptions live in CSV/Excel files**
2. **Code is a pure data processor** (no business logic hardcoded)
3. **248 facilities naturally flow through the model**
4. **Users can update assumptions without touching code**

---

## Current State (Hardcoded Values)

### In `macc.py`:
```python
# Line 74-75
self.ef_naphtha = 0.0149  # tCO2/GJ
self.ef_h2_green = 0.05   # tCO2/ton H2

# Line 244-248
naphtha_fuel_gj = 105.47
lng_gj = 4.49
fuel_gas_gj = 5.62
byproduct_gj = 1.12
```

### Problems:
- Changing assumptions requires code edits
- No traceability of assumption sources
- Risk of inconsistency across modules
- Difficult for non-programmers to update

---

## Target State (Data-Driven)

### New Data Structure:

```
data/
├── MACC_Model_Assumptions.xlsx          # Master assumptions file
│   ├── README                           # How to use
│   ├── Model_Parameters                 # Discount rate, base year, etc.
│   ├── Baseline_Emissions               # Product-specific baseline emissions
│   ├── Technology_Energy                # H2/elec consumption by technology
│   ├── Technology_Costs                 # CAPEX/OPEX trajectories
│   ├── H2_Prices                        # H2 price trajectory
│   ├── RE_Prices                        # RE price trajectory
│   ├── Fuel_Prices                      # Fossil fuel price trajectories
│   ├── Grid_Emissions                   # Grid decarbonization pathway
│   ├── Facility_Applicability           # Which tech applies to which product
│   ├── Heat_Pump_Detail                 # Heat pump specs by process temp
│   ├── Demand_Growth                    # Capacity growth trajectory
│   └── Emission_Factors                 # Emission factors by fuel type
│
├── facility_database.csv                # 248 facilities with baseline data
├── energy_intensities.csv               # Energy use by product/process
└── [all other existing CSV files]       # Preserved
```

---

## Refactoring Steps

### Step 1: Create Data Files ✓
- [x] `model_parameters.csv` - Global model parameters
- [x] `baseline_process_emissions.csv` - Process-specific baseline emissions
- [x] `technology_energy_requirements.csv` - Energy requirements by technology
- [x] `facility_technology_applicability.csv` - Technology-product mapping
- [x] `MACC_Model_Assumptions.xlsx` - Master Excel file

### Step 2: Refactor `modules/macc.py`
Replace hardcoded values with data loading:

```python
# OLD (hardcoded):
self.ef_naphtha = 0.0149
naphtha_fuel_gj = 105.47

# NEW (data-driven):
params = pd.read_csv('data/model_parameters.csv').set_index('parameter')
self.ef_naphtha = params.loc['fossil_fuel_emission_factor', 'value']

baseline_emissions = pd.read_csv('data/baseline_process_emissions.csv')
process_data = baseline_emissions[baseline_emissions['product'] == 'Ethylene'].iloc[0]
naphtha_fuel_gj = process_data['naphtha_fuel_gj_per_ton']
```

### Step 3: Create `DataManager` Class
Centralized data loading and validation:

```python
class DataManager:
    """Load and validate all model data"""

    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.load_all_data()

    def load_all_data(self):
        """Load all data files into DataFrames"""
        self.model_params = self._load_model_parameters()
        self.baseline_emissions = pd.read_csv(self.data_dir / 'baseline_process_emissions.csv')
        self.tech_energy = pd.read_csv(self.data_dir / 'technology_energy_requirements.csv')
        self.facility_applicability = pd.read_csv(self.data_dir / 'facility_technology_applicability.csv')
        # ... load all other files

    def get_baseline_emissions(self, product):
        """Get baseline emissions for a specific product"""
        return self.baseline_emissions[self.baseline_emissions['product'] == product].iloc[0]

    def get_tech_energy_requirement(self, technology, product):
        """Get energy requirements for technology-product combination"""
        mask = (self.tech_energy['technology'] == technology) & \
               (self.tech_energy['applies_to_product'] == product)
        return self.tech_energy[mask].iloc[0]
```

### Step 4: Facility-Technology Integration
Link 248 facilities to applicable technologies:

```python
def get_applicable_technologies(facility_row):
    """Return list of technologies applicable to this facility"""
    product = facility_row['product']
    product_group = identify_product_group(product)

    applicability = facility_applicability[
        (facility_applicability['product'] == product) |
        (facility_applicability['product_group'] == product_group)
    ]

    technologies = []
    if applicability['heat_pump_applicable'].iloc[0]:
        technologies.append('Heat_Pump')
    if applicability['ncc_h2_applicable'].iloc[0]:
        technologies.append('NCC-H2')
    # ... etc

    return technologies
```

### Step 5: Update All Modules
- `modules/baseline.py` - Use facility database directly
- `modules/macc.py` - Load from baseline_emissions.csv
- `modules/optimization.py` - Use facility-technology mapping
- `modules/financial.py` - Read cost assumptions from Excel

### Step 6: Create Validation Layer
```python
def validate_data_consistency():
    """Validate all data files for consistency"""
    # Check products in facility_database match baseline_emissions
    # Check technologies in tech_params match tech_energy
    # Validate year ranges are consistent
    # Check for missing values
    # Validate calculation formulas
```

---

## Benefits

1. **Transparency**: All assumptions visible in Excel
2. **Flexibility**: Update assumptions without code changes
3. **Traceability**: Source/literature reference in each sheet
4. **Collaboration**: Non-programmers can update assumptions
5. **Validation**: Centralized data validation
6. **Documentation**: Self-documenting through Excel structure
7. **Version Control**: Track assumption changes via Git

---

## Implementation Priority

1. ✓ Create all data files
2. ✓ Create master Excel file
3. → Refactor macc.py (in progress)
4. → Create DataManager class
5. → Update facility-technology integration
6. → Add validation layer
7. → Update documentation
8. → Test end-to-end workflow

---

## Testing Strategy

1. **Data Validation Tests**
   - All required columns present
   - No missing critical values
   - Year ranges consistent
   - Products match across files

2. **Calculation Tests**
   - Results match previous hardcoded version
   - Edge cases handled correctly
   - 248 facilities all processed

3. **User Workflow Test**
   - Update Excel → Run model → Verify outputs
   - Document typical update scenarios

---

## Timeline

- **Phase 1** (Current): Data structure design ✓
- **Phase 2** (Next 2 hours): Core refactoring
- **Phase 3** (Following day): Testing & validation
- **Phase 4** (Final): Documentation & examples

---

## Notes for Future Maintainers

- **Never hardcode values in Python code**
- **All assumptions must be in CSV/Excel**
- **Add validation for any new data files**
- **Document assumption sources in Excel comments**
- **Keep this refactoring plan updated**

