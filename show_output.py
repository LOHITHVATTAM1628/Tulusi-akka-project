"""Print sample application output for demo purposes."""

import pandas as pd

from agents.data_agent import DataAnalystAgent
from utils.charts import suggest_chart
from utils.insights import generate_ai_insights, insights_to_markdown
from utils.profiling import build_dataset_profile, get_kpi_metrics, profile_to_text
from utils.reports import generate_excel_report, generate_pdf_report
from utils.security import safe_execute

df = pd.read_csv("data/sample_sales.csv")
profile = build_dataset_profile(df)
kpis = get_kpi_metrics(df, profile)
insights = generate_ai_insights(df, profile)

print("=" * 60)
print("DATASET PREVIEW (first 5 rows)")
print("=" * 60)
print(df.head().to_string())
print()

print("=" * 60)
print("KPI DASHBOARD")
print("=" * 60)
print(f"  Total Records      : {kpis['total_records']:,}")
print(f"  Missing Values     : {kpis['missing_values']:,} ({kpis['missing_pct']}%)")
print(f"  Numerical Features : {kpis['numerical_features']}")
print(f"  Categorical Features: {kpis['categorical_features']}")
print(f"  Datetime Features  : {kpis['datetime_features']}")
print(f"  Duplicate Rows     : {kpis['duplicate_rows']:,}")
print()

print("=" * 60)
print("DATASET PROFILE")
print("=" * 60)
print(profile_to_text(profile))
print()

print("=" * 60)
print("SAFE ANALYSIS OUTPUTS")
print("=" * 60)
total_rev, _ = safe_execute('result = df["revenue"].sum()', df)
print(f"  Total Revenue: ${total_rev:,.2f}")

by_region, _ = safe_execute(
    'result = df.groupby("region")["revenue"].sum().sort_values(ascending=False)',
    df,
)
print("\n  Revenue by Region:")
print(by_region.to_string(header=True))

by_category, _ = safe_execute(
    'result = df.groupby("product_category")["revenue"].mean().round(2)',
    df,
)
print("\n  Average Revenue by Category:")
print(by_category.to_string(header=True))
print()

print("=" * 60)
print("BUSINESS INSIGHTS")
print("=" * 60)
print(insights_to_markdown(insights))

print("=" * 60)
print("SUGGESTED CHART")
print("=" * 60)
suggestion = suggest_chart(df, profile["column_types"])
print(f"  Chart Type : {suggestion['type']}")
print(f"  Parameters : {suggestion['params']}")
print()

pdf_bytes = generate_pdf_report(df, profile, insights)
excel_bytes = generate_excel_report(df, profile, insights)
print("=" * 60)
print("REPORT GENERATION")
print("=" * 60)
print(f"  PDF Report Size  : {len(pdf_bytes):,} bytes")
print(f"  Excel Report Size: {len(excel_bytes):,} bytes")
print()

agent = DataAnalystAgent()
print("=" * 60)
print("AI AGENT STATUS")
print("=" * 60)
print(f"  Gemini API configured: {agent.is_configured}")
if agent.is_configured:
    print("  Running sample AI query: 'What is the total revenue?'")
    result = agent.analyze("What is the total revenue?", df, profile)
    print(f"\n  AI Answer:\n  {result['answer']}")
else:
    print("  Set GOOGLE_API_KEY in .env to enable AI chat responses.")
