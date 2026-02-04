
import pandas as pd
import os
from datetime import datetime
import base64

# Configuration
# Configuration
OUTPUTS_DIR = "outputs"
REPORT_DIR = "reports/pretty_report"
IMAGES_DIR = os.path.join(REPORT_DIR, "images")
FIGURES_DIR = os.path.join(OUTPUTS_DIR, "figures")
CSV_DIR = os.path.join(OUTPUTS_DIR, "csv_exports")
HTML_OUTPUT = os.path.join(REPORT_DIR, "report.html")

def get_image_base64(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

# Helper to read CSV and convert to HTML table
def csv_to_html(filename):
    path = os.path.join(CSV_DIR, filename)
    if os.path.exists(path):
        df = pd.read_csv(path)
        # Clean up for display: limit rows if too long, format numbers
        return df.head(10).to_html(classes="table", index=False, float_format="%.2f")
    return "<p>Data not found.</p>"

def generate_report():
    print("Generating report...")
    
    # Load assets
    cover_img = get_image_base64(os.path.join(IMAGES_DIR, "cover_image.png"))
    emissions_header = get_image_base64(os.path.join(IMAGES_DIR, "section_header_emissions.png"))
    economics_header = get_image_base64(os.path.join(IMAGES_DIR, "section_header_economics.png"))
    
    report_stranded_assets = get_image_base64(os.path.join(FIGURES_DIR, "report_stranded_assets_v2.png"))
    report_macc = get_image_base64(os.path.join(FIGURES_DIR, "report_macc_curves_v2.png"))
    report_top5 = get_image_base64(os.path.join(FIGURES_DIR, "report_top5_companies.png"))

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Petrochemical Decarbonization Report 2025</title>
        <style>
            :root {{
                --primary: #2C3E50;
                --secondary: #E74C3C;
                --light-gray: #ECF0F1;
                --dark: #2c3e50;
            }}
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #333;
                background: #f9f9f9;
                margin: 0;
                padding: 0;
                line-height: 1.6;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            /* Cover */
            .cover {{
                height: 60vh;
                background-image: url('data:image/png;base64,{cover_img}');
                background-size: cover;
                background-position: center;
                display: flex;
                align-items: flex-end;
                color: white;
                padding: 40px;
                position: relative;
            }}
            .cover::after {{
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.8));
            }}
            .cover-content {{
                position: relative;
                z-index: 1;
            }}
            .cover h1 {{
                font-size: 3.5rem;
                margin: 0;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            .cover p {{
                font-size: 1.2rem;
                margin-top: 10px;
                opacity: 0.9;
            }}
            
            /* Sections */
            .section {{
                padding: 40px;
                margin: 20px 0;
            }}
            .section-header {{
                height: 200px;
                overflow: hidden;
                border-radius: 8px;
                margin-bottom: 30px;
                position: relative;
            }}
            .section-header img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            h2 {{
                color: var(--primary);
                font-size: 2rem;
                border-bottom: 2px solid var(--secondary);
                padding-bottom: 10px;
                margin-top: 0;
            }}
            
            /* Figures */
            .figure-container {{
                margin: 40px 0;
                text-align: center;
            }}
            .figure-container img {{
                max-width: 100%;
                border-radius: 4px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .figure-caption {{
                font-style: italic;
                color: #666;
                margin-top: 10px;
            }}
            
            /* Tables */
            .table-container {{
                overflow-x: auto;
                margin: 20px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                font-size: 0.9rem;
            }}
            th {{
                background: var(--primary);
                color: white;
                text-align: left;
                padding: 12px;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }}
            tr:nth-child(even) {{
                background-color: #f8f8f8;
            }}
            
            footer {{
                background: var(--dark);
                color: white;
                padding: 40px;
                text-align: center;
                margin-top: 60px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Cover -->
            <div class="cover">
                <div class="cover-content">
                    <h1>Petrochemical<br>Decarbonization</h1>
                    <p>Korea Industry Analysis & MACC 2025</p>
                    <p style="font-size: 1rem; margin-top: 20px;">Generated on {datetime.now().strftime('%Y-%m-%d')}</p>
                </div>
            </div>

            <!-- Intro -->
            <div class="section">
                <p class="lead">This report analyzes the decarbonization pathways for the Korean petrochemical industry, focusing on Marginal Abatement Cost Curves (MACC) and stranded asset risks under 1.5°C and 2.0°C scenarios.</p>
            </div>

            <!-- Emissions Section -->
            <div class="section">
                <div class="section-header">
                    <img src="data:image/png;base64,{emissions_header}" alt="Emissions Header">
                </div>
                <h2>Emission Pathways & Top Players</h2>
                <p>Analysis of current baseline emissions reveals the significant role of major industry players. The transition to net-zero requires aggressive technology alignment.</p>
                
                <div class="figure-container">
                    <img src="data:image/png;base64,{report_top5}" alt="Top 5 Companies Analysis">
                    <div class="figure-caption">Figure 1: Comprehensive analysis of the top 5 contributing companies.</div>
                </div>

                <h3>Regional Emission Summary (Sample)</h3>
                <div class="table-container">
                    {csv_to_html('regional_mac_summary.csv')}
                </div>
            </div>

            <!-- Economics Section -->
            <div class="section">
                <div class="section-header">
                    <img src="data:image/png;base64,{economics_header}" alt="Economics Header">
                </div>
                <h2>Economic Analysis: MACC & Stranded Assets</h2>
                <p>Economic feasibility is driven by the marginal abatement cost. Our analysis highlights the most cost-effective technologies and the financial risks posed by stranded assets.</p>

                <div class="figure-container">
                    <img src="data:image/png;base64,{report_macc}" alt="MACC Curves">
                    <div class="figure-caption">Figure 2: Marginal Abatement Cost Curves for 2050.</div>
                </div>
                
                <div class="figure-container">
                    <img src="data:image/png;base64,{report_stranded_assets}" alt="Stranded Assets">
                    <div class="figure-caption">Figure 3: Stranded asset risk analysis across scenarios.</div>
                </div>

                <h3>Stranded Assets Overview</h3>
                <div class="table-container">
                    {csv_to_html('stranded_assets_overview.csv')}
                </div>
            </div>
            
            <footer>
                <p>© 2025 PlanIT Institute. All Rights Reserved.</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open(HTML_OUTPUT, "w") as f:
        f.write(html_content)
    
    print(f"Report generated successfully: {HTML_OUTPUT}")

if __name__ == "__main__":
    generate_report()
