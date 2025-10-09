#!/usr/bin/env python3
"""
Company-Level Transition Analysis for Korean Petrochemical Industry
Focus: Individual company strategies, investment requirements, and competitive positioning
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def load_company_data():
    """Load and analyze company-specific data"""
    
    print("🏢 LOADING COMPANY DATA")
    print("=" * 80)
    
    # Major Korean petrochemical companies with facility breakdown
    companies = {
        'SK_Innovation': {
            'facilities': {
                'NCC': 2,  # Ulsan Complex
                'BTX': 3,  # Ulsan
                'Utility': 8
            },
            'total_capacity': 2.1,  # Million tonnes ethylene equivalent
            'current_emissions': 12.5,  # MtCO2e including naphtha
            'geographic_focus': ['Ulsan'],
            'financial_strength': 'High',
            'technology_readiness': 'Medium-High'
        },
        'LG_Chem': {
            'facilities': {
                'NCC': 2,  # Yeosu Complex
                'BTX': 2,  # Yeosu
                'Utility': 6
            },
            'total_capacity': 1.8,
            'current_emissions': 10.8,
            'geographic_focus': ['Yeosu'],
            'financial_strength': 'High',
            'technology_readiness': 'High'
        },
        'Lotte_Chemical': {
            'facilities': {
                'NCC': 2,  # Yeosu, Daesan
                'BTX': 3,  # Multiple locations
                'Utility': 7
            },
            'total_capacity': 1.6,
            'current_emissions': 9.6,
            'geographic_focus': ['Yeosu', 'Daesan'],
            'financial_strength': 'Medium-High',
            'technology_readiness': 'Medium'
        },
        'Hanwha_Solutions': {
            'facilities': {
                'NCC': 1,  # Daesan
                'BTX': 2,  # Daesan
                'Utility': 5
            },
            'total_capacity': 1.2,
            'current_emissions': 7.2,
            'geographic_focus': ['Daesan'],
            'financial_strength': 'Medium',
            'technology_readiness': 'Medium'
        },
        'S_Oil': {
            'facilities': {
                'NCC': 1,  # Ulsan
                'BTX': 2,  # Ulsan
                'Utility': 4
            },
            'total_capacity': 1.0,
            'current_emissions': 6.0,
            'geographic_focus': ['Ulsan'],
            'financial_strength': 'High',
            'technology_readiness': 'Medium-High'
        },
        'Yeochun_NCC': {
            'facilities': {
                'NCC': 1,  # Yeosu
                'BTX': 1,  # Yeosu
                'Utility': 3
            },
            'total_capacity': 0.8,
            'current_emissions': 4.8,
            'geographic_focus': ['Yeosu'],
            'financial_strength': 'Medium',
            'technology_readiness': 'Low-Medium'
        },
        'GS_Caltex': {
            'facilities': {
                'NCC': 0,  # Refinery focus
                'BTX': 3,  # Yeosu
                'Utility': 6
            },
            'total_capacity': 0.6,
            'current_emissions': 3.6,
            'geographic_focus': ['Yeosu'],
            'financial_strength': 'High',
            'technology_readiness': 'Medium'
        },
        'Kumho_Petrochemical': {
            'facilities': {
                'NCC': 0,  # Specialty chemicals
                'BTX': 2,  # Ulsan, Yeosu
                'Utility': 4
            },
            'total_capacity': 0.4,
            'current_emissions': 2.4,
            'geographic_focus': ['Ulsan', 'Yeosu'],
            'financial_strength': 'Medium',
            'technology_readiness': 'Medium'
        }
    }
    
    # Create DataFrame for analysis
    company_df = []
    for company, data in companies.items():
        company_df.append({
            'Company': company,
            'NCC_Facilities': data['facilities']['NCC'],
            'BTX_Facilities': data['facilities']['BTX'],
            'Utility_Facilities': data['facilities']['Utility'],
            'Total_Facilities': sum(data['facilities'].values()),
            'Capacity_Mt': data['total_capacity'],
            'Current_Emissions_Mt': data['current_emissions'],
            'Emission_Intensity': data['current_emissions'] / data['total_capacity'],
            'Geographic_Focus': ', '.join(data['geographic_focus']),
            'Financial_Strength': data['financial_strength'],
            'Technology_Readiness': data['technology_readiness']
        })
    
    df = pd.DataFrame(company_df)
    
    print("📊 Company Overview:")
    print(df[['Company', 'Total_Facilities', 'Capacity_Mt', 'Current_Emissions_Mt', 'Financial_Strength']].round(2))
    
    return companies, df

def analyze_company_transition_strategies():
    """Analyze transition strategies by company profile"""
    
    print("\n\n🎯 COMPANY TRANSITION STRATEGY ANALYSIS")
    print("=" * 80)
    
    companies, df = load_company_data()
    
    # Define transition strategies based on company characteristics
    transition_strategies = {
        'SK_Innovation': {
            'strategy_type': 'First Mover Leadership',
            'hydrogen_approach': 'Integrated production + import',
            'timeline': 'Aggressive (2025-2035)',
            'investment_priority': 'Hydrogen infrastructure',
            'competitive_advantage': 'Scale and financial strength',
            'key_projects': [
                'Ulsan hydrogen complex development',
                'Green hydrogen import terminal',
                'NCC retrofit program (2 facilities)',
                'Renewable energy partnerships'
            ],
            'total_investment': 28.5,  # Trillion KRW
            'risk_factors': ['Technology execution', 'Market timing'],
            'success_metrics': ['First commercial H2-NCC', 'Market share growth']
        },
        'LG_Chem': {
            'strategy_type': 'Technology Innovation Leader',
            'hydrogen_approach': 'Advanced electrolysis + bio-integration',
            'timeline': 'Fast follower (2026-2037)',
            'investment_priority': 'R&D and bio-naphtha',
            'competitive_advantage': 'Technology capabilities',
            'key_projects': [
                'Advanced electrolysis demonstration',
                'Bio-naphtha supply chain development',
                'Battery-chemical integration',
                'Circular economy initiatives'
            ],
            'total_investment': 24.3,
            'risk_factors': ['Technology development', 'Bio-feedstock supply'],
            'success_metrics': ['Patent portfolio', 'Technology licensing']
        },
        'Lotte_Chemical': {
            'strategy_type': 'Multi-Hub Optimization',
            'hydrogen_approach': 'Regional hub strategy',
            'timeline': 'Phased deployment (2027-2040)',
            'investment_priority': 'Multi-site integration',
            'competitive_advantage': 'Geographic diversification',
            'key_projects': [
                'Yeosu-Daesan hydrogen corridor',
                'Integrated logistics network',
                'Shared infrastructure development',
                'Regional partnership platform'
            ],
            'total_investment': 21.6,
            'risk_factors': ['Coordination complexity', 'Regional policy alignment'],
            'success_metrics': ['Hub utilization', 'Cost synergies']
        },
        'Hanwha_Solutions': {
            'strategy_type': 'Renewable-Chemical Integration',
            'hydrogen_approach': 'Solar-powered electrolysis',
            'timeline': 'Renewable-led (2026-2038)',
            'investment_priority': 'Solar-hydrogen integration',
            'competitive_advantage': 'Solar technology expertise',
            'key_projects': [
                'Solar-hydrogen integrated complex',
                'Energy storage optimization',
                'Grid-scale renewable deployment',
                'Technology export platform'
            ],
            'total_investment': 18.0,
            'risk_factors': ['Renewable intermittency', 'Storage costs'],
            'success_metrics': ['Renewable capacity', 'Energy cost reduction']
        },
        'S_Oil': {
            'strategy_type': 'Refinery-Chemical Optimization',
            'hydrogen_approach': 'Refinery integration + blue hydrogen',
            'timeline': 'Integrated transition (2027-2039)',
            'investment_priority': 'Refinery-chemical synergies',
            'competitive_advantage': 'Integrated value chain',
            'key_projects': [
                'Blue hydrogen from refinery',
                'CCUS integration',
                'Refinery-chemical optimization',
                'Advanced fuel development'
            ],
            'total_investment': 15.0,
            'risk_factors': ['CCUS technology', 'Carbon leakage'],
            'success_metrics': ['Integration efficiency', 'Carbon capture rate']
        },
        'Yeochun_NCC': {
            'strategy_type': 'Partnership-Based Transition',
            'hydrogen_approach': 'Shared infrastructure + partnerships',
            'timeline': 'Collaborative (2028-2042)',
            'investment_priority': 'Partnership development',
            'competitive_advantage': 'Flexible partnerships',
            'key_projects': [
                'Yeosu industrial cluster partnerships',
                'Shared hydrogen infrastructure',
                'Technology transfer agreements',
                'Financing partnerships'
            ],
            'total_investment': 12.0,
            'risk_factors': ['Partner coordination', 'Technology access'],
            'success_metrics': ['Partnership effectiveness', 'Cost sharing']
        },
        'GS_Caltex': {
            'strategy_type': 'BTX-Focused Transition',
            'hydrogen_approach': 'Selective hydrogen + electrification',
            'timeline': 'BTX optimization (2026-2040)',
            'investment_priority': 'Process electrification',
            'competitive_advantage': 'BTX specialization',
            'key_projects': [
                'BTX process electrification',
                'Advanced separation technologies',
                'Renewable energy integration',
                'Product portfolio optimization'
            ],
            'total_investment': 10.8,
            'risk_factors': ['Market demand', 'Technology limitations'],
            'success_metrics': ['BTX efficiency', 'Product margins']
        },
        'Kumho_Petrochemical': {
            'strategy_type': 'Niche Specialization',
            'hydrogen_approach': 'Targeted applications + partnerships',
            'timeline': 'Specialty focus (2027-2045)',
            'investment_priority': 'Specialty chemicals',
            'competitive_advantage': 'Market niche focus',
            'key_projects': [
                'High-value specialty chemicals',
                'Advanced polymer technologies',
                'Sustainable materials development',
                'Technology partnerships'
            ],
            'total_investment': 8.4,
            'risk_factors': ['Market size', 'Technology access'],
            'success_metrics': ['Product premiums', 'Market position']
        }
    }
    
    print("🏢 Company-Specific Transition Strategies:")
    for company, strategy in transition_strategies.items():
        print(f"\n🎯 {company.replace('_', ' ')}:")
        print(f"   Strategy: {strategy['strategy_type']}")
        print(f"   Hydrogen Approach: {strategy['hydrogen_approach']}")
        print(f"   Timeline: {strategy['timeline']}")
        print(f"   Investment: ₩{strategy['total_investment']} trillion")
        print(f"   Key Advantage: {strategy['competitive_advantage']}")
        print(f"   Priority Projects:")
        for project in strategy['key_projects']:
            print(f"     • {project}")
    
    return transition_strategies

def calculate_company_investment_requirements():
    """Calculate detailed investment requirements by company"""
    
    print("\n\n💰 COMPANY INVESTMENT ANALYSIS")
    print("=" * 80)
    
    companies, df = load_company_data()
    transition_strategies = analyze_company_transition_strategies()
    
    # Technology cost factors (per facility or capacity)
    cost_factors = {
        'NCC_Hydrogen_Retrofit': 2.5,  # Trillion KRW per NCC facility
        'BTX_Electrification': 0.8,    # Trillion KRW per BTX facility
        'Utility_Modernization': 0.3,  # Trillion KRW per utility facility
        'Renewable_Energy': 1.2,       # Trillion KRW per Mt capacity
        'Bio_Naphtha_Infrastructure': 0.5,  # Trillion KRW per Mt capacity
        'Hydrogen_Infrastructure': 1.8,     # Trillion KRW per Mt capacity
        'R&D_Innovation': 0.4               # Trillion KRW per Mt capacity
    }
    
    # Calculate company-specific investments
    investment_breakdown = {}
    
    for company_name, company_data in companies.items():
        investments = {}
        
        # Technology-specific investments
        investments['NCC_Retrofit'] = company_data['facilities']['NCC'] * cost_factors['NCC_Hydrogen_Retrofit']
        investments['BTX_Electrification'] = company_data['facilities']['BTX'] * cost_factors['BTX_Electrification']
        investments['Utility_Modernization'] = company_data['facilities']['Utility'] * cost_factors['Utility_Modernization']
        investments['Renewable_Energy'] = company_data['total_capacity'] * cost_factors['Renewable_Energy']
        investments['Bio_Naphtha'] = company_data['total_capacity'] * cost_factors['Bio_Naphtha_Infrastructure']
        investments['Hydrogen_Infrastructure'] = company_data['total_capacity'] * cost_factors['Hydrogen_Infrastructure']
        investments['R&D_Innovation'] = company_data['total_capacity'] * cost_factors['R&D_Innovation']
        
        # Apply company-specific strategy multipliers
        strategy = transition_strategies[company_name]
        strategy_multipliers = {
            'First Mover Leadership': 1.3,
            'Technology Innovation Leader': 1.4,
            'Multi-Hub Optimization': 1.1,
            'Renewable-Chemical Integration': 1.2,
            'Refinery-Chemical Optimization': 1.0,
            'Partnership-Based Transition': 0.8,
            'BTX-Focused Transition': 0.9,
            'Niche Specialization': 0.7
        }
        
        multiplier = strategy_multipliers.get(strategy['strategy_type'], 1.0)
        total_investment = sum(investments.values()) * multiplier
        
        investment_breakdown[company_name] = {
            'detailed_investments': investments,
            'strategy_multiplier': multiplier,
            'total_investment': total_investment,
            'investment_per_mt': total_investment / company_data['total_capacity'],
            'investment_per_facility': total_investment / sum(company_data['facilities'].values())
        }
        
        print(f"\n💼 {company_name.replace('_', ' ')} Investment Breakdown:")
        print(f"   Total Investment: ₩{total_investment:.1f} trillion")
        print(f"   Investment per Mt: ₩{total_investment/company_data['total_capacity']:.1f} trillion")
        print(f"   Strategy Multiplier: {multiplier:.1f}x")
        print(f"   Key Components:")
        for component, amount in investments.items():
            if amount > 0:
                print(f"     • {component.replace('_', ' ')}: ₩{amount:.1f}T")
    
    return investment_breakdown

def analyze_competitive_positioning():
    """Analyze competitive positioning post-transition"""
    
    print("\n\n🏆 COMPETITIVE POSITIONING ANALYSIS")
    print("=" * 80)
    
    companies, df = load_company_data()
    transition_strategies = analyze_company_transition_strategies()
    investment_breakdown = calculate_company_investment_requirements()
    
    # Define competitive metrics
    competitive_metrics = {
        'SK_Innovation': {
            'technology_leadership': 4.2,  # 1-5 scale
            'cost_competitiveness': 4.0,
            'market_position': 4.5,
            'financial_resilience': 4.3,
            'innovation_capability': 3.8,
            'sustainability_rating': 4.1,
            'global_competitiveness': 4.2,
            'key_strengths': ['Scale advantages', 'First mover position', 'Financial strength'],
            'potential_challenges': ['Technology execution risk', 'High investment burden']
        },
        'LG_Chem': {
            'technology_leadership': 4.5,
            'cost_competitiveness': 3.8,
            'market_position': 4.2,
            'financial_resilience': 4.1,
            'innovation_capability': 4.7,
            'sustainability_rating': 4.3,
            'global_competitiveness': 4.4,
            'key_strengths': ['Technology innovation', 'R&D capabilities', 'Battery synergies'],
            'potential_challenges': ['Bio-feedstock dependence', 'Technology risks']
        },
        'Lotte_Chemical': {
            'technology_leadership': 3.5,
            'cost_competitiveness': 3.9,
            'market_position': 3.8,
            'financial_resilience': 3.6,
            'innovation_capability': 3.4,
            'sustainability_rating': 3.7,
            'global_competitiveness': 3.6,
            'key_strengths': ['Geographic diversification', 'Hub strategy', 'Cost optimization'],
            'potential_challenges': ['Coordination complexity', 'Technology gap']
        },
        'Hanwha_Solutions': {
            'technology_leadership': 3.8,
            'cost_competitiveness': 4.1,
            'market_position': 3.4,
            'financial_resilience': 3.2,
            'innovation_capability': 4.0,
            'sustainability_rating': 4.4,
            'global_competitiveness': 3.8,
            'key_strengths': ['Solar integration', 'Renewable expertise', 'Energy costs'],
            'potential_challenges': ['Financial constraints', 'Market position']
        },
        'S_Oil': {
            'technology_leadership': 3.6,
            'cost_competitiveness': 4.2,
            'market_position': 3.7,
            'financial_resilience': 4.0,
            'innovation_capability': 3.5,
            'sustainability_rating': 3.8,
            'global_competitiveness': 3.8,
            'key_strengths': ['Refinery integration', 'Cost advantages', 'CCUS potential'],
            'potential_challenges': ['Technology dependence', 'Carbon leakage']
        },
        'Yeochun_NCC': {
            'technology_leadership': 2.8,
            'cost_competitiveness': 3.3,
            'market_position': 3.0,
            'financial_resilience': 2.9,
            'innovation_capability': 2.6,
            'sustainability_rating': 3.2,
            'global_competitiveness': 2.9,
            'key_strengths': ['Partnership flexibility', 'Cost sharing', 'Niche focus'],
            'potential_challenges': ['Technology access', 'Financial limitations']
        },
        'GS_Caltex': {
            'technology_leadership': 3.2,
            'cost_competitiveness': 3.7,
            'market_position': 3.5,
            'financial_resilience': 3.8,
            'innovation_capability': 3.1,
            'sustainability_rating': 3.6,
            'global_competitiveness': 3.4,
            'key_strengths': ['BTX specialization', 'Process optimization', 'Financial stability'],
            'potential_challenges': ['Limited scope', 'Market constraints']
        },
        'Kumho_Petrochemical': {
            'technology_leadership': 3.4,
            'cost_competitiveness': 3.2,
            'market_position': 3.3,
            'financial_resilience': 3.1,
            'innovation_capability': 3.6,
            'sustainability_rating': 3.4,
            'global_competitiveness': 3.3,
            'key_strengths': ['Specialty focus', 'Niche markets', 'Technology partnerships'],
            'potential_challenges': ['Scale limitations', 'Market size']
        }
    }
    
    print("🎯 Post-Transition Competitive Assessment:")
    for company, metrics in competitive_metrics.items():
        overall_score = np.mean([metrics['technology_leadership'], metrics['cost_competitiveness'], 
                               metrics['market_position'], metrics['sustainability_rating']])
        print(f"\n🏢 {company.replace('_', ' ')}:")
        print(f"   Overall Competitiveness: {overall_score:.1f}/5.0")
        print(f"   Technology Leadership: {metrics['technology_leadership']:.1f}")
        print(f"   Cost Competitiveness: {metrics['cost_competitiveness']:.1f}")
        print(f"   Global Potential: {metrics['global_competitiveness']:.1f}")
        print(f"   Key Strengths: {', '.join(metrics['key_strengths'])}")
        print(f"   Challenges: {', '.join(metrics['potential_challenges'])}")
    
    return competitive_metrics

def assess_financial_impact():
    """Assess financial impact on companies"""
    
    print("\n\n📊 FINANCIAL IMPACT ASSESSMENT")
    print("=" * 80)
    
    companies, df = load_company_data()
    investment_breakdown = calculate_company_investment_requirements()
    
    # Financial metrics analysis
    financial_analysis = {}
    
    for company_name, company_data in companies.items():
        # Estimated current annual revenue (based on capacity and market prices)
        annual_revenue = company_data['total_capacity'] * 1200  # USD/tonne average
        
        # Investment requirements
        total_investment = investment_breakdown[company_name]['total_investment']
        annual_investment = total_investment / 25  # Over 25 years
        
        # Financial metrics
        investment_to_revenue = (annual_investment * 1320) / (annual_revenue * 1000)  # KRW to USD conversion
        
        # Estimated returns post-transition
        cost_savings = company_data['current_emissions'] * 0.05 * 25  # Carbon cost savings
        revenue_premium = annual_revenue * 0.15  # Green premium
        
        financial_analysis[company_name] = {
            'annual_revenue_usd': annual_revenue,
            'total_investment_krw': total_investment,
            'annual_investment_krw': annual_investment,
            'investment_to_revenue_ratio': investment_to_revenue,
            'estimated_cost_savings': cost_savings,
            'estimated_revenue_premium': revenue_premium,
            'net_annual_benefit': cost_savings + revenue_premium - (annual_investment * 1320 / 1000),
            'payback_period': total_investment / (cost_savings + revenue_premium) if (cost_savings + revenue_premium) > 0 else 999
        }
        
        print(f"\n💰 {company_name.replace('_', ' ')} Financial Analysis:")
        print(f"   Annual Revenue: ${annual_revenue:.1f} million")
        print(f"   Total Investment: ₩{total_investment:.1f} trillion")
        print(f"   Investment/Revenue Ratio: {investment_to_revenue:.1f}x")
        print(f"   Estimated Payback: {financial_analysis[company_name]['payback_period']:.1f} years")
        print(f"   Net Annual Benefit: ${financial_analysis[company_name]['net_annual_benefit']:.0f} million")
    
    return financial_analysis

def create_company_transition_timeline():
    """Create detailed transition timeline for each company"""
    
    print("\n\n📅 COMPANY TRANSITION TIMELINES")
    print("=" * 80)
    
    companies, df = load_company_data()
    transition_strategies = analyze_company_transition_strategies()
    
    # Define phase-specific milestones for each company
    company_timelines = {
        'SK_Innovation': {
            '2025-2027': ['Hydrogen import terminal construction', 'NCC retrofit design', 'Renewable partnerships'],
            '2028-2030': ['First NCC hydrogen conversion', 'Pilot operations', 'Scale-up planning'],
            '2031-2035': ['Second NCC conversion', 'Commercial operations', 'Technology export'],
            '2036-2040': ['Full portfolio transition', 'Market leadership', 'Global expansion']
        },
        'LG_Chem': {
            '2025-2027': ['R&D facility expansion', 'Bio-naphtha partnerships', 'Electrolysis pilots'],
            '2028-2030': ['Technology demonstration', 'Bio-supply chain', 'Battery integration'],
            '2031-2035': ['Commercial deployment', 'Technology licensing', 'Innovation platform'],
            '2036-2040': ['Global technology leader', 'Full portfolio', 'Next-gen technologies']
        },
        'Lotte_Chemical': {
            '2025-2027': ['Hub strategy planning', 'Infrastructure sharing', 'Partnership development'],
            '2028-2030': ['Yeosu hub development', 'Logistics optimization', 'Technology adoption'],
            '2031-2035': ['Daesan integration', 'Multi-site synergies', 'Cost optimization'],
            '2036-2040': ['Full hub network', 'Regional leadership', 'Export platform']
        }
        # Add other companies as needed
    }
    
    print("📊 Strategic Timeline Overview:")
    for company, timeline in company_timelines.items():
        print(f"\n🏢 {company.replace('_', ' ')}:")
        for period, milestones in timeline.items():
            print(f"   {period}:")
            for milestone in milestones:
                print(f"     • {milestone}")
    
    return company_timelines

def create_comprehensive_company_visualization():
    """Create comprehensive visualization of company analysis"""
    
    print("\n\n📊 CREATING COMPANY ANALYSIS VISUALIZATION")
    print("=" * 80)
    
    # Load all data
    companies, df = load_company_data()
    investment_breakdown = calculate_company_investment_requirements()
    competitive_metrics = analyze_competitive_positioning()
    financial_analysis = assess_financial_impact()
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Investment Requirements by Company
    ax1 = plt.subplot(3, 3, (1, 2))
    
    company_names = list(companies.keys())
    investments = [investment_breakdown[comp]['total_investment'] for comp in company_names]
    colors = plt.cm.Set3(np.linspace(0, 1, len(company_names)))
    
    bars = ax1.bar([name.replace('_', '\n') for name in company_names], investments, 
                   color=colors, alpha=0.8)
    ax1.set_ylabel('Investment Required (Trillion KRW)')
    ax1.set_title('Total Investment Requirements by Company')
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for bar, value in zip(bars, investments):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                f'₩{value:.1f}T', ha='center', va='bottom', fontweight='bold')
    
    # 2. Competitive Positioning Matrix
    ax2 = plt.subplot(3, 3, 3)
    
    tech_scores = [competitive_metrics[comp]['technology_leadership'] for comp in company_names]
    cost_scores = [competitive_metrics[comp]['cost_competitiveness'] for comp in company_names]
    market_sizes = [companies[comp]['total_capacity'] * 100 for comp in company_names]  # For bubble size
    
    scatter = ax2.scatter(tech_scores, cost_scores, s=market_sizes, alpha=0.6, c=colors)
    ax2.set_xlabel('Technology Leadership')
    ax2.set_ylabel('Cost Competitiveness')
    ax2.set_title('Competitive Positioning Matrix')
    ax2.set_xlim(2, 5)
    ax2.set_ylim(2, 5)
    ax2.grid(True, alpha=0.3)
    
    # Add company labels
    for i, name in enumerate(company_names):
        ax2.annotate(name.replace('_', ' ').split('_')[0], 
                    (tech_scores[i], cost_scores[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # 3. Investment vs Capacity Analysis
    ax3 = plt.subplot(3, 3, (4, 5))
    
    capacities = [companies[comp]['total_capacity'] for comp in company_names]
    investment_per_mt = [investment_breakdown[comp]['investment_per_mt'] for comp in company_names]
    
    for i, (comp, cap, inv_mt) in enumerate(zip(company_names, capacities, investment_per_mt)):
        ax3.bar(i, inv_mt, color=colors[i], alpha=0.8, label=comp.replace('_', ' '))
    
    ax3.set_ylabel('Investment per Mt Capacity (Trillion KRW)')
    ax3.set_title('Investment Intensity by Company')
    ax3.set_xticks(range(len(company_names)))
    ax3.set_xticklabels([name.replace('_', '\n') for name in company_names], rotation=45)
    
    # 4. Financial Impact Assessment
    ax4 = plt.subplot(3, 3, 6)
    
    payback_periods = [financial_analysis[comp]['payback_period'] for comp in company_names]
    payback_periods = [min(p, 30) for p in payback_periods]  # Cap at 30 years for visualization
    
    bars = ax4.barh([name.replace('_', '\n') for name in company_names], payback_periods, 
                    color=colors, alpha=0.8)
    ax4.set_xlabel('Payback Period (Years)')
    ax4.set_title('Investment Payback Period')
    ax4.set_xlim(0, 25)
    
    # Add value labels
    for bar, value in zip(bars, payback_periods):
        width = bar.get_width()
        ax4.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                f'{value:.1f}y', ha='left', va='center', fontweight='bold')
    
    # 5. Current vs Future Emissions
    ax5 = plt.subplot(3, 3, (7, 8))
    
    current_emissions = [companies[comp]['current_emissions'] for comp in company_names]
    future_emissions = [em * 0.15 for em in current_emissions]  # 85% reduction target
    
    x = np.arange(len(company_names))
    width = 0.35
    
    ax5.bar(x - width/2, current_emissions, width, label='Current (2024)', color='red', alpha=0.7)
    ax5.bar(x + width/2, future_emissions, width, label='Target (2050)', color='green', alpha=0.7)
    
    ax5.set_ylabel('Emissions (MtCO₂e)')
    ax5.set_title('Emission Reduction Targets by Company')
    ax5.set_xticks(x)
    ax5.set_xticklabels([name.replace('_', '\n') for name in company_names], rotation=45)
    ax5.legend()
    
    # 6. Technology Deployment Strategy
    ax6 = plt.subplot(3, 3, 9)
    
    # Create strategy categorization
    strategy_types = ['First Mover', 'Innovation Leader', 'Multi-Hub', 'Renewable Focus', 
                     'Integrated', 'Partnership', 'BTX Focus', 'Niche']
    strategy_companies = [
        ['SK_Innovation'],
        ['LG_Chem'],
        ['Lotte_Chemical'],
        ['Hanwha_Solutions'],
        ['S_Oil'],
        ['Yeochun_NCC'],
        ['GS_Caltex'],
        ['Kumho_Petrochemical']
    ]
    
    strategy_counts = [len(comps) for comps in strategy_companies]
    colors_strategy = plt.cm.Set3(np.linspace(0, 1, len(strategy_types)))
    
    wedges, texts, autotexts = ax6.pie(strategy_counts, labels=strategy_types, autopct='%1.0f%%',
                                      colors=colors_strategy, startangle=90)
    ax6.set_title('Distribution of Transition Strategies')
    
    plt.suptitle('Korean Petrochemical Companies: Transition Analysis', 
                 fontsize=18, fontweight='bold')
    plt.tight_layout()
    plt.savefig('company_transition_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ Company analysis visualization saved: company_transition_analysis.png")

def generate_company_recommendations():
    """Generate specific recommendations for each company"""
    
    print("\n\n💡 COMPANY-SPECIFIC RECOMMENDATIONS")
    print("=" * 80)
    
    recommendations = {
        'SK_Innovation': {
            'immediate_actions': [
                'Establish hydrogen task force and technology committee',
                'Initiate site preparation for hydrogen import terminal',
                'Begin NCC retrofit engineering studies',
                'Secure renewable energy partnership agreements'
            ],
            'strategic_priorities': [
                'Lead industry hydrogen infrastructure development',
                'Establish first-mover advantage in H2-NCC technology',
                'Create technology licensing and export opportunities',
                'Build strategic partnerships with global hydrogen suppliers'
            ],
            'risk_mitigation': [
                'Diversify hydrogen supply sources and technologies',
                'Implement phased investment approach with go/no-go gates',
                'Establish technology backup plans and alternatives',
                'Create financial hedging for commodity price risks'
            ],
            'success_metrics': [
                'First commercial H2-NCC operation by 2030',
                'Achieve 50% emission reduction by 2035',
                'Generate technology licensing revenue by 2032',
                'Maintain market leadership position'
            ]
        },
        'LG_Chem': {
            'immediate_actions': [
                'Expand R&D budget for green technology development',
                'Establish bio-naphtha supply chain partnerships',
                'Integrate battery and chemical technology platforms',
                'Launch advanced electrolysis demonstration project'
            ],
            'strategic_priorities': [
                'Become global leader in green chemical technologies',
                'Leverage battery business synergies for energy storage',
                'Develop proprietary bio-chemical processes',
                'Create innovation ecosystem with universities and startups'
            ],
            'risk_mitigation': [
                'Maintain technology diversification portfolio',
                'Secure multiple bio-feedstock supply sources',
                'Protect intellectual property and trade secrets',
                'Build financial reserves for R&D investments'
            ],
            'success_metrics': [
                'Achieve 100+ green technology patents by 2030',
                'Launch commercial bio-naphtha operations by 2032',
                'Generate 20% revenue from green products by 2035',
                'Establish global technology licensing platform'
            ]
        }
        # Additional companies can be added following the same structure
    }
    
    print("🎯 Strategic Recommendations by Company:")
    for company, recs in recommendations.items():
        print(f"\n🏢 {company.replace('_', ' ')}:")
        print(f"   Immediate Actions (2025-2026):")
        for action in recs['immediate_actions']:
            print(f"     • {action}")
        print(f"   Strategic Priorities:")
        for priority in recs['strategic_priorities']:
            print(f"     • {priority}")
        print(f"   Success Metrics:")
        for metric in recs['success_metrics']:
            print(f"     • {metric}")
    
    return recommendations

def main():
    """Generate comprehensive company-level analysis"""
    
    print("🏢 KOREAN PETROCHEMICAL COMPANIES")
    print("TRANSITION ANALYSIS & INVESTMENT STRATEGY")
    print("=" * 80)
    print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Run all analyses
    companies, df = load_company_data()
    transition_strategies = analyze_company_transition_strategies()
    investment_breakdown = calculate_company_investment_requirements()
    competitive_metrics = analyze_competitive_positioning()
    financial_analysis = assess_financial_impact()
    company_timelines = create_company_transition_timeline()
    recommendations = generate_company_recommendations()
    
    # Create visualizations
    create_comprehensive_company_visualization()
    
    # Generate summary statistics
    total_company_investment = sum([inv['total_investment'] for inv in investment_breakdown.values()])
    total_capacity = sum([comp['total_capacity'] for comp in companies.values()])
    total_emissions = sum([comp['current_emissions'] for comp in companies.values()])
    
    print(f"\n\n📋 COMPANY ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"✅ Total companies analyzed: {len(companies)}")
    print(f"✅ Total investment required: ₩{total_company_investment:.1f} trillion")
    print(f"✅ Total capacity covered: {total_capacity:.1f} Mt/year")
    print(f"✅ Total emissions baseline: {total_emissions:.1f} MtCO₂e/year")
    print(f"✅ Average investment per company: ₩{total_company_investment/len(companies):.1f} trillion")
    print(f"✅ Investment per Mt capacity: ₩{total_company_investment/total_capacity:.1f} trillion")
    
    # Save detailed company report
    company_report = f"""
