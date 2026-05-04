"""
Data Validation Module
======================
Comprehensive data validation for the Korean Petrochemical MACC Model.

Validates:
- Input CSV files (schema, referential integrity, business rules, temporal consistency)
- Output files (structure, calculation consistency)

Usage:
    # Standalone CLI
    python -m modules.data_validator [--validate-outputs] [--strict]

    # Programmatic
    from modules.data_validator import DataValidator
    validator = DataValidator('data')
    results = validator.validate_all()
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
import pandas as pd
import numpy as np


class Severity(Enum):
    """Severity levels for validation errors"""
    ERROR = "ERROR"      # Critical - will cause failures
    WARNING = "WARNING"  # May cause issues but won't fail
    INFO = "INFO"        # Informational only


@dataclass
class ValidationError:
    """Structured validation error with location and fix suggestion"""
    severity: Severity
    file: str
    message: str
    row: Optional[int] = None
    column: Optional[str] = None
    found: Optional[Any] = None
    expected: Optional[str] = None
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        parts = [f"[{self.severity.value}] {self.file}"]
        if self.row is not None or self.column is not None:
            location = []
            if self.row is not None:
                location.append(f"Row {self.row}")
            if self.column is not None:
                location.append(f"Column '{self.column}'")
            parts.append(f"  {', '.join(location)}: {self.message}")
        else:
            parts.append(f"  {self.message}")
        if self.found is not None:
            parts.append(f"  Found: {self.found}")
        if self.expected is not None:
            parts.append(f"  Expected: {self.expected}")
        if self.suggestion is not None:
            parts.append(f"  Suggestion: {self.suggestion}")
        return "\n".join(parts)


@dataclass
class ValidationResult:
    """Container for validation outcomes"""
    valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    info: List[ValidationError] = field(default_factory=list)

    def add(self, error: ValidationError):
        """Add a validation error to the appropriate list"""
        if error.severity == Severity.ERROR:
            self.errors.append(error)
            self.valid = False
        elif error.severity == Severity.WARNING:
            self.warnings.append(error)
        else:
            self.info.append(error)

    def merge(self, other: 'ValidationResult'):
        """Merge another ValidationResult into this one"""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        if not other.valid:
            self.valid = False

    def __str__(self) -> str:
        parts = []
        status = "PASSED" if self.valid else "FAILED"
        parts.append(f"Validation {status}: {len(self.errors)} errors, {len(self.warnings)} warnings")
        for e in self.errors + self.warnings:
            parts.append(str(e))
        return "\n".join(parts)

    def summary(self) -> str:
        """Return a brief summary"""
        return f"Errors: {len(self.errors)}, Warnings: {len(self.warnings)}, Info: {len(self.info)}"


class SchemaValidator:
    """Validates column presence, data types, and basic constraints"""

    # Schema definitions: {filename: {columns: {col_name: {type, required, nullable}}}}
    SCHEMAS = {
        'facility_database_with_shaheen.csv': {
            'columns': {
                'product': {'type': 'string', 'required': True, 'nullable': False},
                'process': {'type': 'string', 'required': True, 'nullable': False},
                'company': {'type': 'string', 'required': True, 'nullable': False},
                'location': {'type': 'string', 'required': True, 'nullable': False},
                'capacity_kt': {'type': 'numeric', 'required': True, 'nullable': False},
                'year_built': {'type': 'numeric', 'required': True, 'nullable': False},
            }
        },
        'facility_database_with_regions.csv': {
            'columns': {
                'product': {'type': 'string', 'required': True, 'nullable': False},
                'process': {'type': 'string', 'required': True, 'nullable': False},
                'company': {'type': 'string', 'required': True, 'nullable': False},
                'location': {'type': 'string', 'required': True, 'nullable': False},
                'capacity_kt': {'type': 'numeric', 'required': True, 'nullable': False},
                'year_built': {'type': 'numeric', 'required': True, 'nullable': False},
            }
        },
        'product_benchmarks.csv': {
            'columns': {
                'product': {'type': 'string', 'required': True, 'nullable': False},
                'process': {'type': 'string', 'required': True, 'nullable': False},
                'Electricity_kWh_per_tonne': {'type': 'numeric', 'required': True, 'nullable': False},
            }
        },
        'technology_parameters.csv': {
            'columns': {
                'technology': {'type': 'string', 'required': True, 'nullable': False},
                'applies_to': {'type': 'string', 'required': True, 'nullable': False},
                'energy_conversion_efficiency': {'type': 'numeric', 'required': True, 'nullable': True},
                'trl': {'type': 'numeric', 'required': True, 'nullable': True},
                'available_year': {'type': 'numeric', 'required': True, 'nullable': True},
            }
        },
        'technology_capex.csv': {
            'columns': {
                'technology': {'type': 'string', 'required': True, 'nullable': False},
                'applies_to': {'type': 'string', 'required': True, 'nullable': False},
                'capex_2025': {'type': 'numeric', 'required': True, 'nullable': False},
                'capex_2030': {'type': 'numeric', 'required': True, 'nullable': False},
                'capex_2040': {'type': 'numeric', 'required': True, 'nullable': False},
                'capex_2050': {'type': 'numeric', 'required': True, 'nullable': False},
                'opex_pct_capex': {'type': 'numeric', 'required': True, 'nullable': False},
                'lifetime_years': {'type': 'numeric', 'required': True, 'nullable': False},
            }
        },
        'emission_factors.csv': {
            'columns': {
                'fuel': {'type': 'string', 'required': True, 'nullable': False},
            }
        },
        'h2_price_trajectory.csv': {
            'columns': {
                'year': {'type': 'numeric', 'required': True, 'nullable': False},
                'h2_price_usd_per_kg': {'type': 'numeric', 'required': True, 'nullable': False},
            }
        },
        're_price_trajectory.csv': {
            'columns': {
                'year': {'type': 'numeric', 'required': True, 'nullable': False},
                're_price_usd_per_mwh': {'type': 'numeric', 'required': True, 'nullable': False},
            }
        },
        'grid_price_trajectory.csv': {
            'columns': {
                'year': {'type': 'numeric', 'required': True, 'nullable': False},
                'grid_price_usd_per_mwh': {'type': 'numeric', 'required': True, 'nullable': False},
            }
        },
        'grid_emission_trajectory.csv': {
            'columns': {
                'year': {'type': 'numeric', 'required': True, 'nullable': False},
                'grid_ef_tco2_per_mwh': {'type': 'numeric', 'required': True, 'nullable': False},
            }
        },
        'fuel_price_trajectory.csv': {
            'columns': {
                'year': {'type': 'numeric', 'required': True, 'nullable': False},
            }
        },
        'scenario_definitions.csv': {
            'columns': {
                'name': {'type': 'string', 'required': True, 'nullable': False},
                'production': {'type': 'string', 'required': True, 'nullable': False},
                'ncc_tech': {'type': 'string', 'required': True, 'nullable': False},
                'carbon_pathway': {'type': 'string', 'required': True, 'nullable': False},
            }
        },
        'region_mapping.csv': {
            'columns': {
                'location': {'type': 'string', 'required': True, 'nullable': False},
                'region': {'type': 'string', 'required': True, 'nullable': False},
            }
        },
        'carbon_budget_scenarios.csv': {
            'columns': {
                'year': {'type': 'numeric', 'required': True, 'nullable': False},
            }
        },
    }

    def validate(self, filename: str, df: pd.DataFrame) -> ValidationResult:
        """Validate a DataFrame against its schema"""
        result = ValidationResult()

        if filename not in self.SCHEMAS:
            result.add(ValidationError(
                severity=Severity.INFO,
                file=filename,
                message=f"No schema defined for file, skipping schema validation"
            ))
            return result

        schema = self.SCHEMAS[filename]

        # Check required columns exist
        for col, spec in schema['columns'].items():
            if spec.get('required', False) and col not in df.columns:
                result.add(ValidationError(
                    severity=Severity.ERROR,
                    file=filename,
                    message=f"Missing required column",
                    column=col,
                    suggestion=f"Add column '{col}' to the file"
                ))
                continue

            if col not in df.columns:
                continue

            # Check data type
            if spec.get('type') == 'numeric':
                non_numeric = df[col].apply(lambda x: pd.notna(x) and not isinstance(x, (int, float, np.integer, np.floating)))
                if non_numeric.any():
                    bad_rows = df.index[non_numeric].tolist()[:5]  # First 5 bad rows
                    result.add(ValidationError(
                        severity=Severity.ERROR,
                        file=filename,
                        column=col,
                        message=f"Non-numeric values in numeric column",
                        found=f"Rows with issues: {bad_rows}",
                        expected="Numeric values",
                        suggestion="Convert values to numbers or check for typos"
                    ))

            # Check nullability
            if not spec.get('nullable', True):
                null_count = df[col].isna().sum()
                if null_count > 0:
                    null_rows = df.index[df[col].isna()].tolist()[:5]
                    result.add(ValidationError(
                        severity=Severity.ERROR,
                        file=filename,
                        column=col,
                        message=f"Null values in non-nullable column ({null_count} nulls)",
                        found=f"Rows with nulls: {null_rows}",
                        suggestion="Fill in missing values or check data source"
                    ))

        return result


class ReferentialIntegrityValidator:
    """Validates foreign key relationships between files"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._cache: Dict[str, pd.DataFrame] = {}

    def _load_csv(self, path: Path) -> Optional[pd.DataFrame]:
        """Load a CSV file with caching"""
        str_path = str(path)
        if str_path not in self._cache:
            if path.exists():
                self._cache[str_path] = pd.read_csv(path)
            else:
                return None
        return self._cache[str_path]

    def validate_facility_benchmarks(self) -> ValidationResult:
        """Validate that all facility (product, process) pairs have benchmarks"""
        result = ValidationResult()

        # Load files
        fac_path = self.data_dir / 'assets' / 'facility_database_with_shaheen.csv'
        bench_path = self.data_dir / 'assumptions' / 'product_benchmarks.csv'

        facilities = self._load_csv(fac_path)
        benchmarks = self._load_csv(bench_path)

        if facilities is None:
            result.add(ValidationError(
                severity=Severity.ERROR,
                file='facility_database_with_shaheen.csv',
                message="File not found",
                suggestion="Ensure facility database exists in data/assets/"
            ))
            return result

        if benchmarks is None:
            result.add(ValidationError(
                severity=Severity.ERROR,
                file='product_benchmarks.csv',
                message="File not found",
                suggestion="Ensure product benchmarks exists in data/assumptions/"
            ))
            return result

        # Get unique (product, process) pairs
        fac_pairs = set(zip(facilities['product'], facilities['process']))
        bench_pairs = set(zip(benchmarks['product'], benchmarks['process']))

        # Find missing benchmarks
        missing = fac_pairs - bench_pairs
        if missing:
            for product, process in missing:
                result.add(ValidationError(
                    severity=Severity.ERROR,
                    file='product_benchmarks.csv',
                    message=f"Missing benchmark for facility profile",
                    found=f"product='{product}', process='{process}'",
                    suggestion=f"Add row with product='{product}', process='{process}' to product_benchmarks.csv"
                ))

        return result

    def validate_location_region_mapping(self) -> ValidationResult:
        """Validate that all facility locations have region mappings"""
        result = ValidationResult()

        fac_path = self.data_dir / 'assets' / 'facility_database_with_shaheen.csv'
        region_path = self.data_dir / 'assets' / 'region_mapping.csv'

        facilities = self._load_csv(fac_path)
        regions = self._load_csv(region_path)

        if facilities is None or regions is None:
            return result  # File errors already handled

        fac_locations = set(facilities['location'].unique())
        mapped_locations = set(regions['location'].unique())

        missing = fac_locations - mapped_locations
        if missing:
            for loc in missing:
                result.add(ValidationError(
                    severity=Severity.ERROR,
                    file='region_mapping.csv',
                    message=f"Missing region mapping for location",
                    found=f"location='{loc}'",
                    suggestion=f"Add row with location='{loc}' to region_mapping.csv"
                ))

        return result

    def validate_scenario_tech_references(self) -> ValidationResult:
        """Validate that scenario ncc_tech values exist in technology params"""
        result = ValidationResult()

        scenario_path = self.data_dir / 'scenarios' / 'scenario_definitions.csv'
        tech_path = self.data_dir / 'assumptions' / 'technology_parameters.csv'

        scenarios = self._load_csv(scenario_path)
        tech_params = self._load_csv(tech_path)

        if scenarios is None or tech_params is None:
            return result

        valid_techs = set(tech_params['technology'].unique())
        scenario_techs = set(scenarios['ncc_tech'].unique())

        invalid = scenario_techs - valid_techs
        if invalid:
            for tech in invalid:
                result.add(ValidationError(
                    severity=Severity.ERROR,
                    file='scenario_definitions.csv',
                    message=f"Invalid technology reference",
                    column='ncc_tech',
                    found=tech,
                    expected=f"One of: {valid_techs}",
                    suggestion=f"Use valid technology name or add '{tech}' to technology_parameters.csv"
                ))

        return result

    def validate_all(self) -> ValidationResult:
        """Run all referential integrity validations"""
        result = ValidationResult()
        result.merge(self.validate_facility_benchmarks())
        result.merge(self.validate_location_region_mapping())
        result.merge(self.validate_scenario_tech_references())
        return result


