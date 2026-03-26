"""
Master script to generate all synthetic datasets for the Power BI AI Analytics Dashboard.
Generates 8 domain-specific datasets with realistic distributions and correlations.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
Faker.seed(42)
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, 'analysis'), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, 'powerbi_ready'), exist_ok=True)


def generate_ml_model_registry(n=50):
    """Generate ML model registry with 50 models."""
    model_types = ['classification', 'regression', 'clustering', 'NLP', 'computer_vision']
    frameworks = ['sklearn', 'pytorch', 'tensorflow', 'xgboost']
    statuses = ['production', 'staging', 'retired']
    departments = ['Data Science', 'Engineering', 'Marketing', 'Finance', 'Operations', 'HR', 'Product']
    owners = [fake.name() for _ in range(20)]

    base_names = [
        'ChurnPredictor', 'FraudDetector', 'SentimentAnalyzer', 'DemandForecaster',
        'RecommenderEngine', 'PricingOptimizer', 'AnomalyDetector', 'CustomerSegmenter',
        'RiskScorer', 'LeadScorer', 'ImageClassifier', 'TextSummarizer',
        'EntityExtractor', 'SalesPredictor', 'InventoryOptimizer', 'QualityInspector',
        'RoutePlanner', 'CreditScorer', 'AttritionPredictor', 'ClickPredictor',
        'ObjectDetector', 'SpeechRecognizer', 'TranslationModel', 'ContentModerator',
        'DocumentParser'
    ]

    rows = []
    for i in range(n):
        name = np.random.choice(base_names)
        created = fake.date_between(start_date='-2y', end_date='-3m')
        last_trained = fake.date_between(start_date=created, end_date='today')
        status = np.random.choice(statuses, p=[0.5, 0.3, 0.2])
        rows.append({
            'model_id': f'MDL-{i+1:04d}',
            'model_name': f'{name}_v{np.random.randint(1, 10)}',
            'model_type': np.random.choice(model_types),
            'framework': np.random.choice(frameworks),
            'version': f'{np.random.randint(1, 5)}.{np.random.randint(0, 20)}.{np.random.randint(0, 50)}',
            'created_date': created,
            'last_trained': last_trained,
            'status': status,
            'owner': np.random.choice(owners),
            'department': np.random.choice(departments),
        })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, 'ml_model_registry.csv'), index=False)
    print(f"  ml_model_registry.csv: {len(df)} rows")
    return df


def generate_ml_model_metrics(registry_df, n=5000):
    """Generate ML model metrics — hourly for 30 days across models."""
    model_ids = registry_df['model_id'].tolist()
    production_models = registry_df[registry_df['status'] == 'production']['model_id'].tolist()
    if not production_models:
        production_models = model_ids[:10]

    base_time = datetime(2025, 12, 1)
    rows = []

    for i in range(n):
        model_id = np.random.choice(production_models)
        model_row = registry_df[registry_df['model_id'] == model_id].iloc[0]
        hours_offset = np.random.randint(0, 30 * 24)
        ts = base_time + timedelta(hours=hours_offset)

        base_accuracy = np.random.uniform(0.78, 0.98)
        day_factor = hours_offset / (30 * 24)
        drift = np.random.uniform(0, 0.15) * day_factor
        noise = np.random.normal(0, 0.02)

        accuracy = np.clip(base_accuracy - drift + noise, 0.5, 1.0)
        precision_val = np.clip(accuracy + np.random.normal(0, 0.03), 0.5, 1.0)
        recall = np.clip(accuracy + np.random.normal(-0.02, 0.04), 0.5, 1.0)
        f1 = 2 * (precision_val * recall) / (precision_val + recall) if (precision_val + recall) > 0 else 0
        auc_roc = np.clip(accuracy + np.random.normal(0.02, 0.02), 0.5, 1.0)
        mse = np.clip(np.random.exponential(0.05) + drift * 0.3, 0.001, 1.0)

        base_latency = np.random.choice([15, 30, 50, 100, 200])
        latency_p50 = base_latency * np.random.uniform(0.8, 1.2)
        latency_p99 = latency_p50 * np.random.uniform(2.5, 5.0)

        requests = int(np.random.exponential(500) + 50)
        error_rate = np.clip(np.random.exponential(0.01) + drift * 0.05, 0, 0.15)

        data_drift_score = np.clip(drift + np.random.normal(0, 0.03), 0, 1.0)
        pred_drift_score = np.clip(data_drift_score * np.random.uniform(0.5, 1.5), 0, 1.0)
        fi_stability = np.clip(1 - drift * 0.5 + np.random.normal(0, 0.05), 0, 1.0)

        rows.append({
            'metric_id': f'MET-{i+1:06d}',
            'model_id': model_id,
            'timestamp': ts,
            'accuracy': round(accuracy, 4),
            'precision': round(precision_val, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1, 4),
            'auc_roc': round(auc_roc, 4),
            'mse': round(mse, 6),
            'latency_p50_ms': round(latency_p50, 2),
            'latency_p99_ms': round(latency_p99, 2),
            'requests_per_minute': requests,
            'error_rate': round(error_rate, 5),
            'data_drift_score': round(data_drift_score, 4),
            'prediction_drift_score': round(pred_drift_score, 4),
            'feature_importance_stability': round(fi_stability, 4),
        })

    df = pd.DataFrame(rows).sort_values('timestamp').reset_index(drop=True)
    df.to_csv(os.path.join(DATA_DIR, 'ml_model_metrics.csv'), index=False)
    print(f"  ml_model_metrics.csv: {len(df)} rows")
    return df


def generate_genai_operations(n=20000):
    """Generate Gen AI operations data — 20K requests."""
    applications = ['chatbot', 'code_assistant', 'doc_processor', 'summarizer', 'translator', 'analyst']
    models = ['gpt-4o', 'gpt-4', 'claude-3', 'llama-3', 'mistral']
    statuses = ['success', 'error', 'timeout', 'rate_limited']
    status_probs = [0.88, 0.05, 0.04, 0.03]

    model_costs = {'gpt-4o': 0.005, 'gpt-4': 0.03, 'claude-3': 0.015, 'llama-3': 0.001, 'mistral': 0.002}
    base_time = datetime(2025, 11, 1)

    rows = []
    for i in range(n):
        ts = base_time + timedelta(seconds=np.random.randint(0, 60 * 24 * 3600))
        app = np.random.choice(applications)
        model = np.random.choice(models, p=[0.3, 0.15, 0.25, 0.2, 0.1])
        status = np.random.choice(statuses, p=status_probs)

        prompt_tokens = int(np.random.lognormal(6, 1))
        prompt_tokens = np.clip(prompt_tokens, 10, 8000)
        completion_tokens = int(prompt_tokens * np.random.uniform(0.3, 2.0)) if status == 'success' else 0
        total_tokens = prompt_tokens + completion_tokens
        cost = total_tokens * model_costs[model] / 1000

        latency = np.random.lognormal(6, 0.8) if status == 'success' else np.random.lognormal(8, 0.5)
        latency = np.clip(latency, 100, 120000)

        rating = np.random.choice([1, 2, 3, 4, 5, None], p=[0.03, 0.07, 0.15, 0.30, 0.25, 0.20]) if status == 'success' else None
        guardrail = np.random.random() < 0.08
        toxicity = np.clip(np.random.beta(1, 20), 0, 1) if status == 'success' else None
        relevance = np.clip(np.random.beta(8, 2), 0, 1) if status == 'success' else None
        groundedness = np.clip(np.random.beta(6, 3), 0, 1) if status == 'success' else None

        rows.append({
            'request_id': f'REQ-{i+1:06d}',
            'timestamp': ts,
            'application': app,
            'model': model,
            'prompt_tokens': int(prompt_tokens),
            'completion_tokens': int(completion_tokens),
            'total_tokens': int(total_tokens),
            'cost_usd': round(cost, 6),
            'latency_ms': round(latency, 2),
            'status': status,
            'user_rating': rating,
            'guardrail_triggered': guardrail,
            'toxicity_score': round(toxicity, 4) if toxicity is not None else None,
            'relevance_score': round(relevance, 4) if relevance is not None else None,
            'groundedness_score': round(groundedness, 4) if groundedness is not None else None,
        })

    df = pd.DataFrame(rows).sort_values('timestamp').reset_index(drop=True)
    df.to_csv(os.path.join(DATA_DIR, 'genai_operations.csv'), index=False)
    print(f"  genai_operations.csv: {len(df)} rows")
    return df


def generate_data_quality_metrics(n=3000):
    """Generate data quality metrics — daily for 60 days across 50 datasets."""
    dataset_names = [f'ds_{fake.word()}_{fake.word()}' for _ in range(50)]
    table_names = [f'tbl_{fake.word()}' for _ in range(100)]
    base_time = datetime(2025, 10, 1)

    rows = []
    for i in range(n):
        ds = np.random.choice(dataset_names)
        day_offset = np.random.randint(0, 60)
        ts = base_time + timedelta(days=day_offset)

        row_count = int(np.random.lognormal(12, 2))
        null_pct = np.clip(np.random.beta(2, 20), 0, 0.5) * 100
        dup_pct = np.clip(np.random.beta(1, 30), 0, 0.3) * 100
        schema_drift = np.random.random() < 0.05
        freshness = np.clip(np.random.exponential(4), 0.5, 72)

        completeness = np.clip(np.random.beta(15, 2), 0, 1)
        consistency = np.clip(np.random.beta(12, 3), 0, 1)
        validity = np.clip(np.random.beta(14, 2), 0, 1)
        overall = (completeness * 0.35 + consistency * 0.30 + validity * 0.35) + np.random.normal(0, 0.02)
        overall = np.clip(overall, 0, 1)

        anomaly = np.random.random() < 0.08
        sla_met = freshness < 24 and overall > 0.7

        rows.append({
            'scan_id': f'SCN-{i+1:05d}',
            'timestamp': ts,
            'dataset_name': ds,
            'table_name': np.random.choice(table_names),
            'row_count': row_count,
            'null_pct': round(null_pct, 2),
            'duplicate_pct': round(dup_pct, 2),
            'schema_drift_detected': schema_drift,
            'freshness_hours': round(freshness, 2),
            'completeness_score': round(completeness, 4),
            'consistency_score': round(consistency, 4),
            'validity_score': round(validity, 4),
            'overall_dq_score': round(overall, 4),
            'anomaly_detected': anomaly,
            'sla_met': sla_met,
        })

    df = pd.DataFrame(rows).sort_values('timestamp').reset_index(drop=True)
    df.to_csv(os.path.join(DATA_DIR, 'data_quality_metrics.csv'), index=False)
    print(f"  data_quality_metrics.csv: {len(df)} rows")
    return df


def generate_business_impact(n=500):
    """Generate business impact data — AI initiatives across departments."""
    departments = ['Data Science', 'Engineering', 'Marketing', 'Finance', 'Operations', 'Customer Success', 'HR']
    use_cases = [
        'Customer Churn Prediction', 'Fraud Detection', 'Demand Forecasting',
        'Personalization Engine', 'Process Automation', 'Predictive Maintenance',
        'Sentiment Analysis', 'Price Optimization', 'Document Processing',
        'Lead Scoring', 'Quality Inspection', 'Inventory Optimization',
        'Risk Assessment', 'Content Generation', 'Anomaly Detection'
    ]
    statuses = ['pilot', 'scaling', 'production', 'retired']
    quarters = ['2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4', '2025-Q1', '2025-Q2', '2025-Q3', '2025-Q4']

    rows = []
    for i in range(n):
        dept = np.random.choice(departments)
        investment = np.random.lognormal(11, 1.5)
        investment = np.clip(investment, 10000, 5000000)

        status = np.random.choice(statuses, p=[0.2, 0.25, 0.4, 0.15])
        maturity_factor = {'pilot': 0.2, 'scaling': 0.6, 'production': 1.0, 'retired': 0.3}[status]

        cost_savings = investment * np.random.uniform(0.1, 2.5) * maturity_factor
        revenue_uplift = investment * np.random.uniform(0, 1.5) * maturity_factor
        roi = ((cost_savings + revenue_uplift - investment) / investment) * 100

        rows.append({
            'initiative_id': f'INI-{i+1:04d}',
            'quarter': np.random.choice(quarters),
            'department': dept,
            'ai_use_case': np.random.choice(use_cases),
            'investment_usd': round(investment, 2),
            'cost_savings_usd': round(cost_savings, 2),
            'revenue_uplift_usd': round(revenue_uplift, 2),
            'roi_pct': round(roi, 2),
            'time_saved_hours': round(np.random.exponential(200) * maturity_factor, 1),
            'accuracy_improvement_pct': round(np.random.uniform(2, 35) * maturity_factor, 1),
            'customer_satisfaction_delta': round(np.random.normal(5, 3) * maturity_factor, 2),
            'adoption_rate_pct': round(np.clip(np.random.beta(3, 2) * 100, 5, 100), 1),
            'status': status,
        })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, 'business_impact.csv'), index=False)
    print(f"  business_impact.csv: {len(df)} rows")
    return df


def generate_product_analytics(n=30000):
    """Generate product analytics event data — 30K events."""
    features = [
        'dashboard', 'reports', 'search', 'settings', 'profile', 'notifications',
        'export', 'import', 'collaboration', 'api_playground', 'model_builder',
        'data_explorer', 'scheduler', 'alerts', 'marketplace'
    ]
    event_types = ['page_view', 'click', 'conversion', 'error']
    event_probs = [0.45, 0.35, 0.12, 0.08]
    devices = ['mobile', 'desktop', 'tablet']
    device_probs = [0.35, 0.55, 0.10]
    countries = ['US', 'UK', 'DE', 'FR', 'IN', 'JP', 'BR', 'CA', 'AU', 'SG']
    variants = ['A', 'B', 'control']

    base_time = datetime(2025, 11, 1)
    user_ids = [f'USR-{j:05d}' for j in range(2000)]

    rows = []
    for i in range(n):
        ts = base_time + timedelta(seconds=np.random.randint(0, 60 * 24 * 3600))
        user_id = np.random.choice(user_ids)
        session_id = f'SES-{np.random.randint(1, 50000):06d}'
        event_type = np.random.choice(event_types, p=event_probs)

        session_dur = np.random.lognormal(5, 1)
        pages = int(np.clip(np.random.poisson(5), 1, 50))
        conversion = 1 if event_type == 'conversion' else (1 if np.random.random() < 0.05 else 0)
        revenue = round(np.random.lognormal(3, 1.5), 2) if conversion else 0.0

        rows.append({
            'event_id': f'EVT-{i+1:06d}',
            'timestamp': ts,
            'user_id': user_id,
            'session_id': session_id,
            'feature_name': np.random.choice(features),
            'event_type': event_type,
            'device': np.random.choice(devices, p=device_probs),
            'country': np.random.choice(countries),
            'session_duration_sec': round(session_dur, 1),
            'pages_viewed': pages,
            'conversion_flag': conversion,
            'revenue_usd': revenue,
            'ab_test_variant': np.random.choice(variants),
            'feature_flag': np.random.choice([True, False], p=[0.7, 0.3]),
        })

    df = pd.DataFrame(rows).sort_values('timestamp').reset_index(drop=True)
    df.to_csv(os.path.join(DATA_DIR, 'product_analytics.csv'), index=False)
    print(f"  product_analytics.csv: {len(df)} rows")
    return df


def generate_risk_compliance(registry_df, n=2000):
    """Generate AI risk & compliance data — 2K assessments."""
    model_ids = registry_df['model_id'].tolist()
    risk_categories = ['bias', 'fairness', 'privacy', 'security', 'regulatory']
    risk_levels = ['critical', 'high', 'medium', 'low']
    risk_level_probs = [0.05, 0.15, 0.40, 0.40]
    audit_statuses = ['open', 'in_review', 'resolved', 'accepted']
    frameworks = ['GDPR', 'SOC2', 'HIPAA', 'EU_AI_Act']

    findings_templates = [
        'Model shows {} disparity in predictions across demographic groups',
        'Feature {} has disproportionate impact on protected class outcomes',
        'PII detected in {} training data samples without proper masking',
        'Model explanations insufficient for {} compliance requirements',
        'Data retention policy violation found in {} pipeline',
        'Adversarial vulnerability detected in {} input processing',
        'Consent tracking gap identified for {} data source',
        'Model card documentation missing for {} risk category',
        'Audit trail incomplete for {} model retraining cycle',
        'Threshold calibration needed for {} fairness metric',
    ]

    base_date = datetime(2025, 7, 1).date()
    rows = []
    for i in range(n):
        date = base_date + timedelta(days=np.random.randint(0, 180))
        risk_cat = np.random.choice(risk_categories)
        risk_lvl = np.random.choice(risk_levels, p=risk_level_probs)

        dp_ratio = np.clip(np.random.normal(0.85, 0.12), 0.3, 1.2)
        eo_ratio = np.clip(np.random.normal(0.80, 0.15), 0.3, 1.2)
        di_ratio = np.clip(np.random.normal(0.82, 0.10), 0.3, 1.2)
        pii_count = int(np.random.exponential(5)) if risk_cat == 'privacy' else 0

        audit_status = np.random.choice(audit_statuses, p=[0.25, 0.20, 0.35, 0.20])
        days_to_remediate = {'critical': 7, 'high': 30, 'medium': 90, 'low': 180}[risk_lvl]
        deadline = date + timedelta(days=days_to_remediate)

        finding_template = np.random.choice(findings_templates)
        finding = finding_template.format(fake.word())

        rows.append({
            'assessment_id': f'ASM-{i+1:05d}',
            'date': date,
            'model_id': np.random.choice(model_ids),
            'risk_category': risk_cat,
            'risk_level': risk_lvl,
            'finding': finding,
            'demographic_parity_ratio': round(dp_ratio, 4),
            'equalized_odds_ratio': round(eo_ratio, 4),
            'disparate_impact_ratio': round(di_ratio, 4),
            'pii_exposure_count': pii_count,
            'audit_status': audit_status,
            'remediation_deadline': deadline,
            'compliance_framework': np.random.choice(frameworks),
        })

    df = pd.DataFrame(rows).sort_values('date').reset_index(drop=True)
    df.to_csv(os.path.join(DATA_DIR, 'risk_compliance.csv'), index=False)
    print(f"  risk_compliance.csv: {len(df)} rows")
    return df


def generate_iot_manufacturing(n=20000):
    """Generate IoT/manufacturing data — 20K sensor readings."""
    machine_ids = [f'MCH-{j+1:03d}' for j in range(50)]
    sensor_types = ['temperature', 'vibration', 'pressure', 'humidity', 'rpm']

    sensor_params = {
        'temperature': {'mean': 75, 'std': 8, 'min': 40, 'max': 120, 'thresh_min': 50, 'thresh_max': 100},
        'vibration': {'mean': 2.5, 'std': 1.0, 'min': 0.1, 'max': 10, 'thresh_min': 0.5, 'thresh_max': 6},
        'pressure': {'mean': 100, 'std': 12, 'min': 60, 'max': 160, 'thresh_min': 70, 'thresh_max': 140},
        'humidity': {'mean': 45, 'std': 10, 'min': 10, 'max': 90, 'thresh_min': 20, 'thresh_max': 75},
        'rpm': {'mean': 3000, 'std': 400, 'min': 500, 'max': 5500, 'thresh_min': 1000, 'thresh_max': 5000},
    }

    maintenance_types = ['preventive', 'corrective', 'none']
    base_time = datetime(2025, 11, 1)

    rows = []
    for i in range(n):
        ts = base_time + timedelta(minutes=np.random.randint(0, 60 * 24 * 30))
        machine = np.random.choice(machine_ids)
        sensor = np.random.choice(sensor_types)
        params = sensor_params[sensor]

        value = np.random.normal(params['mean'], params['std'])
        value = np.clip(value, params['min'], params['max'])

        alert = value < params['thresh_min'] or value > params['thresh_max']
        maint = 'corrective' if alert and np.random.random() < 0.4 else (
            'preventive' if np.random.random() < 0.1 else 'none')

        downtime = np.random.exponential(30) if maint == 'corrective' else (
            np.random.exponential(10) if maint == 'preventive' else 0)

        output = int(np.random.normal(500, 80))
        output = max(0, output - int(downtime * 2))
        quality = np.clip(np.random.beta(15, 2), 0.5, 1.0)
        energy = np.random.lognormal(3, 0.4)

        availability = np.clip(1 - downtime / (24 * 60), 0, 1)
        performance = np.clip(output / 600, 0, 1)
        oee = availability * performance * quality

        rows.append({
            'reading_id': f'IOT-{i+1:06d}',
            'timestamp': ts,
            'machine_id': machine,
            'sensor_type': sensor,
            'reading_value': round(value, 3),
            'threshold_min': params['thresh_min'],
            'threshold_max': params['thresh_max'],
            'alert_triggered': alert,
            'maintenance_type': maint,
            'downtime_minutes': round(downtime, 1),
            'production_output_units': output,
            'quality_score': round(quality, 4),
            'energy_consumption_kwh': round(energy, 3),
            'oee_score': round(oee, 4),
        })

    df = pd.DataFrame(rows).sort_values('timestamp').reset_index(drop=True)
    df.to_csv(os.path.join(DATA_DIR, 'iot_manufacturing.csv'), index=False)
    print(f"  iot_manufacturing.csv: {len(df)} rows")
    return df


def main():
    print("=" * 60)
    print("Generating all synthetic datasets...")
    print("=" * 60)
    ensure_dirs()

    print("\n[1/8] ML Model Registry")
    registry = generate_ml_model_registry()

    print("[2/8] ML Model Metrics")
    generate_ml_model_metrics(registry)

    print("[3/8] Gen AI Operations")
    generate_genai_operations()

    print("[4/8] Data Quality Metrics")
    generate_data_quality_metrics()

    print("[5/8] Business Impact")
    generate_business_impact()

    print("[6/8] Product Analytics")
    generate_product_analytics()

    print("[7/8] Risk & Compliance")
    generate_risk_compliance(registry)

    print("[8/8] IoT / Manufacturing")
    generate_iot_manufacturing()

    print("\n" + "=" * 60)
    print("All datasets generated successfully in data/")
    print("=" * 60)


if __name__ == '__main__':
    main()
