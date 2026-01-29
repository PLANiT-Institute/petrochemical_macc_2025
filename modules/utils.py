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



class DataLoader:
    """Load all input data from CSV files"""

    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)

    def load_facilities(self):
        """
        Load facility data by merging Facility List (Capacity/Region) with 
        Energy Intensity Benchmarks.
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
        # We merge on [product, process]. 
        # Note: If facility data has intensity columns, drop them first to avoid collision or stale data.
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
        # Check a key intensity column, e.g., 'Electricity_kWh_per_tonne'
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

    def load_energy_intensities(self):
        """
        Load energy intensities (returns facilities merged with benchmarks).
        This is an alias for load_facilities() for backwards compatibility.
        """
        return self.load_facilities()

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

    def load_technology_params(self):
        """Load technology parameters"""
        tech_path = self.data_dir / 'assumptions' / 'technology_parameters.csv'
        if not tech_path.exists():
            raise FileNotFoundError(f"Critical: Missing technology parameters at {tech_path}")
        return pd.read_csv(tech_path, index_col=None)

    def load_fuel_costs(self):
        """Load baseline fuel costs"""
        path = self.data_dir / 'assumptions' / 'prices' / 'fuel_costs_baseline.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing fuel costs at {path}")
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

    def load_electrolyser_params(self):
        """Load electrolyser learning curve parameters"""
        path = self.data_dir / 'assumptions' / 'prices' / 'electrolyser_params.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing electrolyser params at {path}")
        return pd.read_csv(path)

    def load_flat_elec_prices(self):
        """Load flat electricity price trajectory"""
        path = self.data_dir / 'assumptions' / 'prices' / 'elec_price_flat.csv'
        if not path.exists():
            raise FileNotFoundError(f"Critical: Missing flat elec prices at {path}")
        return pd.read_csv(path)


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
        # Validate required column
        if 'capacity_kt' not in facility_row:
            raise ValueError("facility_row missing required 'capacity_kt' column")

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

    def calculate_baseline_metrics(self, facility_row, intensities_row, operating_rate, capacity_multiplier=1.0, process=None):
        """
        Calculate full baseline metrics for a facility.
        Replaces calculate_facility_baseline in run_scenarios.py

        IMPORTANT: For NCC (Naphtha Cracker) facilities, naphtha is FEEDSTOCK (cracked into products),
        NOT combustion fuel. The 29 GJ/t naphtha represents feedstock energy content.
        Only LNG, LPG, and byproduct gas are actual heating fuels that produce emissions.
        """
        # Validate required column
        if 'capacity_kt' not in facility_row:
            raise ValueError("facility_row missing required 'capacity_kt' column")

        capacity_tonnes = facility_row['capacity_kt'] * 1000
        production_tonnes = capacity_tonnes * capacity_multiplier * operating_rate

        # Check if this is an NCC facility - naphtha is feedstock, not fuel
        is_ncc = process == 'Naphtha Cracker' if process else False

        emissions_by_source = {}
        total_heat_gj = 0.0

        # Helper to process a fuel
        def process_fuel(fuel_name, intensity_col, is_heat=True):
            nonlocal total_heat_gj
            intensity = intensities_row.get(intensity_col, 0)
            if intensity > 0:
                # Determine unit (GJ vs kWh)
                if 'kWh' in intensity_col:
                    energy = intensity * production_tonnes  # Returns kWh
                    # Note: MWh conversion happens outside this function
                    # Emission factor lookup handled in calculate_emissions
                    emissions = self.calculate_emissions(fuel_name, energy)
                    return energy, emissions  # energy is in kWh
                else:
                    # GJ
                    energy = intensity * production_tonnes
                    if is_heat:
                        total_heat_gj += energy
                    emissions = self.calculate_emissions(fuel_name, energy)
                    return energy, emissions
            return 0.0, 0.0

        # Calculate for all fuels
        energy_by_source = {}

        # NAPHTHA: For NCC facilities, naphtha is FEEDSTOCK (cracked into products),
        # NOT combustion fuel. The ~29 GJ/t represents feedstock energy content.
        # Only LNG, LPG, and byproduct gas are actual heating fuels.
        #
        # Logic: process_fuel adds naphtha to total_heat_gj initially (is_heat=True),
        # then we subtract it for NCC facilities. This ensures:
        # - NCC: naphtha NOT in heat_demand_gj (correct: it's feedstock)
        # - Non-NCC: naphtha IS in heat_demand_gj (if used as fuel)
        energy_by_source['naphtha'], naphtha_emissions = process_fuel('Naphtha', 'Naphtha_GJ_per_tonne', True)
        if is_ncc:
            # Naphtha is feedstock in NCC - no combustion emissions
            emissions_by_source['naphtha'] = 0.0
            # Exclude naphtha from heat demand (it's feedstock, not heating fuel)
            # This corrects the initial add from process_fuel
            total_heat_gj -= energy_by_source['naphtha']
        else:
            emissions_by_source['naphtha'] = naphtha_emissions

        energy_by_source['lng'], emissions_by_source['lng'] = process_fuel('LNG', 'LNG_GJ_per_tonne', True)
        energy_by_source['fuel_gas'], emissions_by_source['fuel_gas'] = process_fuel('Fuel_Gas', 'Fuel_Gas_GJ_per_tonne', True)
        energy_by_source['byproduct_gas'], emissions_by_source['byproduct_gas'] = process_fuel('Byproduct_Gas', 'Byproduct_Gas_GJ_per_tonne', True)
        energy_by_source['lpg'], emissions_by_source['lpg'] = process_fuel('LPG', 'LPG_GJ_per_tonne', True)
        energy_by_source['fuel_oil'], emissions_by_source['fuel_oil'] = process_fuel('Fuel_Oil', 'Fuel_Oil_GJ_per_tonne', True)
        energy_by_source['diesel'], emissions_by_source['diesel'] = process_fuel('Diesel', 'Diesel_GJ_per_tonne', True)

        # Electricity (special case, not heat)
        elec_kwh, emissions_by_source['electricity'] = process_fuel('Electricity', 'Electricity_kWh_per_tonne', False)
        energy_by_source['electricity'] = elec_kwh # stored as kWh
        elec_mwh = elec_kwh / 1000

        # Sum combustion emissions (all except electricity)
        # For NCC: naphtha emissions are 0, so only LNG/LPG/byproduct count
        combustion_emissions = sum(v for k, v in emissions_by_source.items() if k != 'electricity')

        # Total emissions (combustion + electricity)
        # Note: Electricity emissions here use the generic EF.
        # The simulation might override this with Grid EF trajectory.
        elec_emissions = emissions_by_source.get('electricity', 0.0)
        total_emissions = combustion_emissions + elec_emissions

        return {
            'capacity_tpy': capacity_tonnes,
            'production_t': production_tonnes,
            'emissions_by_source': emissions_by_source,
            'energy_by_source': energy_by_source,
            'combustion_emissions': combustion_emissions,
            'elec_emissions': elec_emissions,
            'total_emissions': total_emissions,
            'elec_demand_mwh': elec_mwh,
            'heat_demand_gj': total_heat_gj,
            'is_ncc': is_ncc,  # Flag for downstream use
        }


class PriceCalculator:
    """Calculate fuel and technology costs"""

    def __init__(self, h2_prices_df, re_prices_df, fuel_prices_df=None,
                 elec_prices_df=None, electrolyser_params_df=None,
                 price_scenario=None):
        self.h2_prices = h2_prices_df
        self.re_prices = re_prices_df
        self.fuel_prices = fuel_prices_df  # Trajectory DataFrame with year + fuel columns
        self.elec_prices = elec_prices_df  # Electricity price trajectory ($/MWh)
        self.electrolyser_params = electrolyser_params_df  # Electrolyser learning curve
        self.price_scenario = price_scenario  # 'coupled', 'decoupled', or None

    def get_elec_price(self, year):
        """Get electricity price for a given year ($/MWh) from elec_prices trajectory"""
        if self.elec_prices is None:
            raise ValueError("Electricity price trajectory not loaded")
        row = self.elec_prices[self.elec_prices['year'] == year]
        if len(row) > 0:
            return row['elec_price_usd_per_mwh'].iloc[0]
        return np.interp(year, self.elec_prices['year'], self.elec_prices['elec_price_usd_per_mwh'])

    def get_coupled_h2_price(self, year):
        """Calculate LCOH from electricity price + electrolyser params for a given year ($/kg)"""
        if self.electrolyser_params is None:
            raise ValueError("Electrolyser parameters not loaded")

        elec_price_mwh = self.get_elec_price(year)
        elec_price_kwh = elec_price_mwh / 1000.0

        # Get electrolyser params for this year
        params = self.electrolyser_params
        row = params[params['year'] == year]
        if len(row) > 0:
            r = row.iloc[0]
        else:
            # Interpolate all params
            r = {}
            for col in ['capex_usd_per_kw', 'opex_usd_per_kw_yr', 'efficiency_kwh_per_kg',
                         'lifespan_years', 'capacity_factor', 'discount_rate']:
                r[col] = np.interp(year, params['year'], params[col])

        capex = r['capex_usd_per_kw']
        opex = r['opex_usd_per_kw_yr']
        efficiency = r['efficiency_kwh_per_kg']  # kWh per kg H2
        lifespan = int(r['lifespan_years'])
        cf = r['capacity_factor']
        dr = r['discount_rate']

        # Annualize CAPEX using CRF (Capital Recovery Factor)
        if dr > 0 and lifespan > 0:
            crf = (dr * (1 + dr) ** lifespan) / ((1 + dr) ** lifespan - 1)
        else:
            crf = 1.0 / lifespan if lifespan > 0 else 1.0
        annualized_capex = capex * crf  # $/kW/yr

        # Annual H2 production per kW of electrolyser capacity
        # hours_per_year * capacity_factor gives effective hours
        # 1 kW * CF * 8760 h = kWh/yr electricity consumed
        # kWh/yr / efficiency (kWh/kg) = kg H2/yr
        annual_elec_kwh_per_kw = cf * 8760  # kWh/yr per kW
        annual_h2_kg_per_kw = annual_elec_kwh_per_kw / efficiency  # kg/yr per kW

        # Costs per kW per year
        elec_cost_per_kw_yr = annual_elec_kwh_per_kw * elec_price_kwh

        # LCOH ($/kg)
        total_cost_per_kw_yr = annualized_capex + opex + elec_cost_per_kw_yr
        lcoh = total_cost_per_kw_yr / annual_h2_kg_per_kw

        return lcoh

    def get_h2_price(self, year):
        """Get H2 price for a given year ($/kg).
        If price_scenario is 'coupled', derives H2 price from electricity via LCOH.
        Otherwise uses domestic H2 price trajectory."""
        if self.price_scenario == 'coupled':
            return self.get_coupled_h2_price(year)
        # Default: use domestic trajectory
        row = self.h2_prices[self.h2_prices['year'] == year]
        if len(row) > 0:
            return row['h2_price_usd_per_kg'].iloc[0]
        return np.interp(year, self.h2_prices['year'], self.h2_prices['h2_price_usd_per_kg'])

    def get_re_price(self, year):
        """Get RE price for a given year ($/MWh).
        If elec_prices is set, delegates to get_elec_price for consistency.
        Otherwise falls back to RE PPA trajectory."""
        if self.elec_prices is not None:
            return self.get_elec_price(year)
        row = self.re_prices[self.re_prices['year'] == year]
        if len(row) > 0:
            return row['re_price_usd_per_mwh'].iloc[0]
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



class TechnologyCostCalculator:
    """Calculate technology costs with interpolation"""

    def __init__(self, technology_params_df, emission_calculator=None, model_config=None):
        self.tech_params = technology_params_df
        self.emission_calculator = emission_calculator

        # Load GJ to MWh conversion factor from model_config (no hardcoded fallback)
        if model_config is not None and 'gj_to_mwh' in model_config:
            self.gj_to_mwh = model_config['gj_to_mwh']
        else:
            raise ValueError(
                "model_config missing required 'gj_to_mwh' parameter. "
                "Ensure model_config.csv is loaded and passed to TechnologyCostCalculator."
            )

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

    def calculate_abatement_requirements(self, technology, facility_baseline, process, ncc_tech_name):
        """
        Calculate energy requirements and abatement for a facility-technology pair.
        Replaces logic previously hardcoded in run_scenarios.py.

        Args:
            technology: Technology name (e.g. 'NCC-H2', 'Heat_Pump')
            facility_baseline: Dict with baseline emissions and heat demand
            process: Process type (e.g. 'Naphtha Cracker', 'BTX Plant')
            ncc_tech_name: The specific NCC technology choice for the scenario

        Returns:
            dict with h2_demand_t, added_elec_mwh, potential_abatement_tco2
        """
        # Energy conversion factor from model_config (loaded in __init__)
        GJ_TO_MWH = self.gj_to_mwh
        
        # Default return values
        h2_demand_t = 0.0
        added_elec_mwh = 0.0
        potential_abatement = facility_baseline['combustion_emissions']
        
        emissions = facility_baseline['emissions_by_source']
        naphtha_emissions = emissions.get('naphtha', 0)
        
        # Get Naphtha EF dynamically if available
        if self.emission_calculator and 'Naphtha' in self.emission_calculator.ef:
            # self.ef['Naphtha'] is ('GJ', value)
            naphtha_ef = self.emission_calculator.ef['Naphtha'][1]
        else:
            raise ValueError("Missing Naphtha emission factor in loaded data")

        # Get Heat Pump COP from CSV
        hp_row = self.tech_params[self.tech_params['technology'] == 'Heat_Pump']
        if len(hp_row) > 0:
            val = hp_row.iloc[0].get('cop')
            if pd.notna(val):
                hp_cop = val
            else:
                raise ValueError("Heat Pump COP value is NaN in technology parameters")
        else:
            raise ValueError("Heat_Pump technology missing from technology parameters")

        # Get RDH efficiency from CSV - NO FALLBACK
        rdh_row = self.tech_params[self.tech_params['technology'] == 'RDH']
        if len(rdh_row) > 0:
            rdh_eff = rdh_row.iloc[0].get('energy_conversion_efficiency')
            if pd.isna(rdh_eff):
                raise ValueError("RDH energy_conversion_efficiency is missing in technology_parameters.csv")
        else:
            raise ValueError("RDH technology missing from technology_parameters.csv")

        # Get NCC-H2 conversion factor from CSV - NO FALLBACK
        ncc_h2_row = self.tech_params[self.tech_params['technology'] == 'NCC-H2']
        if len(ncc_h2_row) > 0:
            h2_factor = ncc_h2_row.iloc[0].get('h2_ton_per_ton_ethylene')
            if pd.isna(h2_factor):
                raise ValueError("NCC-H2 h2_ton_per_ton_ethylene is missing in technology_parameters.csv")
        else:
            raise ValueError("NCC-H2 technology missing from technology_parameters.csv")

        # Get NCC-Electricity conversion factor from CSV - NO FALLBACK
        ncc_elec_row = self.tech_params[self.tech_params['technology'] == 'NCC-Electricity']
        if len(ncc_elec_row) > 0:
            elec_factor = ncc_elec_row.iloc[0].get('elec_mwh_per_ton_ethylene')
            if pd.isna(elec_factor):
                raise ValueError("NCC-Electricity elec_mwh_per_ton_ethylene is missing in technology_parameters.csv")
        else:
            raise ValueError("NCC-Electricity technology missing from technology_parameters.csv")

        # Get production volume for capacity-based calculations
        production_t = facility_baseline.get('production_t', 0)

        # Logic moved from run_scenarios.py
        if self._is_ncc_facility(process):
            # If the tech passed is the one designated for NCC, apply it
            if technology == ncc_tech_name:
                if technology == 'NCC-H2':
                    # H2 demand based on ethylene production (not emissions)
                    # h2_factor is t-H2/t-ethylene from CSV
                    h2_demand_t = production_t * h2_factor
                elif technology == 'NCC-Electricity':
                    # Elec demand based on ethylene production (not emissions)
                    # elec_factor is MWh/t-ethylene from CSV
                    added_elec_mwh = production_t * elec_factor

            # Heat pump always fills the gap for non-naphtha fuels in NCC
            # Calculate remaining heat load (non-naphtha)
            heat_gj_remaining = facility_baseline['heat_demand_gj'] - (naphtha_emissions / naphtha_ef)
            heat_gj_remaining = max(0, heat_gj_remaining)

            # Use dynamic Heat Pump COP from CSV
            hp_elec_mwh = heat_gj_remaining / GJ_TO_MWH / hp_cop
            added_elec_mwh += hp_elec_mwh

        elif self._is_btx_facility(process) and technology == 'RDH':
            # RDH efficiency from CSV
            rdh_elec_mwh = facility_baseline['heat_demand_gj'] / GJ_TO_MWH / rdh_eff
            added_elec_mwh = rdh_elec_mwh

        elif technology == 'Heat_Pump':
            # Standard Heat Pump for others (Dynamic COP from CSV)
            hp_elec_mwh = facility_baseline['heat_demand_gj'] / GJ_TO_MWH / hp_cop
            added_elec_mwh = hp_elec_mwh
            
        return {
            'h2_demand_t': h2_demand_t,
            'added_elec_mwh': added_elec_mwh,
            'potential_abatement_tco2': potential_abatement
        }

    def _is_ncc_facility(self, process):
        return process == 'Naphtha Cracker'

    def _is_btx_facility(self, process):
        return process == 'BTX Plant'


class StrandedAssetCalculator:
    """Calculate stranded asset value based on carbon budgets"""
    
    def __init__(self, carbon_budget_df, valuation_params_df):
        self.budgets = carbon_budget_df
        self.valuation = valuation_params_df.set_index('process')
        
    def calculate_stranding_year(self, annual_emissions_series, budget_scenario='budget_1.5C_tco2'):
        """
        Find the year when cumulative emissions exceed the budget.
        
        Args:
            annual_emissions_series: PD Series of total industry emissions by year
            budget_scenario: Column name in carbon_budget_df to use as limit
            
        Returns:
            int: The 'stranding year' (last year of operation), or 2050 if never exceeded.
        """
        # Calculate cumulative emissions starting from 2025
        cumulative_emissions = annual_emissions_series.cumsum()
        
        # Get budget limit (assumed sufficient for comparison, checking annual decline)
        # Actually, the dummy file provided shows ANNUAL limits declining to 0. 
        # But standard carbon budget is a CUMULATIVE number.
        # Let's check the dummy file structure again.
        # The dummy file has 'budget_1.5C_tco2' as 50Mt, 45Mt... down to 0.
        # This implies an ANNUAL CAP, not a cumulative budget pot.
        # If it were cumulative, it would be a single number like 500Mt.
        # So we will interpret the input as an ANNUAL LIMIT curve.
        
        # Check year by year: Is Industry Emission > Annual Limit?
        # A 'Stranding Year' in this context is usually when the budget runs out.
        # But if we have an annual cap, stranding happens incrementally?
        # The user request said "Stranded from Carbon Budget Perspective".
        # Research note said: Year where Cumulative > Budget.
        # But the dummy file looks like an annual trajectory.
        # Let's sum the dummy file to get the 'Total Budget Pot'.
        
        total_budget = self.budgets[budget_scenario].sum()
        
        # Find year where cumulative emissions exceed total budget
        overrun = cumulative_emissions[cumulative_emissions > total_budget]
        
        if len(overrun) > 0:
            return overrun.index[0]
        return 2050

    def calculate_facility_book_value(self, facility_row, current_year):
        """
        Calculate remaining book value of a facility in a given year.
        Value = Replacement_Cost * Capacity * (Remaining_Life / Useful_Life)
        """
        process = facility_row.get('process', 'Other')
        capacity_t = facility_row['capacity_kt'] * 1000
        year_built = facility_row['year_built']
        
        # Get valuation params
        if process in self.valuation.index:
            params = self.valuation.loc[process]
        else:
            params = self.valuation.loc['Other']
            
        capex_per_ton = params['overnight_capex_usd_per_ton']
        useful_life = params['useful_life_years']
        
        age = current_year - year_built
        remaining_life = useful_life - age
        
        if remaining_life <= 0:
            return 0.0
            
        # Linear depreciation
        replacement_value = capex_per_ton * capacity_t
        book_value = replacement_value * (remaining_life / useful_life)
        
        return book_value

    def calculate_total_stranded_value(self, facilities_df, stranding_year):
        """
        Calculate sum of book values for all facilities at the stranding year.
        """
        total_value = 0.0
        
        for _, facility in facilities_df.iterrows():
            val = self.calculate_facility_book_value(facility, stranding_year)
            total_value += val
            
        return total_value

    def get_facility_stranded_details(self, facilities_df, stranding_year):
        """
        Calculate stranded value for each facility and return as DataFrame.
        """
        results = []
        for _, facility in facilities_df.iterrows():
            val = self.calculate_facility_book_value(facility, stranding_year)
            
            # Basic facility info
            res = {
                'facility_id': facility.get('facility_id', 'Unknown'),
                'company': facility.get('company', 'Unknown'),
                'location': facility.get('location', 'Unknown'),
                'product': facility.get('product', 'Unknown'),
                'process': facility.get('process', 'Unknown'),
                'capacity_kt': facility.get('capacity_kt', 0),
                'year_built': facility.get('year_built', 0),
                'stranding_year': stranding_year,
                'stranded_value_usd': val
            }
            results.append(res)
            
        return pd.DataFrame(results)


def save_figure_data(df, figure_path, figure_type=None):
    """Save tidy/long-format CSV data alongside a figure PNG.

    Args:
        df: pandas DataFrame in tidy format (one observation per row).
            Expected columns include at least ``category``, ``value``, ``unit``.
        figure_path: Path (or str) to the corresponding PNG figure.
            The CSV will be written to the same directory with the same stem.
        figure_type: Optional string tag added as a ``figure_type`` column.
    """
    figure_path = Path(figure_path)
    csv_path = figure_path.with_suffix('.csv')
    if figure_type is not None:
        df = df.copy()
        df['figure_type'] = figure_type
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"   ✓ CSV: {csv_path.name}")


def save_csv_output(df, output_path, description=""):
    """Save DataFrame to CSV with logging"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"   ✓ Saved: {output_path.name} {description}")


def save_plot(fig, output_path, description=""):
    """Save matplotlib figure with logging (PNG + PDF)"""
    from .figure_style import save_figure
    save_figure(fig, output_path, dpi=300, close=True)
    print(f"   \u2713 Saved: {Path(output_path).name} {description}")


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
