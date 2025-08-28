"""
Create Academic-Quality Model Diagram
===================================

Professional publication-ready diagram for Korean Petrochemical MACC model
suitable for academic papers and peer-reviewed journals.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle, FancyArrowPatch, Rectangle
import numpy as np
import matplotlib.patheffects as path_effects

def create_academic_model_diagram():
    """Create academic-quality model diagram"""
    
    # Set academic figure parameters
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif'],
        'font.size': 10,
        'axes.linewidth': 1.2,
        'figure.dpi': 300
    })
    
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Academic color scheme (professional, colorblind-friendly)
    colors = {
        'data': '#F8F9FA',           # Very light gray
        'process': '#E3F2FD',        # Light blue
        'optimization': '#FFF3E0',    # Light amber
        'constraints': '#FFEBEE',     # Light red
        'results': '#E8F5E8',         # Light green
        'flow': '#424242',            # Dark gray
        'highlight': '#1976D2',       # Professional blue
        'accent': '#D32F2F'           # Professional red
    }
    
    # Title with academic formatting
    title = ax.text(8, 11.5, 'Facility-Level Optimization Framework for Korean Petrochemical\nMarginal Abatement Cost Curve (MACC) Analysis', 
            ha='center', va='center', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='black', linewidth=1))
    
    # PHASE 1: DATA PREPARATION AND PREPROCESSING
    phase1_y = 10
    
    # Phase 1 header
    ax.text(8, phase1_y + 0.3, 'PHASE 1: DATA PREPARATION AND PREPROCESSING', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.2", facecolor=colors['data'], edgecolor='black'))
    
    # Facility Database
    facility_box = Rectangle((0.5, phase1_y - 0.8), 3, 1.2, 
                            facecolor=colors['data'], edgecolor='black', linewidth=1)
    ax.add_patch(facility_box)
    ax.text(2, phase1_y - 0.2, r'$\mathbf{F} = \{f_1, f_2, ..., f_8\}$' + '\nFacility Set\n• Companies: 8\n• Regions: 3 (Yeosu, Daesan, Ulsan)\n• Processes: {NCC, BTX, C4}', 
            ha='center', va='center', fontsize=9)
    
    # Technology Portfolio
    tech_box = Rectangle((4, phase1_y - 0.8), 3, 1.2, 
                        facecolor=colors['data'], edgecolor='black', linewidth=1)
    ax.add_patch(tech_box)
    ax.text(5.5, phase1_y - 0.2, r'$\mathbf{T} = \{t_1, t_2, ..., t_{18}\}$' + '\nTechnology Set\n• Categories: 9\n• TRL: [3,9]\n• Commercial: 2023-2035', 
            ha='center', va='center', fontsize=9)
    
    # Emission Factors
    emission_box = Rectangle((7.5, phase1_y - 0.8), 3, 1.2, 
                            facecolor=colors['data'], edgecolor='black', linewidth=1)
    ax.add_patch(emission_box)
    ax.text(9, phase1_y - 0.2, r'$\mathbf{EF}_y = \{ef_{ng}, ef_{fo}, ef_{elec}\}$' + '\nEmission Factors\n• Time series: 2023-2050\n• Korean grid evolution\n• Process emissions', 
            ha='center', va='center', fontsize=9)
    
    # Policy Targets
    policy_box = Rectangle((11.5, phase1_y - 0.8), 3.5, 1.2, 
                          facecolor=colors['constraints'], edgecolor='black', linewidth=1.5)
    ax.add_patch(policy_box)
    ax.text(13.25, phase1_y - 0.2, r'$\mathbf{E}^{target}_y$' + ' (Korean NDC)\nEmission Targets\n• 2030: 15% reduction\n• 2040: 50% reduction\n• 2050: 80% reduction', 
            ha='center', va='center', fontsize=9, fontweight='bold')
    
    # PHASE 2: OPTIMIZATION MODEL FORMULATION
    phase2_y = 7.5
    
    # Phase 2 header
    ax.text(8, phase2_y + 0.8, 'PHASE 2: OPTIMIZATION MODEL FORMULATION', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.2", facecolor=colors['process'], edgecolor='black'))
    
    # Decision Variables
    var_box = Rectangle((1, phase2_y - 0.3), 4.5, 1.2, 
                       facecolor=colors['process'], edgecolor='black', linewidth=1)
    ax.add_patch(var_box)
    ax.text(3.25, phase2_y + 0.3, 'Decision Variables', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(3.25, phase2_y - 0.1, r'$x_{f,t,p} \in [0,1]$' + '\nDeployment level of technology t\nat facility f for process p\n' + r'$\forall f \in F, t \in T, p \in P$', 
            ha='center', va='center', fontsize=9)
    
    # Objective Function
    obj_box = Rectangle((6, phase2_y - 0.3), 4, 1.2, 
                       facecolor=colors['optimization'], edgecolor='black', linewidth=1.5)
    ax.add_patch(obj_box)
    ax.text(8, phase2_y + 0.3, 'Objective Function', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(8, phase2_y - 0.1, r'$\min \sum_{f,t,p} C_{f,t,p} \cdot x_{f,t,p}$' + '\nMinimize total annual cost\nwhere ' + r'$C_{f,t,p} = CAPEX + OPEX + \Delta FC$', 
            ha='center', va='center', fontsize=9)
    
    # Constraints Box
    const_box = Rectangle((10.5, phase2_y - 0.3), 4.5, 1.2, 
                         facecolor=colors['constraints'], edgecolor='black', linewidth=1.5)
    ax.add_patch(const_box)
    ax.text(12.75, phase2_y + 0.3, 'Constraint Set', ha='center', va='center', fontsize=10, fontweight='bold')
    constraint_text = (r'$\sum_{f,t,p} A_{f,t,p} \cdot x_{f,t,p} \geq E^{required}$' + ' (1)\n' +
                      r'$\sum_t x_{f,t,p} \leq 1, \forall f,p$' + ' (2)\n' +
                      r'$x_{f,t,p} \leq CAP_{f,p}, \forall f,t,p$' + ' (3)')
    ax.text(12.75, phase2_y - 0.1, constraint_text, ha='center', va='center', fontsize=8)
    
    # PHASE 3: SOLUTION ALGORITHM AND ANALYSIS
    phase3_y = 5
    
    # Phase 3 header
    ax.text(8, phase3_y + 0.8, 'PHASE 3: SOLUTION ALGORITHM AND ANALYSIS', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.2", facecolor=colors['results'], edgecolor='black'))
    
    # Linear Programming Solver
    solver_box = Rectangle((2, phase3_y - 0.3), 3.5, 1.2, 
                          facecolor=colors['optimization'], edgecolor='black', linewidth=1)
    ax.add_patch(solver_box)
    ax.text(3.75, phase3_y + 0.3, 'LP Solver (CBC)', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(3.75, phase3_y - 0.1, 'Mixed Integer Programming\n• Variables: ' + r'$|F| \times |T| \times |P|$' + '\n• Constraints: ' + r'$O(|F| \times |P|)$' + '\n• Solution: Optimal/Infeasible', 
            ha='center', va='center', fontsize=9)
    
    # Results Analysis
    results_box = Rectangle((6.5, phase3_y - 0.3), 3.5, 1.2, 
                           facecolor=colors['results'], edgecolor='black', linewidth=1)
    ax.add_patch(results_box)
    ax.text(8.25, phase3_y + 0.3, 'Solution Analysis', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(8.25, phase3_y - 0.1, r'$x_{f,t,p}^*$' + ' → Deployment Plan\n• MACC curve generation\n• Investment requirements\n• Technology roadmap', 
            ha='center', va='center', fontsize=9)
    
    # Sensitivity Analysis
    sensitivity_box = Rectangle((10.5, phase3_y - 0.3), 3.5, 1.2, 
                               facecolor=colors['results'], edgecolor='black', linewidth=1)
    ax.add_patch(sensitivity_box)
    ax.text(12.25, phase3_y + 0.3, 'Sensitivity Analysis', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(12.25, phase3_y - 0.1, 'Parameter Variations\n• Cost thresholds\n• Technology availability\n• Policy scenarios', 
            ha='center', va='center', fontsize=9)
    
    # RESULTS SECTION
    results_y = 2.5
    
    # Results header
    ax.text(8, results_y + 0.8, 'MODEL VALIDATION AND RESULTS', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.2", facecolor='#FFE0B2', edgecolor='black'))
    
    # Key Findings
    findings_box = Rectangle((1, results_y - 0.5), 6, 1.2, 
                            facecolor='#FFF9C4', edgecolor='black', linewidth=1.5)
    ax.add_patch(findings_box)
    ax.text(4, results_y + 0.1, 'Key Findings', ha='center', va='center', fontsize=10, fontweight='bold')
    findings_text = ('• 2030 Target: Achievable (Heat pump technology, $2,753/tCO₂)\n' +
                    '• Technology Portfolio: Limited for deep decarbonization (>50%)\n' +
                    '• Investment Required: $181.4B CAPEX for 2030 compliance\n' +
                    '• Regional Distribution: Yeosu (66%), Daesan (17%), Ulsan (16%)')
    ax.text(4, results_y - 0.2, findings_text, ha='center', va='center', fontsize=8)
    
    # Model Performance
    performance_box = Rectangle((8, results_y - 0.5), 6, 1.2, 
                               facecolor='#E8F5E8', edgecolor='black', linewidth=1.5)
    ax.add_patch(performance_box)
    ax.text(11, results_y + 0.1, 'Model Performance', ha='center', va='center', fontsize=10, fontweight='bold')
    performance_text = ('• Computational Efficiency: <1 min solution time\n' +
                       '• Solution Quality: Optimal for feasible scenarios\n' +
                       '• Validation: Emission intensity 2.8 tCO₂/t (industry benchmark)\n' +
                       '• Scalability: 39 viable technology-facility combinations')
    ax.text(11, results_y - 0.2, performance_text, ha='center', va='center', fontsize=8)
    
    # FLOW ARROWS (Academic style - clean and professional)
    
    # Phase 1 to Phase 2 arrows
    for x in [2, 5.5, 9, 13.25]:
        arrow = FancyArrowPatch((x, phase1_y - 0.9), (x, phase2_y + 0.9),
                               arrowstyle='->', mutation_scale=15, 
                               color=colors['flow'], linewidth=1.5)
        ax.add_patch(arrow)
    
    # Phase 2 internal connections
    arrow1 = FancyArrowPatch((5.5, phase2_y + 0.1), (6, phase2_y + 0.1),
                            arrowstyle='->', mutation_scale=12, 
                            color=colors['highlight'], linewidth=2)
    ax.add_patch(arrow1)
    
    arrow2 = FancyArrowPatch((10, phase2_y + 0.1), (10.5, phase2_y + 0.1),
                            arrowstyle='->', mutation_scale=12, 
                            color=colors['accent'], linewidth=2)
    ax.add_patch(arrow2)
    
    # Phase 2 to Phase 3 arrows
    for x in [3.75, 8.25, 12.25]:
        arrow = FancyArrowPatch((x, phase2_y - 0.4), (x, phase3_y + 0.9),
                               arrowstyle='->', mutation_scale=15, 
                               color=colors['flow'], linewidth=1.5)
        ax.add_patch(arrow)
    
    # Phase 3 to Results arrows
    for x in [4, 11]:
        arrow = FancyArrowPatch((x, phase3_y - 0.4), (x, results_y + 1.0),
                               arrowstyle='->', mutation_scale=15, 
                               color=colors['flow'], linewidth=1.5)
        ax.add_patch(arrow)
    
    # MATHEMATICAL NOTATION LEGEND
    legend_box = Rectangle((0.5, 0.2), 15, 1, 
                          facecolor='#F5F5F5', edgecolor='black', linewidth=1)
    ax.add_patch(legend_box)
    ax.text(8, 0.9, 'Mathematical Notation', ha='center', va='center', fontsize=10, fontweight='bold')
    
    notation_text = (r'$F$: Facility set; $T$: Technology set; $P$: Process set; $x_{f,t,p}$: Deployment variable; $C_{f,t,p}$: Technology cost; ' +
                    r'$A_{f,t,p}$: Abatement potential; $E^{required}$: Required emission reduction; $CAP_{f,p}$: Facility capacity')
    ax.text(8, 0.5, notation_text, ha='center', va='center', fontsize=8, style='italic')
    
    # Add figure caption
    caption_text = ('Fig. 1. Methodological framework for facility-level optimization in Korean petrochemical MACC analysis. The model integrates ' +
                   'facility-specific data with alternative technologies through a linear programming approach to identify cost-optimal ' +
                   'decarbonization pathways aligned with Korean NDC targets.')
    ax.text(8, 0.1, caption_text, ha='center', va='center', fontsize=8, style='italic',
           bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='gray', alpha=0.8))
    
    plt.tight_layout()
    return fig

def main():
    """Create and save academic model diagram"""
    
    print("Creating Academic-Quality Korean Petrochemical MACC Model Diagram...")
    
    fig = create_academic_model_diagram()
    
    # Save high-quality diagram suitable for publication
    output_path = "outputs/Korean_MACC_Academic_Model_Diagram.png"
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', 
                edgecolor='none', format='png')
    
    # Also save as PDF for publication
    pdf_path = "outputs/Korean_MACC_Academic_Model_Diagram.pdf"
    fig.savefig(pdf_path, dpi=300, bbox_inches='tight', facecolor='white', 
                edgecolor='none', format='pdf')
    
    print(f"✅ Academic model diagram saved:")
    print(f"   PNG: {output_path}")
    print(f"   PDF: {pdf_path}")
    print("📊 Publication-ready diagram with mathematical notation")
    
    plt.show()
    plt.close(fig)

if __name__ == "__main__":
    main()