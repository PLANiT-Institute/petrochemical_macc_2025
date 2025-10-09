import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class MACCVisualizer:
    """Create visualizations for MACC analysis results"""
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def plot_macc_curve(self, 
                       macc_df: pd.DataFrame, 
                       year: int,
                       title: Optional[str] = None,
                       save_path: Optional[str] = None) -> plt.Figure:
        """Create marginal abatement cost curve plot"""
        
        if macc_df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f'MACC Curve - {year}')
            return fig
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create bar chart
        bars = ax.bar(macc_df['Cumulative_Abatement_MtCO2'] - macc_df['Abatement_MtCO2']/2,
                     macc_df['LCOA_USD_per_tCO2'],
                     width=macc_df['Abatement_MtCO2'],
                     alpha=0.7,
                     edgecolor='black',
                     linewidth=0.5)
        
        # Color bars by process type
        process_types = macc_df['ProcessType'].unique()
        colors = sns.color_palette("husl", len(process_types))
        process_colors = dict(zip(process_types, colors))
        
        for bar, process in zip(bars, macc_df['ProcessType']):
            bar.set_facecolor(process_colors[process])
        
        # Formatting
        ax.set_xlabel('Cumulative Abatement Potential (MtCO₂)', fontsize=12)
        ax.set_ylabel('Levelized Cost of Abatement (USD/tCO₂)', fontsize=12)
        ax.set_title(title or f'Marginal Abatement Cost Curve - {year}', fontsize=14, fontweight='bold')
        
        # Add grid
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_axisbelow(True)
        
        # Add legend
        legend_elements = [plt.Rectangle((0,0),1,1, facecolor=process_colors[proc], 
                                       edgecolor='black', alpha=0.7, label=proc)
                          for proc in process_types]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        
        # Add cost reference lines
        cost_levels = [50, 100, 200, 500]
        for cost in cost_levels:
            if cost < ax.get_ylim()[1]:
                ax.axhline(y=cost, color='red', linestyle='--', alpha=0.5, linewidth=1)
                ax.text(ax.get_xlim()[1]*0.98, cost, f'${cost}/tCO₂', 
                       verticalalignment='bottom', horizontalalignment='right',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        elif title:
            filename = f"macc_curve_{year}.png"
            plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_deployment_timeline(self, 
                               deployment_df: pd.DataFrame,
                               save_path: Optional[str] = None) -> plt.Figure:
        """Plot technology deployment over time"""
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Top plot: Deployment by technology type
        deployment_by_type = deployment_df.groupby(['Year', 'TechType'])['Deployment_kt'].sum().unstack(fill_value=0)
        deployment_by_type.plot(kind='bar', stacked=True, ax=ax1, alpha=0.8)
        
        ax1.set_title('Technology Deployment by Type', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Deployment (kt/year)')
        ax1.legend(title='Technology Type', bbox_to_anchor=(1, 1))
        ax1.grid(True, alpha=0.3)
        
        # Bottom plot: Cumulative abatement
        abatement_by_year = deployment_df.groupby('Year')['Abatement_tCO2'].sum() / 1e6  # Convert to Mt
        cumulative_abatement = abatement_by_year.cumsum()
        
        ax2.plot(cumulative_abatement.index, cumulative_abatement.values, 
                marker='o', linewidth=3, markersize=8, color='darkgreen')
        ax2.fill_between(cumulative_abatement.index, cumulative_abatement.values, 
                        alpha=0.3, color='lightgreen')
        
        ax2.set_title('Cumulative Abatement Achievement', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Cumulative Abatement (MtCO₂)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(self.output_dir / "deployment_timeline.png", dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_cost_breakdown(self, 
                          annual_summary_df: pd.DataFrame,
                          save_path: Optional[str] = None) -> plt.Figure:
        """Plot cost breakdown over time"""
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))
        
        # Top: Annual costs
        years = annual_summary_df['Year']
        capex = annual_summary_df['Annual_CAPEX_Million_USD']
        opex = annual_summary_df['Annual_OPEX_Million_USD']
        
        ax1.bar(years, capex, label='CAPEX', alpha=0.8, color='steelblue')
        ax1.bar(years, opex, bottom=capex, label='OPEX', alpha=0.8, color='orange')
        
        ax1.set_title('Annual Investment Requirements', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Annual Cost (Million USD)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Middle: Abatement progress
        ax2.bar(years, annual_summary_df['Achieved_Abatement_MtCO2'], 
               label='Achieved', alpha=0.8, color='green')
        ax2.bar(years, annual_summary_df['Shortfall_MtCO2'], 
               bottom=annual_summary_df['Achieved_Abatement_MtCO2'],
               label='Shortfall', alpha=0.8, color='red')
        
        # Add required line
        ax2.plot(years, annual_summary_df['Required_Abatement_MtCO2'], 
                'k--', linewidth=2, label='Required')
        
        ax2.set_title('Abatement Achievement vs Requirements', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Abatement (MtCO₂)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Bottom: Cost effectiveness
        cost_effectiveness = []
        for _, row in annual_summary_df.iterrows():
            if row['Achieved_Abatement_MtCO2'] > 0:
                total_cost = row['Annual_CAPEX_Million_USD'] + row['Annual_OPEX_Million_USD']
                cost_per_tco2 = total_cost * 1e6 / (row['Achieved_Abatement_MtCO2'] * 1e6)  # USD/tCO2
                cost_effectiveness.append(cost_per_tco2)
            else:
                cost_effectiveness.append(0)
        
        ax3.plot(years, cost_effectiveness, 'o-', linewidth=2, markersize=8, color='purple')
        ax3.set_title('Annual Cost Effectiveness', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Cost per tCO₂ Abated (USD)')
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(self.output_dir / "cost_breakdown.png", dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_process_contribution(self, 
                                process_df: pd.DataFrame,
                                save_path: Optional[str] = None) -> plt.Figure:
        """Plot abatement contribution by process"""
        
        # Pivot data for stacked area chart
        pivot_df = process_df.pivot(index='Year', columns='ProcessType', values='Abatement_MtCO2')
        pivot_df = pivot_df.fillna(0)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create stacked area chart
        ax.stackplot(pivot_df.index, 
                    *[pivot_df[col] for col in pivot_df.columns],
                    labels=pivot_df.columns,
                    alpha=0.8)
        
        ax.set_title('Abatement Contribution by Process Type', fontsize=14, fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Abatement (MtCO₂)')
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(self.output_dir / "process_contribution.png", dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_emissions_pathway(self, 
                              pathway_df: pd.DataFrame,
                              save_path: Optional[str] = None) -> plt.Figure:
        """Plot emissions pathway from baseline to 2050"""
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
        
        # Top plot: Absolute emissions
        years = pathway_df['Year']
        
        ax1.plot(years, pathway_df['Baseline_Emissions_MtCO2'], 
                'k--', linewidth=2, label='Baseline (No Action)', alpha=0.7)
        ax1.plot(years, pathway_df['Target_Emissions_MtCO2'], 
                'r-', linewidth=3, label='Target Pathway', marker='o', markersize=4)
        ax1.plot(years, pathway_df['Actual_Emissions_MtCO2'], 
                'g-', linewidth=3, label='Optimized Pathway', marker='s', markersize=4)
        
        # Fill areas
        ax1.fill_between(years, pathway_df['Baseline_Emissions_MtCO2'], 
                        pathway_df['Actual_Emissions_MtCO2'], 
                        alpha=0.3, color='lightgreen', label='Abatement Achieved')
        
        ax1.set_title('Korea Petrochemical Emissions Pathway', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Emissions (MtCO₂)', fontsize=12)
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, None)
        
        # Add milestone annotations
        milestones = [2030, 2040, 2050]
        for year in milestones:
            if year in years.values:
                row = pathway_df[pathway_df['Year'] == year].iloc[0]
                reduction = row['Reduction_from_Baseline_Pct']
                ax1.annotate(f'{year}\\n{reduction:.0f}% reduction', 
                           xy=(year, row['Actual_Emissions_MtCO2']), 
                           xytext=(year, row['Actual_Emissions_MtCO2'] + 3),
                           ha='center', va='bottom',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                           arrowprops=dict(arrowstyle='->', color='black', alpha=0.7))
        
        # Bottom plot: Reduction percentage
        ax2.plot(years, pathway_df['Reduction_from_Baseline_Pct'], 
                'b-', linewidth=3, marker='o', markersize=6, label='Emission Reduction')
        ax2.axhline(y=80, color='red', linestyle='--', linewidth=2, alpha=0.7, label='80% Target')
        
        # Fill area under curve
        ax2.fill_between(years, 0, pathway_df['Reduction_from_Baseline_Pct'], 
                        alpha=0.3, color='lightblue')
        
        ax2.set_title('Emission Reduction Progress', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Year', fontsize=12)
        ax2.set_ylabel('Reduction from Baseline (%)', fontsize=12)
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 100)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(self.output_dir / "emissions_pathway.png", dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_production_shares(self, 
                             shares_df: pd.DataFrame,
                             process_type: str,
                             save_path: Optional[str] = None) -> plt.Figure:
        """Plot production share evolution for a specific process"""
        
        # Filter for specific process
        process_data = shares_df[shares_df['ProcessType'] == process_type].copy()
        
        if process_data.empty:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, f'No data available for {process_type}', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f'Production Share Evolution - {process_type}')
            return fig
        
        # Pivot data for stacked area chart
        pivot_df = process_data.pivot(index='Year', columns='TechnologyBand', values='Production_Share_Pct')
        pivot_df = pivot_df.fillna(0)
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Create stacked area chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(pivot_df.columns)))
        ax.stackplot(pivot_df.index, 
                    *[pivot_df[col] for col in pivot_df.columns],
                    labels=pivot_df.columns,
                    colors=colors,
                    alpha=0.8)
        
        ax.set_title(f'Technology Share Evolution - {process_type}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Production Share (%)', fontsize=12)
        ax.set_ylim(0, 100)
        
        # Legend with better formatting
        handles, labels = ax.get_legend_handles_labels()
        # Clean up labels for better readability
        clean_labels = []
        for label in labels:
            if process_type in label:
                clean_labels.append(label.replace(f'{process_type}_', ''))
            else:
                clean_labels.append(label)
        
        ax.legend(handles, clean_labels, loc='center left', bbox_to_anchor=(1, 0.5))
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            filename = f"production_shares_{process_type.lower()}.png"
            plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_all_production_shares(self, 
                                 shares_df: pd.DataFrame,
                                 save_path: Optional[str] = None) -> plt.Figure:
        """Plot production share evolution for all processes in a grid"""
        
        processes = shares_df['ProcessType'].unique()
        n_processes = len(processes)
        
        # Calculate grid dimensions
        cols = 3
        rows = (n_processes + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(20, 6*rows))
        axes = axes.flatten() if n_processes > 1 else [axes]
        
        for i, process_type in enumerate(processes):
            ax = axes[i]
            
            # Filter for specific process
            process_data = shares_df[shares_df['ProcessType'] == process_type].copy()
            
            if not process_data.empty:
                # Pivot data
                pivot_df = process_data.pivot(index='Year', columns='TechnologyBand', values='Production_Share_Pct')
                pivot_df = pivot_df.fillna(0)
                
                # Create stacked area chart
                colors = plt.cm.Set3(np.linspace(0, 1, len(pivot_df.columns)))
                ax.stackplot(pivot_df.index, 
                            *[pivot_df[col] for col in pivot_df.columns],
                            colors=colors,
                            alpha=0.8)
                
                ax.set_title(f'{process_type}', fontsize=12, fontweight='bold')
                ax.set_ylim(0, 100)
                ax.grid(True, alpha=0.3)
                
                if i >= (rows-1)*cols:  # Bottom row
                    ax.set_xlabel('Year')
                if i % cols == 0:  # Left column
                    ax.set_ylabel('Share (%)')
            else:
                ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
                ax.set_title(f'{process_type}', fontsize=12, fontweight='bold')
        
        # Hide unused subplots
        for i in range(n_processes, len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle('Technology Production Share Evolution by Process', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.savefig(self.output_dir / "production_shares_all.png", dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_dashboard(self, 
                        results_dict: Dict[str, pd.DataFrame],
                        year: int = 2030) -> plt.Figure:
        """Create comprehensive dashboard"""
        
        fig = plt.figure(figsize=(20, 16))
        
        # Create subplot grid
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. MACC Curve (top left, spans 2 columns)
        ax1 = fig.add_subplot(gs[0, :2])
        if 'macc_curve' in results_dict and not results_dict['macc_curve'].empty:
            macc_df = results_dict['macc_curve']
            bars = ax1.bar(macc_df['Cumulative_Abatement_MtCO2'] - macc_df['Abatement_MtCO2']/2,
                          macc_df['LCOA_USD_per_tCO2'],
                          width=macc_df['Abatement_MtCO2'],
                          alpha=0.7)
            ax1.set_xlabel('Cumulative Abatement (MtCO₂)')
            ax1.set_ylabel('LCOA (USD/tCO₂)')
            ax1.set_title(f'MACC Curve - {year}', fontweight='bold')
            ax1.grid(True, alpha=0.3)
        
        # 2. Deployment pie chart (top right)
        ax2 = fig.add_subplot(gs[0, 2])
        if 'deployment' in results_dict and not results_dict['deployment'].empty:
            deployment_by_type = results_dict['deployment'].groupby('TechType')['Deployment_kt'].sum()
            ax2.pie(deployment_by_type.values, labels=deployment_by_type.index, autopct='%1.1f%%')
            ax2.set_title('Deployment by Type', fontweight='bold')
        
        # 3. Annual costs (middle left)
        ax3 = fig.add_subplot(gs[1, 0])
        if 'annual_summary' in results_dict:
            summary_df = results_dict['annual_summary']
            ax3.bar(summary_df['Year'], summary_df['Annual_CAPEX_Million_USD'], 
                   label='CAPEX', alpha=0.8)
            ax3.bar(summary_df['Year'], summary_df['Annual_OPEX_Million_USD'], 
                   bottom=summary_df['Annual_CAPEX_Million_USD'], 
                   label='OPEX', alpha=0.8)
            ax3.set_title('Annual Costs', fontweight='bold')
            ax3.set_ylabel('Million USD')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # 4. Target achievement (middle center)
        ax4 = fig.add_subplot(gs[1, 1])
        if 'annual_summary' in results_dict:
            summary_df = results_dict['annual_summary']
            achievement_rate = summary_df['Achieved_Abatement_MtCO2'] / summary_df['Required_Abatement_MtCO2']
            ax4.plot(summary_df['Year'], achievement_rate * 100, 'o-', linewidth=2)
            ax4.axhline(y=100, color='red', linestyle='--', label='Target')
            ax4.set_title('Target Achievement', fontweight='bold')
            ax4.set_ylabel('Achievement Rate (%)')
            ax4.grid(True, alpha=0.3)
            ax4.legend()
        
        # 5. Process breakdown (middle right)
        ax5 = fig.add_subplot(gs[1, 2])
        if 'process_breakdown' in results_dict and not results_dict['process_breakdown'].empty:
            process_df = results_dict['process_breakdown']
            latest_year_data = process_df[process_df['Year'] == process_df['Year'].max()]
            ax5.pie(latest_year_data['Abatement_MtCO2'], 
                   labels=latest_year_data['ProcessType'], 
                   autopct='%1.1f%%')
            ax5.set_title('Process Contribution', fontweight='bold')
        
        # 6. Technology timeline (bottom, spans all columns)
        ax6 = fig.add_subplot(gs[2, :])
        if 'deployment' in results_dict and not results_dict['deployment'].empty:
            deployment_timeline = results_dict['deployment'].groupby(['Year', 'ProcessType'])['Deployment_kt'].sum().unstack(fill_value=0)
            deployment_timeline.plot(kind='area', stacked=True, ax=ax6, alpha=0.7)
            ax6.set_title('Deployment Timeline by Process', fontweight='bold')
            ax6.set_xlabel('Year')
            ax6.set_ylabel('Deployment (kt)')
            ax6.legend(bbox_to_anchor=(1, 1))
            ax6.grid(True, alpha=0.3)
        
        plt.suptitle('Korea Petrochemical MACC Analysis Dashboard', fontsize=16, fontweight='bold', y=0.98)
        
        # Save dashboard
        plt.savefig(self.output_dir / f"dashboard_{year}.png", dpi=300, bbox_inches='tight')
        
        return fig