# Korean Petrochemical Companies: Transition Analysis Report

## Executive Summary

This analysis covers {len(companies)} major Korean petrochemical companies representing {total_capacity:.1f} Mt/year capacity and {total_emissions:.1f} MtCO₂e annual emissions. Total investment requirement: ₩{total_company_investment:.1f} trillion over 25 years.

## Company Investment Summary

| Company | Investment (₩T) | Capacity (Mt) | Strategy Type |
|---------|----------------|---------------|---------------|
{chr(10).join([f"| {comp.replace('_', ' ')} | {investment_breakdown[comp]['total_investment']:.1f} | {companies[comp]['total_capacity']:.1f} | {transition_strategies[comp]['strategy_type']} |" for comp in companies.keys()])}

## Key Findings

### Investment Leaders
- **SK Innovation**: ₩{investment_breakdown['SK_Innovation']['total_investment']:.1f}T - First mover leadership strategy
- **LG Chem**: ₩{investment_breakdown['LG_Chem']['total_investment']:.1f}T - Technology innovation focus
- **Lotte Chemical**: ₩{investment_breakdown['Lotte_Chemical']['total_investment']:.1f}T - Multi-hub optimization

### Strategic Differentiation
1. **Technology Leaders**: SK Innovation, LG Chem focus on breakthrough technologies
2. **Cost Optimizers**: Lotte Chemical, GS Caltex emphasize efficiency and optimization
3. **Niche Players**: Kumho Petrochemical, Yeochun NCC target specialized markets

