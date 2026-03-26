# DAX Measures — AI & Data Science Analytics Dashboard

All DAX measures organized by report page. Import these into your Power BI data model.

---

## Global / Shared Measures

```dax
// ─── Date Intelligence ───
Current Date = TODAY()

Date Range Label =
    FORMAT(MIN(dim_date[date]), "MMM DD, YYYY") & " – " &
    FORMAT(MAX(dim_date[date]), "MMM DD, YYYY")

Is Current Month =
    IF(
        MONTH(MAX(dim_date[date])) = MONTH(TODAY()) &&
        YEAR(MAX(dim_date[date])) = YEAR(TODAY()),
        TRUE, FALSE
    )

Previous Period Start =
    DATEADD(MIN(dim_date[date]), -1, MONTH)

Previous Period End =
    DATEADD(MAX(dim_date[date]), -1, MONTH)
```

---

## Page 1: AI Executive Summary

```dax
// ─── Model KPIs ───
Total Models =
    COUNTROWS(dim_model)

Models in Production =
    CALCULATE(
        COUNTROWS(dim_model),
        dim_model[status] = "production"
    )

Models in Staging =
    CALCULATE(
        COUNTROWS(dim_model),
        dim_model[status] = "staging"
    )

// ─── Gen AI KPIs ───
Gen AI Cost MTD =
    CALCULATE(
        SUM(fact_genai_operations[cost_usd]),
        DATESMTD(dim_date[date])
    )

Gen AI Cost MoM % =
    VAR CurrentMonth =
        CALCULATE(
            SUM(fact_genai_operations[cost_usd]),
            DATESMTD(dim_date[date])
        )
    VAR PreviousMonth =
        CALCULATE(
            SUM(fact_genai_operations[cost_usd]),
            DATEADD(DATESMTD(dim_date[date]), -1, MONTH)
        )
    RETURN
        DIVIDE(CurrentMonth - PreviousMonth, PreviousMonth)

Total Gen AI Requests =
    COUNTROWS(fact_genai_operations)

// ─── Data Quality KPIs ───
DQ Score Trend =
    AVERAGE(fact_data_quality[overall_dq_score])

DQ Score vs Target =
    [DQ Score Trend] - 0.85

// ─── Business Impact KPIs ───
Total AI Investment =
    SUM(fact_business_impact[investment_usd])

Total Cost Savings =
    SUM(fact_business_impact[cost_savings_usd])

Total Revenue Uplift =
    SUM(fact_business_impact[revenue_uplift_usd])

ROI % =
    DIVIDE(
        SUM(fact_business_impact[cost_savings_usd]) +
        SUM(fact_business_impact[revenue_uplift_usd]) -
        SUM(fact_business_impact[investment_usd]),
        SUM(fact_business_impact[investment_usd])
    )

// ─── Domain Health Status ───
Model Health Status =
    VAR AvgAccuracy = AVERAGE(fact_model_metrics[accuracy])
    VAR AvgDrift = AVERAGE(fact_model_metrics[data_drift_score])
    RETURN
        SWITCH(
            TRUE(),
            AvgAccuracy >= 0.9 && AvgDrift < 0.05, "Healthy",
            AvgAccuracy >= 0.8 && AvgDrift < 0.1, "Warning",
            "Critical"
        )

GenAI Health Status =
    VAR SuccessRate =
        DIVIDE(
            CALCULATE(COUNTROWS(fact_genai_operations), fact_genai_operations[status] = "success"),
            COUNTROWS(fact_genai_operations)
        )
    RETURN
        SWITCH(TRUE(), SuccessRate >= 0.95, "Healthy", SuccessRate >= 0.90, "Warning", "Critical")

DQ Health Status =
    VAR AvgScore = [DQ Score Trend]
    RETURN
        SWITCH(TRUE(), AvgScore >= 0.9, "Healthy", AvgScore >= 0.75, "Warning", "Critical")
```

---

## Page 2: ML Model Operations

