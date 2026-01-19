"""
Utility functions shared across all modules
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

try:
    import seaborn as sns
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    class _SeabornStub:
        def set_style(self, *_args, **_kwargs):
            """Fallback when seaborn is unavailable."""

    sns = _SeabornStub()

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10


class DataLoader:
    """Load all input data from CSV files"""

    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)

    def load_facilities(self):
        """Load facility database"""
        return pd.read_csv(self.data_dir / 'facility_database_with_regions.csv')

    def load_energy_intensities(self):
        """Load energy intensity data"""
        return pd.read_csv(self.data_dir / 'energy_intensities.csv')

    def load_emission_factors(self):
        """Load emission factors"""
        return pd.read_csv(self.data_dir / 'emission_factors.csv')

    def load_h2_prices(self):
        """Load H2 price trajectory"""
        return pd.read_csv(self.data_dir / 'h2_price_trajectory.csv')

    def load_re_prices(self):
        """Load RE price trajectory"""
        return pd.read_csv(self.data_dir / 're_price_trajectory.csv')

    def load_grid_emissions(self):
        """Load grid emission trajectory"""
        return pd.read_csv(self.data_dir / 'grid_emission_trajectory.csv')

    def load_grid_prices(self):
        """Load grid electricity price trajectory"""
        return pd.read_csv(self.data_dir / 'grid_price_trajectory.csv')

    def load_technology_params(self):
        """Load technology parameters"""
        # Check both data_dir and output_dir for backwards compatibility
        tech_path = self.data_dir / 'technology_parameters.csv'
        if not tech_path.exists():
            tech_path = Path('output') / 'technology_parameters.csv'
        return pd.read_csv(tech_path, index_col=None)

    def load_heat_pump_applicability(self):
        """Load heat pump applicability"""
        return pd.read_csv(self.data_dir / 'heat_pump_applicability.csv')

    def load_fuel_costs(self):
        """Load baseline fuel costs"""
        return pd.read_csv(self.data_dir / 'fuel_costs_baseline.csv')


class EmissionCalculator:
    """Calculate emissions from energy consumption"""

    def __init__(self, emission_factors_df):
        """
        Args:
            emission_factors_df: DataFrame with emission factors
        """
        self.ef = {}
        for _, row in emission_factors_df.iterrows():
            fuel = row['fuel']
            if 'tCO2_per_GJ' in row and pd.notna(row['tCO2_per_GJ']):
                self.ef[fuel] = ('GJ', row['tCO2_per_GJ'])
            elif 'tCO2_per_kWh' in row and pd.notna(row['tCO2_per_kWh']):
                self.ef[fuel] = ('kWh', row['tCO2_per_kWh'])
            elif 'tCO2_per_kg' in row and pd.notna(row['tCO2_per_kg']):
                self.ef[fuel] = ('kg', row['tCO2_per_kg'])

    def calculate_emissions(self, fuel, energy_consumption):
        """
        Calculate emissions from fuel consumption

        Args:
            fuel: Fuel name
            energy_consumption: Energy amount

        Returns:
            Emissions in tCO2
        """
        if fuel not in self.ef:
            return 0.0

        unit, ef = self.ef[fuel]
        return energy_consumption * ef

    def calculate_total_emissions(self, facility_row, intensities_row):
        """
        Calculate total emissions for a facility

        Args:
            facility_row: Row from facility database
            intensities_row: Row from energy intensities

        Returns:
            Dictionary with emissions by fuel type (in tCO2/year)
        """
        # CRITICAL: capacity is in kt (kilotonnes), intensities are per tonne
        # Must multiply by 1000 to convert kt to tonnes
        capacity_tonnes = facility_row['capacity_kt'] * 1000

        emissions = {}

        # Naphtha
        if intensities_row.get('Naphtha_GJ_per_tonne', 0) > 0:
            energy = intensities_row['Naphtha_GJ_per_tonne'] * capacity_tonnes
            emissions['naphtha'] = self.calculate_emissions('Naphtha', energy)

        # Electricity
        if intensities_row.get('Electricity_kWh_per_tonne', 0) > 0:
            energy = intensities_row['Electricity_kWh_per_tonne'] * capacity_tonnes
            emissions['electricity'] = self.calculate_emissions('Electricity', energy)

        # LNG
        if intensities_row.get('LNG_GJ_per_tonne', 0) > 0:
            energy = intensities_row['LNG_GJ_per_tonne'] * capacity_tonnes
            emissions['lng'] = self.calculate_emissions('LNG', energy)

        # Fuel Gas
        if intensities_row.get('Fuel_Gas_GJ_per_tonne', 0) > 0:
            energy = intensities_row['Fuel_Gas_GJ_per_tonne'] * capacity_tonnes
            emissions['fuel_gas'] = self.calculate_emissions('Fuel_Gas', energy)

        # Byproduct Gas
        if intensities_row.get('Byproduct_Gas_GJ_per_tonne', 0) > 0:
            energy = intensities_row['Byproduct_Gas_GJ_per_tonne'] * capacity_tonnes
            emissions['byproduct_gas'] = self.calculate_emissions('Byproduct_Gas', energy)

        # LPG
        if intensities_row.get('LPG_GJ_per_tonne', 0) > 0:
            energy = intensities_row['LPG_GJ_per_tonne'] * capacity_tonnes
            emissions['lpg'] = self.calculate_emissions('LPG', energy)

        # Fuel Oil
        if intensities_row.get('Fuel_Oil_GJ_per_tonne', 0) > 0:
            energy = intensities_row['Fuel_Oil_GJ_per_tonne'] * capacity_tonnes
            emissions['fuel_oil'] = self.calculate_emissions('Fuel_Oil', energy)

        # Diesel
        if intensities_row.get('Diesel_GJ_per_tonne', 0) > 0:
            energy = intensities_row['Diesel_GJ_per_tonne'] * capacity_tonnes
            emissions['diesel'] = self.calculate_emissions('Diesel', energy)

        emissions['total'] = sum(emissions.values())

        return emissions


class PriceCalculator:
    """Calculate fuel and technology costs"""

    def __init__(self, h2_prices_df, re_prices_df, fuel_prices_df=None):
        self.h2_prices = h2_prices_df
        self.re_prices = re_prices_df
        self.fuel_prices = fuel_prices_df  # Trajectory DataFrame with year + fuel columns

    def get_h2_price(self, year):
        """Get H2 price for a given year ($/kg)"""
        row = self.h2_prices[self.h2_prices['year'] == year]
        if len(row) > 0:
            return row['h2_price_usd_per_kg'].iloc[0]
        # Interpolate if year not found
        return np.interp(year, self.h2_prices['year'], self.h2_prices['h2_price_usd_per_kg'])

    def get_re_price(self, year):
        """Get RE price for a given year ($/MWh)"""
        row = self.re_prices[self.re_prices['year'] == year]
        if len(row) > 0:
            return row['re_price_usd_per_mwh'].iloc[0]
        # Interpolate if year not found
        return np.interp(year, self.re_prices['year'], self.re_prices['re_price_usd_per_mwh'])

    def get_fuel_prices(self, year):
        """Get all fuel prices for a given year ($/GJ or $/kWh)"""
        if self.fuel_prices is None:
            raise ValueError("Fuel price trajectory not loaded")

        row = self.fuel_prices[self.fuel_prices['year'] == year]
        if len(row) > 0:
            return row.iloc[0].to_dict()

        # Interpolate if year not found
        result = {}
        for col in self.fuel_prices.columns:
            if col != 'year':
                result[col] = np.interp(year, self.fuel_prices['year'], self.fuel_prices[col])
        result['year'] = year
        return result

    def calculate_capital_recovery_factor(self, discount_rate, lifetime):
        """Calculate CRF for annualizing capital costs"""
        if discount_rate == 0:
            return 1 / lifetime
        return discount_rate / (1 - (1 + discount_rate) ** (-lifetime))


class TechnologyCostCalculator:
    """Calculate technology costs with interpolation"""

    def __init__(self, technology_params_df):
        self.tech_params = technology_params_df

    def get_technology_costs(self, technology, year):
        """
        Get interpolated technology costs for a given year

        Returns:
            dict with capex_musd_per_mtco2, opex_pct_capex, lifetime_years, available
        """
        tech_row = self.tech_params[self.tech_params['technology'] == technology]

        if len(tech_row) == 0:
            raise ValueError(f"Technology {technology} not found")

        tech_row = tech_row.iloc[0]

        # Check availability
        available = year >= tech_row['available_year']

        # Interpolate capex
        years = [2025, 2030, 2040, 2050]
        capex_values = [
            tech_row['capex_2025_musd_per_mtco2'],
            tech_row['capex_2030_musd_per_mtco2'],
            tech_row['capex_2040_musd_per_mtco2'],
            tech_row['capex_2050_musd_per_mtco2']
        ]

        capex = np.interp(year, years, capex_values)

        return {
            'capex_musd_per_mtco2': capex,
            'opex_pct_capex': tech_row['opex_pct_capex'],
            'lifetime_years': tech_row['lifetime_years'],
            'available': available,
            'cop': tech_row.get('cop', None),
            'trl': tech_row.get('trl', None),
            'h2_ton_per_ton_ethylene': tech_row.get('h2_ton_per_ton_ethylene', None),
            'elec_mwh_per_ton_ethylene': tech_row.get('elec_mwh_per_ton_ethylene', None),
            'naphtha_combustion_gj_per_ton_ethylene': tech_row.get('naphtha_combustion_gj_per_ton_ethylene', None),
            'thermal_energy_replaced_gj_per_ton': tech_row.get('thermal_energy_replaced_gj_per_ton', None),
            'energy_conversion_efficiency': tech_row.get('energy_conversion_efficiency', 1.0),
        }


def save_csv_output(df, output_path, description=""):
    """Save DataFrame to CSV with logging"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"   ✓ Saved: {output_path.name} {description}")


