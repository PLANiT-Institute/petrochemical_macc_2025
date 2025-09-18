from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

@dataclass
class EmissionsTarget:
    year: int
    target_mt_co2: float
    
@dataclass
class ProcessBaseline:
    process_type: str
    production_kt: float
    emission_intensity_t_co2_per_t: float
    current_band_distribution: Dict[str, float]  # band -> share
    
    @property
    def total_emissions_mt(self) -> float:
        return self.production_kt * self.emission_intensity_t_co2_per_t / 1000

class EmissionsBaseline:
    def __init__(self, year: int, total_emissions_mt: float, process_baselines: List[ProcessBaseline]):
        self.year = year
        self.total_emissions_mt = total_emissions_mt
        self.process_baselines = {pb.process_type: pb for pb in process_baselines}
        
    def get_process_emissions(self, process_type: str) -> float:
        """Get emissions for specific process (MtCO2)"""
        if process_type in self.process_baselines:
            return self.process_baselines[process_type].total_emissions_mt
        return 0.0
    
    def get_process_production(self, process_type: str) -> float:
        """Get production volume for specific process (kt)"""
        if process_type in self.process_baselines:
            return self.process_baselines[process_type].production_kt
        return 0.0
        
    def get_band_capacity(self, process_type: str, band: str) -> float:
        """Get current capacity in specific technology band (kt)"""
        if process_type not in self.process_baselines:
            return 0.0
            
        process = self.process_baselines[process_type]
        band_share = process.current_band_distribution.get(band, 0.0)
        return process.production_kt * band_share

class EmissionsScenario:
    def __init__(self, 
                 baseline: EmissionsBaseline,
                 targets: List[EmissionsTarget],
                 timeline: List[int]):
        
        self.baseline = baseline
        self.targets = {t.year: t.target_mt_co2 for t in targets}
        self.timeline = sorted(timeline)
        
        # Interpolate targets for all years
        self._interpolate_targets()
    
    def _interpolate_targets(self):
        """Interpolate targets for years not explicitly defined"""
        target_years = sorted(self.targets.keys())
        
        for year in self.timeline:
            if year in self.targets:
                continue
                
            # Linear interpolation
            if year < target_years[0]:
                self.targets[year] = self.baseline.total_emissions_mt
            elif year > target_years[-1]:
                self.targets[year] = self.targets[target_years[-1]]
            else:
                # Find surrounding years
                lower_year = max([y for y in target_years if y <= year])
                upper_year = min([y for y in target_years if y >= year])
                
                if lower_year == upper_year:
                    self.targets[year] = self.targets[lower_year]
                else:
                    # Linear interpolation
                    t = (year - lower_year) / (upper_year - lower_year)
                    self.targets[year] = (
                        self.targets[lower_year] * (1 - t) + 
                        self.targets[upper_year] * t
                    )
    
    def get_target_emissions(self, year: int) -> float:
        """Get emissions target for given year (MtCO2)"""
        return self.targets.get(year, self.baseline.total_emissions_mt)
    
    def get_required_abatement(self, year: int) -> float:
        """Calculate required abatement for given year (MtCO2)"""
        target = self.get_target_emissions(year)
        return max(0.0, self.baseline.total_emissions_mt - target)
    
    def get_abatement_trajectory(self) -> Dict[int, float]:
        """Get required abatement for all years in timeline"""
        return {year: self.get_required_abatement(year) for year in self.timeline}
        
    def validate_feasibility(self, max_abatement_potential: float) -> Dict[str, any]:
        """Check if scenario targets are technically feasible"""
        results = {
            'feasible': True,
            'infeasible_years': [],
            'max_required': 0.0,
            'max_available': max_abatement_potential
        }
        
        for year in self.timeline:
            required = self.get_required_abatement(year)
            results['max_required'] = max(results['max_required'], required)
            
            if required > max_abatement_potential:
                results['feasible'] = False
                results['infeasible_years'].append(year)
                
        return results
    
    def __repr__(self) -> str:
        final_target = self.get_target_emissions(max(self.timeline))
        reduction_pct = (1 - final_target / self.baseline.total_emissions_mt) * 100
        return (f"EmissionsScenario("
                f"baseline={self.baseline.total_emissions_mt:.1f}Mt, "
                f"final_target={final_target:.1f}Mt, "
                f"reduction={reduction_pct:.1f}%)")