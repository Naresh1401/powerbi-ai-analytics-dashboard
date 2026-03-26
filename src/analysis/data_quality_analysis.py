"""Data Quality analysis — DQ score trends, SLA compliance, anomalies, schema drift."""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
OUTPUT_DIR = os.path.join(DATA_DIR, 'analysis')


def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, 'data_quality_metrics.csv'), parse_dates=['timestamp'])
    return df


def dq_score_trends(df):
    """Overall DQ score trends over time."""
    df['date'] = df['timestamp'].dt.date
    trends = df.groupby('date').agg(
        avg_overall_dq=('overall_dq_score', 'mean'),
        min_overall_dq=('overall_dq_score', 'min'),
        max_overall_dq=('overall_dq_score', 'max'),
        avg_completeness=('completeness_score', 'mean'),
        avg_consistency=('consistency_score', 'mean'),
        avg_validity=('validity_score', 'mean'),
        datasets_scanned=('dataset_name', 'nunique'),
    ).reset_index()
    return trends


def dataset_health_heatmap(df):
    """Create heatmap data: dataset × week → avg DQ score."""
    df['week'] = df['timestamp'].dt.isocalendar().week.astype(int)
    heatmap = df.groupby(['dataset_name', 'week']).agg(
        avg_dq_score=('overall_dq_score', 'mean'),
        scans=('scan_id', 'count'),
    ).reset_index()
    return heatmap


def sla_compliance(df):
    """SLA compliance rates by dataset."""
    sla = df.groupby('dataset_name').agg(
        total_scans=('scan_id', 'count'),
        sla_met_count=('sla_met', 'sum'),
        avg_freshness=('freshness_hours', 'mean'),
        avg_dq_score=('overall_dq_score', 'mean'),
    ).reset_index()
    sla['sla_compliance_pct'] = (sla['sla_met_count'] / sla['total_scans'] * 100).round(2)
    sla = sla.sort_values('sla_compliance_pct', ascending=True)
    return sla


def anomaly_frequency(df):
    """Anomaly detection frequency analysis."""
    df['date'] = df['timestamp'].dt.date
    anomalies = df.groupby(['date', 'dataset_name']).agg(
        anomaly_count=('anomaly_detected', 'sum'),
        scan_count=('scan_id', 'count'),
        avg_null_pct=('null_pct', 'mean'),
        avg_dup_pct=('duplicate_pct', 'mean'),
    ).reset_index()
    anomalies['anomaly_rate'] = (anomalies['anomaly_count'] / anomalies['scan_count'] * 100).round(2)
    return anomalies


def schema_drift_tracking(df):
    """Track schema drift events over time."""
    df['date'] = df['timestamp'].dt.date
    drift = df[df['schema_drift_detected']].groupby(['date', 'dataset_name']).agg(
        drift_count=('scan_id', 'count'),
        affected_tables=('table_name', 'nunique'),
    ).reset_index()
    return drift


def freshness_analysis(df):
    """Freshness SLA analysis by dataset."""
    freshness = df.groupby('dataset_name').agg(
        avg_freshness_hrs=('freshness_hours', 'mean'),
        max_freshness_hrs=('freshness_hours', 'max'),
        p95_freshness_hrs=('freshness_hours', lambda x: x.quantile(0.95)),
        stale_count=('freshness_hours', lambda x: (x > 24).sum()),
        total_scans=('scan_id', 'count'),
    ).reset_index()
    freshness['stale_rate_pct'] = (freshness['stale_count'] / freshness['total_scans'] * 100).round(2)
    return freshness


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = load_data()

    print("Data Quality Analysis")
    print("-" * 40)

    trends = dq_score_trends(df)
    avg_dq = df['overall_dq_score'].mean()
    print(f"  Average DQ score: {avg_dq:.3f}")

    heatmap = dataset_health_heatmap(df)
    print(f"  Heatmap cells: {len(heatmap)}")

    sla = sla_compliance(df)
    overall_sla = df['sla_met'].mean() * 100
    print(f"  Overall SLA compliance: {overall_sla:.1f}%")

    anomalies = anomaly_frequency(df)
    anomaly_rate = df['anomaly_detected'].mean() * 100
    print(f"  Anomaly rate: {anomaly_rate:.1f}%")

    drift = schema_drift_tracking(df)
    drift_events = df['schema_drift_detected'].sum()
    print(f"  Schema drift events: {drift_events}")

    freshness = freshness_analysis(df)
    stale_datasets = (freshness['stale_rate_pct'] > 10).sum()
    print(f"  Datasets with >10% stale rate: {stale_datasets}")

    summary = sla.copy()
    summary.to_csv(os.path.join(OUTPUT_DIR, 'data_quality_summary.csv'), index=False)
    trends.to_csv(os.path.join(OUTPUT_DIR, 'data_quality_trends.csv'), index=False)
    heatmap.to_csv(os.path.join(OUTPUT_DIR, 'data_quality_heatmap.csv'), index=False)
    anomalies.to_csv(os.path.join(OUTPUT_DIR, 'data_quality_anomalies.csv'), index=False)
    drift.to_csv(os.path.join(OUTPUT_DIR, 'data_quality_drift.csv'), index=False)
    freshness.to_csv(os.path.join(OUTPUT_DIR, 'data_quality_freshness.csv'), index=False)

    print(f"\n  Exported to {OUTPUT_DIR}/data_quality_*.csv")


if __name__ == '__main__':
    main()
