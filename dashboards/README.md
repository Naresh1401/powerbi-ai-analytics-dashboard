# Power BI Dashboard Design — 8 Report Pages

Comprehensive design documentation for each Power BI report page, including visuals, measures, slicers, drill-through paths, and conditional formatting rules.

---

## Page 1: AI Executive Summary

### Purpose
High-level KPI overview for C-suite / AI leadership showing health of all AI initiatives at a glance.

### Visuals

| # | Visual Type | Title | Data Source | Measures |
|---|-------------|-------|-------------|----------|
| 1 | **KPI Card** | Total ML Models | dim_model | `Total Models`, `Models in Production` |
| 2 | **KPI Card** | Gen AI Cost (MTD) | fact_genai_operations | `Gen AI Cost MTD`, `Gen AI Cost MoM %` |
| 3 | **KPI Card** | Avg Data Quality Score | fact_data_quality | `DQ Score Trend`, `DQ Score vs Target` |
| 4 | **KPI Card** | Overall ROI | fact_business_impact | `ROI %`, `Total AI Investment` |
| 5 | **KPI Card** | Total Alerts (Mfg) | fact_manufacturing | `Total Alerts`, `Alert Rate %` |
| 6 | **KPI Card** | Open Risk Findings | fact_risk_compliance | `Open Findings`, `Critical Risks` |
| 7 | **Sparkline Area** | Model Accuracy Trend (30d) | fact_model_metrics | `Avg Model Accuracy` by date |
| 8 | **Sparkline Area** | Gen AI Requests Trend | fact_genai_operations | `Total Requests` by date |
| 9 | **Sparkline Area** | DQ Score Trend | fact_data_quality | `DQ Score Trend` by date |
| 10 | **Traffic Light Table** | Domain Health Matrix | Multiple | Status indicators per domain |

### Slicers
- **Date Range**: Connected to `dim_date[date]`
- **Department**: Connected to `dim_department[department_name]`

### Conditional Formatting
- KPI cards: Green (≥ target), Yellow (80-100% of target), Red (< 80% target)
- Traffic lights: ●Green = Healthy, ●Yellow = Warning, ●Red = Critical
- Sparklines: Trend color based on slope (green positive, red negative)

### Drill-Through
- Click any KPI card → navigates to respective detailed page (Pages 2-8)

---

## Page 2: ML Model Operations

### Purpose
Monitor ML model performance, detect drift, track SLA compliance across the model fleet.

### Visuals

| # | Visual Type | Title | Data Source | Measures |
|---|-------------|-------|-------------|----------|
| 1 | **Matrix Heatmap** | Model Performance Grid | fact_model_metrics | Rows: `model_key`, Cols: accuracy/f1/AUC, Values: `Avg Accuracy`, `Avg F1 Score` |
| 2 | **Gauge** | Data Drift Score | fact_model_metrics | `Avg Data Drift Score`, target: 0.1, max: 0.5 |
| 3 | **Gauge** | Prediction Drift | fact_model_metrics | `Avg Prediction Drift`, target: 0.1 |
| 4 | **Histogram** | Latency Distribution (P99) | fact_model_metrics | `latency_p99_ms` binned |
| 5 | **Line Chart** | Error Rate Time Series | fact_model_metrics | X: date, Y: `Avg Error Rate`, Color: model_key |
| 6 | **Radar Chart** | Model Comparison | fact_model_metrics | Axes: accuracy, precision, recall, f1, latency (inverted) |
| 7 | **Line Chart** | Feature Importance Stability | fact_model_metrics | X: date, Y: `Avg FI Stability` |
| 8 | **Table** | SLA Compliance Summary | fact_model_metrics | model, latency SLA %, error SLA % |

### Slicers
- **Model Name**: `dim_model[model_name]`
- **Model Type**: `dim_model[model_type]` (classification, regression, etc.)
- **Framework**: `dim_model[framework]`
- **Status**: `dim_model[status]`
- **Date Range**: `dim_date[date]`

### Conditional Formatting
- Heatmap cells: Color scale Green (>0.9) → Yellow (0.8-0.9) → Red (<0.8)
- Drift gauge: Green zone (0-0.05), Yellow (0.05-0.1), Red (>0.1)
- SLA %: Green ≥95%, Yellow 90-95%, Red <90%

