
from pyomo.environ import ConcreteModel, Set, Param, Var, NonNegativeReals, Objective, Constraint, minimize
from pyomo.environ import SolverFactory

def build_model(years, baseline_mt, target_map, tech_ids, params, groups, depends,
                allow_slack=True, slack_penalty=1e15, discount_rate=0.0, base_year=None):
    m = ConcreteModel()
    m.YEARS = Set(initialize=sorted(years))
    m.TECHS = Set(initialize=sorted(tech_ids))

    # Helpers
    def p_it(getter):
        return {(i,t): getter(i,t) for i in tech_ids for t in years}

    activity = lambda i,t: float(params[i]["activity"][t] or 0.0)
    cap      = lambda i,t: float(params[i]["cap"][t] or 0.0)
    abat     = lambda i,t: float(params[i]["abat"][t] or 0.0)
    capex    = lambda i,t: float(params[i]["capex"][t] or 0.0)
    fixed    = lambda i,t: float(params[i]["fixed"][t] or 0.0)
    varx     = lambda i,t: float(params[i]["var"][t] or 0.0)

    m.activity = Param(m.TECHS, m.YEARS, initialize=p_it(activity), mutable=True)
    m.cap      = Param(m.TECHS, m.YEARS, initialize=p_it(cap), mutable=True)
    m.abat     = Param(m.TECHS, m.YEARS, initialize=p_it(abat), mutable=True)
    m.capex    = Param(m.TECHS, m.YEARS, initialize=p_it(capex), mutable=True)
    m.fixed    = Param(m.TECHS, m.YEARS, initialize=p_it(fixed), mutable=True)
    m.varx     = Param(m.TECHS, m.YEARS, initialize=p_it(varx), mutable=True)

    life_map  = {i: int(params[i]["life"]) for i in tech_ids}
    start_map = {i: int(params[i]["start"]) for i in tech_ids}
    ramp_map  = {i: float(params[i]["ramp"]) for i in tech_ids}
    m.life  = Param(m.TECHS, initialize=life_map, mutable=True)
    m.start = Param(m.TECHS, initialize=start_map, mutable=True)
    m.ramp  = Param(m.TECHS, initialize=ramp_map, mutable=True)

    req = {t: max(0.0, baseline_mt - float(target_map.get(t, baseline_mt))) * 1e6 for t in years}
    m.req = Param(m.YEARS, initialize=req, mutable=True)

    # Discount factors
    if base_year is None:
        base_year = min(years)
    DF = {t: (1.0 / ((1.0 + float(discount_rate)) ** (int(t) - int(base_year)))) for t in years}
    m.df = Param(m.YEARS, initialize=DF, mutable=True)

    # Variables
    m.build = Var(m.TECHS, m.YEARS, within=NonNegativeReals)
    m.share = Var(m.TECHS, m.YEARS, within=NonNegativeReals)
    m.abate = Var(m.TECHS, m.YEARS, within=NonNegativeReals)
    if allow_slack:
        m.shortfall = Var(m.YEARS, within=NonNegativeReals)

    # Constraints
    def stock_rule(m,i,t):
        alive = [tau for tau in years if (tau <= t and (t - tau) < life_map[i])]
        return m.share[i,t] == sum(m.build[i,tau] for tau in alive)
    m.Stock = Constraint(m.TECHS, m.YEARS, rule=stock_rule)

    def start_rule(m,i,t):
        if t < start_map[i]:
            return m.build[i,t] == 0
        return Constraint.Skip
    m.Start = Constraint(m.TECHS, m.YEARS, rule=start_rule)

    def ramp_rule(m,i,t):
        return m.build[i,t] <= m.ramp[i]
    m.Ramp = Constraint(m.TECHS, m.YEARS, rule=ramp_rule)

    def cap_rule(m,i,t):
        return m.share[i,t] <= m.cap[i,t]
    m.Cap = Constraint(m.TECHS, m.YEARS, rule=cap_rule)

    def abat_rule(m,i,t):
        return m.abate[i,t] == m.share[i,t]*m.activity[i,t]*m.abat[i,t]
    m.Abat = Constraint(m.TECHS, m.YEARS, rule=abat_rule)

    def target_rule(m,t):
        if hasattr(m, "shortfall"):
            return sum(m.abate[i,t] for i in m.TECHS) + m.shortfall[t] >= m.req[t]
        else:
            return sum(m.abate[i,t] for i in m.TECHS) >= m.req[t]
    m.Target = Constraint(m.YEARS, rule=target_rule)

    # Mutual exclusivity groups
    m.Groups = []
    for k, G in enumerate(groups):
        G = [g for g in G if g in tech_ids]
        if not G: 
            continue
        def group_rule(m,t, G=tuple(G)):
            return sum(m.share[i,t] for i in G) <= 1.0
        name = f"Group_{k}"
        setattr(m, name, Constraint(m.YEARS, rule=group_rule))
        m.Groups.append(name)

    # Coupling rules primary ≤ secondary
    m.Couplings = []
    for k, (p,s) in enumerate(depends):
        if (p not in tech_ids) or (s not in tech_ids):
            continue
        def couple_rule(m,t, p=p, s=s):
            return m.share[p,t] <= m.share[s,t]
        name = f"Couple_{k}"
        setattr(m, name, Constraint(m.YEARS, rule=couple_rule))
        m.Couplings.append(name)

    # Objective (NPV)
    def obj_rule(m):
        cost_stream = sum( m.df[t] * (m.capex[i,t]/m.life[i] + m.fixed[i,t] + m.varx[i,t]) * m.share[i,t] * m.activity[i,t]
                           for i in m.TECHS for t in m.YEARS )
        pen_stream = sum( m.df[t] * slack_penalty * m.shortfall[t] for t in m.YEARS ) if hasattr(m,"shortfall") else 0.0
        return cost_stream + pen_stream
    m.OBJ = Objective(rule=obj_rule, sense=minimize)
    return m

def solve_model(model, solver="auto"):
    candidates = ["highs","glpk","cbc"] if solver=="auto" else [solver]
    last_err = None
    for s in candidates:
        try:
            opt = SolverFactory(s)
            if opt is None:
                continue
            res = opt.solve(model, tee=False)
            return s, res
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"No suitable LP solver found. Install HiGHS (pip install highspy) or GLPK. Last error: {last_err}")