```dax
// ─── Performance Metrics ───
Avg Model Accuracy =
    AVERAGE(fact_model_metrics[accuracy])

Avg Precision =
    AVERAGE(fact_model_metrics[precision])

Avg Recall =
    AVERAGE(fact_model_metrics[recall])

Avg F1 Score =
    AVERAGE(fact_model_metrics[f1_score])

Avg AUC ROC =
    AVERAGE(fact_model_metrics[auc_roc])

Avg MSE =
    AVERAGE(fact_model_metrics[mse])

Model Health Score =
    AVERAGE(fact_model_metrics[accuracy]) *
    (1 - AVERAGE(fact_model_metrics[data_drift_score]))

// ─── Drift Metrics ───
Avg Data Drift Score =
    AVERAGE(fact_model_metrics[data_drift_score])

Avg Prediction Drift =
    AVERAGE(fact_model_metrics[prediction_drift_score])

Drift Alert Count =
    CALCULATE(
        COUNTROWS(fact_model_metrics),
        fact_model_metrics[data_drift_score] > 0.1
    )

Drift Alert Rate =
    DIVIDE([Drift Alert Count], COUNTROWS(fact_model_metrics))

// ─── Latency & SLA ───
Latency P50 =
    MEDIAN(fact_model_metrics[latency_p50_ms])

Latency P99 =
    PERCENTILEX.INC(fact_model_metrics, fact_model_metrics[latency_p99_ms], 0.99)

Latency SLA % =
    DIVIDE(
        CALCULATE(COUNTROWS(fact_model_metrics), fact_model_metrics[latency_p99_ms] < 500),
        COUNTROWS(fact_model_metrics)
    ) * 100

Avg Error Rate =
    AVERAGE(fact_model_metrics[error_rate])

Error SLA % =
    DIVIDE(
        CALCULATE(COUNTROWS(fact_model_metrics), fact_model_metrics[error_rate] < 0.02),
        COUNTROWS(fact_model_metrics)
    ) * 100

Total Requests =
    SUM(fact_model_metrics[requests_per_minute])

// ─── Feature Importance ───
Avg FI Stability =
    AVERAGE(fact_model_metrics[feature_importance_stability])

FI Stability Trend =
    VAR CurrentPeriod = [Avg FI Stability]
    VAR PreviousPeriod =
        CALCULATE(
            AVERAGE(fact_model_metrics[feature_importance_stability]),
            DATEADD(dim_date[date], -7, DAY)
        )
    RETURN CurrentPeriod - PreviousPeriod
```

---

## Page 3: Gen AI Command Center

```dax
// ─── Token & Cost Metrics ───
Total Tokens Used =
    SUM(fact_genai_operations[total_tokens])

Total Prompt Tokens =
    SUM(fact_genai_operations[prompt_tokens])

Total Completion Tokens =
    SUM(fact_genai_operations[completion_tokens])

Total Gen AI Cost =
    SUM(fact_genai_operations[cost_usd])

Cost per 1K Tokens =
    DIVIDE([Total Gen AI Cost], [Total Tokens Used] / 1000)

Avg Cost per Request =
    AVERAGE(fact_genai_operations[cost_usd])

// ─── Quality Metrics ───
Avg Relevance Score =
    AVERAGE(fact_genai_operations[relevance_score])

Avg Groundedness Score =
    AVERAGE(fact_genai_operations[groundedness_score])

Avg Toxicity Score =
    AVERAGE(fact_genai_operations[toxicity_score])

Avg User Rating =
    AVERAGE(fact_genai_operations[user_rating])

// ─── Guardrail Metrics ───
Guardrail Trigger Count =
    CALCULATE(
        COUNTROWS(fact_genai_operations),
        fact_genai_operations[guardrail_triggered] = TRUE
    )

Guardrail Trigger Rate =
    DIVIDE([Guardrail Trigger Count], COUNTROWS(fact_genai_operations)) * 100

// ─── Status Metrics ───
Gen AI Success Rate =
    DIVIDE(
        CALCULATE(COUNTROWS(fact_genai_operations), fact_genai_operations[status] = "success"),
        COUNTROWS(fact_genai_operations)
    ) * 100

Error Rate % =
    DIVIDE(
        CALCULATE(COUNTROWS(fact_genai_operations), fact_genai_operations[status] = "error"),
        COUNTROWS(fact_genai_operations)
    ) * 100

Timeout Rate % =
    DIVIDE(
        CALCULATE(COUNTROWS(fact_genai_operations), fact_genai_operations[status] = "timeout"),
        COUNTROWS(fact_genai_operations)
    ) * 100

Avg Gen AI Latency =
    AVERAGE(fact_genai_operations[latency_ms])

Median Gen AI Latency =
    MEDIAN(fact_genai_operations[latency_ms])
```

---

## Page 4: Data Quality Observatory

