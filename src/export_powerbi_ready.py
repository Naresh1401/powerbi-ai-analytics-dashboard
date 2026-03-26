"""Export Power BI-ready star-schema datasets with dimension and fact tables."""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
OUTPUT_DIR = os.path.join(DATA_DIR, 'powerbi_ready')


def create_date_dimension(start_date='2024-01-01', end_date='2026-12-31'):
    """Generate a comprehensive date dimension table for time intelligence."""
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    date_dim = pd.DataFrame({'date': dates})
    date_dim['date_key'] = date_dim['date'].dt.strftime('%Y%m%d').astype(int)
    date_dim['year'] = date_dim['date'].dt.year
    date_dim['quarter'] = date_dim['date'].dt.quarter
    date_dim['quarter_name'] = 'Q' + date_dim['quarter'].astype(str)
    date_dim['year_quarter'] = date_dim['year'].astype(str) + '-Q' + date_dim['quarter'].astype(str)
    date_dim['month'] = date_dim['date'].dt.month
    date_dim['month_name'] = date_dim['date'].dt.strftime('%B')
    date_dim['month_short'] = date_dim['date'].dt.strftime('%b')
    date_dim['year_month'] = date_dim['date'].dt.strftime('%Y-%m')
    date_dim['week'] = date_dim['date'].dt.isocalendar().week.astype(int)
    date_dim['day_of_week'] = date_dim['date'].dt.dayofweek
    date_dim['day_name'] = date_dim['date'].dt.strftime('%A')
    date_dim['day_of_month'] = date_dim['date'].dt.day
    date_dim['day_of_year'] = date_dim['date'].dt.dayofyear
    date_dim['is_weekend'] = date_dim['day_of_week'].isin([5, 6])
    date_dim['is_month_start'] = date_dim['date'].dt.is_month_start
    date_dim['is_month_end'] = date_dim['date'].dt.is_month_end
    date_dim['fiscal_year'] = np.where(date_dim['month'] >= 7,
                                        date_dim['year'] + 1, date_dim['year'])
    date_dim['fiscal_quarter'] = np.where(date_dim['month'] >= 7,
                                           (date_dim['month'] - 7) // 3 + 1,
                                           (date_dim['month'] + 5) // 3 + 1)
    return date_dim


def create_model_dimension(registry_df):
    """Create model dimension from registry."""
    dim = registry_df[['model_id', 'model_name', 'model_type', 'framework',
                        'version', 'status', 'owner', 'department']].copy()
    dim.rename(columns={'model_id': 'model_key'}, inplace=True)
    return dim


def create_application_dimension():
    """Create Gen AI application dimension."""
    apps = pd.DataFrame({
        'app_key': ['chatbot', 'code_assistant', 'doc_processor',
                     'summarizer', 'translator', 'analyst'],
        'app_name': ['Customer Chatbot', 'Code Assistant', 'Document Processor',
                      'Text Summarizer', 'Language Translator', 'Data Analyst'],
        'app_category': ['Customer Service', 'Developer Tools', 'Document Management',
                          'Content Processing', 'Localization', 'Analytics'],
        'business_unit': ['Customer Success', 'Engineering', 'Operations',
                           'Content', 'Marketing', 'Data Science'],
    })
    return apps


def create_department_dimension():
    """Create department dimension."""
    depts = pd.DataFrame({
        'department_key': ['Data Science', 'Engineering', 'Marketing', 'Finance',
                           'Operations', 'Customer Success', 'HR', 'Product'],
        'department_name': ['Data Science', 'Engineering', 'Marketing', 'Finance',
                            'Operations', 'Customer Success', 'Human Resources', 'Product'],
        'division': ['Technology', 'Technology', 'Revenue', 'Corporate',
                     'Operations', 'Revenue', 'Corporate', 'Technology'],
        'cost_center': ['CC-100', 'CC-101', 'CC-200', 'CC-300',
                        'CC-400', 'CC-201', 'CC-301', 'CC-102'],
    })
    return depts


def create_machine_dimension():
    """Create machine dimension for IoT data."""
    machines = pd.DataFrame({
        'machine_key': [f'MCH-{j+1:03d}' for j in range(50)],
        'machine_name': [f'Machine {j+1}' for j in range(50)],
        'machine_line': [f'Line {(j // 10) + 1}' for j in range(50)],
        'machine_type': np.random.choice(
            ['CNC Mill', 'Press', 'Lathe', 'Assembly', 'Welding',
             'Painting', 'Packaging', 'Testing'], size=50),
        'installation_year': np.random.choice(
            [2018, 2019, 2020, 2021, 2022, 2023], size=50),
    })
    return machines


def create_fact_model_metrics(metrics_df):
    """Create fact table for ML model metrics."""
    fact = metrics_df.copy()
    fact['date'] = pd.to_datetime(fact['timestamp']).dt.date
    fact['date_key'] = pd.to_datetime(fact['timestamp']).dt.strftime('%Y%m%d').astype(int)
    fact.rename(columns={'model_id': 'model_key'}, inplace=True)
    fact.drop(columns=['metric_id'], inplace=True, errors='ignore')
    return fact


def create_fact_genai(genai_df):
    """Create fact table for Gen AI operations."""
    fact = genai_df.copy()
    fact['date'] = pd.to_datetime(fact['timestamp']).dt.date
    fact['date_key'] = pd.to_datetime(fact['timestamp']).dt.strftime('%Y%m%d').astype(int)
    fact.rename(columns={'application': 'app_key'}, inplace=True)
    return fact


def create_fact_data_quality(dq_df):
    """Create fact table for data quality metrics."""
    fact = dq_df.copy()
    fact['date'] = pd.to_datetime(fact['timestamp']).dt.date
    fact['date_key'] = pd.to_datetime(fact['timestamp']).dt.strftime('%Y%m%d').astype(int)
    return fact


def create_fact_business_impact(bi_df):
    """Create fact table for business impact."""
    fact = bi_df.copy()
    fact.rename(columns={'department': 'department_key'}, inplace=True)
    return fact


def create_fact_product(prod_df):
    """Create fact table for product analytics."""
    fact = prod_df.copy()
    fact['date'] = pd.to_datetime(fact['timestamp']).dt.date
    fact['date_key'] = pd.to_datetime(fact['timestamp']).dt.strftime('%Y%m%d').astype(int)
    return fact


def create_fact_risk(risk_df):
    """Create fact table for risk & compliance."""
    fact = risk_df.copy()
    fact['date_key'] = pd.to_datetime(fact['date']).dt.strftime('%Y%m%d').astype(int)
    fact.rename(columns={'model_id': 'model_key'}, inplace=True)
    return fact


def create_fact_manufacturing(mfg_df):
    """Create fact table for IoT/manufacturing."""
    fact = mfg_df.copy()
    fact['date'] = pd.to_datetime(fact['timestamp']).dt.date
    fact['date_key'] = pd.to_datetime(fact['timestamp']).dt.strftime('%Y%m%d').astype(int)
    fact.rename(columns={'machine_id': 'machine_key'}, inplace=True)
    return fact


def export_relationship_docs():
    """Generate relationship documentation for Power BI."""
    relationships = [
        ('dim_date', 'date_key', 'fact_model_metrics', 'date_key', '1:*', 'Single'),
        ('dim_date', 'date_key', 'fact_genai_operations', 'date_key', '1:*', 'Single'),
        ('dim_date', 'date_key', 'fact_data_quality', 'date_key', '1:*', 'Single'),
        ('dim_date', 'date_key', 'fact_product_analytics', 'date_key', '1:*', 'Single'),
        ('dim_date', 'date_key', 'fact_risk_compliance', 'date_key', '1:*', 'Single'),
        ('dim_date', 'date_key', 'fact_manufacturing', 'date_key', '1:*', 'Single'),
        ('dim_model', 'model_key', 'fact_model_metrics', 'model_key', '1:*', 'Single'),
        ('dim_model', 'model_key', 'fact_risk_compliance', 'model_key', '1:*', 'Single'),
        ('dim_application', 'app_key', 'fact_genai_operations', 'app_key', '1:*', 'Single'),
        ('dim_department', 'department_key', 'fact_business_impact', 'department_key', '1:*', 'Single'),
        ('dim_machine', 'machine_key', 'fact_manufacturing', 'machine_key', '1:*', 'Single'),
    ]

    rel_df = pd.DataFrame(relationships,
                           columns=['from_table', 'from_column', 'to_table', 'to_column',
                                    'cardinality', 'cross_filter_direction'])
    return rel_df


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("Exporting Power BI-ready star schema datasets...")
    print("=" * 60)

    # Load raw data
    registry = pd.read_csv(os.path.join(DATA_DIR, 'ml_model_registry.csv'))
    metrics = pd.read_csv(os.path.join(DATA_DIR, 'ml_model_metrics.csv'))
    genai = pd.read_csv(os.path.join(DATA_DIR, 'genai_operations.csv'))
    dq = pd.read_csv(os.path.join(DATA_DIR, 'data_quality_metrics.csv'))
    bi = pd.read_csv(os.path.join(DATA_DIR, 'business_impact.csv'))
    prod = pd.read_csv(os.path.join(DATA_DIR, 'product_analytics.csv'))
    risk = pd.read_csv(os.path.join(DATA_DIR, 'risk_compliance.csv'))
    mfg = pd.read_csv(os.path.join(DATA_DIR, 'iot_manufacturing.csv'))

    # Dimension tables
    print("\nDimension tables:")
    date_dim = create_date_dimension()
    date_dim.to_csv(os.path.join(OUTPUT_DIR, 'dim_date.csv'), index=False)
    print(f"  dim_date: {len(date_dim)} rows")

    model_dim = create_model_dimension(registry)
    model_dim.to_csv(os.path.join(OUTPUT_DIR, 'dim_model.csv'), index=False)
    print(f"  dim_model: {len(model_dim)} rows")

    app_dim = create_application_dimension()
    app_dim.to_csv(os.path.join(OUTPUT_DIR, 'dim_application.csv'), index=False)
    print(f"  dim_application: {len(app_dim)} rows")

    dept_dim = create_department_dimension()
    dept_dim.to_csv(os.path.join(OUTPUT_DIR, 'dim_department.csv'), index=False)
    print(f"  dim_department: {len(dept_dim)} rows")

    machine_dim = create_machine_dimension()
    machine_dim.to_csv(os.path.join(OUTPUT_DIR, 'dim_machine.csv'), index=False)
    print(f"  dim_machine: {len(machine_dim)} rows")

    # Fact tables
    print("\nFact tables:")
    fact_metrics = create_fact_model_metrics(metrics)
    fact_metrics.to_csv(os.path.join(OUTPUT_DIR, 'fact_model_metrics.csv'), index=False)
    print(f"  fact_model_metrics: {len(fact_metrics)} rows")

    fact_genai = create_fact_genai(genai)
    fact_genai.to_csv(os.path.join(OUTPUT_DIR, 'fact_genai_operations.csv'), index=False)
    print(f"  fact_genai_operations: {len(fact_genai)} rows")

    fact_dq = create_fact_data_quality(dq)
    fact_dq.to_csv(os.path.join(OUTPUT_DIR, 'fact_data_quality.csv'), index=False)
    print(f"  fact_data_quality: {len(fact_dq)} rows")

    fact_bi = create_fact_business_impact(bi)
    fact_bi.to_csv(os.path.join(OUTPUT_DIR, 'fact_business_impact.csv'), index=False)
    print(f"  fact_business_impact: {len(fact_bi)} rows")

    fact_prod = create_fact_product(prod)
    fact_prod.to_csv(os.path.join(OUTPUT_DIR, 'fact_product_analytics.csv'), index=False)
    print(f"  fact_product_analytics: {len(fact_prod)} rows")

    fact_risk = create_fact_risk(risk)
    fact_risk.to_csv(os.path.join(OUTPUT_DIR, 'fact_risk_compliance.csv'), index=False)
    print(f"  fact_risk_compliance: {len(fact_risk)} rows")

    fact_mfg = create_fact_manufacturing(mfg)
    fact_mfg.to_csv(os.path.join(OUTPUT_DIR, 'fact_manufacturing.csv'), index=False)
    print(f"  fact_manufacturing: {len(fact_mfg)} rows")

    # Relationships documentation
    rel_df = export_relationship_docs()
    rel_df.to_csv(os.path.join(OUTPUT_DIR, 'relationships.csv'), index=False)
    print(f"\n  Relationships documented: {len(rel_df)}")

    print("\n" + "=" * 60)
    print(f"All Power BI-ready files exported to {OUTPUT_DIR}/")
    print("=" * 60)


if __name__ == '__main__':
    main()
