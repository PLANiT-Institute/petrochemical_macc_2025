"""
Generate a 2-panel figure showing electricity and hydrogen price scenarios.

Top panel:  Electricity price trajectories (Rising vs Flat)
Bottom panel: Hydrogen price trajectories (Rising+Coupled, Flat+Coupled, Decoupled)

Uses PriceCalculator from modules/utils.py to compute coupled H2 prices,
ensuring the figure shows exactly the prices the MACC model uses.
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.utils import PriceCalculator, DataLoader, save_figure_data
from modules.figure_style import apply_style, save_figure


def main():
    apply_style()
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    loader = DataLoader(data_dir)

    # Load price data
    grid_prices = loader.load_grid_prices()       # Rising electricity
    flat_prices = loader.load_flat_elec_prices()   # Flat electricity
    h2_prices = loader.load_h2_prices()            # Decoupled H2
    re_prices = loader.load_re_prices()            # RE PPA (needed for PriceCalculator)
    electrolyser_params = loader.load_electrolyser_params()

    years = list(range(2025, 2051))

    # --- Electricity trajectories ---
    elec_rising = [
        np.interp(y, grid_prices['year'], grid_prices['grid_price_usd_per_mwh'])
        for y in years
    ]
    elec_flat = [
        np.interp(y, flat_prices['year'], flat_prices['elec_price_usd_per_mwh'])
        for y in years
    ]

    # --- Hydrogen trajectories ---
    # 1. Decoupled (domestic trajectory from CSV)
    h2_decoupled = [
        np.interp(y, h2_prices['year'], h2_prices['h2_price_usd_per_kg'])
        for y in years
    ]

    # 2. Rising + Coupled (LCOH from rising electricity via PriceCalculator)
    pc_rising = PriceCalculator(
        h2_prices_df=h2_prices,
        re_prices_df=re_prices,
        elec_prices_df=grid_prices.rename(columns={'grid_price_usd_per_mwh': 'elec_price_usd_per_mwh'}),
        electrolyser_params_df=electrolyser_params,
        price_scenario='coupled',
    )
    h2_rising_coupled = [pc_rising.get_h2_price(y) for y in years]

    # 3. Flat + Coupled (LCOH from flat electricity via PriceCalculator)
    pc_flat = PriceCalculator(
        h2_prices_df=h2_prices,
        re_prices_df=re_prices,
        elec_prices_df=flat_prices,
        electrolyser_params_df=electrolyser_params,
        price_scenario='coupled',
    )
    h2_flat_coupled = [pc_flat.get_h2_price(y) for y in years]

    # --- Plot ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Top panel: Electricity prices
    ax1.plot(years, elec_rising, 'o-', color='#d62728', markersize=3, linewidth=1.5,
             label=f'Rising (${elec_rising[0]:.0f}' + u'\u2192' + f'${elec_rising[-1]:.0f}/MWh)')
    ax1.plot(years, elec_flat, 's-', color='#1f77b4', markersize=3, linewidth=1.5,
             label=f'Flat (${elec_flat[0]:.0f}/MWh)')
    ax1.set_ylabel('Electricity Price ($/MWh)')
    ax1.set_title('Electricity Price Scenarios (2025\u20132050)')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # Bottom panel: Hydrogen prices
    ax2.plot(years, h2_rising_coupled, 'o-', color='#d62728', markersize=3, linewidth=1.5,
             label=f'Rising + Coupled (LCOH)')
    ax2.plot(years, h2_flat_coupled, 's-', color='#1f77b4', markersize=3, linewidth=1.5,
             label=f'Flat + Coupled (LCOH)')
    ax2.plot(years, h2_decoupled, '^-', color='#2ca02c', markersize=3, linewidth=1.5,
             label=f'Decoupled / Domestic (${h2_decoupled[0]:.2f}' + u'\u2192' + f'${h2_decoupled[-1]:.2f}/kg)')
    ax2.set_ylabel('Hydrogen Price ($/kg)')
    ax2.set_xlabel('Year')
    ax2.set_title('Hydrogen Price Scenarios (2025\u20132050)')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    # Save
    output_dir = os.path.join(os.path.dirname(__file__), "..", "outputs", "figures")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "price_scenarios_elec_h2.png")
    save_figure(fig, output_path)
    print(f"Saved: {output_path}")

    # CSV export
    rows = []
    for yr, val in zip(years, elec_rising):
        rows.append({'year': yr, 'category': 'Electricity Rising', 'value': val, 'unit': 'USD_per_MWh', 'panel': 'A'})
    for yr, val in zip(years, elec_flat):
        rows.append({'year': yr, 'category': 'Electricity Flat', 'value': val, 'unit': 'USD_per_MWh', 'panel': 'A'})
    for yr, val in zip(years, h2_rising_coupled):
        rows.append({'year': yr, 'category': 'H2 Rising+Coupled', 'value': val, 'unit': 'USD_per_kg', 'panel': 'B'})
    for yr, val in zip(years, h2_flat_coupled):
        rows.append({'year': yr, 'category': 'H2 Flat+Coupled', 'value': val, 'unit': 'USD_per_kg', 'panel': 'B'})
    for yr, val in zip(years, h2_decoupled):
        rows.append({'year': yr, 'category': 'H2 Decoupled', 'value': val, 'unit': 'USD_per_kg', 'panel': 'B'})
    import pandas as _pd
    save_figure_data(_pd.DataFrame(rows), output_path, figure_type='line')


if __name__ == "__main__":
    main()
