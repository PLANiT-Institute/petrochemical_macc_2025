from typing import Dict, List, Optional, Tuple
import pandas as pd
from pyomo.environ import ConcreteModel, value
import numpy as np

from ..core.technology import Technology
from ..core.scenario import EmissionsScenario
from ..core.portfolio import TechnologyPortfolio

class ModelResults:
    """Extract and process results from solved optimization model"""
    
    def __init__(self, 
                 model: ConcreteModel, 
                 portfolio: TechnologyPortfolio, 
                 scenario: EmissionsScenario,
                 solver_status: str = "unknown"):
        self.model = model
        self.portfolio = portfolio
        self.scenario = scenario
        self.solver_status = solver_status
        
    def extract_deployment_plan(self) -> pd.DataFrame:
        """Extract technology deployment by year"""
        deployment_data = []
        
        for tech_id in self.model.TECHS:
            tech = self.portfolio.technologies[tech_id]
            
            for year in self.model.YEARS:
                deployment_kt = value(self.model.deployment[tech_id, year])
                abatement_t = value(self.model.abate_achieved[tech_id, year])
                
                if deployment_kt > 0.001:  # Only include meaningful deployments
                    deployment_data.append({
                        'TechID': tech_id,
                        'TechName': getattr(tech, 'name', tech_id),
                        'ProcessType': tech.process_type,
                        'TechType': tech.tech_type.value,
                        'Year': year,
                        'Deployment_kt': deployment_kt,
                        'Abatement_tCO2': abatement_t,
                        'CAPEX_Million_USD': deployment_kt * value(self.model.capex[tech_id, year]),
                        'OPEX_USD_per_year': deployment_kt * value(self.model.opex[tech_id, year]) * 1000,
                        'LCOA_USD_per_tCO2': tech.calculate_lcoa()
                    })
        
        return pd.DataFrame(deployment_data)
    
    def extract_annual_summary(self) -> pd.DataFrame:
        """Extract annual summary of emissions, costs, and abatement"""
        summary_data = []
        
        for year in self.model.YEARS:
            # Calculate totals for this year
            total_deployment = sum(value(self.model.deployment[tech, year]) 
                                 for tech in self.model.TECHS)
            
            total_abatement = sum(value(self.model.abate_achieved[tech, year]) 
                                for tech in self.model.TECHS) / 1e6  # Convert to Mt
            
            total_capex = sum(value(self.model.deployment[tech, year]) * 
                            value(self.model.capex[tech, year])
                            for tech in self.model.TECHS)
            
            total_opex = sum(value(self.model.deployment[tech, year]) * 
                           value(self.model.opex[tech, year]) * 1000
                           for tech in self.model.TECHS)
            
            # Shortfall if it exists
            shortfall = (value(self.model.shortfall[year]) / 1e6 
                        if hasattr(self.model, 'shortfall') else 0.0)
            
            # Emissions after abatement
            baseline_emissions = self.scenario.baseline.total_emissions_mt
            remaining_emissions = baseline_emissions - total_abatement + shortfall
            target_emissions = self.scenario.get_target_emissions(year)
            
            summary_data.append({
                'Year': year,
                'Target_MtCO2': target_emissions,
                'Required_Abatement_MtCO2': self.scenario.get_required_abatement(year),
                'Achieved_Abatement_MtCO2': total_abatement,
                'Shortfall_MtCO2': shortfall,
                'Remaining_Emissions_MtCO2': remaining_emissions,
                'Total_Deployment_kt': total_deployment,
                'Annual_CAPEX_Million_USD': total_capex,
                'Annual_OPEX_Million_USD': total_opex / 1e6,
                'Target_Met': shortfall < 0.01
            })
        
        return pd.DataFrame(summary_data)
    
    def calculate_system_cost(self, discount_rate: float = 0.05) -> Dict[str, float]:
        """Calculate total system cost metrics"""
        
        base_year = min(self.model.YEARS)
        total_npv_cost = 0.0
        annual_costs = {}
        
        for year in self.model.YEARS:
            discount_factor = 1.0 / ((1.0 + discount_rate) ** (year - base_year))
            
            annual_capex = sum(value(self.model.deployment[tech, year]) * 
                             value(self.model.capex[tech, year])
                             for tech in self.model.TECHS)
            
            annual_opex = sum(value(self.model.deployment[tech, year]) * 
                            value(self.model.opex[tech, year]) * 1000
                            for tech in self.model.TECHS)
            
            annual_cost = annual_capex + annual_opex
            annual_costs[year] = annual_cost
            total_npv_cost += annual_cost * discount_factor
        
        # Calculate cost per tonne of abatement
        total_abatement = sum(
            sum(value(self.model.abate_achieved[tech, year]) for tech in self.model.TECHS)
            for year in self.model.YEARS
        )
        
        cost_per_tco2 = total_npv_cost / total_abatement if total_abatement > 0 else float('inf')
        
        return {
            'total_npv_cost_million_usd': total_npv_cost / 1e6,
            'total_abatement_tco2': total_abatement,
            'average_cost_per_tco2_usd': cost_per_tco2,
            'annual_costs': annual_costs
        }
    
    def generate_macc_curve(self, year: int) -> pd.DataFrame:
        """Generate marginal abatement cost curve for specific year"""
        
        if year not in self.model.YEARS:
            raise ValueError(f"Year {year} not in model timeline")
        
        macc_data = []
        
        for tech_id in self.model.TECHS:
            deployment = value(self.model.deployment[tech_id, year])
            
            if deployment > 0.001:  # Only include deployed technologies
                tech = self.portfolio.technologies[tech_id]
                abatement = value(self.model.abate_achieved[tech_id, year]) / 1e6  # Convert to Mt
                
                macc_data.append({
                    'TechID': tech_id,
                    'ProcessType': tech.process_type,
                    'Deployment_kt': deployment,
                    'Abatement_MtCO2': abatement,
                    'LCOA_USD_per_tCO2': tech.calculate_lcoa(),
                    'Cumulative_Deployment_kt': 0.0,  # Will be calculated
                    'Cumulative_Abatement_MtCO2': 0.0,  # Will be calculated
                    'Year': year
                })
        
        if not macc_data:
            return pd.DataFrame()
            
        df = pd.DataFrame(macc_data).sort_values('LCOA_USD_per_tCO2')
        
        # Calculate cumulative values
        df['Cumulative_Deployment_kt'] = df['Deployment_kt'].cumsum()
        df['Cumulative_Abatement_MtCO2'] = df['Abatement_MtCO2'].cumsum()
        
        return df
    
    def get_technology_utilization(self) -> pd.DataFrame:
        """Get utilization rates for each technology"""
        utilization_data = []
        
        for tech_id in self.model.TECHS:
            tech = self.portfolio.technologies[tech_id]
            
            for year in self.model.YEARS:
                deployment = value(self.model.deployment[tech_id, year])
                max_activity = value(self.model.activity[tech_id, year])
                
                utilization_rate = deployment / max_activity if max_activity > 0 else 0.0
                
                utilization_data.append({
                    'TechID': tech_id,
                    'ProcessType': tech.process_type,
                    'Year': year,
                    'Deployment_kt': deployment,
                    'Max_Potential_kt': max_activity,
                    'Utilization_Rate': utilization_rate,
                    'Available': year >= tech.constraints.start_year
                })
        
        return pd.DataFrame(utilization_data)
    
    def get_process_breakdown(self) -> pd.DataFrame:
        """Get abatement breakdown by process type"""
        process_data = []
        
        for year in self.model.YEARS:
            process_abatement = {}
            
            for tech_id in self.model.TECHS:
                tech = self.portfolio.technologies[tech_id]
                abatement = value(self.model.abate_achieved[tech_id, year]) / 1e6  # Convert to Mt
                
                if tech.process_type not in process_abatement:
                    process_abatement[tech.process_type] = 0.0
                process_abatement[tech.process_type] += abatement
            
            for process_type, abatement in process_abatement.items():
                if abatement > 0.001:  # Only include meaningful contributions
                    baseline_emissions = 0.0
                    if process_type in self.scenario.baseline.process_baselines:
                        baseline_emissions = self.scenario.baseline.process_baselines[process_type].total_emissions_mt
                    
                    process_data.append({
                        'ProcessType': process_type,
                        'Year': year,
                        'Abatement_MtCO2': abatement,
                        'Baseline_Emissions_MtCO2': baseline_emissions,
                        'Abatement_Rate': abatement / baseline_emissions if baseline_emissions > 0 else 0.0
                    })
        
        return pd.DataFrame(process_data)
    
    def get_emissions_pathway(self) -> pd.DataFrame:
        """Get emissions pathway from baseline to 2050"""
        pathway_data = []
        
        for year in self.model.YEARS:
            # Calculate total abatement achieved
            total_abatement = sum(value(self.model.abate_achieved[tech, year]) 
                                for tech in self.model.TECHS) / 1e6  # Convert to Mt
            
            # Calculate shortfall
            shortfall = (value(self.model.shortfall[year]) / 1e6 
                        if hasattr(self.model, 'shortfall') else 0.0)
            
            # Calculate actual emissions
            baseline_emissions = self.scenario.baseline.total_emissions_mt
            actual_emissions = baseline_emissions - total_abatement + shortfall
            target_emissions = self.scenario.get_target_emissions(year)
            
            pathway_data.append({
                'Year': year,
                'Baseline_Emissions_MtCO2': baseline_emissions,
                'Target_Emissions_MtCO2': target_emissions,
                'Actual_Emissions_MtCO2': actual_emissions,
                'Total_Abatement_MtCO2': total_abatement,
                'Shortfall_MtCO2': shortfall,
                'Reduction_from_Baseline_Pct': (1 - actual_emissions/baseline_emissions) * 100,
                'Target_Achievement_Pct': min(100, (total_abatement / self.scenario.get_required_abatement(year)) * 100) if self.scenario.get_required_abatement(year) > 0 else 100
            })
        
        return pd.DataFrame(pathway_data)
    
    def get_production_shares(self) -> pd.DataFrame:
        """Get technology production shares evolution by process"""
        share_data = []
        
        for year in self.model.YEARS:
            for process_type in self.scenario.baseline.process_baselines:
                baseline = self.scenario.baseline.process_baselines[process_type]
                total_production = baseline.production_kt
                
                # Calculate shares for each technology band/type in this process
                process_shares = {}
                
                # Start with baseline bands (assuming all unchanged capacity stays in original bands)
                for band_key, baseline_share in baseline.current_band_distribution.items():
                    process_shares[band_key] = baseline_share * total_production
                
                # Subtract capacity moved by transitions and add to target bands
                for tech_id in self.model.TECHS:
                    tech = self.portfolio.technologies[tech_id]
                    deployment = value(self.model.deployment[tech_id, year])
                    
                    if tech.process_type == process_type and deployment > 0.001:
                        if tech.tech_type.value == 'transition':
                            # Remove from source band
                            from_key = f"{process_type}_{tech.from_band.value}"
                            if from_key in process_shares:
                                process_shares[from_key] -= deployment
                                process_shares[from_key] = max(0, process_shares[from_key])
                            
                            # Add to target band
                            to_key = f"{process_type}_{tech.to_band.value}"
                            if to_key not in process_shares:
                                process_shares[to_key] = 0
                            process_shares[to_key] += deployment
                            
                        elif tech.tech_type.value == 'alternative':
                            # Alternative technologies get their own category
                            alt_key = f"{process_type}_{tech.tech_id}"
                            if alt_key not in process_shares:
                                process_shares[alt_key] = 0
                            process_shares[alt_key] += deployment
                
                # Convert to shares (percentage of total production)
                for tech_key, capacity in process_shares.items():
                    if capacity > 0.001:  # Only include meaningful shares
                        share_pct = (capacity / total_production) * 100
                        share_data.append({
                            'Year': year,
                            'ProcessType': process_type,
                            'TechnologyBand': tech_key,
                            'Production_Capacity_kt': capacity,
                            'Production_Share_Pct': share_pct,
                            'Total_Process_Production_kt': total_production
                        })
        
        return pd.DataFrame(share_data)
    
    def validate_solution(self) -> Dict[str, any]:
        """Validate the solution for consistency"""
        validation = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'solver_status': self.solver_status
        }
        
        # Check if targets are met
        for year in self.model.YEARS:
            required = self.scenario.get_required_abatement(year) * 1e6  # Convert to tonnes
            achieved = sum(value(self.model.abate_achieved[tech, year]) for tech in self.model.TECHS)
            shortfall = value(self.model.shortfall[year]) if hasattr(self.model, 'shortfall') else 0.0
            
            if achieved + shortfall < required * 0.999:  # Allow small numerical tolerance
                validation['errors'].append(f"Target not met in {year}: required {required/1e6:.2f}Mt, achieved {achieved/1e6:.2f}Mt")
                validation['valid'] = False
        
        # Check for unrealistic deployments
        for tech_id in self.model.TECHS:
            tech = self.portfolio.technologies[tech_id]
            for year in self.model.YEARS:
                deployment = value(self.model.deployment[tech_id, year])
                max_activity = value(self.model.activity[tech_id, year])
                
                if deployment > max_activity * 1.001:  # Small tolerance
                    validation['warnings'].append(f"Deployment exceeds capacity for {tech_id} in {year}")
        
        return validation