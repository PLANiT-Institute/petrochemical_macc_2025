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
    elif page == "Data & Assumptions":
        show_data_catalog(data)
    elif page == "About":
        show_about()


if __name__ == "__main__":
    main()
