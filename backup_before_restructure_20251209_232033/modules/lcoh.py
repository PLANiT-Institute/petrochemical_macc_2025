"""
LCOH Calculation Module
Calculates Levelized Cost of Hydrogen based on electricity price and electrolyzer parameters.

Source: PLANiT Institute (2025)
"""

import numpy as np

def calculate_crf(discount_rate, lifetime):
    """Calculate Capital Recovery Factor"""
    if discount_rate == 0:
        return 1 / lifetime
    return (discount_rate * (1 + discount_rate)**lifetime) / ((1 + discount_rate)**lifetime - 1)

def calculate_lcoh(elec_price, capex, efficiency=0.70, lifetime=20, capacity_factor=0.90,
                   opex_pct=0.02, discount_rate=0.08, stack_replacement_cost=0.15, stack_lifetime=10):
    """
    Calculate Levelized Cost of Hydrogen (LCOH) using precise formula

    LCOH = (CAPEX × CRF + Fixed_OPEX + Stack_Replacement) / Annual_H2_Production + Variable_Electricity_Cost

    Parameters:
    - elec_price: Electricity price ($/MWh)
    - capex: Electrolyzer CAPEX ($/kW)
    - efficiency: Electrolyzer efficiency (HHV basis, 0.70 = 70%)
    - lifetime: System lifetime (years)
    - capacity_factor: Annual capacity factor
    - opex_pct: Fixed OPEX as % of CAPEX per year
    - discount_rate: WACC/discount rate for CRF calculation
    - stack_replacement_cost: Stack replacement as % of CAPEX
    - stack_lifetime: Years between stack replacements

    Returns:
    - Dictionary with LCOH breakdown in $/kg H2
    """
    # Constants
    H2_HHV = 39.4  # kWh/kg (Higher Heating Value of H2)
    HOURS_PER_YEAR = 8760

    # Electricity consumption per kg H2
    elec_per_kg_kwh = H2_HHV / efficiency  # kWh/kg H2

    # Annual operating hours
    operating_hours = HOURS_PER_YEAR * capacity_factor

    # H2 production per kW of electrolyzer capacity
    # 1 kW electrolyzer * operating_hours / elec_per_kg = kg H2/year/kW
    h2_per_kw_year = operating_hours / elec_per_kg_kwh  # kg H2/year per kW capacity

    # Capital Recovery Factor
    crf = calculate_crf(discount_rate, lifetime)

    # CAPEX component ($/kg H2)
    # CAPEX ($/kW) × CRF / H2 production (kg/kW/year)
    capex_component = (capex * crf) / h2_per_kw_year

    # Fixed OPEX component ($/kg H2)
    # OPEX ($/kW/year) / H2 production (kg/kW/year)
    fixed_opex_component = (capex * opex_pct) / h2_per_kw_year

    # Stack replacement component ($/kg H2) - annualized
    # Number of replacements over lifetime
    num_replacements = max(0, (lifetime // stack_lifetime) - 1)
    if num_replacements > 0:
        # NPV of stack replacements
        stack_npv = sum([stack_replacement_cost * capex / ((1 + discount_rate)**(stack_lifetime * (i+1)))
                         for i in range(int(num_replacements))])
        stack_component = (stack_npv * crf) / h2_per_kw_year
    else:
        stack_component = 0

    # Electricity cost component ($/kg H2)
    # elec_price ($/MWh) × elec_per_kg (kWh) / 1000
    elec_component = elec_price * elec_per_kg_kwh / 1000

    # Total LCOH
    lcoh = capex_component + fixed_opex_component + stack_component + elec_component

    return {
        'lcoh': lcoh,
        'capex_component': capex_component,
        'opex_component': fixed_opex_component,
        'stack_component': stack_component,
        'elec_component': elec_component,
        'elec_per_kg': elec_per_kg_kwh,
        'h2_per_kw_year': h2_per_kw_year,
        'crf': crf
    }
