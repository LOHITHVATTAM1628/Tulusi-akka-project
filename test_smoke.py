"""Quick smoke test for the AI Data Analyst project."""

import pandas as pd

from agents.data_agent import DataAnalystAgent
from utils.charts import suggest_chart, auto_chart
from utils.insights import generate_ai_insights
from utils.profiling import build_dataset_profile, get_kpi_metrics
from utils.reports import generate_excel_report, generate_pdf_report
from utils.security import safe_execute, validate_uploaded_file

df = pd.read_csv("data/sample_sales.csv")
profile = build_dataset_profile(df)
kpis = get_kpi_metrics(df, profile)

assert validate_uploaded_file("sample.csv", 1024)[0]
assert not validate_uploaded_file("sample.exe", 1024)[0]

result, err = safe_execute('result = df["revenue"].sum()', df)
assert err is None
assert result > 0

suggestion = suggest_chart(df, profile["column_types"])
assert suggestion is not None
fig = auto_chart(df, suggestion["type"], suggestion["params"])
assert fig is not None

insights = generate_ai_insights(df, profile)
assert "key_findings" in insights

pdf = generate_pdf_report(df, profile, insights)
excel = generate_excel_report(df, profile, insights)
assert len(pdf) > 100
assert len(excel) > 100

agent = DataAnalystAgent()
assert agent.is_configured is False or agent.is_configured is True

print("SMOKE TEST PASSED")
print(f"Rows: {profile['rows']}")
print(f"Revenue sum: {result:,.2f}")
print(f"KPIs: {kpis['total_records']} records")