def save_plot(fig, output_path, description=""):
    """Save matplotlib figure with logging"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"   ✓ Saved: {output_path.name} {description}")


def identify_product_group(product_name):
    """Identify product group from product name"""
    product_lower = str(product_name).lower()

    if any(x in product_lower for x in ['ethylene', 'propylene', 'butadiene', 'butene']):
        return 'Olefins'
    elif any(x in product_lower for x in ['benzene', 'toluene', 'xylene', 'styrene']):
        return 'Aromatics'
    elif any(x in product_lower for x in ['polyethylene', 'polypropylene', 'pe', 'pp', 'ps', 'pvc']):
        return 'Polymers'
    elif any(x in product_lower for x in ['acetic', 'phenol', 'acetone', 'alcohol', 'glycol']):
        return 'Intermediates'
    else:
        return 'Other'


def is_ncc_facility(product_name):
    """Check if facility is a Naphtha Cracking Complex

    IMPORTANT: Only Ethylene, Propylene, Butadiene are TRUE NCC products
    Benzene, Toluene, Xylene are produced in BTX Plants (aromatics extraction)
    NOT in Naphtha Crackers
    """
    ncc_keywords = ['ethylene', 'propylene', 'butadiene']
    product_lower = str(product_name).lower()
    return any(keyword in product_lower for keyword in ncc_keywords)


def format_number(value, decimals=2):
    """Format number for display"""
    if abs(value) >= 1e9:
        return f"${value/1e9:.{decimals}f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:.{decimals}f}M"
    elif abs(value) >= 1e3:
        return f"${value/1e3:.{decimals}f}K"
    else:
        return f"${value:.{decimals}f}"