### Drill-Through
- Click model → Model Detail page with all metrics for one model over time

---

## Page 3: Gen AI Command Center

### Purpose
Monitor Gen AI usage, costs, quality, and guardrail effectiveness across all applications.

### Visuals

| # | Visual Type | Title | Data Source | Measures |
|---|-------------|-------|-------------|----------|
| 1 | **Stacked Area Chart** | Token Usage & Cost Trend | fact_genai_operations | X: date, Y: `Total Cost`, Stack by: model |
| 2 | **Donut Chart** | Model Usage Distribution | fact_genai_operations | Values: `Total Requests` by model |
| 3 | **Gauge** | Relevance Score | fact_genai_operations | `Avg Relevance Score`, target: 0.8 |
| 4 | **Gauge** | Groundedness Score | fact_genai_operations | `Avg Groundedness Score`, target: 0.75 |
| 5 | **Bar Chart** | Guardrail Triggers by App | fact_genai_operations | X: application, Y: `Guardrail Trigger Rate` |
| 6 | **Table** | Application Comparison | fact_genai_operations | App, requests, cost, avg latency, success rate, avg rating |
| 7 | **Line Chart** | Error/Timeout Rate Trend | fact_genai_operations | X: date, Y: `Error Rate %`, `Timeout Rate %` |
| 8 | **KPI Card** | Cost per 1K Tokens | fact_genai_operations | `Cost per 1K Tokens` |

### Slicers
- **Application**: `fact_genai_operations[app_key]`
- **Model**: `fact_genai_operations[model]`
- **Status**: `fact_genai_operations[status]`
- **Date Range**: `dim_date[date]`

### Conditional Formatting
- Cost trend: Conditional color if month-over-month increase > 20%
- Quality gauges: Green ≥0.8, Yellow 0.6-0.8, Red <0.6
- Guardrail rate: Red if > 10%, Yellow 5-10%, Green < 5%

### Drill-Through
- Click application → Application drill-through with token breakdown, quality metrics, error logs

---

## Page 4: Data Quality Observatory

### Purpose
Monitor data quality across all datasets, track freshness SLAs, detect anomalies and schema drift.

### Visuals

| # | Visual Type | Title | Data Source | Measures |
|---|-------------|-------|-------------|----------|
| 1 | **Matrix Heatmap** | DQ Score by Dataset × Week | fact_data_quality | Rows: dataset_name, Cols: week, Values: `Avg DQ Score` |
| 2 | **Line Chart** | Freshness Timeline | fact_data_quality | X: date, Y: `Avg Freshness Hours`, Threshold line at 24h |
| 3 | **Scatter Plot** | Anomaly Detection | fact_data_quality | X: null_pct, Y: duplicate_pct, Size: row_count, Color: anomaly_detected |
| 4 | **Gauge** | SLA Compliance | fact_data_quality | `SLA Compliance %`, target: 95% |
| 5 | **Table** | Schema Drift Log | fact_data_quality | date, dataset, table, drift details (filtered: schema_drift=True) |
| 6 | **Stacked Bar** | DQ Component Breakdown | fact_data_quality | completeness/consistency/validity scores stacked |
| 7 | **KPI Card** | Datasets Monitored | fact_data_quality | `Distinct Dataset Count` |

### Slicers
- **Dataset Name**: `fact_data_quality[dataset_name]`
- **SLA Met**: `fact_data_quality[sla_met]`
- **Anomaly Detected**: `fact_data_quality[anomaly_detected]`
- **Date Range**: `dim_date[date]`

### Conditional Formatting
- DQ score heatmap: Green ≥0.9, Yellow 0.7-0.9, Red <0.7
- Freshness: Red if > 24 hours, Yellow 12-24h, Green < 12h
- SLA gauge: Green ≥95%, Yellow 85-95%, Red <85%

### Drill-Through
- Click dataset → Dataset detail with row counts, null/dup trends, quality component timelines

---

## Page 5: Business Impact Tracker

