"""Gen AI Operations analysis — token usage, cost trends, quality scores, guardrails."""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
OUTPUT_DIR = os.path.join(DATA_DIR, 'analysis')


def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, 'genai_operations.csv'), parse_dates=['timestamp'])
    return df


def token_cost_trends(df):
    """Daily token usage and cost trends by model."""
    df['date'] = df['timestamp'].dt.date
    trends = df.groupby(['date', 'model']).agg(
        total_requests=('request_id', 'count'),
        total_prompt_tokens=('prompt_tokens', 'sum'),
        total_completion_tokens=('completion_tokens', 'sum'),
        total_tokens=('total_tokens', 'sum'),
        total_cost=('cost_usd', 'sum'),
        avg_cost_per_request=('cost_usd', 'mean'),
        avg_latency=('latency_ms', 'mean'),
    ).reset_index()
    return trends


def model_comparison(df):
    """Compare models on cost vs quality metrics."""
    success_df = df[df['status'] == 'success'].copy()
    comparison = success_df.groupby('model').agg(
        total_requests=('request_id', 'count'),
        total_cost=('cost_usd', 'sum'),
        avg_cost=('cost_usd', 'mean'),
        avg_latency=('latency_ms', 'mean'),
        median_latency=('latency_ms', 'median'),
        avg_relevance=('relevance_score', 'mean'),
        avg_groundedness=('groundedness_score', 'mean'),
        avg_toxicity=('toxicity_score', 'mean'),
        avg_rating=('user_rating', 'mean'),
    ).reset_index()
    comparison['cost_per_1k_tokens'] = (comparison['total_cost'] / (
        success_df.groupby('model')['total_tokens'].sum().values / 1000
    )).round(4)
    return comparison


def guardrail_analysis(df):
    """Analyze guardrail trigger patterns."""
    df['date'] = df['timestamp'].dt.date
    guardrail = df.groupby(['date', 'application']).agg(
        total_requests=('request_id', 'count'),
        guardrail_triggers=('guardrail_triggered', 'sum'),
    ).reset_index()
    guardrail['trigger_rate'] = (guardrail['guardrail_triggers'] / guardrail['total_requests'] * 100).round(2)
    return guardrail


def application_metrics(df):
    """Compute per-application usage and quality metrics."""
    app_metrics = df.groupby('application').agg(
        total_requests=('request_id', 'count'),
        success_rate=('status', lambda x: (x == 'success').mean() * 100),
        total_cost=('cost_usd', 'sum'),
        avg_tokens=('total_tokens', 'mean'),
        avg_latency=('latency_ms', 'mean'),
        guardrail_rate=('guardrail_triggered', 'mean'),
    ).reset_index()
    app_metrics['success_rate'] = app_metrics['success_rate'].round(2)
    app_metrics['guardrail_rate'] = (app_metrics['guardrail_rate'] * 100).round(2)
    return app_metrics


def quality_distributions(df):
    """Quality score distributions for successful requests."""
    success = df[df['status'] == 'success'].copy()
    quality = success.groupby('model').agg(
        relevance_mean=('relevance_score', 'mean'),
        relevance_std=('relevance_score', 'std'),
        relevance_p25=('relevance_score', lambda x: x.quantile(0.25)),
        relevance_p75=('relevance_score', lambda x: x.quantile(0.75)),
        groundedness_mean=('groundedness_score', 'mean'),
        groundedness_std=('groundedness_score', 'std'),
        toxicity_mean=('toxicity_score', 'mean'),
        toxicity_p95=('toxicity_score', lambda x: x.quantile(0.95)),
    ).reset_index()
    return quality


def error_analysis(df):
    """Error and timeout rate analysis over time."""
    df['date'] = df['timestamp'].dt.date
    errors = df.groupby(['date', 'model']).agg(
        total=('request_id', 'count'),
        errors=('status', lambda x: (x == 'error').sum()),
        timeouts=('status', lambda x: (x == 'timeout').sum()),
        rate_limited=('status', lambda x: (x == 'rate_limited').sum()),
    ).reset_index()
    errors['error_rate'] = (errors['errors'] / errors['total'] * 100).round(2)
    errors['timeout_rate'] = (errors['timeouts'] / errors['total'] * 100).round(2)
    return errors


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = load_data()

    print("Gen AI Operations Analysis")
    print("-" * 40)

    trends = token_cost_trends(df)
    total_cost = df['cost_usd'].sum()
    print(f"  Total cost: ${total_cost:,.2f}")

    comparison = model_comparison(df)
    print(f"  Models analyzed: {len(comparison)}")

    guardrail = guardrail_analysis(df)
    trigger_rate = df['guardrail_triggered'].mean() * 100
    print(f"  Overall guardrail trigger rate: {trigger_rate:.1f}%")

    app_met = application_metrics(df)
    print(f"  Applications: {len(app_met)}")

    quality = quality_distributions(df)
    success = df[df['status'] == 'success']
    avg_relevance = success['relevance_score'].mean()
    print(f"  Avg relevance score: {avg_relevance:.3f}")

    errors = error_analysis(df)
    overall_error_rate = (df['status'] != 'success').mean() * 100
    print(f"  Overall non-success rate: {overall_error_rate:.1f}%")

    summary = comparison.copy()
    summary.to_csv(os.path.join(OUTPUT_DIR, 'genai_ops_summary.csv'), index=False)
    trends.to_csv(os.path.join(OUTPUT_DIR, 'genai_ops_trends.csv'), index=False)
    guardrail.to_csv(os.path.join(OUTPUT_DIR, 'genai_ops_guardrails.csv'), index=False)
    app_met.to_csv(os.path.join(OUTPUT_DIR, 'genai_ops_apps.csv'), index=False)
    quality.to_csv(os.path.join(OUTPUT_DIR, 'genai_ops_quality.csv'), index=False)
    errors.to_csv(os.path.join(OUTPUT_DIR, 'genai_ops_errors.csv'), index=False)

    print(f"\n  Exported to {OUTPUT_DIR}/genai_ops_*.csv")


if __name__ == '__main__':
    main()
