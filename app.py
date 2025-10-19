"""
KOREAN PETROCHEMICAL MACC MODEL - STREAMLIT DASHBOARD (ENERGY-BASED)
Facilitates exploration of model outputs across baseline, MACC, and scenario modules.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modules.utils import is_ncc_facility


# -----------------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Korea Petrochemical MACC Model (Energy-Based)",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data() -> dict:
    """Load all model output artifacts into a dictionary."""
    data: dict[str, pd.DataFrame | dict] = {}

    # Module 1 – Baseline
    try:
        data["baseline"] = pd.read_csv("outputs/module_01/baseline_2025_detailed.csv")
        data["bau"] = pd.read_csv("outputs/module_01/bau_trajectory_2025_2050.csv")
        data["emissions_by_product"] = pd.read_csv("outputs/module_01/emissions_by_product.csv")
        data["emissions_by_location"] = pd.read_csv("outputs/module_01/emissions_by_location.csv")
    except FileNotFoundError:
        st.warning("Module 1 outputs not found. Run the baseline pipeline.")

    # Module 2 – MACC
    try:
        data["macc"] = pd.read_csv("outputs/module_02/macc_annual_2025_2050.csv")
    except FileNotFoundError:
        st.warning("Module 2 outputs not found. Run the MACC pipeline.")

    # Module 3 – Scenario optimisation
    try:
        data["scenario_comparison"] = pd.read_csv("outputs/module_03/scenario_comparison.csv")

        # deployment trajectories
        deployment_files = sorted(Path("outputs/module_03").glob("*_deployment.csv"))
        if deployment_files:
            data["scenario_deployments"] = {
                f.stem.replace("_deployment", ""): pd.read_csv(f)
                for f in deployment_files
            }

        # facility allocation snapshots
        allocation_files = sorted(Path("outputs/module_03").glob("*_facility_allocation_2050.csv"))
        if allocation_files:
            data["facility_allocations"] = {
                f.stem.replace("_facility_allocation_2050", ""): pd.read_csv(f)
                for f in allocation_files
            }
    except FileNotFoundError:
        pass

    # Pre-computed LaTeX summaries (auto-generated in the modelling workflow)
    for csv_path in [
        "outputs/module_01/product_group_energy_mix.csv",
        "outputs/module_02/macc_cost_snapshot.csv",
        "outputs/module_03/scenario_summary_for_latex.csv",
    ]:
        try:
            key = Path(csv_path).stem
            data[key] = pd.read_csv(csv_path)
        except FileNotFoundError:
            pass

    try:
        data["grid_emissions"] = pd.read_csv("data/grid_emission_trajectory.csv")
    except FileNotFoundError:
        pass

    return data


@st.cache_data(show_spinner=False)
def compute_overview_metrics(baseline: pd.DataFrame, bau: pd.DataFrame) -> dict:
    """Pre-compute frequently used overview metrics."""
    metrics: dict[str, float | int] = {}
    metrics["n_facilities"] = len(baseline)
    metrics["baseline_mt"] = baseline["total_emissions_kt"].sum() / 1000

    if "year" in bau and "total_emissions_mt" in bau:
        metrics["bau_2050"] = bau.loc[bau["year"] == 2050, "total_emissions_mt"].squeeze()
        metrics["bau_2030"] = bau.loc[bau["year"] == 2030, "total_emissions_mt"].squeeze()
    return metrics


# -----------------------------------------------------------------------------
# UI helpers
# -----------------------------------------------------------------------------
def metric_card(label: str, value: str) -> None:
    st.metric(label, value)


def format_mt(value: float) -> str:
    return f"{value:,.1f} MtCO₂"


# -----------------------------------------------------------------------------
# Derived data helpers
# -----------------------------------------------------------------------------
def _normalize_series(series: pd.Series, fallback_index=None) -> pd.Series:
    series = series.copy().fillna(0.0)
    total = float(series.sum())
    if total <= 0:
        if fallback_index is None:
            fallback_index = series.index
        fallback_list = list(fallback_index)
        if not fallback_list:
            return pd.Series(dtype=float)
        uniform = np.full(len(fallback_list), 1.0 / len(fallback_list))
        return pd.Series(uniform, index=fallback_list)
    return series / total


def _existing_sum(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    existing = [col for col in columns if col in df.columns]
    if not existing:
        return pd.Series(np.zeros(len(df)), index=df.index)
    return df[existing].fillna(0.0).sum(axis=1)


def _get_column(df: pd.DataFrame, column: str) -> pd.Series:
    if column in df.columns:
        return df[column].fillna(0.0)
    return pd.Series(np.zeros(len(df)), index=df.index)


def compute_baseline_shares(baseline: pd.DataFrame) -> tuple[dict[str, pd.Series], dict[str, pd.Series]]:
    df = baseline.copy()
    if "location" not in df.columns:
        df["location"] = "Unknown"
    if "company" not in df.columns:
        df["company"] = "Unknown"

    df["location"] = df["location"].fillna("Unknown")
    df["company"] = df["company"].fillna("Unknown")
    df["is_ncc"] = df["product"].apply(is_ncc_facility)

    df["ncc_naphtha_mt"] = np.where(
        df["is_ncc"],
        _get_column(df, "emissions_naphtha_kt") / 1000,
        0.0,
    )
    df["electricity_mt"] = _get_column(df, "emissions_electricity_kt") / 1000
    df["thermal_mt"] = _existing_sum(
        df,
        [
            "emissions_lng_kt",
            "emissions_fuel_gas_kt",
            "emissions_byproduct_gas_kt",
            "emissions_lpg_kt",
            "emissions_fuel_oil_kt",
            "emissions_diesel_kt",
        ],
    ) / 1000

    locations = df["location"].unique().tolist()
    companies = df["company"].unique().tolist()

    region_shares = {
        "Heat_Pump": _normalize_series(df.groupby("location")["thermal_mt"].sum(), locations),
        "NCC-H2": _normalize_series(
            df[df["is_ncc"]].groupby("location")["ncc_naphtha_mt"].sum(), locations
        ),
        "NCC-Electricity": _normalize_series(
            df[df["is_ncc"]].groupby("location")["ncc_naphtha_mt"].sum(), locations
        ),
        "RE_PPA": _normalize_series(df.groupby("location")["electricity_mt"].sum(), locations),
    }

    company_shares = {
        "Heat_Pump": _normalize_series(df.groupby("company")["thermal_mt"].sum(), companies),
        "NCC-H2": _normalize_series(
            df[df["is_ncc"]].groupby("company")["ncc_naphtha_mt"].sum(), companies
        ),
        "NCC-Electricity": _normalize_series(
            df[df["is_ncc"]].groupby("company")["ncc_naphtha_mt"].sum(), companies
        ),
        "RE_PPA": _normalize_series(df.groupby("company")["electricity_mt"].sum(), companies),
    }

    return region_shares, company_shares


def _resolve_capex_ann(macc: pd.DataFrame, technology: str, year: int) -> float:
    tech_df = macc[macc["technology"] == technology].sort_values("year")
    if tech_df.empty:
        return 0.0

    exact = tech_df[tech_df["year"] == year]
    if not exact.empty:
        value = float(exact.iloc[0]["capex_ann_usd_per_tco2"])
        return max(value, 0.0)

    earlier = tech_df[tech_df["year"] < year]
    if not earlier.empty:
        value = float(earlier.iloc[-1]["capex_ann_usd_per_tco2"])
        return max(value, 0.0)

    value = float(tech_df.iloc[0]["capex_ann_usd_per_tco2"])
    return max(value, 0.0)


@st.cache_data(show_spinner=False)
def prepare_transition_outputs(
    baseline: pd.DataFrame,
    deploy_df: pd.DataFrame,
    macc: pd.DataFrame,
    grid_emissions: pd.DataFrame | None,
    exchange_rate_krw_per_usd: float = 1300.0,
    lifetime_years: int = 20,
) -> dict | None:
    if baseline is None or deploy_df is None or deploy_df.empty or macc is None:
        return None

    deploy = deploy_df.sort_values("year").copy()
    region_shares, company_shares = compute_baseline_shares(baseline)

    years = deploy["year"].astype(int).to_numpy()
    regions = sorted(set(baseline["location"].fillna("Unknown")))
    if not regions:
        regions = ["Unknown"]
    companies = sorted(set(baseline["company"].fillna("Unknown")))
    if not companies:
        companies = ["Unknown"]

    # Hydrogen distribution (kt)
    h2_total = deploy.get("h2_consumption_kt", pd.Series(np.zeros(len(deploy)), index=deploy.index)).fillna(0.0).to_numpy()
    region_h2_share = region_shares.get("NCC-H2", pd.Series(dtype=float)).reindex(regions, fill_value=0.0)
    region_h2_share = _normalize_series(region_h2_share, regions)
    hydrogen_matrix = np.outer(h2_total, region_h2_share.to_numpy())
    regional_h2 = pd.DataFrame(hydrogen_matrix, columns=regions)
    regional_h2.insert(0, "year", years)
    regional_h2_long = regional_h2.melt(id_vars="year", var_name="region", value_name="hydrogen_kt")

    # Renewable electricity components (TWh)
    y_electricity = deploy.get(
        "electricity_consumption_increase_twh",
        pd.Series(np.zeros(len(deploy)), index=deploy.index),
    ).fillna(0.0).to_numpy()
    ncc_vals = deploy.get("ncc_elec_mt", pd.Series(np.zeros(len(deploy)), index=deploy.index)).fillna(0.0).to_numpy()
    hp_vals = deploy.get("heat_pump_mt", pd.Series(np.zeros(len(deploy)), index=deploy.index)).fillna(0.0).to_numpy()

    mask = (ncc_vals + hp_vals) > 0
    if mask.sum() >= 2 and np.any(y_electricity[mask] > 0):
        coeffs, *_ = np.linalg.lstsq(
            np.vstack([ncc_vals[mask], hp_vals[mask]]).T,
            y_electricity[mask],
            rcond=None,
        )
        ncc_coeff, hp_coeff = coeffs
    else:
        ncc_coeff, hp_coeff = 5.3, 0.005

    elec_ncc = ncc_vals * float(max(ncc_coeff, 0.0))
    elec_hp = hp_vals * float(max(hp_coeff, 0.0))
    calc_total = elec_ncc + elec_hp
    scale = np.ones_like(calc_total)
    valid = calc_total > 0
    scale[valid] = np.divide(
        y_electricity[valid],
        calc_total[valid],
        out=np.ones_like(calc_total[valid]),
        where=calc_total[valid] != 0,
    )
    elec_ncc *= scale
    elec_hp *= scale

    grid_series = None
    default_ef = 0.45
    if grid_emissions is not None and not grid_emissions.empty:
        grid_series = grid_emissions.set_index("year")["grid_ef_tco2_per_mwh"]
        default_ef = float(grid_series.iloc[-1])

    reppa_vals = deploy.get("re_ppa_mt", pd.Series(np.zeros(len(deploy)), index=deploy.index)).fillna(0.0).to_numpy()
    reppa_twh = []
    for idx, year in enumerate(years):
        if reppa_vals[idx] <= 0:
            reppa_twh.append(0.0)
            continue
        ef = default_ef
        if grid_series is not None and int(year) in grid_series.index:
            ef = float(grid_series.loc[int(year)])
        ef = ef if ef > 0 else default_ef
        reppa_twh.append(reppa_vals[idx] / ef)
    reppa_twh = np.array(reppa_twh)

    def _distribute_energy(shares: pd.Series, energy: np.ndarray, label: str) -> pd.DataFrame:
        if not len(regions):
            return pd.DataFrame(columns=["year", "region", "twh", "component"])
        norm_shares = _normalize_series(shares.reindex(regions, fill_value=0.0), regions)
        matrix = np.outer(energy, norm_shares.to_numpy())
        df_component = pd.DataFrame(matrix, columns=regions)
        df_component.insert(0, "year", years)
        df_component = df_component.melt(id_vars="year", var_name="region", value_name="twh")
        df_component["component"] = label
        return df_component

    re_components = [
        _distribute_energy(region_shares.get("NCC-Electricity", pd.Series(dtype=float)), elec_ncc, "NCC-Electricity"),
        _distribute_energy(region_shares.get("Heat_Pump", pd.Series(dtype=float)), elec_hp, "Heat Pump"),
        _distribute_energy(region_shares.get("RE_PPA", pd.Series(dtype=float)), reppa_twh, "RE PPA"),
    ]
    regional_re_components = pd.concat(re_components, ignore_index=True)
    regional_re = (
        regional_re_components.groupby(["year", "region"], as_index=False)["twh"].sum().rename(columns={"twh": "renewable_twh"})
    )

    # Company investment tracking
    tech_columns = {
        "Heat_Pump": "heat_pump_mt",
        "NCC-H2": "ncc_h2_mt",
        "NCC-Electricity": "ncc_elec_mt",
        "RE_PPA": "re_ppa_mt",
    }
    prev_values = {tech: 0.0 for tech in tech_columns}
    company_cumulative = {company: 0.0 for company in companies}
    records: list[dict] = []

    for _, row in deploy.iterrows():
        year = int(row["year"])
        for tech, column in tech_columns.items():
            current = float(row.get(column, 0.0) or 0.0)
            additional_mt = max(0.0, current - prev_values[tech])
            prev_values[tech] = current
            if additional_mt <= 0:
                continue

            capex_ann = _resolve_capex_ann(macc, tech, year)
            if capex_ann <= 0:
                continue

            total_capex_usd = additional_mt * 1e6 * capex_ann * lifetime_years
            share_series = company_shares.get(tech, pd.Series(dtype=float)).reindex(companies, fill_value=0.0)
            share_series = _normalize_series(share_series, companies)

            for company, share in share_series.items():
                if share <= 0:
                    continue
                invest_usd = total_capex_usd * share
                company_cumulative[company] += invest_usd
                invest_musd = invest_usd / 1e6
                invest_krw_bn = invest_musd * exchange_rate_krw_per_usd / 1000
                cum_musd = company_cumulative[company] / 1e6
                cum_krw_bn = cum_musd * exchange_rate_krw_per_usd / 1000

                records.append(
                    {
                        "year": year,
                        "company": company,
                        "tech": tech,
                        "capex_increment_musd": invest_musd,
                        "capex_cumulative_musd": cum_musd,
                        "capex_increment_krw_bn": invest_krw_bn,
                        "capex_cumulative_krw_bn": cum_krw_bn,
                    }
                )

    company_investments = pd.DataFrame(records)
    if not company_investments.empty:
        company_totals = (
            company_investments.groupby("company", as_index=False)
            .agg(
                {
                    "capex_increment_musd": "sum",
                    "capex_cumulative_musd": "max",
                    "capex_increment_krw_bn": "sum",
                    "capex_cumulative_krw_bn": "max",
                }
            )
            .rename(
                columns={
                    "capex_increment_musd": "investment_annual_sum_musd",
                    "capex_cumulative_musd": "investment_total_musd",
                    "capex_increment_krw_bn": "investment_annual_sum_krw_bn",
                    "capex_cumulative_krw_bn": "investment_total_krw_bn",
                }
            )
        )
        company_totals["investment_total_krw_trn"] = company_totals["investment_total_krw_bn"] / 1000
    else:
        company_totals = pd.DataFrame(
            columns=[
                "company",
                "investment_annual_sum_musd",
                "investment_total_musd",
                "investment_annual_sum_krw_bn",
                "investment_total_krw_bn",
                "investment_total_krw_trn",
            ]
        )

    return {
        "regional_h2": regional_h2_long,
        "regional_re": regional_re,
        "regional_re_components": regional_re_components,
        "company_investments": company_investments,
        "company_totals": company_totals,
        "electricity_coefficients": {
            "ncc_twh_per_mt": float(ncc_coeff),
            "heat_pump_twh_per_mt": float(hp_coeff),
        },
    }


# -----------------------------------------------------------------------------
# Page builders
# -----------------------------------------------------------------------------
def show_overview(data: dict) -> None:
    st.title("🏭 Korea Petrochemical MACC – Energy-Based Dashboard")
    st.caption("Facility-level baseline • Energy-explicit MACC • Scenario optimisation")

    baseline = data.get("baseline")
    bau = data.get("bau")

    if baseline is not None and bau is not None:
        metrics = compute_overview_metrics(baseline, bau)
        col1, col2, col3 = st.columns(3)
        metric_card("Total Facilities", f"{metrics['n_facilities']}")
        metric_card("2025 Baseline", format_mt(metrics["baseline_mt"]))
        metric_card("2050 BAU", format_mt(metrics["bau_2050"]))

        st.markdown("### BAU Trajectory (2025–2050)")
        fig = px.line(
            bau,
            x="year",
            y="total_emissions_mt",
            labels={"year": "Year", "total_emissions_mt": "Emissions (MtCO₂/yr)"},
            template="plotly_white",
        )
        fig.update_traces(line=dict(width=3, color="#1f77b4"))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        ### Key Features
        - **Baseline module:** quantifies 2025 emissions and BAU pathway for 248 facilities.
        - **Energy-based MACC:** tracks new energy inputs (H₂, electricity) explicitly without discounting.
        - **Scenario explorer:** compares conservative, moderate, and aggressive roll-outs.
        - **Auto-updating tables:** LaTeX manuscript reads directly from model outputs for consistency.
        """
    )


