"""
Create Professional Publication-Quality Model Diagram
===================================================

High-end academic diagram suitable for top-tier journals like Nature Energy,
Energy Policy, Applied Energy, etc.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon, Ellipse
import matplotlib.patheffects as path_effects
import numpy as np
from matplotlib import font_manager

def create_professional_model_diagram():
    """Create professional publication-quality model diagram"""
    
    # Set professional matplotlib parameters
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 9,
        'axes.linewidth': 0.8,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'text.usetex': False,
        'mathtext.fontset': 'stixsans'
    })
    
    # Create figure with golden ratio proportions
    fig_width = 12
    fig_height = fig_width / 1.618  # Golden ratio
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    
    # Professional color palette (based on Nature/Science journals)
    colors = {
        'primary': '#2E3440',      # Dark blue-gray (text)
        'secondary': '#4C566A',    # Medium gray (borders)
        'accent1': '#5E81AC',      # Professional blue
        'accent2': '#8FBCBB',      # Light blue
        'accent3': '#A3BE8C',      # Professional green
        'accent4': '#EBCB8B',      # Professional yellow/amber
        'accent5': '#D08770',      # Professional orange
        'background': '#ECEFF4',   # Very light gray
        'white': '#FFFFFF',        # Pure white
        'highlight': '#BF616A'     # Professional red
    }
    
    # Main title with professional styling
    ax.text(6, 7.2, 'Optimization Framework for Facility-Level Petrochemical Decarbonization Analysis',
            ha='center', va='center', fontsize=12, fontweight='bold', color=colors['primary'])
    ax.text(6, 6.9, 'Linear Programming Approach for Korean NDC Compliance Pathways',
            ha='center', va='center', fontsize=10, style='italic', color=colors['secondary'])
    
    # INPUT MODULE (Left column)
    input_x = 0.5
    input_width = 2.8
    
    # Input header
    input_header = Rectangle((input_x, 6), input_width, 0.4,
                            facecolor=colors['accent1'], edgecolor='none')
    ax.add_patch(input_header)
    ax.text(input_x + input_width/2, 6.2, 'INPUT DATA MODULE', 
            ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    # Facility data
    facility_box = Rectangle((input_x, 5.3), input_width, 0.6,
                           facecolor=colors['background'], edgecolor=colors['secondary'], linewidth=0.8)
    ax.add_patch(facility_box)
    ax.text(input_x + 0.1, 5.7, '𝐅 = {𝑓₁, 𝑓₂, ..., 𝑓₈}', fontweight='bold', fontsize=8, color=colors['primary'])
    ax.text(input_x + 0.1, 5.5, 'Korean petrochemical facilities', fontsize=7, color=colors['secondary'])
    ax.text(input_x + 0.1, 5.35, '• 8 companies, 3 regions, 24 processes', fontsize=6, color=colors['secondary'])
    
    # Technology data  
    tech_box = Rectangle((input_x, 4.6), input_width, 0.6,
                        facecolor=colors['background'], edgecolor=colors['secondary'], linewidth=0.8)
    ax.add_patch(tech_box)
    ax.text(input_x + 0.1, 5.0, '𝐓 = {𝑡₁, 𝑡₂, ..., 𝑡₁₈}', fontweight='bold', fontsize=8, color=colors['primary'])
    ax.text(input_x + 0.1, 4.8, 'Alternative technologies', fontsize=7, color=colors['secondary'])
    ax.text(input_x + 0.1, 4.65, '• Heat pumps, e-crackers, H₂ systems', fontsize=6, color=colors['secondary'])
    
    # Economic data
    econ_box = Rectangle((input_x, 3.9), input_width, 0.6,
                        facecolor=colors['background'], edgecolor=colors['secondary'], linewidth=0.8)
    ax.add_patch(econ_box)
    ax.text(input_x + 0.1, 4.3, '𝐂(𝑡, 𝑓, 𝑦)', fontweight='bold', fontsize=8, color=colors['primary'])
    ax.text(input_x + 0.1, 4.1, 'Cost parameters', fontsize=7, color=colors['secondary'])
    ax.text(input_x + 0.1, 3.95, '• CAPEX, OPEX, fuel costs (2023-2050)', fontsize=6, color=colors['secondary'])
    
    # OPTIMIZATION ENGINE (Center)
    opt_x = 4
    opt_width = 4
    opt_height = 3.5
    
    # Main optimization box with gradient effect
    opt_main = Rectangle((opt_x, 2.5), opt_width, opt_height,
                        facecolor=colors['white'], edgecolor=colors['accent1'], linewidth=1.5)
    ax.add_patch(opt_main)
    
    # Optimization header
    opt_header = Rectangle((opt_x, 5.7), opt_width, 0.4,
                          facecolor=colors['accent1'], edgecolor='none')
    ax.add_patch(opt_header)
    ax.text(opt_x + opt_width/2, 5.9, 'LINEAR PROGRAMMING OPTIMIZATION ENGINE', 
            ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    # Objective function box
    obj_box = Rectangle((opt_x + 0.2, 5.1), opt_width - 0.4, 0.5,
                       facecolor=colors['accent4'], edgecolor='none', alpha=0.3)
    ax.add_patch(obj_box)
    ax.text(opt_x + 0.3, 5.45, 'Objective Function:', fontweight='bold', fontsize=8, color=colors['primary'])
    ax.text(opt_x + 0.3, 5.25, 'minimize    ∑ᶠ∑ᵗ∑ᵖ 𝑐ᶠᵗᵖ · 𝑥ᶠᵗᵖ', fontsize=8, color=colors['primary'], family='monospace')
    
    # Decision variables
    var_box = Rectangle((opt_x + 0.2, 4.4), opt_width - 0.4, 0.4,
                       facecolor=colors['accent2'], edgecolor='none', alpha=0.3)
    ax.add_patch(var_box)
    ax.text(opt_x + 0.3, 4.7, 'Decision Variables:', fontweight='bold', fontsize=8, color=colors['primary'])
    ax.text(opt_x + 0.3, 4.5, '𝑥ᶠᵗᵖ ∈ [0,1]  ∀𝑓∈𝐅, 𝑡∈𝐓, 𝑝∈𝐏', fontsize=8, color=colors['primary'])
    
    # Constraints section
    const_y_start = 3.8
    constraints = [
        ('Emission Target:', '∑ᶠ∑ᵗ∑ᵖ 𝑎ᶠᵗᵖ · 𝑥ᶠᵗᵖ ≥ 𝐸ʳᵉᵠᵘⁱʳᵉᵈ'),
        ('Technology Selection:', '∑ᵗ 𝑥ᶠᵗᵖ ≤ 1  ∀𝑓,𝑝'),
        ('Capacity Limits:', '𝑥ᶠᵗᵖ ≤ 𝐶𝐴𝑃ᶠᵖ  ∀𝑓,𝑡,𝑝'),
        ('Technical Readiness:', '𝑥ᶠᵗᵖ = 0 if 𝑇𝑅𝐿ₜ < 𝑇𝑅𝐿ᵐⁱⁿ')
    ]
    
    for i, (label, formula) in enumerate(constraints):
        y_pos = const_y_start - i * 0.25
        ax.text(opt_x + 0.3, y_pos, label, fontweight='bold', fontsize=7, color=colors['primary'])
        ax.text(opt_x + 1.8, y_pos, formula, fontsize=7, color=colors['primary'], family='monospace')
    
    # Solver indicator
    solver_circle = Circle((opt_x + opt_width/2, 2.8), 0.15, 
                          facecolor=colors['accent3'], edgecolor=colors['secondary'], linewidth=1)
    ax.add_patch(solver_circle)
    ax.text(opt_x + opt_width/2, 2.8, 'CBC', ha='center', va='center', 
            fontsize=7, fontweight='bold', color='white')
    
    # OUTPUT MODULE (Right column)
    output_x = 8.7
    output_width = 2.8
    
    # Output header
    output_header = Rectangle((output_x, 6), output_width, 0.4,
                             facecolor=colors['accent3'], edgecolor='none')
    ax.add_patch(output_header)
    ax.text(output_x + output_width/2, 6.2, 'OUTPUT ANALYSIS MODULE', 
            ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    # Deployment plan
    deploy_box = Rectangle((output_x, 5.3), output_width, 0.6,
                          facecolor=colors['background'], edgecolor=colors['secondary'], linewidth=0.8)
    ax.add_patch(deploy_box)
    ax.text(output_x + 0.1, 5.7, '𝐱* = {𝑥ᶠᵗᵖ*}', fontweight='bold', fontsize=8, color=colors['primary'])
    ax.text(output_x + 0.1, 5.5, 'Optimal deployment plan', fontsize=7, color=colors['secondary'])
    ax.text(output_x + 0.1, 5.35, '• Technology roadmap by facility', fontsize=6, color=colors['secondary'])
    
    # Economic analysis
    econ_out_box = Rectangle((output_x, 4.6), output_width, 0.6,
                            facecolor=colors['background'], edgecolor=colors['secondary'], linewidth=0.8)
    ax.add_patch(econ_out_box)
    ax.text(output_x + 0.1, 5.0, 'MACC Curve', fontweight='bold', fontsize=8, color=colors['primary'])
    ax.text(output_x + 0.1, 4.8, 'Cost-effectiveness ranking', fontsize=7, color=colors['secondary'])
    ax.text(output_x + 0.1, 4.65, '• LCOA: $2,753/tCO₂ (2030)', fontsize=6, color=colors['secondary'])
    
    # Policy insights
    policy_box = Rectangle((output_x, 3.9), output_width, 0.6,
                          facecolor=colors['background'], edgecolor=colors['secondary'], linewidth=0.8)
    ax.add_patch(policy_box)
    ax.text(output_x + 0.1, 4.3, 'Policy Analysis', fontweight='bold', fontsize=8, color=colors['primary'])
    ax.text(output_x + 0.1, 4.1, 'NDC compliance pathways', fontsize=7, color=colors['secondary'])
    ax.text(output_x + 0.1, 3.95, '• Investment: $181.4B (2030)', fontsize=6, color=colors['secondary'])
    
    # KOREAN NDC TARGETS (Bottom center, emphasized)
    ndc_x = 4
    ndc_width = 4
    ndc_height = 0.8
    
    ndc_box = Rectangle((ndc_x, 1.4), ndc_width, ndc_height,
                       facecolor=colors['highlight'], edgecolor='none', alpha=0.1)
    ax.add_patch(ndc_box)
    ndc_border = Rectangle((ndc_x, 1.4), ndc_width, ndc_height,
                          facecolor='none', edgecolor=colors['highlight'], linewidth=2)
    ax.add_patch(ndc_border)
    
    ax.text(ndc_x + ndc_width/2, 1.9, 'KOREAN NDC TARGETS', 
            ha='center', va='center', fontsize=9, fontweight='bold', color=colors['highlight'])
    ax.text(ndc_x + ndc_width/2, 1.6, '2030: 15%    2040: 50%    2050: 80% emission reduction', 
            ha='center', va='center', fontsize=8, color=colors['primary'])
    
    # PROFESSIONAL FLOW ARROWS
    arrow_props = dict(arrowstyle='->', lw=1.5, color=colors['secondary'])
    
    # Input to optimization
    ax.annotate('', xy=(opt_x - 0.1, 4.5), xytext=(input_x + input_width + 0.1, 4.5),
                arrowprops=arrow_props)
    
    # Optimization to output
    ax.annotate('', xy=(output_x - 0.1, 4.5), xytext=(opt_x + opt_width + 0.1, 4.5),
                arrowprops=arrow_props)
    
    # NDC targets to optimization (policy constraint)
    ax.annotate('', xy=(opt_x + opt_width/2, 2.4), xytext=(ndc_x + ndc_width/2, 1.4),
                arrowprops=dict(arrowstyle='->', lw=2, color=colors['highlight']))
    
    # Add subtle constraint arrows
    for y in [3.8, 3.55, 3.3, 3.05]:
        ax.annotate('', xy=(opt_x + opt_width - 0.1, y), xytext=(opt_x + opt_width + 0.3, y),
                    arrowprops=dict(arrowstyle='->', lw=0.8, color=colors['accent1'], alpha=0.6))
    
    # KEY RESULTS (Bottom)
    results_y = 0.7
    results_box = Rectangle((1, results_y - 0.3), 10, 0.5,
                           facecolor=colors['background'], edgecolor=colors['secondary'], 
                           linewidth=0.8, alpha=0.8)
    ax.add_patch(results_box)
    
    ax.text(6, results_y, 'KEY FINDINGS', ha='center', va='center', 
            fontsize=8, fontweight='bold', color=colors['primary'])
    results_text = ('2030 Target: Achievable via heat pump deployment (6.1 MtCO₂ reduction)  •  ' +
                   '2040/2050: Requires technology portfolio expansion  •  ' +
                   'Total viable options: 39 technology-facility combinations')
    ax.text(6, results_y - 0.15, results_text, ha='center', va='center', 
            fontsize=7, color=colors['secondary'])
    
    # Mathematical notation box (very subtle)
    notation_text = ('𝐅: facilities; 𝐓: technologies; 𝐏: processes; 𝑥ᶠᵗᵖ: deployment level; ' +
                    '𝑐ᶠᵗᵖ: annualized cost; 𝑎ᶠᵗᵖ: abatement potential')
    ax.text(6, 0.1, notation_text, ha='center', va='center', fontsize=6, 
            color=colors['secondary'], style='italic', alpha=0.7)
    
    # Add professional grid lines (very subtle)
    for y in [2.2, 4.4, 6.6]:
        ax.axhline(y=y, color=colors['secondary'], alpha=0.1, linewidth=0.5, zorder=0)
    
    # Add version/method identifier
    ax.text(11.8, 0.1, 'Linear Programming\nCBC Solver', ha='right', va='bottom', 
            fontsize=6, color=colors['secondary'], alpha=0.7)
    
    plt.tight_layout()
    return fig

def main():
    """Create and save professional model diagram"""
    
    print("Creating Professional Publication-Quality Korean Petrochemical MACC Model Diagram...")
    
    fig = create_professional_model_diagram()
    
    # Save in multiple formats for publication
    base_path = "outputs/Korean_MACC_Professional_Model_Diagram"
    
    # High-resolution PNG (for presentations, web)
    fig.savefig(f"{base_path}.png", dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none', format='png')
    
    # Vector PDF (for publication)
    fig.savefig(f"{base_path}.pdf", dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none', format='pdf')
    
    # EPS for some journals
    fig.savefig(f"{base_path}.eps", dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none', format='eps')
    
    # SVG for web/editing
    fig.savefig(f"{base_path}.svg", dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none', format='svg')
    
    print(f"✅ Professional model diagram saved in multiple formats:")
    print(f"   📊 PNG: {base_path}.png (presentations)")
    print(f"   📄 PDF: {base_path}.pdf (publication)")
    print(f"   📋 EPS: {base_path}.eps (journals)")
    print(f"   🌐 SVG: {base_path}.svg (web/editing)")
    print("🎯 Publication-ready for Nature Energy, Applied Energy, Energy Policy")
    
    plt.show()
    plt.close(fig)

if __name__ == "__main__":
    main()