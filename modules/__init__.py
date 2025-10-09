"""
Petrochemical MACC Model - Modular Architecture
Korean Petrochemical Industry Decarbonization Analysis

Modules:
- baseline: Baseline emissions and BAU trajectory
- macc: Dynamic MACC analysis
- optimization: Cost optimization under emission constraints
- financial: Financial analysis (NPV, IRR, payback)
- utils: Shared utilities and helper functions
"""

__version__ = '2.0.0'
__author__ = 'Petrochemical MACC Model'

from . import utils

# Import modules as they become available
try:
    from .baseline import BaselineAnalyzer
except ImportError:
    BaselineAnalyzer = None

try:
    from .macc import MACCAnalyzer
except ImportError:
    MACCAnalyzer = None

try:
    from .optimization import CostOptimizer
except ImportError:
    CostOptimizer = None

try:
    from .financial import FinancialAnalyzer
except ImportError:
    FinancialAnalyzer = None

__all__ = [
    'utils',
    'BaselineAnalyzer',
    'MACCAnalyzer',
    'CostOptimizer',
    'FinancialAnalyzer',
]
