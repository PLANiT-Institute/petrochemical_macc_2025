"""
CAPEX Calculator Module
=======================
Calculates technology CAPEX using capacity-based approach ($/t-product/yr).
MAC is calculated as a result, not an input.

Key principle: CAPEX is based on facility capacity, not on abatement.
MAC = (Annualized CAPEX + OPEX + Energy Cost - Fuel Savings) / Abatement
"""

import pandas as pd
import numpy as np
import warnings


class CapexCalculator:
    """
    Calculate technology CAPEX and costs using capacity-based approach.

    CAPEX units: $/t-product/yr (from technology_capex.csv)
    This replaces the old $/tCO2 approach which pre-baked MAC assumptions.
    """

    def __init__(self, capex_df, tech_params_df, model_config):
        """
        Args:
            capex_df: DataFrame from technology_capex.csv
            tech_params_df: DataFrame from technology_parameters.csv
            model_config: Dict from model_config.csv
        """
        self.capex_df = capex_df.set_index('technology')
        self.tech_params = tech_params_df.set_index('technology')
        self.config = model_config

        # Physical constant from config - must be present
        if 'gj_to_mwh' not in model_config:
            raise ValueError("model_config missing required 'gj_to_mwh' parameter")
        self.gj_to_mwh = model_config['gj_to_mwh']

    def get_technology_capex_rate(self, technology, year):
        """
        Get interpolated CAPEX rate for a technology in a given year.

        Returns:
            float: CAPEX in $/t-product/yr
        """
        if technology not in self.capex_df.index:
            raise ValueError(f"Technology '{technology}' not found in technology_capex.csv")

        row = self.capex_df.loc[technology]

        # Interpolate between years
        years = [2025, 2030, 2040, 2050]
        capex_values = [
            row['capex_2025'],
            row['capex_2030'],
            row['capex_2040'],
            row['capex_2050']
        ]

        return np.interp(year, years, capex_values)

    def get_technology_params(self, technology):
        """
        Get technology parameters (efficiency, COP, etc.) with validation.
        Raises error if required parameter is missing - NO FALLBACKS.
        """
        if technology not in self.tech_params.index:
            raise ValueError(f"Technology '{technology}' not found in technology_parameters.csv")

        row = self.tech_params.loc[technology]

        params = {
            'applies_to': row.get('applies_to', ''),
            'available_year': row.get('available_year', 2025),
            'trl': row.get('trl', None),
        }

        # Technology-specific parameters - NO FALLBACKS
        if technology == 'Heat_Pump':
            if pd.isna(row.get('cop')):
                raise ValueError("Heat_Pump COP is missing in technology_parameters.csv")
            params['cop'] = row['cop']

        elif technology == 'RDH':
            if pd.isna(row.get('energy_conversion_efficiency')):
                raise ValueError("RDH energy_conversion_efficiency is missing in technology_parameters.csv")
            params['energy_conversion_efficiency'] = row['energy_conversion_efficiency']

        elif technology == 'NCC-H2':
            if pd.isna(row.get('h2_ton_per_ton_ethylene')):
                raise ValueError("NCC-H2 h2_ton_per_ton_ethylene is missing in technology_parameters.csv")
            params['h2_ton_per_ton_ethylene'] = row['h2_ton_per_ton_ethylene']
            if not pd.isna(row.get('energy_conversion_efficiency')):
                params['energy_conversion_efficiency'] = row['energy_conversion_efficiency']

        elif technology == 'NCC-Electricity':
            if pd.isna(row.get('elec_mwh_per_ton_ethylene')):
                raise ValueError("NCC-Electricity elec_mwh_per_ton_ethylene is missing in technology_parameters.csv")
            params['elec_mwh_per_ton_ethylene'] = row['elec_mwh_per_ton_ethylene']
            if not pd.isna(row.get('energy_conversion_efficiency')):
                params['energy_conversion_efficiency'] = row['energy_conversion_efficiency']

        return params

    def get_capex_info(self, technology):
        """Get CAPEX metadata (OPEX%, lifetime, etc.)

        Note: opex_pct_capex and lifetime_years should be in technology_capex.csv.
        Fallback values (3.0% and 25 years) are only used for backwards compatibility.
        """
        if technology not in self.capex_df.index:
            raise ValueError(f"Technology '{technology}' not found in technology_capex.csv")

        row = self.capex_df.loc[technology]

        # Get OPEX percentage - warn if using fallback
        if 'opex_pct_capex' in row.index and pd.notna(row['opex_pct_capex']):
            opex = row['opex_pct_capex']
        else:
            opex = 3.0
            warnings.warn(
                f"opex_pct_capex not found for {technology} in technology_capex.csv, "
                f"using fallback value of {opex}%",
                UserWarning
            )

        # Get lifetime - warn if using fallback
        if 'lifetime_years' in row.index and pd.notna(row['lifetime_years']):
            lifetime = row['lifetime_years']
        else:
            lifetime = 25
            warnings.warn(
                f"lifetime_years not found for {technology} in technology_capex.csv, "
                f"using fallback value of {lifetime} years",
                UserWarning
            )

        # Get CAPEX unit - warn if using fallback
        if 'capex_unit' in row.index and pd.notna(row['capex_unit']):
            capex_unit = row['capex_unit']
        else:
            capex_unit = 'usd_per_t_product_yr'
            warnings.warn(
                f"capex_unit not found for {technology} in technology_capex.csv, "
                f"using fallback value of {capex_unit}",
                UserWarning
            )

        return {
            'opex_pct_capex': float(opex) if hasattr(opex, 'item') else opex,
            'lifetime_years': int(lifetime) if hasattr(lifetime, 'item') else lifetime,
            'capex_unit': str(capex_unit) if hasattr(capex_unit, 'item') else capex_unit,
        }

    def is_technology_available(self, technology, year):
        """Check if technology is available in a given year"""
        params = self.get_technology_params(technology)
        return year >= params['available_year']

    def calculate_facility_capex(self, technology, capacity_t_yr, year):
        """
        Calculate total CAPEX for a facility using capacity-based approach.

        Args:
            technology: Technology name (e.g., 'NCC-Electricity', 'Heat_Pump')
            capacity_t_yr: Annual production capacity in tonnes/year
            year: Deployment year (for CAPEX interpolation)

        Returns:
            dict with capex_total, capex_rate, capacity
        """
        capex_rate = self.get_technology_capex_rate(technology, year)
        capex_total = capacity_t_yr * capex_rate

        return {
            'capex_total_usd': capex_total,
            'capex_rate_usd_per_t': capex_rate,
            'capacity_t_yr': capacity_t_yr,
            'year': year
        }

    def calculate_annualized_capex(self, capex_total, lifetime_years):
        """
        Calculate annualized CAPEX using simple linear amortization.

        For more sophisticated analysis, could use CRF (Capital Recovery Factor):
        CRF = r * (1+r)^n / ((1+r)^n - 1)
        """
        return capex_total / lifetime_years

    def calculate_energy_requirements(self, technology, facility_baseline, process):
        """
        Calculate energy requirements (H2, electricity) for a technology.

        Args:
            technology: Technology name
            facility_baseline: Dict with baseline emissions and energy data
            process: Process type (e.g., 'Naphtha Cracker', 'BTX Plant')

        Returns:
            dict with h2_demand_t, added_elec_mwh
        """
        params = self.get_technology_params(technology)

        h2_demand_t = 0.0
        added_elec_mwh = 0.0

        production_t = facility_baseline.get('production_t', 0)
        heat_demand_gj = facility_baseline.get('heat_demand_gj', 0)

        if technology == 'NCC-H2':
            # H2 demand based on ethylene production
            h2_per_ethylene = params['h2_ton_per_ton_ethylene']
            h2_demand_t = production_t * h2_per_ethylene

        elif technology == 'NCC-Electricity':
            # Electricity demand based on ethylene production
            elec_per_ethylene = params['elec_mwh_per_ton_ethylene']
            added_elec_mwh = production_t * elec_per_ethylene

        elif technology == 'RDH':
            # RDH for BTX - electricity replaces heat
            efficiency = params['energy_conversion_efficiency']
            added_elec_mwh = heat_demand_gj / self.gj_to_mwh / efficiency

        elif technology == 'Heat_Pump':
            # Heat pump with COP
            cop = params['cop']
            added_elec_mwh = heat_demand_gj / self.gj_to_mwh / cop

        return {
            'h2_demand_t': h2_demand_t,
            'added_elec_mwh': added_elec_mwh
        }