def show_baseline(data: dict) -> None:
    st.header("📈 Baseline and BAU Analysis")
    baseline = data.get("baseline")
    bau = data.get("bau")
    product_mix = data.get("product_group_energy_mix")

    if baseline is None or bau is None:
        st.info("Run Module 1 to populate baseline outputs.")
        return

    with st.expander("Summary statistics", expanded=True):
        total_mt = baseline["total_emissions_kt"].sum() / 1000
        st.write(f"- **2025 baseline:** {format_mt(total_mt)} across {len(baseline)} facilities.")
        st.write(f"- **Steam crackers (NCC):** {baseline[baseline['process'].str.contains('Naphtha Cracker', case=False)].shape[0]} facilities.")
        st.write("- **Product coverage:** Olefins, Aromatics, Polymers, Intermediates, Other.")

    if product_mix is not None:
        st.markdown("### Fuel mix by product group")
        st.dataframe(product_mix, hide_index=True)

    st.markdown("### BAU emissions trajectory")
    fig = px.line(
        bau,
        x="year",
        y=["total_emissions_mt", "fossil_emissions_mt", "electricity_emissions_mt"],
        labels={"value": "Emissions (MtCO₂/yr)", "variable": "Category"},
        template="plotly_white",
    )
    fig.update_traces(mode="lines+markers")
    st.plotly_chart(fig, use_container_width=True)