### Purpose
Track ROI of AI initiatives, compare departments, measure adoption and business value.

### Visuals

| # | Visual Type | Title | Data Source | Measures |
|---|-------------|-------|-------------|----------|
| 1 | **Waterfall Chart** | ROI Waterfall by Department | fact_business_impact | Investment (negative) → Savings → Revenue Uplift → Net |
| 2 | **Bubble Chart** | Investment vs Returns | fact_business_impact | X: investment, Y: total_return, Size: adoption_rate, Color: department |
| 3 | **Clustered Bar** | Department Comparison | fact_business_impact | Departments × investment/savings/revenue_uplift |
| 4 | **Funnel Chart** | Adoption Funnel | fact_business_impact | Stages: pilot → scaling → production |
| 5 | **KPI Card** | Total AI Investment | fact_business_impact | `Total AI Investment` |
| 6 | **KPI Card** | Total Cost Savings | fact_business_impact | `Total Cost Savings` |
| 7 | **KPI Card** | Overall ROI % | fact_business_impact | `ROI %` |
| 8 | **Table** | Top Initiatives by ROI | fact_business_impact | initiative, use_case, investment, roi_pct, status |

### Slicers
- **Department**: `dim_department[department_name]`
- **Quarter**: `fact_business_impact[quarter]`
- **Status**: `fact_business_impact[status]`
- **AI Use Case**: `fact_business_impact[ai_use_case]`

### Conditional Formatting
- ROI %: Green >50%, Yellow 0-50%, Red <0% (negative ROI)
- Bubble colors by department with consistent palette
- Status column: Icon set (✓ production, ↑ scaling, ○ pilot, ✗ retired)

### Drill-Through
- Click department → Department deep dive with all initiatives, timelines, ROI breakdown

---

## Page 6: Product Analytics

### Purpose
Analyze user behavior, feature engagement, A/B test outcomes, and conversion performance.

### Visuals

| # | Visual Type | Title | Data Source | Measures |
|---|-------------|-------|-------------|----------|
| 1 | **Funnel Chart** | User Engagement Funnel | fact_product_analytics | Total Users → Page Viewers → Clickers → Converters |
| 2 | **Matrix Heatmap** | Feature Usage Heatmap | fact_product_analytics | Rows: feature, Cols: day_of_week, Values: event count |
| 3 | **Clustered Bar + Error Bars** | A/B Test Results | analysis data | Control vs Variant conversion rates with 95% CI |
| 4 | **Line Chart** | Conversion Rate Trend | fact_product_analytics | X: date, Y: `Conversion Rate %`, by device |
| 5 | **Filled Map** | Geographic Distribution | fact_product_analytics | Country → user count / revenue |
| 6 | **Donut Chart** | Device Distribution | fact_product_analytics | mobile / desktop / tablet split |
| 7 | **KPI Card** | Total Revenue | fact_product_analytics | `Total Revenue` |
| 8 | **KPI Card** | Conversion Rate | fact_product_analytics | `Overall Conversion Rate` |

### Slicers
- **Feature Name**: `fact_product_analytics[feature_name]`
- **Device**: `fact_product_analytics[device]`
- **Country**: `fact_product_analytics[country]`
- **A/B Variant**: `fact_product_analytics[ab_test_variant]`
- **Date Range**: `dim_date[date]`

### Conditional Formatting
- A/B test results: Green if significant & positive lift, Red if significant & negative
- Conversion rate: Color scale based on performance
- Feature heatmap: Intensity gradient for usage

### Drill-Through
- Click feature → Feature detail with engagement timeline, device breakdown, revenue attribution

---

## Page 7: AI Risk & Compliance

### Purpose
Monitor AI risk posture, fairness metrics, compliance status, and remediation progress.

### Visuals

