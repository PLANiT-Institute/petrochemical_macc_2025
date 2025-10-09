"""
Petrochemical MACC (Marginal Abatement Cost Curve) Library

A comprehensive library for modeling emission abatement technologies
and costs in the petrochemical industry.
"""

from .core.technology import (
    Technology, TechnologyTransition, AlternativeTechnology,
    TechBand, TechType, CostStructure, TechnologyConstraints
)

from .core.scenario import (
    EmissionsScenario, EmissionsBaseline, EmissionsTarget, ProcessBaseline
)

from .core.portfolio import TechnologyPortfolio

from .data.loaders import DataLoader, DataValidator

__version__ = "0.1.0"
__author__ = "Petrochemical MACC Team"

# Main API classes
__all__ = [
    # Core classes
    "Technology",
    "TechnologyTransition", 
    "AlternativeTechnology",
    "TechBand",
    "TechType",
    "CostStructure",
    "TechnologyConstraints",
    
    # Scenario classes
    "EmissionsScenario",
    "EmissionsBaseline", 
    "EmissionsTarget",
    "ProcessBaseline",
    
    # Portfolio
    "TechnologyPortfolio",
    
    # Data handling
    "DataLoader",
    "DataValidator"
]