class MACCalculator:
    """
    Calculate Marginal Abatement Cost (MAC) from components.
    MAC is the RESULT of the calculation, not an input.

    MAC = (Annualized CAPEX + OPEX + New Energy Cost - Fuel Savings) / Abatement
    """

    def __init__(self, capex_calculator, price_calculator, emission_calculator):
        """
        Args:
            capex_calculator: CapexCalculator instance
            price_calculator: PriceCalculator instance (from utils.py)
            emission_calculator: EmissionCalculator instance (from utils.py)
        """
        self.capex_calc = capex_calculator
        self.price_calc = price_calculator
        self.emission_calc = emission_calculator

    def calculate_mac(self, facility_baseline, technology, year, fuel_prices):
        """
        Calculate MAC for a facility-technology pair.

        Args:
            facility_baseline: Dict with baseline emissions, energy, production
            technology: Technology name
            year: Deployment year
            fuel_prices: Dict with fuel prices for the year

        Returns:
            dict with mac, cost breakdown, and all components
        """
        # 1. Get CAPEX
        production_t = facility_baseline.get('production_t', 0)
        capex_info = self.capex_calc.calculate_facility_capex(
            technology, production_t, year
        )
        capex_total = capex_info['capex_total_usd']

        # 2. Get OPEX and lifetime
        capex_meta = self.capex_calc.get_capex_info(technology)
        lifetime = capex_meta['lifetime_years']
        opex_pct = capex_meta['opex_pct_capex'] / 100

        capex_annual = self.capex_calc.calculate_annualized_capex(capex_total, lifetime)
        opex_annual = capex_total * opex_pct

        # 3. Get energy requirements
        process = facility_baseline.get('process', '')
        energy_reqs = self.capex_calc.calculate_energy_requirements(
            technology, facility_baseline, process
        )

        h2_demand_t = energy_reqs['h2_demand_t']
        added_elec_mwh = energy_reqs['added_elec_mwh']

        # 4. Calculate new energy costs
        h2_price = self.price_calc.get_h2_price(year)  # $/kg
        re_price = self.price_calc.get_re_price(year)  # $/MWh

        h2_cost = h2_demand_t * h2_price * 1000  # Convert t to kg
        elec_cost = added_elec_mwh * re_price
        new_energy_cost = h2_cost + elec_cost

        # 5. Calculate fuel savings
        fuel_savings = self._calculate_fuel_savings(facility_baseline, fuel_prices)

        # 6. Get abatement potential
        abatement_tco2 = facility_baseline.get('combustion_emissions', 0)

        # 7. Calculate MAC
        total_annual_cost = capex_annual + opex_annual + new_energy_cost - fuel_savings

        if abatement_tco2 > 0:
            mac = total_annual_cost / abatement_tco2
        else:
            # Use large but finite value instead of inf to prevent aggregation issues
            # 1e9 (billion $/tCO2) is effectively infinity for practical purposes
            mac = 1e9

        return {
            'mac_usd_per_tco2': mac,
            'technology': technology,
            'abatement_tco2': abatement_tco2,
            'capex_total_usd': capex_total,
            'capex_annual_usd': capex_annual,
            'opex_annual_usd': opex_annual,
            'new_energy_cost_usd': new_energy_cost,
            'fuel_savings_usd': fuel_savings,
            'total_annual_cost_usd': total_annual_cost,
            'h2_demand_t': h2_demand_t,
            'added_elec_mwh': added_elec_mwh,
            'lifetime_years': lifetime,
            'production_t': production_t
        }

    def _calculate_fuel_savings(self, facility_baseline, fuel_prices):
        """
        Calculate avoided fuel costs from switching technology.

        IMPORTANT: For NCC (Naphtha Cracker) facilities, naphtha is FEEDSTOCK that is
        cracked into products, NOT combustion fuel. Therefore, there are NO fuel savings
        from naphtha - it's still used as feedstock even with e-cracker or H2 cracker.
        Only LNG, LPG, and byproduct gas are actual heating fuels that can be saved.
        """
        energy_by_source = facility_baseline.get('energy_by_source', {})
        is_ncc = facility_baseline.get('is_ncc', False)

        fuel_savings = 0.0

        # Map internal keys to price keys
        # Note: electricity is NOT included here because:
        # 1. We're calculating fuel SAVINGS from switching away from combustion
        # 2. Electricity cost is handled separately as new_energy_cost
        # 3. Baseline electricity cost is not "saved" when deploying new tech
        fuel_mapping = {
            'naphtha': 'naphtha_usd_per_gj',
            'lng': 'lng_usd_per_gj',
            'fuel_gas': 'fuel_gas_usd_per_gj',
            'byproduct_gas': 'fuel_gas_usd_per_gj',  # Price same as fuel gas
            'lpg': 'lpg_usd_per_gj',
            'fuel_oil': 'fuel_oil_usd_per_gj',
            'diesel': 'diesel_usd_per_gj',
            # Note: 'electricity' intentionally excluded - see comment above
        }

        for internal_key, price_key in fuel_mapping.items():
            # Skip naphtha for NCC - it's feedstock, not fuel
            if internal_key == 'naphtha' and is_ncc:
                continue

            energy_gj = energy_by_source.get(internal_key, 0)
            price = fuel_prices.get(price_key, 0)
            fuel_savings += energy_gj * price

        return fuel_savings


def select_technology_for_facility(process, ncc_tech_choice):
    """
    Determine which technology applies to a facility based on its process.

    Args:
        process: Process type (e.g., 'Naphtha Cracker', 'BTX Plant')
        ncc_tech_choice: Scenario's NCC technology choice ('NCC-H2' or 'NCC-Electricity')

    Returns:
        str: Technology name
    """
    if process == 'Naphtha Cracker':
        return ncc_tech_choice
    elif process == 'BTX Plant':
        return 'RDH'
    else:
        return 'Heat_Pump'
