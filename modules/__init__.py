"""Core modules for the Korean petrochemical MACC model."""

__version__ = '2.0.0'
__author__ = 'Petrochemical MACC Model'

from . import utils
from .data_manager import DataManager
from .baseline import BaselineAnalyzer
from .macc import MACCAnalyzer
from .optimization_v2 import CostOptimizerV2

__all__ = [
    'utils',
    'DataManager',
    'BaselineAnalyzer',
    'MACCAnalyzer',
    'CostOptimizerV2',
]
