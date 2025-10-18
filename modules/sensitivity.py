"""
Sensitivity Analysis Module
Creates alternative MACC scenarios with different assumptions:
1. Baseline clamps fossil fuel savings at zero (no negative fuel_diff)
2. Legacy comparison retains the full fuel cost differential
3. Learning curve sensitivities (with/without legacy fuel differential)
"""

import pandas as pd
import numpy as np
from pathlib import Path

class SensitivityAnalyzer:
    """Run sensitivity analysis on key assumptions"""

    def __init__(self, baseline_dir='data', output_dir='outputs/sensitivity'):
        self.baseline_dir = Path(baseline_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_all_scenarios(self):
        """Run all sensitivity scenarios"""
        print("\n" + "="*80)
        print("SENSITIVITY ANALYSIS: Testing Key Assumptions")
        print("="*80)

        scenarios = {
            'baseline': {
                'include_fuel_diff': False,
                'include_learning': True,
                'description': 'Baseline (No fossil fuel savings)'
            },
            'no_fuel_diff': {
                'include_fuel_diff': False,
                'include_learning': True,
                'description': 'No Fuel Cost Differential (same as baseline)'
            },
            'no_learning': {
                'include_fuel_diff': False,
                'include_learning': False,
                'description': 'No Learning Curves (2025 CAPEX constant)'
            },
            'no_fuel_no_learning': {
                'include_fuel_diff': False,
                'include_learning': False,
                'description': 'No Fuel Diff + No Learning (same as baseline assumptions)'
            },
            'legacy_with_fuel_diff': {
                'include_fuel_diff': True,
                'include_learning': True,
                'description': 'Legacy: includes fossil fuel savings'
            },
            'legacy_with_fuel_diff_no_learning': {
                'include_fuel_diff': True,
                'include_learning': False,
                'description': 'Legacy: fuel savings + no learning'
            }
        }

        results = {}

        for scenario_name, scenario_params in scenarios.items():
            print(f"\n{'─'*80}")
            print(f"Scenario: {scenario_params['description']}")
            print(f"{'─'*80}")

            df_macc = self.calculate_sensitivity_macc(
                include_fuel_diff=scenario_params['include_fuel_diff'],
                include_learning=scenario_params['include_learning']
            )

            # Save results
            output_file = self.output_dir / f'macc_{scenario_name}.csv'
            df_macc.to_csv(output_file, index=False)
            print(f"   ✓ Saved: {output_file.name}")

            # Calculate summary statistics
            summary = self.calculate_summary_statistics(df_macc, scenario_name)
            results[scenario_name] = summary

        # Create comparison table
        self.create_comparison_table(results)

        print(f"\n{'='*80}")
        print("SENSITIVITY ANALYSIS COMPLETE")
        print(f"{'='*80}")
        print(f"Output directory: {self.output_dir}")

        return results

    def calculate_sensitivity_macc(self, include_fuel_diff=True, include_learning=True):
        """
        Calculate MACC with sensitivity flags

        Args:
            include_fuel_diff: If False, set fuel cost differential to 0
            include_learning: If False, use 2025 CAPEX for all years
        """
        # Load data
        from .utils import DataLoader
        loader = DataLoader(self.baseline_dir)

        # Load baseline from module 01 output
        df_baseline = pd.read_csv('outputs/module_01/baseline_2025_detailed.csv')

        df_tech_params = loader.load_technology_params()
        df_h2_prices = loader.load_h2_prices()
        df_re_prices = loader.load_re_prices()
        df_fuel_prices = pd.read_csv(self.baseline_dir / 'fuel_price_trajectory.csv')
        df_grid_emission = loader.load_grid_emissions()
        df_hp_applicability = loader.load_heat_pump_applicability()
        df_ncc_lcoe = pd.read_csv(self.baseline_dir / 'ncc_lcoe_trajectory.csv')

        # Modify parameters based on sensitivity flags
        if not include_learning:
            # Freeze CAPEX at 2025 values for all years
            df_tech_params['capex_2030_musd_per_mtco2'] = df_tech_params['capex_2025_musd_per_mtco2']
            df_tech_params['capex_2040_musd_per_mtco2'] = df_tech_params['capex_2025_musd_per_mtco2']
            df_tech_params['capex_2050_musd_per_mtco2'] = df_tech_params['capex_2025_musd_per_mtco2']

        # Initialize calculators
        from .utils import TechnologyCostCalculator, PriceCalculator
        tech_cost_calc = TechnologyCostCalculator(df_tech_params)
        price_calc = PriceCalculator(df_h2_prices, df_re_prices, df_fuel_prices)

        discount_rate = 0.08
        ef_naphtha = 0.0149  # tCO2/GJ

        macc_data = []

        for year in range(2025, 2051):
            # Get prices
            h2_price = price_calc.get_h2_price(year)
            re_price = price_calc.get_re_price(year)
            naphtha_price = df_fuel_prices[df_fuel_prices['year'] == year]['naphtha_usd_per_gj'].iloc[0]
            grid_ef = df_grid_emission[df_grid_emission['year'] == year]['grid_ef_tco2_per_mwh'].iloc[0]

            # 1. HEAT PUMP
            tech_costs = tech_cost_calc.get_technology_costs('Heat_Pump', year)

            # Calculate abatement potential
            potential_mt = 0
            for _, row in df_hp_applicability.iterrows():
                product_group = row['product_group']
                applicability = row['applicability_pct'] / 100
                df_group = df_baseline[df_baseline['product_group'] == product_group]
                fossil_emissions = (
                    df_group['emissions_naphtha_kt'].sum() +
                    df_group['emissions_lng_kt'].sum() +
                    df_group['emissions_fuel_gas_kt'].sum() +
                    df_group['emissions_lpg_kt'].sum() +
                    df_group['emissions_fuel_oil_kt'].sum() +
                    df_group['emissions_diesel_kt'].sum()
                ) / 1000
                potential_mt += fossil_emissions * applicability

            # Calculate costs
            capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
            lifetime = tech_costs['lifetime_years']
            crf = price_calc.calculate_capital_recovery_factor(discount_rate, lifetime)
            capex_ann = capex_musd_per_mtco2 * crf
            opex_ann = capex_ann * (tech_costs['opex_pct_capex'] / 100)

            # Fuel cost differential
            cop = tech_costs['cop']
            re_price_per_gj_thermal = (re_price / 3.6) / cop
            gj_per_tco2 = 1 / ef_naphtha
            fuel_cost_diff_raw = (re_price_per_gj_thermal - naphtha_price) * gj_per_tco2

            if include_fuel_diff:
                fuel_cost_diff = fuel_cost_diff_raw
            else:
                fuel_cost_diff = max(0.0, fuel_cost_diff_raw)

            total_cost = capex_ann + opex_ann + fuel_cost_diff

            macc_data.append({
                'year': year,
                'technology': 'Heat_Pump',
                'available': tech_costs['available'],
                'abatement_potential_mtco2': potential_mt,
                'capex_ann_usd_per_tco2': capex_ann,
                'opex_ann_usd_per_tco2': opex_ann,
                'fuel_cost_diff_usd_per_tco2': fuel_cost_diff,
                'total_cost_usd_per_tco2': total_cost,
                're_price_usd_per_mwh': re_price,
                'h2_price_usd_per_kg': h2_price,
            })

            # 2. NCC-H2 (LCOE-based - fuel diff included in LCOE)
            ncc_h2_macc = self._calculate_ncc_h2_sensitivity(
                year, df_ncc_lcoe, tech_cost_calc, price_calc, discount_rate
            )
            macc_data.append(ncc_h2_macc)

            # 3. NCC-Electricity (LCOE-based)
            ncc_elec_macc = self._calculate_ncc_elec_sensitivity(
                year, df_ncc_lcoe, tech_cost_calc, price_calc, discount_rate
            )
            macc_data.append(ncc_elec_macc)

            # 4. RE PPA
            re_ppa_macc = self._calculate_re_ppa_sensitivity(
                year, df_baseline, re_price, grid_ef, include_fuel_diff
            )
            macc_data.append(re_ppa_macc)

        df_macc = pd.DataFrame(macc_data)
        return df_macc

    def _calculate_ncc_h2_sensitivity(self, year, df_ncc_lcoe, tech_cost_calc, price_calc, discount_rate):
        """Calculate NCC-H2 MACC (LCOE method, learning already in LCOE trajectory)"""
        ncc_data = df_ncc_lcoe[df_ncc_lcoe['year'] == year].iloc[0]

        lcoe_baseline = ncc_data['baseline_steam_cracker_usd_per_ton']
        lcoe_h2 = ncc_data['ncc_h2_usd_per_ton']
        ei_baseline = ncc_data['baseline_emission_intensity_tco2_per_ton']
        ei_h2 = ncc_data['ncc_h2_emission_intensity_tco2_per_ton']

        # LCOE premium method
        lcoe_premium = lcoe_h2 - lcoe_baseline
        emission_reduction = ei_baseline - ei_h2

        if emission_reduction > 0:
            macc = lcoe_premium / emission_reduction
        else:
            macc = 1e9  # Very high if no reduction

        # Abatement potential (37.6 Mt for all NCC facilities)
        potential_mt = 37.60

        tech_costs = tech_cost_calc.get_technology_costs('NCC-H2', year)

        return {
            'year': year,
            'technology': 'NCC-H2',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': potential_mt,
            'capex_ann_usd_per_tco2': 0,  # Included in LCOE
            'opex_ann_usd_per_tco2': 0,   # Included in LCOE
            'fuel_cost_diff_usd_per_tco2': 0,  # Included in LCOE
            'total_cost_usd_per_tco2': macc,
            'lcoe_baseline_usd_per_ton': lcoe_baseline,
            'lcoe_technology_usd_per_ton': lcoe_h2,
            'lcoe_premium_usd_per_ton': lcoe_premium,
            'emission_intensity_baseline': ei_baseline,
            'emission_intensity_technology': ei_h2,
            'methodology': 'LCOE-based',
        }

    def _calculate_ncc_elec_sensitivity(self, year, df_ncc_lcoe, tech_cost_calc, price_calc, discount_rate):
        """Calculate NCC-Electricity MACC"""
        ncc_data = df_ncc_lcoe[df_ncc_lcoe['year'] == year].iloc[0]

        lcoe_baseline = ncc_data['baseline_steam_cracker_usd_per_ton']
        lcoe_elec = ncc_data['ncc_electricity_usd_per_ton']
        ei_baseline = ncc_data['baseline_emission_intensity_tco2_per_ton']
        ei_elec = ncc_data['ncc_electricity_emission_intensity_tco2_per_ton']

        lcoe_premium = lcoe_elec - lcoe_baseline
        emission_reduction = ei_baseline - ei_elec

        if emission_reduction > 0:
            macc = lcoe_premium / emission_reduction
        else:
            macc = 1e9

        potential_mt = 37.60
        tech_costs = tech_cost_calc.get_technology_costs('NCC-Electricity', year)

        return {
            'year': year,
            'technology': 'NCC-Electricity',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': potential_mt,
            'capex_ann_usd_per_tco2': 0,
            'opex_ann_usd_per_tco2': 0,
            'fuel_cost_diff_usd_per_tco2': 0,
            'total_cost_usd_per_tco2': macc,
            'lcoe_baseline_usd_per_ton': lcoe_baseline,
            'lcoe_technology_usd_per_ton': lcoe_elec,
            'lcoe_premium_usd_per_ton': lcoe_premium,
            'emission_intensity_baseline': ei_baseline,
            'emission_intensity_technology': ei_elec,
            'methodology': 'LCOE-based',
        }

    def _calculate_re_ppa_sensitivity(self, year, df_baseline, re_price, grid_ef, include_fuel_diff):
        """Calculate RE PPA MACC"""
        # Abatement potential (decreases as grid decarbonizes)
        grid_electricity_mt = df_baseline['emissions_electricity_kt'].sum() / 1000
        potential_mt = grid_electricity_mt * (grid_ef / 0.45)  # Scaled to current grid EF

        # Get grid price (from fuel prices)
        # Approximate: $100/MWh (2025) → $150/MWh (2050)
        grid_price = 100 + (150 - 100) * (year - 2025) / (2050 - 2025)

        # Cost differential
        cost_diff_per_mwh_raw = re_price - grid_price

        if include_fuel_diff:
            cost_diff_per_mwh = cost_diff_per_mwh_raw
        else:
            cost_diff_per_mwh = max(0.0, cost_diff_per_mwh_raw)

        # MACC
        if grid_ef > 0:
            macc = cost_diff_per_mwh / grid_ef
        else:
            macc = 0

        return {
            'year': year,
            'technology': 'RE_PPA',
            'available': True,
            'abatement_potential_mtco2': potential_mt,
            'capex_ann_usd_per_tco2': 0,
            'opex_ann_usd_per_tco2': 0,
            'fuel_cost_diff_usd_per_tco2': (cost_diff_per_mwh / grid_ef) if grid_ef > 0 else 0,
            'total_cost_usd_per_tco2': macc,
            'grid_price_usd_per_mwh': grid_price,
            'grid_ef_tco2_per_mwh': grid_ef,
        }

    def calculate_summary_statistics(self, df_macc, scenario_name):
        """Calculate summary statistics for a scenario"""
        summary = {}

        for tech in ['Heat_Pump', 'NCC-H2', 'NCC-Electricity', 'RE_PPA']:
            tech_data = df_macc[df_macc['technology'] == tech]

            # Key years: 2030, 2040, 2050
            macc_2030 = tech_data[tech_data['year'] == 2030]['total_cost_usd_per_tco2'].iloc[0]
            macc_2040 = tech_data[tech_data['year'] == 2040]['total_cost_usd_per_tco2'].iloc[0]
            macc_2050 = tech_data[tech_data['year'] == 2050]['total_cost_usd_per_tco2'].iloc[0]

            summary[tech] = {
                '2030': round(macc_2030, 2),
                '2040': round(macc_2040, 2),
                '2050': round(macc_2050, 2),
                'avg': round(tech_data['total_cost_usd_per_tco2'].mean(), 2),
            }

        return summary

    def create_comparison_table(self, results):
        """Create comparison table across scenarios"""
        comparison_data = []

        for scenario_name, summary in results.items():
            for tech, values in summary.items():
                comparison_data.append({
                    'scenario': scenario_name,
                    'technology': tech,
                    'macc_2030': values['2030'],
                    'macc_2040': values['2040'],
                    'macc_2050': values['2050'],
                    'macc_avg': values['avg'],
                })

        df_comparison = pd.DataFrame(comparison_data)

        # Pivot for easier reading
        pivot_2030 = df_comparison.pivot(index='technology', columns='scenario', values='macc_2030')
        pivot_2050 = df_comparison.pivot(index='technology', columns='scenario', values='macc_2050')

        # Save
        output_file = self.output_dir / 'comparison_summary.csv'
        df_comparison.to_csv(output_file, index=False)
        print(f"\n   ✓ Comparison table: {output_file.name}")

        # Print summary
        print(f"\n{'='*80}")
        print("MACC COMPARISON: 2030 ($/tCO2)")
        print(f"{'='*80}")
        print(pivot_2030.to_string())

        print(f"\n{'='*80}")
        print("MACC COMPARISON: 2050 ($/tCO2)")
        print(f"{'='*80}")
        print(pivot_2050.to_string())

        return df_comparison


if __name__ == '__main__':
    analyzer = SensitivityAnalyzer()
    results = analyzer.run_all_scenarios()