class BusinessRuleValidator:
    """Validates domain-specific business rules"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._cache: Dict[str, pd.DataFrame] = {}

    def _load_csv(self, path: Path) -> Optional[pd.DataFrame]:
        """Load a CSV file with caching"""
        str_path = str(path)
        if str_path not in self._cache:
            if path.exists():
                self._cache[str_path] = pd.read_csv(path)
            else:
                return None
        return self._cache[str_path]

    def validate_facility_data(self) -> ValidationResult:
        """Validate facility database business rules"""
        result = ValidationResult()
        filename = 'facility_database_with_shaheen.csv'

        df = self._load_csv(self.data_dir / 'assets' / filename)
        if df is None:
            return result

        # Rule: capacity_kt must be positive
        if 'capacity_kt' in df.columns:
            invalid_capacity = df[df['capacity_kt'] <= 0]
            if len(invalid_capacity) > 0:
                for idx, row in invalid_capacity.iterrows():
                    result.add(ValidationError(
                        severity=Severity.ERROR,
                        file=filename,
                        row=idx + 2,  # +2 for 1-indexed + header
                        column='capacity_kt',
                        message="Capacity must be positive",
                        found=row['capacity_kt'],
                        expected="capacity_kt > 0",
                        suggestion="Check source data for capacity values"
                    ))

        # Rule: year_built should be between 1950 and 2030 (allowing planned projects)
        if 'year_built' in df.columns:
            invalid_years = df[(df['year_built'] < 1950) | (df['year_built'] > 2030)]
            if len(invalid_years) > 0:
                for idx, row in invalid_years.iterrows():
                    result.add(ValidationError(
                        severity=Severity.WARNING,
                        file=filename,
                        row=idx + 2,
                        column='year_built',
                        message="Year built outside expected range",
                        found=row['year_built'],
                        expected="1950 <= year_built <= 2030 (includes planned projects)",
                        suggestion="Verify construction year is correct"
                    ))

        return result

    def validate_emission_factors(self) -> ValidationResult:
        """Validate emission factors"""
        result = ValidationResult()
        filename = 'emission_factors.csv'

        df = self._load_csv(self.data_dir / 'assumptions' / filename)
        if df is None:
            return result

        # Rule: H2 emission factor should be 0 (green H2 assumption)
        h2_rows = df[df['fuel'] == 'H2']
        if len(h2_rows) > 0:
            for idx, row in h2_rows.iterrows():
                # Check tCO2_per_kg column for H2
                if 'tCO2_per_kg' in df.columns and pd.notna(row.get('tCO2_per_kg')):
                    if row['tCO2_per_kg'] != 0:
                        result.add(ValidationError(
                            severity=Severity.WARNING,
                            file=filename,
                            row=idx + 2,
                            column='tCO2_per_kg',
                            message="H2 emission factor should be 0 for green hydrogen",
                            found=row['tCO2_per_kg'],
                            expected="0 (zero-emission green hydrogen)",
                            suggestion="Verify hydrogen source assumption"
                        ))
        else:
            result.add(ValidationError(
                severity=Severity.WARNING,
                file=filename,
                message="H2 fuel type not found",
                suggestion="Add H2 row with zero emission factor for green hydrogen"
            ))

        # Rule: Required fuels must be present
        required_fuels = {'Naphtha', 'LNG', 'Electricity', 'Fuel_Gas'}
        present_fuels = set(df['fuel'].unique())
        missing_fuels = required_fuels - present_fuels
        if missing_fuels:
            result.add(ValidationError(
                severity=Severity.ERROR,
                file=filename,
                message=f"Missing required fuel types",
                found=f"Present: {present_fuels}",
                expected=f"Required: {required_fuels}",
                suggestion=f"Add rows for: {missing_fuels}"
            ))

        return result

    def validate_technology_capex(self) -> ValidationResult:
        """Validate technology CAPEX data"""
        result = ValidationResult()
        filename = 'technology_capex.csv'

        df = self._load_csv(self.data_dir / 'assumptions' / filename)
        if df is None:
            return result

        capex_cols = ['capex_2025', 'capex_2030', 'capex_2040', 'capex_2050']

        for idx, row in df.iterrows():
            tech = row.get('technology', f'Row {idx}')

            # Skip RE_PPA which has 0 CAPEX by design
            if tech == 'RE_PPA':
                continue

            # Rule: CAPEX should generally decrease over time (learning curve)
            capex_values = [row.get(col, 0) for col in capex_cols if col in df.columns]
            valid_values = [v for v in capex_values if pd.notna(v) and v > 0]

            if len(valid_values) >= 2:
                # Check if values are generally decreasing
                if valid_values[-1] > valid_values[0]:
                    result.add(ValidationError(
                        severity=Severity.WARNING,
                        file=filename,
                        row=idx + 2,
                        message=f"Technology '{tech}' CAPEX increases over time (unusual)",
                        found=f"2025: {valid_values[0]}, 2050: {valid_values[-1]}",
                        expected="CAPEX generally decreasing (learning curve)",
                        suggestion="Verify CAPEX trajectory for this technology"
                    ))

            # Rule: Lifetime should be positive
            if 'lifetime_years' in df.columns:
                lifetime = row.get('lifetime_years')
                if pd.notna(lifetime) and lifetime <= 0:
                    result.add(ValidationError(
                        severity=Severity.ERROR,
                        file=filename,
                        row=idx + 2,
                        column='lifetime_years',
                        message=f"Technology '{tech}' has invalid lifetime",
                        found=lifetime,
                        expected="lifetime_years > 0",
                        suggestion="Set positive lifetime value"
                    ))

        # Rule: Required technologies must be present
        required_techs = {'Heat_Pump', 'NCC-H2', 'NCC-Electricity', 'RDH'}
        present_techs = set(df['technology'].unique())
        missing_techs = required_techs - present_techs
        if missing_techs:
            result.add(ValidationError(
                severity=Severity.ERROR,
                file=filename,
                message=f"Missing required technologies",
                found=f"Present: {present_techs}",
                expected=f"Required: {required_techs}",
                suggestion=f"Add rows for: {missing_techs}"
            ))

        return result

    def validate_product_benchmarks(self) -> ValidationResult:
        """Validate product benchmarks data"""
        result = ValidationResult()
        filename = 'product_benchmarks.csv'

        df = self._load_csv(self.data_dir / 'assumptions' / filename)
        if df is None:
            return result

        # Energy intensity columns to check
        energy_cols = [col for col in df.columns if 'GJ_per_tonne' in col or 'kWh_per_tonne' in col]

        for idx, row in df.iterrows():
            product = row.get('product', f'Row {idx}')

            # Rule: All energy intensities should be >= 0
            for col in energy_cols:
                if col in df.columns and pd.notna(row.get(col)):
                    if row[col] < 0:
                        result.add(ValidationError(
                            severity=Severity.ERROR,
                            file=filename,
                            row=idx + 2,
                            column=col,
                            message=f"Negative energy intensity for {product}",
                            found=row[col],
                            expected="value >= 0",
                            suggestion="Check source data for energy intensity"
                        ))

            # Rule: At least one energy intensity should be > 0
            energy_values = [row.get(col, 0) for col in energy_cols if col in df.columns]
            valid_values = [v for v in energy_values if pd.notna(v)]
            if all(v == 0 for v in valid_values):
                result.add(ValidationError(
                    severity=Severity.WARNING,
                    file=filename,
                    row=idx + 2,
                    message=f"Product '{product}' has zero energy intensity across all sources",
                    suggestion="Verify if this product requires no energy input"
                ))

        return result

    def validate_scenario_definitions(self) -> ValidationResult:
        """Validate scenario definitions"""
        result = ValidationResult()
        filename = 'scenario_definitions.csv'

        df = self._load_csv(self.data_dir / 'scenarios' / filename)
        if df is None:
            return result

        # Valid enum values
        valid_productions = {'shaheen', 'restructure_25pct', 'restructure_40pct', 'baseline'}
        valid_pathways = {'1.5C', '2.0C'}

        for idx, row in df.iterrows():
            scenario_name = row.get('name', f'Row {idx}')

            # Rule: production type must be valid
            production = row.get('production')
            if production not in valid_productions:
                result.add(ValidationError(
                    severity=Severity.ERROR,
                    file=filename,
                    row=idx + 2,
                    column='production',
                    message=f"Invalid production type for scenario '{scenario_name}'",
                    found=production,
                    expected=f"One of: {valid_productions}",
                    suggestion="Use valid production type"
                ))

            # Rule: carbon_pathway must be valid
            pathway = row.get('carbon_pathway')
            if pathway not in valid_pathways:
                result.add(ValidationError(
                    severity=Severity.ERROR,
                    file=filename,
                    row=idx + 2,
                    column='carbon_pathway',
                    message=f"Invalid carbon pathway for scenario '{scenario_name}'",
                    found=pathway,
                    expected=f"One of: {valid_pathways}",
                    suggestion="Use valid carbon pathway"
                ))

        return result

    def validate_all(self) -> ValidationResult:
        """Run all business rule validations"""
        result = ValidationResult()
        result.merge(self.validate_facility_data())
        result.merge(self.validate_emission_factors())
        result.merge(self.validate_technology_capex())
        result.merge(self.validate_product_benchmarks())
        result.merge(self.validate_scenario_definitions())
        return result


class TemporalValidator:
    """Validates time-series completeness and consistency"""

    EXPECTED_YEARS = list(range(2025, 2051))  # 2025-2050

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def _load_csv(self, path: Path) -> Optional[pd.DataFrame]:
        """Load a CSV file"""
        if path.exists():
            return pd.read_csv(path)
        return None

    def validate_price_trajectory(self, filename: str, price_col: str) -> ValidationResult:
        """Validate a price trajectory file"""
        result = ValidationResult()

        # Determine path based on filename
        if filename in ['h2_price_trajectory.csv', 're_price_trajectory.csv',
                       'grid_price_trajectory.csv', 'grid_emission_trajectory.csv',
                       'fuel_price_trajectory.csv']:
            path = self.data_dir / 'assumptions' / 'prices' / filename
        else:
            path = self.data_dir / 'assumptions' / filename

        df = self._load_csv(path)
        if df is None:
            result.add(ValidationError(
                severity=Severity.ERROR,
                file=filename,
                message="File not found",
                suggestion=f"Ensure file exists at {path}"
            ))
            return result

        if 'year' not in df.columns:
            result.add(ValidationError(
                severity=Severity.ERROR,
                file=filename,
                message="Missing 'year' column",
                suggestion="Add 'year' column to the file"
            ))
            return result

        # Check for complete year coverage
        present_years = set(df['year'].unique())
        expected_years = set(self.EXPECTED_YEARS)

        missing_years = expected_years - present_years
        if missing_years:
            result.add(ValidationError(
                severity=Severity.ERROR,
                file=filename,
                column='year',
                message=f"Missing years in trajectory",
                found=f"Missing: {sorted(missing_years)[:10]}{'...' if len(missing_years) > 10 else ''}",
                expected="Complete coverage 2025-2050",
                suggestion="Add rows for missing years"
            ))

        # Check for positive values in price column
        if price_col in df.columns:
            negative_prices = df[df[price_col] < 0]
            if len(negative_prices) > 0:
                bad_years = negative_prices['year'].tolist()[:5]
                result.add(ValidationError(
                    severity=Severity.ERROR,
                    file=filename,
                    column=price_col,
                    message="Negative price values found",
                    found=f"Years with negative prices: {bad_years}",
                    expected="All prices >= 0",
                    suggestion="Check source data for price values"
                ))

        return result

    def validate_h2_price_trajectory(self) -> ValidationResult:
        """Validate H2 price trajectory with additional monotonic check"""
        result = self.validate_price_trajectory('h2_price_trajectory.csv', 'h2_price_usd_per_kg')

        path = self.data_dir / 'assumptions' / 'prices' / 'h2_price_trajectory.csv'
        df = self._load_csv(path)
        if df is None or 'h2_price_usd_per_kg' not in df.columns:
            return result

        # Check monotonically decreasing (technology learning)
        df_sorted = df.sort_values('year')
        prices = df_sorted['h2_price_usd_per_kg'].values

        # Check if any year has higher price than previous
        increases = []
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1] * 1.01:  # 1% tolerance
                increases.append((df_sorted['year'].iloc[i], prices[i-1], prices[i]))

        if increases:
            result.add(ValidationError(
                severity=Severity.WARNING,
                file='h2_price_trajectory.csv',
                column='h2_price_usd_per_kg',
                message="H2 price not monotonically decreasing",
                found=f"Price increases at years: {[i[0] for i in increases[:5]]}",
                expected="Generally decreasing prices (technology learning curve)",
                suggestion="Verify H2 price trajectory assumptions"
            ))

        return result

    def validate_re_price_trajectory(self) -> ValidationResult:
        """Validate RE price trajectory with additional monotonic check"""
        result = self.validate_price_trajectory('re_price_trajectory.csv', 're_price_usd_per_mwh')

        path = self.data_dir / 'assumptions' / 'prices' / 're_price_trajectory.csv'
        df = self._load_csv(path)
        if df is None or 're_price_usd_per_mwh' not in df.columns:
            return result

        # Check monotonically decreasing
        df_sorted = df.sort_values('year')
        prices = df_sorted['re_price_usd_per_mwh'].values

        increases = []
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1] * 1.01:  # 1% tolerance
                increases.append((df_sorted['year'].iloc[i], prices[i-1], prices[i]))

        if increases:
            result.add(ValidationError(
                severity=Severity.WARNING,
                file='re_price_trajectory.csv',
                column='re_price_usd_per_mwh',
                message="RE price not monotonically decreasing",
                found=f"Price increases at years: {[i[0] for i in increases[:5]]}",
                expected="Generally decreasing prices (technology learning curve)",
                suggestion="Verify RE price trajectory assumptions"
            ))

        return result

    def validate_demand_trajectory(self, scenario_type: str) -> ValidationResult:
        """Validate a demand growth trajectory file"""
        result = ValidationResult()
        filename = f'demand_growth_trajectory_{scenario_type}.csv'
        path = self.data_dir / 'scenarios' / filename

        df = self._load_csv(path)
        if df is None:
            result.add(ValidationError(
                severity=Severity.WARNING,
                file=filename,
                message="Demand trajectory file not found",
                suggestion=f"Create file at {path} if scenario '{scenario_type}' is used"
            ))
            return result

        if 'year' not in df.columns:
            result.add(ValidationError(
                severity=Severity.ERROR,
                file=filename,
                message="Missing 'year' column"
            ))
            return result

        # Check year coverage
        present_years = set(df['year'].unique())
        expected_years = set(self.EXPECTED_YEARS)

        missing_years = expected_years - present_years
        if missing_years:
            result.add(ValidationError(
                severity=Severity.ERROR,
                file=filename,
                column='year',
                message=f"Missing years in demand trajectory",
                found=f"Missing: {sorted(missing_years)[:10]}{'...' if len(missing_years) > 10 else ''}",
                expected="Complete coverage 2025-2050"
            ))

        # Check operating rate column if present
        if 'operating_rate_pct' in df.columns:
            invalid_rates = df[(df['operating_rate_pct'] < 0) | (df['operating_rate_pct'] > 150)]
            if len(invalid_rates) > 0:
                result.add(ValidationError(
                    severity=Severity.WARNING,
                    file=filename,
                    column='operating_rate_pct',
                    message="Operating rate outside expected range (0-150%)",
                    found=f"Unusual values at years: {invalid_rates['year'].tolist()[:5]}",
                    suggestion="Verify operating rate assumptions"
                ))

        return result

    def validate_all(self) -> ValidationResult:
        """Run all temporal validations"""
        result = ValidationResult()

        # Price trajectories
        result.merge(self.validate_h2_price_trajectory())
        result.merge(self.validate_re_price_trajectory())
        result.merge(self.validate_price_trajectory('grid_price_trajectory.csv', 'grid_price_usd_per_mwh'))
        result.merge(self.validate_price_trajectory('grid_emission_trajectory.csv', 'grid_ef_tco2_per_mwh'))
        result.merge(self.validate_price_trajectory('fuel_price_trajectory.csv', 'naphtha_usd_per_gj'))

        # Demand trajectories
        for scenario_type in ['shaheen', 'restructure_25pct', 'restructure_40pct']:
            result.merge(self.validate_demand_trajectory(scenario_type))

        return result


class OutputValidator:
    """Validates output CSV files for structure and consistency"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def _load_csv(self, path: Path) -> Optional[pd.DataFrame]:
        """Load a CSV file"""
        if path.exists():
            return pd.read_csv(path)
        return None

    def validate_scenario_results(self) -> ValidationResult:
        """Validate the main scenario_results.csv output"""
        result = ValidationResult()
        filename = 'scenario_results.csv'
        path = self.output_dir / filename

        df = self._load_csv(path)
        if df is None:
            result.add(ValidationError(
                severity=Severity.ERROR,
                file=filename,
                message="Output file not found",
                suggestion="Run scenarios first: python run_scenarios.py"
            ))
            return result

        # Required columns
        required_cols = ['year', 'scenario', 'facility_id', 'bau_emissions_tco2',
                         'emissions_tco2', 'abatement_tco2']
        for col in required_cols:
            if col not in df.columns:
                result.add(ValidationError(
                    severity=Severity.ERROR,
                    file=filename,
                    message=f"Missing required column",
                    column=col
                ))

        if not all(col in df.columns for col in required_cols):
            return result

        # Rule: emissions should be non-negative
        negative_emissions = df[df['emissions_tco2'] < 0]
        if len(negative_emissions) > 0:
            sample_rows = negative_emissions.head(5)
            result.add(ValidationError(
                severity=Severity.ERROR,
                file=filename,
                column='emissions_tco2',
                message=f"Negative emissions found ({len(negative_emissions)} rows)",
                found=f"Sample: {sample_rows[['year', 'scenario', 'facility_id', 'emissions_tco2']].to_dict('records')[:3]}",
                expected="emissions_tco2 >= 0"
            ))

        # Rule: abatement should equal bau - actual (with tolerance)
        df['calc_abatement'] = df['bau_emissions_tco2'] - df['emissions_tco2']
        # Use relative tolerance for larger values
        tolerance_mask = ~np.isclose(df['abatement_tco2'], df['calc_abatement'], rtol=1e-6, atol=1e-3)
        mismatches = df[tolerance_mask]

        if len(mismatches) > 0:
            sample = mismatches.head(3)
            result.add(ValidationError(
                severity=Severity.WARNING,
                file=filename,
                message=f"Abatement calculation mismatch ({len(mismatches)} rows)",
                found=f"abatement_tco2 != (bau - emissions) in some rows",
                expected="abatement_tco2 = bau_emissions_tco2 - emissions_tco2",
                suggestion="Check calculation logic in run_scenarios.py"
            ))

        # Rule: abatement should not exceed BAU
        invalid_abatement = df[df['abatement_tco2'] > df['bau_emissions_tco2'] * 1.01]  # 1% tolerance
        if len(invalid_abatement) > 0:
            result.add(ValidationError(
                severity=Severity.WARNING,
                file=filename,
                column='abatement_tco2',
                message=f"Abatement exceeds BAU emissions ({len(invalid_abatement)} rows)",
                expected="abatement_tco2 <= bau_emissions_tco2",
                suggestion="Check if calculation logic allows over-abatement"
            ))

        # Rule: year range should be 2025-2050
        years = df['year'].unique()
        if min(years) != 2025 or max(years) != 2050:
            result.add(ValidationError(
                severity=Severity.WARNING,
                file=filename,
                column='year',
                message="Unexpected year range",
                found=f"Years: {min(years)}-{max(years)}",
                expected="2025-2050"
            ))

        # Info: report size statistics
        result.add(ValidationError(
            severity=Severity.INFO,
            file=filename,
            message=f"Output statistics: {len(df)} rows, {df['scenario'].nunique()} scenarios, "
                    f"{df['facility_id'].nunique()} facilities, {len(years)} years"
        ))

        return result

    def validate_regional_summaries(self) -> ValidationResult:
        """Validate regional summary outputs"""
        result = ValidationResult()

        for filename in ['regional_mac_summary.csv', 'regional_abatement_summary.csv']:
            path = self.output_dir / filename
            df = self._load_csv(path)

            if df is None:
                result.add(ValidationError(
                    severity=Severity.WARNING,
                    file=filename,
                    message="Regional summary file not found"
                ))
                continue

            # Check required columns
            required = ['scenario', 'year', 'region']
            for col in required:
                if col not in df.columns:
                    result.add(ValidationError(
                        severity=Severity.ERROR,
                        file=filename,
                        column=col,
                        message=f"Missing required column"
                    ))

        return result

    def validate_all(self) -> ValidationResult:
        """Run all output validations"""
        result = ValidationResult()
        result.merge(self.validate_scenario_results())
        result.merge(self.validate_regional_summaries())
        return result


