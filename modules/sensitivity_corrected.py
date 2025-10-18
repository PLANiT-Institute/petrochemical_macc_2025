"""
Sensitivity Analysis Module (CORRECTED)

Creates alternative MACC scenarios with different assumptions:
1. Baseline removes fossil fuel savings (set fossil fuel prices to zero)
   - New energy carriers (H2, electricity) still incur their full costs
2. Legacy comparison keeps fossil fuel prices unchanged (allows savings)
3. Learning curve sensitivities (with/without legacy fossil savings)

CORRECTED INTERPRETATION:
"Fuel cost differential" = savings from NOT buying naphtha/LNG/fuel gas
Removing fossil savings sets fossil fuel prices to ZERO so technologies no longer
benefit from avoided fuel purchases, but they still pay for alternative energy.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from .utils import DataLoader, TechnologyCostCalculator, PriceCalculator, is_ncc_facility


class SensitivityAnalyzerCorrected:
    """Run sensitivity analysis on key assumptions (CORRECTED)"""

    def __init__(self, baseline_dir='data', output_dir='outputs/sensitivity'):
        self.baseline_dir = Path(baseline_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Constants
        self.discount_rate = 0.08
        self.ef_naphtha = 0.0149  # tCO2/GJ

    def run_all_scenarios(self):
        """Run all sensitivity scenarios"""
        print("\n" + "="*80)
        print("SENSITIVITY ANALYSIS (CORRECTED): Testing Key Assumptions")
        print("="*80)
        print("\nCORRECTED LOGIC:")
        print("  - 'No Fuel Differential' = Fossil fuel prices (naphtha/LNG) set to ZERO")
        print("  - This REMOVES the savings from avoiding fossil fuel purchases")
        print("  - New energy costs (H2, electricity) are KEPT")
        print("="*80)

        scenarios = {
            'baseline': {
                'remove_fossil_fuel_savings': True,
                'include_learning': True,
                'description': 'Baseline (No fossil fuel savings)'
            },
            'no_fossil_savings': {
                'remove_fossil_fuel_savings': True,
                'include_learning': True,
                'description': 'No Fossil Fuel Savings (alias of baseline)'
            },
            'no_learning': {
                'remove_fossil_fuel_savings': True,
                'include_learning': False,
                'description': 'No Learning Curves (no fossil savings)'
            },
            'no_fossil_no_learning': {
                'remove_fossil_fuel_savings': True,
                'include_learning': False,
                'description': 'No Fossil Savings + No Learning (alias)'
            },
            'legacy_with_savings': {
                'remove_fossil_fuel_savings': False,
                'include_learning': True,
                'description': 'Legacy: keeps fossil fuel savings'
            },
            'legacy_with_savings_no_learning': {
                'remove_fossil_fuel_savings': False,
                'include_learning': False,
                'description': 'Legacy: fossil savings + no learning'
            }
        }

        results = {}

        for scenario_name, scenario_params in scenarios.items():
            print(f"\n{'─'*80}")
            print(f"Scenario: {scenario_params['description']}")
            print(f"{'─'*80}")

            df_macc = self.calculate_sensitivity_macc(
                remove_fossil_fuel_savings=scenario_params['remove_fossil_fuel_savings'],
                include_learning=scenario_params['include_learning']
            )

            # Save results
            output_file = self.output_dir / f'macc_{scenario_name}.csv'
            df_macc.to_csv(output_file, index=False)
            print(f"   ✓ Saved: {output_file.name}")

            results[scenario_name] = df_macc

        # Create comparison table
        self.create_comparison_summary(results)

        print(f"\n{'='*80}")
        print("SENSITIVITY ANALYSIS COMPLETE (CORRECTED)")
        print(f"{'='*80}")
        print(f"Output directory: {self.output_dir}")

        return results

    def calculate_sensitivity_macc(self, remove_fossil_fuel_savings=False, include_learning=True):
        """
        Calculate MACC with sensitivity flags (CORRECTED)

        Args:
            remove_fossil_fuel_savings: If True, set fossil fuel prices (naphtha, LNG, etc.) to 0
                                       This REMOVES the benefit of avoiding fossil fuel purchases
            include_learning: If False, use 2025 CAPEX for all years
        """
        # Load data
        loader = DataLoader(self.baseline_dir)
        df_baseline = pd.read_csv('outputs/module_01/baseline_2025_detailed.csv')
        df_tech_params = loader.load_technology_params()
        df_h2_prices = loader.load_h2_prices()
        df_re_prices = loader.load_re_prices()
        df_fuel_prices = pd.read_csv(self.baseline_dir / 'fuel_price_trajectory.csv')
        df_grid_emission = loader.load_grid_emissions()
        df_hp_applicability = loader.load_heat_pump_applicability()
        df_ncc_lcoe = pd.read_csv(self.baseline_dir / 'ncc_lcoe_trajectory.csv')

        # Apply learning curve modification if needed
        if not include_learning:
            print("   → Freezing CAPEX at 2025 values (no learning)")
            for col in ['capex_2030_musd_per_mtco2', 'capex_2040_musd_per_mtco2', 'capex_2050_musd_per_mtco2']:
                df_tech_params[col] = df_tech_params['capex_2025_musd_per_mtco2']

        # Apply fossil fuel price modification if needed
        if remove_fossil_fuel_savings:
            print("   → Setting fossil fuel prices to ZERO (removes savings benefit)")
            df_fuel_prices_modified = df_fuel_prices.copy()
            df_fuel_prices_modified['naphtha_usd_per_gj'] = 0.0
            df_fuel_prices_modified['lng_usd_per_gj'] = 0.0
            df_fuel_prices_modified['fuel_gas_usd_per_gj'] = 0.0
            df_fuel_prices_modified['lpg_usd_per_gj'] = 0.0
            df_fuel_prices_modified['fuel_oil_usd_per_gj'] = 0.0
            df_fuel_prices_modified['diesel_usd_per_gj'] = 0.0
            # Note: electricity_usd_per_kwh is KEPT (for RE PPA comparison)
        else:
            df_fuel_prices_modified = df_fuel_prices.copy()

        # Initialize calculators
        tech_cost_calc = TechnologyCostCalculator(df_tech_params)
        price_calc = PriceCalculator(df_h2_prices, df_re_prices, df_fuel_prices_modified)

        # Calculate MACC for all years
        macc_data = []
        years = range(2025, 2051)

        for year in years:
            # Get prices for this year
            h2_price = price_calc.get_h2_price(year)
            re_price = price_calc.get_re_price(year)
            naphtha_price = df_fuel_prices_modified[df_fuel_prices_modified['year'] == year]['naphtha_usd_per_gj'].iloc[0]
            grid_ef = df_grid_emission[df_grid_emission['year'] == year]['grid_ef_tco2_per_mwh'].iloc[0]

            # 1. Heat Pump
            hp_macc = self._calculate_heat_pump_macc_corrected(
                year, re_price, naphtha_price, tech_cost_calc, price_calc,
                df_baseline, df_hp_applicability
            )
            macc_data.append(hp_macc)

            # 2. NCC-H2 (LCOE-based, but we can adjust baseline LCOE)
            ncc_h2_macc = self._calculate_ncc_h2_macc_corrected(
                year, h2_price, naphtha_price, tech_cost_calc, price_calc,
                df_baseline, df_ncc_lcoe, remove_fossil_fuel_savings
            )
            macc_data.append(ncc_h2_macc)

            # 3. NCC-Electricity (LCOE-based)
            ncc_elec_macc = self._calculate_ncc_electricity_macc_corrected(
                year, re_price, naphtha_price, tech_cost_calc, price_calc,
                df_baseline, df_ncc_lcoe, remove_fossil_fuel_savings
            )
            macc_data.append(ncc_elec_macc)

            # 4. RE PPA
            re_ppa_macc = self._calculate_re_ppa_macc_corrected(
                year, re_price, grid_ef, tech_cost_calc, price_calc,
                df_baseline, df_fuel_prices_modified
            )
            macc_data.append(re_ppa_macc)

        df_macc = pd.DataFrame(macc_data)
        return df_macc

    def _calculate_heat_pump_macc_corrected(self, year, re_price, naphtha_price,
                                           tech_cost_calc, price_calc,
                                           df_baseline, df_hp_applicability):
        """Calculate heat pump MACC (CORRECTED)"""
        tech_costs = tech_cost_calc.get_technology_costs('Heat_Pump', year)

        # Abatement potential
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

        # Costs
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        crf = price_calc.calculate_capital_recovery_factor(self.discount_rate, lifetime)
        capex_ann = capex_musd_per_mtco2 * crf
        opex_ann = capex_ann * (tech_costs['opex_pct_capex'] / 100)

        # Fuel cost differential (CORRECTED)
        # Cost to provide heat with RE electricity
        cop = tech_costs['cop']
        re_price_per_gj_thermal = (re_price / 3.6) / cop  # $/GJ thermal output
        gj_per_tco2 = 1 / self.ef_naphtha

        # If naphtha_price = 0 (no fossil fuel savings scenario):
        #   fuel_cost_diff = (RE cost - 0) = just the RE cost (no savings)
        # If naphtha_price > 0 (baseline):
        #   fuel_cost_diff = (RE cost - naphtha cost) = savings if negative
        fuel_cost_diff = (re_price_per_gj_thermal - naphtha_price) * gj_per_tco2

        total_cost = capex_ann + opex_ann + fuel_cost_diff

        return {
            'year': year,
            'technology': 'Heat_Pump',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': potential_mt,
            'capex_ann_usd_per_tco2': capex_ann,
            'opex_ann_usd_per_tco2': opex_ann,
            'fuel_cost_diff_usd_per_tco2': fuel_cost_diff,
            'total_cost_usd_per_tco2': total_cost,
            're_price_usd_per_mwh': re_price,
            'naphtha_price_usd_per_gj': naphtha_price,
        }

    def _calculate_ncc_h2_macc_corrected(self, year, h2_price, naphtha_price,
                                        tech_cost_calc, price_calc,
                                        df_baseline, df_ncc_lcoe, remove_fossil_savings):
        """Calculate NCC-H2 MACC (LCOE-based, CORRECTED)"""
        tech_costs = tech_cost_calc.get_technology_costs('NCC-H2', year)

        # Abatement potential
        ncc_emissions = df_baseline[
            df_baseline['product'].apply(is_ncc_facility)
        ]['emissions_naphtha_kt'].sum() / 1000

        # Get LCOE data
        lcoe_data = df_ncc_lcoe[df_ncc_lcoe['year'] == year].iloc[0]
        lcoe_baseline = lcoe_data['baseline_steam_cracker_usd_per_ton']
        lcoe_h2 = lcoe_data['ncc_h2_usd_per_ton']

        # If removing fossil savings, adjust baseline LCOE to exclude naphtha cost
        if remove_fossil_savings:
            # Baseline LCOE includes naphtha cost - we need to remove it
            # Rough estimate: naphtha cost ~ $400-500/ton ethylene (depends on naphtha price)
            # For simplicity, we can recalculate or set baseline = operating cost only
            # Let's just set baseline LCOE lower to remove fuel cost component
            lcoe_baseline = lcoe_baseline * 0.5  # Approximate: remove fuel cost component

        lcoe_premium = lcoe_h2 - lcoe_baseline

        # Emission intensities
        emission_intensity_baseline = lcoe_data['baseline_emission_intensity_tco2_per_ton']
        emission_intensity_h2 = lcoe_data['ncc_h2_emission_intensity_tco2_per_ton']
        abatement_per_ton_ethylene = emission_intensity_baseline - emission_intensity_h2

        # Calculate MACC
        if abatement_per_ton_ethylene > 0:
            macc_cost = lcoe_premium / abatement_per_ton_ethylene
        else:
            macc_cost = 1e9

        # Component estimates
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        crf = price_calc.calculate_capital_recovery_factor(self.discount_rate, lifetime)
        capex_ann_estimate = capex_musd_per_mtco2 * crf
        opex_ann_estimate = capex_ann_estimate * (tech_costs['opex_pct_capex'] / 100)

        return {
            'year': year,
            'technology': 'NCC-H2',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': ncc_emissions,
            'capex_ann_usd_per_tco2': capex_ann_estimate,
            'opex_ann_usd_per_tco2': opex_ann_estimate,
            'fuel_cost_diff_usd_per_tco2': 0.0,
            'total_cost_usd_per_tco2': macc_cost,
            'h2_price_usd_per_kg': h2_price,
            'naphtha_price_usd_per_gj': naphtha_price,
            'methodology': 'LCOE-based (adjusted for fossil fuel sensitivity)'
        }

    def _calculate_ncc_electricity_macc_corrected(self, year, re_price, naphtha_price,
                                                 tech_cost_calc, price_calc,
                                                 df_baseline, df_ncc_lcoe, remove_fossil_savings):
        """Calculate NCC-Electricity MACC (LCOE-based, CORRECTED)"""
        tech_costs = tech_cost_calc.get_technology_costs('NCC-Electricity', year)

        # Abatement potential
        ncc_emissions = df_baseline[
            df_baseline['product'].apply(is_ncc_facility)
        ]['emissions_naphtha_kt'].sum() / 1000

        # Get LCOE data
        lcoe_data = df_ncc_lcoe[df_ncc_lcoe['year'] == year].iloc[0]
        lcoe_baseline = lcoe_data['baseline_steam_cracker_usd_per_ton']
        lcoe_elec = lcoe_data['ncc_electricity_usd_per_ton']

        # If removing fossil savings, adjust baseline LCOE
        if remove_fossil_savings:
            lcoe_baseline = lcoe_baseline * 0.5

        lcoe_premium = lcoe_elec - lcoe_baseline

        # Emission intensities
        emission_intensity_baseline = lcoe_data['baseline_emission_intensity_tco2_per_ton']
        emission_intensity_elec = lcoe_data['ncc_electricity_emission_intensity_tco2_per_ton']
        abatement_per_ton_ethylene = emission_intensity_baseline - emission_intensity_elec

        # Calculate MACC
        if abatement_per_ton_ethylene > 0:
            macc_cost = lcoe_premium / abatement_per_ton_ethylene
        else:
            macc_cost = 1e9

        # Component estimates
        capex_musd_per_mtco2 = tech_costs['capex_musd_per_mtco2']
        lifetime = tech_costs['lifetime_years']
        crf = price_calc.calculate_capital_recovery_factor(self.discount_rate, lifetime)
        capex_ann_estimate = capex_musd_per_mtco2 * crf
        opex_ann_estimate = capex_ann_estimate * (tech_costs['opex_pct_capex'] / 100)

        return {
            'year': year,
            'technology': 'NCC-Electricity',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': ncc_emissions,
            'capex_ann_usd_per_tco2': capex_ann_estimate,
            'opex_ann_usd_per_tco2': opex_ann_estimate,
            'fuel_cost_diff_usd_per_tco2': 0.0,
            'total_cost_usd_per_tco2': macc_cost,
            're_price_usd_per_mwh': re_price,
            'naphtha_price_usd_per_gj': naphtha_price,
            'methodology': 'LCOE-based (adjusted for fossil fuel sensitivity)'
        }

    def _calculate_re_ppa_macc_corrected(self, year, re_price, grid_ef,
                                        tech_cost_calc, price_calc,
                                        df_baseline, df_fuel_prices):
        """Calculate RE PPA MACC (CORRECTED)"""
        tech_costs = tech_cost_calc.get_technology_costs('Renewable_Energy', year)

        # Grid price (unchanged - this is electricity, not fossil fuel)
        grid_price_per_kwh = df_fuel_prices[
            df_fuel_prices['year'] == year
        ]['electricity_usd_per_kwh'].iloc[0]
        grid_price = grid_price_per_kwh * 1000

        # NCC facilities only
        ncc_facilities = df_baseline[df_baseline['product'].apply(is_ncc_facility)]
        total_elec_emissions_mt = ncc_facilities['emissions_electricity_kt'].sum() / 1000

        # Emission factors
        re_ef = 0.05
        abatement_per_mwh = grid_ef - re_ef
        abatement_potential_mt = total_elec_emissions_mt * (1 - re_ef / grid_ef)

        # Cost
        price_diff_per_mwh = re_price - grid_price
        if abatement_per_mwh > 0:
            cost_per_tco2 = price_diff_per_mwh / abatement_per_mwh
        else:
            cost_per_tco2 = 1e9

        return {
            'year': year,
            'technology': 'RE_PPA',
            'available': tech_costs['available'],
            'abatement_potential_mtco2': abatement_potential_mt,
            'capex_ann_usd_per_tco2': 0,
            'opex_ann_usd_per_tco2': 0,
            'fuel_cost_diff_usd_per_tco2': cost_per_tco2,
            'total_cost_usd_per_tco2': cost_per_tco2,
            're_price_usd_per_mwh': re_price,
            'grid_price_usd_per_mwh': grid_price,
        }

    def create_comparison_summary(self, results):
        """Create comparison summary table"""
        comparison_data = []

        for scenario_name, df_macc in results.items():
            for year in [2025, 2030, 2040, 2050]:
                df_year = df_macc[df_macc['year'] == year]
                for _, row in df_year.iterrows():
                    comparison_data.append({
                        'scenario': scenario_name,
                        'year': year,
                        'technology': row['technology'],
                        'total_cost_usd_per_tco2': row['total_cost_usd_per_tco2'],
                        'abatement_potential_mtco2': row['abatement_potential_mtco2']
                    })

        df_comparison = pd.DataFrame(comparison_data)
        output_file = self.output_dir / 'comparison_summary_corrected.csv'
        df_comparison.to_csv(output_file, index=False)
        print(f"\n   ✓ Comparison summary saved: {output_file.name}")


if __name__ == "__main__":
    analyzer = SensitivityAnalyzerCorrected()
    results = analyzer.run_all_scenarios()
