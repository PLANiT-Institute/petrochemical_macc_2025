"""
Unit tests for calculator modules.

Tests cover:
- EmissionCalculator: Emission calculations by fuel type
- CapexCalculator: CAPEX interpolation and facility cost calculations
- MACCalculator: Marginal Abatement Cost calculations
- PriceCalculator: Price trajectory interpolation
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.utils import EmissionCalculator, PriceCalculator, TechnologyCostCalculator
from modules.capex_calculator import CapexCalculator, MACCalculator


# ============================================================================
# FIXTURES - Test Data Setup
# ============================================================================

@pytest.fixture
def emission_factors_df():
    """Standard emission factors from IPCC/API"""
    return pd.DataFrame([
        {'fuel': 'Naphtha', 'tCO2_per_GJ': 0.0542, 'tCO2_per_kWh': None, 'tCO2_per_kg': None},
        {'fuel': 'Electricity', 'tCO2_per_GJ': None, 'tCO2_per_kWh': 0.000436, 'tCO2_per_kg': None},
        {'fuel': 'LNG', 'tCO2_per_GJ': 0.0561, 'tCO2_per_kWh': None, 'tCO2_per_kg': None},
        {'fuel': 'Fuel_Gas', 'tCO2_per_GJ': 0.050, 'tCO2_per_kWh': None, 'tCO2_per_kg': None},
        {'fuel': 'Byproduct_Gas', 'tCO2_per_GJ': 0.048, 'tCO2_per_kWh': None, 'tCO2_per_kg': None},
        {'fuel': 'LPG', 'tCO2_per_GJ': 0.0631, 'tCO2_per_kWh': None, 'tCO2_per_kg': None},
        {'fuel': 'Fuel_Oil', 'tCO2_per_GJ': 0.0773, 'tCO2_per_kWh': None, 'tCO2_per_kg': None},
        {'fuel': 'Diesel', 'tCO2_per_GJ': 0.0741, 'tCO2_per_kWh': None, 'tCO2_per_kg': None},
        {'fuel': 'H2', 'tCO2_per_GJ': None, 'tCO2_per_kWh': None, 'tCO2_per_kg': 0.0},
    ])


@pytest.fixture
def technology_capex_df():
    """Technology CAPEX data"""
    return pd.DataFrame([
        {'technology': 'Heat_Pump', 'capex_2025': 170, 'capex_2030': 140, 'capex_2040': 120, 'capex_2050': 100,
         'opex_pct_capex': 3.0, 'lifetime_years': 20, 'capex_unit': 'usd_per_t_product_yr'},
        {'technology': 'NCC-H2', 'capex_2025': 350, 'capex_2030': 280, 'capex_2040': 230, 'capex_2050': 180,
         'opex_pct_capex': 4.0, 'lifetime_years': 25, 'capex_unit': 'usd_per_t_ethylene_yr'},
        {'technology': 'NCC-Electricity', 'capex_2025': 280, 'capex_2030': 220, 'capex_2040': 185, 'capex_2050': 150,
         'opex_pct_capex': 4.0, 'lifetime_years': 25, 'capex_unit': 'usd_per_t_ethylene_yr'},
        {'technology': 'RDH', 'capex_2025': 250, 'capex_2030': 200, 'capex_2040': 170, 'capex_2050': 140,
         'opex_pct_capex': 3.0, 'lifetime_years': 25, 'capex_unit': 'usd_per_t_btx_yr'},
        {'technology': 'RE_PPA', 'capex_2025': 0, 'capex_2030': 0, 'capex_2040': 0, 'capex_2050': 0,
         'opex_pct_capex': 0, 'lifetime_years': 99, 'capex_unit': 'usd_per_mwh_premium'},
    ])


@pytest.fixture
def technology_params_df():
    """Technology parameters"""
    return pd.DataFrame([
        {'technology': 'Heat_Pump', 'applies_to': 'Non-NCC low-temp', 'cop': 4.0,
         'h2_ton_per_ton_ethylene': None, 'elec_mwh_per_ton_ethylene': None,
         'energy_conversion_efficiency': 0.95, 'trl': 9, 'available_year': 2025},
        {'technology': 'NCC-H2', 'applies_to': 'Naphtha Cracker', 'cop': None,
         'h2_ton_per_ton_ethylene': 0.2, 'elec_mwh_per_ton_ethylene': None,
         'energy_conversion_efficiency': 0.85, 'trl': 7, 'available_year': 2030},
        {'technology': 'NCC-Electricity', 'applies_to': 'Naphtha Cracker', 'cop': None,
         'h2_ton_per_ton_ethylene': None, 'elec_mwh_per_ton_ethylene': 5.0,
         'energy_conversion_efficiency': 0.95, 'trl': 8, 'available_year': 2030},
        {'technology': 'RDH', 'applies_to': 'BTX Plant', 'cop': None,
         'h2_ton_per_ton_ethylene': None, 'elec_mwh_per_ton_ethylene': None,
         'energy_conversion_efficiency': 0.93, 'trl': 8, 'available_year': 2026},
        {'technology': 'RE_PPA', 'applies_to': 'All electricity', 'cop': None,
         'h2_ton_per_ton_ethylene': None, 'elec_mwh_per_ton_ethylene': None,
         'energy_conversion_efficiency': 1.0, 'trl': None, 'available_year': 2025},
    ])


@pytest.fixture
def h2_prices_df():
    """H2 price trajectory"""
    return pd.DataFrame([
        {'year': 2025, 'h2_price_usd_per_kg': 4.58},
        {'year': 2030, 'h2_price_usd_per_kg': 3.91},
        {'year': 2040, 'h2_price_usd_per_kg': 2.82},
        {'year': 2050, 'h2_price_usd_per_kg': 2.01},
    ])


@pytest.fixture
def re_prices_df():
    """RE price trajectory"""
    return pd.DataFrame([
        {'year': 2025, 're_price_usd_per_mwh': 65.0},
        {'year': 2030, 're_price_usd_per_mwh': 55.69},
        {'year': 2040, 're_price_usd_per_mwh': 40.87},
        {'year': 2050, 're_price_usd_per_mwh': 30.0},
    ])


@pytest.fixture
def model_config():
    """Model configuration"""
    return {
        'discount_rate': 0.08,
        'gj_to_mwh': 3.6,
        'analysis_start_year': 2025,
        'analysis_end_year': 2050,
        'operating_rate_default': 0.7,
    }


# ============================================================================
# EMISSION CALCULATOR TESTS
# ============================================================================

class TestEmissionCalculator:
    """Tests for EmissionCalculator class"""

    def test_calculate_emissions_naphtha(self, emission_factors_df):
        """Verify naphtha emission calculation: 1 GJ * 0.0542 = 0.0542 tCO2"""
        calc = EmissionCalculator(emission_factors_df)
        result = calc.calculate_emissions('Naphtha', 1.0)
        assert result == pytest.approx(0.0542, rel=1e-3)

    def test_calculate_emissions_lng(self, emission_factors_df):
        """Verify LNG emission calculation: 1 GJ * 0.0561 = 0.0561 tCO2"""
        calc = EmissionCalculator(emission_factors_df)
        result = calc.calculate_emissions('LNG', 1.0)
        assert result == pytest.approx(0.0561, rel=1e-3)

    def test_calculate_emissions_lpg(self, emission_factors_df):
        """Verify LPG emission calculation: 1 GJ * 0.0631 = 0.0631 tCO2"""
        calc = EmissionCalculator(emission_factors_df)
        result = calc.calculate_emissions('LPG', 1.0)
        assert result == pytest.approx(0.0631, rel=1e-3)

    def test_calculate_emissions_electricity(self, emission_factors_df):
        """Verify electricity emission calculation: 1 kWh * 0.000436 = 0.000436 tCO2"""
        calc = EmissionCalculator(emission_factors_df)
        result = calc.calculate_emissions('Electricity', 1.0)
        assert result == pytest.approx(0.000436, rel=1e-3)

    def test_calculate_emissions_unknown_fuel_returns_zero(self, emission_factors_df):
        """Unknown fuel should return 0"""
        calc = EmissionCalculator(emission_factors_df)
        result = calc.calculate_emissions('UnknownFuel', 100.0)
        assert result == 0.0

    def test_calculate_emissions_h2_zero(self, emission_factors_df):
        """Green H2 should have zero emissions"""
        calc = EmissionCalculator(emission_factors_df)
        result = calc.calculate_emissions('H2', 1000.0)
        assert result == 0.0

    def test_calculate_emissions_large_energy(self, emission_factors_df):
        """Test with large energy values (typical NCC scale)"""
        calc = EmissionCalculator(emission_factors_df)
        # 10,000 TJ of naphtha
        result = calc.calculate_emissions('Naphtha', 10_000_000)  # GJ
        expected = 10_000_000 * 0.0542
        assert result == pytest.approx(expected, rel=1e-3)

    def test_calculate_baseline_metrics_ncc(self, emission_factors_df):
        """NCC facility: naphtha emissions should be 0 (feedstock treatment)"""
        calc = EmissionCalculator(emission_factors_df)

        facility_row = {'capacity_kt': 1000}  # 1000 kt = 1,000,000 tonnes
        intensities_row = {
            'Naphtha_GJ_per_tonne': 29.0,
            'Electricity_kWh_per_tonne': 85.4,
            'LNG_GJ_per_tonne': 2.027,
            'Fuel_Gas_GJ_per_tonne': 0,
            'Byproduct_Gas_GJ_per_tonne': 1.123,
            'LPG_GJ_per_tonne': 5.223,
            'Fuel_Oil_GJ_per_tonne': 0,
            'Diesel_GJ_per_tonne': 0,
        }

        result = calc.calculate_baseline_metrics(
            facility_row, intensities_row,
            operating_rate=0.7,
            capacity_multiplier=1.0,
            process='Naphtha Cracker'
        )

        # Naphtha emissions should be 0 for NCC
        assert result['emissions_by_source']['naphtha'] == 0.0
        # But naphtha energy should still be tracked
        expected_naphtha_gj = 1_000_000 * 0.7 * 29.0
        assert result['energy_by_source']['naphtha'] == pytest.approx(expected_naphtha_gj, rel=1e-3)
        # is_ncc flag should be True
        assert result['is_ncc'] == True

    def test_calculate_baseline_metrics_btx(self, emission_factors_df):
        """BTX facility: no naphtha in benchmarks"""
        calc = EmissionCalculator(emission_factors_df)

        facility_row = {'capacity_kt': 500}
        intensities_row = {
            'Naphtha_GJ_per_tonne': 0,  # BTX has no naphtha
            'Electricity_kWh_per_tonne': 36.6,
            'LNG_GJ_per_tonne': 1.146,
            'Fuel_Gas_GJ_per_tonne': 0,
            'Byproduct_Gas_GJ_per_tonne': 0.635,
            'LPG_GJ_per_tonne': 2.954,
            'Fuel_Oil_GJ_per_tonne': 0,
            'Diesel_GJ_per_tonne': 0,
        }

        result = calc.calculate_baseline_metrics(
            facility_row, intensities_row,
            operating_rate=0.7,
            process='BTX Plant'
        )

        # is_ncc should be False
        assert result['is_ncc'] == False
        # Naphtha energy should be 0
        assert result['energy_by_source']['naphtha'] == 0.0


# ============================================================================
# CAPEX CALCULATOR TESTS
# ============================================================================

class TestCapexCalculator:
    """Tests for CapexCalculator class"""

    def test_get_technology_capex_rate_2025(self, technology_capex_df, technology_params_df, model_config):
        """Verify exact CAPEX value for 2025"""
        calc = CapexCalculator(technology_capex_df, technology_params_df, model_config)

        # Heat Pump 2025: $170/t-product/yr
        result = calc.get_technology_capex_rate('Heat_Pump', 2025)
        assert result == pytest.approx(170.0, rel=1e-3)

        # NCC-H2 2025: $350/t-ethylene/yr
        result = calc.get_technology_capex_rate('NCC-H2', 2025)
        assert result == pytest.approx(350.0, rel=1e-3)

    def test_get_technology_capex_rate_2050(self, technology_capex_df, technology_params_df, model_config):
        """Verify exact CAPEX value for 2050"""
        calc = CapexCalculator(technology_capex_df, technology_params_df, model_config)

        # Heat Pump 2050: $100/t-product/yr
        result = calc.get_technology_capex_rate('Heat_Pump', 2050)
        assert result == pytest.approx(100.0, rel=1e-3)

        # NCC-H2 2050: $180/t-ethylene/yr
        result = calc.get_technology_capex_rate('NCC-H2', 2050)
        assert result == pytest.approx(180.0, rel=1e-3)

    def test_get_technology_capex_rate_interpolation(self, technology_capex_df, technology_params_df, model_config):
        """Verify interpolation between years"""
        calc = CapexCalculator(technology_capex_df, technology_params_df, model_config)

        # NCC-H2 at 2035 (midpoint between 2030 and 2040)
        # 2030: 280, 2040: 230 -> 2035: 255
        result = calc.get_technology_capex_rate('NCC-H2', 2035)
        assert result == pytest.approx(255.0, rel=1e-3)

    def test_get_technology_capex_rate_invalid_technology(self, technology_capex_df, technology_params_df, model_config):
        """Invalid technology should raise ValueError"""
        calc = CapexCalculator(technology_capex_df, technology_params_df, model_config)

        with pytest.raises(ValueError, match="not found"):
            calc.get_technology_capex_rate('InvalidTech', 2030)

    def test_calculate_annualized_capex(self, technology_capex_df, technology_params_df, model_config):
        """Verify CAPEX / lifetime calculation"""
        calc = CapexCalculator(technology_capex_df, technology_params_df, model_config)

        # $1,000,000 CAPEX / 25 years = $40,000/year
        result = calc.calculate_annualized_capex(1_000_000, 25)
        assert result == pytest.approx(40_000, rel=1e-3)

    def test_calculate_facility_capex(self, technology_capex_df, technology_params_df, model_config):
        """Total CAPEX = capacity * rate"""
        calc = CapexCalculator(technology_capex_df, technology_params_df, model_config)

        # 1,000,000 t/yr capacity * $350/t-ethylene/yr = $350,000,000
        result = calc.calculate_facility_capex('NCC-H2', 1_000_000, 2025)
        assert result['capex_total_usd'] == pytest.approx(350_000_000, rel=1e-3)
        assert result['capex_rate_usd_per_t'] == pytest.approx(350.0, rel=1e-3)

    def test_is_technology_available_before_year(self, technology_capex_df, technology_params_df, model_config):
        """Technology should not be available before its available_year"""
        calc = CapexCalculator(technology_capex_df, technology_params_df, model_config)

        # NCC-H2 available from 2030
        assert calc.is_technology_available('NCC-H2', 2029) == False
        assert calc.is_technology_available('NCC-H2', 2030) == True

        # Heat Pump available from 2025
        assert calc.is_technology_available('Heat_Pump', 2025) == True


# ============================================================================
# PRICE CALCULATOR TESTS
# ============================================================================

class TestPriceCalculator:
    """Tests for PriceCalculator class"""

    def test_get_h2_price_exact_year(self, h2_prices_df, re_prices_df):
        """Return exact value when year is in trajectory"""
        calc = PriceCalculator(h2_prices_df, re_prices_df)

        result = calc.get_h2_price(2025)
        assert result == pytest.approx(4.58, rel=1e-3)

        result = calc.get_h2_price(2050)
        assert result == pytest.approx(2.01, rel=1e-3)

    def test_get_h2_price_interpolation(self, h2_prices_df, re_prices_df):
        """Verify interpolation between years"""
        calc = PriceCalculator(h2_prices_df, re_prices_df)

        # 2035 is midpoint between 2030 and 2040
        # 2030: 3.91, 2040: 2.82 -> 2035: 3.365
        result = calc.get_h2_price(2035)
        expected = (3.91 + 2.82) / 2
        assert result == pytest.approx(expected, rel=1e-2)

    def test_get_re_price_exact_year(self, h2_prices_df, re_prices_df):
        """RE price exact year lookup"""
        calc = PriceCalculator(h2_prices_df, re_prices_df)

        result = calc.get_re_price(2025)
        assert result == pytest.approx(65.0, rel=1e-3)

        result = calc.get_re_price(2050)
        assert result == pytest.approx(30.0, rel=1e-3)

    def test_get_re_price_interpolation(self, h2_prices_df, re_prices_df):
        """Verify RE price interpolation"""
        calc = PriceCalculator(h2_prices_df, re_prices_df)

        # 2035 midpoint
        result = calc.get_re_price(2035)
        expected = (55.69 + 40.87) / 2
        assert result == pytest.approx(expected, rel=1e-2)


# ============================================================================
# MAC CALCULATOR TESTS
# ============================================================================

class TestMACCalculator:
    """Tests for MAC calculation"""

    def test_mac_basic_calculation(self, technology_capex_df, technology_params_df,
                                    h2_prices_df, re_prices_df, emission_factors_df, model_config):
        """MAC = total_annual_cost / abatement"""
        capex_calc = CapexCalculator(technology_capex_df, technology_params_df, model_config)
        price_calc = PriceCalculator(h2_prices_df, re_prices_df)
        emission_calc = EmissionCalculator(emission_factors_df)

        mac_calc = MACCalculator(capex_calc, price_calc, emission_calc)

        # Simple facility baseline for Heat Pump
        # Note: MAC can be negative when fuel savings exceed new energy costs
        facility_baseline = {
            'production_t': 100_000,
            'combustion_emissions': 50_000,  # 50,000 tCO2
            'heat_demand_gj': 500_000,
            'energy_by_source': {'lng': 500_000},
            'is_ncc': False,
            'process': 'Utility'
        }
        fuel_prices = {'lng_usd_per_gj': 12.0}

        result = mac_calc.calculate_mac(facility_baseline, 'Heat_Pump', 2030, fuel_prices)

        # Verify MAC is calculated (can be positive or negative)
        assert 'mac_usd_per_tco2' in result
        assert result['abatement_tco2'] == 50_000
        assert result['technology'] == 'Heat_Pump'
        # MAC is finite (not inf or nan)
        assert np.isfinite(result['mac_usd_per_tco2'])

    def test_mac_zero_abatement_returns_inf(self, technology_capex_df, technology_params_df,
                                            h2_prices_df, re_prices_df, emission_factors_df, model_config):
        """Zero abatement should return infinity"""
        capex_calc = CapexCalculator(technology_capex_df, technology_params_df, model_config)
        price_calc = PriceCalculator(h2_prices_df, re_prices_df)
        emission_calc = EmissionCalculator(emission_factors_df)

        mac_calc = MACCalculator(capex_calc, price_calc, emission_calc)

        facility_baseline = {
            'production_t': 100_000,
            'combustion_emissions': 0,  # Zero abatement potential
            'heat_demand_gj': 0,
            'energy_by_source': {},
            'is_ncc': False,
            'process': 'Utility'
        }

        result = mac_calc.calculate_mac(facility_baseline, 'Heat_Pump', 2030, {})

        assert result['mac_usd_per_tco2'] == np.inf

    def test_mac_includes_fuel_savings(self, technology_capex_df, technology_params_df,
                                       h2_prices_df, re_prices_df, emission_factors_df, model_config):
        """Verify fuel savings reduce total cost"""
        capex_calc = CapexCalculator(technology_capex_df, technology_params_df, model_config)
        price_calc = PriceCalculator(h2_prices_df, re_prices_df)
        emission_calc = EmissionCalculator(emission_factors_df)

        mac_calc = MACCalculator(capex_calc, price_calc, emission_calc)

        facility_baseline = {
            'production_t': 100_000,
            'combustion_emissions': 50_000,
            'heat_demand_gj': 500_000,
            'energy_by_source': {'lng': 500_000},  # 500,000 GJ of LNG
            'is_ncc': False,
            'process': 'Utility'
        }

        # Test with and without fuel savings
        result_with_savings = mac_calc.calculate_mac(
            facility_baseline, 'Heat_Pump', 2030,
            {'lng_usd_per_gj': 12.0}
        )

        result_no_savings = mac_calc.calculate_mac(
            facility_baseline, 'Heat_Pump', 2030,
            {'lng_usd_per_gj': 0.0}  # No fuel cost = no savings
        )

        # MAC with fuel savings should be lower
        assert result_with_savings['mac_usd_per_tco2'] < result_no_savings['mac_usd_per_tco2']
        # Fuel savings should be positive when fuel has a price
        assert result_with_savings['fuel_savings_usd'] > 0

    def test_ncc_naphtha_not_in_fuel_savings(self, technology_capex_df, technology_params_df,
                                             h2_prices_df, re_prices_df, emission_factors_df, model_config):
        """NCC naphtha should not contribute to fuel savings (it's feedstock)"""
        capex_calc = CapexCalculator(technology_capex_df, technology_params_df, model_config)
        price_calc = PriceCalculator(h2_prices_df, re_prices_df)
        emission_calc = EmissionCalculator(emission_factors_df)

        mac_calc = MACCalculator(capex_calc, price_calc, emission_calc)

        facility_baseline = {
            'production_t': 100_000,
            'combustion_emissions': 10_000,
            'heat_demand_gj': 100_000,
            'energy_by_source': {
                'naphtha': 2_900_000,  # Large naphtha feedstock
                'lng': 100_000
            },
            'is_ncc': True,  # This is an NCC facility
            'process': 'Naphtha Cracker'
        }

        fuel_prices = {
            'naphtha_usd_per_gj': 15.0,
            'lng_usd_per_gj': 12.0
        }

        result = mac_calc.calculate_mac(facility_baseline, 'NCC-H2', 2030, fuel_prices)

        # Fuel savings should NOT include naphtha (feedstock)
        # Only LNG should contribute to savings
        expected_lng_savings = 100_000 * 12.0
        assert result['fuel_savings_usd'] == pytest.approx(expected_lng_savings, rel=1e-3)


# ============================================================================
# TECHNOLOGY COST CALCULATOR TESTS
# ============================================================================

class TestTechnologyCostCalculator:
    """Tests for TechnologyCostCalculator class"""

    def test_heat_pump_energy_calculation(self, technology_params_df, emission_factors_df, model_config):
        """Verify Heat Pump: electricity = heat / 3.6 / COP"""
        emission_calc = EmissionCalculator(emission_factors_df)
        tech_calc = TechnologyCostCalculator(technology_params_df, emission_calc, model_config)

        facility_baseline = {
            'production_t': 100_000,
            'combustion_emissions': 10_000,
            'emissions_by_source': {'naphtha': 0, 'lng': 5000, 'lpg': 5000},
            'heat_demand_gj': 360_000,  # 360,000 GJ
            'is_ncc': False
        }

        result = tech_calc.calculate_abatement_requirements(
            'Heat_Pump', facility_baseline, 'Utility', 'NCC-H2'
        )

        # Expected: 360,000 GJ / 3.6 GJ/MWh / 4.0 COP = 25,000 MWh
        expected_elec = 360_000 / 3.6 / 4.0
        assert result['added_elec_mwh'] == pytest.approx(expected_elec, rel=1e-3)
        assert result['h2_demand_t'] == 0.0

    def test_ncc_h2_demand_calculation(self, technology_params_df, emission_factors_df, model_config):
        """Verify NCC-H2: H2 demand = production * 0.2 t-H2/t-ethylene"""
        emission_calc = EmissionCalculator(emission_factors_df)
        tech_calc = TechnologyCostCalculator(technology_params_df, emission_calc, model_config)

        facility_baseline = {
            'production_t': 1_000_000,  # 1 million tonnes ethylene
            'combustion_emissions': 500_000,
            'emissions_by_source': {'naphtha': 0, 'lng': 100_000, 'lpg': 300_000, 'byproduct_gas': 100_000},
            'heat_demand_gj': 8_000_000,
            'is_ncc': True
        }

        result = tech_calc.calculate_abatement_requirements(
            'NCC-H2', facility_baseline, 'Naphtha Cracker', 'NCC-H2'
        )

        # Expected H2: 1,000,000 t * 0.2 = 200,000 t H2
        assert result['h2_demand_t'] == pytest.approx(200_000, rel=1e-3)

    def test_ncc_electricity_demand_calculation(self, technology_params_df, emission_factors_df, model_config):
        """Verify NCC-Electricity: demand = production * 5.0 MWh/t-ethylene"""
        emission_calc = EmissionCalculator(emission_factors_df)
        tech_calc = TechnologyCostCalculator(technology_params_df, emission_calc, model_config)

        facility_baseline = {
            'production_t': 1_000_000,
            'combustion_emissions': 500_000,
            'emissions_by_source': {'naphtha': 0, 'lng': 100_000, 'lpg': 300_000, 'byproduct_gas': 100_000},
            'heat_demand_gj': 8_000_000,
            'is_ncc': True
        }

        result = tech_calc.calculate_abatement_requirements(
            'NCC-Electricity', facility_baseline, 'Naphtha Cracker', 'NCC-Electricity'
        )

        # Expected: 1,000,000 t * 5.0 MWh/t = 5,000,000 MWh (plus heat pump for remaining heat)
        # But the heat pump component requires calculating remaining heat
        assert result['added_elec_mwh'] >= 5_000_000  # At least the e-cracker demand


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_zero_capacity_facility(self, technology_capex_df, technology_params_df, model_config):
        """Zero capacity should result in zero CAPEX"""
        calc = CapexCalculator(technology_capex_df, technology_params_df, model_config)
        result = calc.calculate_facility_capex('Heat_Pump', 0, 2030)
        assert result['capex_total_usd'] == 0.0

    def test_very_small_facility(self, emission_factors_df):
        """Very small facility should still calculate correctly"""
        calc = EmissionCalculator(emission_factors_df)

        facility_row = {'capacity_kt': 1}  # 1 kt = 1000 tonnes (smallest typical facility)
        intensities_row = {
            'Naphtha_GJ_per_tonne': 0,
            'Electricity_kWh_per_tonne': 100,
            'LNG_GJ_per_tonne': 1.0,
            'Fuel_Gas_GJ_per_tonne': 0,
            'Byproduct_Gas_GJ_per_tonne': 0,
            'LPG_GJ_per_tonne': 0,
            'Fuel_Oil_GJ_per_tonne': 0,
            'Diesel_GJ_per_tonne': 0,
        }

        result = calc.calculate_baseline_metrics(
            facility_row, intensities_row,
            operating_rate=0.7,
            process='Utility'
        )

        # Production should be 700 tonnes
        assert result['production_t'] == pytest.approx(700, rel=1e-3)
        # Emissions should be small but positive
        assert result['total_emissions'] > 0

    def test_year_before_trajectory(self, h2_prices_df, re_prices_df):
        """Year before trajectory should extrapolate"""
        calc = PriceCalculator(h2_prices_df, re_prices_df)
        # 2020 is before 2025 trajectory start
        result = calc.get_h2_price(2020)
        # Should extrapolate (or clamp to first value)
        assert result >= 0  # At minimum, should be non-negative

    def test_year_after_trajectory(self, h2_prices_df, re_prices_df):
        """Year after trajectory should extrapolate"""
        calc = PriceCalculator(h2_prices_df, re_prices_df)
        result = calc.get_h2_price(2060)
        # Should extrapolate (or clamp to last value)
        assert result >= 0


# ============================================================================
# STRICT MODE TESTS
# ============================================================================

class TestStrictMode:
    """Tests for strict mode that fails on missing CSV parameters"""

    def test_capex_calculator_strict_mode_missing_opex(self, technology_params_df, model_config):
        """Strict mode should raise error when opex_pct_capex is missing"""
        # Create CAPEX DataFrame with missing opex_pct_capex
        capex_df = pd.DataFrame([{
            'technology': 'Heat_Pump',
            'capex_2025': 100,
            'capex_2030': 90,
            'capex_2040': 80,
            'capex_2050': 70,
            'lifetime_years': 25,
            'capex_unit': 'usd_per_t_product_yr',
            # opex_pct_capex intentionally missing
        }])

        calc = CapexCalculator(capex_df, technology_params_df, model_config, strict=True)

        with pytest.raises(ValueError, match="opex_pct_capex not found"):
            calc.get_capex_info('Heat_Pump')

    def test_capex_calculator_strict_mode_missing_lifetime(self, technology_params_df, model_config):
        """Strict mode should raise error when lifetime_years is missing"""
        # Create CAPEX DataFrame with missing lifetime_years
        capex_df = pd.DataFrame([{
            'technology': 'Heat_Pump',
            'capex_2025': 100,
            'capex_2030': 90,
            'capex_2040': 80,
            'capex_2050': 70,
            'opex_pct_capex': 3.0,
            'capex_unit': 'usd_per_t_product_yr',
            # lifetime_years intentionally missing
        }])

        calc = CapexCalculator(capex_df, technology_params_df, model_config, strict=True)

        with pytest.raises(ValueError, match="lifetime_years not found"):
            calc.get_capex_info('Heat_Pump')

    def test_capex_calculator_non_strict_uses_fallback(self, technology_params_df, model_config):
        """Non-strict mode should use fallback values with warnings"""
        # Create CAPEX DataFrame with missing opex_pct_capex
        capex_df = pd.DataFrame([{
            'technology': 'Heat_Pump',
            'capex_2025': 100,
            'capex_2030': 90,
            'capex_2040': 80,
            'capex_2050': 70,
            # Missing: opex_pct_capex, lifetime_years, capex_unit
        }])

        calc = CapexCalculator(capex_df, technology_params_df, model_config, strict=False)

        # Should not raise, but use fallback values
        with pytest.warns(UserWarning):
            result = calc.get_capex_info('Heat_Pump')

        # Verify fallback values are used
        assert result['opex_pct_capex'] == 3.0
        assert result['lifetime_years'] == 25
        assert result['capex_unit'] == 'usd_per_t_product_yr'

    def test_technology_cost_calculator_requires_model_config(self, technology_params_df, emission_factors_df):
        """TechnologyCostCalculator should raise error when model_config is missing"""
        emission_calc = EmissionCalculator(emission_factors_df)

        with pytest.raises(ValueError, match="model_config missing required 'gj_to_mwh' parameter"):
            TechnologyCostCalculator(technology_params_df, emission_calc, model_config=None)

    def test_technology_cost_calculator_requires_gj_to_mwh(self, technology_params_df, emission_factors_df):
        """TechnologyCostCalculator should raise error when gj_to_mwh is missing from model_config"""
        emission_calc = EmissionCalculator(emission_factors_df)

        # model_config without gj_to_mwh
        incomplete_config = {'discount_rate': 0.08}

        with pytest.raises(ValueError, match="model_config missing required 'gj_to_mwh' parameter"):
            TechnologyCostCalculator(technology_params_df, emission_calc, model_config=incomplete_config)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
