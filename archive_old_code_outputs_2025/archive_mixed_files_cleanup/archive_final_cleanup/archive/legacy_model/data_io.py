
import pandas as pd
import numpy as np

def read_excel(path):
    xls = pd.ExcelFile(path)
    return {name: xls.parse(name) for name in xls.sheet_names}

def baseline_total_mt(sheets):
    if "Baseline_Assumptions" in sheets:
        df = sheets["Baseline_Assumptions"]
        m = df["Parameter"]=="Total_Scope1plus2_MtCO2e_2023"
        if m.any():
            return float(df.loc[m,"Value"].values[0])
    if "Baseline_2023" in sheets:
        b = sheets["Baseline_2023"]
        return float((b["Scope1_tCO2e"].sum(skipna=True) + b["Scope2_tCO2e"].sum(skipna=True))/1e6)
    raise ValueError("Cannot determine baseline (MtCO2e)")

def targets_map(sheets, years=None):
    emt = sheets["Emissions_Target"].dropna(subset=["Year"])
    emt["Year"] = emt["Year"].astype(int)
    if years is not None:
        emt = emt[emt["Year"].isin(years)]
    years_all = emt["Year"].tolist()
    tmap = dict(zip(emt["Year"], emt["Target_MtCO2e"]))
    return years_all, tmap

def _interp(rows, col, years):
    if rows.empty:
        return {y: np.nan for y in years}
    if "Ref_Year" not in rows.columns or rows["Ref_Year"].isna().all():
        v = rows.iloc[0][col] if col in rows.columns else np.nan
        return {y: v for y in years}
    r = rows.dropna(subset=["Ref_Year"]).copy()
    r["Ref_Year"] = r["Ref_Year"].astype(int).sort_values()
    r = r.sort_values("Ref_Year")
    xs = r["Ref_Year"].tolist()
    vs = [r.iloc[i][col] if col in r.columns else np.nan for i in range(len(r))]
    series = {}
    for y in years:
        if y <= xs[0]: series[y] = vs[0]; continue
        if y >= xs[-1]: series[y] = vs[-1]; continue
        for i in range(len(xs)-1):
            x0,x1 = xs[i], xs[i+1]
            if x0 <= y <= x1:
                v0,v1 = vs[i], vs[i+1]
                if pd.isna(v0) and pd.isna(v1): val = np.nan
                elif pd.isna(v0): val = v1
                elif pd.isna(v1): val = v0
                else:
                    t = (y-x0)/(x1-x0); val = v0 + t*(v1-v0)
                series[y] = val; break
    return series

def build_timeseries(sheets, years, ramp_default=0.2):
    macc = sheets["MACC_Template"]
    tech = sheets.get("TechOptions", None)
    tids = sorted(macc["TechID"].dropna().unique())
    params = {}
    for tid in tids:
        rows = macc[macc["TechID"]==tid]
        activity = _interp(rows, "Eligible_Activity_Volume", years)
        cap = _interp(rows, "Max_Adoption_Share", years)
        abat = _interp(rows, "Abatement_tCO2_per_activity", years)
        capex = _interp(rows, "Cost_CAPEX_KRW_per_unit", years)
        fixed = _interp(rows, "Cost_FixedOPEX_KRW_per_unit_per_yr", years)
        varx  = _interp(rows, "Cost_VarOPEX_KRW_per_activity", years)
        life  = _interp(rows, "Lifetime_years", years)
        start = _interp(rows, "StartYear_Commercial", years)
        # backfill from TechOptions if missing
        life_val = start_val = ramp_val = None
        if tech is not None and not tech[tech["TechID"]==tid].empty:
            rec = tech[tech["TechID"]==tid].iloc[0]
            life_val = rec.get("Lifetime_years", None)
            start_val = rec.get("StartYear_Commercial", None)
            ramp_val = rec.get("RampUpSharePerYear", None)
        r0 = ramp_default if ramp_val is None or pd.isna(ramp_val) else float(ramp_val)
        life_scalar = next((int(v) for v in life.values() if v==v), 20)
        start_scalar = next((int(v) for v in start.values() if v==v), min(years))
        params[tid] = {
            "activity": activity, "cap": cap, "abat": abat,
            "capex": capex, "fixed": fixed, "var": varx,
            "life": life_scalar, "start": start_scalar, "ramp": float(r0)
        }
    return tids, params

def parse_links(sheets):
    groups, depends = [], []
    if "TechLinks" not in sheets: return groups, depends
    L = sheets["TechLinks"]
    if "RuleType" not in L.columns: return groups, depends
    parent = {}
    def find(x):
        parent.setdefault(x,x)
        if parent[x]!=x: parent[x]=find(parent[x])
        return parent[x]
    def union(a,b):
        ra, rb = find(a), find(b)
        if ra!=rb: parent[rb]=ra
    for _, r in L.iterrows():
        rt = str(r.get("RuleType","")).lower()
        a = str(r.get("PrimaryTech",""))
        b = str(r.get("SecondaryTech",""))
        if rt=="mutuallyexclusive" and a and b: union(a,b)
        elif rt=="coupling" and a and b: depends.append((a,b))
    sets = {}
    for x in list(parent.keys()):
        rx=find(x); sets.setdefault(rx,set()).add(x)
    groups = [v for v in sets.values() if len(v)>1]
    return groups, depends
