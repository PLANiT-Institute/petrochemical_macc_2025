"""
MODULE 1: BASELINE ANALYSIS
Calculate baseline emissions and BAU trajectory
All facilities operate forever (no retirement)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from .utils import (DataLoader, EmissionCalculator, PriceCalculator,
                    save_csv_output, save_plot, identify_product_group)


class BaselineAnalyzer:
    """
    Baseline emissions analysis
    - Calculate 2025 baseline: 52 MtCO2
    - Project BAU trajectory 2025-2050 with grid decarbonization
    - NO facility retirement (all facilities exist forever)
    - Track energy consumption by fuel type
    """

    def __init__(self, data_dir='data', output_dir='outputs/module_01'):
        """Initialize with data directory"""
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("MODULE 1: BASELINE ANALYSIS")
        print("="*80)

        # Load data
        print("\n📁 Loading data...")
        loader = DataLoader(data_dir)

        self.df_facilities = loader.load_facilities()
        self.df_intensities = loader.load_energy_intensities()
        self.df_emission_factors = loader.load_emission_factors()
        self.df_grid_emissions = loader.load_grid_emissions()
        self.df_fuel_prices = pd.read_csv(self.data_dir / 'fuel_price_trajectory.csv')

        # Load demand growth trajectory
        try:
            self.df_demand_growth = pd.read_csv(self.data_dir / 'demand_growth_trajectory.csv')
            print(f"   - Loaded demand growth trajectory (2025-2050)")
            try:
                growth_2050 = self.df_demand_growth[self.df_demand_growth['year']==2050]['cumulative_capacity_multiplier'].iloc[0]
                print(f"   - Total capacity growth: {(growth_2050-1)*100:.1f}%")
            except (IndexError, KeyError):
                print("   - ⚠️  Could not calculate 2050 growth (data missing)")
        except FileNotFoundError:
            print("   - ⚠️  No demand growth file found, assuming zero growth")
            self.df_demand_growth = pd.DataFrame({
                'year': range(2025, 2051),
                'annual_growth_rate_pct': [0.0] * 26,
                'cumulative_capacity_multiplier': [1.0] * 26
            })

        print(f"   - Loaded {len(self.df_facilities)} facilities")
        print(f"   - Loaded {len(self.df_intensities)} energy intensities")

        # Initialize calculators
        self.emission_calc = EmissionCalculator(self.df_emission_factors)

    def calculate_baseline_2025(self):
        """
        Calculate 2025 baseline emissions for all facilities
        Returns DataFrame with facility-level details and energy consumption
        """
        print("\nCalculating 2025 baseline...")

        baseline = []

        for idx, facility in self.df_facilities.iterrows():
            # Get energy intensities for this product
            intensity_row = self.df_intensities.iloc[idx]

            capacity = facility['capacity_kt']  # kt/year

            # Calculate energy consumption (total for facility per year)
            energy_consumption = {
                'naphtha_gj': intensity_row['Naphtha_GJ_per_tonne'] * capacity * 1000,  # GJ/year
                'electricity_kwh': intensity_row['Electricity_kWh_per_tonne'] * capacity * 1000,  # kWh/year
                'lng_gj': intensity_row['LNG_GJ_per_tonne'] * capacity * 1000,
                'fuel_gas_gj': intensity_row['Fuel_Gas_GJ_per_tonne'] * capacity * 1000,
                'byproduct_gas_gj': intensity_row['Byproduct_Gas_GJ_per_tonne'] * capacity * 1000,
                'lpg_gj': intensity_row['LPG_GJ_per_tonne'] * capacity * 1000,
                'fuel_oil_gj': intensity_row['Fuel_Oil_GJ_per_tonne'] * capacity * 1000,
                'diesel_gj': intensity_row['Diesel_GJ_per_tonne'] * capacity * 1000,
            }

            # Calculate emissions by fuel (kt CO2/year)
            emissions = self.emission_calc.calculate_total_emissions(facility, intensity_row)

            # Add product group
            product_group = identify_product_group(facility['product'])

            # Compile baseline row
            baseline.append({
                'product': facility['product'],
                'product_group': product_group,
                'process': facility['process'],
                'company': facility['company'],
                'location': facility['location'],
                'capacity_kt': capacity,
                'year_built': facility['year_built'],
                # Energy consumption
                'naphtha_gj_per_year': energy_consumption['naphtha_gj'],
                'electricity_kwh_per_year': energy_consumption['electricity_kwh'],
                'lng_gj_per_year': energy_consumption['lng_gj'],
                'fuel_gas_gj_per_year': energy_consumption['fuel_gas_gj'],
                'byproduct_gas_gj_per_year': energy_consumption['byproduct_gas_gj'],
                'lpg_gj_per_year': energy_consumption['lpg_gj'],
                'fuel_oil_gj_per_year': energy_consumption['fuel_oil_gj'],
                'diesel_gj_per_year': energy_consumption['diesel_gj'],
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

        df_baseline = pd.DataFrame(baseline)

        total_emissions = df_baseline['total_emissions_kt'].sum() / 1000  # MtCO2

        print(f"   - Total baseline emissions: {total_emissions:.2f} MtCO2")
        print(f"   - Facilities: {len(df_baseline)}")

        # Calculate shares
        naphtha_share = df_baseline['emissions_naphtha_kt'].sum() / df_baseline['total_emissions_kt'].sum() * 100
        elec_share = df_baseline['emissions_electricity_kt'].sum() / df_baseline['total_emissions_kt'].sum() * 100
        other_share = 100 - naphtha_share - elec_share

        print(f"   - Naphtha: {naphtha_share:.1f}%")
        print(f"   - Electricity: {elec_share:.1f}%")
        print(f"   - Other: {other_share:.1f}%")

        self.df_baseline = df_baseline
        return df_baseline

    def project_bau_trajectory(self, start_year=2025, end_year=2050, facility_lifetime=None):
        """
        Project BAU emissions trajectory
        - Optional facility retirement based on lifetime (default: no retirement)
        - Grid decarbonization reduces electricity emissions
        - Demand growth increases overall capacity and emissions

        Parameters:
        - facility_lifetime: If specified (e.g., 50), facilities retire after this many years
        """
        print(f"\n📈 Projecting BAU trajectory ({start_year}-{end_year})...")
        if facility_lifetime:
            print(f"   - Facility lifetime: {facility_lifetime} years (retirement enabled)")
        else:
            print(f"   - Facility lifetime: infinite (no retirement)")

        years = range(start_year, end_year + 1)
        trajectory = []

        # Get baseline 2025 energy consumption
        baseline_2025 = self.df_baseline

        # Get grid emission factor baseline
        grid_ef_2025 = self.df_grid_emissions[self.df_grid_emissions['year'] == 2025]['grid_ef_tco2_per_mwh'].iloc[0]

        for year in years:
            # Get grid emission factor for this year
            try:
                grid_ef = self.df_grid_emissions[self.df_grid_emissions['year'] == year]['grid_ef_tco2_per_mwh'].iloc[0]
            except (IndexError, KeyError):
                # Fallback to 2045 or previous known value if 2050 is missing
                # Assuming monotonic decrease, using last available is safe approx
                if year > 2025:
                     grid_ef = trajectory[-1]['grid_ef_tco2_per_mwh']
                else:
                     grid_ef = 0.436 # Fallback to 2025 default

            # Calculate active facilities if retirement is enabled
            if facility_lifetime:
                # Facilities retire when (year - year_built) > lifetime
                retirement_year_threshold = year - facility_lifetime
                active_facilities = baseline_2025[baseline_2025['year_built'] > retirement_year_threshold]

                # Calculate remaining capacity fraction
                remaining_capacity_fraction = active_facilities['capacity_kt'].sum() / baseline_2025['capacity_kt'].sum()
                n_active = len(active_facilities)
                n_retired = len(baseline_2025) - n_active
            else:
                active_facilities = baseline_2025
                remaining_capacity_fraction = 1.0
                n_active = len(baseline_2025)
                n_retired = 0

            # Get demand row for this year
            demand_row = self.df_demand_growth[self.df_demand_growth['year'] == year]
            
            if not demand_row.empty:
                try:
                     capacity_multiplier = demand_row['cumulative_capacity_multiplier'].iloc[0]
                except (IndexError, KeyError):
                     capacity_multiplier = 1.0
                
                try:
                     if 'operating_rate_pct' in demand_row.columns:
                         op_rate = demand_row['operating_rate_pct'].iloc[0] / 100.0
                     else:
                         op_rate = 1.0
                except (IndexError, KeyError):
                     op_rate = 1.0
            else:
                 # Missing year
                 capacity_multiplier = 1.0
                 op_rate = 1.0
                 if year == 2050:
                     print(f"   Warning: Missing growth data for {year}, using default 1.0")

            # Effective production = Capacity * Growth * Operating Rate
            effective_multiplier = capacity_multiplier * op_rate

            # Emissions scale with:
            # 1. Remaining capacity (after retirement)
            # 2. Demand growth (capacity multiplier)
            # 3. Operating Rate (NEW)
            # 4. Grid decarbonization (electricity only)

            # Fossil fuel emissions
            fossil_emissions_base = (
                active_facilities['emissions_naphtha_kt'].sum() +
                active_facilities['emissions_lng_kt'].sum() +
                active_facilities['emissions_fuel_gas_kt'].sum() +
                active_facilities['emissions_byproduct_gas_kt'].sum() +
                active_facilities['emissions_lpg_kt'].sum() +
                active_facilities['emissions_fuel_oil_kt'].sum() +
                active_facilities['emissions_diesel_kt'].sum()
            )
            fossil_emissions = fossil_emissions_base * effective_multiplier

            # Electricity emissions scale with both demand/op_rate AND grid decarbonization
            elec_emissions_base = active_facilities['emissions_electricity_kt'].sum()
            grid_scaling = grid_ef / grid_ef_2025
            elec_emissions = elec_emissions_base * effective_multiplier * grid_scaling

            total_emissions = fossil_emissions + elec_emissions

            # Calculate total capacity (installed capacity, not actual production)
            total_capacity = active_facilities['capacity_kt'].sum() * capacity_multiplier

            trajectory.append({
                'year': year,
                'fossil_emissions_mt': fossil_emissions / 1000,
                'electricity_emissions_mt': elec_emissions / 1000,
                'total_emissions_mt': total_emissions / 1000,
                'grid_ef_tco2_per_mwh': grid_ef,
                'n_facilities_active': n_active,
                'n_facilities_retired': n_retired,
                'remaining_capacity_fraction': remaining_capacity_fraction,
                'capacity_multiplier': capacity_multiplier,
                'total_capacity_kt': total_capacity,
            })

        df_trajectory = pd.DataFrame(trajectory)

        print(f"   - {start_year} emissions: {df_trajectory.iloc[0]['total_emissions_mt']:.2f} MtCO2")
        print(f"   - {end_year} emissions: {df_trajectory.iloc[-1]['total_emissions_mt']:.2f} MtCO2")
        print(f"   - Capacity growth: {(df_trajectory.iloc[-1]['capacity_multiplier']-1)*100:.1f}%")
        if facility_lifetime:
            print(f"   - {df_trajectory.iloc[0]['n_facilities_active']} → {df_trajectory.iloc[-1]['n_facilities_active']} facilities (retired: {df_trajectory.iloc[-1]['n_facilities_retired']})")
            print(f"   - Remaining capacity: {df_trajectory.iloc[-1]['remaining_capacity_fraction']*100:.1f}%")
        else:
            print(f"   - All {len(baseline_2025)} facilities operate forever")

        self.df_trajectory = df_trajectory
        return df_trajectory

    def calculate_aggregations(self):
        """Calculate emissions by product, company, location"""
        print("\nCalculating aggregations...")

        # By product group
        by_product = self.df_baseline.groupby('product_group').agg({
            'total_emissions_kt': 'sum',
            'capacity_kt': 'sum',
            'product': 'count'
        }).reset_index()
        by_product.columns = ['product_group', 'emissions_kt', 'capacity_kt', 'n_facilities']
        by_product['emissions_mt'] = by_product['emissions_kt'] / 1000
        by_product['share_pct'] = 100 * by_product['emissions_mt'] / by_product['emissions_mt'].sum()
        by_product = by_product.sort_values('emissions_mt', ascending=False)

        # By company
        by_company = self.df_baseline.groupby('company').agg({
            'total_emissions_kt': 'sum',
            'capacity_kt': 'sum',
            'product': 'count'
        }).reset_index()
        by_company.columns = ['company', 'emissions_kt', 'capacity_kt', 'n_facilities']
        by_company['emissions_mt'] = by_company['emissions_kt'] / 1000
        by_company['share_pct'] = 100 * by_company['emissions_mt'] / by_company['emissions_mt'].sum()
        by_company = by_company.sort_values('emissions_mt', ascending=False)

        # By location
        by_location = self.df_baseline.groupby('location').agg({
            'total_emissions_kt': 'sum',
            'capacity_kt': 'sum',
            'product': 'count'
        }).reset_index()
        by_location.columns = ['location', 'emissions_kt', 'capacity_kt', 'n_facilities']
        by_location['emissions_mt'] = by_location['emissions_kt'] / 1000
        by_location['share_pct'] = 100 * by_location['emissions_mt'] / by_location['emissions_mt'].sum()
        by_location = by_location.sort_values('emissions_mt', ascending=False)

        print(f"   - Aggregated by {len(by_product)} product groups")
        print(f"   - Aggregated by {len(by_company)} companies")
        print(f"   - Aggregated by {len(by_location)} locations")

        self.df_by_product = by_product
        self.df_by_company = by_company
        self.df_by_location = by_location

        return by_product, by_company, by_location

    def calculate_fuel_costs(self):
        """Calculate annual fuel costs for baseline"""
        print("\n💰 Calculating fuel costs...")

        # Get 2025 fuel prices
        try:
            prices_2025 = self.df_fuel_prices[self.df_fuel_prices['year'] == 2025].iloc[0]
        except (IndexError, KeyError):
            print("   Warning: Missing 2025 fuel prices, using defaults")
            # Create dummy series with 0.0 or reasonable defaults
            prices_2025 = pd.Series(dtype=float)
            for fuel in ['naphtha', 'electricity', 'lng', 'fuel_gas', 'lpg', 'fuel_oil', 'diesel']:
                 prices_2025[f'{fuel}_usd_per_gj'] = 0.0
            prices_2025['electricity_usd_per_kwh'] = 0.0

        total_cost = 0

        # Calculate cost for each fuel
        costs = {}

        # Naphtha
        naphtha_gj = self.df_baseline['naphtha_gj_per_year'].sum()
        costs['naphtha'] = naphtha_gj * prices_2025['naphtha_usd_per_gj'] / 1e6  # Million USD

        # Electricity
        electricity_kwh = self.df_baseline['electricity_kwh_per_year'].sum()
        costs['electricity'] = electricity_kwh * prices_2025['electricity_usd_per_kwh'] / 1e6

        # LNG
        lng_gj = self.df_baseline['lng_gj_per_year'].sum()
        costs['lng'] = lng_gj * prices_2025['lng_usd_per_gj'] / 1e6

        # Fuel Gas
        fuel_gas_gj = self.df_baseline['fuel_gas_gj_per_year'].sum()
        costs['fuel_gas'] = fuel_gas_gj * prices_2025['fuel_gas_usd_per_gj'] / 1e6

        # LPG
        lpg_gj = self.df_baseline['lpg_gj_per_year'].sum()
        costs['lpg'] = lpg_gj * prices_2025['lpg_usd_per_gj'] / 1e6

        # Fuel Oil
        fuel_oil_gj = self.df_baseline['fuel_oil_gj_per_year'].sum()
        costs['fuel_oil'] = fuel_oil_gj * prices_2025['fuel_oil_usd_per_gj'] / 1e6

        # Diesel
        diesel_gj = self.df_baseline['diesel_gj_per_year'].sum()
        costs['diesel'] = diesel_gj * prices_2025['diesel_usd_per_gj'] / 1e6

        total_cost = sum(costs.values())

        print(f"   - Total annual fuel cost (2025): ${total_cost:.1f} Million")
        print(f"      - Naphtha: ${costs['naphtha']:.1f}M ({costs['naphtha']/total_cost*100:.1f}%)")
        print(f"      - Electricity: ${costs['electricity']:.1f}M ({costs['electricity']/total_cost*100:.1f}%)")

        self.fuel_costs = costs
        return costs

    def create_visualizations(self):
        """Create all visualizations - Publication quality"""
        print("\nCreating visualizations...")

        # 1. Baseline by product group - Professional pie chart
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = sns.color_palette("Set2", len(self.df_by_product))
        wedges, texts, autotexts = ax.pie(self.df_by_product['emissions_mt'],
               labels=self.df_by_product['product_group'],
               autopct='%1.1f%%',
               colors=colors,
               startangle=90,
               textprops={'fontsize': 11, 'weight': 'bold'})

        # Enhance text visibility
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)

        ax.set_title('2025 Baseline Emissions by Product Group\n52 MtCO2 Total',
                    fontsize=15, fontweight='bold', pad=20)
        save_plot(fig, self.output_dir / 'baseline_2025_by_product.png')

        # 2. BAU trajectory - Professional line chart
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.plot(self.df_trajectory['year'], self.df_trajectory['total_emissions_mt'],
               linewidth=3.5, color='#E74C3C', label='Total Emissions', marker='o', markersize=5)
        ax.plot(self.df_trajectory['year'], self.df_trajectory['fossil_emissions_mt'],
               linewidth=2.5, color='#8B4513', linestyle='--', label='Fossil Fuels', marker='s', markersize=4)
        ax.plot(self.df_trajectory['year'], self.df_trajectory['electricity_emissions_mt'],
               linewidth=2.5, color='#3498DB', linestyle='--', label='Electricity (Grid)', marker='^', markersize=4)

        ax.set_xlabel('Year', fontsize=13, fontweight='bold')
        ax.set_ylabel('Emissions (MtCO2/year)', fontsize=13, fontweight='bold')
        ax.set_title('Business-as-Usual Emissions Trajectory (2025-2050)\nAll Facilities Operate Forever',
                    fontsize=15, fontweight='bold')
        ax.legend(loc='upper right', fontsize=11, framealpha=0.95, edgecolor='black')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(2024, 2051)

        # Add shaded region for context
        ax.fill_between(self.df_trajectory['year'], 0, self.df_trajectory['total_emissions_mt'],
                       alpha=0.1, color='red')

        save_plot(fig, self.output_dir / 'bau_trajectory.png')

        # 3. Top 10 companies - Professional horizontal bar chart
        fig, ax = plt.subplots(figsize=(12, 8))
        top_10 = self.df_by_company.head(10)
        bars = ax.barh(range(len(top_10)), top_10['emissions_mt'],
                      color='#3498DB', alpha=0.8, edgecolor='black', linewidth=1.2)

        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, top_10['emissions_mt'])):
            ax.text(val + 0.2, i, f'{val:.2f} Mt', va='center', fontsize=10, fontweight='bold')

        ax.set_yticks(range(len(top_10)))
        ax.set_yticklabels(top_10['company'], fontsize=11)
        ax.set_xlabel('Annual Emissions (MtCO2/year)', fontsize=13, fontweight='bold')
        ax.set_title('Top 10 Emitting Companies (2025 Baseline)', fontsize=15, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x', linestyle='--')
        ax.set_xlim(0, max(top_10['emissions_mt']) * 1.15)

        save_plot(fig, self.output_dir / 'baseline_2025_top_companies.png')

    def save_outputs(self):
        """Save all output files"""
        print("\nSaving outputs...")

        # CSVs
        save_csv_output(self.df_baseline, self.output_dir / 'baseline_2025_detailed.csv',
                       f"({len(self.df_baseline)} facilities)")
        save_csv_output(self.df_trajectory, self.output_dir / 'bau_trajectory_2025_2050.csv',
                       f"({len(self.df_trajectory)} years)")
        save_csv_output(self.df_by_product, self.output_dir / 'emissions_by_product.csv')
        save_csv_output(self.df_by_company, self.output_dir / 'emissions_by_company.csv')
        save_csv_output(self.df_by_location, self.output_dir / 'emissions_by_location.csv')

    def run_complete_analysis(self, include_retirement_scenario=True):
        """Run complete baseline analysis"""
        print("\n" + "="*80)
        print("RUNNING COMPLETE BASELINE ANALYSIS")
        print("="*80)

        self.calculate_baseline_2025()

        # Scenario 1: No retirement (infinite lifetime)
        print("\n" + "="*60)
        print("SCENARIO 1: NO RETIREMENT (Infinite Lifetime)")
        print("="*60)
        df_traj_infinite = self.project_bau_trajectory(facility_lifetime=None)

        # Scenario 2: 50-year retirement (optional)
        df_traj_50yr = None
        if include_retirement_scenario:
            print("\n" + "="*60)
            print("SCENARIO 2: 50-YEAR FACILITY LIFETIME")
            print("="*60)
            df_traj_50yr = self.project_bau_trajectory(facility_lifetime=50)

            # Save retirement scenario separately
            save_csv_output(df_traj_50yr, self.output_dir / 'bau_trajectory_with_retirement_50yr.csv',
                           f"({len(df_traj_50yr)} years)")

            # Create comparison visualization
            self._create_retirement_comparison(df_traj_infinite, df_traj_50yr)

        # Use infinite lifetime as default for subsequent analysis
        self.df_trajectory = df_traj_infinite

        self.calculate_aggregations()
        self.calculate_fuel_costs()
        self.create_visualizations()
        self.save_outputs()

        print("\n" + "="*80)
        print("- MODULE 1 COMPLETE")
        print("="*80)
        print(f"\nOutputs saved to: {self.output_dir}")

        return {
            'baseline': self.df_baseline,
            'trajectory': self.df_trajectory,
            'trajectory_50yr': df_traj_50yr,
            'by_product': self.df_by_product,
            'by_company': self.df_by_company,
            'by_location': self.df_by_location,
        }

    def _create_retirement_comparison(self, df_infinite, df_50yr):
        """Create comparison visualization for retirement scenarios"""
        print("\nCreating retirement scenario comparison...")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Plot 1: Emissions comparison
        ax1.plot(df_infinite['year'], df_infinite['total_emissions_mt'],
                linewidth=3, color='#E74C3C', label='No Retirement (Infinite)', marker='o', markersize=5)
        ax1.plot(df_50yr['year'], df_50yr['total_emissions_mt'],
                linewidth=3, color='#2ECC71', label='50-Year Retirement', marker='s', markersize=5)

        ax1.fill_between(df_infinite['year'], df_50yr['total_emissions_mt'], df_infinite['total_emissions_mt'],
                        alpha=0.3, color='orange', label='Difference')

        ax1.set_xlabel('Year', fontsize=13, fontweight='bold')
        ax1.set_ylabel('Emissions (MtCO2/year)', fontsize=13, fontweight='bold')
        ax1.set_title('BAU Emissions: Retirement Impact', fontsize=15, fontweight='bold')
        ax1.legend(loc='upper right', fontsize=11)
        ax1.grid(True, alpha=0.3, linestyle='--')

        # Plot 2: Active facilities
        ax2.plot(df_50yr['year'], df_50yr['n_facilities_active'],
                linewidth=3, color='#3498DB', marker='o', markersize=5)
        ax2.fill_between(df_50yr['year'], 0, df_50yr['n_facilities_active'],
                        alpha=0.3, color='#3498DB')

        ax2_twin = ax2.twinx()
        ax2_twin.plot(df_50yr['year'], df_50yr['n_facilities_retired'],
                     linewidth=3, color='#E74C3C', linestyle='--', marker='s', markersize=5)

        ax2.set_xlabel('Year', fontsize=13, fontweight='bold')
        ax2.set_ylabel('Active Facilities', fontsize=13, fontweight='bold', color='#3498DB')
        ax2_twin.set_ylabel('Retired Facilities', fontsize=13, fontweight='bold', color='#E74C3C')
        ax2.set_title('Facility Retirement Schedule (50-Year Lifetime)', fontsize=15, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.tick_params(axis='y', labelcolor='#3498DB')
        ax2_twin.tick_params(axis='y', labelcolor='#E74C3C')

        plt.tight_layout()
        save_plot(fig, self.output_dir / 'bau_retirement_comparison.png')

        # Calculate and print key statistics
        reduction_2050 = df_infinite.iloc[-1]['total_emissions_mt'] - df_50yr.iloc[-1]['total_emissions_mt']
        reduction_pct = (reduction_2050 / df_infinite.iloc[-1]['total_emissions_mt']) * 100

        print(f"   - 2050 emissions reduction from retirement: {reduction_2050:.2f} MtCO2 ({reduction_pct:.1f}%)")
        print(f"   - Facilities retired by 2050: {df_50yr.iloc[-1]['n_facilities_retired']}/{len(self.df_baseline)}")
