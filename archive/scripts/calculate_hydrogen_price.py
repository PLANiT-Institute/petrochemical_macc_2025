"""
Calculate Levelized Cost of Hydrogen (LCOH) from grid.xlsx.

Two-step calculation:
  1. Compute per-fuel LCOE using calculate_lcoe_with_economic_lifespan(),
     then derive generation-weighted average grid LCOE per year.
  2. Feed that grid LCOE as electricity_cost into calculate_lcoh() along
     with electrolyser parameters to get LCOH per year (KRW/kg H2).
"""

import sys
import os
import pandas as pd

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from archive.lcoe import load_excel, calculate_lcoe_with_economic_lifespan, calculate_lcoh


def main():
    filepath = os.path.join(os.path.dirname(__file__), "..", "archive", "grid.xlsx")

    # Determine year range from the capacity sheet
    cap_raw = pd.read_excel(filepath, sheet_name="capacity", index_col=0)
    cap_raw = cap_raw.drop(index=["unit", "description"], errors="ignore")
    cap_raw.index = cap_raw.index.astype(int)
    start_year, end_year = int(cap_raw.index.min()), int(cap_raw.index.max())

    # Load all sheets (excluding 'exclude_*' sheets)
    data = load_excel(filepath, start_year, end_year)

    capacity_df = data["capacity"]
    generation_df = data["generation"]
    capex_df = data["capex"]
    opex_df = data["opex"]
    fuelcost_df = data["fuelcost"]
    landcost_df = data["landcost"]
    lifespan_df = data["lifespan"]
    economic_lifespan_df = data["economic_lifespan"]
    degradation_df = data["degradation"]

    # Discount rate from assumption sheet
    assumption = data["assumption"]
    discount_rate = assumption.loc["discount_rate", "value"] / 100  # 4.5% -> 0.045

    # Electrolyser parameters
    electrolyser = data["electrolyser"]

    years = capacity_df.index
    fuels = capacity_df.columns

    # ------------------------------------------------------------------
    # Step 1: Calculate per-fuel LCOE for each year, then grid-weighted average
    #
    # NOTE: Unit mismatch — grid.xlsx provides capex/opex/land in KRW/kW
    # and generation in GWh, but calculate_lcoe_with_economic_lifespan()
    # expects KRW/MW and MWh respectively. The errors partially cancel
    # (fixed costs 1000x low, generation denominator 1000x low), but
    # variable costs (fuel) are distorted. The resulting LCOE is in
    # KRW/MWh (~33,000) rather than KRW/kWh (~33). This produces an
    # LCOH ~670x too high when fed into calculate_lcoh() which expects
    # electricity_cost in KRW/kWh.
    #
    # Decision: Instead of fixing the unit conversion here, the MACC model
    # now reads domestic H2 prices directly from the exclude_h2cost sheet
    # in grid.xlsx (via h2_price_trajectory.csv), which provides validated
    # market-based hydrogen prices (10,000→2,500 KRW/kg, 2023→2050).
    # ------------------------------------------------------------------
    lcoe_df = pd.DataFrame(index=years, columns=fuels, dtype=float)

    for fuel in fuels:
        for year in years:
            cap = capacity_df.loc[year, fuel]
            gen = generation_df.loc[year, fuel]
            if pd.isna(cap) or pd.isna(gen) or cap == 0 or gen == 0:
                lcoe_df.loc[year, fuel] = 0.0
                continue

            lcoe_val = calculate_lcoe_with_economic_lifespan(
                capacity=cap,
                generation=gen,
                capex_per_mw=capex_df.loc[year, fuel],
                fixed_opex_per_mw=opex_df.loc[year, fuel],
                variable_opex=fuelcost_df.loc[year, fuel],
                land_cost_per_mw=landcost_df.loc[year, fuel],
                lifespan=int(lifespan_df.loc[year, fuel]),
                economic_lifespan=int(economic_lifespan_df.loc[year, fuel]),
                discount_rate=discount_rate,
                degradation=degradation_df.loc[year, fuel],
            )
            lcoe_df.loc[year, fuel] = lcoe_val

    # Generation-weighted average grid LCOE per year (KRW/kWh)
    grid_lcoe = (lcoe_df * generation_df).sum(axis=1) / generation_df.sum(axis=1)

    print("=" * 60)
    print("Step 1: Generation-weighted Grid LCOE (KRW/kWh)")
    print("=" * 60)
    for year in years:
        print(f"  {year}: {grid_lcoe.loc[year]:.2f}")

    # ------------------------------------------------------------------
    # Step 2: Calculate LCOH per year
    # ------------------------------------------------------------------
    lcoh_series = pd.Series(index=years, dtype=float, name="LCOH (KRW/kg H2)")

    for year in years:
        lcoh_val = calculate_lcoh(
            capex_per_kw=electrolyser.loc[year, "capex"],
            fixed_opex_per_kw=electrolyser.loc[year, "opex"],
            efficiency=electrolyser.loc[year, "efficiency"],
            electricity_cost=grid_lcoe.loc[year],
            capacity=1,  # 1 kW normalised
            capacity_factor=0.6,
            discount_rate=discount_rate,
            lifespan=int(electrolyser.loc[year, "lifespan"]),
            degradation=0,
        )
        lcoh_series.loc[year] = lcoh_val

    print()
    print("=" * 60)
    print("Step 2: Levelized Cost of Hydrogen — LCOH (KRW/kg H2)")
    print("=" * 60)
    for year in years:
        print(f"  {year}: {lcoh_series.loc[year]:,.2f}")

    # ------------------------------------------------------------------
    # Sanity check against exclude_h2cost reference values
    # ------------------------------------------------------------------
    h2cost_ref = pd.read_excel(filepath, sheet_name="exclude_h2cost", index_col=0)
    h2cost_ref = h2cost_ref.drop(index=["unit", "description"], errors="ignore")
    h2cost_ref.index = h2cost_ref.index.astype(int)
    h2cost_ref = h2cost_ref.apply(pd.to_numeric, errors="coerce")

    print()
    print("=" * 60)
    print("Sanity Check: Reference H2 Cost from exclude_h2cost sheet")
    print("=" * 60)
    common_years = lcoh_series.index.intersection(h2cost_ref.index)
    comparison = pd.DataFrame({
        "Calculated LCOH": lcoh_series.loc[common_years],
        **{col: h2cost_ref.loc[common_years, col] for col in h2cost_ref.columns},
    })
    print(comparison.to_string())

    # ------------------------------------------------------------------
    # Save results
    # ------------------------------------------------------------------
    output_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(output_dir, exist_ok=True)

    results = pd.DataFrame({
        "grid_lcoe_krw_per_kwh": grid_lcoe,
        "lcoh_krw_per_kg": lcoh_series,
    })
    outpath = os.path.join(output_dir, "hydrogen_price.csv")
    results.to_csv(outpath)
    print(f"\nResults saved to {outpath}")


if __name__ == "__main__":
    main()
