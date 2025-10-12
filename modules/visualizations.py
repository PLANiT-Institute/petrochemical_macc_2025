"""
ENHANCED VISUALIZATIONS MODULE
Additional visualization capabilities for transition analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from .utils import save_plot


class TransitionVisualizer:
    """
    Enhanced visualizations for industry transition
    - Energy mix transition over time
    - Investment timeline and requirements
    - Technology deployment schedules
    - Facility transition waterfall charts
    """

    def __init__(self, output_dir='outputs/visualizations'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_energy_transition(self, df_deployment, df_baseline, save_path=None):
        """
        Visualize energy mix transition over time
        Shows how fuel sources change from fossil to electric/H2
        """
        print("\n📊 Creating energy transition visualization...")

        # Calculate energy mix for each year
        years = sorted(df_deployment['year'].unique())
        energy_mix = []

        baseline_total_fossil = (
            df_baseline['naphtha_gj_per_year'].sum() +
            df_baseline['lng_gj_per_year'].sum() +
            df_baseline['fuel_gas_gj_per_year'].sum() +
            df_baseline['lpg_gj_per_year'].sum() +
            df_baseline['fuel_oil_gj_per_year'].sum() +
            df_baseline['diesel_gj_per_year'].sum()
        )
        baseline_total_elec = df_baseline['electricity_kwh_per_year'].sum() / 3.6  # Convert to GJ

        for _, row in df_deployment.iterrows():
            year = row['year']

            # Get technology adoption levels from columns
            hp_deployed = row.get('heat_pump_mt', 0)
            h2_deployed = row.get('ncc_h2_mt', 0)
            elec_deployed = row.get('ncc_elec_mt', 0)

            # Rough conversion: 1 MtCO2 abated ≈ 67 PJ fossil fuel replaced (using EF=0.0149 tCO2/GJ)
            ef_fossil = 0.0149
            fossil_replaced_gj = (hp_deployed + h2_deployed + elec_deployed) * 1e6 / ef_fossil

            # Remaining fossil fuel
            fossil_remaining = max(0, baseline_total_fossil - fossil_replaced_gj)

            # Heat pump electricity (additional)
            hp_electricity = fossil_replaced_gj / 4.0  # Assuming COP=4

            # Electric cracker electricity (replaces fossil)
            elec_cracker_electricity = elec_deployed * 1e6 / ef_fossil

            # H2 consumption (replaces fossil)
            h2_consumption = h2_deployed * 1e6 / ef_fossil

            energy_mix.append({
                'year': year,
                'fossil_fuels_pj': fossil_remaining / 1000,  # Convert GJ to PJ
                'h2_pj': h2_consumption / 1000,
                'renewable_electricity_pj': (baseline_total_elec + hp_electricity + elec_cracker_electricity) / 1000,
            })

        df_mix = pd.DataFrame(energy_mix)

        # Create stacked area chart
        fig, ax = plt.subplots(figsize=(14, 8))

        ax.fill_between(df_mix['year'], 0, df_mix['fossil_fuels_pj'],
                       label='Fossil Fuels (Naphtha, LNG, etc.)', color='#8B4513', alpha=0.8)
        ax.fill_between(df_mix['year'], df_mix['fossil_fuels_pj'],
                       df_mix['fossil_fuels_pj'] + df_mix['h2_pj'],
                       label='Hydrogen', color='#3498DB', alpha=0.8)
        ax.fill_between(df_mix['year'], df_mix['fossil_fuels_pj'] + df_mix['h2_pj'],
                       df_mix['fossil_fuels_pj'] + df_mix['h2_pj'] + df_mix['renewable_electricity_pj'],
                       label='Renewable Electricity', color='#2ECC71', alpha=0.8)

        ax.set_xlabel('Year', fontsize=14, fontweight='bold')
        ax.set_ylabel('Energy Consumption (PJ/year)', fontsize=14, fontweight='bold')
        ax.set_title('Industry Energy Transition (2025-2050)\nFossil Fuels → Clean Energy',
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=12, framealpha=0.95, edgecolor='black')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(years[0], years[-1])

        if save_path:
            save_plot(fig, save_path)
        else:
            save_plot(fig, self.output_dir / 'energy_transition.png')

        return fig

    def plot_investment_timeline(self, df_deployment, save_path=None):
        """
        Visualize cumulative investment requirements
        """
        print("\n💰 Creating investment timeline visualization...")

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 7))

        # Plot cumulative investment
        years = df_deployment['year']
        cumulative_capex = df_deployment['cumulative_capex_musd']

        ax.fill_between(years, 0, cumulative_capex, alpha=0.3, color='#1f77b4')
        ax.plot(years, cumulative_capex, linewidth=3, color='#1f77b4', marker='o', markersize=5)

        # Add value labels at key years
        for year in [2025, 2030, 2040, 2050]:
            if year in years.values:
                val = df_deployment[df_deployment['year'] == year]['cumulative_capex_musd'].iloc[0]
                ax.text(year, val, f'${val:,.0f}M', fontsize=10, ha='center', va='bottom', fontweight='bold')

        ax.set_xlabel('Year', fontsize=13, fontweight='bold')
        ax.set_ylabel('Cumulative Investment (Million USD)', fontsize=13, fontweight='bold')
        ax.set_title('Cumulative Technology Investment (2025-2050)', fontsize=15, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')

        plt.tight_layout()

        if save_path:
            save_plot(fig, save_path)
        else:
            save_plot(fig, self.output_dir / 'investment_timeline.png')

        return fig

    def plot_technology_deployment(self, df_deployment, save_path=None):
        """
        Visualize technology deployment schedule (cumulative abatement)
        """
        print("\n🔧 Creating technology deployment visualization...")

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))

        colors = {'heat_pump_mt': '#2ECC71', 'ncc_h2_mt': '#3498DB', 'ncc_elec_mt': '#E74C3C', 're_ppa_mt': '#F39C12'}
        labels = {'heat_pump_mt': 'Heat Pump', 'ncc_h2_mt': 'NCC-H2', 'ncc_elec_mt': 'NCC-Electricity', 're_ppa_mt': 'RE PPA'}
        markers = {'heat_pump_mt': 'o', 'ncc_h2_mt': 'D', 'ncc_elec_mt': '^', 're_ppa_mt': 's'}

        for col in ['heat_pump_mt', 'ncc_h2_mt', 'ncc_elec_mt', 're_ppa_mt']:
            if col in df_deployment.columns:
                ax.plot(df_deployment['year'], df_deployment[col],
                       linewidth=3, marker=markers.get(col, 'o'), markersize=7,
                       label=labels.get(col, col), color=colors.get(col, 'gray'), alpha=0.9)

        ax.set_xlabel('Year', fontsize=14, fontweight='bold')
        ax.set_ylabel('Abatement (MtCO2/year)', fontsize=14, fontweight='bold')
        ax.set_title('Technology Deployment Schedule',
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=12, framealpha=0.95, edgecolor='black')
        ax.grid(True, alpha=0.3, linestyle='--')

        if save_path:
            save_plot(fig, save_path)
        else:
            save_plot(fig, self.output_dir / 'technology_deployment.png')

        return fig

    def plot_facility_transition_waterfall(self, df_baseline, df_allocation, year=2050, save_path=None):
        """
        Waterfall chart showing emission reduction pathway
        """
        print(f"\n📊 Creating facility transition waterfall for {year}...")

        # Get total abatement by technology from allocation file
        tech_abatement = df_allocation.groupby('technology')['abatement_kt'].sum() / 1000  # Convert to Mt

        # Create waterfall data
        fig, ax = plt.subplots(figsize=(14, 8))

        x_pos = 0
        x_labels = []
        x_positions = []

        # Start with total baseline
        baseline_total = df_baseline['total_emissions_kt'].sum() / 1000  # Mt
        current = baseline_total
        ax.bar(x_pos, current, color='#E74C3C', alpha=0.8, edgecolor='black', linewidth=1.2, width=0.8)
        x_labels.append(f'Baseline\n{baseline_total:.1f} Mt')
        x_positions.append(x_pos)
        x_pos += 1

        # Show reductions by technology
        tech_colors = {'Heat_Pump': '#2ECC71', 'NCC-H2': '#3498DB', 'NCC-Electricity': '#9B59B6', 'RE_PPA': '#F39C12'}

        for tech in ['Heat_Pump', 'NCC-H2', 'NCC-Electricity', 'RE_PPA']:
            if tech in tech_abatement.index:
                reduction = tech_abatement[tech]
                if reduction > 0:
                    ax.bar(x_pos, -reduction, bottom=current, color=tech_colors.get(tech, 'gray'),
                          alpha=0.8, edgecolor='black', linewidth=1.2, width=0.8)
                    current -= reduction
                    x_labels.append(f'{tech.replace("_", " ")}\n-{reduction:.1f} Mt')
                    x_positions.append(x_pos)
                    x_pos += 1

        # Final emissions
        ax.bar(x_pos, current, color='#2ECC71', alpha=0.8, edgecolor='black', linewidth=1.2, width=0.8)
        x_labels.append(f'Final {year}\n{current:.1f} Mt')
        x_positions.append(x_pos)

        ax.set_xticks(x_positions)
        ax.set_xticklabels(x_labels, fontsize=11)
        ax.set_ylabel('Emissions (MtCO2/year)', fontsize=14, fontweight='bold')
        ax.set_title(f'Emission Reduction Pathway: Baseline → {year}\nWaterfall by Technology',
                    fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1)

        if save_path:
            save_plot(fig, save_path)
        else:
            save_plot(fig, self.output_dir / f'facility_transition_waterfall_{year}.png')

        return fig

    def plot_capacity_growth(self, df_trajectory, save_path=None):
        """
        Visualize capacity growth over time
        """
        print("\n📈 Creating capacity growth visualization...")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # 1. Total capacity over time
        ax1.plot(df_trajectory['year'], df_trajectory['total_capacity_kt'],
                linewidth=3, color='#1f77b4', marker='o', markersize=6)
        ax1.fill_between(df_trajectory['year'], 0, df_trajectory['total_capacity_kt'],
                        alpha=0.3, color='#1f77b4')
        ax1.set_xlabel('Year', fontsize=13, fontweight='bold')
        ax1.set_ylabel('Total Capacity (kt/year)', fontsize=13, fontweight='bold')
        ax1.set_title('Industry Capacity Growth (2025-2050)', fontsize=15, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')

        # Add value labels
        for year in [2025, 2030, 2040, 2050]:
            if year in df_trajectory['year'].values:
                val = df_trajectory[df_trajectory['year'] == year]['total_capacity_kt'].iloc[0]
                ax1.text(year, val, f'{val:,.0f} kt', fontsize=9, ha='center', va='bottom')

        # 2. Capacity multiplier
        ax2.plot(df_trajectory['year'], df_trajectory['capacity_multiplier'],
                linewidth=3, color='#E74C3C', marker='s', markersize=6)
        ax2.fill_between(df_trajectory['year'], 1, df_trajectory['capacity_multiplier'],
                        alpha=0.3, color='#E74C3C')
        ax2.axhline(y=1, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax2.set_xlabel('Year', fontsize=13, fontweight='bold')
        ax2.set_ylabel('Capacity Multiplier (2025 = 1.0)', fontsize=13, fontweight='bold')
        ax2.set_title('Relative Capacity Growth', fontsize=15, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')

        # Add percentage labels
        for year in [2025, 2030, 2040, 2050]:
            if year in df_trajectory['year'].values:
                val = df_trajectory[df_trajectory['year'] == year]['capacity_multiplier'].iloc[0]
                pct = (val - 1) * 100
                ax2.text(year, val, f'+{pct:.1f}%', fontsize=9, ha='center', va='bottom')

        plt.tight_layout()

        if save_path:
            save_plot(fig, save_path)
        else:
            save_plot(fig, self.output_dir / 'capacity_growth.png')

        return fig