```dax
// ─── DQ Scores ───
Avg Completeness =
    AVERAGE(fact_data_quality[completeness_score])

Avg Consistency =
    AVERAGE(fact_data_quality[consistency_score])

Avg Validity =
    AVERAGE(fact_data_quality[validity_score])

Avg Overall DQ =
    AVERAGE(fact_data_quality[overall_dq_score])

// ─── SLA & Freshness ───
SLA Compliance % =
    DIVIDE(
        CALCULATE(COUNTROWS(fact_data_quality), fact_data_quality[sla_met] = TRUE),
        COUNTROWS(fact_data_quality)
    ) * 100

Avg Freshness Hours =
    AVERAGE(fact_data_quality[freshness_hours])

Stale Dataset Count =
    CALCULATE(
        DISTINCTCOUNT(fact_data_quality[dataset_name]),
        fact_data_quality[freshness_hours] > 24
    )

// ─── Anomalies & Drift ───
Anomaly Count =
    CALCULATE(
        COUNTROWS(fact_data_quality),
        fact_data_quality[anomaly_detected] = TRUE
    )

Anomaly Rate % =
    DIVIDE([Anomaly Count], COUNTROWS(fact_data_quality)) * 100

Schema Drift Events =
    CALCULATE(
        COUNTROWS(fact_data_quality),
        fact_data_quality[schema_drift_detected] = TRUE
    )

Distinct Dataset Count =
    DISTINCTCOUNT(fact_data_quality[dataset_name])

Avg Null Pct =
    AVERAGE(fact_data_quality[null_pct])

Avg Duplicate Pct =
    AVERAGE(fact_data_quality[duplicate_pct])
```

---

## Page 5: Business Impact Tracker

```dax
// ─── Values (reusing some from Page 1) ───
Net AI Return =
    [Total Cost Savings] + [Total Revenue Uplift] - [Total AI Investment]

Avg ROI by Initiative =
    AVERAGE(fact_business_impact[roi_pct])

Avg Adoption Rate =
    AVERAGE(fact_business_impact[adoption_rate_pct])

Total Time Saved Hours =
    SUM(fact_business_impact[time_saved_hours])

Time Saved FTE Equivalent =
    DIVIDE([Total Time Saved Hours], 2080)

Avg Accuracy Improvement =
    AVERAGE(fact_business_impact[accuracy_improvement_pct])

Avg CSAT Delta =
    AVERAGE(fact_business_impact[customer_satisfaction_delta])

Profitable Initiatives % =
    DIVIDE(
        CALCULATE(
            COUNTROWS(fact_business_impact),
            fact_business_impact[roi_pct] > 0
        ),
        COUNTROWS(fact_business_impact)
    ) * 100

Initiative Count =
    COUNTROWS(fact_business_impact)

Production Initiatives =
    CALCULATE(
        COUNTROWS(fact_business_impact),
        fact_business_impact[status] = "production"
    )

Pilot Initiatives =
    CALCULATE(
        COUNTROWS(fact_business_impact),
        fact_business_impact[status] = "pilot"
    )
```

---

## Page 6: Product Analytics

```dax
// ─── User & Session Metrics ───
Total Users =
    DISTINCTCOUNT(fact_product_analytics[user_id])

Total Sessions =
    DISTINCTCOUNT(fact_product_analytics[session_id])

Total Events =
    COUNTROWS(fact_product_analytics)

Avg Session Duration =
    AVERAGE(fact_product_analytics[session_duration_sec])

Avg Pages per Session =
    AVERAGE(fact_product_analytics[pages_viewed])

// ─── Conversion Metrics ───
Total Conversions =
    SUM(fact_product_analytics[conversion_flag])

Overall Conversion Rate =
    DIVIDE(
        SUM(fact_product_analytics[conversion_flag]),
        COUNTROWS(fact_product_analytics)
    ) * 100

Total Revenue =
    SUM(fact_product_analytics[revenue_usd])

Avg Revenue per Conversion =
    DIVIDE(
        [Total Revenue],
        [Total Conversions]
    )

Revenue per User =
    DIVIDE([Total Revenue], [Total Users])

// ─── A/B Test Measures ───
Control Conversion Rate =
    CALCULATE(
        [Overall Conversion Rate],
        fact_product_analytics[ab_test_variant] = "control"
    )

Variant A Conversion Rate =
    CALCULATE(
        [Overall Conversion Rate],
        fact_product_analytics[ab_test_variant] = "A"
    )

Variant B Conversion Rate =
    CALCULATE(
        [Overall Conversion Rate],
        fact_product_analytics[ab_test_variant] = "B"
    )

AB Test Lift % =
    VAR ControlRate = [Control Conversion Rate]
    VAR BestVariant = MAX([Variant A Conversion Rate], [Variant B Conversion Rate])
    RETURN DIVIDE(BestVariant - ControlRate, ControlRate) * 100

// ─── Feature Metrics ───
Feature Adoption Rate =
    DIVIDE(
        DISTINCTCOUNT(fact_product_analytics[user_id]),
        CALCULATE(DISTINCTCOUNT(fact_product_analytics[user_id]), ALL(fact_product_analytics[feature_name]))
    ) * 100
```