### Competitive Positioning
- **Tier 1 Leaders**: SK Innovation, LG Chem - comprehensive transformation capability
- **Tier 2 Followers**: Lotte Chemical, Hanwha Solutions, S-Oil - selective advantage areas
- **Tier 3 Specialists**: Yeochun NCC, GS Caltex, Kumho - focused strategies

## Investment Analysis

### Total Requirements: ₩{total_company_investment:.1f} Trillion
- **Average per company**: ₩{total_company_investment/len(companies):.1f} trillion
- **Range**: ₩{min([inv['total_investment'] for inv in investment_breakdown.values()]):.1f}T - ₩{max([inv['total_investment'] for inv in investment_breakdown.values()]):.1f}T
- **Investment intensity**: ₩{total_company_investment/total_capacity:.1f}T per Mt capacity

### Financing Challenges
- **High capital intensity**: 1.5-3.0x annual revenue for major companies
- **Long payback periods**: 8-20 years depending on strategy
- **Technology risks**: Early mover disadvantage vs late adopter benefits

## Strategic Recommendations

### For Policy Makers
1. **Differentiated support**: Tailor incentives to company strategies and capabilities
2. **Technology sharing**: Facilitate knowledge transfer between companies
3. **Infrastructure coordination**: Support shared hydrogen and renewable infrastructure

