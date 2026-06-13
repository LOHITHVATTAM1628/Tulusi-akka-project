"""Generate PDF and Excel reports from the sample dataset."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from utils.insights import generate_ai_insights
from utils.profiling import build_dataset_profile
from utils.reports import generate_excel_report, generate_pdf_report

DATA_FILE = Path("data/sample_sales.csv")
REPORTS_DIR = Path("reports")


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(DATA_FILE)
    profile = build_dataset_profile(df)
    insights = generate_ai_insights(df, profile)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = REPORTS_DIR / f"data_analyst_report_{timestamp}.pdf"
    excel_path = REPORTS_DIR / f"data_summary_{timestamp}.xlsx"

    pdf_bytes = generate_pdf_report(
        df,
        profile,
        insights,
        title="AI Data Analyst Report — Sample Sales",
    )
    excel_bytes = generate_excel_report(df, profile, insights)

    pdf_path.write_bytes(pdf_bytes)
    excel_path.write_bytes(excel_bytes)

    print("Reports generated successfully!")
    print(f"  PDF   : {pdf_path.resolve()}")
    print(f"  Excel : {excel_path.resolve()}")
    print(f"  PDF size   : {len(pdf_bytes):,} bytes")
    print(f"  Excel size : {len(excel_bytes):,} bytes")


if __name__ == "__main__":
    main()
