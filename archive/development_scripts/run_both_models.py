#!/usr/bin/env python3
"""
Korean Petrochemical MACC Models Comparison
Run both simulation and optimization models and compare results
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import subprocess
import sys

def run_simulation_model():
    """Run the simulation model"""
    print("🔄 Running Simulation Model...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, "run_simulation_model.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Simulation model completed successfully!")
            return True
        else:
            print("❌ Simulation model failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Simulation model timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running simulation model: {e}")
        return False

def run_optimization_model():
    """Run the optimization model"""
    print("\n🔄 Running Optimization Model...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, "run_optimization_model_v2.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Optimization model completed successfully!")
            return True
        else:
            print("❌ Optimization model failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Optimization model timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running optimization model: {e}")
        return False

def compare_model_results():
    """Compare results from both models"""
    
    print("\n📊 Comparing Model Results...")
    print("=" * 50)
    
    # Load results
    output_dir = Path("outputs")
    
    # Simulation results
    sim_file = output_dir / "emission_pathway_2023_2050.csv"
    opt_file = output_dir / "optimization_pathway_v2.csv"
    
    if not sim_file.exists():
        print("❌ Simulation results not found!")
        return
        
    if not opt_file.exists():
        print("❌ Optimization results not found!")
        return
    
    sim_df = pd.read_csv(sim_file)
    opt_df = pd.read_csv(opt_file)
    
    # Key comparison years
    comparison_years = [2030, 2040, 2050]
    
    print("\n🎯 KEY PERFORMANCE INDICATORS:")
    print("=" * 70)
    print(f"{'Year':<8} {'Metric':<25} {'Simulation':<15} {'Optimization':<15} {'Difference':<12}")
    print("-" * 70)
    
    baseline = sim_df['BaselineEmissions_MtCO2'].iloc[0]
    
    for year in comparison_years:
        sim_row = sim_df[sim_df['Year'] == year]
        opt_row = opt_df[opt_df['Year'] == year]
        
        if not sim_row.empty and not opt_row.empty:
            # Emissions
            sim_emissions = sim_row['TotalEmissions_MtCO2'].iloc[0]
            opt_emissions = opt_row['OptimizedEmissions_MtCO2'].iloc[0]
            
            print(f"{year:<8} {'Emissions (MtCO2)':<25} {sim_emissions:<15.1f} {opt_emissions:<15.1f} {opt_emissions-sim_emissions:<+12.1f}")
            
            # Reduction percentage
            sim_reduction_pct = (baseline - sim_emissions) / baseline * 100
            opt_reduction_pct = (baseline - opt_emissions) / baseline * 100
            
            print(f"{'':<8} {'Reduction (%)':<25} {sim_reduction_pct:<15.1f} {opt_reduction_pct:<15.1f} {opt_reduction_pct-sim_reduction_pct:<+12.1f}")
            
            # Investment
            sim_investment = sim_row['CumulativeInvestment_Billion_USD'].iloc[0]
            opt_investment = opt_row['CumulativeInvestment_Billion_USD'].iloc[0]
            
            print(f"{'':<8} {'Investment (Billion USD)':<25} {sim_investment:<15.1f} {opt_investment:<15.1f} {opt_investment-sim_investment:<+12.1f}")
            
            # Cost per tonne avoided
            sim_reduction = sim_row['EmissionReduction_MtCO2'].iloc[0] if 'EmissionReduction_MtCO2' in sim_row else baseline - sim_emissions
            opt_reduction = opt_row['EmissionReduction_MtCO2'].iloc[0]
            
            if sim_reduction > 0:
                sim_cost_per_t = sim_investment * 1000 / sim_reduction  # Million USD / MtCO2 = USD/tCO2
            else:
                sim_cost_per_t = 0
                
            if opt_reduction > 0:
                opt_cost_per_t = opt_investment * 1000 / opt_reduction
            else:
                opt_cost_per_t = 0
            
            print(f"{'':<8} {'Cost (USD/tCO2)':<25} {sim_cost_per_t:<15.0f} {opt_cost_per_t:<15.0f} {opt_cost_per_t-sim_cost_per_t:<+12.0f}")
            print("-" * 70)
    
    # Model characteristics comparison
    print("\n📋 MODEL CHARACTERISTICS:")
    print("=" * 70)
    print(f"{'Aspect':<30} {'Simulation Model':<20} {'Optimization Model'}")
    print("-" * 70)
    print(f"{'Approach':<30} {'Heuristic Rules':<20} {'Linear Programming'}")
    print(f"{'Objective':<30} {'Technology Ramp-up':<20} {'Cost Minimization'}")
    print(f"{'Emission Targets':<30} {'Reference Only':<20} {'Hard Constraints'}")
    print(f"{'Technology Selection':<30} {'Cost Threshold':<20} {'Optimal Portfolio'}")
    print(f"{'Time Resolution':<30} {'Annual':<20} {'Key Years'}")
    print(f"{'Computational Speed':<30} {'Fast':<20} {'Medium'}")
    print(f"{'Deployment Logic':<30} {'Gradual Ramp':<20} {'Target-Driven'}")
    
    # Create detailed comparison plot
    create_detailed_comparison_plot(sim_df, opt_df, baseline)
    
    print(f"\n✅ Comparison completed! Check outputs/ for detailed comparison plots.")

def create_detailed_comparison_plot(sim_df, opt_df, baseline):
    """Create a detailed comparison plot between both models"""
    
    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(24, 16))
    
    # 1. Emission Pathways
    ax1.plot(sim_df['Year'], sim_df['BaselineEmissions_MtCO2'], 
             'k--', linewidth=2, label='Baseline', alpha=0.7)
    ax1.plot(sim_df['Year'], sim_df['TotalEmissions_MtCO2'], 
             'b-', linewidth=3, label='Simulation Model')
    ax1.plot(opt_df['Year'], opt_df['OptimizedEmissions_MtCO2'], 
             'r-', linewidth=3, label='Optimization Model', alpha=0.8)
    
    # Add targets
    targets = {2030: baseline * 0.85, 2040: baseline * 0.50, 2050: baseline * 0.20}
    for year, target in targets.items():
        ax1.scatter(year, target, color='orange', s=100, zorder=5)
        ax1.annotate(f'{int((baseline-target)/baseline*100)}%', (year, target), 
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Emissions (MtCO2/year)')
    ax1.set_title('Emission Pathways Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 26)
    
    # 2. Emission Reductions
    sim_reductions = sim_df['BaselineEmissions_MtCO2'] - sim_df['TotalEmissions_MtCO2']
    ax2.plot(sim_df['Year'], sim_reductions, 'b-', linewidth=3, label='Simulation')
    ax2.plot(opt_df['Year'], opt_df['EmissionReduction_MtCO2'], 'r-', linewidth=3, label='Optimization')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Emission Reduction (MtCO2/year)')
    ax2.set_title('Emission Reduction Achievement')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Investment Requirements
    ax3.plot(sim_df['Year'], sim_df['CumulativeInvestment_Billion_USD'], 
             'b-', linewidth=3, label='Simulation')
    ax3.plot(opt_df['Year'], opt_df['CumulativeInvestment_Billion_USD'], 
             'r-', linewidth=3, label='Optimization')
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Cumulative Investment (Billion USD)')
    ax3.set_title('Investment Requirements')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Cost Effectiveness
    sim_cost_eff = []
    for _, row in sim_df.iterrows():
        reduction = row['BaselineEmissions_MtCO2'] - row['TotalEmissions_MtCO2']
        if reduction > 0:
            cost_eff = row['CumulativeInvestment_Billion_USD'] * 1000 / reduction  # USD/tCO2
        else:
            cost_eff = 0
        sim_cost_eff.append(cost_eff)
    
    opt_cost_eff = []
    for _, row in opt_df.iterrows():
        if row['EmissionReduction_MtCO2'] > 0:
            cost_eff = row['CumulativeInvestment_Billion_USD'] * 1000 / row['EmissionReduction_MtCO2']
        else:
            cost_eff = 0
        opt_cost_eff.append(cost_eff)
    
    ax4.plot(sim_df['Year'], sim_cost_eff, 'b-', linewidth=3, label='Simulation')
    ax4.plot(opt_df['Year'], opt_cost_eff, 'r-', linewidth=3, label='Optimization')
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Investment per tCO2 Reduced (USD/tCO2)')
    ax4.set_title('Cost Effectiveness Comparison')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(0, 5000)
    
    # 5. Emission Reduction Rate (Year-over-Year)
    sim_reduction_rate = sim_reductions.diff()
    opt_reduction_rate = opt_df['EmissionReduction_MtCO2'].diff()
    
    ax5.plot(sim_df['Year'][1:], sim_reduction_rate[1:], 'b-', linewidth=3, label='Simulation')
    ax5.plot(opt_df['Year'][1:], opt_reduction_rate[1:], 'r-', linewidth=3, label='Optimization')
    ax5.set_xlabel('Year')
    ax5.set_ylabel('Annual Reduction Rate (MtCO2/year²)')
    ax5.set_title('Decarbonization Speed')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Model Performance Summary (Bar Chart)
    years = [2030, 2040, 2050]
    sim_emissions_by_year = []
    opt_emissions_by_year = []
    targets_by_year = []
    
    for year in years:
        sim_row = sim_df[sim_df['Year'] == year]
        opt_row = opt_df[opt_df['Year'] == year]
        
        if not sim_row.empty and not opt_row.empty:
            sim_emissions_by_year.append(sim_row['TotalEmissions_MtCO2'].iloc[0])
            opt_emissions_by_year.append(opt_row['OptimizedEmissions_MtCO2'].iloc[0])
            targets_by_year.append(targets[year])
    
    x = np.arange(len(years))
    width = 0.25
    
    ax6.bar(x - width, sim_emissions_by_year, width, label='Simulation', color='blue', alpha=0.7)
    ax6.bar(x, opt_emissions_by_year, width, label='Optimization', color='red', alpha=0.7)
    ax6.bar(x + width, targets_by_year, width, label='Targets', color='orange', alpha=0.7)
    
    ax6.set_xlabel('Year')
    ax6.set_ylabel('Emissions (MtCO2/year)')
    ax6.set_title('Target Achievement Comparison')
    ax6.set_xticks(x)
    ax6.set_xticklabels(years)
    ax6.legend()
    ax6.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('outputs/detailed_model_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Main comparison function"""
    
    print("🏭 Korean Petrochemical MACC Models Comparison")
    print("=" * 60)
    print("Running both Simulation and Optimization models for comparison")
    
    # Run both models
    sim_success = run_simulation_model()
    opt_success = run_optimization_model()
    
    # Compare results if both succeeded
    if sim_success and opt_success:
        compare_model_results()
    else:
        print("\n❌ Cannot compare results - one or both models failed!")
        if not sim_success:
            print("   - Simulation model failed")
        if not opt_success:
            print("   - Optimization model failed")

if __name__ == "__main__":
    main()