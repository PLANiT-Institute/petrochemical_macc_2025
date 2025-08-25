from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum
import numpy as np

class TechBand(Enum):
    HT = "HT"  # High Temperature
    MT = "MT"  # Medium Temperature  
    LT = "LT"  # Low Temperature

class TechType(Enum):
    TRANSITION = "transition"    # Band-to-band improvements
    ALTERNATIVE = "alternative"  # New breakthrough technologies

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
        tech_type: TechType,
        cost_structure: CostStructure,
        constraints: TechnologyConstraints,
        emission_factor: float,  # tCO2/t product
        abatement_potential: float = 0.0,  # tCO2/t reduction vs baseline
        from_band: Optional[TechBand] = None,
        to_band: Optional[TechBand] = None
    ):
        self.tech_id = tech_id
        self.name = name
        self.process_type = process_type
        self.tech_type = tech_type
        self.cost_structure = cost_structure
        self.constraints = constraints
        self.emission_factor = emission_factor
        self.abatement_potential = abatement_potential
        self.from_band = from_band
        self.to_band = to_band
        
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
    
    def is_applicable_to_band(self, current_band: TechBand) -> bool:
        """Check if technology can be applied to current technology band"""
        if self.tech_type == TechType.TRANSITION:
            return self.from_band == current_band
        else:  # ALTERNATIVE
            return True  # Alternative techs can replace any band
            
    def __repr__(self) -> str:
        band_info = f"{self.from_band.value}→{self.to_band.value}" if self.from_band and self.to_band else "N/A"
        return f"Technology({self.tech_id}, {self.process_type}, {band_info}, LCOA=${self.calculate_lcoa():.1f}/tCO2)"

class TechnologyTransition(Technology):
    """Technology representing efficiency improvement between bands"""
    
    def __init__(self, tech_id: str, process_type: str, from_band: TechBand, to_band: TechBand,
                 abatement_per_t: float, cost_structure: CostStructure, constraints: TechnologyConstraints):
        
        name = f"{process_type}_{from_band.value}_to_{to_band.value}"
        super().__init__(
            tech_id=tech_id,
            name=name,
            process_type=process_type,
            tech_type=TechType.TRANSITION,
            cost_structure=cost_structure,
            constraints=constraints,
            emission_factor=0.0,  # Will be calculated relative to baseline
            abatement_potential=abatement_per_t,
            from_band=from_band,
            to_band=to_band
        )

class AlternativeTechnology(Technology):
    """Breakthrough technology that can replace existing processes"""
    
    def __init__(self, tech_id: str, name: str, process_type: str, emission_factor: float,
                 cost_structure: CostStructure, constraints: TechnologyConstraints, 
                 baseline_displacement: List[str] = None):
        
        # Calculate abatement potential vs displaced baseline
        baseline_ef = 1.0  # Will be set based on baseline displacement
        abatement_potential = max(0, baseline_ef - emission_factor)
        
        super().__init__(
            tech_id=tech_id,
            name=name,
            process_type=process_type,
            tech_type=TechType.ALTERNATIVE,
            cost_structure=cost_structure,
            constraints=constraints,
            emission_factor=emission_factor,
            abatement_potential=abatement_potential
        )
        
        self.baseline_displacement = baseline_displacement or []