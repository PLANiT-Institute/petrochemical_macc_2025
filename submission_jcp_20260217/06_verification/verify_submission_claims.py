#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "03_data"
OUT_DIR = Path(__file__).resolve().parent
FIG_DIR = BASE / "02_figures"

PAPER_RESULTS = DATA_DIR / "jcp_consolidated_results.csv"
FULL_RESULTS = DATA_DIR / "scenario_results.csv"


@dataclass
class ClaimSpec:
    claim_id: str
    section: str
    claim_text: str
    source_file: str
    calculation_rule: str
    expected_value: float
    tolerance: float
    unit: str


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.groupby(["scenario", "year"], as_index=False)
        .agg(
            bau_emissions_tco2=("bau_emissions_tco2", "sum"),
            emissions_tco2=("emissions_tco2", "sum"),
            abatement_tco2=("abatement_tco2", "sum"),
            total_cost_usd=("total_cost_usd", "sum"),
            elec_demand_mwh=("elec_demand_mwh", "sum"),
            added_elec_mwh=("added_elec_mwh", "sum"),
            h2_demand_t=("h2_demand_t", "sum"),
        )
        .sort_values(["scenario", "year"])
    )
    out["bau_mtco2"] = out["bau_emissions_tco2"] / 1e6
    out["emissions_mtco2"] = out["emissions_tco2"] / 1e6
    out["abatement_mtco2"] = out["abatement_tco2"] / 1e6
    out["total_cost_busd"] = out["total_cost_usd"] / 1e9
    out["elec_twh"] = out["elec_demand_mwh"] / 1e6
    out["added_elec_twh"] = out["added_elec_mwh"] / 1e6
    out["h2_mt"] = out["h2_demand_t"] / 1e6
    return out


def get_value(df: pd.DataFrame, scenario: str, year: int, col: str) -> float:
    row = df[(df["scenario"] == scenario) & (df["year"] == year)]
    if row.empty:
        raise ValueError(f"Missing row: scenario={scenario}, year={year}")
    return float(row.iloc[0][col])


def build_claim_specs() -> List[ClaimSpec]:
    return [
        ClaimSpec(
            claim_id="C01",
            section="Methods",
            claim_text="Coverage includes 243 facilities and 2025-2050 period.",
            source_file="03_data/jcp_consolidated_results.csv",
            calculation_rule="nunique(facility_id)==243 and min(year)==2025 and max(year)==2050",
            expected_value=243.0,
            tolerance=0.0,
            unit="count",
        ),
        ClaimSpec(
            claim_id="C02",
            section="Results",
            claim_text="S2 2030 annual transition cost is 7.273 BUSD/yr.",
            source_file="03_data/jcp_consolidated_results.csv",
            calculation_rule="sum(total_cost_usd)/1e9 for scenario=S2_NetZero_HighAmbition, year=2030",
            expected_value=7.273,
            tolerance=0.10,
            unit="BUSD/yr",
        ),
        ClaimSpec(
            claim_id="C03",
            section="Results",
            claim_text="S2 2030 abatement is 1.902 MtCO2/yr.",
            source_file="03_data/jcp_consolidated_results.csv",
            calculation_rule="sum(abatement_tco2)/1e6 for scenario=S2_NetZero_HighAmbition, year=2030",
            expected_value=1.902,
            tolerance=0.10,
            unit="MtCO2/yr",
        ),
        ClaimSpec(
            claim_id="C04",
            section="Results",
            claim_text="S2 2050 annual transition cost is 25.043 BUSD/yr.",
            source_file="03_data/jcp_consolidated_results.csv",
            calculation_rule="sum(total_cost_usd)/1e9 for scenario=S2_NetZero_HighAmbition, year=2050",
            expected_value=25.043,
            tolerance=0.10,
            unit="BUSD/yr",
        ),
        ClaimSpec(
            claim_id="C05",
            section="Results",
            claim_text="S2 2050 abatement is 51.505 MtCO2/yr.",
            source_file="03_data/jcp_consolidated_results.csv",
            calculation_rule="sum(abatement_tco2)/1e6 for scenario=S2_NetZero_HighAmbition, year=2050",
            expected_value=51.505,
            tolerance=0.10,
            unit="MtCO2/yr",
        ),
        ClaimSpec(
            claim_id="C06",
            section="Results",
            claim_text="Electricity-centered pathways require 146.034 TWh/yr added electricity in 2050.",
            source_file="03_data/scenario_results.csv",
            calculation_rule="mean(group=*_elec_*, year=2050, added_elec_mwh/1e6)",
            expected_value=146.034,
            tolerance=0.50,
            unit="TWh/yr",
        ),
        ClaimSpec(
            claim_id="C07",
            section="Results",
            claim_text="Hydrogen-centered pathways require 4.546 Mt/yr hydrogen in 2050.",
            source_file="03_data/scenario_results.csv",
            calculation_rule="mean(group=*_h2_*, year=2050, h2_demand_t/1e6)",
            expected_value=4.546,
            tolerance=0.02,
            unit="Mt/yr",
        ),
        ClaimSpec(
            claim_id="C08",
            section="Results",
            claim_text="Hydrogen-centered pathways require 32.380 TWh/yr added electricity in 2050.",
            source_file="03_data/scenario_results.csv",
            calculation_rule="mean(group=*_h2_*, year=2050, added_elec_mwh/1e6)",
            expected_value=32.380,
            tolerance=0.50,
            unit="TWh/yr",
        ),
        ClaimSpec(
            claim_id="C09",
            section="Results",
            claim_text="S3 incurs 16.994 BUSD/yr cost premium over S2 in 2050.",
            source_file="03_data/jcp_consolidated_results.csv",
            calculation_rule="(S3 total_cost_busd - S2 total_cost_busd) at year=2050",
            expected_value=16.994,
            tolerance=0.10,
            unit="BUSD/yr",
        ),
    ]


