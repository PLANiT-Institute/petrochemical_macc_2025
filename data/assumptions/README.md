# Assumption Data Documentation

This directory contains all external parameters and assumptions used in the Petrochemical Net Zero Simulation. These values are distinct from the "Asset Database" (which represents physical reality) and "Scenarios" (which represent policy/demand choices).

## Directory Structure
*   `emission_factors.csv`: Carbon intensity of fuels (tCO2/GJ). Source: IPCC 2019.
*   `technology_parameters.csv`: CAPEX, OPEX, Efficiency, and Availability of decarbonization technologies (e.g., NCC-H2, Heat Pumps).
*   `asset_valuation_params.csv`: Parameters for calculating book value and stranded assets (Useful life, Overnight CAPEX).
*   `carbon_budget_scenarios.csv`: Annual emission limits for the sector under 1.5C and 2.0C pathways.

### prices/
Contains price trajectories for key commodities (2025-2050):
*   `fuel_price_trajectory.csv`: Fossil fuels (Naphtha, LNG, Fuel Gas).
*   `h2_price_trajectory.csv`: Clean Hydrogen (Blue/Green mix).
*   `re_price_trajectory.csv`: Renewable Energy (PPA).
*   `grid_price_trajectory.csv`: Industrial grid electricity tariffs.
*   `grid_emission_trajectory.csv`: Grid carbon intensity (tCO2/MWh).

---

## Key Assumptions Summary

### Technology
*   **Heat Pumps**: COP 4.0, Available 2025. Assumed applicable to process heat <165°C.
*   **NCC Electrification**: 5.0 MWh/ton-Ethylene. Available 2030.
*   **Hydrogen Furnaces**: 0.2 ton-H2/ton-Ethylene. Available 2030.

### Economics
*   **Discount Rate**: Standard social discount rate or WACC (check `utils.py` for default, usually not applied to raw prices but to NPV if calculated).
*   **Fuel Savings**: Calculated as the full displaced cost of Naphtha/Gas/Oil at annual prices.
