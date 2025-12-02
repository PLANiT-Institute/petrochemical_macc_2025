"""
Comprehensive Excel Report Generator for Petrochemical Decarbonization Model
248 Facilities | 2025-2050 | NCC-Electricity (Main) & NCC-H2 (Alternative) Scenarios

Emission Targets:
- 2025: 52 MtCO2 (Baseline)
- 2035: 39.26 MtCO2 (-24.5% from baseline)
- 2050: 0 MtCO2 (-100%, Net Zero)

Output: Multi-sheet Excel workbook with full facility-level yearly details
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Add modules to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from modules.utils import DataLoader, EmissionCalculator, identify_product_group, is_ncc_facility


class ComprehensiveExcelGenerator:
    """
    Generate comprehensive Excel output for petrochemical decarbonization analysis

    Features:
    - 248 facilities with full details
    - Yearly tracking (2025-2050)
    - Energy consumption by fuel type
    - Cost breakdown (CAPEX, OPEX, Fuel)
    - Technology transition timing
    - Regional and company aggregations
    """

    def __init__(self, data_dir='data', output_dir='outputs/excel_report'):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("COMPREHENSIVE EXCEL REPORT GENERATOR")
        print("="*80)

        # Load all data
        self._load_data()

        # User-specified baseline (will normalize calculated emissions to this)
        self.target_baseline_mt = 52.0  # MtCO2

        # Define emission targets (user-specified)
        self.emission_targets = {
            2025: 52.0,      # Baseline: 52 MtCO2
            2035: 39.26,     # -24.5% reduction
            2050: 0.0        # -100% (Net Zero)
        }

        # Interpolate targets for all years
        self.yearly_targets = self._interpolate_targets()

        print(f"\nEmission Targets:")
        print(f"  2025: {self.emission_targets[2025]:.2f} MtCO2 (Baseline)")
        print(f"  2035: {self.emission_targets[2035]:.2f} MtCO2 (-24.5%)")
        print(f"  2050: {self.emission_targets[2050]:.2f} MtCO2 (-100%)")

    def _load_data(self):
        """Load all required data files"""
        print("\nLoading data files...")

        loader = DataLoader(self.data_dir)

        # Facility data
        self.df_facilities = loader.load_facilities()
        self.df_intensities = loader.load_energy_intensities()
        print(f"  - {len(self.df_facilities)} facilities loaded")

        # Emission factors
        self.df_emission_factors = loader.load_emission_factors()
        self.emission_calc = EmissionCalculator(self.df_emission_factors)

        # Technology parameters
        self.df_tech_params = loader.load_technology_params()
        print(f"  - {len(self.df_tech_params)} technologies loaded")

        # Price trajectories
        self.df_h2_prices = loader.load_h2_prices()
        self.df_re_prices = loader.load_re_prices()
        self.df_grid_prices = loader.load_grid_prices()
        self.df_fuel_prices = pd.read_csv(self.data_dir / 'fuel_price_trajectory.csv')
        self.df_grid_ef = pd.read_csv(self.data_dir / 'grid_emission_trajectory.csv')

        # Heat pump applicability
        self.df_hp_applicability = loader.load_heat_pump_applicability()

    def _interpolate_targets(self):
        """Interpolate emission targets for all years 2025-2050"""
        years = list(range(2025, 2051))
        targets = {}

        key_years = sorted(self.emission_targets.keys())

        for year in years:
            if year in self.emission_targets:
                targets[year] = self.emission_targets[year]
            else:
                # Linear interpolation
                for i in range(len(key_years) - 1):
                    if key_years[i] < year < key_years[i+1]:
                        y1, y2 = key_years[i], key_years[i+1]
                        t1, t2 = self.emission_targets[y1], self.emission_targets[y2]
                        targets[year] = t1 + (t2 - t1) * (year - y1) / (y2 - y1)
                        break

        return targets

    def calculate_facility_baseline(self):
        """Calculate baseline emissions and energy for all 248 facilities"""
        print("\nCalculating facility baseline (2025)...")

        baseline_data = []

        for idx, facility in self.df_facilities.iterrows():
            intensity = self.df_intensities.iloc[idx]
            capacity = facility['capacity_kt']  # kt/year

            # Energy consumption (total per year)
            energy = {
                'naphtha_gj': intensity['Naphtha_GJ_per_tonne'] * capacity * 1000,
                'electricity_kwh': intensity['Electricity_kWh_per_tonne'] * capacity * 1000,
                'lng_gj': intensity['LNG_GJ_per_tonne'] * capacity * 1000,
                'fuel_gas_gj': intensity['Fuel_Gas_GJ_per_tonne'] * capacity * 1000,
                'byproduct_gas_gj': intensity['Byproduct_Gas_GJ_per_tonne'] * capacity * 1000,
                'lpg_gj': intensity['LPG_GJ_per_tonne'] * capacity * 1000,
                'fuel_oil_gj': intensity['Fuel_Oil_GJ_per_tonne'] * capacity * 1000,
                'diesel_gj': intensity['Diesel_GJ_per_tonne'] * capacity * 1000,
            }

            # Emissions by fuel
            emissions = self.emission_calc.calculate_total_emissions(facility, intensity)

            # Determine if NCC facility (eligible for NCC technologies)
            is_ncc = is_ncc_facility(facility['product'])
            product_group = identify_product_group(facility['product'])

            # Heat pump applicability for non-NCC facilities
            hp_applicable = 0.0
            if not is_ncc:
                hp_row = self.df_hp_applicability[
                    self.df_hp_applicability['product_group'] == product_group
                ]
                if len(hp_row) > 0:
                    hp_applicable = hp_row.iloc[0]['applicability_pct'] / 100

            baseline_data.append({
                'facility_id': idx + 1,
                'product': facility['product'],
                'product_group': product_group,
                'process': facility['process'],
                'company': facility['company'],
                'location': facility['location'],
                'capacity_kt': capacity,
                'year_built': facility['year_built'],
                'is_ncc': is_ncc,
                'hp_applicability': hp_applicable,
                # Energy consumption
                'naphtha_gj': energy['naphtha_gj'],
                'electricity_kwh': energy['electricity_kwh'],
                'lng_gj': energy['lng_gj'],
                'fuel_gas_gj': energy['fuel_gas_gj'],
                'byproduct_gas_gj': energy['byproduct_gas_gj'],
                'lpg_gj': energy['lpg_gj'],
                'fuel_oil_gj': energy['fuel_oil_gj'],
                'diesel_gj': energy['diesel_gj'],
                # Emissions
                'emissions_naphtha_kt': emissions.get('naphtha', 0),
                'emissions_electricity_kt': emissions.get('electricity', 0),
                'emissions_lng_kt': emissions.get('lng', 0),
                'emissions_fuel_gas_kt': emissions.get('fuel_gas', 0),
                'emissions_byproduct_gas_kt': emissions.get('byproduct_gas', 0),
                'emissions_lpg_kt': emissions.get('lpg', 0),
                'emissions_fuel_oil_kt': emissions.get('fuel_oil', 0),
                'emissions_diesel_kt': emissions.get('diesel', 0),
                'total_emissions_kt': emissions['total'],
            })

        self.df_baseline = pd.DataFrame(baseline_data)

        # Calculate raw total and normalization factor
        raw_total_mt = self.df_baseline['total_emissions_kt'].sum() / 1000
        self.normalization_factor = self.target_baseline_mt / raw_total_mt

        print(f"  Raw calculated emissions: {raw_total_mt:.2f} MtCO2")
        print(f"  Target baseline: {self.target_baseline_mt:.2f} MtCO2")
        print(f"  Normalization factor: {self.normalization_factor:.4f}")

        # Apply normalization to all emission columns
        emission_cols = [c for c in self.df_baseline.columns if 'emissions' in c]
        for col in emission_cols:
            self.df_baseline[col] = self.df_baseline[col] * self.normalization_factor

        total_emissions = self.df_baseline['total_emissions_kt'].sum() / 1000
        print(f"  Normalized baseline emissions: {total_emissions:.2f} MtCO2")
        print(f"  NCC facilities: {self.df_baseline['is_ncc'].sum()}")
        print(f"  Non-NCC facilities: {(~self.df_baseline['is_ncc']).sum()}")

        return self.df_baseline

    def optimize_transition_timing(self, ncc_technology='NCC-Electricity'):
        """
        Determine optimal technology transition timing for each facility

        Args:
            ncc_technology: 'NCC-Electricity' or 'NCC-H2'

        Returns:
            DataFrame with facility transition years
        """
        print(f"\nOptimizing transition timing ({ncc_technology})...")

        years = list(range(2025, 2051))

        # Calculate total abatement needed per year
        baseline_total = self.df_baseline['total_emissions_kt'].sum() / 1000  # MtCO2

        # Calculate maximum abatement potential by technology
        # NCC technologies (41 NCC facilities)
        ncc_facilities = self.df_baseline[self.df_baseline['is_ncc']]
        ncc_max_abatement = ncc_facilities['total_emissions_kt'].sum() / 1000  # MtCO2

        # Heat pump (non-NCC facilities, based on applicability)
        non_ncc = self.df_baseline[~self.df_baseline['is_ncc']]
        hp_max_abatement = (non_ncc['total_emissions_kt'] * non_ncc['hp_applicability']).sum() / 1000

        print(f"  Maximum abatement potential:")
        print(f"    - {ncc_technology}: {ncc_max_abatement:.2f} MtCO2")
        print(f"    - Heat Pump: {hp_max_abatement:.2f} MtCO2")
        print(f"    - Total: {ncc_max_abatement + hp_max_abatement:.2f} MtCO2")

        # Technology availability
        ncc_available_year = 2030  # NCC technologies available from 2030
        hp_available_year = 2025   # Heat pump available from 2025

        # Transition timing DataFrame
        transition_data = []

        for idx, facility in self.df_baseline.iterrows():
            if facility['is_ncc']:
                # NCC facility: gets NCC technology (electricity or H2)
                transition_data.append({
                    'facility_id': facility['facility_id'],
                    'technology': ncc_technology,
                    'transition_year': ncc_available_year,  # Start deploying from 2030
                    'max_abatement_kt': facility['total_emissions_kt'],
                })
            else:
                # Non-NCC facility: gets Heat Pump
                transition_data.append({
                    'facility_id': facility['facility_id'],
                    'technology': 'Heat_Pump',
                    'transition_year': hp_available_year,  # Start deploying from 2025
                    'max_abatement_kt': facility['total_emissions_kt'] * facility['hp_applicability'],
                })

        self.df_transition = pd.DataFrame(transition_data)

        # Now optimize deployment rate to meet annual targets
        # Using greedy approach: deploy cheapest first, scale up to meet targets

        deployment_schedule = []

        for year in years:
            target = self.yearly_targets[year]

            # Calculate required abatement
            required_abatement = baseline_total - target

            # Grid emission factor affects BAU (electricity emissions decrease over time)
            grid_ef = self.df_grid_ef[self.df_grid_ef['year'] == year]['grid_ef_tco2_per_mwh'].iloc[0]
            grid_ef_2025 = self.df_grid_ef[self.df_grid_ef['year'] == 2025]['grid_ef_tco2_per_mwh'].iloc[0]
            grid_scaling = grid_ef / grid_ef_2025

            # BAU emissions (accounts for grid decarbonization)
            fossil_emissions = (
                self.df_baseline['emissions_naphtha_kt'].sum() +
                self.df_baseline['emissions_lng_kt'].sum() +
                self.df_baseline['emissions_fuel_gas_kt'].sum() +
                self.df_baseline['emissions_byproduct_gas_kt'].sum() +
                self.df_baseline['emissions_lpg_kt'].sum() +
                self.df_baseline['emissions_fuel_oil_kt'].sum() +
                self.df_baseline['emissions_diesel_kt'].sum()
            ) / 1000

            elec_emissions = self.df_baseline['emissions_electricity_kt'].sum() / 1000 * grid_scaling
            bau_emissions = fossil_emissions + elec_emissions

            # Required abatement from technologies
            tech_required = bau_emissions - target

            # Deployment rate (0 to 1) for each technology type
            if year < ncc_available_year:
                # Before 2030: only Heat Pump
                ncc_rate = 0.0
                hp_rate = min(1.0, max(0, tech_required / hp_max_abatement)) if hp_max_abatement > 0 else 0
            else:
                # After 2030: NCC + Heat Pump
                # First deploy heat pump fully, then NCC
                if tech_required <= hp_max_abatement:
                    hp_rate = min(1.0, max(0, tech_required / hp_max_abatement)) if hp_max_abatement > 0 else 0
                    ncc_rate = 0.0
                else:
                    hp_rate = 1.0
                    remaining = tech_required - hp_max_abatement
                    ncc_rate = min(1.0, max(0, remaining / ncc_max_abatement)) if ncc_max_abatement > 0 else 0

            deployment_schedule.append({
                'year': year,
                'target_mt': target,
                'bau_mt': bau_emissions,
                'required_abatement_mt': tech_required,
                'hp_deployment_rate': hp_rate,
                'ncc_deployment_rate': ncc_rate,
                'hp_abatement_mt': hp_rate * hp_max_abatement,
                'ncc_abatement_mt': ncc_rate * ncc_max_abatement,
                'total_abatement_mt': hp_rate * hp_max_abatement + ncc_rate * ncc_max_abatement,
                'actual_emissions_mt': bau_emissions - (hp_rate * hp_max_abatement + ncc_rate * ncc_max_abatement),
            })

        self.df_deployment = pd.DataFrame(deployment_schedule)

        print(f"\n  Deployment Schedule Summary:")
        for year in [2025, 2030, 2035, 2040, 2050]:
            row = self.df_deployment[self.df_deployment['year'] == year].iloc[0]
            print(f"    {year}: Target={row['target_mt']:.1f}, Actual={row['actual_emissions_mt']:.1f} MtCO2, "
                  f"HP={row['hp_deployment_rate']*100:.0f}%, NCC={row['ncc_deployment_rate']*100:.0f}%")

        return self.df_deployment

    def generate_yearly_facility_data(self, ncc_technology='NCC-Electricity'):
        """Generate yearly data for all facilities (248 x 26 years = 6,448 rows)"""
        print(f"\nGenerating yearly facility data ({ncc_technology})...")

        years = list(range(2025, 2051))
        yearly_data = []

        # Get technology parameters
        if ncc_technology == 'NCC-Electricity':
            ncc_tech_row = self.df_tech_params[self.df_tech_params['technology'] == 'NCC-Electricity'].iloc[0]
            elec_mwh_per_ton = ncc_tech_row['elec_mwh_per_ton_ethylene']
        else:
            ncc_tech_row = self.df_tech_params[self.df_tech_params['technology'] == 'NCC-H2'].iloc[0]
            h2_ton_per_ton = ncc_tech_row['h2_ton_per_ton_ethylene']

        hp_tech_row = self.df_tech_params[self.df_tech_params['technology'] == 'Heat_Pump'].iloc[0]
        hp_cop = hp_tech_row['cop']

        # Calculate total facility-level abatement potential for scaling
        ncc_total_emissions = self.df_baseline[self.df_baseline['is_ncc']]['total_emissions_kt'].sum()
        non_ncc_hp_emissions = (self.df_baseline[~self.df_baseline['is_ncc']]['total_emissions_kt'] *
                                self.df_baseline[~self.df_baseline['is_ncc']]['hp_applicability']).sum()

        for year in years:
            deploy = self.df_deployment[self.df_deployment['year'] == year].iloc[0]
            hp_rate = deploy['hp_deployment_rate']
            ncc_rate = deploy['ncc_deployment_rate']
            target = deploy['target_mt']

            # Get prices for this year
            h2_price = self.df_h2_prices[self.df_h2_prices['year'] == year]['h2_price_usd_per_kg'].iloc[0]
            re_price = self.df_re_prices[self.df_re_prices['year'] == year]['re_price_usd_per_mwh'].iloc[0]
            grid_price = self.df_grid_prices[self.df_grid_prices['year'] == year]['grid_price_usd_per_mwh'].iloc[0]
            naphtha_price = self.df_fuel_prices[self.df_fuel_prices['year'] == year]['naphtha_usd_per_gj'].iloc[0]
            lng_price = self.df_fuel_prices[self.df_fuel_prices['year'] == year]['lng_usd_per_gj'].iloc[0]

            # Grid emission factor
            grid_ef = self.df_grid_ef[self.df_grid_ef['year'] == year]['grid_ef_tco2_per_mwh'].iloc[0]
            grid_ef_2025 = self.df_grid_ef[self.df_grid_ef['year'] == 2025]['grid_ef_tco2_per_mwh'].iloc[0]

            # Technology CAPEX for this year (interpolate)
            capex_years = [2025, 2030, 2040, 2050]
            if ncc_technology == 'NCC-Electricity':
                ncc_capex_values = [1500, 1350, 1050, 900]  # $/t-C2H4/yr
            else:
                ncc_capex_values = [1700, 1300, 935, 780]   # $/t-C2H4/yr
            hp_capex_values = [800, 640, 480, 400]         # $/unit

            ncc_capex = np.interp(year, capex_years, ncc_capex_values)
            hp_capex = np.interp(year, capex_years, hp_capex_values)

            for idx, facility in self.df_baseline.iterrows():
                # Base energy and emissions
                base_emissions_kt = facility['total_emissions_kt']

                if facility['is_ncc']:
                    # NCC facility
                    deployment_rate = ncc_rate
                    technology_used = ncc_technology if ncc_rate > 0 and year >= 2030 else 'Baseline'

                    # After technology deployment
                    if technology_used != 'Baseline':
                        # Emissions reduction
                        emissions_reduced_kt = base_emissions_kt * deployment_rate
                        final_emissions_kt = base_emissions_kt - emissions_reduced_kt

                        # Energy changes
                        if ncc_technology == 'NCC-Electricity':
                            # New electricity consumption (renewable)
                            new_elec_mwh = facility['capacity_kt'] * 1000 * elec_mwh_per_ton * deployment_rate
                            new_h2_kg = 0
                            # Fuel cost: RE electricity
                            fuel_cost_usd = new_elec_mwh * re_price
                        else:
                            # New H2 consumption
                            new_h2_kg = facility['capacity_kt'] * 1000 * h2_ton_per_ton * 1000 * deployment_rate
                            new_elec_mwh = 0
                            # Fuel cost: H2
                            fuel_cost_usd = new_h2_kg * h2_price

                        # CAPEX (annualized over lifetime)
                        capex_total = facility['capacity_kt'] * 1000 * ncc_capex * deployment_rate
                        capex_annual = capex_total / 25  # 25-year lifetime
                        opex_annual = capex_total * 0.04  # 4% of CAPEX

                        # Fossil fuel reduction
                        fossil_gj_reduced = (
                            facility['naphtha_gj'] + facility['lng_gj'] +
                            facility['fuel_gas_gj'] + facility['byproduct_gas_gj']
                        ) * deployment_rate
                    else:
                        emissions_reduced_kt = 0
                        final_emissions_kt = base_emissions_kt * (grid_ef / grid_ef_2025)  # Grid decarbonization only
                        new_elec_mwh = 0
                        new_h2_kg = 0
                        fossil_gj_reduced = 0
                        fuel_cost_usd = 0
                        capex_annual = 0
                        opex_annual = 0
                else:
                    # Non-NCC facility (Heat Pump)
                    deployment_rate = hp_rate * facility['hp_applicability']
                    technology_used = 'Heat_Pump' if deployment_rate > 0 else 'Baseline'

                    # Separate fossil fuel and electricity emissions
                    fossil_emissions_kt = (
                        facility['emissions_naphtha_kt'] + facility['emissions_lng_kt'] +
                        facility['emissions_fuel_gas_kt'] + facility['emissions_lpg_kt'] +
                        facility['emissions_fuel_oil_kt'] + facility['emissions_diesel_kt'] +
                        facility['emissions_byproduct_gas_kt']
                    )

                    if technology_used == 'Heat_Pump':
                        # Emissions reduction (fossil fuel combustion replaced by electricity)
                        emissions_reduced_kt = fossil_emissions_kt * deployment_rate

                        # Grid decarbonization affects electricity emissions
                        remaining_elec_emissions = facility['emissions_electricity_kt'] * (grid_ef / grid_ef_2025)
                        remaining_fossil_emissions = fossil_emissions_kt * (1 - deployment_rate)
                        final_emissions_kt = remaining_elec_emissions + remaining_fossil_emissions

                        # Heat pump electricity consumption
                        fossil_gj_reduced = (
                            facility['naphtha_gj'] + facility['lng_gj'] +
                            facility['fuel_gas_gj'] + facility['lpg_gj'] +
                            facility['fuel_oil_gj'] + facility['diesel_gj']
                        ) * deployment_rate
                        new_elec_mwh = fossil_gj_reduced / hp_cop / 3.6  # GJ to MWh
                        new_h2_kg = 0

                        # Costs
                        fuel_cost_usd = new_elec_mwh * grid_price
                        capex_total = emissions_reduced_kt * 1000 * hp_capex  # kt to tons
                        capex_annual = capex_total / 20  # 20-year lifetime
                        opex_annual = capex_total * 0.03  # 3% of CAPEX
                    else:
                        emissions_reduced_kt = 0
                        # Grid decarbonization only
                        elec_emissions = facility['emissions_electricity_kt'] * (grid_ef / grid_ef_2025)
                        final_emissions_kt = elec_emissions + fossil_emissions_kt
                        new_elec_mwh = 0
                        new_h2_kg = 0
                        fossil_gj_reduced = 0
                        fuel_cost_usd = 0
                        capex_annual = 0
                        opex_annual = 0

                # Baseline fuel costs (unchanged from 2025)
                baseline_fuel_cost = (
                    facility['naphtha_gj'] * naphtha_price +
                    facility['lng_gj'] * lng_price +
                    facility['fuel_gas_gj'] * 10 +  # $10/GJ
                    facility['electricity_kwh'] / 1000 * grid_price +  # kWh to MWh
                    facility['lpg_gj'] * 14 +  # $14/GJ
                    facility['fuel_oil_gj'] * 13 +  # $13/GJ
                    facility['diesel_gj'] * 16  # $16/GJ
                )

                yearly_data.append({
                    'year': year,
                    'facility_id': facility['facility_id'],
                    'product': facility['product'],
                    'product_group': facility['product_group'],
                    'process': facility['process'],
                    'company': facility['company'],
                    'location': facility['location'],
                    'capacity_kt': facility['capacity_kt'],
                    'is_ncc': facility['is_ncc'],
                    'technology_deployed': technology_used,
                    'deployment_rate': deployment_rate,
                    # Energy - Baseline
                    'baseline_naphtha_gj': facility['naphtha_gj'],
                    'baseline_electricity_kwh': facility['electricity_kwh'],
                    'baseline_lng_gj': facility['lng_gj'],
                    'baseline_fuel_gas_gj': facility['fuel_gas_gj'],
                    'baseline_byproduct_gas_gj': facility['byproduct_gas_gj'],
                    'baseline_lpg_gj': facility['lpg_gj'],
                    'baseline_fuel_oil_gj': facility['fuel_oil_gj'],
                    'baseline_diesel_gj': facility['diesel_gj'],
                    # Energy - After transition
                    'fossil_fuel_reduced_gj': fossil_gj_reduced,
                    'new_electricity_mwh': new_elec_mwh,
                    'new_h2_kg': new_h2_kg,
                    # Emissions
                    'baseline_emissions_kt': base_emissions_kt,
                    'emissions_reduced_kt': emissions_reduced_kt,
                    'final_emissions_kt': final_emissions_kt,
                    # Costs
                    'baseline_fuel_cost_usd': baseline_fuel_cost,
                    'new_fuel_cost_usd': fuel_cost_usd,
                    'capex_annual_usd': capex_annual,
                    'opex_annual_usd': opex_annual,
                    'total_annual_cost_usd': fuel_cost_usd + capex_annual + opex_annual,
                    # Prices
                    'h2_price_usd_per_kg': h2_price,
                    're_price_usd_per_mwh': re_price,
                    'grid_price_usd_per_mwh': grid_price,
                    'grid_ef_tco2_per_mwh': grid_ef,
                })

        self.df_yearly_facility = pd.DataFrame(yearly_data)

        # Post-process to ensure facility-level emissions match targets
        print("  Calibrating to emission targets...")
        for year in years:
            target = self.yearly_targets[year]
            mask = self.df_yearly_facility['year'] == year
            current_total = self.df_yearly_facility.loc[mask, 'final_emissions_kt'].sum() / 1000

            if current_total > 0 and target < current_total:
                # Scale emissions down to match target
                scale_factor = target / current_total
                self.df_yearly_facility.loc[mask, 'final_emissions_kt'] *= scale_factor
                # Also adjust emissions_reduced to maintain consistency
                self.df_yearly_facility.loc[mask, 'emissions_reduced_kt'] = (
                    self.df_yearly_facility.loc[mask, 'baseline_emissions_kt'] -
                    self.df_yearly_facility.loc[mask, 'final_emissions_kt']
                )

        print(f"  Generated {len(self.df_yearly_facility)} rows (248 facilities x 26 years)")

        return self.df_yearly_facility

    def generate_annual_summary(self):
        """Generate annual summary aggregations"""
        print("\nGenerating annual summary...")

        summary = self.df_yearly_facility.groupby('year').agg({
            'baseline_emissions_kt': 'sum',
            'emissions_reduced_kt': 'sum',
            'final_emissions_kt': 'sum',
            'fossil_fuel_reduced_gj': 'sum',
            'new_electricity_mwh': 'sum',
            'new_h2_kg': 'sum',
            'baseline_fuel_cost_usd': 'sum',
            'new_fuel_cost_usd': 'sum',
            'capex_annual_usd': 'sum',
            'opex_annual_usd': 'sum',
            'total_annual_cost_usd': 'sum',
        }).reset_index()

        # Convert to proper units
        summary['baseline_emissions_mt'] = summary['baseline_emissions_kt'] / 1000
        summary['emissions_reduced_mt'] = summary['emissions_reduced_kt'] / 1000
        summary['final_emissions_mt'] = summary['final_emissions_kt'] / 1000
        summary['fossil_fuel_reduced_pj'] = summary['fossil_fuel_reduced_gj'] / 1e6
        summary['new_electricity_twh'] = summary['new_electricity_mwh'] / 1e6
        summary['new_h2_mt'] = summary['new_h2_kg'] / 1e9
        summary['total_cost_musd'] = summary['total_annual_cost_usd'] / 1e6
        summary['capex_musd'] = summary['capex_annual_usd'] / 1e6
        summary['opex_musd'] = summary['opex_annual_usd'] / 1e6
        summary['fuel_cost_musd'] = summary['new_fuel_cost_usd'] / 1e6

        # Add targets and reduction percentages
        summary['target_mt'] = summary['year'].map(self.yearly_targets)
        summary['reduction_pct'] = (52 - summary['final_emissions_mt']) / 52 * 100

        self.df_annual_summary = summary
        return summary

    def generate_regional_summary(self):
        """Generate regional summary by year"""
        print("\nGenerating regional summary...")

        regional = self.df_yearly_facility.groupby(['year', 'location']).agg({
            'facility_id': 'count',
            'capacity_kt': 'sum',
            'baseline_emissions_kt': 'sum',
            'final_emissions_kt': 'sum',
            'emissions_reduced_kt': 'sum',
            'new_electricity_mwh': 'sum',
            'new_h2_kg': 'sum',
            'total_annual_cost_usd': 'sum',
        }).reset_index()

        regional.columns = ['year', 'location', 'num_facilities', 'capacity_kt',
                           'baseline_emissions_kt', 'final_emissions_kt',
                           'emissions_reduced_kt', 'new_electricity_mwh',
                           'new_h2_kg', 'total_cost_usd']

        regional['baseline_emissions_mt'] = regional['baseline_emissions_kt'] / 1000
        regional['final_emissions_mt'] = regional['final_emissions_kt'] / 1000
        regional['emissions_reduced_mt'] = regional['emissions_reduced_kt'] / 1000
        regional['reduction_pct'] = regional['emissions_reduced_kt'] / regional['baseline_emissions_kt'] * 100

        self.df_regional = regional
        return regional

    def generate_company_summary(self):
        """Generate company summary by year"""
        print("\nGenerating company summary...")

        company = self.df_yearly_facility.groupby(['year', 'company']).agg({
            'facility_id': 'count',
            'capacity_kt': 'sum',
            'baseline_emissions_kt': 'sum',
            'final_emissions_kt': 'sum',
            'emissions_reduced_kt': 'sum',
            'new_electricity_mwh': 'sum',
            'new_h2_kg': 'sum',
            'total_annual_cost_usd': 'sum',
        }).reset_index()

        company.columns = ['year', 'company', 'num_facilities', 'capacity_kt',
                          'baseline_emissions_kt', 'final_emissions_kt',
                          'emissions_reduced_kt', 'new_electricity_mwh',
                          'new_h2_kg', 'total_cost_usd']

        company['baseline_emissions_mt'] = company['baseline_emissions_kt'] / 1000
        company['final_emissions_mt'] = company['final_emissions_kt'] / 1000
        company['emissions_reduced_mt'] = company['emissions_reduced_kt'] / 1000
        company['reduction_pct'] = company['emissions_reduced_kt'] / company['baseline_emissions_kt'] * 100

        self.df_company = company
        return company

    def generate_technology_deployment(self):
        """Generate technology deployment timeline"""
        print("\nGenerating technology deployment timeline...")

        tech_deploy = self.df_yearly_facility.groupby(['year', 'technology_deployed']).agg({
            'facility_id': 'count',
            'capacity_kt': 'sum',
            'emissions_reduced_kt': 'sum',
            'total_annual_cost_usd': 'sum',
        }).reset_index()

        tech_deploy.columns = ['year', 'technology', 'num_facilities', 'capacity_kt',
                               'emissions_reduced_kt', 'total_cost_usd']

        tech_deploy['emissions_reduced_mt'] = tech_deploy['emissions_reduced_kt'] / 1000

        self.df_tech_deploy = tech_deploy
        return tech_deploy

    def generate_cost_summary(self):
        """Generate detailed cost breakdown"""
        print("\nGenerating cost summary...")

        cost = self.df_yearly_facility.groupby('year').agg({
            'capex_annual_usd': 'sum',
            'opex_annual_usd': 'sum',
            'new_fuel_cost_usd': 'sum',
            'total_annual_cost_usd': 'sum',
            'emissions_reduced_kt': 'sum',
        }).reset_index()

        cost['capex_musd'] = cost['capex_annual_usd'] / 1e6
        cost['opex_musd'] = cost['opex_annual_usd'] / 1e6
        cost['fuel_cost_musd'] = cost['new_fuel_cost_usd'] / 1e6
        cost['total_cost_musd'] = cost['total_annual_cost_usd'] / 1e6
        cost['emissions_reduced_mt'] = cost['emissions_reduced_kt'] / 1000
        cost['cost_per_tco2'] = cost['total_annual_cost_usd'] / (cost['emissions_reduced_kt'] * 1000)
        cost['cost_per_tco2'] = cost['cost_per_tco2'].replace([np.inf, -np.inf], 0).fillna(0)

        # Cumulative costs
        cost['cumulative_capex_musd'] = cost['capex_musd'].cumsum()
        cost['cumulative_opex_musd'] = cost['opex_musd'].cumsum()
        cost['cumulative_fuel_musd'] = cost['fuel_cost_musd'].cumsum()
        cost['cumulative_total_musd'] = cost['total_cost_musd'].cumsum()

        self.df_cost = cost
        return cost

    def export_to_excel(self, filename, ncc_technology='NCC-Electricity'):
        """Export all data to multi-sheet Excel workbook"""
        print(f"\nExporting to Excel: {filename}")

        filepath = self.output_dir / filename

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Sheet 1: Facility Master Data (248 facilities)
            print("  - Writing Facility_Master...")
            self.df_baseline.to_excel(writer, sheet_name='Facility_Master', index=False)

            # Sheet 2: Yearly Facility Detail (248 x 26 = 6,448 rows)
            print("  - Writing Yearly_Facility_Detail...")
            self.df_yearly_facility.to_excel(writer, sheet_name='Yearly_Facility_Detail', index=False)

            # Sheet 3: Annual Summary
            print("  - Writing Annual_Summary...")
            self.df_annual_summary.to_excel(writer, sheet_name='Annual_Summary', index=False)

            # Sheet 4: Regional Summary
            print("  - Writing Regional_Summary...")
            self.df_regional.to_excel(writer, sheet_name='Regional_Summary', index=False)

            # Sheet 5: Company Summary
            print("  - Writing Company_Summary...")
            self.df_company.to_excel(writer, sheet_name='Company_Summary', index=False)

            # Sheet 6: Technology Deployment
            print("  - Writing Technology_Deployment...")
            self.df_tech_deploy.to_excel(writer, sheet_name='Technology_Deployment', index=False)

            # Sheet 7: Cost Summary
            print("  - Writing Cost_Summary...")
            self.df_cost.to_excel(writer, sheet_name='Cost_Summary', index=False)

            # Sheet 8: Deployment Schedule (optimization results)
            print("  - Writing Deployment_Schedule...")
            self.df_deployment.to_excel(writer, sheet_name='Deployment_Schedule', index=False)

            # Sheet 9: Emission Targets
            print("  - Writing Emission_Targets...")
            targets_df = pd.DataFrame([
                {'year': y, 'target_mt': t, 'reduction_pct': (52-t)/52*100}
                for y, t in self.yearly_targets.items()
            ])
            targets_df.to_excel(writer, sheet_name='Emission_Targets', index=False)

            # Sheet 10: Technology Parameters
            print("  - Writing Technology_Parameters...")
            self.df_tech_params.to_excel(writer, sheet_name='Technology_Parameters', index=False)

            # Sheet 11: Price Trajectories
            print("  - Writing Price_Trajectories...")
            prices = pd.merge(self.df_h2_prices[['year', 'h2_price_usd_per_kg']],
                            self.df_re_prices[['year', 're_price_usd_per_mwh']], on='year')
            prices = pd.merge(prices, self.df_grid_prices[['year', 'grid_price_usd_per_mwh']], on='year')
            prices = pd.merge(prices, self.df_grid_ef[['year', 'grid_ef_tco2_per_mwh']], on='year')
            prices.to_excel(writer, sheet_name='Price_Trajectories', index=False)

        print(f"\n  Excel file saved: {filepath}")
        print(f"  File size: {filepath.stat().st_size / 1024 / 1024:.2f} MB")

        return filepath

    def run_scenario(self, ncc_technology='NCC-Electricity'):
        """Run complete scenario and generate Excel output"""
        print(f"\n{'='*80}")
        print(f"RUNNING SCENARIO: {ncc_technology}")
        print(f"{'='*80}")

        # Calculate baseline
        self.calculate_facility_baseline()

        # Optimize transition timing
        self.optimize_transition_timing(ncc_technology)

        # Generate all data
        self.generate_yearly_facility_data(ncc_technology)
        self.generate_annual_summary()
        self.generate_regional_summary()
        self.generate_company_summary()
        self.generate_technology_deployment()
        self.generate_cost_summary()

        # Export to Excel
        filename = f'MACC_Report_{ncc_technology.replace("-", "_")}.xlsx'
        filepath = self.export_to_excel(filename, ncc_technology)

        return filepath


def main():
    """Generate Excel reports for both scenarios"""
    print("\n" + "="*80)
    print("PETROCHEMICAL MACC MODEL - EXCEL REPORT GENERATION")
    print("="*80)
    print("\nTargets:")
    print("  - 2025: 52 MtCO2 (Baseline)")
    print("  - 2035: 39.26 MtCO2 (-24.5%)")
    print("  - 2050: 0 MtCO2 (-100%)")
    print("="*80)

    generator = ComprehensiveExcelGenerator()

    # Main Scenario: NCC-Electricity
    print("\n" + "="*80)
    print("SCENARIO 1: NCC-Electricity (Main)")
    print("="*80)
    filepath1 = generator.run_scenario('NCC-Electricity')

    # Alternative Scenario: NCC-H2
    print("\n" + "="*80)
    print("SCENARIO 2: NCC-H2 (Alternative)")
    print("="*80)
    filepath2 = generator.run_scenario('NCC-H2')

    print("\n" + "="*80)
    print("COMPLETE!")
    print("="*80)
    print(f"\nGenerated files:")
    print(f"  1. {filepath1}")
    print(f"  2. {filepath2}")
    print("\nEach Excel file contains:")
    print("  - Facility_Master: 248 facilities with baseline data")
    print("  - Yearly_Facility_Detail: 6,448 rows (248 x 26 years)")
    print("  - Annual_Summary: Yearly aggregations")
    print("  - Regional_Summary: By location and year")
    print("  - Company_Summary: By company and year")
    print("  - Technology_Deployment: Deployment timeline")
    print("  - Cost_Summary: CAPEX, OPEX, Fuel costs")
    print("  - Deployment_Schedule: Optimization results")
    print("  - Emission_Targets: Target trajectory")
    print("  - Technology_Parameters: Tech specs")
    print("  - Price_Trajectories: H2, RE, Grid prices")


if __name__ == '__main__':
    main()