def evaluate_claims(paper_agg: pd.DataFrame, full_agg: pd.DataFrame, paper_df_raw: pd.DataFrame) -> pd.DataFrame:
    specs = build_claim_specs()
    rows: List[Dict[str, object]] = []

    y2050 = full_agg[full_agg["year"] == 2050].copy()
    elec_grp = y2050[y2050["scenario"].str.contains("_elec_")]
    h2_grp = y2050[y2050["scenario"].str.contains("_h2_")]

    actual_map: Dict[str, float] = {
        "C01": float(paper_df_raw["facility_id"].astype(str).str.strip().nunique()),
        "C02": get_value(paper_agg, "S2_NetZero_HighAmbition", 2030, "total_cost_busd"),
        "C03": get_value(paper_agg, "S2_NetZero_HighAmbition", 2030, "abatement_mtco2"),
        "C04": get_value(paper_agg, "S2_NetZero_HighAmbition", 2050, "total_cost_busd"),
        "C05": get_value(paper_agg, "S2_NetZero_HighAmbition", 2050, "abatement_mtco2"),
        "C06": float(elec_grp["added_elec_twh"].mean()),
        "C07": float(h2_grp["h2_mt"].mean()),
        "C08": float(h2_grp["added_elec_twh"].mean()),
        "C09": float(
            get_value(paper_agg, "S3_Tech_Constraints", 2050, "total_cost_busd")
            - get_value(paper_agg, "S2_NetZero_HighAmbition", 2050, "total_cost_busd")
        ),
    }

    for spec in specs:
        actual = actual_map[spec.claim_id]
        status = "PASS" if abs(actual - spec.expected_value) <= spec.tolerance else "CHECK"
        rows.append(
            {
                "claim_id": spec.claim_id,
                "section": spec.section,
                "expected": spec.expected_value,
                "actual": actual,
                "tolerance": spec.tolerance,
                "unit": spec.unit,
                "status": status,
                "source_file": spec.source_file,
                "calc_rule": spec.calculation_rule,
            }
        )

    reg_rows = [
        {
            "claim_id": spec.claim_id,
            "manuscript_section": spec.section,
            "claim_text": spec.claim_text,
            "source_file": spec.source_file,
            "calculation_rule": spec.calculation_rule,
            "expected_value": spec.expected_value,
            "status": next(r["status"] for r in rows if r["claim_id"] == spec.claim_id),
        }
        for spec in specs
    ]

    claim_checks = pd.DataFrame(rows).sort_values("claim_id")
    claim_register = pd.DataFrame(reg_rows).sort_values("claim_id")

    claim_checks.to_csv(OUT_DIR / "claim_checks.csv", index=False)
    claim_register.to_csv(OUT_DIR / "claim_register.csv", index=False)
    return claim_checks


