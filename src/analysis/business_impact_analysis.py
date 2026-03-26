"""Business Impact analysis — ROI, investment vs returns, adoption, time savings."""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
OUTPUT_DIR = os.path.join(DATA_DIR, 'analysis')


def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, 'business_impact.csv'))
    return df


def roi_by_department(df):
    """ROI analysis by department and use case."""
    dept_roi = df.groupby('department').agg(
        total_investment=('investment_usd', 'sum'),
        total_savings=('cost_savings_usd', 'sum'),
        total_revenue_uplift=('revenue_uplift_usd', 'sum'),
        avg_roi=('roi_pct', 'mean'),
        median_roi=('roi_pct', 'median'),
        initiative_count=('initiative_id', 'count'),
    ).reset_index()
    dept_roi['net_return'] = dept_roi['total_savings'] + dept_roi['total_revenue_uplift'] - dept_roi['total_investment']
    dept_roi['overall_roi_pct'] = (dept_roi['net_return'] / dept_roi['total_investment'] * 100).round(2)
    return dept_roi


def roi_by_use_case(df):
    """ROI breakdown by AI use case."""
    uc_roi = df.groupby('ai_use_case').agg(
        total_investment=('investment_usd', 'sum'),
        total_savings=('cost_savings_usd', 'sum'),
        total_revenue_uplift=('revenue_uplift_usd', 'sum'),
        avg_roi=('roi_pct', 'mean'),
        initiative_count=('initiative_id', 'count'),
        avg_adoption=('adoption_rate_pct', 'mean'),
    ).reset_index()
    return uc_roi


def investment_vs_returns(df):
    """Scatter data: investment vs total returns."""
    scatter = df[['initiative_id', 'department', 'ai_use_case', 'status',
                   'investment_usd', 'cost_savings_usd', 'revenue_uplift_usd',
                   'roi_pct', 'adoption_rate_pct']].copy()
    scatter['total_return'] = scatter['cost_savings_usd'] + scatter['revenue_uplift_usd']
    scatter['net_return'] = scatter['total_return'] - scatter['investment_usd']
    scatter['profitable'] = scatter['net_return'] > 0
    return scatter


def adoption_trends(df):
    """Adoption rate trends by quarter and status."""
    adoption = df.groupby(['quarter', 'status']).agg(
        avg_adoption=('adoption_rate_pct', 'mean'),
        initiative_count=('initiative_id', 'count'),
        avg_roi=('roi_pct', 'mean'),
    ).reset_index()
    return adoption


def cost_savings_waterfall(df):
    """Waterfall breakdown of cost savings by department."""
    waterfall = df.groupby('department').agg(
        gross_investment=('investment_usd', 'sum'),
        cost_savings=('cost_savings_usd', 'sum'),
        revenue_uplift=('revenue_uplift_usd', 'sum'),
    ).reset_index()
    waterfall['net_impact'] = waterfall['cost_savings'] + waterfall['revenue_uplift'] - waterfall['gross_investment']
    waterfall = waterfall.sort_values('net_impact', ascending=False)
    return waterfall


def time_to_value(df):
    """Time saved analysis by status and department."""
    ttv = df.groupby(['department', 'status']).agg(
        total_time_saved=('time_saved_hours', 'sum'),
        avg_time_saved=('time_saved_hours', 'mean'),
        avg_accuracy_improvement=('accuracy_improvement_pct', 'mean'),
        avg_csat_delta=('customer_satisfaction_delta', 'mean'),
        initiative_count=('initiative_id', 'count'),
    ).reset_index()
    return ttv


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = load_data()

    print("Business Impact Analysis")
    print("-" * 40)

    dept = roi_by_department(df)
    total_investment = df['investment_usd'].sum()
    total_return = df['cost_savings_usd'].sum() + df['revenue_uplift_usd'].sum()
    print(f"  Total investment: ${total_investment:,.0f}")
    print(f"  Total return: ${total_return:,.0f}")
    print(f"  Overall ROI: {((total_return - total_investment) / total_investment * 100):.1f}%")

    uc = roi_by_use_case(df)
    top_uc = uc.sort_values('avg_roi', ascending=False).iloc[0]
    print(f"  Top use case by ROI: {top_uc['ai_use_case']} ({top_uc['avg_roi']:.1f}%)")

    scatter = investment_vs_returns(df)
    profitable_pct = scatter['profitable'].mean() * 100
    print(f"  Profitable initiatives: {profitable_pct:.1f}%")

    adoption = adoption_trends(df)
    avg_adoption = df['adoption_rate_pct'].mean()
    print(f"  Average adoption rate: {avg_adoption:.1f}%")

    waterfall = cost_savings_waterfall(df)
    ttv = time_to_value(df)
    total_hours = df['time_saved_hours'].sum()
    print(f"  Total time saved: {total_hours:,.0f} hours")

    summary = dept.copy()
    summary.to_csv(os.path.join(OUTPUT_DIR, 'business_impact_summary.csv'), index=False)
    uc.to_csv(os.path.join(OUTPUT_DIR, 'business_impact_use_cases.csv'), index=False)
    scatter.to_csv(os.path.join(OUTPUT_DIR, 'business_impact_scatter.csv'), index=False)
    adoption.to_csv(os.path.join(OUTPUT_DIR, 'business_impact_adoption.csv'), index=False)
    waterfall.to_csv(os.path.join(OUTPUT_DIR, 'business_impact_waterfall.csv'), index=False)
    ttv.to_csv(os.path.join(OUTPUT_DIR, 'business_impact_ttv.csv'), index=False)

    print(f"\n  Exported to {OUTPUT_DIR}/business_impact_*.csv")


if __name__ == '__main__':
    main()
