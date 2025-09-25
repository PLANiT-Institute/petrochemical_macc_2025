from pyomo.environ import ConcreteModel, Set, Param, Var, NonNegativeReals, Objective, Constraint, minimize
from typing import Dict, List, Tuple
import pandas as pd

from ..core.scenario import EmissionsScenario
from ..core.portfolio import TechnologyPortfolio
from ..core.technology import TechType

class MACCModelBuilder:
    """Build Pyomo optimization models for MACC analysis"""
    
    def __init__(self, scenario: EmissionsScenario, portfolio: TechnologyPortfolio):
        self.scenario = scenario
        self.portfolio = portfolio
        self.model = None
        
    def build_model(self, 
                   allow_slack: bool = True, 
                   slack_penalty: float = 1e15,
                   discount_rate: float = 0.05) -> ConcreteModel:
        """Build complete Pyomo model"""
        
        m = ConcreteModel("MACC_Optimization")
        
        # Sets
        m.YEARS = Set(initialize=sorted(self.scenario.timeline))
        m.TECHS = Set(initialize=list(self.portfolio.technologies.keys()))
        m.PROCESSES = Set(initialize=list(self.scenario.baseline.process_baselines.keys()))
        
        # Parameters - Technology characteristics
        self._add_technology_parameters(m)
        
        # Parameters - Scenario data  
        self._add_scenario_parameters(m, discount_rate)
        
        # Variables
        self._add_variables(m, allow_slack)
        
        # Constraints
        self._add_constraints(m)
        
        # Objective
        self._add_objective(m, allow_slack, slack_penalty)
        
        self.model = m
        return m
    
    def _add_technology_parameters(self, m):
        """Add technology-specific parameters"""
        
        # Cost parameters
        capex_data = {}
        opex_data = {}
        abatement_data = {}
        activity_data = {}
        lifetime_data = {}
        
        for tech_id, tech in self.portfolio.technologies.items():
            lifetime_data[tech_id] = tech.constraints.lifetime_years
            
            for year in self.scenario.timeline:
                if year >= tech.constraints.start_year:
                    capex_data[(tech_id, year)] = tech.cost_structure.capex_usd_per_kt / 1000  # Convert to USD/t
                    opex_data[(tech_id, year)] = tech.cost_structure.opex_delta_usd_per_t
                    abatement_data[(tech_id, year)] = tech.abatement_potential
                    
                    # Calculate applicable activity for this technology
                    if tech.process_type in self.scenario.baseline.process_baselines:
                        baseline = self.scenario.baseline.process_baselines[tech.process_type]
                        
                        if tech.tech_type == TechType.TRANSITION:
                            # For transitions, activity is capacity in the source band
                            band_key = f"{tech.process_type}_{tech.from_band.value}"
                            applicable_capacity = self.scenario.baseline.get_band_capacity(tech.process_type, band_key)
                        else:
                            # For alternatives, activity is total process capacity  
                            applicable_capacity = baseline.production_kt
                            
                        activity_data[(tech_id, year)] = applicable_capacity * tech.constraints.max_applicability
                    else:
                        activity_data[(tech_id, year)] = 0.0
                else:
                    # Technology not available yet
                    capex_data[(tech_id, year)] = 0.0
                    opex_data[(tech_id, year)] = 0.0
                    abatement_data[(tech_id, year)] = 0.0
                    activity_data[(tech_id, year)] = 0.0
        
        m.capex = Param(m.TECHS, m.YEARS, initialize=capex_data, default=0.0)
        m.opex = Param(m.TECHS, m.YEARS, initialize=opex_data, default=0.0)
        m.abatement = Param(m.TECHS, m.YEARS, initialize=abatement_data, default=0.0)
        m.activity = Param(m.TECHS, m.YEARS, initialize=activity_data, default=0.0)
        m.lifetime = Param(m.TECHS, initialize=lifetime_data)
        
        # Ramp rate constraints
        ramp_data = {tech_id: tech.constraints.ramp_rate_per_year 
                     for tech_id, tech in self.portfolio.technologies.items()}
        m.ramp_rate = Param(m.TECHS, initialize=ramp_data)
        
    def _add_scenario_parameters(self, m, discount_rate: float):
        """Add scenario-specific parameters"""
        
        # Emissions requirements
        req_data = {year: self.scenario.get_required_abatement(year) * 1e6  # Convert to tonnes
                    for year in self.scenario.timeline}
        m.requirement = Param(m.YEARS, initialize=req_data)
        
        # Discount factors
        base_year = min(self.scenario.timeline)
        df_data = {year: 1.0 / ((1.0 + discount_rate) ** (year - base_year))
                   for year in self.scenario.timeline}
        m.discount_factor = Param(m.YEARS, initialize=df_data)
        
    def _add_variables(self, m, allow_slack: bool):
        """Add decision variables"""
        
        # Technology deployment (kt/year capacity)
        m.deployment = Var(m.TECHS, m.YEARS, within=NonNegativeReals)
        
        # Annual abatement achieved (tonnes CO2)
        m.abate_achieved = Var(m.TECHS, m.YEARS, within=NonNegativeReals)
        
        # Shortfall variable (if allowed)
        if allow_slack:
            m.shortfall = Var(m.YEARS, within=NonNegativeReals)
    
    def _add_constraints(self, m):
        """Add model constraints"""
        
        # Constraint 1: Abatement calculation
        def abatement_rule(model, tech, year):
            return model.abate_achieved[tech, year] == (
                model.deployment[tech, year] * model.abatement[tech, year] * 1000  # Convert kt to t
            )
        m.abatement_calc = Constraint(m.TECHS, m.YEARS, rule=abatement_rule)
        
        # Constraint 2: Activity/capacity limits
        def capacity_rule(model, tech, year):
            return model.deployment[tech, year] <= model.activity[tech, year]
        m.capacity_limit = Constraint(m.TECHS, m.YEARS, rule=capacity_rule)
        
        # Constraint 3: Ramp rate constraints
        def ramp_rule(model, tech, year):
            if year == min(self.scenario.timeline):
                return Constraint.Skip
            prev_year = year - 1
            max_increase = model.activity[tech, year] * model.ramp_rate[tech]
            return model.deployment[tech, year] <= model.deployment[tech, prev_year] + max_increase
        m.ramp_constraint = Constraint(m.TECHS, m.YEARS, rule=ramp_rule)
        
        # Constraint 4: Emissions target
        def target_rule(model, year):
            total_abatement = sum(model.abate_achieved[tech, year] for tech in model.TECHS)
            if hasattr(model, 'shortfall'):
                return total_abatement + model.shortfall[year] * 1e6 >= model.requirement[year]
            else:
                return total_abatement >= model.requirement[year]
        m.target_constraint = Constraint(m.YEARS, rule=target_rule)
        
        # Constraint 5: Technology mutual exclusivity (if needed)
        self._add_exclusivity_constraints(m)
        
    def _add_exclusivity_constraints(self, m):
        """Add mutual exclusivity constraints for competing technologies"""
        
        # Group technologies by process and identify conflicts
        exclusivity_groups = {}
        
        for tech_id, tech in self.portfolio.technologies.items():
            if tech.tech_type == TechType.TRANSITION:
                # Transitions from same band are mutually exclusive
                key = (tech.process_type, tech.from_band)
                if key not in exclusivity_groups:
                    exclusivity_groups[key] = []
                exclusivity_groups[key].append(tech_id)
        
        # Add constraints for groups with more than one technology
        constraint_count = 0
        for key, tech_list in exclusivity_groups.items():
            if len(tech_list) > 1:
                def exclusivity_rule(model, year, techs=tech_list):
                    process_type, from_band = key
                    if process_type in self.scenario.baseline.process_baselines:
                        band_key = f"{process_type}_{from_band.value}"
                        max_capacity = self.scenario.baseline.get_band_capacity(process_type, band_key)
                        return sum(model.deployment[tech, year] for tech in techs) <= max_capacity
                    else:
                        return Constraint.Skip
                
                constraint_name = f"exclusivity_{constraint_count}"
                setattr(m, constraint_name, Constraint(m.YEARS, rule=exclusivity_rule))
                constraint_count += 1
    
    def _add_objective(self, m, allow_slack: bool, slack_penalty: float):
        """Add objective function (minimize NPV of total cost)"""
        
        def objective_rule(model):
            # Technology deployment costs
            tech_costs = sum(
                model.discount_factor[year] * (
                    model.capex[tech, year] * model.deployment[tech, year] * 1000 +  # Convert back to USD
                    model.opex[tech, year] * model.deployment[tech, year] * 1000
                ) for tech in model.TECHS for year in model.YEARS
            )
            
            # Penalty for shortfalls
            penalty_costs = 0.0
            if allow_slack and hasattr(model, 'shortfall'):
                penalty_costs = sum(
                    model.discount_factor[year] * slack_penalty * model.shortfall[year]
                    for year in model.YEARS
                )
            
            return tech_costs + penalty_costs
        
        m.total_cost = Objective(rule=objective_rule, sense=minimize)
    
    def get_model_summary(self) -> Dict:
        """Get summary statistics of the built model"""
        if not self.model:
            return {"error": "Model not built yet"}
            
        m = self.model
        
        return {
            "sets": {
                "years": len(m.YEARS),
                "technologies": len(m.TECHS), 
                "processes": len(m.PROCESSES)
            },
            "variables": {
                "deployment": len(m.TECHS) * len(m.YEARS),
                "abatement": len(m.TECHS) * len(m.YEARS),
                "shortfall": len(m.YEARS) if hasattr(m, 'shortfall') else 0
            },
            "constraints": {
                "abatement_calc": len(m.TECHS) * len(m.YEARS),
                "capacity_limit": len(m.TECHS) * len(m.YEARS),
                "ramp_constraint": len(m.TECHS) * (len(m.YEARS) - 1),
                "target_constraint": len(m.YEARS)
            },
            "parameters_populated": {
                "capex": sum(1 for (t, y) in m.capex if m.capex[t, y] > 0),
                "activity": sum(1 for (t, y) in m.activity if m.activity[t, y] > 0)
            }
        }