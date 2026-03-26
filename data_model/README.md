# Data Model Documentation

Star schema data model for the AI & Data Science Analytics Power BI Dashboard.

---

## Star Schema Diagram

```
                          ┌─────────────────┐
                          │    dim_date      │
                          │─────────────────│
                          │ date_key (PK)    │
                          │ date             │
                          │ year             │
                          │ quarter          │
                          │ month            │
                          │ week             │
                          │ day_of_week      │
                          │ fiscal_year      │
                          │ fiscal_quarter   │
                          └────────┬────────┘
                                   │
              ┌────────────────────┼────────────────────────┐
              │                    │                         │
              │                    │                         │
    ┌─────────▼──────────┐  ┌─────▼───────────────┐  ┌─────▼──────────────┐
    │ fact_model_metrics  │  │fact_genai_operations│  │ fact_data_quality   │
    │────────────────────│  │────────────────────│  │────────────────────│
    │ date_key (FK)       │  │ date_key (FK)       │  │ date_key (FK)       │
    │ model_key (FK)      │  │ app_key (FK)        │  │ scan_id (PK)        │
    │ accuracy            │  │ request_id (PK)     │  │ dataset_name        │
    │ precision           │  │ model               │  │ overall_dq_score    │
    │ recall              │  │ cost_usd            │  │ completeness_score  │
    │ f1_score            │  │ total_tokens        │  │ freshness_hours     │
    │ latency_p50_ms      │  │ latency_ms          │  │ sla_met             │
    │ data_drift_score    │  │ status              │  │ anomaly_detected    │
    │ error_rate          │  │ relevance_score     │  │ schema_drift        │
    └─────────┬──────────┘  └─────┬───────────────┘  └────────────────────┘
              │                    │
    ┌─────────▼──────────┐  ┌─────▼───────────────┐
    │    dim_model        │  │  dim_application     │
    │────────────────────│  │────────────────────│
    │ model_key (PK)      │  │ app_key (PK)        │
    │ model_name          │  │ app_name             │
    │ model_type          │  │ app_category         │
    │ framework           │  │ business_unit        │
    │ status              │  └────────────────────┘
    │ owner               │
    │ department           │
    └────────────────────┘


    ┌─────────────────────┐   ┌─────────────────────┐   ┌────────────────────┐
    │fact_business_impact  │   │fact_risk_compliance  │   │ fact_manufacturing │
    │─────────────────────│   │─────────────────────│   │────────────────────│
    │ initiative_id (PK)   │   │ assessment_id (PK)   │   │ reading_id (PK)    │
    │ department_key (FK)  │   │ date_key (FK)        │   │ date_key (FK)      │
    │ quarter              │   │ model_key (FK)       │   │ machine_key (FK)   │
    │ ai_use_case          │   │ risk_category        │   │ sensor_type        │
    │ investment_usd       │   │ risk_level           │   │ reading_value      │
    │ cost_savings_usd     │   │ finding              │   │ oee_score          │
    │ roi_pct              │   │ demographic_parity   │   │ downtime_minutes   │
    │ adoption_rate_pct    │   │ audit_status         │   │ production_output  │
    └──────────┬──────────┘   └──────────┬──────────┘   └──────────┬─────────┘
               │                          │                         │
    ┌──────────▼──────────┐   ┌──── (uses dim_model) ──┐   ┌──────▼─────────┐
    │  dim_department      │   │   via model_key (FK)   │   │  dim_machine    │
    │─────────────────────│   └────────────────────────┘   │────────────────│
    │ department_key (PK)  │                                │ machine_key(PK)│
    │ department_name      │                                │ machine_name   │
    │ division             │                                │ machine_line   │
    │ cost_center          │                                │ machine_type   │
    └─────────────────────┘                                └────────────────┘


    ┌──────────────────────┐
    │ fact_product_analytics│
    │──────────────────────│
    │ event_id (PK)         │
    │ date_key (FK)         │
    │ user_id               │
    │ session_id            │
    │ feature_name          │
    │ event_type            │
    │ device                │
    │ country               │
    │ conversion_flag       │
    │ revenue_usd           │
    │ ab_test_variant       │
    └──────────────────────┘
```

---

## Dimension Tables

| Table | Primary Key | Rows | Description |
|-------|-------------|------|-------------|
| `dim_date` | `date_key` | ~1,096 | Calendar dimension with fiscal year support |
| `dim_model` | `model_key` | 50 | ML model registry dimension |
| `dim_application` | `app_key` | 6 | Gen AI application dimension |
| `dim_department` | `department_key` | 8 | Business department dimension |
| `dim_machine` | `machine_key` | 50 | Manufacturing machine dimension |

