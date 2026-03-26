# Power Query M Transformations

Power Query M code for data import, type conversions, joins, and calculated columns in Power BI.

---

## 1. Data Type Conversions

### ML Model Metrics — Type Assignment

```powerquery-m
let
    Source = Csv.Document(File.Contents("data/powerbi_ready/fact_model_metrics.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(PromotedHeaders, {
        {"model_key", type text},
        {"timestamp", type datetime},
        {"accuracy", type number},
        {"precision", type number},
        {"recall", type number},
        {"f1_score", type number},
        {"auc_roc", type number},
        {"mse", type number},
        {"latency_p50_ms", type number},
        {"latency_p99_ms", type number},
        {"requests_per_minute", Int64.Type},
        {"error_rate", type number},
        {"data_drift_score", type number},
        {"prediction_drift_score", type number},
        {"feature_importance_stability", type number},
        {"date", type date},
        {"date_key", Int64.Type}
    })
in
    TypedColumns
```

### Gen AI Operations — Type Assignment

```powerquery-m
let
    Source = Csv.Document(File.Contents("data/powerbi_ready/fact_genai_operations.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(PromotedHeaders, {
        {"request_id", type text},
        {"timestamp", type datetime},
        {"app_key", type text},
        {"model", type text},
        {"prompt_tokens", Int64.Type},
        {"completion_tokens", Int64.Type},
        {"total_tokens", Int64.Type},
        {"cost_usd", Currency.Type},
        {"latency_ms", type number},
        {"status", type text},
        {"user_rating", Int64.Type},
        {"guardrail_triggered", type logical},
        {"toxicity_score", type number},
        {"relevance_score", type number},
        {"groundedness_score", type number},
        {"date", type date},
        {"date_key", Int64.Type}
    })
in
    TypedColumns
```

---

## 2. Date Table Generation

Generate a standalone date table if not importing the pre-built `dim_date.csv`.

```powerquery-m
let
    StartDate = #date(2024, 1, 1),
    EndDate = #date(2026, 12, 31),
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    DateList = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    DateTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"date"}, null, ExtraValues.Error),
    TypedDate = Table.TransformColumnTypes(DateTable, {{"date", type date}}),
    AddDateKey = Table.AddColumn(TypedDate, "date_key", each Number.From(Date.ToText([date], "yyyyMMdd")), Int64.Type),
    AddYear = Table.AddColumn(AddDateKey, "year", each Date.Year([date]), Int64.Type),
    AddQuarter = Table.AddColumn(AddYear, "quarter", each Date.QuarterOfYear([date]), Int64.Type),
    AddQuarterName = Table.AddColumn(AddQuarter, "quarter_name", each "Q" & Text.From(Date.QuarterOfYear([date])), type text),
    AddYearQuarter = Table.AddColumn(AddQuarterName, "year_quarter", each Text.From(Date.Year([date])) & "-Q" & Text.From(Date.QuarterOfYear([date])), type text),
    AddMonth = Table.AddColumn(AddYearQuarter, "month", each Date.Month([date]), Int64.Type),
    AddMonthName = Table.AddColumn(AddMonth, "month_name", each Date.MonthName([date]), type text),
    AddMonthShort = Table.AddColumn(AddMonthName, "month_short", each Text.Start(Date.MonthName([date]), 3), type text),
    AddYearMonth = Table.AddColumn(AddMonthShort, "year_month", each Date.ToText([date], "yyyy-MM"), type text),
    AddWeek = Table.AddColumn(AddYearMonth, "week", each Date.WeekOfYear([date]), Int64.Type),
    AddDayOfWeek = Table.AddColumn(AddWeek, "day_of_week", each Date.DayOfWeek([date], Day.Monday), Int64.Type),
    AddDayName = Table.AddColumn(AddDayOfWeek, "day_name", each Date.DayOfWeekName([date]), type text),
    AddDayOfMonth = Table.AddColumn(AddDayName, "day_of_month", each Date.Day([date]), Int64.Type),
    AddIsWeekend = Table.AddColumn(AddDayOfMonth, "is_weekend", each Date.DayOfWeek([date], Day.Monday) >= 5, type logical),
    AddFiscalYear = Table.AddColumn(AddIsWeekend, "fiscal_year", each if Date.Month([date]) >= 7 then Date.Year([date]) + 1 else Date.Year([date]), Int64.Type),
    AddFiscalQuarter = Table.AddColumn(AddFiscalYear, "fiscal_quarter", each if Date.Month([date]) >= 7 then Number.RoundDown((Date.Month([date]) - 7) / 3) + 1 else Number.RoundDown((Date.Month([date]) + 5) / 3) + 1, Int64.Type)
in
    AddFiscalQuarter
```

---

## 3. Joins Between Fact and Dimension Tables

### Model Metrics with Model Dimension

```powerquery-m
let
    Source = fact_model_metrics,
    JoinModel = Table.NestedJoin(Source, {"model_key"}, dim_model, {"model_key"}, "ModelDim", JoinKind.LeftOuter),
    ExpandModel = Table.ExpandTableColumn(JoinModel, "ModelDim", {"model_name", "model_type", "framework", "status", "department"})
in
    ExpandModel
```

### Gen AI with Application Dimension

```powerquery-m
let
    Source = fact_genai_operations,
    JoinApp = Table.NestedJoin(Source, {"app_key"}, dim_application, {"app_key"}, "AppDim", JoinKind.LeftOuter),
    ExpandApp = Table.ExpandTableColumn(JoinApp, "AppDim", {"app_name", "app_category", "business_unit"})
in
    ExpandApp
```

### Manufacturing with Machine Dimension

