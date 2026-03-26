"""Manufacturing Intelligence analysis — OEE, alerts, maintenance, energy, production."""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
OUTPUT_DIR = os.path.join(DATA_DIR, 'analysis')


def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, 'iot_manufacturing.csv'), parse_dates=['timestamp'])
    return df


def oee_analysis(df):
    """OEE breakdown: availability × performance × quality by machine."""
    machine_oee = df.groupby('machine_id').agg(
        avg_oee=('oee_score', 'mean'),
        min_oee=('oee_score', 'min'),
        max_oee=('oee_score', 'max'),
        std_oee=('oee_score', 'std'),
        total_downtime=('downtime_minutes', 'sum'),
        total_output=('production_output_units', 'sum'),
        avg_quality=('quality_score', 'mean'),
        readings=('reading_id', 'count'),
    ).reset_index()

    total_possible_minutes = df.groupby('machine_id')['timestamp'].apply(
        lambda x: (x.max() - x.min()).total_seconds() / 60
    ).reset_index(name='total_minutes')

    machine_oee = machine_oee.merge(total_possible_minutes, on='machine_id', how='left')
    machine_oee['availability'] = np.clip(
        1 - machine_oee['total_downtime'] / machine_oee['total_minutes'].replace(0, 1), 0, 1
    )
    machine_oee['availability'] = machine_oee['availability'].round(4)
    return machine_oee


def oee_daily_trend(df):
    """Daily OEE trend across all machines."""
    df['date'] = df['timestamp'].dt.date
    daily = df.groupby('date').agg(
        avg_oee=('oee_score', 'mean'),
        total_output=('production_output_units', 'sum'),
        total_downtime=('downtime_minutes', 'sum'),
        avg_quality=('quality_score', 'mean'),
        alert_count=('alert_triggered', 'sum'),
    ).reset_index()
    return daily


def alert_correlation(df):
    """Alert frequency by sensor type and machine."""
    alerts = df[df['alert_triggered']].groupby(['machine_id', 'sensor_type']).agg(
        alert_count=('reading_id', 'count'),
        avg_reading=('reading_value', 'mean'),
        max_reading=('reading_value', 'max'),
    ).reset_index()
    return alerts


def alert_heatmap(df):
    """Alert heatmap: machine × hour-of-day."""
    df['hour'] = df['timestamp'].dt.hour
    heatmap = df[df['alert_triggered']].groupby(['machine_id', 'hour']).agg(
        alert_count=('reading_id', 'count'),
    ).reset_index()
    return heatmap


def maintenance_patterns(df):
    """Predictive maintenance pattern analysis."""
    maint = df[df['maintenance_type'] != 'none'].copy()
    patterns = maint.groupby(['machine_id', 'maintenance_type']).agg(
        maintenance_count=('reading_id', 'count'),
        total_downtime=('downtime_minutes', 'sum'),
        avg_downtime=('downtime_minutes', 'mean'),
        avg_oee_during=('oee_score', 'mean'),
    ).reset_index()

    maint['date'] = maint['timestamp'].dt.date
    mtbf = maint.groupby('machine_id').agg(
        first_maint=('date', 'min'),
        last_maint=('date', 'max'),
        maint_events=('reading_id', 'count'),
    ).reset_index()
    mtbf['days_span'] = (pd.to_datetime(mtbf['last_maint']) - pd.to_datetime(mtbf['first_maint'])).dt.days
    mtbf['mtbf_days'] = (mtbf['days_span'] / mtbf['maint_events']).round(1)
    return patterns, mtbf


def energy_efficiency(df):
    """Energy consumption trends and efficiency analysis."""
    df['date'] = df['timestamp'].dt.date
    energy = df.groupby(['date', 'machine_id']).agg(
        total_energy=('energy_consumption_kwh', 'sum'),
        total_output=('production_output_units', 'sum'),
        avg_oee=('oee_score', 'mean'),
    ).reset_index()
    energy['energy_per_unit'] = np.where(
        energy['total_output'] > 0,
        energy['total_energy'] / energy['total_output'],
        0
    )
    energy['energy_per_unit'] = energy['energy_per_unit'].round(4)
    return energy


def production_vs_quality(df):
    """Production output vs quality score analysis."""
    df['date'] = df['timestamp'].dt.date
    pq = df.groupby(['date', 'machine_id']).agg(
        total_output=('production_output_units', 'sum'),
        avg_quality=('quality_score', 'mean'),
        avg_oee=('oee_score', 'mean'),
        total_downtime=('downtime_minutes', 'sum'),
        alerts=('alert_triggered', 'sum'),
    ).reset_index()
    return pq


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = load_data()

    print("Manufacturing Intelligence Analysis")
    print("-" * 40)

    machine_oee = oee_analysis(df)
    avg_oee = df['oee_score'].mean()
    print(f"  Average OEE: {avg_oee:.3f} ({avg_oee * 100:.1f}%)")

    daily = oee_daily_trend(df)
    print(f"  Daily trend data points: {len(daily)}")

    alerts = alert_correlation(df)
    total_alerts = df['alert_triggered'].sum()
    print(f"  Total alerts: {total_alerts}")

    heatmap = alert_heatmap(df)
    print(f"  Alert heatmap cells: {len(heatmap)}")

    patterns, mtbf = maintenance_patterns(df)
    corrective = df[df['maintenance_type'] == 'corrective'].shape[0]
    preventive = df[df['maintenance_type'] == 'preventive'].shape[0]
    print(f"  Maintenance events — corrective: {corrective}, preventive: {preventive}")

    energy = energy_efficiency(df)
    avg_energy_unit = energy[energy['energy_per_unit'] > 0]['energy_per_unit'].mean()
    print(f"  Avg energy per unit: {avg_energy_unit:.4f} kWh")

    pq = production_vs_quality(df)
    print(f"  Production-quality data points: {len(pq)}")

    summary = machine_oee.copy()
    summary.to_csv(os.path.join(OUTPUT_DIR, 'manufacturing_summary.csv'), index=False)
    daily.to_csv(os.path.join(OUTPUT_DIR, 'manufacturing_daily.csv'), index=False)
    alerts.to_csv(os.path.join(OUTPUT_DIR, 'manufacturing_alerts.csv'), index=False)
    heatmap.to_csv(os.path.join(OUTPUT_DIR, 'manufacturing_alert_heatmap.csv'), index=False)
    patterns.to_csv(os.path.join(OUTPUT_DIR, 'manufacturing_maintenance.csv'), index=False)
    mtbf.to_csv(os.path.join(OUTPUT_DIR, 'manufacturing_mtbf.csv'), index=False)
    energy.to_csv(os.path.join(OUTPUT_DIR, 'manufacturing_energy.csv'), index=False)
    pq.to_csv(os.path.join(OUTPUT_DIR, 'manufacturing_production_quality.csv'), index=False)

    print(f"\n  Exported to {OUTPUT_DIR}/manufacturing_*.csv")


if __name__ == '__main__':
    main()
