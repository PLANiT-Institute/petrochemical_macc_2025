"""
Generate 6 CSV summary files from MACC model outputs.

Usage: python scripts/generate_csv_exports.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
KRW_PER_USD = 1300
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs" / "csv_exports"
# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SCENARIO_ORDER = [
    "shaheen_ncc_h2_rising_coupled",
    "shaheen_ncc_h2_rising_decoupled",
    "shaheen_ncc_h2_flat_coupled",
    "shaheen_ncc_h2_flat_decoupled",
    "shaheen_ncc_elec_rising_coupled",
    "shaheen_ncc_elec_rising_decoupled",
    "shaheen_ncc_elec_flat_coupled",
    "shaheen_ncc_elec_flat_decoupled",
]

COMPANY_NAME_MAP = {
    "Lotte Chemical": "롯데케미칼",
    "LG Chem": "LG화학",
    "Hanwha TotalEnergies": "한화솔루션",
    "SK Geocentric": "SK지오센트릭",
    "S-Oil": "에쓰오일",
    "Daehan Oil Chemical": "대한유화",
    "Yeochon NCC": "여천NCC",
    "HD Hyundai Chemical": "HD현대케미칼",
    "GS Caltex": "GS칼텍스",
    "S-Oil Shaheen": "에쓰오일 샤힌",
    "SK Advanced": "SK어드밴스드",
    "SK Energy": "SK에너지",
    "HDHyundai Oilbank": "HD현대오일뱅크",
    "Kumho Petrochemical": "금호석유화학",
    "Lotte GS Chemical": "롯데GS화학",
    "Hyosung Chemical": "효성화학",
    "Taekwang Industrial": "태광산업",
    "Caprolactam": "카프로락탐",
}

REGION_MAP = {
    "Daesan": "대산",
    "Yeosu": "여수",
    "Ulsan": "울산",
}


def _parse_scenario(scenario: str):
    """Extract technology_path and price_variant from scenario name."""
    # e.g. shaheen_ncc_h2_rising_coupled -> h2, rising_coupled
    parts = scenario.replace("shaheen_ncc_", "")
    if parts.startswith("h2_"):
        tech = "NCC-H2"
        pv = parts[3:]  # rising_coupled, etc.
    elif parts.startswith("elec_"):
        tech = "NCC-Elec"
        pv = parts[5:]
    else:
        tech = parts
        pv = ""
    return tech, pv


def usd_to_billion_won(usd):
    return usd * KRW_PER_USD / 1e9


def usd_to_million_usd(usd):
    return usd / 1e6


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
def load_data():
    sr = pd.read_csv(BASE_DIR / "outputs" / "scenario_results.csv")
    table1 = pd.read_csv(
        BASE_DIR / "outputs" / "report_tables" / "table1_scenario_comparison.csv",
        encoding="utf-8-sig",
    )
    table2_summary = pd.read_csv(
        BASE_DIR / "outputs" / "report_tables" / "table2_stranded_summary.csv",
        encoding="utf-8-sig",
    )
    table2_facility = pd.read_csv(
        BASE_DIR / "outputs" / "report_tables" / "table2_ncc_facility_details.csv",
        encoding="utf-8-sig",
    )
    table2_company = pd.read_csv(
        BASE_DIR / "outputs" / "report_tables" / "table2_2_company_stranded.csv",
        encoding="utf-8-sig",
    )
    h2_prices = pd.read_csv(BASE_DIR / "outputs" / "hydrogen_price.csv")
    grid_price = pd.read_csv(
        BASE_DIR / "data" / "assumptions" / "prices" / "grid_price_trajectory.csv"
    )
    flat_elec = pd.read_csv(
        BASE_DIR / "data" / "assumptions" / "prices" / "elec_price_flat.csv"
    )
    h2_traj = pd.read_csv(
        BASE_DIR / "data" / "assumptions" / "prices" / "h2_price_trajectory.csv"
    )
    fac_db = pd.read_csv(
        BASE_DIR / "data" / "assets" / "facility_database_with_shaheen.csv"
    )
    return dict(
        sr=sr,
        table1=table1,
        table2_summary=table2_summary,
        table2_facility=table2_facility,
        table2_company=table2_company,
        h2_prices=h2_prices,
        grid_price=grid_price,
        flat_elec=flat_elec,
        h2_traj=h2_traj,
        fac_db=fac_db,
    )


# ---------------------------------------------------------------------------
# FILE 1: scenario_total_cost.csv
# ---------------------------------------------------------------------------
def gen_file1(sr, table1, **kw):
    """8 rows: one per scenario with total cost breakdown."""
    # Deduplicated CAPEX: take capex_usd at install year only (initial investment)
    install_rows = sr.dropna(subset=["install_year"]).copy()
    install_rows = install_rows[install_rows["year"] == install_rows["install_year"]]
    capex_dedup = (
        install_rows.drop_duplicates(subset=["scenario", "facility_id"])
        .groupby("scenario")["capex_usd"]
        .sum()
        .rename("total_capex_usd")
    )

    # Total cost components summed over all years
    cost_agg = sr.groupby("scenario").agg(
        total_opex_usd=("cost_component_opex_annual_usd", "sum"),
        total_cost_usd_components=("total_cost_usd", "sum"),
        capex_annual_sum=("cost_component_capex_annual_usd", "sum"),
        new_energy_sum=("cost_component_new_energy_usd", "sum"),
        fuel_savings_sum=("cost_component_fuel_savings_usd", "sum"),
    )

    # total_cost = capex_annual + opex + new_energy - fuel_savings
    cost_agg["total_cost_usd"] = (
        cost_agg["capex_annual_sum"]
        + cost_agg["total_opex_usd"]
        + cost_agg["new_energy_sum"]
        - cost_agg["fuel_savings_sum"]
    )

    df = cost_agg.join(capex_dedup).reset_index()
    df["total_capex_usd"] = df["total_capex_usd"].fillna(0)

    # Parse scenario metadata
    df["technology_path"] = df["scenario"].apply(lambda s: _parse_scenario(s)[0])
    df["price_variant"] = df["scenario"].apply(lambda s: _parse_scenario(s)[1])

    # Convert
    df["total_cost_billion_won"] = usd_to_billion_won(df["total_cost_usd"])
    df["total_capex_billion_won"] = usd_to_billion_won(df["total_capex_usd"])
    df["total_opex_billion_won"] = usd_to_billion_won(df["total_opex_usd"])
    df["total_cost_million_usd"] = usd_to_million_usd(df["total_cost_usd"])

    cols = [
        "scenario",
        "technology_path",
        "price_variant",
        "total_cost_billion_won",
        "total_capex_billion_won",
        "total_opex_billion_won",
        "total_cost_million_usd",
    ]
    out = df[cols].copy()
    # Sort by scenario order
    out["_sort"] = out["scenario"].map(
        {s: i for i, s in enumerate(SCENARIO_ORDER)}
    )
    out = out.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)
    out.to_csv(OUTPUT_DIR / "scenario_total_cost.csv", index=False, encoding="utf-8-sig")
    print(f"FILE 1: {len(out)} rows -> scenario_total_cost.csv")

    # Verification: table1 stores sum-of-book-values across years, not initial investment.
    # Our capex is the deduplicated initial investment (install-year capex).
    # Print both for reference.
    for _, row in out.iterrows():
        t1_row = table1[table1["scenario"] == row["scenario"]]
        if len(t1_row) == 0:
            continue
        t1_capex_b_usd = t1_row["total_capex_billion_usd"].values[0]
        my_capex_b_usd = row["total_capex_billion_won"] / KRW_PER_USD  # back to billion USD
        print(
            f"  {row['scenario']}: install_capex={my_capex_b_usd:.2f}B USD, "
            f"table1_book_value_sum={t1_capex_b_usd:.2f}B USD"
        )
    return out


# ---------------------------------------------------------------------------
# FILE 2: company_transition_cost.csv
# ---------------------------------------------------------------------------
def gen_file2(sr, **kw):
    """~160 rows: per company × scenario."""
    # Deduplicated CAPEX per company+scenario: take capex at install year
    install_rows = sr.dropna(subset=["install_year"]).copy()
    install_rows = install_rows[install_rows["year"] == install_rows["install_year"]]
    capex_dedup = (
        install_rows.drop_duplicates(subset=["scenario", "facility_id"])
        .groupby(["company", "scenario"])["capex_usd"]
        .sum()
        .rename("total_capex_usd")
    )

    cost_agg = sr.groupby(["company", "scenario"]).agg(
        total_opex_usd=("cost_component_opex_annual_usd", "sum"),
        capex_annual_sum=("cost_component_capex_annual_usd", "sum"),
        new_energy_sum=("cost_component_new_energy_usd", "sum"),
        fuel_savings_sum=("cost_component_fuel_savings_usd", "sum"),
    )

    cost_agg["transition_cost_usd"] = (
        cost_agg["capex_annual_sum"]
        + cost_agg["total_opex_usd"]
        + cost_agg["new_energy_sum"]
        - cost_agg["fuel_savings_sum"]
    )

    df = cost_agg.join(capex_dedup).reset_index()
    df["total_capex_usd"] = df["total_capex_usd"].fillna(0)

    df["price_variant"] = df["scenario"].apply(lambda s: _parse_scenario(s)[1])

    # Map company names
    df["company"] = df["company"].map(lambda c: COMPANY_NAME_MAP.get(c, c))

    # Remove ghost "0.0" company and all-zero rows
    df = df[df["company"].apply(lambda c: isinstance(c, str) and c != "0.0")]
    df = df[df.groupby("company")["transition_cost_usd"].transform("sum").abs() > 0]

    # Convert
    df["transition_cost_billion_won"] = usd_to_billion_won(df["transition_cost_usd"])
    df["capex_billion_won"] = usd_to_billion_won(df["total_capex_usd"])
    df["opex_billion_won"] = usd_to_billion_won(df["total_opex_usd"])

    cols = [
        "company",
        "scenario",
        "price_variant",
        "transition_cost_billion_won",
        "capex_billion_won",
        "opex_billion_won",
    ]
    out = df[cols].copy()
    out["_sort"] = out["scenario"].map(
        {s: i for i, s in enumerate(SCENARIO_ORDER)}
    )
    out = out.sort_values(["company", "_sort"]).drop(columns="_sort").reset_index(drop=True)
    out.to_csv(OUTPUT_DIR / "company_transition_cost.csv", index=False, encoding="utf-8-sig")
    print(f"FILE 2: {len(out)} rows -> company_transition_cost.csv")
    return out


# ---------------------------------------------------------------------------
# FILE 3: region_transition_cost.csv
# ---------------------------------------------------------------------------
def gen_file3(sr, fac_db, **kw):
    """~24 rows: 3 regions × 8 scenarios (excluding Other)."""
    # Only keep main 3 regions
    main_regions = ["Daesan", "Yeosu", "Ulsan"]
    sr_main = sr[sr["region"].isin(main_regions)].copy()

    # Cost aggregation per region + scenario
    cost_agg = sr_main.groupby(["region", "scenario"]).agg(
        capex_annual_sum=("cost_component_capex_annual_usd", "sum"),
        total_opex_usd=("cost_component_opex_annual_usd", "sum"),
        new_energy_sum=("cost_component_new_energy_usd", "sum"),
        fuel_savings_sum=("cost_component_fuel_savings_usd", "sum"),
    )
    cost_agg["transition_cost_usd"] = (
        cost_agg["capex_annual_sum"]
        + cost_agg["total_opex_usd"]
        + cost_agg["new_energy_sum"]
        - cost_agg["fuel_savings_sum"]
    )

    df = cost_agg.reset_index()
    df["technology_path"] = df["scenario"].apply(lambda s: _parse_scenario(s)[0])
    df["price_variant"] = df["scenario"].apply(lambda s: _parse_scenario(s)[1])

    # Facility count and capacity from facility_database
    # Map complex to region
    complex_to_region = {
        "Daesan Complex": "Daesan",
        "Yeosu Complex": "Yeosu",
        "Ulsan Complex": "Ulsan",
    }
    fac = fac_db.copy()
    fac["region_mapped"] = fac["complex"].map(complex_to_region)
    # Handle Shaheen (has "Onsan Complex" in region column)
    fac.loc[fac["region_mapped"].isna() & fac["location"].isin(["Onsan", "Ulsan"]), "region_mapped"] = "Ulsan"
    fac_main = fac[fac["region_mapped"].isin(main_regions)]

    region_stats = (
        fac_main.groupby("region_mapped")
        .agg(num_facilities=("company", "count"), total_capacity_kt=("capacity_kt", "sum"))
        .reset_index()
        .rename(columns={"region_mapped": "region"})
    )

    df = df.merge(region_stats, on="region", how="left")

    # Convert
    df["transition_cost_billion_won"] = usd_to_billion_won(df["transition_cost_usd"])
    df["region"] = df["region"].map(REGION_MAP)

    cols = [
        "region",
        "scenario",
        "technology_path",
        "price_variant",
        "transition_cost_billion_won",
        "num_facilities",
        "total_capacity_kt",
    ]
    out = df[cols].copy()
    region_order = {"대산": 0, "여수": 1, "울산": 2}
    out["_sort_r"] = out["region"].map(region_order)
    out["_sort_s"] = out["scenario"].map(
        {s: i for i, s in enumerate(SCENARIO_ORDER)}
    )
    out = (
        out.sort_values(["_sort_r", "_sort_s"])
        .drop(columns=["_sort_r", "_sort_s"])
        .reset_index(drop=True)
    )
    out.to_csv(OUTPUT_DIR / "region_transition_cost.csv", index=False, encoding="utf-8-sig")
    print(f"FILE 3: {len(out)} rows -> region_transition_cost.csv")
    return out


# ---------------------------------------------------------------------------
# FILE 4: stranded_assets_overview.csv
# ---------------------------------------------------------------------------
def gen_file4(table1, table2_summary, **kw):
    """8 rows: stranded asset overview per scenario (1.5C only)."""
    df = table2_summary.copy()

    df["technology_path"] = df["scenario"].apply(lambda s: _parse_scenario(s)[0])
    df["price_variant"] = df["scenario"].apply(lambda s: _parse_scenario(s)[1])
    df["budget_scenario"] = "1.5C"
    df["stranding_year"] = df["stranding_year_15c"]

    # Stranded asset in billion won
    df["total_stranded_asset_billion_won"] = df["ncc_stranded_15c_billion_usd"] * KRW_PER_USD

    # NCC replacement cost = total CAPEX from table1 (this is the full replacement/transition CAPEX)
    capex_map = table1.set_index("scenario")["total_capex_billion_usd"].to_dict()
    df["total_ncc_replacement_cost_billion_won"] = (
        df["scenario"].map(capex_map) * KRW_PER_USD
    )

    # Stranded ratio
    df["stranded_ratio_pct"] = (
        df["ncc_stranded_15c_billion_usd"]
        / df["scenario"].map(capex_map)
        * 100
    )

    cols = [
        "scenario",
        "technology_path",
        "price_variant",
        "budget_scenario",
        "stranding_year",
        "total_stranded_asset_billion_won",
        "total_ncc_replacement_cost_billion_won",
        "stranded_ratio_pct",
    ]
    out = df[cols].copy()
    out["_sort"] = out["scenario"].map(
        {s: i for i, s in enumerate(SCENARIO_ORDER)}
    )
    out = out.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)
    out.to_csv(OUTPUT_DIR / "stranded_assets_overview.csv", index=False, encoding="utf-8-sig")
    print(f"FILE 4: {len(out)} rows -> stranded_assets_overview.csv")

    # Verification
    for _, row in out.iterrows():
        t2_row = table2_summary[table2_summary["scenario"] == row["scenario"]]
        if len(t2_row) == 0:
            continue
        expected_bw = t2_row["ncc_stranded_15c_trillion_krw"].values[0] * 1000  # trillion -> billion
        actual_bw = row["total_stranded_asset_billion_won"]
        diff = abs(expected_bw - actual_bw)
        if diff > 0.5:
            print(
                f"  WARNING: Stranded mismatch for {row['scenario']}: "
                f"table2={expected_bw:.2f}B KRW, computed={actual_bw:.2f}B KRW"
            )
    return out


# ---------------------------------------------------------------------------
# FILE 5: company_stranded_assets.csv
# ---------------------------------------------------------------------------
def gen_file5(table2_facility, **kw):
    """Facility-level stranded assets with age data, 1.5C only."""
    df = table2_facility.copy()

    # Keep facility-level rows (no groupby)
    df["technology_path"] = df["scenario"].apply(lambda s: _parse_scenario(s)[0])
    df["budget_scenario"] = "1.5C"
    df["age_2025"] = 2025 - df["year_built"]
    df["book_value_billion_won"] = usd_to_billion_won(df["stranded_value_usd"])
    df["stranded_asset_billion_won"] = usd_to_billion_won(df["stranded_value_usd"])
    df["company"] = df["company"].map(lambda c: COMPANY_NAME_MAP.get(c, c))

    cols = [
        "company", "location", "product", "capacity_kt",
        "year_built", "age_2025",
        "scenario", "technology_path", "budget_scenario",
        "book_value_billion_won", "stranded_asset_billion_won",
    ]
    out = df[cols].copy()
    out["_sort"] = out["scenario"].map(
        {s: i for i, s in enumerate(SCENARIO_ORDER)}
    )
    out = out.sort_values(["company", "_sort"]).drop(columns="_sort").reset_index(drop=True)
    out.to_csv(OUTPUT_DIR / "company_stranded_assets.csv", index=False, encoding="utf-8-sig")
    print(f"FILE 5: {len(out)} rows -> company_stranded_assets.csv")
    return out


# ---------------------------------------------------------------------------
# FILE 6: energy_price_assumptions.csv
# ---------------------------------------------------------------------------
def gen_file6(h2_prices, grid_price, flat_elec, h2_traj, **kw):
    """24 rows: 4 price variants × 6 years."""
    target_years = [2025, 2030, 2035, 2040, 2045, 2050]

    # Build lookup tables
    grid_lookup = grid_price.set_index("year")["grid_price_usd_per_mwh"].to_dict()
    flat_elec_lookup = flat_elec.set_index("year")["elec_price_usd_per_mwh"].to_dict()
    h2_lcoh_flat = h2_prices.set_index("year")["lcoh_flat_usd_per_kg"].to_dict()
    h2_lcoh_rising = h2_prices.set_index("year")["lcoh_rising_usd_per_kg"].to_dict()
    h2_traj_lookup = h2_traj.set_index("year")["h2_price_usd_per_kg"].to_dict()

    # Variant definitions:
    # rising_coupled:    elec=grid_trajectory, h2=lcoh_rising (coupled = H2 from grid elec, rising price)
    # rising_decoupled:  elec=grid_trajectory, h2=h2_price_trajectory (decoupled = independent H2 market)
    # flat_coupled:      elec=flat ($77/MWh),  h2=lcoh_flat (coupled = H2 from flat elec)
    # flat_decoupled:    elec=flat ($77/MWh),  h2=h2_price_trajectory (decoupled)
    variants = {
        "rising_coupled": {
            "scenario": "shaheen_ncc_h2_rising_coupled",
            "elec_fn": lambda y: grid_lookup.get(y, np.nan),
            "h2_fn": lambda y: h2_lcoh_rising.get(y, np.nan),
        },
        "rising_decoupled": {
            "scenario": "shaheen_ncc_h2_rising_decoupled",
            "elec_fn": lambda y: grid_lookup.get(y, np.nan),
            "h2_fn": lambda y: h2_traj_lookup.get(y, np.nan),
        },
        "flat_coupled": {
            "scenario": "shaheen_ncc_h2_flat_coupled",
            "elec_fn": lambda y: flat_elec_lookup.get(y, np.nan),
            "h2_fn": lambda y: h2_lcoh_flat.get(y, np.nan),
        },
        "flat_decoupled": {
            "scenario": "shaheen_ncc_h2_flat_decoupled",
            "elec_fn": lambda y: flat_elec_lookup.get(y, np.nan),
            "h2_fn": lambda y: h2_traj_lookup.get(y, np.nan),
        },
    }

    rows = []
    for pv, cfg in variants.items():
        for y in target_years:
            elec_usd_mwh = cfg["elec_fn"](y)
            h2_usd_kg = cfg["h2_fn"](y)
            # Convert: USD/MWh -> KRW/kWh (×1300/1000 = ×1.3)
            elec_won_kwh = elec_usd_mwh * KRW_PER_USD / 1000
            # Convert: USD/kg -> KRW/kg
            h2_won_kg = h2_usd_kg * KRW_PER_USD
            rows.append(
                {
                    "scenario": cfg["scenario"],
                    "price_variant": pv,
                    "year": y,
                    "electricity_price_won_kwh": round(elec_won_kwh, 2),
                    "hydrogen_price_won_kg": round(h2_won_kg, 2),
                }
            )

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_DIR / "energy_price_assumptions.csv", index=False, encoding="utf-8-sig")
    print(f"FILE 6: {len(out)} rows -> energy_price_assumptions.csv")
    return out


# ---------------------------------------------------------------------------
# FILE 7: facility_technology_transitions.csv
# ---------------------------------------------------------------------------
def gen_file7(sr, fac_db, **kw):
    """~Row per NCC facility x scenario. Tracks technology transition."""
    # Filter for Naphtha Crackers only
    df = sr[sr["process"] == "Naphtha Cracker"].copy()
    
    # 1. Get list of all NCC facilities and scenarios
    base_cols = ["scenario", "facility_id", "company", "region", "product", "capacity_tpy"]
    # Get unique facilities from year 2025 (start of simulation) to ensure we have all of them
    all_facilities = df.drop_duplicates(subset=["scenario", "facility_id"])[base_cols].copy()
    
    # 2. Find transitions
    # Subset rows with technology != Baseline.
    # drop duplicates on scenario+facility.
    transition_rows = df[df["technology"] != "Baseline"].sort_values("year").drop_duplicates(subset=["scenario", "facility_id"])
    transition_lookup = transition_rows.set_index(["scenario", "facility_id"])[["technology", "install_year"]]
    
    # Merge
    out = all_facilities.merge(transition_lookup, on=["scenario", "facility_id"], how="left")
    
    # Fill NA
    # If technology is NaN, it means it never transitioned -> Baseline
    out["final_technology"] = out["technology"].fillna("Baseline")
    
    # Formatting
    out["technology_path"] = out["scenario"].apply(lambda s: _parse_scenario(s)[0])
    out["price_variant"] = out["scenario"].apply(lambda s: _parse_scenario(s)[1])
    
    out["capacity_kt"] = out["capacity_tpy"] / 1000.0
    
    out["company"] = out["company"].map(lambda c: COMPANY_NAME_MAP.get(c, c))
    out["region"] = out["region"].map(REGION_MAP)
    
    # Clean up columns
    cols = [
        "scenario",
        "technology_path",
        "price_variant",
        "company",
        "facility_id",
        "region",
        "product",
        "capacity_kt",
        "final_technology",
        "install_year"
    ]
    
    out = out[cols].rename(columns={"install_year": "transition_year"})
    
    # Sort
    out["_sort"] = out["scenario"].map({s: i for i, s in enumerate(SCENARIO_ORDER)})
    out = out.sort_values(["_sort", "company", "facility_id"]).drop(columns="_sort").reset_index(drop=True)
    
    # Handle the transition_year display
    out["transition_year"] = out["transition_year"].apply(lambda x: str(int(x)) if pd.notna(x) else "No Transition")
    
    out.to_csv(OUTPUT_DIR / "facility_technology_transitions.csv", index=False, encoding="utf-8-sig")
    print(f"FILE 7: {len(out)} rows -> facility_technology_transitions.csv")
    return out


# ---------------------------------------------------------------------------
# FILE 8: scenario_transition_cost_summary.csv
# ---------------------------------------------------------------------------
def gen_file8(sr, **kw):
    """8 rows: simple scenario-level total transition cost."""
    # Deduplicated CAPEX
    install_rows = sr.dropna(subset=["install_year"]).copy()
    install_rows = install_rows[install_rows["year"] == install_rows["install_year"]]
    capex_dedup = (
        install_rows.drop_duplicates(subset=["scenario", "facility_id"])
        .groupby("scenario")["capex_usd"]
        .sum()
        .rename("total_capex_usd")
    )

    cost_agg = sr.groupby("scenario").agg(
        total_opex_usd=("cost_component_opex_annual_usd", "sum"),
        capex_annual_sum=("cost_component_capex_annual_usd", "sum"),
        new_energy_sum=("cost_component_new_energy_usd", "sum"),
        fuel_savings_sum=("cost_component_fuel_savings_usd", "sum"),
    )
    cost_agg["total_cost_usd"] = (
        cost_agg["capex_annual_sum"]
        + cost_agg["total_opex_usd"]
        + cost_agg["new_energy_sum"]
        - cost_agg["fuel_savings_sum"]
    )

    df = cost_agg.join(capex_dedup).reset_index()
    df["total_capex_usd"] = df["total_capex_usd"].fillna(0)

    df["technology_path"] = df["scenario"].apply(lambda s: _parse_scenario(s)[0])
    df["price_variant"] = df["scenario"].apply(lambda s: _parse_scenario(s)[1])

    df["total_transition_cost_billion_won"] = usd_to_billion_won(df["total_cost_usd"])
    df["capex_billion_won"] = usd_to_billion_won(df["total_capex_usd"])
    df["opex_billion_won"] = usd_to_billion_won(df["total_opex_usd"])

    cols = [
        "scenario",
        "technology_path",
        "price_variant",
        "total_transition_cost_billion_won",
        "capex_billion_won",
        "opex_billion_won",
    ]
    out = df[cols].copy()
    out["_sort"] = out["scenario"].map(
        {s: i for i, s in enumerate(SCENARIO_ORDER)}
    )
    out = out.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)
    out.to_csv(OUTPUT_DIR / "scenario_transition_cost_summary.csv", index=False, encoding="utf-8-sig")
    print(f"FILE 8: {len(out)} rows -> scenario_transition_cost_summary.csv")
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Loading data...")
    data = load_data()
    print()

    gen_file1(**data)
    gen_file2(**data)
    gen_file3(**data)
    gen_file4(**data)
    gen_file5(**data)
    gen_file6(**data)
    gen_file7(**data)
    gen_file8(**data)

    print(f"\nAll files written to {OUTPUT_DIR}")

    # Final verification: check all 8 scenarios appear in each file
    for fname in [
        "scenario_total_cost.csv",
        "company_transition_cost.csv",
        "region_transition_cost.csv",
        "stranded_assets_overview.csv",
        "company_stranded_assets.csv",
        "facility_technology_transitions.csv",
        "scenario_transition_cost_summary.csv",
    ]:
        df = pd.read_csv(OUTPUT_DIR / fname, encoding="utf-8-sig")
        scenarios = df["scenario"].nunique()
        if scenarios != 8:
            print(f"  WARNING: {fname} has {scenarios} scenarios (expected 8)")
        else:
            print(f"  OK: {fname} has 8 scenarios")

    # FILE 6 check
    df6 = pd.read_csv(OUTPUT_DIR / "energy_price_assumptions.csv", encoding="utf-8-sig")
    pvs = df6["price_variant"].nunique()
    if pvs != 4:
        print(f"  WARNING: energy_price_assumptions.csv has {pvs} variants (expected 4)")
    else:
        print(f"  OK: energy_price_assumptions.csv has 4 price variants")


if __name__ == "__main__":
    main()
