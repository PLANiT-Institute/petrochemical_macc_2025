# Streamlit Dashboard Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install streamlit plotly
```

### 2. Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 📊 Dashboard Features

### 7 Interactive Pages

#### 1. 🏠 Overview
- **Key metrics** at a glance (facilities, emissions, companies)
- **Model status** indicators
- **Scenario comparison table** showing all scenarios side-by-side
- Quick navigation to other sections

#### 2. 📈 Baseline & BAU
- **2025 baseline emissions** breakdown
- **BAU trajectory** visualization (2025-2050)
- **Emissions by fuel type** pie chart and breakdown
- Key assumptions explained

#### 3. 💰 MACC Analysis
- **Interactive MACC curves** for any year (2025, 2030, 2040, 2050)
- **Technology cost details** (CAPEX, OPEX, fuel costs)
- **Cost evolution charts** showing how costs decline over time
- Technology availability indicators

#### 4. 🎯 Scenario Explorer
- **Select any scenario** from dropdown
- **Emission trajectory** comparison (BAU vs target vs actual)
- **Technology deployment** stacked area chart
- **Cumulative emissions** tracking (for carbon budget scenarios)
- Detailed data table export

#### 5. 🏢 Company Analysis
- **Top 10 emitters** bar chart
- **Company ranking table** with emissions and market share
- **Validation status** vs ESG reports
- Interactive filtering

#### 6. 📍 Regional Analysis
- **Emissions by location** bar chart
- **Regional distribution** pie chart
- Location-level data table

#### 7. ℹ️ About the Model
- Complete model documentation
- Technology descriptions
- Validation methodology
- Data sources and assumptions

---

## 🎨 Interactive Features

### Scenario Explorer
**Use cases:**
- Compare different decarbonization pathways
- Understand technology deployment timing
- Evaluate carbon budget compliance
- Export data for presentations

**How to use:**
1. Select scenario from sidebar dropdown
2. View emission trajectory chart
3. Explore technology deployment over time
4. Check detailed data table at bottom

### MACC Analysis
**Use cases:**
- Understand technology costs for specific years
- Compare cost-effectiveness across technologies
- Track cost evolution trends

**How to use:**
1. Select year from sidebar (2025, 2030, 2040, 2050)
2. View MACC curve with technology bars
3. Hover for detailed cost breakdowns
4. Check technology details below chart

### Company & Regional Analysis
**Use cases:**
- Identify major emitters
- Understand industry structure
- Validate model against real data

**How to use:**
1. View top emitters in charts
2. Explore full data tables
3. Check validation notes

---

## 📁 Data Requirements

**The dashboard automatically loads data from:**
```
outputs/
├── module_01/
│   ├── baseline_2025_detailed.csv
│   ├── bau_trajectory_2025_2050.csv
│   ├── emissions_by_company.csv
│   ├── emissions_by_product.csv
│   └── emissions_by_location.csv
├── module_02/
│   └── macc_annual_2025_2050.csv
├── module_03/
│   ├── *_deployment.csv (all scenarios)
│   └── scenario_comparison.csv
└── module_04/
    └── financial_summary.csv
