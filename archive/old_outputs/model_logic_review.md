# MACC Model Logic Review and Corrections

## Current Issues Identified

### 1. Unit Inconsistencies
- **Problem**: Mixed capacity vs throughput units
- **Impact**: Incorrect cost calculations and constraint formulations

### 2. Technology Implementation Logic
- **Problem**: No clear distinction between capacity deployment and production throughput
- **Impact**: Abatement calculations don't reflect actual technology implementation

### 3. Scale Unit Confusion
- **Problem**: CAPEX costs not properly scaled to deployment decisions
- **Impact**: Unrealistic cost estimates

## Corrected Model Structure (Alternative Technologies Only)

### Core Principle: Separate Capacity and Production

**Key Variables:**
1. `capacity_installed[tech, year]` - New capacity installed (kt/year processing capacity)
2. `capacity_total[tech, year]` - Total available capacity (kt/year) 
3. `production[tech, year]` - Actual production using this technology (kt/year)

### Technology Types and Units

#### Alternative Technologies (New Processes Only)
```  
CAPEX: Million USD per kt/year of new capacity built
OPEX: USD per tonne of production using new technology
Abatement: tCO2 per tonne of production (compared to baseline process)
Deployment Unit: kt/year new capacity built
```

### Corrected Mathematical Formulation

#### Decision Variables
- `install[tech, year]` ∈ [0, +∞) - New capacity installed (kt/year)
- `capacity[tech, year]` ∈ [0, +∞) - Total capacity available (kt/year)
- `production[tech, year]` ∈ [0, +∞) - Production using this technology (kt/year)

#### Key Constraints
1. **Capacity Evolution**: 
   ```
   capacity[tech, year] = sum(install[tech, tau] for tau in active_years[tech, year])
   ```
   where active_years considers technology lifetime

2. **Production Limits**:
   ```
   production[tech, year] <= capacity[tech, year]
   ```

3. **Process Mass Balance**:
   ```
   sum(production[tech, year] for tech in alternative_techs) + baseline_production[process] <= total_demand[process]
   ```

4. **Abatement Calculation**:
   ```
   abatement[tech, year] = production[tech, year] * abatement_factor[tech] * 1000
   ```

5. **Cost Calculation**:
   ```
   annual_capex[tech, year] = install[tech, year] * capex_per_kt[tech] * CRF[tech]
   annual_opex[tech, year] = production[tech, year] * opex_per_t[tech] * 1000
   ```

### Implementation Scale Units

#### For Alternative Technologies:  
- **Scale**: New capacity construction that displaces baseline production
- **Base**: Market penetration limits vs total process production
- **Constraint**: Cannot build more than market allows or baseline production capacity
- **Cost**: Applied to new capacity built (install variable)
- **Abatement**: Applied to production through new capacity vs displaced baseline

## Benefits of Simplified Alternative-Only Approach

1. **Clear Unit Consistency**: All costs, capacities, and production in consistent units
2. **Realistic Technology Implementation**: Separates investment decisions from operational decisions  
3. **Proper Scale Representation**: Technology deployment reflects actual industrial implementation
4. **Accurate Costing**: CAPEX applied to capacity decisions, OPEX to production decisions
5. **Better Constraints**: Mass balance and capacity limits properly enforced
6. **Simplified Logic**: No complex band transition logic, only alternative technology adoption

## Next Steps

1. Implement corrected model formulation
2. Update data structure to support proper units
3. Validate with simplified test case
4. Verify unit consistency throughout model chain