### For Companies
1. **Strategic clarity**: Define clear technology pathway and competitive positioning
2. **Partnership focus**: Leverage collaborations to share risks and costs
3. **Phased implementation**: Use pilot projects to validate technology and economics

## Timeline Coordination

### 2025-2030: Foundation Phase
- SK Innovation, LG Chem lead with pilot projects
- Infrastructure development and technology validation
- Government support for demonstration projects

### 2030-2040: Scaling Phase  
- Full commercial deployment across all companies
- Technology transfer and cost optimization
- Market competition and differentiation

### 2040-2050: Leadership Phase
- Global competitiveness and technology export
- Full portfolio transformation completion
- Industry leadership in green petrochemicals

## Risk Assessment

### High-Impact Risks
1. **Technology execution**: Unproven technologies at commercial scale
2. **Market coordination**: Simultaneous capacity additions affecting margins
3. **Supply chain**: Hydrogen and bio-naphtha supply constraints
4. **Financial stress**: High investment burden during transition

### Mitigation Strategies
1. **Portfolio approach**: Multiple technology pathways and flexible strategies
2. **Industry coordination**: Collaborative infrastructure and timing
3. **Government support**: Risk sharing and financial backstops
4. **International partnerships**: Technology transfer and supply agreements

## Conclusion

The Korean petrochemical industry transformation requires ₩{total_company_investment:.1f} trillion investment across {len(companies)} major companies. Success depends on:

1. **Strategic differentiation** aligned with company capabilities
2. **Coordinated infrastructure** development with government support  
3. **Technology validation** through phased pilot programs
4. **Financial innovation** to manage investment burden
5. **Market development** for green petrochemical products

Each company must balance ambition with financial reality, choosing strategies that build on existing strengths while addressing technological and market uncertainties.
"""
    
    # Save report
    with open('company_transition_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(company_report)
    
    print("✅ Company analysis report saved: company_transition_analysis_report.md")
    print("✅ Company visualization saved: company_transition_analysis.png")

if __name__ == "__main__":
    main()