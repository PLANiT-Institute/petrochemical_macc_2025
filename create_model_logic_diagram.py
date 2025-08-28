"""
Create Model Logic Diagram for Client Explanation
===============================================

Creates a comprehensive flow diagram explaining the Korean Petrochemical MACC model logic.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_model_logic_diagram():
    """Create comprehensive model logic flow diagram"""
    
    fig, ax = plt.subplots(figsize=(20, 14))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # Define colors
    colors = {
        'data': '#E8F4FD',      # Light blue
        'process': '#FFF2CC',    # Light yellow  
        'optimization': '#E1D5E7', # Light purple
        'results': '#D5E8D4',    # Light green
        'arrow': '#4472C4'       # Blue
    }
    
    # Title
    ax.text(10, 13.5, 'Korean Petrochemical MACC Model Logic Flow', 
            ha='center', va='center', fontsize=20, fontweight='bold')
    
    # 1. DATA INPUT LAYER (Top)
    data_y = 12
    
    # Facility Data
    facility_box = FancyBboxPatch((0.5, data_y-0.4), 3, 0.8, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=colors['data'], 
                                  edgecolor='black', linewidth=1)
    ax.add_patch(facility_box)
    ax.text(2, data_y, 'Facility Data\n• 8 Korean Companies\n• 3 Regions (Yeosu, Daesan, Ulsan)\n• Process Types (NCC, BTX, C4)', 
            ha='center', va='center', fontsize=9)
    
    # Technology Data
    tech_box = FancyBboxPatch((4.5, data_y-0.4), 3, 0.8, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['data'], 
                              edgecolor='black', linewidth=1)
    ax.add_patch(tech_box)
    ax.text(6, data_y, 'Alternative Technologies\n• 18 Technologies\n• 9 Categories\n• TRL & Commercial Timeline', 
            ha='center', va='center', fontsize=9)
    
    # Baseline Consumption
    baseline_box = FancyBboxPatch((8.5, data_y-0.4), 3, 0.8, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=colors['data'], 
                                  edgecolor='black', linewidth=1)
    ax.add_patch(baseline_box)
    ax.text(10, data_y, 'Baseline Consumption\n• Energy (NG, FO, Electricity)\n• Process Emissions\n• 2.8 tCO2/t intensity', 
            ha='center', va='center', fontsize=9)
    
    # Time Series Data
    timeseries_box = FancyBboxPatch((12.5, data_y-0.4), 3, 0.8, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor=colors['data'], 
                                    edgecolor='black', linewidth=1)
    ax.add_patch(timeseries_box)
    ax.text(14, data_y, 'Time Series Data\n• Emission Factors (2023-2050)\n• Fuel Costs\n• Korean Grid Evolution', 
            ha='center', va='center', fontsize=9)
    
    # Korean NDC Targets
    targets_box = FancyBboxPatch((16.5, data_y-0.4), 3, 0.8, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=colors['data'], 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(targets_box)
    ax.text(18, data_y, 'Korean NDC Targets\n• 2030: 15% reduction\n• 2040: 50% reduction\n• 2050: 80% reduction', 
            ha='center', va='center', fontsize=9)
    
    # 2. PROCESSING LAYER
    process_y = 10
    
    # Baseline Calculation
    baseline_calc_box = FancyBboxPatch((1, process_y-0.4), 4, 0.8, 
                                       boxstyle="round,pad=0.1", 
                                       facecolor=colors['process'], 
                                       edgecolor='black', linewidth=1)
    ax.add_patch(baseline_calc_box)
    ax.text(3, process_y, 'Baseline Emissions Calculation\n• Facility × Process level\n• Energy + Process emissions\n• Total: 48.9 ktCO2/year', 
            ha='center', va='center', fontsize=9)
    
    # Viable Options Generation
    options_box = FancyBboxPatch((6, process_y-0.4), 4, 0.8, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=colors['process'], 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(options_box)
    ax.text(8, process_y, 'Viable Options Generation\n• Technology × Facility matrix\n• Abatement potential calculation\n• LCOA < $25,000/tCO2 filter', 
            ha='center', va='center', fontsize=9)
    
    # Cost Calculation
    cost_calc_box = FancyBboxPatch((11, process_y-0.4), 4, 0.8, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=colors['process'], 
                                   edgecolor='black', linewidth=1)
    ax.add_patch(cost_calc_box)
    ax.text(13, process_y, 'Cost Calculation\n• CAPEX + OPEX + Fuel costs\n• Regional adjustments\n• Levelized Cost of Abatement', 
            ha='center', va='center', fontsize=9)
    
    # Technology Filtering
    filter_box = FancyBboxPatch((16, process_y-0.4), 3, 0.8, 
                                boxstyle="round,pad=0.1", 
                                facecolor=colors['process'], 
                                edgecolor='black', linewidth=1)
    ax.add_patch(filter_box)
    ax.text(17.5, process_y, 'Technology Filtering\n• Commercial availability\n• Technical readiness\n• Process applicability', 
            ha='center', va='center', fontsize=9)
    
    # 3. OPTIMIZATION LAYER
    opt_y = 7.5
    
    # Linear Programming Setup
    lp_setup_box = FancyBboxPatch((2, opt_y-0.4), 5, 0.8, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=colors['optimization'], 
                                  edgecolor='black', linewidth=1)
    ax.add_patch(lp_setup_box)
    ax.text(4.5, opt_y, 'Linear Programming Optimization (PuLP)\n• Objective: Minimize total annual cost\n• Variables: Technology deployment levels (0-1)', 
            ha='center', va='center', fontsize=9)
    
    # Constraints
    constraints_box = FancyBboxPatch((8, opt_y-0.4), 5, 0.8, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor=colors['optimization'], 
                                     edgecolor='black', linewidth=1)
    ax.add_patch(constraints_box)
    ax.text(10.5, opt_y, 'Optimization Constraints\n• Meet Korean NDC emission targets\n• Max one technology per facility-process\n• Capacity and readiness limits', 
            ha='center', va='center', fontsize=9)
    
    # Solver
    solver_box = FancyBboxPatch((14, opt_y-0.4), 4, 0.8, 
                                boxstyle="round,pad=0.1", 
                                facecolor=colors['optimization'], 
                                edgecolor='black', linewidth=1)
    ax.add_patch(solver_box)
    ax.text(16, opt_y, 'CBC Solver\n• Mixed Integer Programming\n• Optimal solution finding\n• Feasibility checking', 
            ha='center', va='center', fontsize=9)
    
    # 4. ANALYSIS LAYER
    analysis_y = 5.5
    
    # Investment Analysis
    investment_box = FancyBboxPatch((1, analysis_y-0.4), 3, 0.8, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor=colors['results'], 
                                    edgecolor='black', linewidth=1)
    ax.add_patch(investment_box)
    ax.text(2.5, analysis_y, 'Investment Analysis\n• CAPEX requirements\n• Annual OPEX costs\n• Regional distribution', 
            ha='center', va='center', fontsize=9)
    
    # Pathway Analysis  
    pathway_box = FancyBboxPatch((5, analysis_y-0.4), 3, 0.8, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=colors['results'], 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(pathway_box)
    ax.text(6.5, analysis_y, 'Pathway Analysis\n• Emission reduction timeline\n• Cumulative investments\n• Technology deployment', 
            ha='center', va='center', fontsize=9)
    
    # Technology Analysis
    tech_analysis_box = FancyBboxPatch((9, analysis_y-0.4), 3, 0.8, 
                                       boxstyle="round,pad=0.1", 
                                       facecolor=colors['results'], 
                                       edgecolor='black', linewidth=1)
    ax.add_patch(tech_analysis_box)
    ax.text(10.5, analysis_y, 'Technology Analysis\n• MACC curve generation\n• Cost-effectiveness ranking\n• Market share evolution', 
            ha='center', va='center', fontsize=9)
    
    # Company Analysis
    company_box = FancyBboxPatch((13, analysis_y-0.4), 3, 0.8, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=colors['results'], 
                                 edgecolor='black', linewidth=1)
    ax.add_patch(company_box)
    ax.text(14.5, analysis_y, 'Company Analysis\n• Facility-level impacts\n• Regional participation\n• Investment distribution', 
            ha='center', va='center', fontsize=9)
    
    # Scenario Analysis
    scenario_box = FancyBboxPatch((17, analysis_y-0.4), 2.5, 0.8, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=colors['results'], 
                                  edgecolor='black', linewidth=1)
    ax.add_patch(scenario_box)
    ax.text(18.25, analysis_y, 'Scenario Analysis\n• Multiple target years\n• Sensitivity analysis\n• Policy scenarios', 
            ha='center', va='center', fontsize=9)
    
    # 5. OUTPUT LAYER
    output_y = 3.5
    
    # Visualization Outputs
    viz_box = FancyBboxPatch((2, output_y-0.4), 4, 0.8, 
                             boxstyle="round,pad=0.1", 
                             facecolor=colors['results'], 
                             edgecolor='black', linewidth=1)
    ax.add_patch(viz_box)
    ax.text(4, output_y, 'Comprehensive Visualizations\n• 9-panel analysis dashboard\n• MACC curves\n• Investment timelines\n• Technology roadmaps', 
            ha='center', va='center', fontsize=9)
    
    # Data Outputs
    data_output_box = FancyBboxPatch((7, output_y-0.4), 4, 0.8, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor=colors['results'], 
                                     edgecolor='black', linewidth=1)
    ax.add_patch(data_output_box)
    ax.text(9, output_y, 'Detailed Data Outputs\n• Deployment plans (CSV)\n• Investment analysis\n• Pathway projections\n• Technology matrices', 
            ha='center', va='center', fontsize=9)
    
    # Policy Recommendations
    policy_box = FancyBboxPatch((12, output_y-0.4), 4, 0.8, 
                                boxstyle="round,pad=0.1", 
                                facecolor=colors['results'], 
                                edgecolor='black', linewidth=1)
    ax.add_patch(policy_box)
    ax.text(14, output_y, 'Policy Insights\n• Cost-optimal strategies\n• Korean NDC compliance\n• Regional policy targeting\n• Technology priorities', 
            ha='center', va='center', fontsize=9)
    
    # 6. KEY RESULTS BOX
    results_box = FancyBboxPatch((8, 1.5), 4, 1.2, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#FFE6E6', 
                                 edgecolor='red', linewidth=2)
    ax.add_patch(results_box)
    ax.text(10, 2.1, 'KEY MODEL RESULTS\n\n✅ 2030: 15% reduction achievable\n    Cost: $2,753/tCO2, Investment: $181B\n\n⚠️ 2040/2050: Technology portfolio expansion needed\n    Current portfolio insufficient for deep cuts', 
            ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 7. ARROWS - Data Flow
    arrow_props = dict(arrowstyle='->', lw=2, color=colors['arrow'])
    
    # From data to processing
    for x in [2, 6, 10, 14, 18]:
        ax.annotate('', xy=(x, process_y+0.5), xytext=(x, data_y-0.5), 
                    arrowprops=arrow_props)
    
    # From processing to optimization
    ax.annotate('', xy=(4.5, opt_y+0.5), xytext=(3, process_y-0.5), 
                arrowprops=arrow_props)
    ax.annotate('', xy=(10.5, opt_y+0.5), xytext=(8, process_y-0.5), 
                arrowprops=arrow_props)
    ax.annotate('', xy=(16, opt_y+0.5), xytext=(13, process_y-0.5), 
                arrowprops=arrow_props)
    
    # From optimization to analysis
    for x_start, x_end in [(4.5, 2.5), (10.5, 6.5), (16, 14.5)]:
        ax.annotate('', xy=(x_end, analysis_y+0.5), xytext=(x_start, opt_y-0.5), 
                    arrowprops=arrow_props)
    
    # From analysis to outputs
    ax.annotate('', xy=(4, output_y+0.5), xytext=(2.5, analysis_y-0.5), 
                arrowprops=arrow_props)
    ax.annotate('', xy=(9, output_y+0.5), xytext=(6.5, analysis_y-0.5), 
                arrowprops=arrow_props)
    ax.annotate('', xy=(14, output_y+0.5), xytext=(14.5, analysis_y-0.5), 
                arrowprops=arrow_props)
    
    # 8. LEGEND
    legend_x = 0.5
    legend_y = 1
    
    legend_elements = [
        (colors['data'], 'Data Input'),
        (colors['process'], 'Processing'),
        (colors['optimization'], 'Optimization'),
        (colors['results'], 'Analysis & Results')
    ]
    
    ax.text(legend_x, legend_y+0.5, 'LEGEND:', fontweight='bold', fontsize=10)
    for i, (color, label) in enumerate(legend_elements):
        rect = patches.Rectangle((legend_x, legend_y-0.2-i*0.2), 0.3, 0.15, 
                               facecolor=color, edgecolor='black')
        ax.add_patch(rect)
        ax.text(legend_x+0.4, legend_y-0.125-i*0.2, label, va='center', fontsize=9)
    
    plt.tight_layout()
    return fig

def main():
    """Create and save model logic diagram"""
    
    print("Creating Korean Petrochemical MACC Model Logic Diagram...")
    
    fig = create_model_logic_diagram()
    
    # Save high-quality diagram
    output_path = Path("outputs/Korean_MACC_Model_Logic_Diagram.png")
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    
    print(f"✅ Model logic diagram saved: {output_path}")
    print("📊 High-resolution diagram ready for client presentation")
    
    plt.show()
    plt.close(fig)

if __name__ == "__main__":
    from pathlib import Path
    main()