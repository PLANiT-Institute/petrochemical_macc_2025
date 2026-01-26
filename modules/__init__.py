"""
Core modules for the Korean Petrochemical MACC Model.
=====================================================
All data comes from CSV files - no hardcoded values.
"""

__version__ = '3.0.0'
__author__ = 'PLANiT Institute'

from . import utils
from . import data_loader
from . import capex_calculator
from . import data_validator
from . import excel_reviewer

# Re-export key classes for convenience
from .data_loader import DataLoader, validate_data_integrity
from .capex_calculator import CapexCalculator, MACCalculator, select_technology_for_facility
from .utils import (
    EmissionCalculator,
    PriceCalculator,
    TechnologyCostCalculator,
    StrandedAssetCalculator,
    save_csv_output,
    save_plot,
    identify_product_group,
    is_ncc_facility,
    format_number
)
from .data_validator import (
    DataValidator,
    ValidationResult,
    ValidationError,
    Severity,
    SchemaValidator,
    ReferentialIntegrityValidator,
    BusinessRuleValidator,
    TemporalValidator,
    OutputValidator,
)
from .excel_reviewer import (
    ExcelReviewer,
    ExcelReviewerConfig,
    get_available_scenarios,
)

__all__ = [
    'utils',
    'data_loader',
    'capex_calculator',
    'data_validator',
    'excel_reviewer',
    # Classes
    'DataLoader',
    'CapexCalculator',
    'MACCalculator',
    'EmissionCalculator',
    'PriceCalculator',
    'TechnologyCostCalculator',
    'StrandedAssetCalculator',
    # Validator classes
    'DataValidator',
    'ValidationResult',
    'ValidationError',
    'Severity',
    'SchemaValidator',
    'ReferentialIntegrityValidator',
    'BusinessRuleValidator',
    'TemporalValidator',
    'OutputValidator',
    # Excel reviewer classes
    'ExcelReviewer',
    'ExcelReviewerConfig',
    'get_available_scenarios',
    # Functions
    'validate_data_integrity',
    'select_technology_for_facility',
    'save_csv_output',
    'save_plot',
    'identify_product_group',
    'is_ncc_facility',
    'format_number',
]
