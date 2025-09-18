#!/usr/bin/env python3
"""
Command-line interface for the Korea Petrochemical MACC model
"""

import click
import sys
from pathlib import Path
from typing import Optional

# Add lib to path for imports
from .lib import (
    DataLoader, DataValidator, TechnologyPortfolio, EmissionsScenario
)
from .lib.optimization.model_builder import MACCModelBuilder
from .lib.analysis.results import ModelResults
from .lib.visualization.charts import MACCVisualizer

@click.group()
@click.version_option()
def cli():
    """Korea Petrochemical MACC (Marginal Abatement Cost Curve) Model"""
    pass

@cli.command()
@click.option('--data-dir', type=str, help='Directory containing data files')
@click.option('--output-dir', type=str, default='outputs', help='Output directory for results')
def validate(data_dir: Optional[str], output_dir: str):
    """Validate input data files"""
    click.echo("🔍 Validating MACC model data...")
    
    try:
        loader = DataLoader(data_dir)
        
        # Load and validate excel data
        excel_data = {}
        macc_file = Path(loader.data_dir) / "Korea_Petrochemical_MACC_Database.xlsx"
        
        if not macc_file.exists():
            click.echo(f"❌ MACC database file not found: {macc_file}")
            sys.exit(1)
        
        import pandas as pd
        with pd.ExcelFile(macc_file) as xls:
            for sheet_name in xls.sheet_names:
                excel_data[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
        
        # Validate Excel structure
        from .lib.data.validators import DataValidator
        excel_validation = DataValidator.validate_excel_data(excel_data)
        
        click.echo(f"📊 Excel validation: {'✅ PASS' if excel_validation.valid else '❌ FAIL'}")
        
        for warning in excel_validation.warnings:
            click.echo(f"  ⚠️  {warning}")
        
        for error in excel_validation.errors:
            click.echo(f"  ❌ {error}")
        
        # Load and validate portfolio
        portfolio = loader.load_technology_portfolio()
        portfolio_validation = DataValidator.validate_portfolio(portfolio)
        
        click.echo(f"🔧 Portfolio validation: {'✅ PASS' if portfolio_validation.valid else '❌ FAIL'}")
        click.echo(f"   Technologies loaded: {len(portfolio.technologies)}")
        
        for warning in portfolio_validation.warnings:
            click.echo(f"  ⚠️  {warning}")
        
        for error in portfolio_validation.errors:
            click.echo(f"  ❌ {error}")
        
        # Load and validate scenario
        scenario = loader.load_emissions_scenario()
        scenario_validation = DataValidator.validate_scenario(scenario)
        
        click.echo(f"📈 Scenario validation: {'✅ PASS' if scenario_validation.valid else '❌ FAIL'}")
        
        for warning in scenario_validation.warnings:
            click.echo(f"  ⚠️  {warning}")
        
        for error in scenario_validation.errors:
            click.echo(f"  ❌ {error}")
        
        # Overall validation
        overall_valid = excel_validation.valid and portfolio_validation.valid and scenario_validation.valid
        
        if overall_valid:
            click.echo("🎉 All validations passed! Data is ready for optimization.")
        else:
            click.echo("⚠️  Some validations failed. Please check errors above.")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--data-dir', type=str, help='Directory containing data files')
@click.option('--output-dir', type=str, default='outputs', help='Output directory for results')
@click.option('--discount-rate', type=float, default=0.05, help='Annual discount rate')
@click.option('--allow-slack/--no-slack', default=True, help='Allow emissions shortfalls')
@click.option('--slack-penalty', type=float, default=1e15, help='Penalty for shortfalls (USD/tCO2)')
@click.option('--solver', type=str, default='auto', help='Solver to use (highs|glpk|cbc|auto)')
@click.option('--generate-charts/--no-charts', default=True, help='Generate visualization charts')
def optimize(data_dir: Optional[str], output_dir: str, discount_rate: float, 
            allow_slack: bool, slack_penalty: float, solver: str, generate_charts: bool):
    """Run MACC optimization model"""
    
    click.echo("🚀 Running Korea Petrochemical MACC optimization...")
    
    try:
        # Load data
        click.echo("📂 Loading data...")
        loader = DataLoader(data_dir)
        portfolio = loader.load_technology_portfolio()
        scenario = loader.load_emissions_scenario()
        
        click.echo(f"   Loaded {len(portfolio.technologies)} technologies")
        click.echo(f"   Timeline: {min(scenario.timeline)} - {max(scenario.timeline)}")
        
        # Build model
        click.echo("🔧 Building optimization model...")
        model_builder = MACCModelBuilder(scenario, portfolio)
        model = model_builder.build_model(
            allow_slack=allow_slack,
            slack_penalty=slack_penalty,
            discount_rate=discount_rate
        )
        
        summary = model_builder.get_model_summary()
        click.echo(f"   Variables: {sum(summary['variables'].values())}")
        click.echo(f"   Constraints: {sum(summary['constraints'].values())}")
        
        # Solve model
        click.echo("⚡ Solving optimization model...")
        from pyomo.opt import SolverFactory
        
        # Try solvers in order
        solvers_to_try = [solver] if solver != 'auto' else ['highs', 'glpk', 'cbc']
        solver_used = None
        results = None
        
        for solver_name in solvers_to_try:
            try:
                opt = SolverFactory(solver_name)
                results = opt.solve(model, tee=False)
                solver_used = solver_name
                click.echo(f"   Solved with {solver_used}: {results.solver.termination_condition}")
                break
            except Exception as e:
                click.echo(f"   Failed with {solver_name}: {e}")
                continue
        
        if not solver_used:
            click.echo("❌ No suitable solver found!")
            sys.exit(1)
        
        # Extract results
        click.echo("📊 Extracting results...")
        model_results = ModelResults(model, portfolio, scenario, str(results.solver.termination_condition))
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate reports
        deployment_df = model_results.extract_deployment_plan()
        annual_summary_df = model_results.extract_annual_summary()
        cost_metrics = model_results.calculate_system_cost(discount_rate)
        
        # Save to CSV
        deployment_df.to_csv(output_path / 'deployment_plan.csv', index=False)
        annual_summary_df.to_csv(output_path / 'annual_summary.csv', index=False)
        
        # Print summary
        click.echo("📈 Optimization Results:")
        click.echo(f"   Total NPV Cost: ${cost_metrics['total_npv_cost_million_usd']:.1f} Million")
        click.echo(f"   Total Abatement: {cost_metrics['total_abatement_tco2']/1e6:.1f} MtCO2")
        click.echo(f"   Average Cost: ${cost_metrics['average_cost_per_tco2_usd']:.1f}/tCO2")
        
        # Generate charts
        if generate_charts:
            click.echo("📊 Generating charts...")
            visualizer = MACCVisualizer(output_dir)
            
            # MACC curve for 2030
            if 2030 in scenario.timeline:
                macc_2030 = model_results.generate_macc_curve(2030)
                if not macc_2030.empty:
                    visualizer.plot_macc_curve(macc_2030, 2030, "MACC Curve 2030")
            
            # Deployment timeline
            if not deployment_df.empty:
                visualizer.plot_deployment_timeline(deployment_df)
            
            # Cost breakdown
            visualizer.plot_cost_breakdown(annual_summary_df)
            
            click.echo(f"   Charts saved to {output_path}")
        
        click.echo(f"✅ Optimization complete! Results saved to {output_path}")
        
    except Exception as e:
        click.echo(f"❌ Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

@cli.command()
@click.option('--data-dir', type=str, help='Directory containing data files')
def info(data_dir: Optional[str]):
    """Show information about the MACC model data"""
    
    try:
        loader = DataLoader(data_dir)
        portfolio = loader.load_technology_portfolio()
        scenario = loader.load_emissions_scenario()
        
        click.echo("ℹ️  Korea Petrochemical MACC Model Information")
        click.echo("=" * 50)
        
        # Portfolio info
        summary = portfolio.get_portfolio_summary()
        click.echo("🔧 Technology Portfolio:")
        click.echo(f"   Total Technologies: {summary['total_technologies']}")
        click.echo(f"   - Transitions: {summary['transitions']}")
        click.echo(f"   - Alternatives: {summary['alternatives']}")
        click.echo(f"   Processes Covered: {', '.join(summary['process_types'])}")
        click.echo(f"   Cost Range: ${summary['min_lcoa_usd_per_tco2']:.0f} - ${summary['max_lcoa_usd_per_tco2']:.0f} per tCO2")
        
        # Scenario info
        click.echo(f"\n📈 Emissions Scenario:")
        click.echo(f"   Baseline ({scenario.baseline.year}): {scenario.baseline.total_emissions_mt:.1f} MtCO2")
        final_year = max(scenario.timeline)
        final_target = scenario.get_target_emissions(final_year)
        reduction_pct = (1 - final_target / scenario.baseline.total_emissions_mt) * 100
        click.echo(f"   Final Target ({final_year}): {final_target:.1f} MtCO2 ({reduction_pct:.1f}% reduction)")
        click.echo(f"   Timeline: {min(scenario.timeline)} - {max(scenario.timeline)}")
        
        # Process breakdown
        click.echo(f"\n🏭 Process Breakdown:")
        for process_name, baseline in scenario.baseline.process_baselines.items():
            click.echo(f"   {process_name}: {baseline.production_kt:.0f} kt, {baseline.total_emissions_mt:.1f} MtCO2")
        
        # Abatement potential
        total_potential = portfolio.calculate_total_abatement_potential(scenario)
        max_required = max(scenario.get_required_abatement(year) for year in scenario.timeline)
        click.echo(f"\n⚡ Abatement Analysis:")
        click.echo(f"   Total Technical Potential: {total_potential:.1f} MtCO2")
        click.echo(f"   Maximum Required ({max([y for y in scenario.timeline if scenario.get_required_abatement(y) == max_required])[0]}): {max_required:.1f} MtCO2")
        click.echo(f"   Feasibility Ratio: {total_potential/max_required:.1f}x")
        
    except Exception as e:
        click.echo(f"❌ Error loading model info: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli()