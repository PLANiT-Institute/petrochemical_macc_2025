from dataclasses import dataclass
from typing import Dict, Optional, List
import numpy as np

@dataclass
class CostStructure:
    capex_usd_per_kt: float
    opex_delta_usd_per_t: float
    maintenance_pct: float
    fuel_cost_usd_per_gj: Optional[float] = None

@dataclass
class TechnologyConstraints:
    lifetime_years: int
    start_year: int
    ramp_rate_per_year: float
    max_applicability: float
    technical_readiness_level: int

class Technology:
    def __init__(
        self,
        tech_id: str,
        name: str,
        process_type: str,
        cost_structure: CostStructure,
        constraints: TechnologyConstraints,
        emission_factor: float,  # tCO2/t product
        abatement_potential: float = 0.0,  # tCO2/t reduction vs baseline
        baseline_displacement: List[str] = None
    ):
        self.tech_id = tech_id
        self.name = name
        self.process_type = process_type
        self.cost_structure = cost_structure
        self.constraints = constraints
        self.emission_factor = emission_factor
        self.abatement_potential = abatement_potential
        self.baseline_displacement = baseline_displacement or []
        
    def calculate_lcoa(self, discount_rate: float = 0.05) -> float:
        """Calculate Levelized Cost of Abatement (USD/tCO2)"""
        if self.abatement_potential <= 0:
            return float('inf')
            
        # Annualized CAPEX
        crf = discount_rate / (1 - (1 + discount_rate) ** -self.constraints.lifetime_years)
        annual_capex = self.cost_structure.capex_usd_per_kt * crf / 1000  # Convert to USD/t
        
        # Total annual cost per tonne
        annual_cost_per_t = annual_capex + self.cost_structure.opex_delta_usd_per_t
        
        # LCOA = Annual cost per tonne / Abatement per tonne
        return annual_cost_per_t / self.abatement_potential
    
    def get_max_deployment(self, year: int, baseline_capacity: float) -> float:
        """Get maximum possible deployment in given year (kt/year)"""
        if year < self.constraints.start_year:
            return 0.0
            
        years_available = year - self.constraints.start_year + 1
        ramp_limited = baseline_capacity * self.constraints.ramp_rate_per_year * years_available
        technical_limited = baseline_capacity * self.constraints.max_applicability
        
        return min(ramp_limited, technical_limited)
    
    def __repr__(self) -> str:
        return f"Technology({self.tech_id}, {self.process_type}, LCOA=${self.calculate_lcoa():.1f}/tCO2)"


