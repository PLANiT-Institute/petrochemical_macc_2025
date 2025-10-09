import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..core.technology import (
    Technology, CostStructure, TechnologyConstraints
)
from ..core.scenario import EmissionsScenario, EmissionsBaseline, EmissionsTarget, ProcessBaseline
from ..core.portfolio import TechnologyPortfolio

class DataValidator:
    """Validates loaded data for consistency and completeness"""
    
    @staticmethod  
    def validate_portfolio(portfolio: 'TechnologyPortfolio') -> Dict[str, Any]:
        """Validate technology portfolio"""
        results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check for duplicate IDs
        tech_ids = [tech.tech_id for tech in portfolio.technologies.values()]
        if len(tech_ids) != len(set(tech_ids)):
            results['errors'].append("Duplicate technology IDs found")
            results['valid'] = False
        
        # Check cost structure validity
        invalid_costs = []
        for tech in portfolio.technologies.values():
            if tech.calculate_lcoa() < 0:
                invalid_costs.append(tech.tech_id)
        
        if invalid_costs:
            results['warnings'].append(f"Technologies with negative LCOA: {invalid_costs}")
        
        return results

class DataLoader:
    """Main class for loading and parsing Excel data files"""
    
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            # Default to data directory relative to project root
            self.data_dir = Path(__file__).parent.parent.parent.parent / 'data'
    
    def load_baseline_data(self, filename: str = "Korea Petrochemical Carbon Neutrality Dataset 2023.xlsx") -> EmissionsBaseline:
        """Load baseline emissions and production data"""
        filepath = self.data_dir / filename
        
        # Read Excel file
        with pd.ExcelFile(filepath) as xls:
            production_df = pd.read_excel(xls, sheet_name='Production_2023')
            tech_bands_df = pd.read_excel(xls, sheet_name='TechBands')
            
        # Process baseline data
        process_baselines = []
        
        # Group by process type
        for process_type, group in production_df.groupby('ProcessType'):
            total_production = group['Production_kt'].sum()
            weighted_emission_intensity = (
                (group['Production_kt'] * group['EmissionIntensity_tCO2_per_t']).sum() / 
                total_production
            )
            
            # Calculate band distribution
            band_dist = {}
            for _, row in group.iterrows():
                tech_key = row['TechKey']
                share = row['Production_kt'] / total_production
                band_dist[tech_key] = share
            
            process_baseline = ProcessBaseline(
                process_type=process_type,
                production_kt=total_production,
                emission_intensity_t_co2_per_t=weighted_emission_intensity,
                current_band_distribution=band_dist
            )
            process_baselines.append(process_baseline)
        
        total_emissions = sum(pb.total_emissions_mt for pb in process_baselines)
        
        return EmissionsBaseline(
            year=2023,
            total_emissions_mt=total_emissions,
            process_baselines=process_baselines
        )
    
    
    def load_alternative_technologies(self, filename: str = "Korea_Petrochemical_MACC_Database.xlsx") -> List[Technology]:
        """Load alternative technology data"""
        filepath = self.data_dir / filename
        
        with pd.ExcelFile(filepath) as xls:
            emerging_df = pd.read_excel(xls, sheet_name='AlternativeTechnologies')
            costs_df = pd.read_excel(xls, sheet_name='AlternativeCosts')
        
        # Merge dataframes
        merged_df = emerging_df.merge(costs_df, on='TechID')
        
        technologies = []
        for _, row in merged_df.iterrows():
            cost_structure = CostStructure(
                capex_usd_per_kt=row['CAPEX_Million_USD_per_kt'] * 1e6,  # Convert to USD
                opex_delta_usd_per_t=row['OPEX_USD_per_t'],
                maintenance_pct=0.03,  # Default
                fuel_cost_usd_per_gj=row['FuelCost_USD_per_GJ']
            )
            
            constraints = TechnologyConstraints(
                lifetime_years=int(row['Lifetime_years']),
                start_year=int(row['CommercialYear']),
                ramp_rate_per_year=float(row['RampRate_per_year']),
                max_applicability=row['MaxPenetration'],
                technical_readiness_level=int(row['TRL'])
            )
            
            baseline_displacement = row['BaselineDisplacement'].split('+') if '+' in str(row['BaselineDisplacement']) else [row['BaselineDisplacement']]
            
            tech = Technology(
                tech_id=row['TechID'],
                name=row['TechName'],
                process_type=row['ProcessType'],
                cost_structure=cost_structure,
                constraints=constraints,
                emission_factor=row['EmissionFactor_tCO2_per_t'],
                abatement_potential=row.get('EmissionReduction_tCO2_per_t', 0.0),
                baseline_displacement=baseline_displacement
            )
            
            technologies.append(tech)
        
        return technologies
    
    def load_technology_portfolio(self) -> TechnologyPortfolio:
        """Load complete technology portfolio"""
        portfolio = TechnologyPortfolio()
        
        # Load only alternative technologies
        alternatives = self.load_alternative_technologies()
        for tech in alternatives:
            portfolio.add_technology(tech)
        
        return portfolio
    
    def load_emissions_scenario(self, target_file: Optional[str] = None) -> EmissionsScenario:
        """Load emissions scenario with baseline and targets"""
        baseline = self.load_baseline_data()
        
        # Load targets (if specific file provided, otherwise use defaults)
        if target_file:
            # Custom targets from file
            targets_df = pd.read_excel(self.data_dir / target_file)
            targets = [
                EmissionsTarget(year=int(row['Year']), target_mt_co2=float(row['Target_MtCO2e']))
                for _, row in targets_df.iterrows()
            ]
        else:
            # Default Korean petrochemical targets
            targets = [
                EmissionsTarget(year=2023, target_mt_co2=50.0),
                EmissionsTarget(year=2030, target_mt_co2=40.0),
                EmissionsTarget(year=2040, target_mt_co2=25.0),
                EmissionsTarget(year=2050, target_mt_co2=10.0)
            ]
        
        timeline = list(range(2023, 2051))  # Annual resolution
        
        return EmissionsScenario(baseline=baseline, targets=targets, timeline=timeline)
    
    def load_constraints(self, filename: str = "Korea_Petrochemical_MACC_Database.xlsx") -> Dict[str, pd.DataFrame]:
        """Load implementation constraints"""
        filepath = self.data_dir / filename
        constraints = {}
        
        with pd.ExcelFile(filepath) as xls:
            for sheet_name in xls.sheet_names:
                constraints[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
        
        return constraints