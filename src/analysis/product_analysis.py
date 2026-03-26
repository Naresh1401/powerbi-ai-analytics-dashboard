"""Product Analytics — user engagement, feature adoption, A/B testing, conversions."""

import os
import pandas as pd
import numpy as np
from scipy import stats

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
OUTPUT_DIR = os.path.join(DATA_DIR, 'analysis')


def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, 'product_analytics.csv'), parse_dates=['timestamp'])
    return df


def user_engagement_funnel(df):
    """Build user engagement funnel: visits → clicks → conversions."""
    funnel_data = []
    total_users = df['user_id'].nunique()
    total_sessions = df['session_id'].nunique()

    page_viewers = df[df['event_type'] == 'page_view']['user_id'].nunique()
    clickers = df[df['event_type'] == 'click']['user_id'].nunique()
    converters = df[df['conversion_flag'] == 1]['user_id'].nunique()

    for stage, count in [('Total Users', total_users), ('Page Viewers', page_viewers),
                         ('Clickers', clickers), ('Converters', converters)]:
        funnel_data.append({
            'stage': stage,
            'users': count,
            'pct_of_total': round(count / total_users * 100, 2),
        })

    return pd.DataFrame(funnel_data)


def feature_adoption(df):
    """Feature adoption rates and engagement metrics."""
    features = df.groupby('feature_name').agg(
        unique_users=('user_id', 'nunique'),
        total_events=('event_id', 'count'),
        avg_session_duration=('session_duration_sec', 'mean'),
        conversion_rate=('conversion_flag', 'mean'),
        total_revenue=('revenue_usd', 'sum'),
        click_rate=('event_type', lambda x: (x == 'click').mean()),
        error_rate=('event_type', lambda x: (x == 'error').mean()),
    ).reset_index()
    features['conversion_rate'] = (features['conversion_rate'] * 100).round(2)
    features['click_rate'] = (features['click_rate'] * 100).round(2)
    features['error_rate'] = (features['error_rate'] * 100).round(2)
    total_users = df['user_id'].nunique()
    features['adoption_pct'] = (features['unique_users'] / total_users * 100).round(2)
    return features


def ab_test_results(df):
    """A/B test analysis with statistical significance."""
    results = []
    for feature in df['feature_name'].unique():
        feat_df = df[df['feature_name'] == feature]
        variants = feat_df['ab_test_variant'].unique()

        if 'control' not in variants or len(variants) < 2:
            continue

        control = feat_df[feat_df['ab_test_variant'] == 'control']
        control_cr = control['conversion_flag'].mean()
        control_n = len(control)

        for variant in ['A', 'B']:
            if variant not in variants:
                continue
            test = feat_df[feat_df['ab_test_variant'] == variant]
            test_cr = test['conversion_flag'].mean()
            test_n = len(test)

            if control_n < 10 or test_n < 10:
                continue

            contingency = [
                [control['conversion_flag'].sum(), control_n - control['conversion_flag'].sum()],
                [test['conversion_flag'].sum(), test_n - test['conversion_flag'].sum()]
            ]
            try:
                chi2, p_value, _, _ = stats.chi2_contingency(contingency)
            except ValueError:
                p_value = 1.0

            lift = ((test_cr - control_cr) / control_cr * 100) if control_cr > 0 else 0

            results.append({
                'feature': feature,
                'variant': variant,
                'control_conversion_rate': round(control_cr * 100, 2),
                'variant_conversion_rate': round(test_cr * 100, 2),
                'lift_pct': round(lift, 2),
                'p_value': round(p_value, 4),
                'significant': p_value < 0.05,
                'control_n': control_n,
                'variant_n': test_n,
            })

    return pd.DataFrame(results)


def conversion_analysis(df):
    """Conversion trends over time by device and country."""
    df['date'] = df['timestamp'].dt.date
    conversions = df.groupby(['date', 'device']).agg(
        total_events=('event_id', 'count'),
        conversions=('conversion_flag', 'sum'),
        total_revenue=('revenue_usd', 'sum'),
    ).reset_index()
    conversions['conversion_rate'] = (conversions['conversions'] / conversions['total_events'] * 100).round(2)
    return conversions


def session_analytics(df):
    """Session-level analytics summary."""
    sessions = df.groupby('session_id').agg(
        user_id=('user_id', 'first'),
        device=('device', 'first'),
        country=('country', 'first'),
        events=('event_id', 'count'),
        duration=('session_duration_sec', 'max'),
        pages=('pages_viewed', 'max'),
        converted=('conversion_flag', 'max'),
        revenue=('revenue_usd', 'sum'),
    ).reset_index()

    session_summary = sessions.groupby('device').agg(
        total_sessions=('session_id', 'count'),
        avg_events=('events', 'mean'),
        avg_duration=('duration', 'mean'),
        avg_pages=('pages', 'mean'),
        conversion_rate=('converted', 'mean'),
        avg_revenue=('revenue', 'mean'),
    ).reset_index()
    session_summary['conversion_rate'] = (session_summary['conversion_rate'] * 100).round(2)
    return session_summary


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = load_data()

    print("Product Analytics")
    print("-" * 40)

    funnel = user_engagement_funnel(df)
    print(f"  Total users: {funnel.iloc[0]['users']:,}")
    print(f"  Conversion rate: {funnel.iloc[-1]['pct_of_total']:.2f}%")

    features = feature_adoption(df)
    top_feature = features.sort_values('total_revenue', ascending=False).iloc[0]
    print(f"  Top revenue feature: {top_feature['feature_name']} (${top_feature['total_revenue']:,.0f})")

    ab = ab_test_results(df)
    sig_tests = ab[ab['significant']].shape[0] if len(ab) > 0 else 0
    print(f"  Significant A/B test results: {sig_tests}")

    conversions = conversion_analysis(df)
    overall_cr = df['conversion_flag'].mean() * 100
    print(f"  Overall conversion rate: {overall_cr:.2f}%")

    sessions = session_analytics(df)
    print(f"  Session summary by device: {len(sessions)} device types")

    summary = features.copy()
    summary.to_csv(os.path.join(OUTPUT_DIR, 'product_summary.csv'), index=False)
    funnel.to_csv(os.path.join(OUTPUT_DIR, 'product_funnel.csv'), index=False)
    ab.to_csv(os.path.join(OUTPUT_DIR, 'product_ab_tests.csv'), index=False)
    conversions.to_csv(os.path.join(OUTPUT_DIR, 'product_conversions.csv'), index=False)
    sessions.to_csv(os.path.join(OUTPUT_DIR, 'product_sessions.csv'), index=False)

    print(f"\n  Exported to {OUTPUT_DIR}/product_*.csv")


if __name__ == '__main__':
    main()
