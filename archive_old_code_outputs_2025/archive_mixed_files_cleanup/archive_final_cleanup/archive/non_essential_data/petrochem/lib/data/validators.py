from typing import Dict, Any, List
import pandas as pd
import numpy as np

from ..core.technology import Technology
from ..core.scenario import EmissionsScenario
from ..core.portfolio import TechnologyPortfolio
from .schemas import DataValidationResult, DataSchema, validate_dataframe

class DataValidator:
    """Comprehensive data validation for MACC model components"""
    
    @staticmethod
    def validate_excel_data(excel_data: Dict[str, pd.DataFrame]) -> DataValidationResult:
        """Validate all sheets in the MACC database Excel file"""
        overall_result = DataValidationResult(valid=True, errors=[], warnings=[])
        
        # Define validation schemas for each sheet
        sheet_schemas = {
            'TransitionPotentials': DataSchema.TRANSITION_POTENTIALS_SCHEMA,
            'AbatementPotentials': DataSchema.ABATEMENT_POTENTIALS_SCHEMA,
            'AlternativeTechnologies': DataSchema.ALTERNATIVE_TECHNOLOGIES_SCHEMA,
        }
        
        # Validate each sheet with its schema
        for sheet_name, schema in sheet_schemas.items():
            if sheet_name in excel_data:
                result = validate_dataframe(excel_data[sheet_name], schema, sheet_name)
                overall_result.errors.extend(result.errors)
                overall_result.warnings.extend(result.warnings)
                if not result.valid:
                    overall_result.valid = False
            else:
                overall_result.add_warning(f"Sheet '{sheet_name}' not found in Excel file")
        
        # Cross-sheet validation
        cross_validation = DataValidator._validate_cross_references(excel_data)
        overall_result.errors.extend(cross_validation.errors)
        overall_result.warnings.extend(cross_validation.warnings)
        if not cross_validation.valid:
            overall_result.valid = False
            
        return overall_result
    
    @staticmethod
    def _validate_cross_references(excel_data: Dict[str, pd.DataFrame]) -> DataValidationResult:
        """Validate references between sheets"""
        result = DataValidationResult(valid=True, errors=[], warnings=[])
        
        # Check TransitionID consistency
        if 'TransitionPotentials' in excel_data and 'AbatementPotentials' in excel_data:
            transition_ids = set(excel_data['TransitionPotentials']['TransitionID'])
            abatement_ids = set(excel_data['AbatementPotentials']['TransitionID'])
            
            missing_abatement = transition_ids - abatement_ids
            if missing_abatement:
                result.add_error(f"Transitions missing abatement data: {missing_abatement}")
            
            extra_abatement = abatement_ids - transition_ids
            if extra_abatement:
                result.add_warning(f"Abatement data without transitions: {extra_abatement}")
        
        # Check TechID consistency for alternatives
        if 'AlternativeTechnologies' in excel_data and 'AlternativeCosts' in excel_data:
            alt_tech_ids = set(excel_data['AlternativeTechnologies']['TechID'])
            alt_cost_ids = set(excel_data['AlternativeCosts']['TechID'])
            
            missing_costs = alt_tech_ids - alt_cost_ids
            if missing_costs:
                result.add_error(f"Alternative technologies missing cost data: {missing_costs}")
                
            extra_costs = alt_cost_ids - alt_tech_ids
            if extra_costs:
                result.add_warning(f"Cost data without technology definitions: {extra_costs}")
        
        return result
    
    @staticmethod
    def validate_scenario(scenario: EmissionsScenario) -> DataValidationResult:
        """Validate emissions scenario for consistency"""
        result = DataValidationResult(valid=True, errors=[], warnings=[])
        
        # Check baseline year is in timeline
        if scenario.baseline.year not in scenario.timeline:
            result.add_warning(f"Baseline year {scenario.baseline.year} not in timeline")
        
        # Check targets are generally decreasing (allowing for some flexibility)
        target_years = sorted(scenario.targets.keys())
        target_values = [scenario.get_target_emissions(year) for year in target_years]
        
        # Allow small increases but flag large ones
        for i in range(len(target_values) - 1):
            if target_values[i+1] > target_values[i] * 1.1:  # More than 10% increase
                result.add_warning(f"Significant emissions increase from {target_years[i]} to {target_years[i+1]}")
        
        # Check process baseline consistency
        total_process_emissions = sum(pb.total_emissions_mt for pb in scenario.baseline.process_baselines.values())
        baseline_diff = abs(total_process_emissions - scenario.baseline.total_emissions_mt)
        
        if baseline_diff > 0.1:  # Allow small rounding differences
            result.add_error(
                f"Process emissions sum ({total_process_emissions:.2f} Mt) doesn't match "
                f"total baseline ({scenario.baseline.total_emissions_mt:.2f} Mt). "
                f"Difference: {baseline_diff:.2f} Mt"
            )
        
        # Check for reasonable emission intensities
        for process_name, baseline in scenario.baseline.process_baselines.items():
            if baseline.emission_intensity_t_co2_per_t < 0:
                result.add_error(f"Negative emission intensity for {process_name}")
            elif baseline.emission_intensity_t_co2_per_t > 5.0:  # Very high intensity
                result.add_warning(f"Very high emission intensity for {process_name}: {baseline.emission_intensity_t_co2_per_t:.2f} tCO2/t")
        
        return result
    
    @staticmethod
    def validate_portfolio(portfolio: TechnologyPortfolio) -> DataValidationResult:
        """Validate technology portfolio"""
        result = DataValidationResult(valid=True, errors=[], warnings=[])
        
        # Check for duplicate IDs
        tech_ids = [tech.tech_id for tech in portfolio.technologies.values()]
        if len(tech_ids) != len(set(tech_ids)):
            duplicates = [id for id in tech_ids if tech_ids.count(id) > 1]
            result.add_error(f"Duplicate technology IDs found: {set(duplicates)}")
        
        # Validate individual technologies
        invalid_costs = []
        negative_abatement = []
        unrealistic_costs = []
        
        for tech in portfolio.technologies.values():
            # Check LCOA calculation
            lcoa = tech.calculate_lcoa()
            if lcoa < 0:
                invalid_costs.append(tech.tech_id)
            elif lcoa > 50000:  # Very expensive (>$50k/tCO2)
                unrealistic_costs.append((tech.tech_id, lcoa))
            
            # Check abatement potential
            if tech.abatement_potential < 0:
                negative_abatement.append(tech.tech_id)
                
            # Check constraint logic
            if tech.constraints.max_applicability > 1.0:
                result.add_error(f"Technology {tech.tech_id} has max applicability > 100%")
            
            if tech.constraints.ramp_rate_per_year > 1.0:
                result.add_warning(f"Technology {tech.tech_id} has very high ramp rate: {tech.constraints.ramp_rate_per_year}")
        
        if invalid_costs:
            result.add_warning(f"Technologies with negative LCOA: {invalid_costs}")
        
        if negative_abatement:
            result.add_error(f"Technologies with negative abatement potential: {negative_abatement}")
        
        if unrealistic_costs:
            cost_info = [(tid, f"${cost:.0f}") for tid, cost in unrealistic_costs]
            result.add_warning(f"Technologies with very high costs: {cost_info}")
        
        # Check transition logic
        invalid_transitions = []
        for trans in portfolio.transitions.values():
            if trans.from_band == trans.to_band:
                invalid_transitions.append(trans.tech_id)
        
        if invalid_transitions:
            result.add_error(f"Invalid transitions (same from/to band): {invalid_transitions}")
        
        return result
    
    @staticmethod
    def validate_model_inputs(scenario: EmissionsScenario, portfolio: TechnologyPortfolio) -> DataValidationResult:
        """Validate complete model inputs for optimization"""
        result = DataValidationResult(valid=True, errors=[], warnings=[])
        
        # Validate individual components
        scenario_result = DataValidator.validate_scenario(scenario)
        portfolio_result = DataValidator.validate_portfolio(portfolio)
        
        # Combine results
        result.errors.extend(scenario_result.errors + portfolio_result.errors)
        result.warnings.extend(scenario_result.warnings + portfolio_result.warnings)
        if not scenario_result.valid or not portfolio_result.valid:
            result.valid = False
        
        # Check feasibility
        total_abatement_potential = portfolio.calculate_total_abatement_potential(scenario)
        max_required = max(scenario.get_required_abatement(year) for year in scenario.timeline)
        
        if max_required > total_abatement_potential:
            result.add_error(
                f"Scenario infeasible: Maximum required abatement ({max_required:.1f} Mt) "
                f"exceeds total portfolio potential ({total_abatement_potential:.1f} Mt)"
            )
        elif max_required > total_abatement_potential * 0.8:
            result.add_warning(
                f"Scenario may be challenging: Required abatement is {max_required/total_abatement_potential*100:.1f}% "
                f"of total potential"
            )
        
        # Check process coverage
        scenario_processes = set(scenario.baseline.process_baselines.keys())
        portfolio_processes = set(tech.process_type for tech in portfolio.technologies.values())
        portfolio_processes.discard('All')  # Remove generic 'All' process
        
        uncovered_processes = scenario_processes - portfolio_processes
        if uncovered_processes:
            result.add_warning(f"Processes without abatement technologies: {uncovered_processes}")
        
        return result