"""MLOps analysis — model performance trends, drift detection, SLA compliance."""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
OUTPUT_DIR = os.path.join(DATA_DIR, 'analysis')


def load_data():
    registry = pd.read_csv(os.path.join(DATA_DIR, 'ml_model_registry.csv'))
    metrics = pd.read_csv(os.path.join(DATA_DIR, 'ml_model_metrics.csv'), parse_dates=['timestamp'])
    return registry, metrics


def model_performance_trends(metrics):
    """Compute daily performance trends per model."""
    metrics['date'] = metrics['timestamp'].dt.date
    trends = metrics.groupby(['model_id', 'date']).agg(
        avg_accuracy=('accuracy', 'mean'),
        avg_f1=('f1_score', 'mean'),
        avg_auc=('auc_roc', 'mean'),
        avg_mse=('mse', 'mean'),
        total_requests=('requests_per_minute', 'sum'),
        avg_error_rate=('error_rate', 'mean'),
    ).reset_index()
    return trends


def drift_detection(metrics):
    """Analyze drift scores over time."""
    metrics['date'] = metrics['timestamp'].dt.date
    drift = metrics.groupby(['model_id', 'date']).agg(
        avg_data_drift=('data_drift_score', 'mean'),
        max_data_drift=('data_drift_score', 'max'),
        avg_pred_drift=('prediction_drift_score', 'mean'),
        max_pred_drift=('prediction_drift_score', 'max'),
        drift_alert_count=('data_drift_score', lambda x: (x > 0.1).sum()),
    ).reset_index()
    return drift


def sla_compliance(metrics):
    """Compute SLA compliance: latency < 500ms, error rate < 2%."""
    metrics['latency_sla_met'] = metrics['latency_p99_ms'] < 500
    metrics['error_sla_met'] = metrics['error_rate'] < 0.02
    metrics['date'] = metrics['timestamp'].dt.date

    sla = metrics.groupby(['model_id', 'date']).agg(
        latency_sla_pct=('latency_sla_met', 'mean'),
        error_sla_pct=('error_sla_met', 'mean'),
        avg_latency_p50=('latency_p50_ms', 'mean'),
        avg_latency_p99=('latency_p99_ms', 'mean'),
    ).reset_index()
    sla['latency_sla_pct'] = (sla['latency_sla_pct'] * 100).round(2)
    sla['error_sla_pct'] = (sla['error_sla_pct'] * 100).round(2)
    return sla


def model_comparison(registry, metrics):
    """Build model comparison matrix."""
    comparison = metrics.groupby('model_id').agg(
        avg_accuracy=('accuracy', 'mean'),
        avg_precision=('precision', 'mean'),
        avg_recall=('recall', 'mean'),
        avg_f1=('f1_score', 'mean'),
        avg_latency_p99=('latency_p99_ms', 'mean'),
        avg_error_rate=('error_rate', 'mean'),
        total_requests=('requests_per_minute', 'sum'),
    ).reset_index()

    comparison = comparison.merge(
        registry[['model_id', 'model_name', 'model_type', 'framework', 'status']],
        on='model_id', how='left'
    )
    return comparison


def feature_importance_stability(metrics):
    """Track feature importance stability over time."""
    metrics['date'] = metrics['timestamp'].dt.date
    fi = metrics.groupby(['model_id', 'date']).agg(
        avg_fi_stability=('feature_importance_stability', 'mean'),
        min_fi_stability=('feature_importance_stability', 'min'),
        stability_std=('feature_importance_stability', 'std'),
    ).reset_index()
    fi['stability_std'] = fi['stability_std'].fillna(0)
    return fi


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    registry, metrics = load_data()

    print("MLOps Analysis")
    print("-" * 40)

    trends = model_performance_trends(metrics)
    print(f"  Performance trends: {len(trends)} rows")

    drift = drift_detection(metrics)
    high_drift_days = (drift['max_data_drift'] > 0.1).sum()
    print(f"  Drift alerts: {high_drift_days} model-days with high drift")

    sla = sla_compliance(metrics)
    avg_latency_sla = sla['latency_sla_pct'].mean()
    print(f"  Avg latency SLA compliance: {avg_latency_sla:.1f}%")

    comparison = model_comparison(registry, metrics)
    print(f"  Models compared: {len(comparison)}")

    fi = feature_importance_stability(metrics)
    avg_stability = fi['avg_fi_stability'].mean()
    print(f"  Avg feature importance stability: {avg_stability:.3f}")

    summary = comparison.copy()
    summary['avg_latency_p99'] = summary['avg_latency_p99'].round(2)
    summary['avg_error_rate'] = summary['avg_error_rate'].round(5)

    summary.to_csv(os.path.join(OUTPUT_DIR, 'mlops_summary.csv'), index=False)
    trends.to_csv(os.path.join(OUTPUT_DIR, 'mlops_trends.csv'), index=False)
    drift.to_csv(os.path.join(OUTPUT_DIR, 'mlops_drift.csv'), index=False)
    sla.to_csv(os.path.join(OUTPUT_DIR, 'mlops_sla.csv'), index=False)
    fi.to_csv(os.path.join(OUTPUT_DIR, 'mlops_fi_stability.csv'), index=False)

    print(f"\n  Exported to {OUTPUT_DIR}/mlops_*.csv")


if __name__ == '__main__':
    main()