def show_macc(data: dict) -> None:
    st.header("💰 Energy-Based MACC Analysis")
    macc = data.get("macc")
    if macc is None:
        st.info("Run Module 2 to populate MACC outputs.")
        return

    years = sorted(macc["year"].unique())
    default_year = 2030 if 2030 in years else years[0]
    selected_year = st.slider("Select year", min_value=int(years[0]), max_value=int(years[-1]), value=int(default_year), step=1)

    subset = macc[macc["year"] == selected_year].copy()
    subset.sort_values("total_cost_usd_per_tco2", inplace=True)

    st.markdown(f"### MACC in {selected_year}")
    st.dataframe(
        subset[["technology", "total_cost_usd_per_tco2", "abatement_potential_mtco2"]],
        hide_index=True,
        column_config={
            "total_cost_usd_per_tco2": st.column_config.NumberColumn("Cost (\$/tCO₂)", format="%.0f"),
            "abatement_potential_mtco2": st.column_config.NumberColumn("Abatement (MtCO₂)", format="%.2f"),
            "technology": "Technology",
        },
    )

    col1, col2 = st.columns(2)

    with col1:
        bar_fig = px.bar(
            subset,
            x="technology",
            y="total_cost_usd_per_tco2",
            color="technology",
            labels={"total_cost_usd_per_tco2": "Cost (\$/tCO₂)", "technology": "Technology"},
            template="plotly_white",
        )
        bar_fig.update_layout(showlegend=False)
        st.plotly_chart(bar_fig, use_container_width=True)

    with col2:
        scatter_fig = px.scatter(
            subset,
            x="abatement_potential_mtco2",
            y="total_cost_usd_per_tco2",
            text="technology",
            size="abatement_potential_mtco2",
            labels={
                "abatement_potential_mtco2": "Abatement (MtCO₂)",
                "total_cost_usd_per_tco2": "Cost (\$/tCO₂)",
            },
            template="plotly_white",
        )
        scatter_fig.update_traces(textposition="top center")
        st.plotly_chart(scatter_fig, use_container_width=True)

    st.markdown("### Cost trajectories (2025–2050)")
    line_fig = px.line(
        macc,
        x="year",
        y="total_cost_usd_per_tco2",
        color="technology",
        labels={"total_cost_usd_per_tco2": "Cost (\$/tCO₂)", "year": "Year"},
        template="plotly_white",
    )
    line_fig.update_traces(mode="lines+markers")
    st.plotly_chart(line_fig, use_container_width=True)


