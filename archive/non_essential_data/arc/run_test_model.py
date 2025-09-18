#!/usr/bin/env python3
"""
Run the MACC model with test data
"""

import sys
from pathlib import Path

# Add the petrochem package to path
sys.path.insert(0, str(Path(__file__).parent))

def create_test_scenario():
    """Create a test scenario for running the model"""
    from petrochem.lib import DataLoader
    from petrochem.lib.core.scenario import EmissionsScenario, EmissionsBaseline, EmissionsTarget, ProcessBaseline
    from petrochem.lib.optimization.model_builder import MACCModelBuilder
    from petrochem.lib.analysis.results import ModelResults
    from petrochem.lib.visualization.charts import MACCVisualizer
    
    print("🚀 Running Korea Petrochemical MACC Model Test")
    print("=" * 50)
    
    # Load technology portfolio from our comprehensive Excel file
    print("📂 Loading technology portfolio...")
    loader = DataLoader()
    portfolio = loader.load_technology_portfolio()
    
    print(f"✅ Loaded {len(portfolio.technologies)} technologies")
    
    # Create realistic test scenario based on Korea's petrochemical industry
    print("📊 Creating test emissions scenario...")
    
    # Realistic baseline data for Korea's petrochemical industry
    process_baselines = [
        ProcessBaseline("NCC", 17687, 1.356, {"NCC_HT": 0.65, "NCC_MT": 0.35}),  # Naphtha Cracking
        ProcessBaseline("BTX", 20972, 0.191, {"BTX_HT": 0.50, "BTX_MT": 0.50}),  # BTX Aromatics
        ProcessBaseline("PDH", 3500, 0.8, {"PDH_HT": 0.70, "PDH_MT": 0.30}),     # Propane Dehydrogenation
        ProcessBaseline("Poly_PE", 6181, 0.169, {"Poly_PE_MT": 0.80, "Poly_PE_LT": 0.20}),  # PE Polymerization
        ProcessBaseline("Poly_PP", 4601, 0.199, {"Poly_PP_MT": 0.80, "Poly_PP_LT": 0.20}),  # PP Polymerization  
        ProcessBaseline("Utilities", 5000, 1.701, {"Utilities_HT": 0.85, "Utilities_MT": 0.15})  # Utilities
    ]
    
    baseline = EmissionsBaseline(
        year=2023,
        total_emissions_mt=50.0,  # Korea's petrochemical emissions
        process_baselines=process_baselines
    )
    
    # Net-zero pathway targets
    targets = [
        EmissionsTarget(year=2023, target_mt_co2=50.0),  # Baseline
        EmissionsTarget(year=2030, target_mt_co2=40.0),  # 20% reduction
        EmissionsTarget(year=2040, target_mt_co2=25.0),  # 50% reduction
        EmissionsTarget(year=2050, target_mt_co2=10.0),  # 80% reduction
    ]
    
    timeline = list(range(2023, 2051))
    scenario = EmissionsScenario(baseline=baseline, targets=targets, timeline=timeline)
    
    print(f"✅ Created scenario: {scenario}")
    
    # Check abatement potential
    total_potential = portfolio.calculate_total_abatement_potential(scenario)
    max_required = max(scenario.get_required_abatement(year) for year in timeline)
    
    print(f"📈 Abatement Analysis:")
    print(f"   Total Technical Potential: {total_potential:.1f} MtCO2")
    print(f"   Maximum Required: {max_required:.1f} MtCO2")
    print(f"   Feasibility Ratio: {total_potential/max_required:.1f}x")
    
    return portfolio, scenario

def run_optimization(portfolio, scenario):
    """Run the optimization model"""
    from pyomo.opt import SolverFactory
    from petrochem.lib.optimization.model_builder import MACCModelBuilder
    
    print("\n🏗️ Building optimization model...")
    
    # Build model
    model_builder = MACCModelBuilder(scenario, portfolio)
    model = model_builder.build_model(
        allow_slack=True,
        slack_penalty=1e15,  # Very high penalty to discourage shortfalls
        discount_rate=0.05
    )
    
    summary = model_builder.get_model_summary()
    print(f"✅ Model built successfully:")
    print(f"   Variables: {sum(summary['variables'].values())}")
    print(f"   Constraints: {sum(summary['constraints'].values())}")
    
    # Solve model
    print("\n⚡ Solving optimization...")
    
    solvers_to_try = ['highs', 'glpk', 'cbc']
    solver_used = None
    results = None
    
    for solver_name in solvers_to_try:
        try:
            print(f"   Trying {solver_name}...")
            opt = SolverFactory(solver_name)
            results = opt.solve(model, tee=False)
            solver_used = solver_name
            status = str(results.solver.termination_condition)
            print(f"   ✅ Solved with {solver_used}: {status}")
            break
        except Exception as e:
            print(f"   ❌ {solver_name} failed: {e}")
            continue
    
    if not solver_used:
        print("❌ No suitable solver found!")
        return None, None, None
    
    return model, results, solver_used

