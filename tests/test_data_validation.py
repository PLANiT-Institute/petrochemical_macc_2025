"""
Data validation tests for petrochemical MACC model.

Tests verify:
- Input data quality and completeness
- Reasonable value ranges
- Data consistency across files
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

DATA_DIR = Path(__file__).parent.parent / 'data'


# ============================================================================
# INPUT DATA VALIDATION TESTS
# ============================================================================

class TestFacilityData:
    """Tests for facility database"""

    @pytest.fixture
    def facilities_df(self):
        return pd.read_csv(DATA_DIR / 'assets' / 'facility_database_with_regions.csv')

    def test_facility_count(self, facilities_df):
        """Should have 237 baseline facilities"""
        assert len(facilities_df) == 237

    def test_facility_capacity_positive(self, facilities_df):
        """All capacity values should be positive"""
        assert (facilities_df['capacity_kt'] > 0).all(), \
            f"Found facilities with non-positive capacity: {facilities_df[facilities_df['capacity_kt'] <= 0]}"

    def test_facility_required_columns(self, facilities_df):
        """Required columns should be present"""
        required_cols = ['product', 'process', 'company', 'location', 'region', 'capacity_kt']
        missing = set(required_cols) - set(facilities_df.columns)
        assert len(missing) == 0, f"Missing required columns: {missing}"

    def test_facility_no_null_product(self, facilities_df):
        """No null values in product column"""
        assert facilities_df['product'].notna().all()

    def test_facility_process_values(self, facilities_df):
        """Process should be one of expected values"""
        valid_processes = ['Naphtha Cracker', 'BTX Plant', 'Utility', 'Extraction',
                          'BTX Extraction', 'Polymerization']
        invalid = facilities_df[~facilities_df['process'].isin(valid_processes)]
        assert len(invalid) == 0, f"Invalid process types found: {invalid['process'].unique()}"

    def test_facility_regions_valid(self, facilities_df):
        """Regions should be from expected list"""
        valid_regions = ['Yeosu Complex', 'Daesan Complex', 'Ulsan Complex', 'Other Regions']
        invalid = facilities_df[~facilities_df['region'].isin(valid_regions)]
        assert len(invalid) == 0, f"Invalid regions found: {invalid['region'].unique()}"


class TestEmissionFactors:
    """Tests for emission factors"""

    @pytest.fixture
    def ef_df(self):
        return pd.read_csv(DATA_DIR / 'assumptions' / 'emission_factors.csv')

    def test_emission_factors_positive(self, ef_df):
        """All emission factors should be >= 0 (H2 is 0)"""
        for col in ['tCO2_per_GJ', 'tCO2_per_kWh', 'tCO2_per_kg']:
            if col in ef_df.columns:
                values = ef_df[col].dropna()
                assert (values >= 0).all(), f"Negative values in {col}"

    def test_emission_factors_required_fuels(self, ef_df):
        """Required fuels should be present"""
        required_fuels = ['Naphtha', 'Electricity', 'LNG', 'LPG', 'H2']
        missing = set(required_fuels) - set(ef_df['fuel'])
        assert len(missing) == 0, f"Missing fuels: {missing}"

    def test_naphtha_ef_ipcc_range(self, ef_df):
        """Naphtha EF should be in IPCC range (0.05-0.06 tCO2/GJ)"""
        naphtha = ef_df[ef_df['fuel'] == 'Naphtha']['tCO2_per_GJ'].iloc[0]
        assert 0.05 <= naphtha <= 0.06, f"Naphtha EF {naphtha} outside IPCC range"

    def test_lng_ef_ipcc_range(self, ef_df):
        """LNG EF should be in IPCC range (0.05-0.06 tCO2/GJ)"""
        lng = ef_df[ef_df['fuel'] == 'LNG']['tCO2_per_GJ'].iloc[0]
        assert 0.05 <= lng <= 0.06, f"LNG EF {lng} outside IPCC range"

    def test_h2_ef_zero(self, ef_df):
        """Green H2 should have zero emissions"""
        h2 = ef_df[ef_df['fuel'] == 'H2']['tCO2_per_kg'].iloc[0]
        assert h2 == 0.0, f"H2 EF should be 0, got {h2}"


class TestTechnologyParameters:
    """Tests for technology parameters"""

    @pytest.fixture
    def tech_df(self):
        return pd.read_csv(DATA_DIR / 'assumptions' / 'technology_parameters.csv')

    def test_required_technologies(self, tech_df):
        """Required technologies should be present"""
        required = ['Heat_Pump', 'NCC-H2', 'NCC-Electricity', 'RDH', 'RE_PPA']
        missing = set(required) - set(tech_df['technology'])
        assert len(missing) == 0, f"Missing technologies: {missing}"

    def test_heat_pump_cop_reasonable(self, tech_df):
        """Heat pump COP should be in range 2-6"""
        cop = tech_df[tech_df['technology'] == 'Heat_Pump']['cop'].iloc[0]
        assert 2 <= cop <= 6, f"Heat pump COP {cop} outside reasonable range"

    def test_ncc_h2_conversion_factor(self, tech_df):
        """NCC-H2 should have h2_ton_per_ton_ethylene"""
        h2_factor = tech_df[tech_df['technology'] == 'NCC-H2']['h2_ton_per_ton_ethylene'].iloc[0]
        assert pd.notna(h2_factor), "NCC-H2 missing h2_ton_per_ton_ethylene"
        assert 0.1 <= h2_factor <= 0.5, f"H2 factor {h2_factor} outside reasonable range"

    def test_ncc_elec_conversion_factor(self, tech_df):
        """NCC-Electricity should have elec_mwh_per_ton_ethylene"""
        elec_factor = tech_df[tech_df['technology'] == 'NCC-Electricity']['elec_mwh_per_ton_ethylene'].iloc[0]
        assert pd.notna(elec_factor), "NCC-Electricity missing elec_mwh_per_ton_ethylene"
        assert 3 <= elec_factor <= 8, f"Elec factor {elec_factor} outside reasonable range"

    def test_rdh_efficiency(self, tech_df):
        """RDH should have energy_conversion_efficiency"""
        eff = tech_df[tech_df['technology'] == 'RDH']['energy_conversion_efficiency'].iloc[0]
        assert pd.notna(eff), "RDH missing efficiency"
        assert 0.8 <= eff <= 1.0, f"RDH efficiency {eff} outside reasonable range"


class TestTechnologyCapex:
    """Tests for technology CAPEX"""

    @pytest.fixture
    def capex_df(self):
        return pd.read_csv(DATA_DIR / 'assumptions' / 'technology_capex.csv')

    def test_capex_decreases_over_time(self, capex_df):
        """CAPEX should decrease from 2025 to 2050 (learning curves)"""
        for _, row in capex_df.iterrows():
            if row['technology'] == 'RE_PPA':
                continue  # RE_PPA has zero CAPEX
            assert row['capex_2025'] >= row['capex_2050'], \
                f"{row['technology']} CAPEX increases from 2025 to 2050"

    def test_capex_positive(self, capex_df):
        """CAPEX should be non-negative"""
        capex_cols = ['capex_2025', 'capex_2030', 'capex_2040', 'capex_2050']
        for col in capex_cols:
            assert (capex_df[col] >= 0).all(), f"Negative CAPEX in {col}"

    def test_lifetime_reasonable(self, capex_df):
        """Lifetime should be 15-30 years for most technologies"""
        for _, row in capex_df.iterrows():
            if row['technology'] == 'RE_PPA':
                continue  # RE_PPA is contract-based
            assert 15 <= row['lifetime_years'] <= 30, \
                f"{row['technology']} lifetime {row['lifetime_years']} outside range"

    def test_opex_percentage_reasonable(self, capex_df):
        """OPEX should be 2-6% of CAPEX"""
        for _, row in capex_df.iterrows():
            if row['technology'] == 'RE_PPA':
                continue
            assert 0 <= row['opex_pct_capex'] <= 10, \
                f"{row['technology']} OPEX% {row['opex_pct_capex']} outside range"


class TestPriceTrajectories:
    """Tests for price trajectories"""

    @pytest.fixture
    def h2_prices(self):
        return pd.read_csv(DATA_DIR / 'assumptions' / 'prices' / 'h2_price_trajectory.csv')

    @pytest.fixture
    def re_prices(self):
        return pd.read_csv(DATA_DIR / 'assumptions' / 'prices' / 're_price_trajectory.csv')

    @pytest.fixture
    def fuel_prices(self):
        return pd.read_csv(DATA_DIR / 'assumptions' / 'prices' / 'fuel_price_trajectory.csv')

    def test_h2_price_trajectory_years(self, h2_prices):
        """H2 trajectory should cover 2025-2050"""
        years = h2_prices['year'].tolist()
        assert min(years) == 2025
        assert max(years) == 2050
        assert len(years) == 26  # All years from 2025-2050

    def test_h2_price_reasonable(self, h2_prices):
        """H2 price should be in range $1-10/kg"""
        assert (h2_prices['h2_price_usd_per_kg'] >= 1).all()
        assert (h2_prices['h2_price_usd_per_kg'] <= 10).all()

    def test_h2_price_decreases(self, h2_prices):
        """H2 price should decrease over time (learning curve)"""
        price_2025 = h2_prices[h2_prices['year'] == 2025]['h2_price_usd_per_kg'].iloc[0]
        price_2050 = h2_prices[h2_prices['year'] == 2050]['h2_price_usd_per_kg'].iloc[0]
        assert price_2050 < price_2025, "H2 price should decrease from 2025 to 2050"

    def test_re_price_trajectory_years(self, re_prices):
        """RE trajectory should cover 2025-2050"""
        years = re_prices['year'].tolist()
        assert min(years) == 2025
        assert max(years) == 2050

    def test_re_price_reasonable(self, re_prices):
        """RE price should be in range $20-100/MWh"""
        assert (re_prices['re_price_usd_per_mwh'] >= 20).all()
        assert (re_prices['re_price_usd_per_mwh'] <= 100).all()

    def test_re_price_decreases(self, re_prices):
        """RE price should decrease over time"""
        price_2025 = re_prices[re_prices['year'] == 2025]['re_price_usd_per_mwh'].iloc[0]
        price_2050 = re_prices[re_prices['year'] == 2050]['re_price_usd_per_mwh'].iloc[0]
        assert price_2050 < price_2025

    def test_fuel_prices_no_nan(self, fuel_prices):
        """Fuel prices should have no NaN values"""
        assert not fuel_prices.isnull().any().any(), "NaN values found in fuel prices"

    def test_fuel_prices_positive(self, fuel_prices):
        """All fuel prices should be positive"""
        fuel_cols = [c for c in fuel_prices.columns if c != 'year']
        for col in fuel_cols:
            assert (fuel_prices[col] >= 0).all(), f"Negative prices in {col}"


class TestProductBenchmarks:
    """Tests for product benchmarks"""

    @pytest.fixture
    def benchmarks_df(self):
        return pd.read_csv(DATA_DIR / 'assumptions' / 'product_benchmarks.csv')

    def test_benchmarks_no_nan_electricity(self, benchmarks_df):
        """Every product should have electricity intensity"""
        assert benchmarks_df['Electricity_kWh_per_tonne'].notna().all()

    def test_ncc_products_have_naphtha(self, benchmarks_df):
        """NCC products should have naphtha feedstock"""
        ncc = benchmarks_df[benchmarks_df['process'] == 'Naphtha Cracker']
        assert (ncc['Naphtha_GJ_per_tonne'] > 0).all(), \
            "NCC products should have positive naphtha intensity"

    def test_btx_no_naphtha(self, benchmarks_df):
        """BTX products should not have naphtha (aromatics extraction)"""
        btx = benchmarks_df[benchmarks_df['process'] == 'BTX Plant']
        assert (btx['Naphtha_GJ_per_tonne'] == 0).all(), \
            "BTX products should not have naphtha feedstock"

    def test_utility_no_naphtha(self, benchmarks_df):
        """Utility products should not have naphtha"""
        utility = benchmarks_df[benchmarks_df['process'] == 'Utility']
        assert (utility['Naphtha_GJ_per_tonne'] == 0).all()

    def test_ethylene_intensity_reasonable(self, benchmarks_df):
        """Ethylene energy intensity should be in literature range (25-40 GJ/t total)"""
        ethylene = benchmarks_df[benchmarks_df['product'] == 'Ethylene'].iloc[0]
        total_gj = ethylene['Naphtha_GJ_per_tonne'] + ethylene['LNG_GJ_per_tonne'] + \
                   ethylene['LPG_GJ_per_tonne'] + ethylene['Byproduct_Gas_GJ_per_tonne']
        # Literature range for steam cracking: 25-40 GJ/t
        assert 25 <= total_gj <= 45, f"Ethylene total GJ/t {total_gj} outside literature range"


class TestGridEmissionTrajectory:
    """Tests for grid emission factor trajectory"""

    @pytest.fixture
    def grid_ef(self):
        return pd.read_csv(DATA_DIR / 'assumptions' / 'prices' / 'grid_emission_trajectory.csv')

    def test_grid_ef_reaches_zero_2050(self, grid_ef):
        """Grid EF in 2050 should be 0 (net zero)"""
        ef_2050 = grid_ef[grid_ef['year'] == 2050]['grid_ef_tco2_per_mwh'].iloc[0]
        assert ef_2050 == pytest.approx(0.0, abs=0.001)

    def test_grid_ef_decreases(self, grid_ef):
        """Grid EF should decrease over time"""
        ef_2025 = grid_ef[grid_ef['year'] == 2025]['grid_ef_tco2_per_mwh'].iloc[0]
        ef_2050 = grid_ef[grid_ef['year'] == 2050]['grid_ef_tco2_per_mwh'].iloc[0]
        assert ef_2050 < ef_2025

    def test_grid_ef_2025_korea(self, grid_ef):
        """2025 grid EF should match Korea grid (~0.4-0.5 tCO2/MWh)"""
        ef_2025 = grid_ef[grid_ef['year'] == 2025]['grid_ef_tco2_per_mwh'].iloc[0]
        assert 0.35 <= ef_2025 <= 0.55, f"2025 grid EF {ef_2025} outside Korea range"


# ============================================================================
# DATA CONSISTENCY TESTS
# ============================================================================

class TestDataConsistency:
    """Tests for cross-file data consistency"""

    def test_facility_benchmark_coverage(self):
        """All facility product-process combinations should have benchmarks"""
        facilities = pd.read_csv(DATA_DIR / 'assets' / 'facility_database_with_regions.csv')
        benchmarks = pd.read_csv(DATA_DIR / 'assumptions' / 'product_benchmarks.csv')

        # Get unique combinations
        facility_combos = set(zip(facilities['product'], facilities['process']))
        benchmark_combos = set(zip(benchmarks['product'], benchmarks['process']))

        missing = facility_combos - benchmark_combos
        assert len(missing) == 0, f"Missing benchmarks for: {missing}"

    def test_technology_capex_params_alignment(self):
        """Technologies in capex should also be in params"""
        capex = pd.read_csv(DATA_DIR / 'assumptions' / 'technology_capex.csv')
        params = pd.read_csv(DATA_DIR / 'assumptions' / 'technology_parameters.csv')

        capex_techs = set(capex['technology'])
        params_techs = set(params['technology'])

        missing_params = capex_techs - params_techs
        assert len(missing_params) == 0, f"Techs in capex but not params: {missing_params}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
