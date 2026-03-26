# AI & Data Science Analytics Dashboard — Power BI

**Author:** Naresh Sampangi

Multi-domain analytics dashboard built with Power BI for monitoring ML model performance, Gen AI operations, data quality, and business KPIs across enterprise AI initiatives. Includes Python data pipelines and comprehensive DAX measures.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Power BI AI Analytics Dashboard                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────────────┐  │
│  │  Data Layer  │───▶│Analysis Layer│───▶│  Presentation Layer    │  │
│  └─────────────┘    └──────────────┘    └────────────────────────┘  │
│        │                   │                       │                │
│  ┌─────▼─────┐    ┌───────▼──────┐    ┌───────────▼────────────┐   │
│  │ generate_  │    │  7 Analysis  │    │   Power BI Desktop     │   │
│  │ all_data.py│    │   Modules    │    │                        │   │
│  │            │    │              │    │  ┌──────────────────┐  │   │
│  │ • ML Models│    │ • MLOps      │    │  │ 8 Report Pages   │  │   │
│  │ • Gen AI   │    │ • Gen AI Ops │    │  │                  │  │   │
│  │ • Data Qty │    │ • Data Qty   │    │  │ • Executive Sum  │  │   │
│  │ • Business │    │ • Business   │    │  │ • ML Operations  │  │   │
│  │ • Product  │    │ • Product    │    │  │ • Gen AI Center  │  │   │
│  │ • Risk     │    │ • Risk       │    │  │ • Data Quality   │  │   │
│  │ • IoT/Mfg  │    │ • Mfg        │    │  │ • Business ROI   │  │   │
│  │            │    │              │    │  │ • Product Analyt  │  │   │
│  └────────────┘    └──────────────┘    │  │ • Risk/Compliance │  │   │
│        │                   │           │  │ • Manufacturing   │  │   │
│  ┌─────▼─────┐    ┌───────▼──────┐    │  └──────────────────┘  │   │
│  │  data/     │    │data/analysis/│    │                        │   │
│  │  8 CSVs    │    │  7 summaries │    │  DAX Measures (50+)    │   │
│  │  ~80K rows │    │              │    │  Power Query M Xforms  │   │
│  └────────────┘    └──────────────┘    └────────────────────────┘   │
│        │                                         ▲                  │
│  ┌─────▼──────────┐                              │                  │
│  │export_powerbi_  │─────────────────────────────┘                  │
│  │ready.py         │                                                │
│  │                 │                                                │
│  │ • Star Schema   │                                                │
│  │ • Date Dim      │                                                │
│  │ • Fact Tables   │                                                │
│  │ • Denormalized  │                                                │
│  └─────────────────┘                                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Report Pages

| # | Page | Description |
|---|------|-------------|
| 1 | **AI Executive Summary** | KPI cards (total models, Gen AI cost, avg DQ score, ROI), trend sparklines, traffic light status indicators across all domains |
| 2 | **ML Model Operations** | Model performance heatmap, drift gauge, latency distribution, error rate time series, model comparison radar chart |
| 3 | **Gen AI Command Center** | Token/cost stacked area chart, model usage donut, quality score gauges, guardrail trigger bar chart, application comparison table |
| 4 | **Data Quality Observatory** | DQ score matrix heatmap, freshness timeline, anomaly scatter plot, SLA compliance gauge, schema drift log |
| 5 | **Business Impact Tracker** | ROI waterfall chart, investment bubble chart, department comparison clustered bar, adoption funnel, time-saved calculator |
| 6 | **Product Analytics** | User engagement funnel, feature heatmap, A/B test results with confidence intervals, conversion trend, geographic map |
| 7 | **AI Risk & Compliance** | Risk matrix (probability × impact), fairness metrics line chart, compliance status donut, PII exposure trend, remediation burndown |
| 8 | **Manufacturing Intelligence** | OEE gauge, sensor readings real-time line, alert heatmap, maintenance calendar, energy vs output scatter |

---

## Tech Stack

- **Python 3.9+** — Data generation & analysis (pandas, numpy, scikit-learn, scipy)
- **Power BI Desktop** — Dashboard visualization & interactive reporting
- **DAX** — 50+ measures for calculated KPIs, time intelligence, and statistical analysis
- **Power Query M** — Data transformations, type conversions, and schema management
- **pandas / numpy** — Data pipelines and statistical computations
- **scikit-learn** — ML model metrics and feature importance calculations
- **Faker** — Realistic synthetic data generation

---

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Power BI Desktop (Windows) or Power BI Service
- Git

### Python Setup

```bash
# Clone the repository
cd ~/ds-projects/powerbi-ai-analytics-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Generate all synthetic datasets
make generate-data

# Run all analysis modules
make analyze

# Export Power BI-ready star schema
make export-powerbi

# Or run everything at once
make all
```

### Power BI Setup

1. Open Power BI Desktop
2. **Get Data** → **Text/CSV** → Navigate to `data/powerbi_ready/`
3. Import all CSV files from the `powerbi_ready/` folder
4. Set up relationships as documented in `data_model/README.md`
5. Create measures from `dashboards/dax_measures.md`
6. Apply Power Query transformations from `dashboards/power_query_m.md`
7. Build report pages following `dashboards/README.md`

---

## Project Structure

```
powerbi-ai-analytics-dashboard/
├── README.md
├── requirements.txt
├── Makefile
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── generate_all_data.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── mlops_analysis.py
│   │   ├── genai_ops_analysis.py
│   │   ├── data_quality_analysis.py
│   │   ├── business_impact_analysis.py
│   │   ├── product_analysis.py
│   │   ├── risk_analysis.py
│   │   └── manufacturing_analysis.py
│   └── export_powerbi_ready.py
├── data/                  # Generated (git-ignored)
│   ├── *.csv
│   ├── analysis/
│   └── powerbi_ready/
├── dashboards/
│   ├── README.md
│   ├── dax_measures.md
│   └── power_query_m.md
└── data_model/
    └── README.md
```

---

## License

MIT

**Author:** Naresh Sampangi
