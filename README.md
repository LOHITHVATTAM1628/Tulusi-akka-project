# AI Data Analyst

A production-ready web application for analyzing CSV and Excel datasets using natural language. Built with **Streamlit**, **Pandas**, **Plotly**, **LangChain**, and **Google Gemini**.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![Gemini](https://img.shields.io/badge/Gemini-API-green)

## Features

- **File Upload** — CSV and XLSX support with validation and size limits
- **AI Chat** — ChatGPT-style interface with follow-up question support
- **Dataset Profiling** — Automatic detection of numerical, categorical, and datetime columns
- **Safe Analysis** — Gemini generates Pandas code executed in a sandboxed environment
- **Visualizations** — Interactive Plotly charts (bar, line, pie, scatter, histogram, heatmap)
- **Business Insights** — Key findings, trends, anomalies, correlations, and recommendations
- **KPI Dashboard** — Records, missing values, feature counts, and top categories
- **Reports** — Downloadable PDF and Excel summary reports

## Project Structure

```
AI_Data_Analyst/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (API keys)
├── .env.example            # Environment template
├── agents/
│   └── data_agent.py       # LangChain + Gemini analysis agent
├── utils/
│   ├── loader.py           # File loading utilities
│   ├── profiling.py        # Dataset profiling
│   ├── charts.py           # Plotly visualization engine
│   ├── insights.py         # Business insights generation
│   ├── reports.py          # PDF and Excel report generation
│   └── security.py         # Safe code execution sandbox
├── reports/                # Generated reports output directory
└── data/
    └── sample_sales.csv    # Sample dataset for testing
```

## Prerequisites

- Python 3.10 or higher
- Google Gemini API key ([Get one free](https://aistudio.google.com/apikey))

## Setup

### 1. Clone or navigate to the project

```bash
cd AI_Data_Analyst
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and add your API key:

```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```

Edit `.env`:

```env
GOOGLE_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
MAX_FILE_SIZE_MB=25
```

### 5. Run the application

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Usage

1. **Upload** a CSV or Excel file via the sidebar
2. Review the **KPI dashboard** and **dataset overview**
3. Ask questions in the **AI Chat** section
4. Explore **visualizations** and **business insights**
5. **Download** PDF or Excel reports

## Sample Prompts for Testing

Use `data/sample_sales.csv` to test these prompts:

| Prompt | Expected Behavior |
|--------|-------------------|
| What columns are in this dataset? | Schema overview |
| What is the total revenue? | Aggregation on `revenue` |
| Show top 5 regions by revenue | GroupBy + bar chart |
| What is the average units sold by product category? | GroupBy analysis |
| Are there correlations between numerical features? | Correlation heatmap |
| Which customer segment generates the most revenue? | Segment analysis |
| Show revenue trend over time | Line chart by date |
| What are the key business insights? | Insight summary |
| How many missing values are there? | Data quality check |
| Compare Electronics vs Clothing revenue | Category comparison |

## Security

- File type and size validation on upload
- Analysis code is validated via AST parsing before execution
- Blocked: imports, file I/O, `exec`/`eval`, dunder attributes, dangerous builtins
- Restricted namespace: only `df`, `pd`, `np`, and safe builtins
- Graceful error handling throughout the application

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | — | Google Gemini API key (required for AI) |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model name |
| `MAX_FILE_SIZE_MB` | `25` | Maximum upload file size |

## Tech Stack

- **Streamlit** — Web UI framework
- **Pandas / NumPy** — Data manipulation
- **Plotly** — Interactive charts
- **LangChain** — LLM orchestration
- **langchain-google-genai** — Gemini integration
- **ReportLab** — PDF report generation
- **openpyxl / xlsxwriter** — Excel support

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `GOOGLE_API_KEY is not set` | Add your key to `.env` and restart Streamlit |
| Excel file won't load | Ensure `openpyxl` is installed |
| Chart not rendering | Check that column names in the prompt match the dataset |
| API rate limits | Wait and retry, or switch to a different Gemini model |

## License

MIT License — free to use and modify.
