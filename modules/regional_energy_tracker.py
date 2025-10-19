"""
Regional Energy Transition Tracker
Tracks technology adoption and energy consumption changes by location/region
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


class RegionalEnergyTracker:
    """
    Track regional technology transitions and energy consumption changes
    """

    def __init__(self, baseline_dir='data', output_dir='outputs/regional_analysis'):
        self.baseline_dir = Path(baseline_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load facility database
        self.df_facilities = pd.read_csv(self.baseline_dir / 'facility_database.csv')
        self.df_baseline = pd.read_csv(self.baseline_dir / 'baseline_2025_detailed.csv')

        # Exchange rate (KRW/USD)
        self.krw_usd_rate = 1300

        # Energy conversion factors
        self.boe_per_gj = 0.17  # Barrels of oil equivalent per GJ

    def add_alternative_cost_units(self, df_macc):
        """
        Add alternative cost units to MACC dataframe

        Args:
            df_macc: MACC results with total_cost_usd_per_tco2

        Returns:
            DataFrame with additional cost columns
        """
        df = df_macc.copy()

        # Typical abatement per ton ethylene (tCO2/ton ethylene)
        # Baseline: 29.0 GJ/ton × 0.0542 tCO2/GJ = 1.739 tCO2/ton for NCC
        # For NCC-Electricity: 1.739 - 0.15 = 1.59 tCO2/ton
        # For NCC-H2: 1.739 tCO2/ton

        abatement_per_ton_ethylene = {
            'Heat_Pump': 0.5,  # Approximate for BTX/Utility
            'RE_PPA': 0.4,     # Grid emission reduction
            'NCC-Electricity': 1.59,
            'NCC-H2': 1.739
        }

        # Add cost per ton ethylene
        df['cost_usd_per_ton_ethylene'] = df.apply(
            lambda row: row['total_cost_usd_per_tco2'] * abatement_per_ton_ethylene.get(row['technology'], 1.0),
            axis=1
        )

        # Add cost in KRW per ton
        df['cost_krw_per_ton_ethylene'] = df['cost_usd_per_ton_ethylene'] * self.krw_usd_rate

        # Add cost per barrel oil equivalent (based on naphtha replacement)
        # 1 ton ethylene ≈ 29 GJ naphtha ≈ 4.93 boe
        df['cost_usd_per_boe'] = df['cost_usd_per_ton_ethylene'] / 4.93

        return df

    def create_regional_baseline(self):
        """
        Create regional baseline emissions and energy consumption
        """
        # Baseline already has location column
        df = self.df_baseline.copy()

        # Calculate total energy from all fuel columns
        fuel_cols = [c for c in df.columns if c.endswith('_gj_per_year') or c.endswith('_kwh_per_year')]

        # Convert kWh to GJ (1 kWh = 0.0036 GJ)
        df['total_energy_gj'] = 0
        for col in fuel_cols:
            if 'kwh' in col.lower():
                df['total_energy_gj'] += df[col].fillna(0) * 0.0036
            else:
                df['total_energy_gj'] += df[col].fillna(0)

        # Total emissions (convert kt to tCO2)
        df['total_emissions_tco2'] = df['total_emissions_kt'].fillna(0) * 1000

        # Aggregate by region
        regional = df.groupby('location').agg({
            'total_emissions_tco2': 'sum',
            'total_energy_gj': 'sum',
            'capacity_kt': 'sum',
            'product': 'count'
        }).reset_index()

        regional.columns = ['location', 'emissions_tco2', 'energy_gj',
                           'capacity_kt', 'num_facilities']

        # Convert to Mt and PJ
        regional['emissions_mt'] = regional['emissions_tco2'] / 1e6
        regional['energy_pj'] = regional['energy_gj'] / 1e6

        return regional

    def track_regional_transition(self, df_deployment):
        """
        Track technology deployment by region over time

        Args:
            df_deployment: Technology deployment results from optimization module

        Returns:
            DataFrame with regional technology adoption and energy changes
        """
        # Merge with facility locations
        df = df_deployment.merge(
            self.df_facilities[['product', 'company', 'location']],
            on=['product', 'company'],
            how='left'
        )

        # Group by location, year, technology
        regional_tech = df.groupby(['location', 'year', 'technology']).agg({
            'capacity_deployed_kt': 'sum',
            'emissions_reduced_tco2': 'sum',
            'capex_total_musd': 'sum'
        }).reset_index()

        return regional_tech

    def calculate_energy_consumption_change(self, df_deployment):
        """
        Calculate energy consumption changes by region, year, and fuel type

        Args:
            df_deployment: Technology deployment with energy data

        Returns:
            DataFrame showing fuel switching by region
        """
        results = []

        for idx, row in df_deployment.iterrows():
            tech = row['technology']
            year = row['year']
            capacity = row.get('capacity_deployed_kt', 0)

            # Get location
            location = self.df_facilities[
                (self.df_facilities['product'] == row.get('product', '')) &
                (self.df_facilities['company'] == row.get('company', ''))
            ]['location'].values

            if len(location) == 0:
                continue
            location = location[0]

            # Energy changes based on technology
            if tech == 'NCC-Electricity':
                # Naphtha reduction: 29.0 GJ/ton
                # Electricity increase: 3.0 MWh/ton = 10.8 GJ/ton
                naphtha_reduced = capacity * 1000 * 29.0 / 1e6  # PJ
                electricity_increased = capacity * 1000 * 10.8 / 1e6  # PJ

                results.append({
                    'location': location,
                    'year': year,
                    'technology': tech,
                    'fuel_type': 'Naphtha',
                    'energy_change_pj': -naphtha_reduced
                })
                results.append({
                    'location': location,
                    'year': year,
                    'technology': tech,
                    'fuel_type': 'Renewable_Electricity',
                    'energy_change_pj': electricity_increased
                })

            elif tech == 'NCC-H2':
                # Naphtha reduction: 29.0 GJ/ton
                # H2 increase: 0.18 ton H2/ton ethylene × 120 GJ/ton H2 = 21.6 GJ/ton
                naphtha_reduced = capacity * 1000 * 29.0 / 1e6  # PJ
                h2_increased = capacity * 1000 * 21.6 / 1e6  # PJ

                results.append({
                    'location': location,
                    'year': year,
                    'technology': tech,
                    'fuel_type': 'Naphtha',
                    'energy_change_pj': -naphtha_reduced
                })
                results.append({
                    'location': location,
                    'year': year,
                    'technology': tech,
                    'fuel_type': 'Green_H2',
                    'energy_change_pj': h2_increased
                })

            elif tech == 'Heat_Pump':
                # Thermal fuel reduction (LNG/FuelGas)
                # Electricity increase (with COP=4.0)
                # Assume 50 GJ/kt capacity for BTX/Utility
                thermal_reduced = capacity * 1000 * 50.0 / 1e6  # PJ
                electricity_increased = thermal_reduced / 4.0  # PJ (COP=4.0)

                results.append({
                    'location': location,
                    'year': year,
                    'technology': tech,
                    'fuel_type': 'Thermal_Fuel',
                    'energy_change_pj': -thermal_reduced
                })
                results.append({
                    'location': location,
                    'year': year,
                    'technology': tech,
                    'fuel_type': 'Renewable_Electricity',
                    'energy_change_pj': electricity_increased
                })

            elif tech == 'RE_PPA':
                # Grid electricity → RE electricity (no net energy change)
                grid_electricity = capacity * 1000 * 5.0 / 1e6  # PJ (assumed)

                results.append({
                    'location': location,
                    'year': year,
                    'technology': tech,
                    'fuel_type': 'Grid_Electricity',
                    'energy_change_pj': -grid_electricity
                })
                results.append({
                    'location': location,
                    'year': year,
                    'technology': tech,
                    'fuel_type': 'Renewable_Electricity',
                    'energy_change_pj': grid_electricity
                })

        return pd.DataFrame(results)

    def create_regional_summary_table(self, regional_baseline, regional_tech_2030, regional_tech_2050):
        """
        Create summary table for each region showing baseline and transitions
        """
        summary = []

        locations = regional_baseline['location'].unique()

        for loc in locations:
            baseline = regional_baseline[regional_baseline['location'] == loc].iloc[0]

            # 2030 deployment
            tech_2030 = regional_tech_2030[regional_tech_2030['location'] == loc]
            emissions_reduced_2030 = tech_2030['emissions_reduced_tco2'].sum() / 1e6  # Mt

            # 2050 deployment
            tech_2050 = regional_tech_2050[regional_tech_2050['location'] == loc]
            emissions_reduced_2050 = tech_2050['emissions_reduced_tco2'].sum() / 1e6  # Mt

            summary.append({
                'location': loc,
                'baseline_emissions_mt': baseline['emissions_mt'],
                'baseline_energy_pj': baseline['energy_pj'],
                'num_facilities': baseline['num_facilities'],
                'emissions_reduced_2030_mt': emissions_reduced_2030,
                'reduction_pct_2030': emissions_reduced_2030 / baseline['emissions_mt'] * 100,
                'emissions_reduced_2050_mt': emissions_reduced_2050,
                'reduction_pct_2050': emissions_reduced_2050 / baseline['emissions_mt'] * 100
            })

        return pd.DataFrame(summary)

    def visualize_regional_transitions(self, df_energy_change):
        """
        Create visualizations for regional energy transitions
        """
        # 1. Fuel switching by region (2030 vs 2050)
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        for idx, year in enumerate([2030, 2050]):
            df_year = df_energy_change[df_energy_change['year'] == year]

            pivot = df_year.pivot_table(
                values='energy_change_pj',
                index='location',
                columns='fuel_type',
                aggfunc='sum',
                fill_value=0
            )

            pivot.plot(kind='bar', stacked=True, ax=axes[idx],
                      colormap='RdYlGn', edgecolor='black', linewidth=0.5)

            axes[idx].set_title(f'Energy Fuel Mix Changes by Region ({year})',
                               fontsize=14, fontweight='bold')
            axes[idx].set_xlabel('Location', fontsize=12)
            axes[idx].set_ylabel('Energy Change (PJ)', fontsize=12)
            axes[idx].legend(title='Fuel Type', fontsize=9)
            axes[idx].grid(True, alpha=0.3, axis='y')
            axes[idx].axhline(y=0, color='black', linewidth=1.5)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'regional_energy_transitions.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

        # 2. Technology adoption by region over time
        fig, ax = plt.subplots(figsize=(14, 8))

        locations = df_energy_change['location'].unique()
        years = sorted(df_energy_change['year'].unique())

        # Create heatmap of technology adoption
        tech_adoption = df_energy_change.groupby(['location', 'year', 'technology'])['energy_change_pj'].sum().reset_index()

        # Pivot for heatmap
        for tech in tech_adoption['technology'].unique():
            df_tech = tech_adoption[tech_adoption['technology'] == tech]
            pivot = df_tech.pivot(index='location', columns='year', values='energy_change_pj')

            # Save individual technology maps
            fig_tech, ax_tech = plt.subplots(figsize=(12, 6))
            sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn',
                       center=0, ax=ax_tech, cbar_kws={'label': 'Energy Change (PJ)'})
            ax_tech.set_title(f'{tech} Deployment by Region (2025-2050)',
                            fontsize=14, fontweight='bold')
            ax_tech.set_xlabel('Year', fontsize=12)
            ax_tech.set_ylabel('Location', fontsize=12)

            plt.tight_layout()
            plt.savefig(self.output_dir / f'regional_{tech}_heatmap.png',
                       dpi=300, bbox_inches='tight')
            plt.close()


def create_cost_conversion_table(df_macc):
    """
    Create table with multiple cost units for easy understanding

    Args:
        df_macc: MACC results dataframe

    Returns:
        DataFrame with multiple cost representations
    """
    tracker = RegionalEnergyTracker()
    df_converted = tracker.add_alternative_cost_units(df_macc)

    # Select snapshot years
    df_snapshot = df_converted[df_converted['year'].isin([2025, 2030, 2040, 2050])].copy()

    # Create readable table
    cost_table = df_snapshot[[
        'year', 'technology',
        'total_cost_usd_per_tco2',
        'cost_usd_per_ton_ethylene',
        'cost_krw_per_ton_ethylene',
        'cost_usd_per_boe',
        'abatement_potential_mtco2'
    ]].copy()

    # Round for readability
    cost_table['total_cost_usd_per_tco2'] = cost_table['total_cost_usd_per_tco2'].round(0)
    cost_table['cost_usd_per_ton_ethylene'] = cost_table['cost_usd_per_ton_ethylene'].round(0)
    cost_table['cost_krw_per_ton_ethylene'] = cost_table['cost_krw_per_ton_ethylene'].round(0)
    cost_table['cost_usd_per_boe'] = cost_table['cost_usd_per_boe'].round(0)
    cost_table['abatement_potential_mtco2'] = cost_table['abatement_potential_mtco2'].round(2)

    # Rename for clarity
    cost_table.columns = [
        'Year', 'Technology',
        'Cost ($/tCO2)',
        'Cost ($/ton ethylene)',
        'Cost (₩/ton ethylene)',
        'Cost ($/boe)',
        'Abatement (MtCO2)'
    ]

    return cost_table
