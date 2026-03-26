"""Risk & Compliance analysis — risk distribution, fairness metrics, compliance gaps."""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
OUTPUT_DIR = os.path.join(DATA_DIR, 'analysis')


def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, 'risk_compliance.csv'), parse_dates=['date'])
    df['remediation_deadline'] = pd.to_datetime(df['remediation_deadline'])
    return df


def risk_distribution(df):
    """Risk distribution by category and level."""
    dist = df.groupby(['risk_category', 'risk_level']).agg(
        count=('assessment_id', 'count'),
    ).reset_index()
    dist_pivot = dist.pivot_table(index='risk_category', columns='risk_level',
                                   values='count', fill_value=0).reset_index()
    for col in ['critical', 'high', 'medium', 'low']:
        if col not in dist_pivot.columns:
            dist_pivot[col] = 0
    dist_pivot['total'] = dist_pivot[['critical', 'high', 'medium', 'low']].sum(axis=1)
    dist_pivot['critical_high_pct'] = (
        (dist_pivot['critical'] + dist_pivot['high']) / dist_pivot['total'] * 100
    ).round(2)
    return dist_pivot


def fairness_metrics_tracking(df):
    """Track fairness metrics over time."""
    df['month'] = df['date'].dt.to_period('M').astype(str)
    fairness = df.groupby('month').agg(
        avg_demographic_parity=('demographic_parity_ratio', 'mean'),
        avg_equalized_odds=('equalized_odds_ratio', 'mean'),
        avg_disparate_impact=('disparate_impact_ratio', 'mean'),
        min_demographic_parity=('demographic_parity_ratio', 'min'),
        min_equalized_odds=('equalized_odds_ratio', 'min'),
        assessments=('assessment_id', 'count'),
    ).reset_index()
    fairness['dp_compliant'] = (fairness['avg_demographic_parity'] >= 0.8).astype(int)
    fairness['eo_compliant'] = (fairness['avg_equalized_odds'] >= 0.8).astype(int)
    return fairness


def compliance_gap_analysis(df):
    """Analyze compliance gaps by framework."""
    compliance = df.groupby(['compliance_framework', 'audit_status']).agg(
        count=('assessment_id', 'count'),
    ).reset_index()
    compliance_pivot = compliance.pivot_table(
        index='compliance_framework', columns='audit_status',
        values='count', fill_value=0
    ).reset_index()
    for col in ['open', 'in_review', 'resolved', 'accepted']:
        if col not in compliance_pivot.columns:
            compliance_pivot[col] = 0
    compliance_pivot['total'] = compliance_pivot[['open', 'in_review', 'resolved', 'accepted']].sum(axis=1)
    compliance_pivot['resolution_rate'] = (
        (compliance_pivot['resolved'] + compliance_pivot['accepted']) / compliance_pivot['total'] * 100
    ).round(2)
    compliance_pivot['open_rate'] = (
        compliance_pivot['open'] / compliance_pivot['total'] * 100
    ).round(2)
    return compliance_pivot


def remediation_sla_tracking(df):
    """Track remediation SLA compliance."""
    today = pd.Timestamp('2025-12-31')
    df['days_to_deadline'] = (df['remediation_deadline'] - today).dt.days
    df['overdue'] = df['days_to_deadline'] < 0
    df['sla_status'] = df.apply(
        lambda r: 'resolved' if r['audit_status'] in ('resolved', 'accepted')
        else ('overdue' if r['overdue'] else 'on_track'), axis=1
    )

    sla = df.groupby(['risk_level', 'sla_status']).agg(
        count=('assessment_id', 'count'),
    ).reset_index()
    sla_pivot = sla.pivot_table(index='risk_level', columns='sla_status',
                                 values='count', fill_value=0).reset_index()
    return sla_pivot


def pii_exposure_trends(df):
    """PII exposure count trends over time."""
    df['month'] = df['date'].dt.to_period('M').astype(str)
    pii = df[df['risk_category'] == 'privacy'].groupby('month').agg(
        total_pii_exposures=('pii_exposure_count', 'sum'),
        avg_pii_per_assessment=('pii_exposure_count', 'mean'),
        max_pii=('pii_exposure_count', 'max'),
        assessments=('assessment_id', 'count'),
    ).reset_index()
    return pii


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = load_data()

    print("Risk & Compliance Analysis")
    print("-" * 40)

    dist = risk_distribution(df)
    critical_count = df[df['risk_level'] == 'critical'].shape[0]
    high_count = df[df['risk_level'] == 'high'].shape[0]
    print(f"  Critical risks: {critical_count}, High risks: {high_count}")

    fairness = fairness_metrics_tracking(df)
    avg_dp = df['demographic_parity_ratio'].mean()
    print(f"  Avg demographic parity ratio: {avg_dp:.3f}")

    compliance = compliance_gap_analysis(df)
    open_findings = df[df['audit_status'] == 'open'].shape[0]
    print(f"  Open findings: {open_findings}")

    sla = remediation_sla_tracking(df)
    overdue = df[
        (df['audit_status'].isin(['open', 'in_review'])) &
        (df['remediation_deadline'] < pd.Timestamp('2025-12-31'))
    ].shape[0]
    print(f"  Overdue remediations: {overdue}")

    pii = pii_exposure_trends(df)
    total_pii = df['pii_exposure_count'].sum()
    print(f"  Total PII exposures: {total_pii}")

    summary = dist.copy()
    summary.to_csv(os.path.join(OUTPUT_DIR, 'risk_summary.csv'), index=False)
    fairness.to_csv(os.path.join(OUTPUT_DIR, 'risk_fairness.csv'), index=False)
    compliance.to_csv(os.path.join(OUTPUT_DIR, 'risk_compliance_gaps.csv'), index=False)
    sla.to_csv(os.path.join(OUTPUT_DIR, 'risk_remediation_sla.csv'), index=False)
    pii.to_csv(os.path.join(OUTPUT_DIR, 'risk_pii_trends.csv'), index=False)

    print(f"\n  Exported to {OUTPUT_DIR}/risk_*.csv")


if __name__ == '__main__':
    main()