class DataValidator:
    """Main orchestrator for all data validation"""

    def __init__(self, data_dir: str = 'data', output_dir: str = 'outputs'):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)

        # Initialize validators
        self.schema_validator = SchemaValidator()
        self.ref_validator = ReferentialIntegrityValidator(self.data_dir)
        self.business_validator = BusinessRuleValidator(self.data_dir)
        self.temporal_validator = TemporalValidator(self.data_dir)
        self.output_validator = OutputValidator(self.output_dir)

    def _load_all_csvs(self) -> Dict[str, Tuple[Path, pd.DataFrame]]:
        """Load all CSV files from the data directory"""
        csvs = {}

        # Assets
        for f in (self.data_dir / 'assets').glob('*.csv'):
            csvs[f.name] = (f, pd.read_csv(f))

        # Assumptions
        for f in (self.data_dir / 'assumptions').glob('*.csv'):
            csvs[f.name] = (f, pd.read_csv(f))

        # Prices
        for f in (self.data_dir / 'assumptions' / 'prices').glob('*.csv'):
            csvs[f.name] = (f, pd.read_csv(f))

        # Scenarios
        for f in (self.data_dir / 'scenarios').glob('*.csv'):
            csvs[f.name] = (f, pd.read_csv(f))

        return csvs

    def validate_schema_all(self) -> ValidationResult:
        """Run schema validation on all CSV files"""
        result = ValidationResult()
        csvs = self._load_all_csvs()

        for filename, (path, df) in csvs.items():
            file_result = self.schema_validator.validate(filename, df)
            result.merge(file_result)

        return result

    def validate_inputs(self, strict: bool = False) -> ValidationResult:
        """
        Validate all input data files.

        Args:
            strict: If True, treat warnings as errors

        Returns:
            ValidationResult with all validation outcomes
        """
        result = ValidationResult()

        print("Validating input data...")
        print("-" * 60)

        # 1. Schema validation
        print("  [1/4] Schema validation...")
        schema_result = self.validate_schema_all()
        result.merge(schema_result)
        print(f"        {schema_result.summary()}")

        # 2. Referential integrity
        print("  [2/4] Referential integrity...")
        ref_result = self.ref_validator.validate_all()
        result.merge(ref_result)
        print(f"        {ref_result.summary()}")

        # 3. Business rules
        print("  [3/4] Business rules...")
        business_result = self.business_validator.validate_all()
        result.merge(business_result)
        print(f"        {business_result.summary()}")

        # 4. Temporal consistency
        print("  [4/4] Temporal consistency...")
        temporal_result = self.temporal_validator.validate_all()
        result.merge(temporal_result)
        print(f"        {temporal_result.summary()}")

        # Apply strict mode
        if strict and result.warnings:
            for warning in result.warnings:
                warning.severity = Severity.ERROR
                result.errors.append(warning)
            result.warnings = []
            result.valid = len(result.errors) == 0

        return result

    def validate_outputs(self) -> ValidationResult:
        """Validate output files after scenario run"""
        print("\nValidating output data...")
        print("-" * 60)

        result = self.output_validator.validate_all()
        print(f"  {result.summary()}")

        return result

    def validate_all(self, include_outputs: bool = False, strict: bool = False) -> ValidationResult:
        """
        Run complete validation suite.

        Args:
            include_outputs: If True, also validate output files
            strict: If True, treat warnings as errors

        Returns:
            Combined ValidationResult
        """
        result = ValidationResult()

        # Validate inputs
        input_result = self.validate_inputs(strict=strict)
        result.merge(input_result)

        # Optionally validate outputs
        if include_outputs:
            output_result = self.validate_outputs()
            result.merge(output_result)

        return result

    def print_report(self, result: ValidationResult, verbose: bool = False):
        """Print a formatted validation report"""
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)

        status = "PASSED" if result.valid else "FAILED"
        print(f"\nStatus: {status}")
        print(f"Errors: {len(result.errors)}")
        print(f"Warnings: {len(result.warnings)}")
        print(f"Info: {len(result.info)}")

        if result.errors:
            print("\n--- ERRORS ---")
            for e in result.errors:
                print(str(e))
                print()

        if result.warnings:
            print("\n--- WARNINGS ---")
            for w in result.warnings:
                print(str(w))
                print()

        if verbose and result.info:
            print("\n--- INFO ---")
            for i in result.info:
                print(str(i))
                print()

        print("=" * 60)


def main():
    """CLI entry point for data validation"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate data files for Korean Petrochemical MACC Model'
    )
    parser.add_argument(
        '--validate-outputs',
        action='store_true',
        help='Also validate output files (requires prior scenario run)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show info messages in report'
    )
    parser.add_argument(
        '--data-dir',
        default='data',
        help='Path to data directory (default: data)'
    )
    parser.add_argument(
        '--output-dir',
        default='outputs',
        help='Path to outputs directory (default: outputs)'
    )

    args = parser.parse_args()

    # Run validation
    validator = DataValidator(args.data_dir, args.output_dir)
    result = validator.validate_all(
        include_outputs=args.validate_outputs,
        strict=args.strict
    )

    # Print report
    validator.print_report(result, verbose=args.verbose)

    # Exit with appropriate code
    import sys
    sys.exit(0 if result.valid else 1)


if __name__ == '__main__':
    main()
