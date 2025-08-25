
import click, os
import pandas as pd
from .data_io import read_excel, baseline_total_mt, targets_map, build_timeseries, parse_links
from .model_pyomo import build_model, solve_model

@click.command()
@click.option("--excel", required=True, help="Path to Excel scenario file")
@click.option("--years", multiple=True, type=int, help="Two numbers: inclusive range; else explicit list")
@click.option("--allow-slack", is_flag=True, help="Allow shortfall with penalty")
@click.option("--no-slack", is_flag=True, help="Disallow slack (hard constraint)")
@click.option("--slack-penalty", type=float, default=1e15, help="Penalty KRW/tCO2 (very large by default)")
@click.option("--discount-rate", type=float, default=0.0, help="Annual discount rate (e.g., 0.05)")
@click.option("--ramp-default", type=float, default=0.2, help="Default ramp share/year if missing")
@click.option("--solver", type=str, default="auto", help="highs|glpk|cbc|auto")
@click.option("--plots", is_flag=True, help="Emit cost-ordered MACC-like chart per year")
def main(excel, years, allow_slack, no_slack, slack_penalty, discount_rate, ramp_default, solver, plots):
    sheets = read_excel(excel)
    years_all, tmap = targets_map(sheets, None)

    if years:
        yrs = list(years)
        if len(yrs)==2 and min(yrs)<max(yrs) and len(set(yrs))==2:
            years_model = [y for y in range(min(yrs), max(yrs)+1) if y in years_all]
        else:
            years_model = [y for y in yrs if y in years_all]
    else:
        years_model = years_all

    baseline_mt = baseline_total_mt(sheets)

    tech_ids, params = build_timeseries(sheets, years_model, ramp_default=ramp_default)
    groups, depends = parse_links(sheets)

    slack = allow_slack and (not no_slack)
    m = build_model(years_model, baseline_mt, tmap, tech_ids, params, groups, depends,
                    allow_slack=slack, slack_penalty=slack_penalty,
                    discount_rate=discount_rate, base_year=min(years_model))

    solver_used, results = solve_model(m, solver=solver)
    os.makedirs("outputs", exist_ok=True)

    # Export per-year plans
    summary = []
    for y in years_model:
        rows = []
        for i in tech_ids:
            rows.append({
                "TechID": i, "Year": y,
                "Build_share": float(m.build[i,y].value or 0.0),
                "Share": float(m.share[i,y].value or 0.0),
                "Abatement_tCO2": float(m.abate[i,y].value or 0.0),
                "Activity": float(m.activity[i,y].value),
                "Cap": float(m.cap[i,y].value),
                "Abate_per_activity": float(m.abat[i,y].value)
            })
        df = pd.DataFrame(rows).sort_values(["Year","TechID"])
        df.to_csv(os.path.join("outputs", f"plan_{y}.csv"), index=False, encoding="utf-8-sig")

        achieved = df["Abatement_tCO2"].sum()
        shortfall = float(m.shortfall[y].value or 0.0) if hasattr(m,"shortfall") else 0.0
        summary.append({
            "Year": y,
            "Baseline_MtCO2e": baseline_mt,
            "Target_MtCO2e": float(tmap.get(y, baseline_mt)),
            "Required_Abatement_MtCO2": float(m.req[y].value/1e6),
            "Achieved_Abatement_MtCO2": achieved/1e6,
            "Shortfall_MtCO2": shortfall/1e6,
            "Solver": solver_used,
            "Status": str(results.solver.termination_condition) if hasattr(results,'solver') else "OK"
        })

        if plots:
            import numpy as np, matplotlib.pyplot as plt
            # cost-per-t ranking
            costs = []
            for i in tech_ids:
                lf = max(1, int(params[i]["life"]))
                c_act = (params[i]["capex"][y] or 0.0)/lf + (params[i]["fixed"][y] or 0.0) + (params[i]["var"][y] or 0.0)
                ab = (params[i]["abat"][y] or 0.0)
                cpt = c_act/ab if ab>0 else np.inf
                if ab>0:
                    costs.append((i, cpt))
            cost_map = dict(costs)
            ach = df[df["Abatement_tCO2"]>0].copy()
            if not ach.empty:
                ach["cpt"] = ach["TechID"].map(cost_map)
                ach = ach.replace([np.inf,-np.inf], np.nan).dropna(subset=["cpt"]).sort_values("cpt")
                widths = ach["Abatement_tCO2"].values/1e6
                lefts = np.concatenate(([0.0], np.cumsum(widths)[:-1]))
                heights = ach["cpt"].values
                import matplotlib.pyplot as plt
                plt.figure(figsize=(12,6))
                for l,w,h in zip(lefts,widths,heights):
                    plt.bar(l,h,width=w,align="edge")
                plt.xlabel("Cumulative abatement (MtCO₂)"); plt.ylabel("Annual cost per tCO₂ (KRW)")
                plt.title(f"Optimized cost curve — {y} (solver: {solver_used})")
                plt.tight_layout(); plt.savefig(os.path.join("outputs", f"cost_curve_{y}.png"), dpi=200); plt.close()

    pd.DataFrame(summary).to_csv(os.path.join("outputs","summary.csv"), index=False, encoding="utf-8-sig")
    click.echo(f"[OK] Solver: {solver_used}. Results saved to outputs/.")