---

## Fact Tables

| Table | Primary Key | Dimension FKs | Rows | Grain |
|-------|-------------|---------------|------|-------|
| `fact_model_metrics` | — | `date_key`, `model_key` | 5,000 | One row per model per hour |
| `fact_genai_operations` | `request_id` | `date_key`, `app_key` | 20,000 | One row per Gen AI request |
| `fact_data_quality` | `scan_id` | `date_key` | 3,000 | One row per dataset scan |
| `fact_business_impact` | `initiative_id` | `department_key` | 500 | One row per initiative per quarter |
| `fact_product_analytics` | `event_id` | `date_key` | 30,000 | One row per user event |
| `fact_risk_compliance` | `assessment_id` | `date_key`, `model_key` | 2,000 | One row per risk assessment |
| `fact_manufacturing` | `reading_id` | `date_key`, `machine_key` | 20,000 | One row per sensor reading |

---

## Relationships

| From (Dimension) | Key | To (Fact) | Key | Cardinality | Cross-Filter |
|-------------------|-----|-----------|-----|-------------|--------------|
| `dim_date` | `date_key` | `fact_model_metrics` | `date_key` | 1:Many | Single |
| `dim_date` | `date_key` | `fact_genai_operations` | `date_key` | 1:Many | Single |
| `dim_date` | `date_key` | `fact_data_quality` | `date_key` | 1:Many | Single |
| `dim_date` | `date_key` | `fact_product_analytics` | `date_key` | 1:Many | Single |
| `dim_date` | `date_key` | `fact_risk_compliance` | `date_key` | 1:Many | Single |
| `dim_date` | `date_key` | `fact_manufacturing` | `date_key` | 1:Many | Single |
| `dim_model` | `model_key` | `fact_model_metrics` | `model_key` | 1:Many | Single |
| `dim_model` | `model_key` | `fact_risk_compliance` | `model_key` | 1:Many | Single |
| `dim_application` | `app_key` | `fact_genai_operations` | `app_key` | 1:Many | Single |
| `dim_department` | `department_key` | `fact_business_impact` | `department_key` | 1:Many | Single |
| `dim_machine` | `machine_key` | `fact_manufacturing` | `machine_key` | 1:Many | Single |

---

## Role-Playing Dimensions

The `dim_date` table serves as a **role-playing dimension**, connecting to 6 fact tables simultaneously via the `date_key` foreign key. In Power BI:

- The **active relationship** should be set to the most commonly filtered fact table (recommend `fact_model_metrics` or `fact_genai_operations`)
- Use `USERELATIONSHIP()` in DAX for inactive relationships:

```dax
// Example: Filter manufacturing by date when dim_date is actively joined to another table
Manufacturing by Date =
    CALCULATE(
        [OEE],
        USERELATIONSHIP(dim_date[date_key], fact_manufacturing[date_key])
    )
```

Alternatively, enable **all relationships as active** since each fact table connects via the same column name (`date_key`), and Power BI handles multiple active relationships to different tables.

---

## Cardinality Summary

| Relationship Type | Count |
|--------------------|-------|
| 1:Many | 11 |
| Many:Many | 0 |
| 1:1 | 0 |

All cross-filter directions are **Single** (dimension → fact) for optimal performance. Avoid bidirectional filtering unless explicitly needed for specific DAX calculations.

---

## Data Volume Estimates

| Table | Rows | Columns | Approx Size (CSV) |
|-------|------|---------|--------------------|
| dim_date | 1,096 | 18 | ~80 KB |
| dim_model | 50 | 8 | ~5 KB |
| dim_application | 6 | 4 | ~1 KB |
| dim_department | 8 | 4 | ~1 KB |
| dim_machine | 50 | 5 | ~3 KB |
| fact_model_metrics | 5,000 | 17 | ~600 KB |
| fact_genai_operations | 20,000 | 17 | ~2.5 MB |
| fact_data_quality | 3,000 | 16 | ~400 KB |
| fact_business_impact | 500 | 14 | ~60 KB |
| fact_product_analytics | 30,000 | 15 | ~3.5 MB |
| fact_risk_compliance | 2,000 | 14 | ~300 KB |
| fact_manufacturing | 20,000 | 15 | ~2.5 MB |
| **Total** | **~81,710** | | **~10 MB** |
