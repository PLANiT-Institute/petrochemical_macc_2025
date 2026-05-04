#!/usr/bin/env python3
"""
Calculate Levelized Cost of Hydrogen (LCOH) from electrolyser parameters
and electricity price trajectories.

Outputs:
  - outputs/hydrogen_price.csv              (full LCOH results for both price trajectories)
  - data/assumptions/prices/h2_price_trajectory.csv  (overwrites with flat-scenario LCOH as default)
  - outputs/figures/h2_price_comparison.png  (comparison figure)

Uses the same CRF-based formula as modules/utils.py:get_coupled_h2_price().
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "assumptions" / "prices"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"

ELECTROLYSER_CSV = DATA_DIR / "electrolyser_params.csv"
ELEC_FLAT_CSV = DATA_DIR / "elec_price_flat.csv"
ELEC_RISING_CSV = DATA_DIR / "re_price_trajectory.csv"
H2_TRAJ_CSV = DATA_DIR / "h2_price_trajectory.csv"
OUTPUT_CSV = OUTPUT_DIR / "hydrogen_price.csv"
OUTPUT_FIG = FIGURES_DIR / "h2_price_comparison.png"


# ---------------------------------------------------------------------------
# LCOH calculation (mirrors modules/utils.py:get_coupled_h2_price)
# ---------------------------------------------------------------------------

def calculate_lcoh(capex: float, opex: float, efficiency: float,
                   lifespan: int, cf: float, dr: float,
                   elec_price_mwh: float) -> float:
    """Return LCOH in $/kg H2.

    Parameters
    ----------
    capex : float          USD/kW electrolyser capital cost
    opex : float           USD/kW/yr fixed O&M
    efficiency : float     kWh per kg H2
    lifespan : int         years
    cf : float             capacity factor (0–1)
    dr : float             discount rate (0–1)
    elec_price_mwh : float electricity price in USD/MWh
    """
    # Capital Recovery Factor
    if dr > 0 and lifespan > 0:
        crf = (dr * (1 + dr) ** lifespan) / ((1 + dr) ** lifespan - 1)
    else:
        crf = 1.0 / lifespan if lifespan > 0 else 1.0

    annualized_capex = capex * crf                          # $/kW/yr

    annual_elec_kwh_per_kw = cf * 8760                      # kWh/yr per kW
    annual_h2_kg_per_kw = annual_elec_kwh_per_kw / efficiency  # kg/yr per kW

    # Key unit fix: convert $/MWh → $/kWh
    elec_cost_per_kw_yr = annual_elec_kwh_per_kw * (elec_price_mwh / 1000.0)

    total_cost_per_kw_yr = annualized_capex + opex + elec_cost_per_kw_yr
    return total_cost_per_kw_yr / annual_h2_kg_per_kw


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Load input data
    params = pd.read_csv(ELECTROLYSER_CSV)
    elec_flat = pd.read_csv(ELEC_FLAT_CSV)
    elec_rising = pd.read_csv(ELEC_RISING_CSV)

    years = params["year"].values
    records = []

    for _, row in params.iterrows():
        yr = int(row["year"])
        capex = row["capex_usd_per_kw"]
        opex = row["opex_usd_per_kw_yr"]
        eff = row["efficiency_kwh_per_kg"]
        life = int(row["lifespan_years"])
        cf = row["capacity_factor"]
        dr = row["discount_rate"]

        # Flat electricity price
        flat_row = elec_flat[elec_flat["year"] == yr]
        if len(flat_row) > 0:
            ep_flat = flat_row["elec_price_usd_per_mwh"].iloc[0]
        else:
            ep_flat = np.interp(yr, elec_flat["year"], elec_flat["elec_price_usd_per_mwh"])

        # Rising (declining RE) electricity price
        rising_row = elec_rising[elec_rising["year"] == yr]
        if len(rising_row) > 0:
            ep_rising = rising_row["re_price_usd_per_mwh"].iloc[0]
        else:
            ep_rising = np.interp(yr, elec_rising["year"], elec_rising["re_price_usd_per_mwh"])

        lcoh_flat = calculate_lcoh(capex, opex, eff, life, cf, dr, ep_flat)
        lcoh_rising = calculate_lcoh(capex, opex, eff, life, cf, dr, ep_rising)

        records.append({
            "year": yr,
            "lcoh_flat_usd_per_kg": round(lcoh_flat, 6),
            "lcoh_rising_usd_per_kg": round(lcoh_rising, 6),
            "elec_flat_usd_per_mwh": round(ep_flat, 2),
            "elec_rising_usd_per_mwh": round(ep_rising, 2),
        })

    df = pd.DataFrame(records)

    # --- Save full output CSV ---
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"  Saved: {OUTPUT_CSV}")

    # --- Overwrite h2_price_trajectory.csv with flat-scenario LCOH ---
    h2_traj = pd.DataFrame({
        "year": df["year"],
        "h2_price_usd_per_kg": df["lcoh_flat_usd_per_kg"],
        "source": "LCOH calculation (electrolyser_params + elec_price_flat)",
        "notes": "CRF-based LCOH using flat electricity price trajectory",
    })
    h2_traj.to_csv(H2_TRAJ_CSV, index=False)
    print(f"  Saved: {H2_TRAJ_CSV}")

    # --- Print comparison table ---
    print("\n  LCOH Comparison ($/kg H2):")
    print(f"  {'Year':>6}  {'Flat Elec':>10}  {'Rising Elec':>12}  {'Old Domestic':>13}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*12}  {'-'*13}")

    # Old domestic prices for comparison
    old_domestic = {
        2025: 4.615, 2030: 2.692, 2035: 2.500, 2040: 2.308, 2045: 2.115, 2050: 1.923
    }
    for _, row in df.iterrows():
        yr = int(row["year"])
        if yr % 5 == 0:
            old = old_domestic.get(yr, "")
            old_str = f"${old:.2f}" if old else ""
            print(f"  {yr:>6}  ${row['lcoh_flat_usd_per_kg']:>8.2f}  "
                  f"${row['lcoh_rising_usd_per_kg']:>10.2f}  {old_str:>13}")

    # --- Generate comparison figure ---
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        sys.path.insert(0, str(PROJECT_ROOT))
        from modules.figure_style import apply_style, save_figure
        apply_style()

        fig, ax = plt.subplots(figsize=(7, 4))

        ax.plot(df["year"], df["lcoh_flat_usd_per_kg"],
                color="#2E86AB", linewidth=2, label="LCOH (Flat electricity)")
        ax.plot(df["year"], df["lcoh_rising_usd_per_kg"],
                color="#A23B72", linewidth=2, label="LCOH (Declining RE)")

        # Old domestic trajectory for reference
        old_years = sorted(old_domestic.keys())
        old_prices = [old_domestic[y] for y in old_years]
        ax.plot(old_years, old_prices, color="#808080", linewidth=1.5,
                linestyle="--", marker="o", markersize=3,
                label="Old domestic market price")

        ax.set_xlabel("Year")
        ax.set_ylabel("H$_2$ Price (USD/kg)")
        ax.set_title("Hydrogen Price Trajectories: LCOH vs Old Domestic Market")
        ax.legend(loc="upper right")
        ax.set_xlim(2025, 2050)

        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        save_figure(fig, OUTPUT_FIG)
        print(f"\n  Saved: {OUTPUT_FIG}")

    except Exception as exc:
        print(f"\n  Warning: Could not generate figure: {exc}")


if __name__ == "__main__":
    main()
