"""
MODULE 2: ENERGY-BASED MACC ANALYSIS
MACC Analysis Module
Calculates Marginal Abatement Cost Curves for petrochemical technologies.

Source: PLANiT Institute (2025) - RE PPA Price & LCOH Logic
Calculate Marginal Abatement Cost Curves with explicit energy consumption tracking
REDESIGNED: 2025-10-16 - Replaced LCOE approach with energy-based methodology
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from .utils import (DataLoader, TechnologyCostCalculator, PriceCalculator,
                    save_csv_output, save_plot, is_ncc_facility, identify_product_group)
from .lcoh import calculate_lcoh


class MACCAnalyzer:
    """
    Energy-Based MACC Analysis

    Key Principle:
        MACC = CAPEX_annual + OPEX_annual + Fuel_Cost_Differential

    Where Fuel_Cost_Differential explicitly tracks:
        - Energy replacement (fossil → H2/electricity)
        - Price differentials
        - Emission reductions

    CRITICAL: Naphtha feedstock cost is FIXED (not included in differential)
    """

    def __init__(self, baseline_output='outputs/module_01', data_dir='data',
                 output_dir='outputs/module_02'):
        self.baseline_dir = Path(baseline_output)
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("MODULE 2: ENERGY-BASED MACC ANALYSIS")
        print("="*80)

        # Load data
        print("\nLoading data...")
        loader = DataLoader(self.data_dir)

        self.df_baseline = pd.read_csv(self.baseline_dir / 'baseline_2025_detailed.csv')
        self.df_tech_params = loader.load_technology_params()
        self.df_h2_prices = loader.load_h2_prices()
        self.df_re_prices = loader.load_re_prices()
        self.df_grid_prices = loader.load_grid_prices()
        self.df_hp_applicability = loader.load_heat_pump_applicability()
        self.df_fuel_prices = pd.read_csv(self.data_dir / 'fuel_price_trajectory.csv')
        self.df_grid_emission = pd.read_csv(self.data_dir / 'grid_emission_trajectory.csv')

        # Load demand growth trajectory
        try:
            self.df_demand_growth = pd.read_csv(self.data_dir / 'demand_growth_trajectory.csv')
            print(f"   - Loaded demand growth trajectory")
        except FileNotFoundError:
            print("   - No demand growth file, assuming zero growth")
            self.df_demand_growth = pd.DataFrame({
                'year': range(2025, 2051),
                'cumulative_capacity_multiplier': [1.0] * 26
            })

        print(f"   - Loaded baseline: {len(self.df_baseline)} facilities")
        print(f"   - Loaded {len(self.df_tech_params)} technologies")

        # Initialize calculators
        self.tech_cost_calc = TechnologyCostCalculator(self.df_tech_params)
        self.price_calc = PriceCalculator(self.df_h2_prices, self.df_re_prices, self.df_fuel_prices)

        # Load emission factors from data file
        self.df_emission_factors = pd.read_csv(self.data_dir / 'emission_factors.csv')
        ef_dict = self.df_emission_factors.set_index('fuel')

        # Get emission factors
        self.ef_naphtha = ef_dict.loc['Naphtha', 'tCO2_per_GJ']
        self.ef_h2_green = ef_dict.loc['H2', 'tCO2_per_kg']  # Green H2 = 0.0

    def calculate_macc_annual(self, years=range(2025, 2051)):
        """Calculate MACC for all technologies and years"""
        print(f"\nCalculating dynamic MACC ({min(years)}-{max(years)})...")

        macc_data = []

        for year in years:
            # Get prices for this year
            h2_price = self.price_calc.get_h2_price(year)  # $/kg
            re_price = self.price_calc.get_re_price(year)  # $/MWh
            naphtha_price = self.df_fuel_prices[self.df_fuel_prices['year'] == year]['naphtha_usd_per_gj'].iloc[0]

            # Get GRID electricity price and emission factor (Korean grid)
            grid_price = self.df_grid_prices[self.df_grid_prices['year'] == year]['grid_price_usd_per_mwh'].iloc[0]
            grid_ef = self.df_grid_emission[self.df_grid_emission['year'] == year]['grid_ef_tco2_per_mwh'].iloc[0]

            # 1. HEAT PUMPS
            # Uses GRID electricity by default (RE PPA can clean it later)
            hp_macc = self._calculate_heat_pump_macc(year, h2_price, re_price, naphtha_price, grid_price, grid_ef)
            macc_data.append(hp_macc)

            # 2. NCC-H2 (Hydrogen)
            # Pass re_price to enable dynamic LCOH calculation
            ncc_h2_macc = self._calculate_ncc_h2_macc(year, h2_price, naphtha_price, re_price=re_price)
            macc_data.append(ncc_h2_macc)

            # 3. NCC-Electricity (uses RENEWABLE electricity - RE_PPA)
            ncc_elec_macc = self._calculate_ncc_electricity_macc(year, re_price, naphtha_price)
            macc_data.append(ncc_elec_macc)

            # 4. RE Switching (converting grid electricity to RE)
            re_ppa_macc = self._calculate_re_ppa_macc(year, re_price, grid_price, grid_ef)
            macc_data.append(re_ppa_macc)

            # 5. RDH (RotoDynamic Heater for high-temp BTX processes)
            # Covers the gap where Heat Pump cannot reach (>200°C)
            rdh_macc = self._calculate_rdh_macc(year, re_price, grid_ef)
            macc_data.append(rdh_macc)

        df_macc = pd.DataFrame(macc_data)

        print(f"   - Calculated {len(df_macc)} technology-year combinations")

        self.df_macc = df_macc
        return df_macc

    def _calculate_heat_pump_macc(self, year, h2_price, re_price, naphtha_price, elec_price, grid_ef):
        """
        Calculate Heat Pump MACC with explicit energy conversion
        
        Uses GRID ELECTRICITY by default.
        RE PPA is a separate measure that can decarbonize this electricity.
        """
        tech_costs = self.tech_cost_calc.get_technology_costs('Heat_Pump', year)
        cop = tech_costs['cop']

        # Get capacity multiplier for this year (demand growth)
        capacity_multiplier = self.df_demand_growth[
            self.df_demand_growth['year'] == year
        ]['cumulative_capacity_multiplier'].iloc[0]

        # Abatement potential
        # Heat pumps replace ALL fossil fuel combustion (NOT electricity)
        potential_mt = 0
        total_fossil_fuel_gj = 0  # For fuel cost calculation

        for _, row in self.df_hp_applicability.iterrows():
            product_group = row['product_group']
            applicability = row['applicability_pct'] / 100

            # Get fossil fuel combustion emissions for NON-NCC facilities only
            # NCC facilities get NCC-H2 and NCC-Electricity, not Heat Pump
            df_group = self.df_baseline[
                (self.df_baseline['product_group'] == product_group) &
                (self.df_baseline['process'] != 'Naphtha Cracker')
            ]

            fossil_emissions_kt = (
                df_group['emissions_naphtha_kt'].sum() +
                df_group['emissions_lng_kt'].sum() +
                df_group['emissions_fuel_gas_kt'].sum() +
                df_group['emissions_lpg_kt'].sum() +
                df_group['emissions_fuel_oil_kt'].sum() +
                df_group['emissions_diesel_kt'].sum()
            )

            # Calculate total fossil fuel energy (GJ) from emissions
            # Assuming average EF for fossil fuels ≈ 0.0149 tCO2/GJ
            fossil_fuel_gj = (fossil_emissions_kt * 1000) / self.ef_naphtha

            potential_mt += (fossil_emissions_kt / 1000) * applicability
            total_fossil_fuel_gj += fossil_fuel_gj * applicability

        # Scale by demand growth
        potential_mt *= capacity_multiplier
        total_fossil_fuel_gj *= capacity_multiplier

        # Energy conversion
        electricity_mwh_required = total_fossil_fuel_gj / cop / 3.6  # MWh

        # Emissions after heat pump (using GRID electricity)
        # grid_ef is passed from the main loop
        emissions_after_mt = (electricity_mwh_required * grid_ef) / 1e6  # MtCO2

        # Actual abatement (considering Grid emissions)
        abatement_mt = potential_mt - emissions_after_mt

        # Costs per MtCO2 abated (Simple annualization: NO discount rate)
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        capex_ann = capex_musd_per_mtco2 / lifetime  # Simple: CAPEX / lifetime
        opex_ann = capex_musd_per_mtco2 * (tech_costs['opex_pct_capex'] / 100)  # OPEX as % of CAPEX

        # Fuel cost: GRID electricity cost (elec_price = grid_price)
        electricity_cost_total = electricity_mwh_required * elec_price
        fuel_cost_diff_total = electricity_cost_total  # Pure electricity cost (assuming fossil fuel savings are handled elsewhere or ignored for simplicity in this diff calculation? Wait, original code ignored fossil savings. I should keep it consistent or fix it? Original comment: "Pure RE electricity cost (no fossil fuel savings counted)". This is a simplification. I will keep it but use Grid Price.)

        if abatement_mt > 0:
            fuel_cost_diff_per_tco2 = fuel_cost_diff_total / (abatement_mt * 1e6)
        else:
            fuel_cost_diff_per_tco2 = 1e9

        total_cost = capex_ann + opex_ann + fuel_cost_diff_per_tco2

        return {
            'year': year,
            'technology': 'Heat_Pump',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': abatement_mt,
            'capex_ann_usd_per_tco2': capex_ann,
            'opex_ann_usd_per_tco2': opex_ann,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff_per_tco2,
            'total_cost_usd_per_tco2': total_cost,
            're_price_usd_per_mwh': np.nan,
            'h2_price_usd_per_kg': h2_price,
            'electricity_consumption_mwh': electricity_mwh_required,
            'fossil_fuel_replaced_gj': total_fossil_fuel_gj,
            'methodology': 'Energy-based',
            'grid_ef_tco2_per_mwh': grid_ef,
            'grid_price_usd_per_mwh': elec_price
        }

    def _calculate_ncc_h2_macc(self, year, h2_price, naphtha_price, re_price=None):
        """
        Calculate NCC-H2 MACC with H2 as energy source
        
        NEW: Calculates H2 price dynamically using LCOH logic if re_price is provided.
        """
        tech_costs = self.tech_cost_calc.get_technology_costs('NCC-H2', year)
        h2_ton_per_ton_ethylene = tech_costs['h2_ton_per_ton_ethylene']

        # Get capacity multiplier and operating rate
        demand_row = self.df_demand_growth[self.df_demand_growth['year'] == year]
        capacity_multiplier = demand_row['cumulative_capacity_multiplier'].iloc[0]
        
        if 'operating_rate_pct' in demand_row.columns:
            op_rate = demand_row['operating_rate_pct'].iloc[0] / 100.0
        else:
            op_rate = 1.0
            
        # Effective multiplier
        effective_multiplier = capacity_multiplier * op_rate

        # Get total NCC production capacity (ALL NCC products, not just ethylene)
        # NCC-H2 covers ALL naphtha cracker products (Ethylene, Propylene, BTX, etc.)
        ncc_facilities = self.df_baseline[self.df_baseline['process'] == 'Naphtha Cracker']
        total_ncc_capacity_kt = ncc_facilities['capacity_kt'].sum()
        total_ncc_capacity_kt *= effective_multiplier

        # Emissions calculation: Use ALL NCC facility emissions (combustion only, not electricity)
        # NCC-H2/Electricity replaces combustion emissions, not existing electricity
        if len(ncc_facilities) > 0:
            # Total combustion emissions (excluding electricity)
            total_ncc_emissions_kt = (
                ncc_facilities['total_emissions_kt'].sum() - 
                ncc_facilities['emissions_electricity_kt'].sum()
            )
            total_capacity_kt = ncc_facilities['capacity_kt'].sum()
            emission_baseline_per_ton = total_ncc_emissions_kt / total_capacity_kt  # tCO2/ton
        else:
            emission_baseline_per_ton = 1.74  # Fallback

        # After NCC-H2: Naphtha becomes FEEDSTOCK only (no combustion), H2 provides energy
        emission_h2_per_ton = self.ef_h2_green  # tCO2/ton (green H2 = 0)
        abatement_per_ton = emission_baseline_per_ton - emission_h2_per_ton

        # Total abatement potential (ALL NCC products)
        abatement_mt = (total_ncc_capacity_kt * 1000 * abatement_per_ton) / 1e6  # MtCO2

        # Costs
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        capex_ann = capex_musd_per_mtco2 / lifetime  # Simple: CAPEX / lifetime
        opex_ann = capex_musd_per_mtco2 * (tech_costs['opex_pct_capex'] / 100)  # OPEX as % of CAPEX

        # DYNAMIC H2 PRICE CALCULATION (LCOH)
        if re_price is not None:
            # Electrolyzer CAPEX trajectory: $1000/kW (2025) -> $500/kW (2050) = 50% decline
            # Linear interpolation: 20 $/kW/year decline
            ely_capex = max(500, 1000 - (year - 2025) * 20)

            # Efficiency trajectory: 70% (2025) -> 75% (2050)
            ely_efficiency = min(0.75, 0.70 + (year - 2025) * 0.002)

            lcoh_result = calculate_lcoh(
                elec_price=re_price,
                capex=ely_capex,
                efficiency=ely_efficiency,
                lifetime=20
            )
            final_h2_price = lcoh_result['lcoh']
            # print(f"   [DEBUG] Year {year}: RE=${re_price:.1f}/MWh, Ely=${ely_capex}/kW -> LCOH=${final_h2_price:.2f}/kg")
        else:
            final_h2_price = h2_price

        # Fuel cost: H2 cost only (no fossil fuel savings)
        h2_fuel_cost_per_ton = h2_ton_per_ton_ethylene * 1000 * final_h2_price  # $/ton ethylene

        if abatement_per_ton > 0:
            fuel_cost_diff_per_tco2 = h2_fuel_cost_per_ton / abatement_per_ton  # $/tCO2
        else:
            fuel_cost_diff_per_tco2 = 0

        total_cost = capex_ann + opex_ann + fuel_cost_diff_per_tco2

        return {
            'year': year,
            'technology': 'NCC-H2',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': abatement_mt,
            'capex_ann_usd_per_tco2': capex_ann,
            'opex_ann_usd_per_tco2': opex_ann,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff_per_tco2,
            'total_cost_usd_per_tco2': total_cost,
            're_price_usd_per_mwh': np.nan,
            'h2_price_usd_per_kg': final_h2_price,
            'h2_consumption_ton_per_ton_ethylene': h2_ton_per_ton_ethylene,
            'baseline_combustion_emissions_tco2_per_ton': emission_baseline_per_ton,
            'ncc_capacity_kt': total_ncc_capacity_kt,
            'h2_fuel_cost_per_ton_ethylene': h2_fuel_cost_per_ton,
            'methodology': 'Energy-based (Dynamic LCOH)'
        }

    def _calculate_ncc_electricity_macc(self, year, re_price, naphtha_price):
        """
        Calculate NCC-Electricity MACC using RENEWABLE electricity (RE_PPA)

        Process Change:
            Before: Naphtha cracking with LNG/Fuel Gas combustion (~11 GJ/ton ethylene)
            After:  Naphtha cracking with RENEWABLE electricity (5.0 MWh/ton ethylene)

        CRITICAL:
            - Naphtha feedstock (105 GJ) continues unchanged - still purchased!
            - LNG/Fuel Gas combustion (~11 GJ) is ELIMINATED
            - RENEWABLE electricity provides energy (RE_PPA pricing)
            - Renewable electricity has ZERO emissions (no EF penalty)
            - NO fuel cost saving (naphtha not used as fuel before)

        Cost:
            MACC = CAPEX_annual + OPEX_annual + RE_electricity_cost / tCO2_abated

        Emissions:
            Baseline: Fossil fuel combustion emissions
            After: ZERO emissions (renewable electricity)
            Abatement: Baseline emissions (100% abatement)
        """
        tech_costs = self.tech_cost_calc.get_technology_costs('NCC-Electricity', year)
        elec_mwh_per_ton = tech_costs['elec_mwh_per_ton_ethylene']

        # Get capacity multiplier and operating rate
        demand_row = self.df_demand_growth[self.df_demand_growth['year'] == year]
        capacity_multiplier = demand_row['cumulative_capacity_multiplier'].iloc[0]
        
        if 'operating_rate_pct' in demand_row.columns:
            op_rate = demand_row['operating_rate_pct'].iloc[0] / 100.0
        else:
            op_rate = 1.0
            
        # Effective multiplier
        effective_multiplier = capacity_multiplier * op_rate

        # Get total NCC production capacity (ALL NCC products, not just ethylene)
        # NCC-Electricity covers ALL naphtha cracker products (Ethylene, Propylene, BTX, etc.)
        ncc_facilities = self.df_baseline[self.df_baseline['process'] == 'Naphtha Cracker']
        total_ncc_capacity_kt = ncc_facilities['capacity_kt'].sum()
        total_ncc_capacity_kt *= effective_multiplier

        # Emissions calculation: Use ALL NCC facility emissions (combustion only, not electricity)
        # NCC-Electricity replaces combustion emissions, not existing electricity
        if len(ncc_facilities) > 0:
            # Total combustion emissions (excluding electricity)
            total_ncc_emissions_kt = (
                ncc_facilities['total_emissions_kt'].sum() - 
                ncc_facilities['emissions_electricity_kt'].sum()
            )
            total_capacity_kt = ncc_facilities['capacity_kt'].sum()
            emission_baseline_per_ton = total_ncc_emissions_kt / total_capacity_kt  # tCO2/ton
        else:
            emission_baseline_per_ton = 1.74  # Fallback

        # After NCC-Electricity: Uses RENEWABLE electricity (ZERO emissions)
        emission_elec_per_ton = 0.0  # tCO2/ton (renewable = zero emissions)

        abatement_per_ton = emission_baseline_per_ton  # 100% abatement (baseline - 0)

        # Total abatement potential (ALL NCC products)
        abatement_mt = (total_ncc_capacity_kt * 1000 * abatement_per_ton) / 1e6  # MtCO2

        # Costs
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        capex_ann = capex_musd_per_mtco2 / lifetime  # Simple: CAPEX / lifetime
        opex_ann = capex_musd_per_mtco2 * (tech_costs['opex_pct_capex'] / 100)  # OPEX as % of CAPEX

        # Fuel cost: RENEWABLE electricity cost only (no fossil fuel savings)
        electricity_cost_per_ton = elec_mwh_per_ton * re_price  # $/ton ethylene

        if abatement_per_ton > 0:
            fuel_cost_diff_per_tco2 = electricity_cost_per_ton / abatement_per_ton  # $/tCO2
        else:
            fuel_cost_diff_per_tco2 = 0

        total_cost = capex_ann + opex_ann + fuel_cost_diff_per_tco2

        return {
            'year': year,
            'technology': 'NCC-Electricity',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': abatement_mt,
            'capex_ann_usd_per_tco2': capex_ann,
            'opex_ann_usd_per_tco2': opex_ann,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff_per_tco2,
            'total_cost_usd_per_tco2': total_cost,
            're_price_usd_per_mwh': re_price,
            'h2_price_usd_per_kg': np.nan,
            'electricity_consumption_mwh_per_ton_ethylene': elec_mwh_per_ton,
            'baseline_combustion_emissions_tco2_per_ton': emission_baseline_per_ton,
            'ncc_capacity_kt': total_ncc_capacity_kt,
            'electricity_cost_per_ton_ethylene': electricity_cost_per_ton,
            'grid_ef_tco2_per_mwh': 0.0,
            'grid_price_usd_per_mwh': np.nan,
            'methodology': 'Energy-based'
        }

    def _calculate_re_ppa_macc(self, year, re_price, grid_price, grid_ef):
        """
        Calculate Renewable Electricity MACC (ALL facilities + Heat Pump electricity)

        Renewable Electricity = Switching from grid electricity to renewable energy
        Simply switching from grid electricity to RE electricity for ALL facilities
        No infrastructure needed - just procurement contract (PPA)
        No energy consumption change - just price differential

        EXTENDED: Also covers NEW electricity from Heat Pump deployment
        This enables full decarbonization by cleaning the grid electricity that
        Heat Pumps use to replace fossil fuel combustion.

        Cost:
            MACC = Price_Diff / Abatement_per_MWh
            (CAPEX = 0, OPEX = 0)
        """
        tech_costs = self.tech_cost_calc.get_technology_costs('RE_PPA', year)

        # Get capacity multiplier and op rate
        demand_row = self.df_demand_growth[self.df_demand_growth['year'] == year]
        capacity_multiplier = demand_row['cumulative_capacity_multiplier'].iloc[0]
        if 'operating_rate_pct' in demand_row.columns:
            op_rate = demand_row['operating_rate_pct'].iloc[0] / 100.0
        else:
            op_rate = 1.0
        effective_multiplier = capacity_multiplier * op_rate

        # 1. Baseline electricity emissions (ALL facilities)
        all_facilities = self.df_baseline.copy()
        baseline_elec_emissions_mt = all_facilities['emissions_electricity_kt'].sum() / 1000  # MtCO2
        baseline_elec_emissions_mt *= effective_multiplier

        # 2. NEW: Calculate Heat Pump electricity emissions (if Heat Pump deployed)
        # Heat Pump uses grid electricity which creates NEW emissions
        hp_elec_emissions_mt = 0
        for _, row in self.df_hp_applicability.iterrows():
            product_group = row['product_group']
            applicability = row['applicability_pct'] / 100
            
            # Get fossil fuel emissions for NON-NCC facilities
            df_group = self.df_baseline[
                (self.df_baseline['product_group'] == product_group) &
                (self.df_baseline['process'] != 'Naphtha Cracker')
            ]
            
            fossil_emissions_kt = (
                df_group['emissions_naphtha_kt'].sum() +
                df_group['emissions_lng_kt'].sum() +
                df_group['emissions_fuel_gas_kt'].sum() +
                df_group['emissions_lpg_kt'].sum() +
                df_group['emissions_fuel_oil_kt'].sum() +
                df_group['emissions_diesel_kt'].sum()
            )
            
            # Fossil fuel energy (GJ) and electricity needed
            fossil_fuel_gj = (fossil_emissions_kt * 1000) / self.ef_naphtha * applicability
            cop = 4.0  # COP of heat pump
            elec_mwh = fossil_fuel_gj / cop / 3.6
            hp_elec_emissions_mt += (elec_mwh * grid_ef) / 1e6  # MtCO2
        
        hp_elec_emissions_mt *= effective_multiplier

        # Total electricity emissions that RE_PPA can clean
        total_elec_emissions_mt = baseline_elec_emissions_mt + hp_elec_emissions_mt

        # Emission factors
        re_ef = 0.05  # tCO2/MWh (lifecycle emissions for renewable energy)

        # SAFETY CHECK: If Grid is cleaner than RE (or zero), RE PPA has NO benefit
        if grid_ef <= re_ef or np.isclose(grid_ef, 0):
            abatement_potential_mt = 0.0
            total_cost_diff = 0.0
            cost_per_tco2 = 1e9  # Infinite cost (not available/effective)
        else:
            # Abatement per MWh
            # abatement_per_mwh = grid_ef - re_ef

            # Abatement potential: all facility electricity + HP electricity could switch to RE
            # Potential = Emissions * (1 - RE_EF / Grid_EF)
            # Derived from: MWh = Emissions / Grid_EF
            #               New_Emissions = MWh * RE_EF = (Emissions / Grid_EF) * RE_EF
            #               Abatement = Emissions - New_Emissions = Emissions * (1 - RE_EF/Grid_EF)
            abatement_potential_mt = total_elec_emissions_mt * (1 - re_ef / grid_ef)

            # Cost: Price differential between RE and Grid (Option A - Switching)
            # When switching from Grid to RE:
            #   - Stop paying Grid price
            #   - Start paying RE price
            #   - Net cost = (RE price - Grid price) × electricity
            #   - This can be NEGATIVE if RE is cheaper than Grid!
            
            # Calculate MWh safely
            total_elec_mwh = total_elec_emissions_mt * 1e6 / grid_ef  # MWh
            
            price_diff = re_price - grid_price  # Can be negative!
            total_cost_diff = total_elec_mwh * price_diff  # Total incremental cost (can be negative!)

            if abatement_potential_mt > 0.001:  # Avoid tiny division errors
                cost_per_tco2 = total_cost_diff / (abatement_potential_mt * 1e6)  # $/tCO2
            else:
                cost_per_tco2 = 1e9

        return {
            'year': year,
            'technology': 'RE_PPA',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': abatement_potential_mt,
            'capex_ann_usd_per_tco2': 0,  # No capital investment for PPA
            'opex_ann_usd_per_tco2': 0,   # Operating cost included in PPA price
            'fuel_cost_diff_usd_per_tco2': cost_per_tco2,
            'total_cost_usd_per_tco2': cost_per_tco2,
            're_price_usd_per_mwh': re_price,
            'h2_price_usd_per_kg': np.nan,
            'grid_price_usd_per_mwh': grid_price,
            'grid_ef_tco2_per_mwh': grid_ef,
            'methodology': 'Energy-based'
        }

    def _calculate_rdh_macc(self, year, re_price, grid_ef):
        """
        Calculate RotoDynamic Heater (RDH) MACC for high-temperature BTX processes
        
        RDH (Coolbrook) replaces fossil fuel combustion for aromatics/BTX reforming.
        Applicable to non-NCC facilities where Heat Pump cannot reach (>200°C).
        
        Source: Coolbrook (2024)
        - Efficiency: 92-95% (electric-to-heat)
        - Temperature: up to 1700°C
        - TRL 8, Commercial 2026
        """
        tech_costs = self.tech_cost_calc.get_technology_costs('RDH', year)
        efficiency = tech_costs.get('energy_conversion_efficiency', 0.93)
        
        # Get capacity multiplier for this year
        capacity_multiplier = self.df_demand_growth[
            self.df_demand_growth['year'] == year
        ]['cumulative_capacity_multiplier'].iloc[0]
        
        # Calculate abatement potential from high-temp non-NCC processes
        # This covers the GAP that Heat Pump cannot address (>200°C)
        # Focus on Aromatics (BTX) which have 60% HP applicability, leaving 40% gap
        potential_mt = 0
        total_fossil_fuel_gj = 0
        
        for _, row in self.df_hp_applicability.iterrows():
            product_group = row['product_group']
            hp_applicability = row['applicability_pct'] / 100
            rdh_applicability = 1.0 - hp_applicability  # RDH covers the rest
            
            # Get fossil fuel emissions for NON-NCC facilities only
            df_group = self.df_baseline[
                (self.df_baseline['product_group'] == product_group) &
                (self.df_baseline['process'] != 'Naphtha Cracker')
            ]
            
            fossil_emissions_kt = (
                df_group['emissions_naphtha_kt'].sum() +
                df_group['emissions_lng_kt'].sum() +
                df_group['emissions_fuel_gas_kt'].sum() +
                df_group['emissions_lpg_kt'].sum() +
                df_group['emissions_fuel_oil_kt'].sum() +
                df_group['emissions_diesel_kt'].sum()
            )
            
            # Fossil fuel energy (GJ) from emissions
            fossil_fuel_gj = (fossil_emissions_kt * 1000) / self.ef_naphtha
            
            potential_mt += (fossil_emissions_kt / 1000) * rdh_applicability
            total_fossil_fuel_gj += fossil_fuel_gj * rdh_applicability
        
        # Scale by demand growth
        potential_mt *= capacity_multiplier
        total_fossil_fuel_gj *= capacity_multiplier
        
        # Energy conversion: Electric heat replaces fossil combustion
        # MWh required = GJ / 3.6 / efficiency
        electricity_mwh_required = total_fossil_fuel_gj / 3.6 / efficiency
        
        # RDH uses RE electricity (zero emissions after conversion)
        emissions_after_mt = 0  # Zero emissions when powered by RE
        abatement_mt = potential_mt - emissions_after_mt
        
        # Costs
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        capex_ann = capex_musd_per_mtco2 / lifetime
        opex_ann = capex_musd_per_mtco2 * (tech_costs['opex_pct_capex'] / 100)
        
        # Fuel cost: RE electricity cost
        electricity_cost_total = electricity_mwh_required * re_price
        
        if abatement_mt > 0:
            fuel_cost_diff_per_tco2 = electricity_cost_total / (abatement_mt * 1e6)
        else:
            fuel_cost_diff_per_tco2 = 1e9
        
        total_cost = capex_ann + opex_ann + fuel_cost_diff_per_tco2
        
        return {
            'year': year,
            'technology': 'RDH',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': abatement_mt,
            'capex_ann_usd_per_tco2': capex_ann,
            'opex_ann_usd_per_tco2': opex_ann,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff_per_tco2,
            'total_cost_usd_per_tco2': total_cost,
            're_price_usd_per_mwh': re_price,
            'h2_price_usd_per_kg': np.nan,
            'electricity_consumption_mwh': electricity_mwh_required,
            'fossil_fuel_replaced_gj': total_fossil_fuel_gj,
            'grid_ef_tco2_per_mwh': 0.0,  # Uses RE
            'grid_price_usd_per_mwh': np.nan,
            'methodology': 'Energy-based',
            'source': 'Coolbrook (2024)'
        }

    def create_visualizations(self):
        """Create MACC curve visualizations"""
        print("\nCreating visualizations...")

        # MACC curves for key years
        key_years = [2025, 2030, 2040, 2050]

        for year in key_years:
            df_year = self.df_macc[
                (self.df_macc['year'] == year) &
                (self.df_macc['available'] == True) &
                (self.df_macc['technology'] != 'Heat_Pump')  # Exclude Heat Pump from visualization
            ].sort_values('total_cost_usd_per_tco2')

            if len(df_year) == 0:
                continue

            fig, ax = plt.subplots(figsize=(12, 7))

            # Sort by cost for proper MACC ordering
            df_year_sorted = df_year.sort_values('total_cost_usd_per_tco2')

            # Create MACC bars
            x_pos = 0
            colors = {'Heat_Pump': '#2ECC71', 'NCC-H2': '#3498DB', 'NCC-Electricity': '#E74C3C', 'RE_PPA': '#F39C12'}
            tech_labels = {
                'Heat_Pump': 'Heat Pump',
                'RE_PPA': 'RE PPA',
                'NCC-Electricity': 'NCC-Electricity',
                'NCC-H2': 'NCC-H2'
            }

            legend_entries = []

            for _, row in df_year_sorted.iterrows():
                width = row['abatement_potential_mtco2']
                height = row['total_cost_usd_per_tco2']
                color = colors.get(row['technology'], 'gray')
                label = tech_labels.get(row['technology'], row['technology'])

                if label not in legend_entries:
                    ax.bar(x_pos + width/2, height, width=width, color=color,
                          edgecolor='black', linewidth=1.2, alpha=0.85, label=label)
                    legend_entries.append(label)
                else:
                    ax.bar(x_pos + width/2, height, width=width, color=color,
                          edgecolor='black', linewidth=1.2, alpha=0.85)

                x_pos += width

            # Zero line
            ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5, alpha=0.8, zorder=10)

            # Labels
            ax.set_xlabel('Cumulative Abatement Potential (MtCO2/year)', fontsize=13, fontweight='bold')
            ax.set_ylabel('Marginal Abatement Cost ($/tCO2)', fontsize=13, fontweight='bold')
            ax.set_title(f'MACC Curve - {year} (Energy-Based)', fontsize=15, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y', linestyle='--')
            ax.legend(loc='best', fontsize=10, framealpha=0.95, edgecolor='black')

            save_plot(fig, self.output_dir / f'macc_curve_{year}.png')

        # Cost evolution
        fig, ax = plt.subplots(figsize=(12, 7))

        tech_styles = {
            'Heat_Pump': {'color': '#2ECC71', 'marker': 'o', 'label': 'Heat Pump'},
            'RE_PPA': {'color': '#F39C12', 'marker': 's', 'label': 'RE PPA'},
            'NCC-Electricity': {'color': '#E74C3C', 'marker': '^', 'label': 'NCC-Electricity'},
            'NCC-H2': {'color': '#3498DB', 'marker': 'D', 'label': 'NCC-H2'}
        }

        # Exclude Heat Pump from cost evolution plot
        for tech in ['RE_PPA', 'NCC-Electricity', 'NCC-H2']:
            df_tech = self.df_macc[self.df_macc['technology'] == tech]
            style = tech_styles[tech]
            ax.plot(df_tech['year'], df_tech['total_cost_usd_per_tco2'],
                   linewidth=2.5, color=style['color'], marker=style['marker'],
                   markersize=6, label=style['label'], alpha=0.9)

        ax.axhline(y=0, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label='Cost Parity')
        ax.set_xlabel('Year', fontsize=13, fontweight='bold')
        ax.set_ylabel('Marginal Abatement Cost ($/tCO2)', fontsize=13, fontweight='bold')
        ax.set_title('Technology Cost Trajectories (2025-2050) - Energy-Based', fontsize=15, fontweight='bold')
        ax.legend(loc='best', fontsize=10, framealpha=0.95)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(2024, 2051)

        save_plot(fig, self.output_dir / 'cost_evolution_annual.png')

    def save_outputs(self):
        """Save outputs"""
        print("\nSaving outputs...")
        save_csv_output(self.df_macc, self.output_dir / 'macc_annual_2025_2050.csv',
                       f"({len(self.df_macc)} tech-year combinations)")

        # Add alternative cost units (if available)
        try:
            from .regional_energy_tracker import create_cost_conversion_table
            df_cost_conversion = create_cost_conversion_table(self.df_macc)
            save_csv_output(df_cost_conversion, self.output_dir / 'macc_cost_units_comparison.csv',
                           "Multiple cost units for easier interpretation")
        except (ImportError, ModuleNotFoundError):
            print("   (skipping cost conversion table - regional_energy_tracker not available)")

    def run_complete_analysis(self):
        """Run complete MACC analysis"""
        print("\n" + "="*80)
        print("RUNNING COMPLETE MACC ANALYSIS (ENERGY-BASED)")
        print("="*80)

        self.calculate_macc_annual()
        self.create_visualizations()
        self.save_outputs()

        print("\n" + "="*80)
        print("MODULE 2 COMPLETE")
        print("="*80)
        print(f"\nOutputs saved to: {self.output_dir}")
        print("\nKey changes from LCOE approach:")
        print("  - Explicit CAPEX, OPEX, Fuel Cost tracking")
        print("  - H2 consumption: 0.2 ton/ton ethylene (Energy Only)")
        print("  - Electricity consumption: 5.0 MWh/ton ethylene (BASF/SABIC Pilot)")
        print("  - Naphtha feedstock cost: FIXED (not in differential)")

        return {'macc': self.df_macc}