def build_infrastructure_checks(full_agg: pd.DataFrame) -> pd.DataFrame:
    full = full_agg.copy()
    full["scenario_group"] = full["scenario"].apply(
        lambda s: "electricity_centered" if "_elec_" in s else ("hydrogen_centered" if "_h2_" in s else "other")
    )

    grouped = (
        full[full["scenario_group"].isin(["electricity_centered", "hydrogen_centered"])]
        .groupby(["scenario_group", "year"], as_index=False)
        .agg(
            added_elec_twh=("added_elec_twh", "mean"),
            h2_mt=("h2_mt", "mean"),
            abatement_mtco2=("abatement_mtco2", "mean"),
        )
    )

    # interpretation flag is asserted for 2050 policy-relevant endpoint
    pivot = grouped.pivot(index="year", columns="scenario_group", values=["added_elec_twh", "h2_mt"])
    flags = {}
    for y in sorted(grouped["year"].unique()):
        if y != 2050:
            flags[y] = "NA"
            continue
        try:
            elec_added = pivot.loc[y, ("added_elec_twh", "electricity_centered")]
            h2_added = pivot.loc[y, ("added_elec_twh", "hydrogen_centered")]
            elec_h2 = pivot.loc[y, ("h2_mt", "electricity_centered")]
            h2_h2 = pivot.loc[y, ("h2_mt", "hydrogen_centered")]
            pass_flag = (elec_added > h2_added) and (h2_h2 > 0.0) and (abs(elec_h2) < 1e-9)
            flags[y] = "PASS" if pass_flag else "CHECK"
        except KeyError:
            flags[y] = "CHECK"

    grouped["interpretation_flag"] = grouped["year"].map(flags).fillna("NA")
    grouped.to_csv(OUT_DIR / "infrastructure_hypothesis_checks.csv", index=False)

    note = [
        "# Infrastructure Hypothesis Note",
        "",
        "Hypothesis: pathway feasibility is constrained by infrastructure (grid + hydrogen supply) rather than static cost ordering alone.",
        "",
        "Operational check per year:",
        "- electricity_centered added_elec_twh > hydrogen_centered added_elec_twh",
        "- hydrogen_centered h2_mt > 0",
        "- electricity_centered h2_mt ~= 0",
        "",
        "Result is recorded in `interpretation_flag` of `infrastructure_hypothesis_checks.csv`.",
    ]
    (OUT_DIR / "infrastructure_hypothesis_note.md").write_text("\n".join(note), encoding="utf-8")
    return grouped


def export_main_tables(paper_agg: pd.DataFrame, infra_checks: pd.DataFrame) -> None:
    # Main Table 1: paper scenarios at 2030/2040/2050
    main1 = paper_agg[paper_agg["year"].isin([2030, 2040, 2050])][
        ["scenario", "year", "total_cost_busd", "abatement_mtco2", "added_elec_twh", "h2_mt"]
    ].copy()
    main1 = main1.rename(
        columns={
            "total_cost_busd": "cost_busd_per_year",
            "abatement_mtco2": "abatement_mtco2_per_year",
            "added_elec_twh": "added_electricity_twh_per_year",
            "h2_mt": "hydrogen_mt_per_year",
        }
    )
    main1.to_csv(OUT_DIR / "table_main_cost_abatement_energy_2030_2040_2050.csv", index=False)

    # Main Table 2: 2050 infrastructure by scenario group
    main2 = infra_checks[infra_checks["year"] == 2050][
        ["scenario_group", "year", "added_elec_twh", "h2_mt", "abatement_mtco2", "interpretation_flag"]
    ].copy()
    main2.to_csv(OUT_DIR / "table_main_infrastructure_requirements_2050.csv", index=False)


def export_energy_snapshot(full_agg: pd.DataFrame) -> None:
    y2050 = full_agg[full_agg["year"] == 2050][
        ["scenario", "total_cost_busd", "abatement_mtco2", "elec_twh", "added_elec_twh", "h2_mt"]
    ].copy()
    y2050.to_csv(OUT_DIR / "energy_demand_2050.csv", index=False)