```

**⚠️ Make sure to run the model first:**
```bash
python run_all.py
```

---

## 🎯 Use Cases for Clients

### 1. Policy Makers
**Pages to explore:**
- Overview → Quick status check
- Scenario Explorer → Compare "Korea_NDC" vs "Linear_2050"
- MACC Analysis → Understand technology costs for budget planning

**Key questions answered:**
- Can we meet Korea's 2030 NDC target?
- What's the cost difference between scenarios?
- When should we deploy each technology?

### 2. Industry Executives
**Pages to explore:**
- Company Analysis → See your company's emissions ranking
- MACC Analysis → Technology investment costs
- Scenario Explorer → Early vs late action costs

**Key questions answered:**
- How does our company compare to competitors?
- What technologies should we invest in first?
- What's the financial impact of different timelines?

### 3. Researchers & Analysts
**Pages to explore:**
- All pages for comprehensive analysis
- Scenario Explorer → Export detailed data tables
- About → Methodology and validation details

**Key questions answered:**
- How was the model validated?
- What are the key assumptions?
- Can I export data for my own analysis?

### 4. Financial Institutions
**Pages to explore:**
- Scenario Explorer → Technology deployment patterns
- MACC Analysis → Investment requirements by year
- Company Analysis → Risk assessment by company

**Key questions answered:**
- What's the total investment required?
- When will technologies become cost-effective?
- Which companies are most exposed?

---

## 💡 Tips for Best Experience

### Navigation
- Use the **sidebar** to switch between pages
- **Hover over charts** for detailed tooltips
- **Expand data tables** for full detail

### Scenario Comparison
1. Start with **Overview** page
2. Review **scenario_comparison** table
3. Deep dive into specific scenarios in **Scenario Explorer**
4. Compare visually across years

### Exporting Data
- Click on any data table
- Use built-in CSV export (top-right of table)
- Right-click charts to save as PNG

### Performance
- Dashboard uses **caching** for fast loading
- First load may take 2-3 seconds
- Subsequent page switches are instant
- Refresh page to reload data after running model

---

## 🔧 Customization

### Adding Your Own Scenarios

1. **Edit scenario file:**
   ```bash
   nano data/emission_scenarios_template.csv
   ```

2. **Add your scenario:**
   ```csv
   My_Scenario,annual_path,2025,52.00,Baseline
   My_Scenario,annual_path,2030,40.00,Target
   My_Scenario,annual_path,2050,2.00,Net-zero
   ```

3. **Run optimization:**
   ```bash
   python run_module_03.py
   ```

4. **Refresh dashboard:**
   - Your scenario will appear in dropdown automatically!

### Modifying Charts

The dashboard uses **Plotly** for interactive charts. You can modify:
- Colors
- Chart types
- Layout options
- Hover text

Edit `app.py` and search for the chart you want to modify.

### Adding New Metrics

To add custom metrics:
1. Calculate in your module
2. Save to CSV
3. Load in `load_data()` function
4. Display in relevant page

---

## 🐛 Troubleshooting

### "Module outputs not found"
**Solution:** Run the model first
```bash
python run_all.py
```

### Charts not displaying
**Solution:** Check if plotly is installed
```bash
pip install plotly
```

### Data looks outdated
**Solution:** Refresh the page or clear cache
- Press `C` in the browser (Streamlit shortcut)
- Or add `?cache_bust=123` to URL

### Port already in use
**Solution:** Specify different port
```bash
streamlit run app.py --server.port 8502
```

---

## 📊 Example Workflows

### Workflow 1: Policy Analysis
1. Open dashboard → Go to **Overview**
2. Check scenario comparison table
3. Select **Korea_NDC** in Scenario Explorer
4. Verify 2030 reduction = 20.2% ✓
5. Export deployment data for report

### Workflow 2: Technology Assessment
1. Go to **MACC Analysis**
2. Select year **2030**
3. Compare Heat Pump vs NCC-H2 costs
4. Check **Cost Evolution** chart
5. Note when technologies become available

### Workflow 3: Company Benchmarking
1. Go to **Company Analysis**
2. Find your company in table
3. Compare emissions vs top competitors
4. Check validation notes
5. Export table for internal report

### Workflow 4: Scenario Development
1. Edit `emission_scenarios_template.csv`
2. Add your custom scenario
3. Run `python run_module_03.py`
4. Open dashboard
5. Select your scenario from dropdown
6. Analyze results visually

---

## 🚀 Deployment Options

### Local (Default)
```bash
streamlit run app.py
```
Access at: `http://localhost:8501`

### Network Access (Share with team)
```bash
streamlit run app.py --server.address 0.0.0.0
```
Access at: `http://YOUR_IP:8501`

### Cloud Deployment
**Streamlit Cloud (Free):**
1. Push to GitHub
2. Connect at streamlit.io/cloud
3. Deploy with one click
4. Get shareable URL

**Other options:**
- Heroku
- AWS EC2
- Google Cloud Run
- Azure App Service

---

## 📞 Support

**For technical issues:**
- Check this guide first
- Review error messages in terminal
- Ensure all data files exist in `outputs/`

**For model questions:**
- See [EMISSION_SCENARIOS_GUIDE.md](EMISSION_SCENARIOS_GUIDE.md)
- See [FINAL_MODEL_SUMMARY.md](FINAL_MODEL_SUMMARY.md)
- See [README.md](README.md)

---

## 🎉 Next Steps

1. **Run the model** to generate data
2. **Launch the dashboard** with `streamlit run app.py`
3. **Explore** the 7 interactive pages
4. **Customize** scenarios to your needs
5. **Share** with your clients/stakeholders

**The dashboard makes your complex model accessible to non-technical audiences!**
