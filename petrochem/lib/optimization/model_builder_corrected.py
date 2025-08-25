from pyomo.environ import ConcreteModel, Set, Param, Var, NonNegativeReals, Objective, Constraint, minimize
from typing import Dict, List, Tuple
import pandas as pd

from ..core.scenario import EmissionsScenario
from ..core.portfolio import TechnologyPortfolio
from ..core.technology import TechType

class CorrectedMACCModelBuilder:
    """Build Pyomo optimization models with correct scale units and logic"""
    
    def __init__(self, scenario: EmissionsScenario, portfolio: TechnologyPortfolio):
        self.scenario = scenario
        self.portfolio = portfolio
        self.model = None
        
    def build_model(self, 
                   allow_slack: bool = True, 
                   slack_penalty: float = 1e15,
                   discount_rate: float = 0.05) -> ConcreteModel:
        """Build complete Pyomo model with corrected units"""
        
        m = ConcreteModel("MACC_Corrected")
        
        # Sets
        m.YEARS = Set(initialize=sorted(self.scenario.timeline))
        m.TECHS = Set(initialize=list(self.portfolio.technologies.keys()))
        m.PROCESSES = Set(initialize=list(self.scenario.baseline.process_baselines.keys()))
        
        # Parameters - Technology characteristics with correct units
        self._add_technology_parameters(m)
        
        # Parameters - Scenario data  
        self._add_scenario_parameters(m, discount_rate)
        
        # Variables - Separated capacity and production
        self._add_variables(m, allow_slack)
        
        # Constraints - Corrected formulation
        self._add_constraints(m)
        
        # Objective - Proper cost accounting
        self._add_objective(m, allow_slack, slack_penalty)
        
        self.model = m
        return m
    
    def _add_technology_parameters(self, m):
        """Add technology parameters with correct units"""
        
        # Technology characteristics
        capex_per_kt_data = {}    # Million USD per kt/year capacity
        opex_per_t_data = {}      # USD per tonne production
        abatement_per_t_data = {} # tCO2 per tonne production
        lifetime_data = {}        # Years
        max_capacity_data = {}    # kt/year maximum deployable capacity
        
        for tech_id, tech in self.portfolio.technologies.items():
            lifetime_data[tech_id] = tech.constraints.lifetime_years
            
            for year in self.scenario.timeline:
                if year >= tech.constraints.start_year:
                    # CORRECTED: Keep CAPEX in Million USD/kt capacity units
                    capex_per_kt_data[(tech_id, year)] = tech.cost_structure.capex_usd_per_kt / 1e6  # Convert to Million USD/kt
                    
                    # CORRECTED: OPEX in USD per tonne production
                    opex_per_t_data[(tech_id, year)] = tech.cost_structure.opex_delta_usd_per_t
                    
                    # CORRECTED: Abatement per tonne production
                    abatement_per_t_data[(tech_id, year)] = tech.abatement_potential
                    
                    # CORRECTED: Calculate maximum deployable capacity based on technology type
                    max_capacity = self._calculate_max_capacity(tech, year)
                    max_capacity_data[(tech_id, year)] = max_capacity
                else:
                    # Technology not available yet
                    capex_per_kt_data[(tech_id, year)] = 0.0
                    opex_per_t_data[(tech_id, year)] = 0.0
                    abatement_per_t_data[(tech_id, year)] = 0.0
                    max_capacity_data[(tech_id, year)] = 0.0
        
        m.capex_per_kt = Param(m.TECHS, m.YEARS, initialize=capex_per_kt_data, default=0.0)
        m.opex_per_t = Param(m.TECHS, m.YEARS, initialize=opex_per_t_data, default=0.0)
        m.abatement_per_t = Param(m.TECHS, m.YEARS, initialize=abatement_per_t_data, default=0.0)
        m.lifetime = Param(m.TECHS, initialize=lifetime_data)
        m.max_capacity = Param(m.TECHS, m.YEARS, initialize=max_capacity_data, default=0.0)
        
        # Ramp rate constraints (fraction of max capacity per year)
        ramp_data = {tech_id: tech.constraints.ramp_rate_per_year 
                     for tech_id, tech in self.portfolio.technologies.items()}
        m.ramp_rate = Param(m.TECHS, initialize=ramp_data)
        
    def _calculate_max_capacity(self, tech, year) -> float:
        """Calculate maximum deployable capacity for a technology in a given year"""
        
        if tech.process_type not in self.scenario.baseline.process_baselines:
            return 0.0
            
        baseline = self.scenario.baseline.process_baselines[tech.process_type]
        
        if tech.tech_type == TechType.TRANSITION:
            # For transitions: max capacity = existing capacity in source band * max applicability
            band_key = f"{tech.process_type}_{tech.from_band.value}"
            source_capacity = self.scenario.baseline.get_band_capacity(tech.process_type, band_key)
            return source_capacity * tech.constraints.max_applicability
            
        else:  # Alternative technology
            # For alternatives: max capacity = total process capacity * max penetration
            total_capacity = baseline.production_kt
            return total_capacity * tech.constraints.max_applicability
    
    def _add_scenario_parameters(self, m, discount_rate: float):
        """Add scenario parameters with correct units"""
        
        # Emissions requirements (tonnes CO2)
        req_data = {year: self.scenario.get_required_abatement(year) * 1e6  # Convert Mt to tonnes
                    for year in self.scenario.timeline}
        m.requirement = Param(m.YEARS, initialize=req_data)
        
        # Discount factors
        base_year = min(self.scenario.timeline)
        df_data = {year: 1.0 / ((1.0 + discount_rate) ** (year - base_year))
                   for year in self.scenario.timeline}
        m.discount_factor = Param(m.YEARS, initialize=df_data)
        
        # Capital Recovery Factor for annualized CAPEX
        crf_data = {}
        for tech_id, tech in self.portfolio.technologies.items():
            lifetime = tech.constraints.lifetime_years
            if discount_rate > 0:
                crf = discount_rate / (1 - (1 + discount_rate) ** -lifetime)
            else:
                crf = 1.0 / lifetime
            crf_data[tech_id] = crf
        m.crf = Param(m.TECHS, initialize=crf_data)
        
    def _add_variables(self, m, allow_slack: bool):
        """Add decision variables with clear separation"""
        
        # CORRECTED: Capacity installation decisions (kt/year new capacity per year)
        m.install_capacity = Var(m.TECHS, m.YEARS, within=NonNegativeReals)
        
        # CORRECTED: Total available capacity (kt/year total capacity)
        m.total_capacity = Var(m.TECHS, m.YEARS, within=NonNegativeReals)
        
        # CORRECTED: Production using each technology (kt/year production)
        m.production = Var(m.TECHS, m.YEARS, within=NonNegativeReals)
        
        # Abatement achieved (tonnes CO2)
        m.abatement = Var(m.TECHS, m.YEARS, within=NonNegativeReals)
        
        # Shortfall variable (if allowed)
        if allow_slack:
            m.shortfall = Var(m.YEARS, within=NonNegativeReals)
    
    def _add_constraints(self, m):
        """Add constraints with corrected formulation"""
        
        # CORRECTED Constraint 1: Capacity evolution (vintaging)
        def capacity_evolution_rule(model, tech, year):
            tech_obj = self.portfolio.technologies[tech]
            lifetime = tech_obj.constraints.lifetime_years
            
            # Sum capacity installed in years that are still active
            active_capacity = sum(
                model.install_capacity[tech, tau] 
                for tau in model.YEARS 
                if tau <= year and (year - tau) < lifetime
            )
            
            return model.total_capacity[tech, year] == active_capacity
        m.capacity_evolution = Constraint(m.TECHS, m.YEARS, rule=capacity_evolution_rule)
        
        # CORRECTED Constraint 2: Production limited by available capacity
        def production_limit_rule(model, tech, year):
            return model.production[tech, year] <= model.total_capacity[tech, year]
        m.production_limit = Constraint(m.TECHS, m.YEARS, rule=production_limit_rule)
        
        # CORRECTED Constraint 3: Capacity installation limits
        def capacity_limit_rule(model, tech, year):
            return model.install_capacity[tech, year] <= model.max_capacity[tech, year]
        m.capacity_limit = Constraint(m.TECHS, m.YEARS, rule=capacity_limit_rule)
        
        # CORRECTED Constraint 4: Ramp rate for capacity installation
        def ramp_rule(model, tech, year):
            if year == min(self.scenario.timeline):
                return Constraint.Skip
            max_annual_install = model.max_capacity[tech, year] * model.ramp_rate[tech]
            return model.install_capacity[tech, year] <= max_annual_install
        m.ramp_constraint = Constraint(m.TECHS, m.YEARS, rule=ramp_rule)
        
        # CORRECTED Constraint 5: Abatement calculation
        def abatement_rule(model, tech, year):
            # Abatement = Production * Abatement_per_tonne
            return model.abatement[tech, year] == (
                model.production[tech, year] * model.abatement_per_t[tech, year] * 1000  # kt to tonnes
            )
        m.abatement_calc = Constraint(m.TECHS, m.YEARS, rule=abatement_rule)
        
        # CORRECTED Constraint 6: Emissions target
        def target_rule(model, year):
            total_abatement = sum(model.abatement[tech, year] for tech in model.TECHS)
            if hasattr(model, 'shortfall'):
                return total_abatement + model.shortfall[year] >= model.requirement[year]
            else:
                return total_abatement >= model.requirement[year]
        m.target_constraint = Constraint(m.YEARS, rule=target_rule)
        
        # CORRECTED Constraint 7: Process mass balance (for transitions)
        self._add_process_balance_constraints(m)
        
    def _add_process_balance_constraints(self, m):
        """Add process-level mass balance constraints"""
        
        for process_type in self.scenario.baseline.process_baselines:
            baseline = self.scenario.baseline.process_baselines[process_type]
            total_baseline_production = baseline.production_kt
            
            def process_balance_rule(model, year, proc=process_type):
                # Total production using all technologies for this process
                process_production = sum(
                    model.production[tech, year] 
                    for tech in model.TECHS 
                    if self.portfolio.technologies[tech].process_type == proc
                )
                
                # Cannot exceed baseline production capacity
                return process_production <= total_baseline_production
            
            constraint_name = f"process_balance_{process_type}"
            setattr(m, constraint_name, Constraint(m.YEARS, rule=process_balance_rule))
    
    def _add_objective(self, m, allow_slack: bool, slack_penalty: float):
        """Add objective with corrected cost calculation"""
        
        def objective_rule(model):
            total_cost = 0.0
            
            # CORRECTED: Technology costs
            for tech in model.TECHS:
                for year in model.YEARS:
                    # Annualized CAPEX based on capacity installation
                    annual_capex = (model.install_capacity[tech, year] * 
                                   model.capex_per_kt[tech, year] * 
                                   model.crf[tech])  # Million USD/year
                    
                    # Annual OPEX based on production
                    annual_opex = (model.production[tech, year] * 
                                  model.opex_per_t[tech, year] / 1000)  # Million USD/year (kt * USD/t / 1000)
                    
                    # Discounted total cost
                    total_cost += model.discount_factor[year] * (annual_capex + annual_opex)
            
            # Penalty for shortfalls
            if allow_slack and hasattr(model, 'shortfall'):
                penalty_cost = sum(
                    model.discount_factor[year] * slack_penalty * model.shortfall[year] / 1e6  # Convert to Million USD
                    for year in model.YEARS
                )
                total_cost += penalty_cost
            
            return total_cost
        
        m.total_cost = Objective(rule=objective_rule, sense=minimize)
    
    def get_model_summary(self) -> Dict:
        """Get summary of corrected model"""
        if not self.model:
            return {"error": "Model not built yet"}
            
        m = self.model
        
        return {
            "model_type": "Corrected MACC Model",
            "sets": {
                "years": len(m.YEARS),
                "technologies": len(m.TECHS), 
                "processes": len(m.PROCESSES)
            },
            "variables": {
                "install_capacity": len(m.TECHS) * len(m.YEARS),
                "total_capacity": len(m.TECHS) * len(m.YEARS),
                "production": len(m.TECHS) * len(m.YEARS),
                "abatement": len(m.TECHS) * len(m.YEARS),
                "shortfall": len(m.YEARS) if hasattr(m, 'shortfall') else 0
            },
            "unit_corrections": {
                "capex": "Million USD per kt/year capacity",
                "opex": "USD per tonne production", 
                "abatement": "tCO2 per tonne production",
                "capacity": "kt/year processing capacity",
                "production": "kt/year actual production"
            }
        }