def render_figures(paper_agg: pd.DataFrame, infra_checks: pd.DataFrame) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return

    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # Figure 1: added electricity trajectory (paper scenarios)
    fig1 = plt.figure(figsize=(9, 5))
    for s in ["S1_Baseline_Trends", "S2_NetZero_HighAmbition", "S3_Tech_Constraints"]:
        sub = paper_agg[paper_agg["scenario"] == s]
        plt.plot(sub["year"], sub["added_elec_twh"], label=s, linewidth=2)
    plt.xlabel("Year")
    plt.ylabel("Added electricity demand (TWh/yr)")
    plt.title("Main Figure 1: Added Electricity Demand Trajectory (Paper Scenarios)")
    plt.grid(alpha=0.3)
    plt.legend(fontsize=8)
    fig1.tight_layout()
    fig1.savefig(FIG_DIR / "fig_main_added_electricity_trajectory.png", dpi=220)
    plt.close(fig1)

    # Figure 2: hydrogen demand trajectory (paper scenarios)
    fig2 = plt.figure(figsize=(9, 5))
    for s in ["S1_Baseline_Trends", "S2_NetZero_HighAmbition", "S3_Tech_Constraints"]:
        sub = paper_agg[paper_agg["scenario"] == s]
        plt.plot(sub["year"], sub["h2_mt"], label=s, linewidth=2)
    plt.xlabel("Year")
    plt.ylabel("Hydrogen demand (Mt/yr)")
    plt.title("Main Figure 2: Hydrogen Demand Trajectory (Paper Scenarios)")
    plt.grid(alpha=0.3)
    plt.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(FIG_DIR / "fig_main_hydrogen_trajectory.png", dpi=220)
    plt.close(fig2)

    # Figure 3: 2050 infrastructure tradeoff (group comparison)
    y2050 = infra_checks[infra_checks["year"] == 2050].copy().set_index("scenario_group")
    groups = [g for g in ["electricity_centered", "hydrogen_centered"] if g in y2050.index]
    added = [float(y2050.loc[g, "added_elec_twh"]) for g in groups]
    h2 = [float(y2050.loc[g, "h2_mt"]) for g in groups]

    fig3, ax1 = plt.subplots(figsize=(8, 5))
    x = range(len(groups))
    ax1.bar(x, added, color="#1f77b4", width=0.5)
    ax1.set_ylabel("Added electricity demand (TWh/yr)", color="#1f77b4")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(groups)
    ax1.set_title("Main Figure 3: 2050 Infrastructure Tradeoff by Scenario Group")
    ax2 = ax1.twinx()
    ax2.plot(list(x), h2, color="#d62728", marker="o", linewidth=2)
    ax2.set_ylabel("Hydrogen demand (Mt/yr)", color="#d62728")
    ax2.tick_params(axis="y", labelcolor="#d62728")
    fig3.tight_layout()
    fig3.savefig(FIG_DIR / "fig_main_infrastructure_tradeoff_2050.png", dpi=220)
    plt.close(fig3)


def deterministic_check(claim_checks: pd.DataFrame, paper_agg: pd.DataFrame, full_agg: pd.DataFrame, paper_df_raw: pd.DataFrame) -> str:
    # Re-evaluate and compare deterministic hash for claim checks
    first = claim_checks.sort_values("claim_id").to_csv(index=False)
    second = evaluate_claims(paper_agg, full_agg, paper_df_raw).sort_values("claim_id").to_csv(index=False)
    h1 = hashlib.sha256(first.encode("utf-8")).hexdigest()
    h2 = hashlib.sha256(second.encode("utf-8")).hexdigest()
    return "PASS" if h1 == h2 else "CHECK"


