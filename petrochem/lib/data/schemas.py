from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from enum import Enum
import pandas as pd

class ProcessType(Enum):
    NCC = "NCC"
    BTX = "BTX" 
    PDH = "PDH"
    POLY_PE = "Poly_PE"
    POLY_PP = "Poly_PP"
    UTILITIES = "Utilities"
    ALL = "All"

@dataclass
class DataValidationResult:
    """Result of data validation"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    
    def add_error(self, message: str):
        self.errors.append(message)
        self.valid = False
    
    def add_warning(self, message: str):
        self.warnings.append(message)

class DataSchema:
    """Defines expected data schemas for validation"""
    
    TRANSITION_POTENTIALS_SCHEMA = {
        'required_columns': [
            'TechID', 'ProcessType', 'FromBand', 'ToBand', 'TransitionID',
            'MaxApplicability', 'TechnicalReadiness', 'CommercialYear'
        ],
        'data_types': {
            'TechID': str,
            'ProcessType': str,
            'FromBand': str,
            'ToBand': str,
            'TransitionID': str,
            'MaxApplicability': float,
            'TechnicalReadiness': int,
            'CommercialYear': int
        },
        'constraints': {
            'MaxApplicability': (0.0, 1.0),
            'TechnicalReadiness': (1, 9),
            'CommercialYear': (2020, 2060)
        }
    }
    
    ABATEMENT_POTENTIALS_SCHEMA = {
        'required_columns': [
            'TransitionID', 'EmissionReduction_tCO2_per_t', 'EnergyReduction_GJ_per_t',
            'PrimaryFuelShift', 'SecondaryBenefit', 'Lifetime_years', 'RampRate_per_year'
        ],
        'data_types': {
            'TransitionID': str,
            'EmissionReduction_tCO2_per_t': float,
            'EnergyReduction_GJ_per_t': float,
            'PrimaryFuelShift': str,
            'SecondaryBenefit': str,
            'Lifetime_years': int,
            'RampRate_per_year': float
        },
        'constraints': {
            'EmissionReduction_tCO2_per_t': (0.0, 10.0),
            'EnergyReduction_GJ_per_t': (0.0, 100.0),
            'Lifetime_years': (5, 50),
            'RampRate_per_year': (0.01, 1.0)
        }
    }
    
    ALTERNATIVE_TECHNOLOGIES_SCHEMA = {
        'required_columns': [
            'TechID', 'ProcessType', 'TechName', 'TechType', 'BaselineDisplacement',
            'MaxPenetration', 'TRL', 'CommercialYear', 'Lifetime_years', 'RampRate_per_year'
        ],
        'data_types': {
            'TechID': str,
            'ProcessType': str,
            'TechName': str,
            'TechType': str,
            'BaselineDisplacement': str,
            'MaxPenetration': float,
            'TRL': int,
            'CommercialYear': int,
            'Lifetime_years': int,
            'RampRate_per_year': float
        },
        'constraints': {
            'MaxPenetration': (0.0, 1.0),
            'TRL': (1, 9),
            'CommercialYear': (2020, 2060),
            'Lifetime_years': (5, 50),
            'RampRate_per_year': (0.001, 0.5)
        }
    }

def validate_dataframe(df: pd.DataFrame, schema: Dict, sheet_name: str) -> DataValidationResult:
    """Validate a dataframe against a schema"""
    result = DataValidationResult(valid=True, errors=[], warnings=[])
    
    # Check required columns
    missing_cols = set(schema['required_columns']) - set(df.columns)
    if missing_cols:
        result.add_error(f"{sheet_name}: Missing required columns: {missing_cols}")
        return result
    
    # Check data types and constraints
    for col, expected_type in schema['data_types'].items():
        if col in df.columns:
            # Check for null values in required columns
            if df[col].isnull().any():
                result.add_warning(f"{sheet_name}: Column '{col}' has null values")
            
            # Check constraints if they exist
            if col in schema.get('constraints', {}):
                min_val, max_val = schema['constraints'][col]
                if expected_type in (int, float):
                    invalid_values = df[(df[col] < min_val) | (df[col] > max_val)]
                    if not invalid_values.empty:
                        result.add_error(f"{sheet_name}: Column '{col}' has values outside range [{min_val}, {max_val}]")
    
    return result