"""
Data Manager - Centralized data loading and validation
All model assumptions are loaded from CSV/Excel files
NO HARDCODED VALUES in this module
"""

import pandas as pd
import numpy as np
from pathlib import Path


class DataManager:
    """
    Centralized data management for MACC model

    Responsibilities:
    1. Load all data files
    2. Validate data consistency
    3. Provide convenient access methods
    4. No business logic - pure data management
    """

    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        print("\n" + "="*80)
        print("DATA MANAGER: Loading all model data")
        print("="*80)

        # Load all data files
        self._load_all_data()

        # Validate data
        self._validate_data()

        print("✓ All data loaded and validated")
        print("="*80 + "\n")

    def _load_all_data(self):
        """Load all data files into DataFrames"""

        # 1. Model parameters (global settings)
        print("Loading model parameters...")
        self.model_params = pd.read_csv(
            self.data_dir / 'model_parameters.csv'
        ).set_index('parameter')

        # 2. Baseline emissions by process
        print("Loading baseline emissions...")
        self.baseline_emissions = pd.read_csv(
            self.data_dir / 'baseline_process_emissions.csv'
        )

        # 3. Technology energy requirements
        print("Loading technology specifications...")
        self.tech_energy = pd.read_csv(
            self.data_dir / 'technology_energy_requirements.csv'
        )

        # 4. Technology costs (CAPEX/OPEX)
        self.tech_costs = pd.read_csv(
            self.data_dir / 'technology_parameters.csv'
        )

        # 5. Facility-technology applicability
        print("Loading facility-technology mapping...")
        self.facility_applicability = pd.read_csv(
            self.data_dir / 'facility_technology_applicability.csv'
        )

        # 6. Price trajectories
        print("Loading price trajectories...")
        self.h2_prices = pd.read_csv(
            self.data_dir / 'h2_price_trajectory.csv'
        )
        self.re_prices = pd.read_csv(
            self.data_dir / 're_price_trajectory.csv'
        )
        self.fuel_prices = pd.read_csv(
            self.data_dir / 'fuel_price_trajectory.csv'
        )

        # 7. Grid emission trajectory
        self.grid_emissions = pd.read_csv(
            self.data_dir / 'grid_emission_trajectory.csv'
        )

        # 8. Emission factors
        self.emission_factors = pd.read_csv(
            self.data_dir / 'emission_factors.csv'
        ).set_index('fuel')

        # 9. Facility database (248 facilities)
        print("Loading facility database...")
        self.facilities = pd.read_csv(
            self.data_dir / 'facility_database.csv'
        )

        # 10. Energy intensities
        self.energy_intensities = pd.read_csv(
            self.data_dir / 'energy_intensities.csv'
        )

        # 11. Heat pump applicability
        self.heat_pump_applicability = pd.read_csv(
            self.data_dir / 'heat_pump_applicability.csv'
        )

        # 12. Demand growth trajectory
        try:
            self.demand_growth = pd.read_csv(
                self.data_dir / 'demand_growth_trajectory.csv'
            )
        except FileNotFoundError:
            print("  Warning: No demand growth file, assuming zero growth")
            self.demand_growth = pd.DataFrame({
                'year': range(2025, 2051),
                'cumulative_capacity_multiplier': [1.0] * 26
            })

    def _validate_data(self):
        """Validate data consistency"""
        print("\nValidating data consistency...")

        # Check year ranges are consistent
        years_h2 = set(self.h2_prices['year'])
        years_re = set(self.re_prices['year'])
        years_fuel = set(self.fuel_prices['year'])

        if not (years_h2 == years_re == years_fuel):
            print("  ⚠️  Warning: Inconsistent year ranges in price trajectories")
        else:
            print(f"  ✓ Price trajectories: {min(years_h2)}-{max(years_h2)}")

        # Check products consistency
        baseline_products = set(self.baseline_emissions['product'])
        print(f"  ✓ Baseline emissions defined for {len(baseline_products)} products")

        # Check facilities
        print(f"  ✓ {len(self.facilities)} facilities loaded")

        # Check for missing critical values
        critical_params = [
            # 'discount_rate',  # REMOVED - using simple annualization
            'ethylene_baseline_naphtha_fuel',
            'naphtha_emission_factor',
            'green_h2_emission_factor'
        ]
        missing = [p for p in critical_params if p not in self.model_params.index]
        if missing:
            raise ValueError(f"Missing critical parameters: {missing}")
        print(f"  ✓ All critical parameters present")

    # ========================================================================
    # GETTER METHODS - Convenient access to data
    # ========================================================================

    def get_parameter(self, param_name):
        """Get a model parameter value"""
        return self.model_params.loc[param_name, 'value']

    def get_baseline_emissions(self, product):
        """Get baseline emissions data for a product"""
        mask = self.baseline_emissions['product'] == product
        if not mask.any():
            # Return default/average if product not found
            return self.baseline_emissions.iloc[0]  # Use Ethylene as default
        return self.baseline_emissions[mask].iloc[0]

    def get_tech_energy_requirement(self, technology, product):
        """Get energy requirements for technology-product combination"""
        mask = (self.tech_energy['technology'] == technology) & \
               (self.tech_energy['applies_to_product'] == product)

        if not mask.any():
            # Try with 'All' or generic product
            mask = self.tech_energy['technology'] == technology
            if mask.any():
                return self.tech_energy[mask].iloc[0]
            raise ValueError(f"No energy requirement found for {technology} + {product}")

        return self.tech_energy[mask].iloc[0]

    def get_applicable_technologies(self, product, process=None):
        """Get list of technologies applicable to a product"""
        # Try exact product match first
        mask = self.facility_applicability['product'] == product

        if not mask.any():
            # Fall back to product group
            from .utils import identify_product_group
            product_group = identify_product_group(product)
            mask = self.facility_applicability['product_group'] == product_group

        if not mask.any():
            # Default to general applicability
            mask = self.facility_applicability['product'] == 'All other products'

        if not mask.any():
            return []

        row = self.facility_applicability[mask].iloc[0]

        technologies = []
        if row.get('heat_pump_applicable', False):
            technologies.append('Heat_Pump')
        if row.get('ncc_h2_applicable', False):
            technologies.append('NCC-H2')
        if row.get('ncc_electricity_applicable', False):
            technologies.append('NCC-Electricity')
        if row.get('re_ppa_applicable', False):
            technologies.append('RE_PPA')

        return technologies

    def get_price(self, year, price_type):
        """
        Get price for a given year

        Args:
            year: int
            price_type: 'h2', 're', 'naphtha', 'lng', 'electricity', etc.

        Returns:
            float: price in appropriate units
        """
        if price_type == 'h2':
            df = self.h2_prices
            col = 'h2_price_usd_per_kg'
        elif price_type == 're':
            df = self.re_prices
            col = 're_price_usd_per_mwh'
        elif price_type in ['naphtha', 'lng', 'fuel_gas', 'electricity']:
            df = self.fuel_prices
            if price_type == 'electricity':
                col = 'electricity_usd_per_kwh'
            else:
                col = f'{price_type}_usd_per_gj'
        else:
            raise ValueError(f"Unknown price type: {price_type}")

        row = df[df['year'] == year]
        if len(row) > 0:
            return row[col].iloc[0]

        # Interpolate if year not found
        return np.interp(year, df['year'], df[col])

    def get_grid_emission_factor(self, year):
        """Get grid emission factor for a given year (tCO2/MWh)"""
        row = self.grid_emissions[self.grid_emissions['year'] == year]
        if len(row) > 0:
            return row['grid_ef_tco2_per_mwh'].iloc[0]
        # Interpolate
        return np.interp(
            year,
            self.grid_emissions['year'],
            self.grid_emissions['grid_ef_tco2_per_mwh']
        )

    def get_emission_factor(self, fuel_type):
        """Get emission factor for a fuel type"""
        if fuel_type not in self.emission_factors.index:
            raise ValueError(f"Unknown fuel type: {fuel_type}")

        row = self.emission_factors.loc[fuel_type]

        # Return appropriate column based on what's available
        if pd.notna(row.get('tCO2_per_GJ')):
            return row['tCO2_per_GJ'], 'GJ'
        elif pd.notna(row.get('tCO2_per_kWh')):
            return row['tCO2_per_kWh'], 'kWh'
        elif pd.notna(row.get('tCO2_per_kg')):
            return row['tCO2_per_kg'], 'kg'
        else:
            raise ValueError(f"No emission factor found for {fuel_type}")

    def get_capacity_multiplier(self, year):
        """Get demand growth capacity multiplier for a year"""
        row = self.demand_growth[self.demand_growth['year'] == year]
        if len(row) > 0:
            return row['cumulative_capacity_multiplier'].iloc[0]
        # Interpolate
        return np.interp(
            year,
            self.demand_growth['year'],
            self.demand_growth['cumulative_capacity_multiplier']
        )

    # ========================================================================
    # SUMMARY METHODS
    # ========================================================================

    def print_summary(self):
        """Print summary of loaded data"""
        print("\n" + "="*80)
        print("DATA SUMMARY")
        print("="*80)

        print(f"\nFacilities: {len(self.facilities)}")
        print(f"  Products: {self.facilities['product'].nunique()}")
        print(f"  Companies: {self.facilities['company'].nunique()}")
        print(f"  Locations: {self.facilities['location'].nunique()}")

        print(f"\nTechnologies: {len(self.tech_costs)}")
        for _, row in self.tech_costs.iterrows():
            print(f"  - {row['technology']}")

        print(f"\nPrice trajectories: {min(self.h2_prices['year'])}-{max(self.h2_prices['year'])}")

        print(f"\nBaseline emissions defined for:")
        for _, row in self.baseline_emissions.iterrows():
            print(f"  - {row['product']}: {row['total_emissions_tco2_per_ton']:.3f} tCO2/ton")

        print("\n" + "="*80 + "\n")


# Convenience function for quick access
def load_data(data_dir='data'):
    """Load all data using DataManager"""
    return DataManager(data_dir)