| # | Visual Type | Title | Data Source | Measures |
|---|-------------|-------|-------------|----------|
| 1 | **Scatter/Matrix** | Risk Matrix (Severity × Count) | fact_risk_compliance | X: risk_category, Y: risk_level, Size: count |
| 2 | **Line Chart** | Fairness Metrics Trend | fact_risk_compliance | X: month, Y: demographic_parity, equalized_odds, disparate_impact |
| 3 | **Donut Chart** | Compliance Framework Status | fact_risk_compliance | By framework: resolved/open/in_review |
| 4 | **Area Chart** | PII Exposure Trend | fact_risk_compliance | X: month, Y: total PII exposures |
| 5 | **Stacked Bar** | Remediation Burndown | fact_risk_compliance | By risk_level: open vs resolved over time |
| 6 | **Table** | Critical/High Findings | fact_risk_compliance | Filtered table of critical & high risk findings |
| 7 | **KPI Card** | Open Findings | fact_risk_compliance | `Open Findings` count |
| 8 | **KPI Card** | Avg Demographic Parity | fact_risk_compliance | `Avg Demographic Parity Ratio` |

### Slicers
- **Risk Category**: `fact_risk_compliance[risk_category]`
- **Risk Level**: `fact_risk_compliance[risk_level]`
- **Compliance Framework**: `fact_risk_compliance[compliance_framework]`
- **Audit Status**: `fact_risk_compliance[audit_status]`
- **Model**: `dim_model[model_name]`
- **Date Range**: `dim_date[date]`

### Conditional Formatting
- Risk matrix: Red (critical), Orange (high), Yellow (medium), Green (low)
- Fairness metrics: Red line at 0.8 threshold (below = non-compliant)
- Overdue remediations: Red background for past-deadline items

### Drill-Through
- Click risk category → Category detail with all findings, models affected, remediation timelines

---

## Page 8: Manufacturing Intelligence

### Purpose
Monitor factory OEE, sensor health, maintenance effectiveness, and production quality.

### Visuals

| # | Visual Type | Title | Data Source | Measures |
|---|-------------|-------|-------------|----------|
| 1 | **Gauge** | Overall OEE | fact_manufacturing | `OEE`, target: 0.85, max: 1.0 |
| 2 | **Line Chart** | Sensor Readings Timeline | fact_manufacturing | X: timestamp, Y: reading_value, Filter by sensor_type |
| 3 | **Matrix Heatmap** | Alert Heatmap (Machine × Hour) | fact_manufacturing | Rows: machine_key, Cols: hour, Values: alert count |
| 4 | **Stacked Bar** | Maintenance Calendar | fact_manufacturing | X: date, Y: count, Stack: preventive/corrective |
| 5 | **Scatter Plot** | Energy vs Output | fact_manufacturing | X: energy_consumption_kwh, Y: production_output_units, Color: machine |
| 6 | **Line Chart** | Daily OEE Trend | fact_manufacturing | X: date, Y: `Avg OEE` |
| 7 | **KPI Card** | Total Downtime (hrs) | fact_manufacturing | `Total Downtime Hours` |
| 8 | **KPI Card** | Alert Count | fact_manufacturing | `Total Alerts` |
| 9 | **Table** | Machine Performance Ranking | fact_manufacturing | machine, OEE, downtime, output, quality |

### Slicers
- **Machine**: `dim_machine[machine_name]`
- **Machine Line**: `dim_machine[machine_line]`
- **Sensor Type**: `fact_manufacturing[sensor_type]`
- **Maintenance Type**: `fact_manufacturing[maintenance_type]`
- **Date Range**: `dim_date[date]`

### Conditional Formatting
- OEE gauge: Green ≥85%, Yellow 70-85%, Red <70%
- Alert heatmap: Intensity gradient (white → red)
- Machine ranking: Data bars for OEE, conditional icons for quality

### Drill-Through
- Click machine → Machine detail with all sensors, maintenance history, OEE breakdown, energy trend

---

## Cross-Page Features

### Global Slicers (Sync Group)
- Date Range slicer synced across all pages
- Department slicer synced between Executive Summary and Business Impact

### Bookmarks
- **Dark Mode** / **Light Mode** toggle
- **Executive View** (simplified KPI cards only)
- **Detailed View** (all visuals and tables)

### Navigation
- Left sidebar with page icons
- Back button on drill-through pages
- Tooltip pages for quick hover previews on KPI cards

### Mobile Layout
- Optimized layouts for Pages 1-3 with stacked KPI cards and simplified charts
