"""
Data Loader Module
==================
Centralized data loading with validation.
All data comes from CSV files - no hardcoded values.
"""

import pandas as pd
import numpy as np
from pathlib import Path


class DataLoader:
    """Load all input data from CSV files with validation"""

    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self._model_config = None  # Cache for model config

    def load_model_config(self):
        """
        Load model configuration parameters.
        Returns dict with all model parameters.
        """
        if self._model_config is not None:
            return self._model_config

        config_path = self.data_dir / 'assumptions' / 'model_config.csv'
        if not config_path.exists():
            raise FileNotFoundError(f"Critical: Missing model config at {config_path}")

        df = pd.read_csv(config_path)

        # Convert to dict with type conversion
        config = {}
        for _, row in df.iterrows():
            param = row['parameter']
            value = row['value']
            unit = row.get('unit', '')

            # Convert numeric values
            if unit == 'decimal' or unit == 'year':
                config[param] = float(value)
            elif '/' in unit:  # Conversion factors like GJ/MWh
                config[param] = float(value)
            else:
                config[param] = value

        self._model_config = config
        return config

    def get_config_value(self, param_name):
        """Get a specific config value, loading config if needed"""
        config = self.load_model_config()
        if param_name not in config:
            raise ValueError(f"Parameter '{param_name}' not found in model_config.csv")
        return config[param_name]

    def load_facilities(self):
        """
        Load facility data by merging Facility List with Energy Intensity Benchmarks.
        Enforces 100% data coverage check.
        """
        # 1. Load Facility Metadata
        path_shaheen = self.data_dir / 'assets' / 'facility_database_with_shaheen.csv'
        path_regions = self.data_dir / 'assets' / 'facility_database_with_regions.csv'

        if path_shaheen.exists():
            df_facilities = pd.read_csv(path_shaheen)
        else:
            df_facilities = pd.read_csv(path_regions)

        # 2. Load Benchmarks
        benchmarks_path = self.data_dir / 'assumptions' / 'product_benchmarks.csv'
        if not benchmarks_path.exists():
            raise FileNotFoundError(f"Critical: Missing benchmarks at {benchmarks_path}")

        df_benchmarks = pd.read_csv(benchmarks_path)

        # 3. Merge Strategies
        cols_to_drop = [c for c in df_facilities.columns if 'GJ_per_tonne' in c or 'kWh_per_tonne' in c]
        if cols_to_drop:
            df_facilities = df_facilities.drop(columns=cols_to_drop)

        df_merged = pd.merge(
            df_facilities,
            df_benchmarks,
            on=['product', 'process'],
            how='left'
        )

        # 4. Integrity Check (100% match)
        if df_merged['Electricity_kWh_per_tonne'].isna().any():
            missing = df_merged[df_merged['Electricity_kWh_per_tonne'].isna()]
            unique_missing = missing[['product', 'process']].drop_duplicates()
            raise ValueError(
                f"Data Integrity Error: {len(missing)} facilities have no matching benchmark.\n"
                f"Missing profiles for:\n{unique_missing}"
            )

        return df_merged

    def load_emission_factors(self):
        """Load emission factors"""
        path = self.data_dir / 'assumptions' / 'emission_factors.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing emission factors at {path}")
        return pd.read_csv(path)

    def load_technology_params(self):
        """Load technology parameters (efficiency, COP, etc.)"""
        tech_path = self.data_dir / 'assumptions' / 'technology_parameters.csv'
        if not tech_path.exists():
            raise FileNotFoundError(f"Critical: Missing technology parameters at {tech_path}")
        return pd.read_csv(tech_path)

    def load_energy_intensities(self):
        """
        Load energy intensities (product benchmarks merged with facility context).
        Returns the same data as load_facilities() since intensities are merged there.
        This is an alias for backwards compatibility with run_scenarios.py.
        """
        return self.load_facilities()

    def load_technology_capex(self):
        """Load technology CAPEX data (new structure with $/t-product/yr)"""
        capex_path = self.data_dir / 'assumptions' / 'technology_capex.csv'
        if not capex_path.exists():
            raise FileNotFoundError(f"Critical: Missing technology CAPEX at {capex_path}")
        return pd.read_csv(capex_path)

    def load_h2_prices(self):
        """Load H2 price trajectory"""
        path = self.data_dir / 'assumptions' / 'prices' / 'h2_price_trajectory.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing H2 prices at {path}")
        return pd.read_csv(path)

    def load_re_prices(self):
        """Load RE price trajectory"""
        path = self.data_dir / 'assumptions' / 'prices' / 're_price_trajectory.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing RE prices at {path}")
        return pd.read_csv(path)

    def load_grid_emissions(self):
        """Load grid emission trajectory"""
        path = self.data_dir / 'assumptions' / 'prices' / 'grid_emission_trajectory.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing grid emissions at {path}")
        return pd.read_csv(path)

    def load_grid_prices(self):
        """Load grid electricity price trajectory"""
        path = self.data_dir / 'assumptions' / 'prices' / 'grid_price_trajectory.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing grid prices at {path}")
        return pd.read_csv(path)

    def load_fuel_prices(self):
        """Load fuel price trajectory"""
        path = self.data_dir / 'assumptions' / 'prices' / 'fuel_price_trajectory.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing fuel prices at {path}")
        return pd.read_csv(path)

    def load_heat_pump_applicability(self):
        """Load heat pump applicability"""
        path = self.data_dir / 'assumptions' / 'heat_pump_applicability.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing heat pump applicability at {path}")
        return pd.read_csv(path)

    def load_carbon_budgets(self):
        """Load carbon budget scenarios"""
        path = self.data_dir / 'assumptions' / 'carbon_budget_scenarios.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing carbon budgets at {path}")
        return pd.read_csv(path)

    def load_asset_valuation_params(self):
        """Load asset valuation parameters"""
        path = self.data_dir / 'assumptions' / 'asset_valuation_params.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing asset valuation params at {path}")
        return pd.read_csv(path)

    def load_scenario_definitions(self):
        """Load scenario definitions"""
        path = self.data_dir / 'scenarios' / 'scenario_definitions.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing scenario definitions at {path}")
        return pd.read_csv(path)

    def load_emission_targets(self):
        """Load emission targets"""
        path = self.data_dir / 'scenarios' / 'emission_targets.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing emission targets at {path}")
        return pd.read_csv(path)

    def load_region_mapping(self):
        """Load region mapping"""
        path = self.data_dir / 'assets' / 'region_mapping.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing region mapping at {path}")
        return pd.read_csv(path)

    def load_operating_rate_trajectory(self, scenario_type):
        """
        Load operating rate trajectory for a scenario type.

        Args:
            scenario_type: 'shaheen', 'restructure_25pct', or 'restructure_40pct'
        """
        path = self.data_dir / 'scenarios' / f'demand_growth_trajectory_{scenario_type}.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing operating rate trajectory at {path}")
        return pd.read_csv(path)


