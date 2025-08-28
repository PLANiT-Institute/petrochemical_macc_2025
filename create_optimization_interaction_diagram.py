"""
Create Interactive Optimization Process Diagram
==============================================

Shows the detailed interaction between optimization, constraints, and outputs
with feedback loops and decision processes.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle, FancyArrowPatch
import numpy as np

def create_optimization_interaction_diagram():
    """Create detailed optimization interaction diagram"""
    
    fig, ax = plt.subplots(figsize=(22, 16))
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 16)
    ax.axis('off')
    
    # Define colors with better contrast
    colors = {
        'input': '#E3F2FD',           # Light blue
        'process': '#FFF3E0',         # Light orange
        'optimization': '#F3E5F5',    # Light purple
        'constraints': '#FFEBEE',     # Light red
        'solver': '#E8F5E8',          # Light green
        'output': '#FFF8E1',          # Light yellow
        'feedback': '#FF5722',        # Orange red
        'decision': '#4CAF50'         # Green
    }
    
    # Title
    ax.text(11, 15.5, 'Korean Petrochemical MACC: Optimization Interaction Process', 
            ha='center', va='center', fontsize=18, fontweight='bold')
    
    # SECTION 1: INPUT DATA (Left side)
    input_x = 1
    
    # Facility Data
    facility_box = FancyBboxPatch((input_x, 13), 3.5, 1.5, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=colors['input'], 
                                  edgecolor='black', linewidth=1.5)
    ax.add_patch(facility_box)
    ax.text(input_x + 1.75, 13.75, '🏭 FACILITY DATA\n\n• 8 Korean Companies\n• 24 Process Units\n• Regional Distribution\n• Technical Readiness', 
            ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Technology Options
    tech_box = FancyBboxPatch((input_x, 11), 3.5, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['input'], 
                              edgecolor='black', linewidth=1.5)
    ax.add_patch(tech_box)
    ax.text(input_x + 1.75, 11.75, '⚙️ TECH OPTIONS\n\n• 18 Technologies\n• Cost Data (CAPEX/OPEX)\n• Abatement Potential\n• Commercial Timeline', 
            ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Korean NDC Targets
    targets_box = FancyBboxPatch((input_x, 9), 3.5, 1.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=colors['constraints'], 
                                 edgecolor='red', linewidth=2)
    ax.add_patch(targets_box)
    ax.text(input_x + 1.75, 9.75, '🎯 KOREAN NDC TARGETS\n\n• 2030: 15% reduction\n• 2040: 50% reduction\n• 2050: 80% reduction\n• MUST BE MET!', 
            ha='center', va='center', fontsize=9, fontweight='bold')
    
    # SECTION 2: VIABLE OPTIONS MATRIX (Center-left)
    matrix_x = 6
    matrix_box = FancyBboxPatch((matrix_x, 11), 4, 3, 
                                boxstyle="round,pad=0.1", 
                                facecolor=colors['process'], 
                                edgecolor='black', linewidth=1.5)
    ax.add_patch(matrix_box)
    ax.text(matrix_x + 2, 13.5, '📊 VIABLE OPTIONS MATRIX', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(matrix_x + 2, 12.5, 'Technology × Facility Combinations\n\n• Calculate abatement potential\n• Estimate costs (LCOA)\n• Filter viable options\n• Create decision variables\n\nResult: 39 viable options', 
            ha='center', va='center', fontsize=9)
    
    # SECTION 3: OPTIMIZATION ENGINE (Center)
    opt_x = 11.5
    opt_y = 9.5
    
    # Main Optimization Box
    opt_main_box = FancyBboxPatch((opt_x, opt_y), 4.5, 4, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=colors['optimization'], 
                                  edgecolor='purple', linewidth=2)
    ax.add_patch(opt_main_box)
    ax.text(opt_x + 2.25, opt_y + 3.5, '🎲 LINEAR PROGRAMMING SOLVER', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Objective Function
    obj_box = FancyBboxPatch((opt_x + 0.3, opt_y + 2.5), 3.9, 0.8, 
                             boxstyle="round,pad=0.05", 
                             facecolor='white', 
                             edgecolor='blue', linewidth=1)
    ax.add_patch(obj_box)
    ax.text(opt_x + 2.25, opt_y + 2.9, 'OBJECTIVE: Minimize Total Annual Cost\nΣ (Technology Cost × Deployment Level)', 
            ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Decision Variables
    var_box = FancyBboxPatch((opt_x + 0.3, opt_y + 1.5), 3.9, 0.8, 
                             boxstyle="round,pad=0.05", 
                             facecolor='white', 
                             edgecolor='green', linewidth=1)
    ax.add_patch(var_box)
    ax.text(opt_x + 2.25, opt_y + 1.9, 'VARIABLES: Deployment Levels (0-1)\nFor each Technology-Facility option', 
            ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Solver Status
    solver_box = FancyBboxPatch((opt_x + 0.3, opt_y + 0.3), 3.9, 0.8, 
                                boxstyle="round,pad=0.05", 
                                facecolor=colors['solver'], 
                                edgecolor='darkgreen', linewidth=1)
    ax.add_patch(solver_box)
    ax.text(opt_x + 2.25, opt_y + 0.7, 'CBC SOLVER ENGINE\nOptimal / Infeasible / Unbounded', 
            ha='center', va='center', fontsize=8, fontweight='bold')
    
    # SECTION 4: CONSTRAINTS (Right side, interactive)
    const_x = 17
    
    # Emission Target Constraint
    emission_const_box = FancyBboxPatch((const_x, 12.5), 4, 1.2, 
                                        boxstyle="round,pad=0.1", 
                                        facecolor=colors['constraints'], 
                                        edgecolor='red', linewidth=2)
    ax.add_patch(emission_const_box)
    ax.text(const_x + 2, 13.1, '🚫 EMISSION CONSTRAINT\n\nΣ Abatement ≥ Required Reduction\nMUST meet Korean NDC targets', 
            ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Technology Constraint
    tech_const_box = FancyBboxPatch((const_x, 10.8), 4, 1.2, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor=colors['constraints'], 
                                    edgecolor='red', linewidth=2)
    ax.add_patch(tech_const_box)
    ax.text(const_x + 2, 11.4, '⚙️ TECHNOLOGY CONSTRAINT\n\nMax 1 technology per facility-process\nNo double deployment', 
            ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Capacity Constraint
    capacity_const_box = FancyBboxPatch((const_x, 9.1), 4, 1.2, 
                                        boxstyle="round,pad=0.1", 
                                        facecolor=colors['constraints'], 
                                        edgecolor='red', linewidth=2)
    ax.add_patch(capacity_const_box)
    ax.text(const_x + 2, 9.7, '🏭 CAPACITY CONSTRAINT\n\nDeployment ≤ Facility Capacity\nTechnical readiness limits', 
            ha='center', va='center', fontsize=9, fontweight='bold')
    
    # SECTION 5: DECISION LOGIC (Center-bottom)
    decision_x = 8
    decision_y = 6.5
    
    # Decision Diamond
    decision_diamond = patches.RegularPolygon((decision_x + 2, decision_y), 4, radius=1.2, 
                                              orientation=np.pi/4,
                                              facecolor=colors['decision'], 
                                              edgecolor='black', linewidth=2)
    ax.add_patch(decision_diamond)
    ax.text(decision_x + 2, decision_y, 'SOLUTION\nFEASIBLE?', 
            ha='center', va='center', fontsize=10, fontweight='bold')
    
    # SECTION 6: OUTPUTS (Bottom)
    
    # Success Path
    success_box = FancyBboxPatch((2, 4), 4, 1.8, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=colors['output'], 
                                 edgecolor='green', linewidth=2)
    ax.add_patch(success_box)
    ax.text(4, 4.9, '✅ OPTIMAL SOLUTION\n\n• Deployment plan\n• Cost breakdown\n• Investment requirements\n• Technology roadmap\n• Policy recommendations', 
            ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Failure Path
    failure_box = FancyBboxPatch((16, 4), 4, 1.8, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#FFCDD2', 
                                 edgecolor='red', linewidth=2)
    ax.add_patch(failure_box)
    ax.text(18, 4.9, '❌ INFEASIBLE\n\n• Targets too aggressive\n• Technology portfolio limited\n• Cost threshold too low\n• Need policy intervention\n• Portfolio expansion required', 
            ha='center', va='center', fontsize=9, fontweight='bold')
    
    # SECTION 7: FEEDBACK LOOPS AND INTERACTIONS
    
    # Data to Matrix
    arrow1 = FancyArrowPatch((input_x + 3.5, 12.5), (matrix_x, 12.5),
                             arrowstyle='->', mutation_scale=20, 
                             color=colors['decision'], linewidth=2)
    ax.add_patch(arrow1)
    
    # Matrix to Optimization
    arrow2 = FancyArrowPatch((matrix_x + 4, 12.5), (opt_x, 12),
                             arrowstyle='->', mutation_scale=20, 
                             color=colors['decision'], linewidth=2)
    ax.add_patch(arrow2)
    
    # Constraints to Optimization (interactive arrows)
    for const_y in [13.1, 11.4, 9.7]:
        arrow = FancyArrowPatch((const_x, const_y), (opt_x + 4.5, opt_y + 2),
                                arrowstyle='->', mutation_scale=15, 
                                color=colors['feedback'], linewidth=2, linestyle='--')
        ax.add_patch(arrow)
    
    # NDC Targets to Constraints
    arrow3 = FancyArrowPatch((input_x + 3.5, 9.75), (const_x, 13.1),
                             arrowstyle='->', mutation_scale=20, 
                             color=colors['feedback'], linewidth=2, 
                             connectionstyle="arc3,rad=0.3")
    ax.add_patch(arrow3)
    
    # Optimization to Decision
    arrow4 = FancyArrowPatch((opt_x + 2.25, opt_y), (decision_x + 2, decision_y + 1),
                             arrowstyle='->', mutation_scale=20, 
                             color=colors['decision'], linewidth=3)
    ax.add_patch(arrow4)
    
    # Decision to Success (YES path)
    arrow5 = FancyArrowPatch((decision_x + 1, decision_y - 0.8), (4, 5.8),
                             arrowstyle='->', mutation_scale=20, 
                             color='green', linewidth=3)
    ax.add_patch(arrow5)
    ax.text(decision_x - 1, decision_y - 1.3, 'YES\nOptimal Found', 
            ha='center', va='center', fontsize=9, fontweight='bold', color='green')
    
    # Decision to Failure (NO path)
    arrow6 = FancyArrowPatch((decision_x + 3, decision_y - 0.8), (18, 5.8),
                             arrowstyle='->', mutation_scale=20, 
                             color='red', linewidth=3)
    ax.add_patch(arrow6)
    ax.text(decision_x + 5, decision_y - 1.3, 'NO\nInfeasible', 
            ha='center', va='center', fontsize=9, fontweight='bold', color='red')
    
    # SECTION 8: FEEDBACK LOOP (for model iteration)
    feedback_arrow = FancyArrowPatch((18, 3), (matrix_x + 2, 10.5),
                                     arrowstyle='->', mutation_scale=15, 
                                     color=colors['feedback'], linewidth=2, 
                                     linestyle=':', connectionstyle="arc3,rad=-0.4")
    ax.add_patch(feedback_arrow)
    ax.text(12, 2, 'FEEDBACK LOOP:\nAdjust parameters, expand technology portfolio,\nrevise targets for infeasible scenarios', 
            ha='center', va='center', fontsize=8, style='italic', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.7))
    
    # SECTION 9: KEY INSIGHTS BOX
    insights_box = FancyBboxPatch((8, 0.5), 6, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='#E1F5FE', 
                                  edgecolor='blue', linewidth=2)
    ax.add_patch(insights_box)
    ax.text(11, 1.1, '🔍 KEY MODEL INSIGHTS\n\n2030: ✅ Feasible (Heat pump, $2,753/tCO2)  |  2040/2050: ❌ Infeasible (Need portfolio expansion)', 
            ha='center', va='center', fontsize=10, fontweight='bold')
    
    # SECTION 10: LEGEND
    legend_x = 0.5
    legend_y = 6.5
    
    ax.text(legend_x, legend_y + 1, 'LEGEND:', fontweight='bold', fontsize=11)
    
    legend_elements = [
        (colors['input'], '📊 Input Data'),
        (colors['process'], '⚙️ Processing'),
        (colors['optimization'], '🎲 Optimization'),
        (colors['constraints'], '🚫 Constraints'),
        (colors['output'], '📋 Outputs'),
        ('green', '→ Success Path'),
        ('red', '→ Failure Path'),
        (colors['feedback'], '⟲ Feedback')
    ]
    
    for i, (color, label) in enumerate(legend_elements):
        if i < 5:  # Regular boxes
            rect = patches.Rectangle((legend_x, legend_y - 0.3 - i*0.4), 0.3, 0.2, 
                                   facecolor=color, edgecolor='black')
            ax.add_patch(rect)
        else:  # Arrow indicators
            arrow = FancyArrowPatch((legend_x, legend_y - 0.2 - i*0.4), 
                                    (legend_x + 0.3, legend_y - 0.2 - i*0.4),
                                    arrowstyle='->', mutation_scale=10, 
                                    color=color, linewidth=2)
            ax.add_patch(arrow)
        
        ax.text(legend_x + 0.4, legend_y - 0.2 - i*0.4, label, 
                va='center', fontsize=9)
    
    plt.tight_layout()
    return fig

def main():
    """Create and save interactive optimization diagram"""
    
    print("Creating Interactive Optimization Process Diagram...")
    
    fig = create_optimization_interaction_diagram()
    
    # Save high-quality diagram
    output_path = "outputs/Korean_MACC_Optimization_Interaction_Diagram.png"
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    
    print(f"✅ Interactive optimization diagram saved: {output_path}")
    print("📊 Shows detailed optimization mechanics and constraint interactions")
    
    plt.show()
    plt.close(fig)

if __name__ == "__main__":
    main()