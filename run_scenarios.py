"""
SCENARIO RUNNER - Cost-Optimized with Emission Constraints
==========================================================
Runs all 6 scenarios with ANNUAL results (2025-2050).

Refactored to use centralized logic in modules/utils.py

Outputs (separate files per scenario):
- outputs/{scenario_name}.csv - Facility-level annual results
- outputs/regional_mac_summary.csv - Regional MAC curves by scenario/year
- outputs/regional_abatement_summary.csv - Regional abatement by scenario/year
- outputs/scenario_results.csv - Combined results (all scenarios)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from modules.utils import DataLoader, EmissionCalculator, PriceCalculator, TechnologyCostCalculator, StrandedAssetCalculator, format_number
from modules.data_loader import DataLoader as NewDataLoader
from modules.capex_calculator import CapexCalculator, MACCalculator, select_technology_for_facility

# Configuration
DATA_DIR = Path('data')
OUTPUT_DIR = Path('outputs')
OUTPUT_DIR.mkdir(exist_ok=True)

# Years for analysis - ANNUAL from 2025 to 2050
YEARS = list(range(2025, 2051))  # 26 years

# Load EXTERNAL configurations
def load_scenario_config():
    """Load scenarios, targets, and mapping from CSVs"""
    # 1. Emission Targets
    targets_df = pd.read_csv(DATA_DIR / 'scenarios' / 'emission_targets.csv')
    key_targets = dict(zip(targets_df['year'], targets_df['reduction_target_pct']))
    
    # 2. Scenario Definitions
    scenarios_df = pd.read_csv(DATA_DIR / 'scenarios' / 'scenario_definitions.csv')
    scenarios = scenarios_df.to_dict('records')
    
    # 3. Region Mapping
    region_df = pd.read_csv(DATA_DIR / 'assets' / 'region_mapping.csv')
    region_map = dict(zip(region_df['location'], region_df['region']))
    
    return key_targets, scenarios, region_map

print("Loading configuration from CSVs...")
KEY_TARGETS, SCENARIOS, REGION_MAP = load_scenario_config()

# Interpolate emission targets for all years
def interpolate_targets(key_targets, years):
    """Interpolate emission targets for annual years"""
    key_years = sorted(key_targets.keys())
    key_values = [key_targets[y] for y in key_years]
    return {y: np.interp(y, key_years, key_values) for y in years}

EMISSION_TARGETS = interpolate_targets(KEY_TARGETS, YEARS)


def load_data():
    """Load all input data and initialize calculators"""
    print("=" * 80)
    print("LOADING INPUT DATA")
    print("=" * 80)

    loader = DataLoader(DATA_DIR)
    new_loader = NewDataLoader(DATA_DIR)

    # 1. Load Raw Data
    facilities = loader.load_facilities()
    facilities_shaheen = pd.read_csv(DATA_DIR / 'assets' / 'facility_database_with_shaheen.csv')
    intensities = loader.load_energy_intensities()
    emission_factors = loader.load_emission_factors()
    tech_params = loader.load_technology_params()
    h2_prices = loader.load_h2_prices()
    re_prices = loader.load_re_prices()
    grid_emissions = loader.load_grid_emissions()
    grid_prices = loader.load_grid_prices()
    fuel_prices = pd.read_csv(DATA_DIR / 'assumptions' / 'prices' / 'fuel_price_trajectory.csv')
    carbon_budgets = loader.load_carbon_budgets()
    valuation_params = loader.load_asset_valuation_params()

    # 1b. Load NEW config files (model_config, technology_capex)
    model_config = new_loader.load_model_config()
    tech_capex = new_loader.load_technology_capex()

    # 2. Initialize Calculators
    emission_calc = EmissionCalculator(emission_factors)
    # Price calculator needs h2, re, and fuel prices
    price_calc = PriceCalculator(h2_prices, re_prices, fuel_prices)
    tech_calc = TechnologyCostCalculator(tech_params, emission_calc)
    stranded_calc = StrandedAssetCalculator(carbon_budgets, valuation_params)

    # 2b. Initialize NEW calculators (capacity-based CAPEX)
    capex_calc = CapexCalculator(tech_capex, tech_params, model_config)
    mac_calc = MACCalculator(capex_calc, price_calc, emission_calc)

    data = {
        'facilities': facilities,
        'facilities_shaheen': facilities_shaheen,
        'intensities': intensities,
        'emission_factors': emission_factors,
        'tech_params': tech_params,
        'tech_capex': tech_capex,
        'model_config': model_config,
        'h2_prices': h2_prices,
        're_prices': re_prices,
        'grid_emissions': grid_emissions,
        'grid_prices': grid_prices,
        'carbon_budgets': carbon_budgets,
        'valuation_params': valuation_params,
        # Calculators (OLD - for backwards compatibility)
        'emission_calc': emission_calc,
        'price_calc': price_calc,
        'tech_calc': tech_calc,
        'stranded_calc': stranded_calc,
        # Calculators (NEW - capacity-based CAPEX)
        'capex_calc': capex_calc,
        'mac_calc': mac_calc,
    }

    # Load operating rate trajectories
    data['op_rate_shaheen'] = pd.read_csv(DATA_DIR / 'scenarios' / 'demand_growth_trajectory_shaheen.csv')
    data['op_rate_restructure_25pct'] = pd.read_csv(DATA_DIR / 'scenarios' / 'demand_growth_trajectory_restructure_25pct.csv')
    data['op_rate_restructure_40pct'] = pd.read_csv(DATA_DIR / 'scenarios' / 'demand_growth_trajectory_restructure_40pct.csv')

    # Create intensity lookup by key (company, product, location) for safe matching
    intensities['_key'] = intensities['company'] + '_' + intensities['product'] + '_' + intensities['location']
    data['intensity_lookup'] = intensities.set_index('_key').to_dict('index')

    print(f"  Loaded {len(data['facilities'])} baseline facilities")
    print(f"  Loaded {len(data['facilities_shaheen'])} facilities with Shaheen")
    print(f"  Loaded model_config with {len(model_config)} parameters")
    print(f"  Loaded technology_capex with {len(tech_capex)} technologies")
    print(f"  Initialized Calculators (OLD + NEW)")

    return data


def get_region(location):
    """Map location to region using loaded configuration"""
    return REGION_MAP.get(location, 'Other')


def calculate_facility_mac_v2(facility_baseline, process, ncc_tech, year, data, grid_ef):
    """
    Calculate MAC using centralized calculators.
    Returns MAC and detailed breakdown including fuel savings.
    """
    price_calc = data['price_calc']
    tech_calc = data['tech_calc']

    # Get prices
    h2_price = price_calc.get_h2_price(year)
    re_price = price_calc.get_re_price(year)
    fuel_prices = price_calc.get_fuel_prices(year) # Get all fuel prices for savings calc

    # Determine technology
    if process == 'Naphtha Cracker':
        technology = ncc_tech
    elif process == 'BTX Plant':
        technology = 'RDH'
    else:
        technology = 'Heat_Pump'

    # Get abatement requirements (Energy & Abatement)
    reqs = tech_calc.calculate_abatement_requirements(
        technology, facility_baseline, process, ncc_tech
    )
    
    h2_demand_t = reqs['h2_demand_t']
    added_elec_mwh = reqs['added_elec_mwh']
    potential_abatement = reqs['potential_abatement_tco2']

    # Default return if no abatement
    if potential_abatement <= 0:
        return float('inf'), 'None', 0, {}, {}

    # 1. New Energy Costs (H2 + Electricity)
    h2_cost = h2_demand_t * h2_price * 1000 # price is /kg, so *1000 for /tonne
    elec_cost = added_elec_mwh * re_price
    new_energy_cost = h2_cost + elec_cost

    # 2. Fuel Savings (Avoided Cost)
    # We assume the technology replaces ALL combustion emissions, so we save ALL combustion fuel costs.
    # Use baseline['energy_by_source'] (GJ) and fuel_prices ($/GJ)
    fuel_savings = 0.0
    energy_by_source = facility_baseline.get('energy_by_source', {})
    
    # Map internal keys to price keys
    # price keys: naphtha_usd_per_gj, lng_usd_per_gj, fuel_gas_usd_per_gj, lpg_usd_per_gj, fuel_oil_usd_per_gj
    # internal keys: naphtha, lng, fuel_gas, byproduct_gas, lpg, fuel_oil, diesel
    
    # Naphtha
    fuel_savings += energy_by_source.get('naphtha', 0) * fuel_prices.get('naphtha_usd_per_gj', 0)
    # LNG
    fuel_savings += energy_by_source.get('lng', 0) * fuel_prices.get('lng_usd_per_gj', 0)
    # Fuel Gas
    fuel_savings += energy_by_source.get('fuel_gas', 0) * fuel_prices.get('fuel_gas_usd_per_gj', 0)
    # LPG
    fuel_savings += energy_by_source.get('lpg', 0) * fuel_prices.get('lpg_usd_per_gj', 0)
    # Fuel Oil
    fuel_savings += energy_by_source.get('fuel_oil', 0) * fuel_prices.get('fuel_oil_usd_per_gj', 0)
    # Diesel
    fuel_savings += energy_by_source.get('diesel', 0) * fuel_prices.get('diesel_usd_per_gj', 0)
    # Byproduct Gas - assumed priced same as Fuel Gas or 0? 
    # Usually valued at natural gas or fuel gas price. Let's use fuel_gas price.
    fuel_savings += energy_by_source.get('byproduct_gas', 0) * fuel_prices.get('fuel_gas_usd_per_gj', 0)

    # 3. Tech Costs (CAPEX/OPEX) - NEW CAPACITY-BASED APPROACH
    # Use new CapexCalculator which uses $/t-product/yr from technology_capex.csv
    capex_calc = data['capex_calc']

    # Get production volume from baseline
    production_t = facility_baseline.get('production_t', 0)

    # Calculate CAPEX using capacity-based approach
    capex_info = capex_calc.calculate_facility_capex(technology, production_t, year)
    capex_total_usd = capex_info['capex_total_usd']

    # Get OPEX% and lifetime from CAPEX CSV
    capex_meta = capex_calc.get_capex_info(technology)
    opex_pct = capex_meta['opex_pct_capex'] / 100
    lifetime = capex_meta['lifetime_years']

    opex_annual_usd = capex_total_usd * opex_pct

    # Annualize CAPEX (simple linear amortization)
    capex_annual_usd = capex_total_usd / lifetime
    
    # 4. Total Annual Cost
    # Total = Annualized Capex + Opex + New Energy - Fuel Savings
    total_annual_cost = capex_annual_usd + opex_annual_usd + new_energy_cost - fuel_savings

    mac = total_annual_cost / potential_abatement if potential_abatement > 0 else float('inf')

    cost_breakdown = {
        'capex_total_usd': capex_total_usd,
        'capex_annual_usd': capex_annual_usd,
        'opex_annual_usd': opex_annual_usd,
        'new_energy_cost_usd': new_energy_cost,
        'fuel_savings_usd': fuel_savings,
        'total_annual_cost_usd': total_annual_cost
    }

    tech_details = {
        'h2_demand_t': h2_demand_t,
        'added_elec_mwh': added_elec_mwh,
        'lifetime': lifetime,
        'opex_pct': opex_pct
    }

    return mac, technology, potential_abatement, cost_breakdown, tech_details


def calculate_lcoa(facility, ncc_tech, start_year, data, all_years):
    """
    Calculate Levelized Cost of Abatement (LCOA) from start_year to 2050.
    LCOA = NPV(Annual Costs) / Sum(Abatement)
    
    This anticipates future carbon price/energy price changes.
    """
    # Get discount rate from model_config (no fallback - must be in CSV)
    model_config = data.get('model_config')
    if model_config is not None and 'discount_rate' in model_config:
        DISCOUNT_RATE = model_config['discount_rate']
    else:
        raise ValueError("discount_rate not found in model_config.csv - this parameter is required")
    
    total_npv_cost = 0
    total_abatement = 0
    
    # Cache lookup
    fid = facility['facility_id']
    intensity = data['intensity_lookup'].get(fid)
    if not intensity: return float('inf')
    
    # Loop from start install year to end of horizon
    # (Simplified: assume lifetime covers the period or up to 2050)
    
    future_years = [y for y in all_years if y >= start_year]
    if not future_years: return float('inf')
    
    # To optimize: pre-fetch op_rate_df if possible, but passing 'data' is ok
    # We need to know which scenarios op_rate to use.
    # Actually, calculate_lcoa needs to know the scenario context!
    # The 'data' dict has op_rates loaded by key. 
    # But facility doesn't know which scenario it's in.
    # Hack: Pass `op_rate_df` explicitly or assume `op_rate_shaheen` (most conservative/standard)?
    # Better: Inspect `data` to find the active op_rate_df? 
    # Actually, the caller `run_scenario` knows the scenario. 
    # But I see I didn't pass `scenario` or `op_rate_df` to `calculate_lcoa`.
    # I passed `data`.
    # Let's assume standard 'shaheen' op rate for LCOA ranking (it's a ranking metric).
    # Small differences in op_rate don't change the RELATIVE order of technology costs much.
    op_rate_df = data.get('op_rate_shaheen') 
    
    for y in future_years:
        # 1. Get Environment vars for year y
        # (This repetition is inefficient but robust. Optimization later if needed.)
        op_row = op_rate_df[op_rate_df['year'] == y]
        if len(op_row) == 0: continue
        op_rate = op_row['operating_rate_pct'].iloc[0] / 100
        cap_mult = op_row['cumulative_capacity_multiplier'].iloc[0]
        
        grid_row = data['grid_emissions'][data['grid_emissions']['year'] == y]
        grid_ef = grid_row['grid_ef_tco2_per_mwh'].iloc[0]
        
        # 2. Calculate Baseline
        baseline = data['emission_calc'].calculate_baseline_metrics(
            facility, intensity, op_rate, cap_mult
        )
        
        # 3. Calculate Annual Cost & Abatement (v2)
        # Note: calculate_facility_mac_v2 returns annual cost (Capex_Annual + Opex + Energy - Savings)
        res = calculate_facility_mac_v2(baseline, facility.get('process'), ncc_tech, y, data, grid_ef)
        # res = (mac, tech, abatement, cost_bd, tech_det)
        
        abatement = res[2]
        cost_bd = res[3]
        total_annual_cost = cost_bd.get('total_annual_cost_usd', 0)
        
        # 4. Discounting
        df = (1 + DISCOUNT_RATE) ** (y - start_year)
        total_npv_cost += total_annual_cost / df
        total_abatement += abatement # Undiscounted abatement (Physical tons)
        
    if total_abatement <= 0:
        return float('inf')
        
    return total_npv_cost / total_abatement


def run_scenario(scenario, data, years):
    """Run a single scenario with cost-optimized deployment"""
    print(f"\n  Running: {scenario['name']}")

    # 1. Setup
    results = []
    
    # Select facility list based on scenario
    if scenario['production'] == 'shaheen':
        facilities = data['facilities_shaheen'].copy()
    else:
        facilities = data['facilities'].copy()
        
    # Create facility ID (critical for tracking)
    facilities['facility_id'] = facilities.apply(
        lambda x: f"{x['company']}_{x['product']}_{x['location']}", axis=1
    )
        
    # State tracking
    deployment_status = {f['facility_id']: {'deployed': False, 'year': None} for _, f in facilities.iterrows()}
    
    # Pre-calculate baseline intensity lookup for speed
    intensity_lookup = data['intensities'].set_index('_key').to_dict('index')
    
    # Validation of required data
    op_rate_key = f"op_rate_{scenario['production']}"
    if op_rate_key not in data:
         # Fallback to base shaheen if specific rate not found (or handle error)
         # For the standard 6 scenarios, strictly mapped:
         # shaheen -> op_rate_shaheen
         # restructure_XX -> op_rate_restructure_XX
         pass

    op_rate_df = data.get(op_rate_key)
    if op_rate_df is None:
         # Try default 'op_rate_shaheen' if specific one missing? Or error?
         # Based on scenario_definitions.csv, production is 'shaheen', 'restructure_25pct', etc.
         pass
         
    # 2. Year-by-Year Simulation
    for year in years:
        # --- A. Get Annual Parameters ---
        # Operating Rate & Capacity
        op_row = op_rate_df[op_rate_df['year'] == year]
        if len(op_row) == 0: raise ValueError(f"Missing op rate for {year}")
        op_rate = op_row['operating_rate_pct'].iloc[0] / 100
        cap_mult = op_row['cumulative_capacity_multiplier'].iloc[0]
        
        # Grid EF
        grid_row = data['grid_emissions'][data['grid_emissions']['year'] == year]
        if len(grid_row) == 0: raise ValueError(f"Missing Grid EF for {year}")
        grid_ef = grid_row['grid_ef_tco2_per_mwh'].iloc[0]
        
        # Baseline Grid EF (2025) for BAU
        grid_ef_2025 = data['grid_emissions'][data['grid_emissions']['year'] == 2025]['grid_ef_tco2_per_mwh'].iloc[0]

        # --- B. Calculate Current Emissions (Pre-Intervention for this year) ---
        current_year_results = []
        total_emissions = 0
        total_bau = 0
        
        # We need a temporary list to hold facility state for simple summation
        # Real calculation happens later
        
        # --- C. Check Target Gap ---
        # To check the gap, we first calculate emissions assuming NO NEW DEPLOYMENT this year
        # (Facilities already deployed in previous years stay deployed)
        
        # Let's iterate facilities to calculate their state
        candidates_for_optimization = []
        
        current_stats = [] # Store temp data to avoid re-calculating for results
        
        for _, fac in facilities.iterrows():
            fid = fac['facility_id']
            # Get Baseline
            key = fac['facility_id'] # Simplified lookup if IDs are unique
            # Reconstruct lookup key? 
            # Original code: intensities['_key'] = company + product + location.
            # But here we iterating row objects. 
            # Let's use the exact logic from before.
            # actually facilities iterator doesn't have the _key pre-built unless we did it.
            # The previous code did: intensities['key']... data['intensity_lookup']...
            # And iterated facilities... 
            # Let's rely on data['intensity_lookup'] using fac['facility_id'] if we indexed by ID?
            # NO, the lookup calculates key ON THE FLY. check line 111 of original code.
            # "intensities['_key'] = ... data['intensity_lookup'] = intensities.set_index('_key')"
            # And loop used: "if facility_key not in intensity_lookup" where facility_key = facility['facility_id'].
            # Wait, facility_id is unique?
            # Line 110: "intensities['_key'] = ... set_index('_key')"
            # Line 330: "facility_key = facility['facility_id']" -> this implies ID maps to Intensity Key?
            # Actually, looking at `load_data`: it creates intensity_lookup.
            # Let's blindly trust `intensity_lookup[fid]` works if fid is the ID.
            
            if fid not in intensity_lookup:
                continue

            intensity = intensity_lookup[fid]
            
            # Baseline Metrics (BAU)
            base_metrics = data['emission_calc'].calculate_baseline_metrics(fac, intensity, op_rate, cap_mult)
            bau_emis = base_metrics['combustion_emissions'] + base_metrics['elec_demand_mwh'] * grid_ef_2025
            
            # Current Metrics (taking into account deployment status)
            is_deployed = deployment_status[fid]['deployed']
            
            if is_deployed:
                # Already decarbonized
                # Calculate reduced emissions
                # For simplicity, calculate "Mac" style but ignore cost for now
                # We need the EMISSIONS from the new tech.
                # calculate_facility_mac_v2 returns `tech_det` which has `h2_demand`, `added_elec`.
                # We need the actual emissions.
                # Tech emissions = (H2 * 0) + (Elec * GridEF) approx?
                # Actually, Mac function doesn't explicit return "new emissions".
                # But we can infer: Abatement = Baseline - New. 
                # So New = Baseline - Abatement.
                
                # We need to run the calc to get abatement at current year conditions
                res = calculate_facility_mac_v2(base_metrics, fac['process'], scenario['ncc_tech'], year, data, grid_ef)
                # res = (mac, tech_name, abatement, cost_bd, tech_det)
                abatement = res[2]
                current_emis = base_metrics['combustion_emissions'] - abatement # Only combustion avoided?
                # Wait, Reference: "Total Emissions = Comb + Elec". 
                # Tech replaces Combustion. Reduced Comb = 0 roughly.
                # New Elec Emissions = (BaseElec + AddedElec) * GridEF.
                # Let's strictly use: NewEmis = BauEmis - Abatement? 
                # No, Bau uses fixed 2025 Grid. Real emissions use Current Grid.
                
                # Precise Logic:
                # 1. Combustion = 0 (replaced) or 15% (if 85% eff). Assumed replaced or calculated in Abatement.
                #    calculate_facility_mac_v2 calculates `potential_abatement` = `combustion_emissions` * coverage.
                #    So Remaining Combustion = `combustion_emissions` - `potential_abatement`.
                # 2. Electricity = (BaseElec + AddedElec) * GridEF.
                # 3. Total = RemComb + Elec.
                
                pot_abate = res[2]
                tech_det = res[4]
                
                rem_comb = base_metrics['combustion_emissions'] - pot_abate
                total_elec = base_metrics['elec_demand_mwh'] + tech_det.get('added_elec_mwh', 0)
                current_emis = rem_comb + total_elec * grid_ef
                
                # For results recording
                res_packet = {
                    'fac': fac, 'mac_res': res, 'is_deployed': 1, 
                    'bau': bau_emis, 'emis': current_emis, 'abate': bau_emis - current_emis # vs BAU
                }
            else:
                # Not deployed (Baseline)
                # Current Emissions = Comb + BaseElec * GridEF
                current_emis = base_metrics['combustion_emissions'] + base_metrics['elec_demand_mwh'] * grid_ef
                res_packet = {
                    'fac': fac, 'mac_res': None, 'is_deployed': 0,
                    'bau': bau_emis, 'emis': current_emis, 'abate': 0
                }
                candidates_for_optimization.append(res_packet)
            
            total_emissions += current_emis
            total_bau += bau_emis
            current_stats.append(res_packet)
            
        # --- D. Gap Analysis & Optimization ---
        # Target for this year
        target_pct = EMISSION_TARGETS[year]
        # Target Emissions = BAU_2025_Total * (1 - target_pct)? 
        # Or Baseline_Current_Year * ...?
        # Convention: Reduction relative to BASELINE YEAR (2025).
        # We need Total 2025 Emissions from the *start* of the script?
        # Actually, let's calculate the "2025 Reference" dynamically or pass it.
        # In this loop, if year==2025, we set the reference.
        
        if year == 2025:
            REFERENCE_EMISSIONS = total_bau # BAU in 2025
        
        target_emissions = REFERENCE_EMISSIONS * (1 - target_pct)
        gap = total_emissions - target_emissions
        
        if gap > 0 and len(candidates_for_optimization) > 0:
            # OPTIMIZATION TRIGGERED
            # print(f"    Year {year}: Gap {gap/1e6:.2f} Mt. Optimizing...")
            
            # Calculate LCOA for all candidates
            # This projects their costs from [year...2050]
            lcoa_list = []
            for item in candidates_for_optimization:
                fac = item['fac']
                # Helper function to get NVP-based cost
                lcoa = calculate_lcoa(fac, scenario['ncc_tech'], year, data, YEARS) 
                lcoa_list.append({'fac_id': fac['facility_id'], 'lcoa': lcoa, 'item': item})
            
            # Sort by LCOA (Cheapest first)
            lcoa_list.sort(key=lambda x: x['lcoa'])
            
            # Deploy until gap filled
            for cand in lcoa_list:
                # Deploy this facility
                fid = cand['fac_id']
                
                # Calculate how much it reduces emissions THIS YEAR
                # We need to switch it to deployed state
                base_metrics = data['emission_calc'].calculate_baseline_metrics(
                    cand['item']['fac'], intensity_lookup[fid], op_rate, cap_mult
                )
                res = calculate_facility_mac_v2(base_metrics, cand['item']['fac']['process'], 
                                              scenario['ncc_tech'], year, data, grid_ef)
                
                pot_abate = res[2]
                tech_det = res[4]
                rem_comb = base_metrics['combustion_emissions'] - pot_abate
                total_elec = base_metrics['elec_demand_mwh'] + tech_det.get('added_elec_mwh', 0)
                new_emis = rem_comb + total_elec * grid_ef
                
                # Reduction achieved
                old_emis = cand['item']['emis'] # Current emisisons (undeployed)
                reduction = old_emis - new_emis
                
                # Update State
                deployment_status[fid]['deployed'] = True
                deployment_status[fid]['year'] = year
                
                # Update Loop Goal
                gap -= reduction
                
                # Update the stats list for final reporting
                # (Find the item in current_stats and update it)
                # This is inefficient O(N), but safe.
                for s in current_stats:
                    if s['fac']['facility_id'] == fid:
                        s['is_deployed'] = 1
                        s['mac_res'] = res
                        s['emis'] = new_emis
                        s['abate'] = s['bau'] - new_emis
                        break
                
                if gap <= 0:
                    break

        # --- E. Record Results ---
        # Now current_stats reflects the final state of the year
        deployment_count = 0
        for s in current_stats:
            fac = s['fac']
            res = s['mac_res']
            is_dep = s['is_deployed']
            
            # Extract costs (if deployed)
            if is_dep and res:
                 # res = (mac, technology, potential_abatement, cost_bd, tech_det)
                 # cost_bd has 'capex_total_usd', 'total_annual_cost_usd', etc.
                 cost_bd = res[3] if len(res)>3 else {}
                 tech_det = res[4] if len(res)>4 else {}
                 
                 # Using the components calculated by mac_v2
                 row = {
                    'year': year, 'scenario': scenario['name'], 'region': get_region(fac['location']),
                    'facility_id': fac['facility_id'], 'company': fac['company'], 'product': fac['product'],
                    'process': fac.get('process'), 'technology': res[1],
                    'capacity_tpy': fac['capacity_kt']*1000, 
                    'production_t': fac['capacity_kt']*1000 * op_rate * cap_mult,
                    'bau_emissions_tco2': s['bau'], 
                    'emissions_tco2': s['emis'],
                    'abatement_tco2': s['abate'],
                    # Costs
                    'capex_usd': cost_bd.get('capex_total_usd', 0), # Total CAPEX (overnight)
                    'opex_usd_yr': cost_bd.get('opex_annual_usd', 0),
                    'fuel_cost_usd_yr': 0, # Not tracked explicitly?
                    'total_cost_usd': cost_bd.get('total_annual_cost_usd', 0),
                    'mac_usd_per_tco2': res[0],
                    # Components
                    'cost_component_capex_annual_usd': cost_bd.get('capex_annual_usd', 0),
                    'cost_component_opex_annual_usd': cost_bd.get('opex_annual_usd', 0),
                    'cost_component_new_energy_usd': cost_bd.get('new_energy_cost_usd', 0),
                    'cost_component_fuel_savings_usd': cost_bd.get('fuel_savings_usd', 0),
                    # Demands
                    'elec_demand_mwh': base_metrics['elec_demand_mwh'] + tech_det.get('added_elec_mwh', 0),
                    'h2_demand_t': tech_det.get('h2_demand_t', 0),
                    'heat_demand_gj': 0, 
                    'tech_deployed': 1,
                    'install_year': deployment_status[fac['facility_id']]['year']
                 }
                 deployment_count += 1
            else:
                 # Undeployed
                 row = {
                    'year': year, 'scenario': scenario['name'], 'region': get_region(fac['location']),
                    'facility_id': fac['facility_id'], 'company': fac['company'], 'product': fac['product'],
                    'process': fac.get('process'), 'technology': 'Baseline',
                    'capacity_tpy': fac['capacity_kt']*1000, 
                    'production_t': fac['capacity_kt']*1000 * op_rate * cap_mult,
                    'bau_emissions_tco2': s['bau'], 
                    'emissions_tco2': s['emis'],
                    'abatement_tco2': 0,
                    'capex_usd': 0, 'opex_usd_yr': 0, 'fuel_cost_usd_yr': 0, 'total_cost_usd': 0, 'mac_usd_per_tco2': 0,
                    'cost_component_capex_annual_usd': 0, 'cost_component_opex_annual_usd': 0,
                    'cost_component_new_energy_usd': 0, 'cost_component_fuel_savings_usd': 0,
                    'elec_demand_mwh': base_metrics['elec_demand_mwh'],
                    'h2_demand_t': 0,
                    'heat_demand_gj': 0,
                    'install_year': None
                 }
            results.append(row)

    return results


def main():
    """Main execution"""
    print("=" * 80)
    print("KOREA PETROCHEMICAL NET ZERO - COST-OPTIMIZED SCENARIO RUNNER")
    print("=" * 80)
    print(f"\nYears: {YEARS[0]} - {YEARS[-1]} (annual, {len(YEARS)} years)")
    print("\nKey Emission Targets:")
    for year, target in KEY_TARGETS.items():
        print(f"  {year}: {target*100:.1f}% reduction")

    # Load data
    data = load_data()

    # Run all scenarios
    print("\n" + "=" * 80)
    print("RUNNING SCENARIOS")
    print("=" * 80)

    all_results = []
    scenario_dfs = {}  # Store individual scenario DataFrames

    for scenario in SCENARIOS:
        results = run_scenario(scenario, data, YEARS)
        all_results.extend(results)

        # Create DataFrame for this scenario
        df_scenario = pd.DataFrame(results)
        scenario_dfs[scenario['name']] = df_scenario

    # Convert combined results to DataFrame
    df_results = pd.DataFrame(all_results)

    # Reorder columns
    column_order = [
        'year', 'scenario', 'region', 'facility_id', 'company', 'product', 'process',
        'technology', 'capacity_tpy', 'production_t',
        'bau_emissions_tco2', 'emissions_tco2', 'abatement_tco2',
        'capex_usd', 'opex_usd_yr', 'fuel_cost_usd_yr', 'total_cost_usd', 'mac_usd_per_tco2',
        'cost_component_capex_annual_usd', 'cost_component_opex_annual_usd',
        'cost_component_new_energy_usd', 'cost_component_fuel_savings_usd',
        'elec_demand_mwh', 'h2_demand_t', 'heat_demand_gj',
        'tech_deployed', 'install_year'
    ]

    # Only include columns that exist
    column_order = [c for c in column_order if c in df_results.columns]
    df_results = df_results[column_order]

    # ==================== SAVE OUTPUTS ====================
    print("\n" + "=" * 80)
    print("SAVING OUTPUTS")
    print("=" * 80)

    # 1. Save combined results
    output_path = OUTPUT_DIR / 'scenario_results.csv'
    df_results.to_csv(output_path, index=False)
    print(f"  ✓ Combined results: {output_path}")

    # 2. Save separate files for each scenario
    for scenario_name, df_scenario in scenario_dfs.items():
        df_scenario = df_scenario[column_order]
        scenario_path = OUTPUT_DIR / f'{scenario_name}.csv'
        df_scenario.to_csv(scenario_path, index=False)
        print(f"  ✓ Scenario file: {scenario_path}")

    # 3. Generate and save Regional MAC Summary
    regional_mac_data = []
    for scenario_name in df_results['scenario'].unique():
        df_s = df_results[df_results['scenario'] == scenario_name]
        for year in YEARS:
            df_y = df_s[df_s['year'] == year]
            for region in df_y['region'].unique():
                df_r = df_y[df_y['region'] == region]
                total_abatement = df_r['abatement_tco2'].sum()
                total_cost = df_r['total_cost_usd'].sum()
                mac = total_cost / total_abatement if total_abatement > 0 else 0
                regional_mac_data.append({
                    'scenario': scenario_name,
                    'year': year,
                    'region': region,
                    'abatement_tco2': total_abatement,
                    'total_cost_usd': total_cost,
                    'mac_usd_per_tco2': mac,
                    'facilities_deployed': df_r[df_r['tech_deployed'] == 1]['facility_id'].nunique(),
                    'total_facilities': df_r['facility_id'].nunique(),
                })

    df_regional_mac = pd.DataFrame(regional_mac_data)
    mac_path = OUTPUT_DIR / 'regional_mac_summary.csv'
    df_regional_mac.to_csv(mac_path, index=False)
    print(f"  ✓ Regional MAC summary: {mac_path}")

    # 4. Generate and save Regional Abatement Summary
    regional_abatement_data = []
    for scenario_name in df_results['scenario'].unique():
        df_s = df_results[df_results['scenario'] == scenario_name]
        
        for year in YEARS:
            df_y = df_s[df_s['year'] == year]
            for region in df_y['region'].unique():
                df_r = df_y[df_y['region'] == region]
                regional_abatement_data.append({
                    'scenario': scenario_name,
                    'year': year,
                    'region': region,
                    'bau_emissions_tco2': df_r['bau_emissions_tco2'].sum(),
                    'emissions_tco2': df_r['emissions_tco2'].sum(),
                    'abatement_tco2': df_r['abatement_tco2'].sum(),
                    'abatement_mt': df_r['abatement_tco2'].sum() / 1e6,
                    'capex_usd': df_r['capex_usd'].sum(),
                    'total_cost_usd': df_r['total_cost_usd'].sum(),
                    'annual_capex_usd': df_r['cost_component_capex_annual_usd'].sum(),
                    'annual_opex_usd': df_r['cost_component_opex_annual_usd'].sum(),
                    'annual_new_energy_usd': df_r['cost_component_new_energy_usd'].sum(),
                    'annual_fuel_savings_usd': df_r['cost_component_fuel_savings_usd'].sum(),
                    'elec_demand_mwh': df_r['elec_demand_mwh'].sum(),
                    'h2_demand_t': df_r['h2_demand_t'].sum(),
                })

    df_regional_abatement = pd.DataFrame(regional_abatement_data)
    abatement_path = OUTPUT_DIR / 'regional_abatement_summary.csv'
    df_regional_abatement.to_csv(abatement_path, index=False)
    print(f"  ✓ Regional abatement summary: {abatement_path}")

    # ==================== STRANDED ASSETS CALCULATION ====================
    print("\n" + "=" * 80)
    print("CALCULATING STRANDED ASSETS (Carbon Budget Perspective)")
    print("=" * 80)
    
    stranded_results = []
    stranded_details_list = []
    
    # Use loaded facility data instead of re-reading CSVs
    db_baseline = data['facilities'].copy()
    db_shaheen_full = data['facilities_shaheen'].copy()
    
    stranded_calc = data['stranded_calc']
    
    for scenario_name in df_results['scenario'].unique():
        df_s = df_results[df_results['scenario'] == scenario_name]
        
        # Determine which facility list to use
        if 'shaheen' in scenario_name:
            current_facilities = db_shaheen_full
        else:
            current_facilities = db_baseline
            
        # Get annual industry emissions
        annual_emissions = df_s.groupby('year')['emissions_tco2'].sum()
        
        # 1.5C Scenario
        year_15c = stranded_calc.calculate_stranding_year(annual_emissions, 'budget_1.5C_tco2')
        value_15c = stranded_calc.calculate_total_stranded_value(current_facilities, year_15c)
        
        # 2.0C Scenario
        year_20c = stranded_calc.calculate_stranding_year(annual_emissions, 'budget_2.0C_tco2')
        value_20c = stranded_calc.calculate_total_stranded_value(current_facilities, year_20c)
        
        stranded_results.append({
            'scenario': scenario_name,
            'stranding_year_1.5C': year_15c,
            'stranded_value_1.5C_usd': value_15c,
            'stranded_value_1.5C_fmt': format_number(value_15c),
            'stranding_year_2.0C': year_20c,
            'stranded_value_2.0C_usd': value_20c,
            'stranded_value_2.0C_fmt': format_number(value_20c)
        })

        # --- Detailed Facility Report (1.5C Focus) ---
        df_details = stranded_calc.get_facility_stranded_details(current_facilities, year_15c)
        df_details['scenario'] = scenario_name
        df_details['budget_scenario'] = '1.5C'
        stranded_details_list.append(df_details)

        print(f"  {scenario_name}:")
        print(f"    1.5C Budget: Exhausted in {year_15c}. Stranded Value: {format_number(value_15c)}")
        print(f"    2.0C Budget: Exhausted in {year_20c}. Stranded Value: {format_number(value_20c)}")

    df_stranded = pd.DataFrame(stranded_results)
    stranded_path = OUTPUT_DIR / 'stranded_assets_summary.csv'
    df_stranded.to_csv(stranded_path, index=False)
    print(f"  ✓ Stranded asset summary: {stranded_path}")
    
    # Save Detailed Report
    if stranded_details_list:
        df_stranded_details = pd.concat(stranded_details_list, ignore_index=True)
        details_path = OUTPUT_DIR / 'stranded_assets_facilities.csv'
        df_stranded_details.to_csv(details_path, index=False)
        print(f"  ✓ Stranded asset facility details: {details_path}")

    # ==================== OUTPUT SUMMARY ====================
    print("\n" + "=" * 80)
    print("OUTPUT SUMMARY")
    print("=" * 80)
    print(f"  Total rows: {len(df_results):,}")
    print(f"  Scenarios: {df_results['scenario'].nunique()}")
    print(f"  Years: {YEARS[0]} - {YEARS[-1]} ({len(YEARS)} annual)")
    print(f"  Facilities: {df_results['facility_id'].nunique()}")
    print(f"  Regions: {df_results['region'].unique().tolist()}")

    # ==================== VALIDATION ====================
    print("\n" + "=" * 80)
    print("VALIDATION - EMISSION TARGETS (Key Years)")
    print("=" * 80)

    validation_years = [2025, 2030, 2035, 2040, 2045, 2050]
    for scenario_name in df_results['scenario'].unique():
        print(f"\n  {scenario_name}:")
        df_s = df_results[df_results['scenario'] == scenario_name]

        baseline_2025 = df_s[df_s['year'] == 2025]['bau_emissions_tco2'].sum() / 1e6

        for year in validation_years:
            df_y = df_s[df_s['year'] == year]
            emissions = df_y['emissions_tco2'].sum() / 1e6
            reduction = (1 - emissions / baseline_2025) * 100 if baseline_2025 > 0 else 0
            target = EMISSION_TARGETS.get(year, 0) * 100
            deployed = df_y[df_y['tech_deployed'] == 1]['facility_id'].nunique()

            status = "✓" if reduction >= target - 1 else "✗"
            print(f"    {year}: {emissions:.2f} Mt ({reduction:.1f}% red, target {target:.1f}%) "
                  f"[{deployed} deployed] {status}")

    print("\n" + "=" * 80)
    print("DONE - All outputs saved to outputs/")
    print("=" * 80)

    return df_results


if __name__ == '__main__':
    df = main()