def analyze_results(model, results, solver_used, portfolio, scenario):
    """Analyze and display results"""
    from petrochem.lib.analysis.results import ModelResults
    
    print("\n📊 Analyzing results...")
    
    # Extract results
    model_results = ModelResults(model, portfolio, scenario, str(results.solver.termination_condition))
    
    # Get deployment plan
    deployment_df = model_results.extract_deployment_plan()
    annual_summary_df = model_results.extract_annual_summary()
    cost_metrics = model_results.calculate_system_cost()
    
    # Get new analyses
    emissions_pathway_df = model_results.get_emissions_pathway()
    production_shares_df = model_results.get_production_shares()
    
    print(f"✅ Results extracted:")
    print(f"   Technologies deployed: {len(deployment_df)}")
    print(f"   Years analyzed: {len(annual_summary_df)}")
    
    # Display key results
    print(f"\n💰 Economic Results:")
    print(f"   Total NPV Cost: ${cost_metrics['total_npv_cost_million_usd']:.0f} Million")
    print(f"   Total Abatement: {cost_metrics['total_abatement_tco2']/1e6:.1f} MtCO2")
    print(f"   Average Cost: ${cost_metrics['average_cost_per_tco2_usd']:.0f}/tCO2")
    
    # Show target achievement
    print(f"\n🎯 Target Achievement:")
    for _, row in annual_summary_df.iterrows():
        if row['Year'] in [2030, 2040, 2050]:
            achievement = "✅" if row['Target_Met'] else "❌"
            shortfall = f" (shortfall: {row['Shortfall_MtCO2']:.1f})" if row['Shortfall_MtCO2'] > 0.01 else ""
            print(f"   {row['Year']}: {row['Achieved_Abatement_MtCO2']:.1f}/{row['Required_Abatement_MtCO2']:.1f} MtCO2 {achievement}{shortfall}")
    
    # Show top technologies
    print(f"\n🔧 Top Technologies (by deployment):")
    if not deployment_df.empty:
        top_techs = deployment_df.nlargest(5, 'Deployment_kt')[['TechID', 'ProcessType', 'Year', 'Deployment_kt', 'LCOA_USD_per_tCO2']]
        for _, tech in top_techs.iterrows():
            print(f"   {tech['TechID']}: {tech['Deployment_kt']:.0f}kt in {tech['Year']} (${tech['LCOA_USD_per_tCO2']:.0f}/tCO2)")
    
    return model_results, deployment_df, annual_summary_df, emissions_pathway_df, production_shares_df

def create_visualizations(model_results, deployment_df, annual_summary_df, emissions_pathway_df, production_shares_df, scenario):
    """Create charts and save results"""
    from petrochem.lib.visualization.charts import MACCVisualizer
    
    print(f"\n📊 Creating visualizations...")
    
    # Create output directory
    output_dir = Path("outputs_test_model")
    output_dir.mkdir(exist_ok=True)
    
    # Save CSV results
    deployment_df.to_csv(output_dir / "deployment_plan.csv", index=False)
    annual_summary_df.to_csv(output_dir / "annual_summary.csv", index=False)
    emissions_pathway_df.to_csv(output_dir / "emissions_pathway.csv", index=False)
    production_shares_df.to_csv(output_dir / "production_shares.csv", index=False)
    
    print(f"✅ CSV files saved to {output_dir}/")
    
    # Create visualizations
    visualizer = MACCVisualizer(str(output_dir))
    
    try:
        # MACC curve for 2030
        if 2030 in scenario.timeline:
            macc_2030 = model_results.generate_macc_curve(2030)
            if not macc_2030.empty:
                visualizer.plot_macc_curve(macc_2030, 2030, "Korea Petrochemical MACC Curve 2030")
                print(f"   ✅ MACC curve 2030 created")
        
        # Deployment timeline
        if not deployment_df.empty:
            visualizer.plot_deployment_timeline(deployment_df)
            print(f"   ✅ Deployment timeline created")
        
        # Cost breakdown
        visualizer.plot_cost_breakdown(annual_summary_df)
        print(f"   ✅ Cost breakdown created")
        
        # NEW: Emissions pathway
        visualizer.plot_emissions_pathway(emissions_pathway_df)
        print(f"   ✅ Emissions pathway created")
        
        # NEW: Production shares for major processes
        if not production_shares_df.empty:
            major_processes = ['NCC', 'BTX', 'Utilities']
            for process in major_processes:
                if process in production_shares_df['ProcessType'].values:
                    visualizer.plot_production_shares(production_shares_df, process)
                    print(f"   ✅ Production shares for {process} created")
            
            # All processes overview
            visualizer.plot_all_production_shares(production_shares_df)
            print(f"   ✅ All production shares overview created")
        
        print(f"📈 All charts saved to {output_dir}/")
        
    except Exception as e:
        print(f"   ⚠️ Visualization error: {e}")

def main():
    """Main function"""
    try:
        # Create test scenario
        portfolio, scenario = create_test_scenario()
        
        # Run optimization
        model, results, solver_used = run_optimization(portfolio, scenario)
        
        if model is None:
            print("❌ Optimization failed!")
            return 1
        
        # Analyze results
        model_results, deployment_df, annual_summary_df, emissions_pathway_df, production_shares_df = analyze_results(
            model, results, solver_used, portfolio, scenario
        )
        
        # Create visualizations
        create_visualizations(model_results, deployment_df, annual_summary_df, emissions_pathway_df, production_shares_df, scenario)
        
        print(f"\n🎉 Model run completed successfully!")
        print(f"📁 Results saved to outputs_test_model/")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Model run failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())