def show_scenarios(data: dict) -> None:
    st.header("🎯 Scenario Explorer")
    scenario_summary = data.get("scenario_summary_for_latex")
    scenario_comparison = data.get("scenario_comparison")
    scenario_deployments: dict | None = data.get("scenario_deployments")  # type: ignore
    facility_allocations: dict | None = data.get("facility_allocations")  # type: ignore

    if scenario_summary is None and scenario_comparison is None:
        st.info("Run Module 3 to generate scenario outputs.")
        return

    if scenario_summary is not None:
        st.markdown("### Key outcomes (relative to 52.0 MtCO₂ baseline)")
        st.dataframe(
            scenario_summary,
            hide_index=True,
            column_config={
                "Scenario": st.column_config.TextColumn("Scenario"),
                "Emissions_2030_Mt": st.column_config.NumberColumn("2030 Emissions (Mt)", format="%.1f"),
                "Reduction_2030_pct": st.column_config.NumberColumn("2030 Reduction (%)", format="%.1f"),
                "Emissions_2050_Mt": st.column_config.NumberColumn("2050 Emissions (Mt)", format="%.1f"),
                "Reduction_2050_pct": st.column_config.NumberColumn("2050 Reduction (%)", format="%.1f"),
            },
        )

    if scenario_comparison is not None:
        st.markdown("### Emissions trajectory by scenario")
        plot_df = scenario_comparison.melt(
            id_vars="scenario",
            value_vars=[col for col in scenario_comparison.columns if "emissions_" in col and col.endswith("_mt")],
            var_name="metric",
            value_name="value",
        )
        # Extract year and scenario
        plot_df["year"] = plot_df["metric"].str.extract(r"emissions_(\d{4})")[0].astype(int)
        fig = px.line(
            plot_df,
            x="year",
            y="value",
            color="scenario",
            labels={"value": "Emissions (MtCO₂/yr)", "year": "Year", "scenario": "Scenario"},
            template="plotly_white",
        )
        fig.update_traces(mode="lines+markers")
        st.plotly_chart(fig, use_container_width=True)

    if scenario_deployments:
        st.markdown("### Deployment details")
        scenario_names = sorted(scenario_deployments.keys())
        selected = st.selectbox("Select scenario", scenario_names, format_func=lambda s: s.capitalize())
        deploy_df = scenario_deployments[selected].copy()

        tech_cols = ["heat_pump_mt", "re_ppa_mt", "ncc_elec_mt", "ncc_h2_mt"]
        existing_cols = [c for c in tech_cols if c in deploy_df.columns]
        if existing_cols:
            stacked = deploy_df.melt(
                id_vars="year",
                value_vars=existing_cols,
                var_name="technology",
                value_name="abatement_mt",
            )
            tech_labels = {
                "heat_pump_mt": "Heat Pump",
                "re_ppa_mt": "RE PPA",
                "ncc_elec_mt": "NCC-Electricity",
                "ncc_h2_mt": "NCC-H₂",
            }
            stacked["technology"] = stacked["technology"].map(tech_labels)
            area_fig = px.area(
                stacked,
                x="year",
                y="abatement_mt",
                color="technology",
                labels={"abatement_mt": "Abatement (MtCO₂)", "year": "Year", "technology": "Technology"},
                template="plotly_white",
            )
            area_fig.update_layout(legend_title=None)
            st.plotly_chart(area_fig, use_container_width=True)

        energy_cols: list[str] = []
        if "electricity_consumption_increase_twh" in deploy_df.columns:
            energy_cols.append("electricity_consumption_increase_twh")
        if "h2_consumption_kt" in deploy_df.columns:
            energy_cols.append("h2_consumption_kt")
        if energy_cols:
            rename_map = {
                "electricity_consumption_increase_twh": "Electricity increase (TWh)",
                "h2_consumption_kt": "Hydrogen consumption (kt)",
            }
            energy_plot = deploy_df[["year"] + energy_cols].rename(columns=rename_map)
            energy_fig = px.line(
                energy_plot,
                x="year",
                y=list(rename_map[col] for col in energy_cols),
                labels={"value": "Value", "variable": "Metric", "year": "Year"},
                template="plotly_white",
            )
            energy_fig.update_traces(mode="lines+markers")
            energy_fig.update_yaxes(title="Energy impact")
            st.plotly_chart(energy_fig, use_container_width=True)

        if "cumulative_capex_musd" in deploy_df.columns:
            capex_fig = px.line(
                deploy_df,
                x="year",
                y="cumulative_capex_musd",
                labels={"cumulative_capex_musd": "Cumulative CAPEX (MUSD)", "year": "Year"},
                template="plotly_white",
            )
            capex_fig.update_traces(mode="lines+markers", line=dict(color="#d62728"))
            st.plotly_chart(capex_fig, use_container_width=True)

    if facility_allocations and selected in facility_allocations:
        st.markdown("#### Facility allocation snapshot (2050)")
        alloc_df = facility_allocations[selected]
        st.dataframe(alloc_df.head(20), hide_index=True)