def validate_data_integrity(loader):
    """
    Validate that all required data files exist and have consistent structure.
    Returns True if all checks pass, raises ValueError otherwise.
    """
    errors = []

    # Check model config
    try:
        config = loader.load_model_config()
        required_params = ['discount_rate', 'gj_to_mwh', 'analysis_start_year', 'analysis_end_year']
        for param in required_params:
            if param not in config:
                errors.append(f"Missing required parameter '{param}' in model_config.csv")
    except FileNotFoundError as e:
        errors.append(str(e))

    # Check technology parameters
    try:
        tech_params = loader.load_technology_params()
        required_cols = ['technology', 'applies_to', 'energy_conversion_efficiency', 'trl', 'available_year']
        for col in required_cols:
            if col not in tech_params.columns:
                errors.append(f"Missing required column '{col}' in technology_parameters.csv")
    except FileNotFoundError as e:
        errors.append(str(e))

    # Check technology CAPEX
    try:
        tech_capex = loader.load_technology_capex()
        required_cols = ['technology', 'capex_unit', 'capex_2025', 'capex_2030', 'capex_2040', 'capex_2050']
        for col in required_cols:
            if col not in tech_capex.columns:
                errors.append(f"Missing required column '{col}' in technology_capex.csv")
    except FileNotFoundError as e:
        errors.append(str(e))

    # Check emission factors
    try:
        ef = loader.load_emission_factors()
        if 'fuel' not in ef.columns:
            errors.append("Missing 'fuel' column in emission_factors.csv")
    except FileNotFoundError as e:
        errors.append(str(e))

    if errors:
        raise ValueError("Data validation failed:\n" + "\n".join(errors))

    return True