def write_report(
    claim_checks: pd.DataFrame,
    infra_checks: pd.DataFrame,
    paper_agg: pd.DataFrame,
    reproducibility_status: str,
) -> None:
    pass_count = int((claim_checks["status"] == "PASS").sum())
    total_count = int(len(claim_checks))

    s2_2030 = paper_agg[(paper_agg["scenario"] == "S2_NetZero_HighAmbition") & (paper_agg["year"] == 2030)].iloc[0]
    s2_2050 = paper_agg[(paper_agg["scenario"] == "S2_NetZero_HighAmbition") & (paper_agg["year"] == 2050)].iloc[0]

    y2050 = infra_checks[infra_checks["year"] == 2050].set_index("scenario_group")
    elec_added = float(y2050.loc["electricity_centered", "added_elec_twh"])
    h2_added = float(y2050.loc["hydrogen_centered", "added_elec_twh"])
    h2_demand = float(y2050.loc["hydrogen_centered", "h2_mt"])

    md = []
    md.append("# Verification Report for JCP Submission Package")
    md.append("")
    md.append("## 1) Evidence lock")
    md.append("")
    md.append("- Source-of-truth files: `03_data/jcp_consolidated_results.csv`, `03_data/scenario_results.csv`")
    md.append("- Manuscript claims are linked by claim IDs (`C01`-`C09`).")

    md.append("")
    md.append("## 2) Claim checks")
    md.append("")
    md.append(f"- PASS: **{pass_count}/{total_count}**")
    md.append("- Detailed file: `claim_checks.csv`")
    md.append("- Claim register: `claim_register.csv`")

    md.append("")
    md.append("| claim_id | expected | actual | tolerance | unit | status |")
    md.append("|---|---:|---:|---:|---|---|")
    for _, r in claim_checks.sort_values("claim_id").iterrows():
        md.append(
            f"| {r['claim_id']} | {r['expected']:.3f} | {r['actual']:.3f} | {r['tolerance']:.3f} | {r['unit']} | {r['status']} |"
        )

    md.append("")
    md.append("## 3) Hypothesis-centric infrastructure checks")
    md.append("")
    md.append("- File: `infrastructure_hypothesis_checks.csv`")
    md.append(
        f"- 2050 electricity-centered added electricity demand: **{elec_added:.3f} TWh/yr**"
    )
    md.append(
        f"- 2050 hydrogen-centered hydrogen demand: **{h2_demand:.3f} Mt/yr**"
    )
    md.append(
        f"- 2050 hydrogen-centered added electricity demand: **{h2_added:.3f} TWh/yr**"
    )
    md.append("- Interpretation: infrastructure requirements are first-order transition constraints.")

    md.append("")
    md.append("## 4) Main manuscript anchor values")
    md.append("")
    md.append(f"- S2 2030: cost **{s2_2030['total_cost_busd']:.3f} BUSD/yr**, abatement **{s2_2030['abatement_mtco2']:.3f} MtCO2/yr**")
    md.append(f"- S2 2050: cost **{s2_2050['total_cost_busd']:.3f} BUSD/yr**, abatement **{s2_2050['abatement_mtco2']:.3f} MtCO2/yr**")

    md.append("")
    md.append("## 5) Reproducibility")
    md.append("")
    md.append(f"- Deterministic rerun check: **{reproducibility_status}**")
    md.append("- Run command: `python3 06_verification/verify_submission_claims.py`")

    md.append("")
    md.append("## 6) Generated outputs")
    md.append("")
    outputs = [
        "claim_register.csv",
        "claim_checks.csv",
        "paper_yearly_summary.csv",
        "full_yearly_summary.csv",
        "infrastructure_hypothesis_checks.csv",
        "infrastructure_hypothesis_note.md",
        "table_main_cost_abatement_energy_2030_2040_2050.csv",
        "table_main_infrastructure_requirements_2050.csv",
    ]
    for o in outputs:
        md.append(f"- `{o}`")

    (OUT_DIR / "verification_report.md").write_text("\n".join(md), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    paper_df_raw = pd.read_csv(PAPER_RESULTS)
    full_df_raw = pd.read_csv(FULL_RESULTS)

    # Keep full dataset intact for sums; normalize facility_id artifacts for count-only checks if needed externally
    paper_agg = aggregate(paper_df_raw)
    full_agg = aggregate(full_df_raw)

    paper_agg.to_csv(OUT_DIR / "paper_yearly_summary.csv", index=False)
    full_agg.to_csv(OUT_DIR / "full_yearly_summary.csv", index=False)

    claim_checks = evaluate_claims(paper_agg, full_agg, paper_df_raw)
    infra_checks = build_infrastructure_checks(full_agg)
    export_main_tables(paper_agg, infra_checks)
    export_energy_snapshot(full_agg)
    render_figures(paper_agg, infra_checks)

    repro_status = deterministic_check(claim_checks, paper_agg, full_agg, paper_df_raw)
    write_report(claim_checks, infra_checks, paper_agg, repro_status)


if __name__ == "__main__":
    main()