def _format_scenario_label(name: str) -> str:
    return name.replace("_", " ").replace("-", " ").title()


def show_transition_outlook(data: dict) -> None:
    st.header("🌐 Transition Outlook")
    baseline = data.get("baseline")
    deployments: dict | None = data.get("scenario_deployments")  # type: ignore
    macc = data.get("macc")
    grid_emissions = data.get("grid_emissions")

    if baseline is None or deployments is None or not deployments:
        st.info("Run Modules 1–3 to generate scenario deployment results.")
        return
    if macc is None:
        st.info("Module 2 MACC outputs are required to evaluate investment needs.")
        return

    scenario_names = sorted(deployments.keys())
    selected = st.selectbox(
        "Select scenario",
        scenario_names,
        format_func=_format_scenario_label,
    )

    deploy_df = deployments[selected]
    insights = prepare_transition_outputs(baseline, deploy_df, macc, grid_emissions)
    if insights is None:
        st.warning("Transition insights could not be prepared. Check that scenario files contain the required columns.")
        return

    st.markdown(
        """
        선택한 시나리오에 대해 **지역별 수소·재생에너지 도입 궤적**과
        **기업별 누적 투자 규모**를 함께 정리했습니다. 2035년 50% 감축과
        2050년 90% 감축을 위해 어떤 지역이 언제 얼마나 준비해야 하는지
        최종적으로 한눈에 확인할 수 있습니다.
        """
    )

    regional_h2 = insights["regional_h2"].copy()
    regional_h2["year"] = regional_h2["year"].astype(int)
    h2_fig = px.area(
        regional_h2,
        x="year",
        y="hydrogen_kt",
        color="region",
        labels={"hydrogen_kt": "Hydrogen demand (kt)", "year": "Year", "region": "Region"},
        title="Regional hydrogen requirement trajectory",
        template="plotly_white",
    )
    h2_fig.update_layout(legend_title_text="Region")
    st.plotly_chart(h2_fig, use_container_width=True)

    key_h2_years = regional_h2[regional_h2["year"].isin([2030, 2035, 2050])]
    if not key_h2_years.empty:
        key_h2_years = (
            key_h2_years.groupby(["region", "year"], as_index=False)["hydrogen_kt"].sum()
        )
        h2_pivot = key_h2_years.pivot(index="region", columns="year", values="hydrogen_kt").fillna(0.0)
        h2_pivot = h2_pivot.reindex(sorted(h2_pivot.index))
        st.dataframe(
            h2_pivot.round(1),
            column_config={year: st.column_config.NumberColumn(format="%.1f") for year in h2_pivot.columns},
            use_container_width=True,
        )

    regional_re = insights["regional_re"].copy()
    regional_re["year"] = regional_re["year"].astype(int)
    re_fig = px.area(
        regional_re,
        x="year",
        y="renewable_twh",
        color="region",
        labels={"renewable_twh": "Renewable electricity (TWh)", "year": "Year", "region": "Region"},
        title="Renewable electricity sourcing by region",
        template="plotly_white",
    )
    re_fig.update_layout(legend_title_text="Region")
    st.plotly_chart(re_fig, use_container_width=True)

    components = insights["regional_re_components"].copy()
    components["year"] = components["year"].astype(int)
    comp_2050 = components[components["year"] == 2050]
    if not comp_2050.empty:
        comp_2050 = (
            comp_2050.groupby(["region", "component"], as_index=False)["twh"].sum()
        )
        comp_pivot = comp_2050.pivot(index="region", columns="component", values="twh").fillna(0.0)
        comp_pivot = comp_pivot.reindex(sorted(comp_pivot.index))
        st.dataframe(
            comp_pivot.round(1),
            column_config={col: st.column_config.NumberColumn(format="%.1f") for col in comp_pivot.columns},
            use_container_width=True,
        )

    company_totals = insights["company_totals"].copy()
    if not company_totals.empty:
        company_totals.sort_values("investment_total_krw_bn", ascending=False, inplace=True)
        st.subheader("기업별 누적 투자 규모 (누계)")
        capex_fig = px.bar(
            company_totals.head(10),
            x="investment_total_krw_bn",
            y="company",
            orientation="h",
            labels={"investment_total_krw_bn": "Total investment (₩ billion)", "company": "Company"},
            text_auto=".1f",
            template="plotly_white",
        )
        capex_fig.update_layout(xaxis_title="₩ billion", yaxis_title=None)
        st.plotly_chart(capex_fig, use_container_width=True)

        st.dataframe(
            company_totals.round(
                {
                    "investment_annual_sum_musd": 1,
                    "investment_total_musd": 1,
                    "investment_annual_sum_krw_bn": 1,
                    "investment_total_krw_bn": 1,
                    "investment_total_krw_trn": 3,
                }
            ),
            hide_index=True,
            use_container_width=True,
            column_config={
                "investment_annual_sum_musd": st.column_config.NumberColumn("Annual spend Σ (MUSD)", format="%.1f"),
                "investment_total_musd": st.column_config.NumberColumn("Cumulative (MUSD)", format="%.1f"),
                "investment_annual_sum_krw_bn": st.column_config.NumberColumn("Annual spend Σ (₩ billion)", format="%.1f"),
                "investment_total_krw_bn": st.column_config.NumberColumn("Cumulative (₩ billion)", format="%.1f"),
                "investment_total_krw_trn": st.column_config.NumberColumn("Cumulative (₩ trillion)", format="%.3f"),
            },
        )

        investments = insights["company_investments"].copy()
        if not investments.empty:
            top_companies = company_totals.head(5)["company"].tolist()
            selected_companies = st.multiselect(
                "투자 추적 기업 선택",
                options=company_totals["company"].tolist(),
                default=top_companies,
            )
            if selected_companies:
                timeline = investments[investments["company"].isin(selected_companies)].copy()
                timeline["year"] = timeline["year"].astype(int)
                timeline_fig = px.line(
                    timeline,
                    x="year",
                    y="capex_cumulative_krw_bn",
                    color="company",
                    line_dash="tech",
                    labels={
                        "capex_cumulative_krw_bn": "Cumulative investment (₩ billion)",
                        "year": "Year",
                        "company": "Company",
                        "tech": "Technology",
                    },
                    template="plotly_white",
                )
                timeline_fig.update_traces(mode="lines+markers")
                st.plotly_chart(timeline_fig, use_container_width=True)
    else:
        st.info("No investment commitments were identified for this scenario.")