```powerquery-m
let
    Source = fact_manufacturing,
    JoinMachine = Table.NestedJoin(Source, {"machine_key"}, dim_machine, {"machine_key"}, "MachineDim", JoinKind.LeftOuter),
    ExpandMachine = Table.ExpandTableColumn(JoinMachine, "MachineDim", {"machine_name", "machine_line", "machine_type"})
in
    ExpandMachine
```

---

## 4. Column Transformations

### Latency Bucketing (Model Metrics)

```powerquery-m
let
    Source = fact_model_metrics,
    AddLatencyBucket = Table.AddColumn(Source, "latency_bucket", each
        if [latency_p99_ms] < 50 then "< 50ms"
        else if [latency_p99_ms] < 100 then "50-100ms"
        else if [latency_p99_ms] < 200 then "100-200ms"
        else if [latency_p99_ms] < 500 then "200-500ms"
        else if [latency_p99_ms] < 1000 then "500ms-1s"
        else "> 1s",
        type text
    )
in
    AddLatencyBucket
```

### Cost Tier (Gen AI Operations)

```powerquery-m
let
    Source = fact_genai_operations,
    AddCostTier = Table.AddColumn(Source, "cost_tier", each
        if [cost_usd] < 0.01 then "Micro (< $0.01)"
        else if [cost_usd] < 0.05 then "Low ($0.01-$0.05)"
        else if [cost_usd] < 0.20 then "Medium ($0.05-$0.20)"
        else if [cost_usd] < 1.00 then "High ($0.20-$1.00)"
        else "Very High (> $1.00)",
        type text
    )
in
    AddCostTier
```

### Risk Score Calculation (Risk/Compliance)

```powerquery-m
let
    Source = fact_risk_compliance,
    AddRiskScore = Table.AddColumn(Source, "risk_score", each
        (if [risk_level] = "critical" then 4
         else if [risk_level] = "high" then 3
         else if [risk_level] = "medium" then 2
         else 1) *
        (if [audit_status] = "open" then 1.5
         else if [audit_status] = "in_review" then 1.2
         else 0.5),
        type number
    )
in
    AddRiskScore
```

### DQ Score Grade (Data Quality)

```powerquery-m
let
    Source = fact_data_quality,
    AddGrade = Table.AddColumn(Source, "dq_grade", each
        if [overall_dq_score] >= 0.95 then "A+"
        else if [overall_dq_score] >= 0.90 then "A"
        else if [overall_dq_score] >= 0.85 then "B+"
        else if [overall_dq_score] >= 0.80 then "B"
        else if [overall_dq_score] >= 0.70 then "C"
        else if [overall_dq_score] >= 0.60 then "D"
        else "F",
        type text
    )
in
    AddGrade
```

---

## 5. Filtering Out Test Data

### Remove Test/Demo Records

```powerquery-m
let
    Source = fact_product_analytics,
    FilterTestUsers = Table.SelectRows(Source, each
        not Text.StartsWith([user_id], "TEST_") and
        not Text.StartsWith([user_id], "DEMO_") and
        [user_id] <> "internal_bot"
    ),
    FilterTestSessions = Table.SelectRows(FilterTestUsers, each
        [session_duration_sec] > 0 and
        [session_duration_sec] < 86400
    )
in
    FilterTestSessions
```

### Remove Zero-Row Datasets from DQ

```powerquery-m
let
    Source = fact_data_quality,
    FilterEmpty = Table.SelectRows(Source, each [row_count] > 0)
in
    FilterEmpty
```

---

## 6. Creating Calculated Columns

### Hour Extraction for Time-of-Day Analysis

```powerquery-m
let
    Source = fact_genai_operations,
    AddHour = Table.AddColumn(Source, "hour_of_day", each Time.Hour(DateTime.Time([timestamp])), Int64.Type),
    AddTimeBlock = Table.AddColumn(AddHour, "time_block", each
        if [hour_of_day] < 6 then "Night (12AM-6AM)"
        else if [hour_of_day] < 12 then "Morning (6AM-12PM)"
        else if [hour_of_day] < 18 then "Afternoon (12PM-6PM)"
        else "Evening (6PM-12AM)",
        type text
    )
in
    AddTimeBlock
```

### Sensor Alert Status (Manufacturing)

```powerquery-m
let
    Source = fact_manufacturing,
    AddAlertStatus = Table.AddColumn(Source, "sensor_status", each
        if [alert_triggered] = true and [maintenance_type] = "corrective" then "Critical - Maintenance Required"
        else if [alert_triggered] = true then "Warning - Alert Active"
        else if [reading_value] > ([threshold_max] * 0.9) or [reading_value] < ([threshold_min] * 1.1) then "Caution - Near Threshold"
        else "Normal",
        type text
    ),
    AddOEECategory = Table.AddColumn(AddAlertStatus, "oee_category", each
        if [oee_score] >= 0.85 then "World Class"
        else if [oee_score] >= 0.70 then "Good"
        else if [oee_score] >= 0.50 then "Below Average"
        else "Poor",
        type text
    )
in
    AddOEECategory
```

### Business Impact ROI Category

```powerquery-m
let
    Source = fact_business_impact,
    AddROICategory = Table.AddColumn(Source, "roi_category", each
        if [roi_pct] > 100 then "Exceptional (>100%)"
        else if [roi_pct] > 50 then "Strong (50-100%)"
        else if [roi_pct] > 0 then "Positive (0-50%)"
        else "Negative (<0%)",
        type text
    ),
    AddInvestmentSize = Table.AddColumn(AddROICategory, "investment_size", each
        if [investment_usd] > 1000000 then "Enterprise (>$1M)"
        else if [investment_usd] > 250000 then "Large ($250K-$1M)"
        else if [investment_usd] > 50000 then "Medium ($50K-$250K)"
        else "Small (<$50K)",
        type text
    )
in
    AddInvestmentSize
```
