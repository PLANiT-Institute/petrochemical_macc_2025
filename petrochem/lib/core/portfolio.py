from typing import Dict, List, Optional, Tuple
from .technology import Technology, TechBand, TechType, TechnologyTransition, AlternativeTechnology
from .scenario import EmissionsScenario
import pandas as pd

class TechnologyPortfolio:
    """Manages collection of technologies and their interactions"""
    
    def __init__(self):
        self.technologies: Dict[str, Technology] = {}
        self.transitions: Dict[str, TechnologyTransition] = {}
        self.alternatives: Dict[str, AlternativeTechnology] = {}
        
    def add_technology(self, tech: Technology):
        """Add a technology to the portfolio"""
        self.technologies[tech.tech_id] = tech
        
        if isinstance(tech, TechnologyTransition):
            self.transitions[tech.tech_id] = tech
        elif isinstance(tech, AlternativeTechnology):
            self.alternatives[tech.tech_id] = tech
    
    def get_technologies_for_process(self, process_type: str) -> List[Technology]:
        """Get all technologies applicable to a process"""
        return [tech for tech in self.technologies.values() 
                if tech.process_type == process_type or tech.process_type == "All"]
    
    def get_transitions_from_band(self, process_type: str, from_band: TechBand) -> List[TechnologyTransition]:
        """Get all possible transitions from a technology band"""
        return [trans for trans in self.transitions.values()
                if trans.process_type == process_type and trans.from_band == from_band]
    
    def get_alternatives_for_process(self, process_type: str) -> List[AlternativeTechnology]:
        """Get alternative technologies for a process"""
        return [alt for alt in self.alternatives.values()
                if alt.process_type == process_type or alt.process_type == "All"]
    
    def calculate_total_abatement_potential(self, scenario: EmissionsScenario) -> float:
        """Calculate maximum theoretical abatement potential (MtCO2)"""
        total_potential = 0.0
        
        for process_type, baseline in scenario.baseline.process_baselines.items():
            process_potential = 0.0
            
            # Calculate transition potential
            for band, capacity_share in baseline.current_band_distribution.items():
                capacity_kt = baseline.production_kt * capacity_share
                
                # Find best transition path from this band
                try:
                    current_band = TechBand(band.split('_')[-1])  # Extract band from tech name
                    transitions = self.get_transitions_from_band(process_type, current_band)
                    
                    if transitions:
                        # Take maximum abatement transition
                        best_transition = max(transitions, key=lambda t: t.abatement_potential)
                        transition_potential = (capacity_kt * best_transition.abatement_potential * 
                                              best_transition.constraints.max_applicability / 1000)
                        process_potential += transition_potential
                        
                except ValueError:
                    # Band extraction failed, skip
                    continue
            
            # Add alternative technology potential
            alternatives = self.get_alternatives_for_process(process_type)
            for alt in alternatives:
                alt_capacity = baseline.production_kt * alt.constraints.max_applicability
                alt_potential = alt_capacity * alt.abatement_potential / 1000  # Convert to Mt
                process_potential += alt_potential
            
            total_potential += process_potential
            
        return total_potential
    
    def generate_macc_curve(self, scenario: EmissionsScenario, year: int) -> pd.DataFrame:
        """Generate marginal abatement cost curve for given year"""
        macc_data = []
        
        for tech in self.technologies.values():
            if year < tech.constraints.start_year:
                continue
                
            # Calculate abatement potential for this technology in this year
            if tech.tech_type == TechType.TRANSITION:
                # Find applicable baseline capacity
                baseline_capacity = 0.0
                if tech.from_band and tech.process_type in scenario.baseline.process_baselines:
                    band_key = f"{tech.process_type}_{tech.from_band.value}"
                    baseline_capacity = scenario.baseline.get_band_capacity(tech.process_type, band_key)
                    
            else:  # Alternative technology
                baseline_capacity = scenario.baseline.get_process_production(tech.process_type)
            
            max_deployment = tech.get_max_deployment(year, baseline_capacity)
            abatement_potential = max_deployment * tech.abatement_potential / 1000  # MtCO2
            
            if abatement_potential > 0:
                macc_data.append({
                    'TechID': tech.tech_id,
                    'ProcessType': tech.process_type,
                    'TechType': tech.tech_type.value,
                    'LCOA_USD_per_tCO2': tech.calculate_lcoa(),
                    'AbatementPotential_MtCO2': abatement_potential,
                    'MaxDeployment_kt': max_deployment,
                    'Year': year
                })
        
        df = pd.DataFrame(macc_data)
        if not df.empty:
            df = df.sort_values('LCOA_USD_per_tCO2')
            df['CumulativeAbatement_MtCO2'] = df['AbatementPotential_MtCO2'].cumsum()
            
        return df
    
    def get_cost_effective_technologies(self, max_cost_per_tco2: float) -> List[Technology]:
        """Get technologies below a cost threshold"""
        return [tech for tech in self.technologies.values() 
                if tech.calculate_lcoa() <= max_cost_per_tco2]
    
    def get_portfolio_summary(self) -> Dict[str, any]:
        """Get summary statistics of the portfolio"""
        total_techs = len(self.technologies)
        transitions = len(self.transitions)
        alternatives = len(self.alternatives)
        
        processes = set(tech.process_type for tech in self.technologies.values())
        
        lcoa_values = [tech.calculate_lcoa() for tech in self.technologies.values() 
                      if tech.calculate_lcoa() < float('inf')]
        
        return {
            'total_technologies': total_techs,
            'transitions': transitions,
            'alternatives': alternatives,
            'processes_covered': len(processes),
            'process_types': list(processes),
            'avg_lcoa_usd_per_tco2': sum(lcoa_values) / len(lcoa_values) if lcoa_values else 0,
            'min_lcoa_usd_per_tco2': min(lcoa_values) if lcoa_values else 0,
            'max_lcoa_usd_per_tco2': max(lcoa_values) if lcoa_values else 0
        }
    
    def __len__(self) -> int:
        return len(self.technologies)
    
    def __repr__(self) -> str:
        summary = self.get_portfolio_summary()
        return (f"TechnologyPortfolio("
                f"techs={summary['total_technologies']}, "
                f"processes={summary['processes_covered']}, "
                f"avg_lcoa=${summary['avg_lcoa_usd_per_tco2']:.1f}/tCO2)")