def show_data_catalog(data: dict) -> None:
    st.header("📂 Data & Assumptions")
    st.markdown(
        """
        - **Module 1 outputs:** `outputs/module_01/*`
        - **Module 2 outputs:** `outputs/module_02/macc_annual_2025_2050.csv`
        - **Module 3 outputs:** `outputs/module_03/*.csv`
        - **Assumption files:** `data/technology_parameters.csv`, `data/h2_price_trajectory.csv`, `data/re_price_trajectory.csv`
        """
    )
    if st.checkbox("Preview technology parameters (first 10 rows)"):
        try:
            st.dataframe(pd.read_csv("data/technology_parameters.csv").head(10))
        except FileNotFoundError:
            st.warning("Missing data/technology_parameters.csv")
    if st.checkbox("Preview hydrogen price trajectory"):
        try:
            st.dataframe(pd.read_csv("data/h2_price_trajectory.csv"))
        except FileNotFoundError:
            st.warning("Missing data/h2_price_trajectory.csv")


def show_about() -> None:
    st.header("ℹ️ About")
    st.markdown(
        """
        **Korean Petrochemical MACC Model (Energy-Based)**  
        - Developed by PLANiT Institute (Jinsu Park).  
        - Fully scripted workflow: baseline → MACC → optimisation → documentation.  
        - LaTeX manuscript (`latex_paper/main.tex`) reads the same CSV files used here, ensuring data consistency.

        **Methodological highlights**
        - Explicit tracking of hydrogen and electricity consumption per facility.
        - Simple annualisation (no discounting) emphasises physical cost components.
        - Technology exclusivity (electric vs hydrogen crackers) handled in optimisation stage.

        **Feedback & collaboration:** feel free to open issues or pull requests in the project repository.
        """
    )


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------
def main() -> None:
    with st.spinner("Loading model outputs…"):
        data = load_data()

    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        [
            "Overview",
            "Baseline & BAU",
            "MACC Analysis",
            "Scenario Explorer",
            "Transition Outlook",
            "Data & Assumptions",
            "About",
        ],
    )

    if page == "Overview":
        show_overview(data)
    elif page == "Baseline & BAU":
        show_baseline(data)
    elif page == "MACC Analysis":
        show_macc(data)
    elif page == "Scenario Explorer":
        show_scenarios(data)
    elif page == "Transition Outlook":
        show_transition_outlook(data)
    elif page == "Data & Assumptions":
        show_data_catalog(data)
    elif page == "About":
        show_about()


if __name__ == "__main__":
    main()