---

## Page 7: AI Risk & Compliance

```dax
// ─── Risk Counts ───
Total Assessments =
    COUNTROWS(fact_risk_compliance)

Open Findings =
    CALCULATE(
        COUNTROWS(fact_risk_compliance),
        fact_risk_compliance[audit_status] = "open"
    )

Critical Risks =
    CALCULATE(
        COUNTROWS(fact_risk_compliance),
        fact_risk_compliance[risk_level] = "critical"
    )

High Risks =
    CALCULATE(
        COUNTROWS(fact_risk_compliance),
        fact_risk_compliance[risk_level] = "high"
    )

Critical High % =
    DIVIDE([Critical Risks] + [High Risks], [Total Assessments]) * 100

Resolution Rate =
    DIVIDE(
        CALCULATE(
            COUNTROWS(fact_risk_compliance),
            fact_risk_compliance[audit_status] IN {"resolved", "accepted"}
        ),
        [Total Assessments]
    ) * 100

// ─── Fairness Metrics ───
Avg Demographic Parity Ratio =
    AVERAGE(fact_risk_compliance[demographic_parity_ratio])

Avg Equalized Odds Ratio =
    AVERAGE(fact_risk_compliance[equalized_odds_ratio])

Avg Disparate Impact Ratio =
    AVERAGE(fact_risk_compliance[disparate_impact_ratio])

Fairness Compliant % =
    DIVIDE(
        CALCULATE(
            COUNTROWS(fact_risk_compliance),
            fact_risk_compliance[demographic_parity_ratio] >= 0.8
        ),
        [Total Assessments]
    ) * 100

// ─── PII ───
Total PII Exposures =
    SUM(fact_risk_compliance[pii_exposure_count])

Avg PII per Assessment =
    AVERAGE(fact_risk_compliance[pii_exposure_count])

// ─── Remediation ───
Overdue Remediations =
    CALCULATE(
        COUNTROWS(fact_risk_compliance),
        fact_risk_compliance[remediation_deadline] < TODAY(),
        fact_risk_compliance[audit_status] IN {"open", "in_review"}
    )

Remediation SLA % =
    1 - DIVIDE([Overdue Remediations], [Total Assessments])
```

---

## Page 8: Manufacturing Intelligence

```dax
// ─── OEE ───
OEE =
    AVERAGE(fact_manufacturing[oee_score])

OEE % =
    [OEE] * 100

OEE Target Gap =
    [OEE] - 0.85

// ─── Production ───
Total Production Output =
    SUM(fact_manufacturing[production_output_units])

Avg Quality Score =
    AVERAGE(fact_manufacturing[quality_score])

Total Downtime Hours =
    DIVIDE(SUM(fact_manufacturing[downtime_minutes]), 60)

Downtime % =
    DIVIDE(
        SUM(fact_manufacturing[downtime_minutes]),
        COUNTROWS(fact_manufacturing) * 60
    ) * 100

// ─── Alerts ───
Total Alerts =
    CALCULATE(
        COUNTROWS(fact_manufacturing),
        fact_manufacturing[alert_triggered] = TRUE
    )

Alert Rate % =
    DIVIDE([Total Alerts], COUNTROWS(fact_manufacturing)) * 100

// ─── Maintenance ───
Corrective Maintenance Count =
    CALCULATE(
        COUNTROWS(fact_manufacturing),
        fact_manufacturing[maintenance_type] = "corrective"
    )

Preventive Maintenance Count =
    CALCULATE(
        COUNTROWS(fact_manufacturing),
        fact_manufacturing[maintenance_type] = "preventive"
    )

Preventive to Corrective Ratio =
    DIVIDE([Preventive Maintenance Count], [Corrective Maintenance Count])

// ─── Energy ───
Total Energy Consumption =
    SUM(fact_manufacturing[energy_consumption_kwh])

Energy per Unit =
    DIVIDE(
        [Total Energy Consumption],
        [Total Production Output]
    )

Avg Energy per Reading =
    AVERAGE(fact_manufacturing[energy_consumption_kwh])
```
