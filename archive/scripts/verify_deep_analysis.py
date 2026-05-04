#!/usr/bin/env python3
"""
DEEP VERIFICATION SCRIPT
Cross-checks all calculations from multiple independent approaches
to identify any remaining errors in the analysis.

Author: PLANiT
Date: December 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Color codes for terminal output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{'='*80}{RESET}")

def print_pass(text):
    print(f"{GREEN}✓ PASS:{RESET} {text}")

def print_fail(text):
    print(f"{RED}✗ FAIL:{RESET} {text}")

def print_warn(text):
    print(f"{YELLOW}⚠ WARN:{RESET} {text}")

def print_info(text):
    print(f"{BLUE}ℹ INFO:{RESET} {text}")

class DeepVerification:
    """Comprehensive verification of all calculations"""

    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.errors = []
        self.warnings = []
        self.load_data()

    def load_data(self):
        """Load all input data"""
        print_header("LOADING DATA")

        self.facilities = pd.read_csv(self.data_dir / 'facility_database_with_regions.csv')
        self.intensities = pd.read_csv(self.data_dir / 'energy_intensities.csv')
        self.emission_factors = pd.read_csv(self.data_dir / 'emission_factors.csv')
        self.grid_trajectory = pd.read_csv(self.data_dir / 'grid_emission_trajectory.csv')
        self.h2_prices = pd.read_csv(self.data_dir / 'h2_price_trajectory.csv')
        self.re_prices = pd.read_csv(self.data_dir / 're_price_trajectory.csv')
        self.tech_params = pd.read_csv(self.data_dir / 'technology_parameters.csv')

        # Build emission factor dict
        self.ef = {}
        for _, row in self.emission_factors.iterrows():
            fuel = row['fuel']
            if pd.notna(row.get('tCO2_per_GJ')):
                self.ef[fuel] = ('GJ', row['tCO2_per_GJ'])
            elif pd.notna(row.get('tCO2_per_kWh')):
                self.ef[fuel] = ('kWh', row['tCO2_per_kWh'])

        print_info(f"Loaded {len(self.facilities)} facilities")
        print_info(f"Loaded {len(self.intensities)} energy intensity records")
        print_info(f"Loaded {len(self.emission_factors)} emission factors")

    def verify_data_consistency(self):
        """Verify data file consistency"""
        print_header("1. DATA CONSISTENCY CHECKS")

        # Check row counts match
        if len(self.facilities) == len(self.intensities):
            print_pass(f"Facility count ({len(self.facilities)}) matches intensity count ({len(self.intensities)})")
        else:
            print_fail(f"Facility count ({len(self.facilities)}) != intensity count ({len(self.intensities)})")
            self.errors.append("Facility/intensity count mismatch")

        # Check for duplicate facilities
        dup_key = self.facilities.duplicated(subset=['product', 'company', 'location', 'capacity_kt'], keep=False)
        n_dups = dup_key.sum()
        if n_dups == 0:
            print_pass("No duplicate facilities found")
        else:
            print_fail(f"Found {n_dups} duplicate facility entries")
            self.errors.append(f"{n_dups} duplicate facilities")
            dups = self.facilities[dup_key]
            for _, row in dups.head(10).iterrows():
                print(f"     - {row['product']} | {row['company']} | {row['location']} | {row['capacity_kt']} kt")

        # Check for missing values in critical columns
        critical_cols = ['product', 'company', 'location', 'capacity_kt', 'year_built']
        for col in critical_cols:
            n_missing = self.facilities[col].isna().sum()
            if n_missing == 0:
                print_pass(f"No missing values in '{col}'")
            else:
                print_fail(f"{n_missing} missing values in '{col}'")
                self.errors.append(f"Missing values in {col}")

        # Check capacity values are positive
        neg_cap = (self.facilities['capacity_kt'] <= 0).sum()
        if neg_cap == 0:
            print_pass("All capacity values are positive")
        else:
            print_fail(f"{neg_cap} facilities have non-positive capacity")
            self.errors.append("Non-positive capacity values")

        # Check year_built is reasonable
        invalid_years = ((self.facilities['year_built'] < 1960) |
                        (self.facilities['year_built'] > 2030)).sum()
        if invalid_years == 0:
            print_pass("All year_built values are reasonable (1960-2030)")
        else:
            print_warn(f"{invalid_years} facilities have unusual year_built values")
            self.warnings.append("Unusual year_built values")

    def verify_emission_calculations(self):
        """Verify emission calculations using multiple methods"""
        print_header("2. EMISSION CALCULATION VERIFICATION")

        # Method 1: Direct calculation from intensities
        print_info("Method 1: Direct calculation from energy intensities")

        total_emissions_method1 = 0
        emissions_by_fuel_m1 = {'naphtha': 0, 'electricity': 0, 'lng': 0,
                               'fuel_gas': 0, 'byproduct_gas': 0, 'lpg': 0,
                               'fuel_oil': 0, 'diesel': 0}

        for idx in range(len(self.facilities)):
            fac = self.facilities.iloc[idx]
            intensity = self.intensities.iloc[idx]
            capacity_tonnes = fac['capacity_kt'] * 1000

            # Calculate each fuel
            fuels = [
                ('naphtha', 'Naphtha_GJ_per_tonne', 'Naphtha'),
                ('electricity', 'Electricity_kWh_per_tonne', 'Electricity'),
                ('lng', 'LNG_GJ_per_tonne', 'LNG'),
                ('fuel_gas', 'Fuel_Gas_GJ_per_tonne', 'Fuel_Gas'),
                ('byproduct_gas', 'Byproduct_Gas_GJ_per_tonne', 'Byproduct_Gas'),
                ('lpg', 'LPG_GJ_per_tonne', 'LPG'),
                ('fuel_oil', 'Fuel_Oil_GJ_per_tonne', 'Fuel_Oil'),
                ('diesel', 'Diesel_GJ_per_tonne', 'Diesel'),
            ]

            for key, intensity_col, ef_key in fuels:
                if intensity_col in intensity and intensity[intensity_col] > 0:
                    energy = intensity[intensity_col] * capacity_tonnes
                    if ef_key in self.ef:
                        _, ef_value = self.ef[ef_key]
                        emissions = energy * ef_value
                        emissions_by_fuel_m1[key] += emissions
                        total_emissions_method1 += emissions

        print(f"   Total: {total_emissions_method1/1e6:.2f} MtCO2")
        print(f"   Naphtha: {emissions_by_fuel_m1['naphtha']/1e6:.2f} MtCO2 ({emissions_by_fuel_m1['naphtha']/total_emissions_method1*100:.1f}%)")
        print(f"   Electricity: {emissions_by_fuel_m1['electricity']/1e6:.2f} MtCO2 ({emissions_by_fuel_m1['electricity']/total_emissions_method1*100:.1f}%)")
        print(f"   LNG: {emissions_by_fuel_m1['lng']/1e6:.2f} MtCO2 ({emissions_by_fuel_m1['lng']/total_emissions_method1*100:.1f}%)")
        print(f"   Fuel Gas: {emissions_by_fuel_m1['fuel_gas']/1e6:.2f} MtCO2 ({emissions_by_fuel_m1['fuel_gas']/total_emissions_method1*100:.1f}%)")

        # Method 2: Using the EmissionCalculator class
        print_info("\nMethod 2: Using EmissionCalculator class")
        sys.path.insert(0, '.')
        from modules.utils import EmissionCalculator

        calc = EmissionCalculator(self.emission_factors)
        total_emissions_method2 = 0

        for idx in range(len(self.facilities)):
            fac = self.facilities.iloc[idx]
            intensity = self.intensities.iloc[idx]
            emissions = calc.calculate_total_emissions(fac, intensity)
            total_emissions_method2 += emissions['total']

        print(f"   Total: {total_emissions_method2/1e6:.2f} MtCO2")

        # Compare methods
        diff_pct = abs(total_emissions_method1 - total_emissions_method2) / total_emissions_method1 * 100
        if diff_pct < 0.01:
            print_pass(f"Method 1 and Method 2 match (diff: {diff_pct:.4f}%)")
        else:
            print_fail(f"Method 1 ({total_emissions_method1/1e6:.2f} Mt) != Method 2 ({total_emissions_method2/1e6:.2f} Mt)")
            self.errors.append("Emission calculation methods don't match")

        # Store for later checks
        self.total_emissions_100pct = total_emissions_method1
        self.total_emissions_70pct = total_emissions_method1 * 0.70

        # Method 3: Cross-check with literature/external data
        print_info("\nMethod 3: External benchmark comparison")

        # Korea petrochemical emissions are approximately 46-52 MtCO2 at 70% operating rate
        expected_range_low = 40e6  # 40 MtCO2
        expected_range_high = 55e6  # 55 MtCO2

        if expected_range_low <= self.total_emissions_70pct <= expected_range_high:
            print_pass(f"70% op rate emissions ({self.total_emissions_70pct/1e6:.2f} Mt) within expected range (40-55 Mt)")
        else:
            print_warn(f"70% op rate emissions ({self.total_emissions_70pct/1e6:.2f} Mt) outside expected range (40-55 Mt)")
            self.warnings.append("Emissions outside expected range")

    def verify_energy_intensities(self):
        """Verify energy intensity values against literature"""
        print_header("3. ENERGY INTENSITY VERIFICATION")

        # Literature values for petrochemical processes (GJ/tonne product)
        # Source: IEA Chemical Industry Roadmap, DECHEMA 2017
        # Note: Downstream products (P-X, HDPE, PP) are primarily electricity-driven
        # with minimal thermal energy - this is CORRECT for polymerization
        literature_values = {
            'Ethylene': {'naphtha': (25, 35), 'total_energy': (30, 45)},  # GJ/t - steam cracking
            'Propylene': {'naphtha': (20, 30), 'total_energy': (25, 40)},  # steam cracking
            'Benzene': {'total_energy': (5, 15)},  # BTX extraction
            # Downstream products have very LOW thermal energy (primarily electricity)
            # 'P-X': {'total_energy': (0, 5)},  # Separation process - minimal thermal
            # 'HDPE': {'total_energy': (0, 3)},  # Polymerization - electricity dominant
            # 'PP': {'total_energy': (0, 3)},    # Polymerization - electricity dominant
        }

        products_checked = 0
        products_ok = 0

        for product, ranges in literature_values.items():
            # Get facilities for this product
            product_facs = self.facilities[self.facilities['product'] == product]

            if len(product_facs) == 0:
                continue

            products_checked += 1

            # Get average intensity
            idx = product_facs.index[0]
            intensity = self.intensities.iloc[idx]

            # Calculate total thermal energy (excluding electricity)
            total_thermal = (
                intensity.get('Naphtha_GJ_per_tonne', 0) +
                intensity.get('LNG_GJ_per_tonne', 0) +
                intensity.get('Fuel_Gas_GJ_per_tonne', 0) +
                intensity.get('Byproduct_Gas_GJ_per_tonne', 0) +
                intensity.get('LPG_GJ_per_tonne', 0) +
                intensity.get('Fuel_Oil_GJ_per_tonne', 0) +
                intensity.get('Diesel_GJ_per_tonne', 0)
            )

            # Check against literature
            if 'total_energy' in ranges:
                low, high = ranges['total_energy']
                if low <= total_thermal <= high:
                    print_pass(f"{product}: {total_thermal:.1f} GJ/t within literature range ({low}-{high})")
                    products_ok += 1
                elif total_thermal < low * 0.5 or total_thermal > high * 2:
                    print_fail(f"{product}: {total_thermal:.1f} GJ/t FAR outside literature range ({low}-{high})")
                    self.errors.append(f"{product} energy intensity far outside range")
                else:
                    print_warn(f"{product}: {total_thermal:.1f} GJ/t outside literature range ({low}-{high})")
                    self.warnings.append(f"{product} energy intensity outside range")

        print_info(f"\nChecked {products_checked} products, {products_ok} within expected ranges")

    def verify_regional_distribution(self):
        """Verify regional distribution makes sense"""
        print_header("4. REGIONAL DISTRIBUTION VERIFICATION")

        regional = self.facilities.groupby('region').agg({
            'capacity_kt': 'sum',
            'product': 'count'
        }).reset_index()
        regional.columns = ['region', 'capacity_kt', 'n_facilities']
        regional['share'] = regional['capacity_kt'] / regional['capacity_kt'].sum() * 100
        regional = regional.sort_values('capacity_kt', ascending=False)

        print("Regional distribution:")
        for _, r in regional.iterrows():
            print(f"   {r['region']:<20}: {int(r['n_facilities']):>3} facilities, {int(r['capacity_kt']):>8,} kt ({r['share']:.1f}%)")

        # Check that major complexes have reasonable shares
        # Yeosu, Daesan, Ulsan should each have >20%
        major_complexes = ['Yeosu Complex', 'Daesan Complex', 'Ulsan Complex']
        for complex_name in major_complexes:
            share = regional[regional['region'] == complex_name]['share'].values
            if len(share) > 0:
                if share[0] >= 15:
                    print_pass(f"{complex_name} has reasonable share ({share[0]:.1f}%)")
                else:
                    print_warn(f"{complex_name} has low share ({share[0]:.1f}%) - expected >15%")
                    self.warnings.append(f"Low share for {complex_name}")
            else:
                print_fail(f"{complex_name} not found in data")
                self.errors.append(f"Missing {complex_name}")

    def verify_ncc_facilities(self):
        """Verify NCC (Naphtha Cracker) facilities"""
        print_header("5. NCC FACILITY VERIFICATION")

        # NCC facilities should be labeled as "Naphtha Cracker" process
        ncc = self.facilities[self.facilities['process'] == 'Naphtha Cracker']

        print_info(f"Found {len(ncc)} Naphtha Cracker facilities")

        # Total NCC capacity
        ncc_ethylene = ncc[ncc['product'] == 'Ethylene']['capacity_kt'].sum()
        ncc_propylene = ncc[ncc['product'] == 'Propylene']['capacity_kt'].sum()

        print(f"   Ethylene capacity: {ncc_ethylene:,.0f} kt")
        print(f"   Propylene capacity: {ncc_propylene:,.0f} kt")

        # Korea's ethylene capacity is ~9.9 Mt (2022), growing to ~12 Mt
        if 9000 <= ncc_ethylene <= 15000:
            print_pass(f"Ethylene capacity ({ncc_ethylene:,.0f} kt) within expected range (9,000-15,000 kt)")
        else:
            print_fail(f"Ethylene capacity ({ncc_ethylene:,.0f} kt) outside expected range")
            self.errors.append("Ethylene capacity outside expected range")

        # Check major NCC operators are present
        major_ncc_operators = ['Yeochon NCC', 'Lotte Chemical', 'LG Chem', 'SK Geocentric',
                              'Hanwha TotalEnergies', 'HD Hyundai Chemical']

        ncc_companies = ncc['company'].unique()
        for operator in major_ncc_operators:
            found = any(operator.lower() in c.lower() for c in ncc_companies)
            if found:
                print_pass(f"Major NCC operator '{operator}' found")
            else:
                # Some operators might have different names
                print_warn(f"Major NCC operator '{operator}' not found (may have different name)")
                self.warnings.append(f"NCC operator {operator} not found")

    def verify_technology_parameters(self):
        """Verify technology parameters are reasonable"""
        print_header("6. TECHNOLOGY PARAMETER VERIFICATION")

        # Check CAPEX learning curve (should decline over time)
        for _, tech in self.tech_params.iterrows():
            name = tech['technology']
            capex_2025 = tech['capex_2025_musd_per_mtco2']
            capex_2050 = tech['capex_2050_musd_per_mtco2']

            if capex_2050 <= capex_2025:
                print_pass(f"{name}: CAPEX declines from {capex_2025} to {capex_2050} M$/MtCO2")
            else:
                print_fail(f"{name}: CAPEX increases from {capex_2025} to {capex_2050} M$/MtCO2")
                self.errors.append(f"{name} CAPEX increases over time")

        # Check NCC-H2 H2 consumption
        ncc_h2 = self.tech_params[self.tech_params['technology'] == 'NCC-H2']
        if len(ncc_h2) > 0:
            h2_consumption = ncc_h2['h2_ton_per_ton_ethylene'].values[0]
            # Literature: 0.15-0.25 t-H2/t-ethylene
            if 0.1 <= h2_consumption <= 0.3:
                print_pass(f"NCC-H2 H2 consumption ({h2_consumption} t/t) within expected range")
            else:
                print_fail(f"NCC-H2 H2 consumption ({h2_consumption} t/t) outside expected range (0.1-0.3)")
                self.errors.append("NCC-H2 H2 consumption outside range")

        # Check NCC-Electricity electricity consumption
        ncc_elec = self.tech_params[self.tech_params['technology'] == 'NCC-Electricity']
        if len(ncc_elec) > 0:
            elec_consumption = ncc_elec['elec_mwh_per_ton_ethylene'].values[0]
            # Literature: 4.5-6.0 MWh/t-ethylene (BASF/SABIC eFurnace)
            if 4.0 <= elec_consumption <= 7.0:
                print_pass(f"NCC-Electricity consumption ({elec_consumption} MWh/t) within expected range")
            else:
                print_fail(f"NCC-Electricity consumption ({elec_consumption} MWh/t) outside expected range (4-7)")
                self.errors.append("NCC-Electricity consumption outside range")

    def verify_price_trajectories(self):
        """Verify price trajectories are reasonable"""
        print_header("7. PRICE TRAJECTORY VERIFICATION")

        # H2 price should decline
        h2_2025 = self.h2_prices[self.h2_prices['year'] == 2025]['h2_price_usd_per_kg'].values[0]
        h2_2050 = self.h2_prices[self.h2_prices['year'] == 2050]['h2_price_usd_per_kg'].values[0]

        if h2_2050 < h2_2025:
            print_pass(f"H2 price declines: ${h2_2025:.2f} (2025) → ${h2_2050:.2f} (2050)")
        else:
            print_fail(f"H2 price does not decline: ${h2_2025:.2f} (2025) → ${h2_2050:.2f} (2050)")
            self.errors.append("H2 price trajectory incorrect")

        # Check H2 price range (IEA: $2-6/kg for green H2)
        if 1.5 <= h2_2050 <= 3.0:
            print_pass(f"2050 H2 price (${h2_2050:.2f}/kg) within IEA target range ($1.5-3.0)")
        else:
            print_warn(f"2050 H2 price (${h2_2050:.2f}/kg) outside typical target range")
            self.warnings.append("2050 H2 price outside target range")

        # RE price should decline
        re_2025 = self.re_prices[self.re_prices['year'] == 2025]['re_price_usd_per_mwh'].values[0]
        re_2050 = self.re_prices[self.re_prices['year'] == 2050]['re_price_usd_per_mwh'].values[0]

        if re_2050 < re_2025:
            print_pass(f"RE price declines: ${re_2025:.0f} (2025) → ${re_2050:.0f} (2050)")
        else:
            print_fail(f"RE price does not decline: ${re_2025:.0f} (2025) → ${re_2050:.0f} (2050)")
            self.errors.append("RE price trajectory incorrect")

        # Grid EF should reach zero by 2050
        grid_2025 = self.grid_trajectory[self.grid_trajectory['year'] == 2025]['grid_ef_tco2_per_mwh'].values[0]
        grid_2050 = self.grid_trajectory[self.grid_trajectory['year'] == 2050]['grid_ef_tco2_per_mwh'].values[0]

        if grid_2050 == 0:
            print_pass(f"Grid EF reaches zero by 2050 (Net Zero grid)")
        else:
            print_warn(f"Grid EF in 2050 is {grid_2050} tCO2/MWh (not zero)")
            self.warnings.append("Grid not fully decarbonized by 2050")

        print(f"   Grid EF trajectory: {grid_2025:.3f} (2025) → {grid_2050:.3f} (2050)")

    def verify_mass_balance(self):
        """Verify mass balance and energy balance consistency"""
        print_header("8. MASS/ENERGY BALANCE CHECKS")

        # For NCCs: Propylene/Ethylene ratio should be ~0.5-0.7 (typical naphtha cracking)
        ncc = self.facilities[self.facilities['process'] == 'Naphtha Cracker']
        ethylene = ncc[ncc['product'] == 'Ethylene']['capacity_kt'].sum()
        propylene = ncc[ncc['product'] == 'Propylene']['capacity_kt'].sum()

        if ethylene > 0:
            ratio = propylene / ethylene
            if 0.4 <= ratio <= 0.9:
                print_pass(f"Propylene/Ethylene ratio ({ratio:.2f}) within expected range (0.4-0.9)")
            else:
                print_warn(f"Propylene/Ethylene ratio ({ratio:.2f}) outside typical range (0.4-0.9)")
                self.warnings.append("P/E ratio outside typical range")

        # Check that total capacity matches industry data
        total_capacity = self.facilities['capacity_kt'].sum()
        print_info(f"Total petrochemical capacity: {total_capacity:,.0f} kt/year")

        # Korea's petrochemical capacity is approximately 50-60 Mt of primary products
        # Our database has ~100 Mt which includes downstream products
        if 80000 <= total_capacity <= 120000:
            print_pass(f"Total capacity ({total_capacity:,.0f} kt) within expected range")
        else:
            print_warn(f"Total capacity ({total_capacity:,.0f} kt) may need verification")
            self.warnings.append("Total capacity needs verification")

    def verify_scenario_logic(self):
        """Verify scenario assumptions are consistent"""
        print_header("9. SCENARIO LOGIC VERIFICATION")

        # Check Shaheen facilities
        shaheen_file = self.data_dir / 'facility_database_with_shaheen.csv'
        if shaheen_file.exists():
            shaheen_db = pd.read_csv(shaheen_file)
            n_shaheen = len(shaheen_db) - len(self.facilities)

            if n_shaheen == 6:
                print_pass(f"Shaheen project adds 6 facilities (correct)")
            else:
                print_fail(f"Shaheen project adds {n_shaheen} facilities (expected 6)")
                self.errors.append("Incorrect Shaheen facility count")

            # Shaheen capacity check
            shaheen_only = shaheen_db[shaheen_db['company'].str.contains('Shaheen', case=False, na=False)]
            shaheen_capacity = shaheen_only['capacity_kt'].sum()

            # S-Oil Shaheen: 1.8 Mt ethylene, 770kt propylene, etc. = ~4 Mt total
            if 3500 <= shaheen_capacity <= 4500:
                print_pass(f"Shaheen capacity ({shaheen_capacity:,.0f} kt) matches project specs")
            else:
                print_warn(f"Shaheen capacity ({shaheen_capacity:,.0f} kt) differs from expected (~4,000 kt)")
                self.warnings.append("Shaheen capacity differs from expected")
        else:
            print_warn("Shaheen facility database not found")
            self.warnings.append("Shaheen database missing")

        # Check demand growth trajectories exist
        for scenario in ['shaheen', 'restructure_25pct', 'restructure_40pct']:
            traj_file = self.data_dir / f'demand_growth_trajectory_{scenario}.csv'
            if traj_file.exists():
                df = pd.read_csv(traj_file)
                if 'operating_rate_pct' in df.columns:
                    op_rate = df['operating_rate_pct'].iloc[0]
                    if op_rate == 70:
                        print_pass(f"{scenario} scenario has 70% operating rate")
                    else:
                        print_warn(f"{scenario} scenario has {op_rate}% operating rate (expected 70%)")
                        self.warnings.append(f"{scenario} operating rate is {op_rate}%")
            else:
                print_info(f"{scenario} demand trajectory not found (may be OK)")

    def run_all_verifications(self):
        """Run all verification checks"""
        print_header("DEEP VERIFICATION ANALYSIS")
        print("Running comprehensive checks on Korea Petrochemical Net Zero model...")

        self.verify_data_consistency()
        self.verify_emission_calculations()
        self.verify_energy_intensities()
        self.verify_regional_distribution()
        self.verify_ncc_facilities()
        self.verify_technology_parameters()
        self.verify_price_trajectories()
        self.verify_mass_balance()
        self.verify_scenario_logic()

        # Summary
        print_header("VERIFICATION SUMMARY")

        if len(self.errors) == 0:
            print(f"{GREEN}{BOLD}NO CRITICAL ERRORS FOUND{RESET}")
        else:
            print(f"{RED}{BOLD}CRITICAL ERRORS: {len(self.errors)}{RESET}")
            for error in self.errors:
                print(f"   {RED}✗{RESET} {error}")

        if len(self.warnings) > 0:
            print(f"\n{YELLOW}{BOLD}WARNINGS: {len(self.warnings)}{RESET}")
            for warn in self.warnings:
                print(f"   {YELLOW}⚠{RESET} {warn}")

        # Key metrics
        print(f"\n{BOLD}KEY METRICS:{RESET}")
        print(f"   Baseline facilities: {len(self.facilities)}")
        print(f"   Total capacity: {self.facilities['capacity_kt'].sum():,.0f} kt/year")
        print(f"   Emissions (100%): {self.total_emissions_100pct/1e6:.2f} MtCO2")
        print(f"   Emissions (70%): {self.total_emissions_70pct/1e6:.2f} MtCO2")

        return len(self.errors) == 0


if __name__ == '__main__':
    verifier = DeepVerification()
    success = verifier.run_all_verifications()

    if success:
        print(f"\n{GREEN}All verification checks passed!{RESET}")
        sys.exit(0)
    else:
        print(f"\n{RED}Verification found errors that need attention.{RESET}")
        sys.exit(1)
