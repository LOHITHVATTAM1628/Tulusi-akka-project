"""LangChain + Google Gemini data analysis agent."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import pandas as pd
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from utils.charts import auto_chart
from utils.loader import get_column_sample_values
from utils.profiling import profile_to_text
from utils.security import safe_execute


ANALYSIS_SYSTEM_PROMPT = """You are an expert AI Data Analyst. You help users analyze tabular data.

You have access to a Pandas DataFrame named `df`. When analysis requires computation, respond with a JSON object:

{
  "answer": "Clear human-readable explanation of findings",
  "needs_code": true,
  "code": "result = df.groupby('column')['value'].sum()",
  "chart": {
    "type": "bar|line|pie|scatter|histogram|heatmap|none",
    "params": {"x": "col", "y": "col", "title": "Chart title"}
  },
  "insights": ["optional bullet insight"]
}

Rules for code:
- Assign the final output to variable `result` (DataFrame, Series, or scalar).
- Use only `df`, `pd`, and `np`. No imports, no file I/O, no print.
- Keep code short and focused on the user's question.
- Use exact column names from the schema.

If no computation is needed (general question about schema), set needs_code to false and omit code.

For charts, set type to "none" if no visualization is appropriate.
Always return ONLY valid JSON, no markdown fences."""


class DataAnalystAgent:
    """AI agent that translates natural language into safe Pandas analysis."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        temperature: float = 0.2,
    ):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.temperature = temperature
        self._llm: ChatGoogleGenerativeAI | None = None

    @property
    def is_configured(self) -> bool:
        """Return True if a Gemini API key is available."""
        return bool(self.api_key)

    def _get_llm(self) -> ChatGoogleGenerativeAI:
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY is not set. Add it to your .env file."
            )
        if self._llm is None:
            self._llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=self.temperature,
            )
        return self._llm

    def _build_schema_context(self, df: pd.DataFrame, profile: dict[str, Any]) -> str:
        """Build rich schema context for the LLM."""
        samples = get_column_sample_values(df)
        sample_lines = [
            f"  - {col}: examples {vals}" for col, vals in samples.items()
        ]
        return (
            f"{profile_to_text(profile)}\n\n"
            f"Data types:\n"
            + "\n".join(f"  - {k}: {v}" for k, v in profile["dtypes"].items())
            + "\n\nSample values:\n"
            + "\n".join(sample_lines)
        )

    @staticmethod
    def _parse_agent_response(text: str) -> dict[str, Any]:
        """Parse JSON from the model response."""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {
                "answer": text,
                "needs_code": False,
                "chart": {"type": "none", "params": {}},
            }

    @staticmethod
    def _format_result(result: Any) -> str:
        """Format execution result for display."""
        if result is None:
            return "No result returned."
        if isinstance(result, pd.DataFrame):
            if len(result) > 20:
                return result.head(20).to_string() + f"\n\n... ({len(result)} rows total)"
            return result.to_string()
        if isinstance(result, pd.Series):
            if len(result) > 20:
                return result.head(20).to_string() + f"\n\n... ({len(result)} values total)"
            return result.to_string()
        return str(result)

    def analyze(
        self,
        question: str,
        df: pd.DataFrame,
        profile: dict[str, Any],
        chat_history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """
        Process a user question against the dataset.

        Returns dict with keys: answer, result_text, chart_figure, chart_error, insights, raw_response.
        """
        if not self.is_configured:
            return {
                "answer": (
                    "Gemini API key is not configured. Set GOOGLE_API_KEY in your .env file "
                    "to enable AI analysis. You can still explore data using the dashboard."
                ),
                "result_text": None,
                "chart_figure": None,
                "chart_error": None,
                "insights": [],
                "raw_response": None,
            }

        llm = self._get_llm()
        schema_context = self._build_schema_context(df, profile)

        messages: list[Any] = [
            SystemMessage(content=ANALYSIS_SYSTEM_PROMPT),
            SystemMessage(content=f"Current dataset schema:\n{schema_context}"),
        ]

        if chat_history:
            for turn in chat_history[-6:]:
                role = turn.get("role", "user")
                content = turn.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                else:
                    messages.append(AIMessage(content=content))

        messages.append(HumanMessage(content=question))

        try:
            response = llm.invoke(messages)
            content = response.content if hasattr(response, "content") else str(response)
            parsed = self._parse_agent_response(content)
        except Exception as exc:  # noqa: BLE001
            return {
                "answer": f"AI analysis failed: {exc}",
                "result_text": None,
                "chart_figure": None,
                "chart_error": None,
                "insights": [],
                "raw_response": None,
            }

        answer = parsed.get("answer", "Analysis complete.")
        result_text = None
        chart_figure = None
        chart_error = None
        insights = parsed.get("insights", [])

        if parsed.get("needs_code") and parsed.get("code"):
            result, error = safe_execute(parsed["code"], df)
            if error:
                answer = f"{answer}\n\n⚠️ Computation note: {error}"
            else:
                result_text = self._format_result(result)
                if result_text and result_text != "No result returned.":
                    answer = f"{answer}\n\n**Computed Result:**\n```\n{result_text}\n```"

        chart_spec = parsed.get("chart") or {}
        chart_type = chart_spec.get("type", "none")
        if chart_type and chart_type.lower() != "none":
            try:
                chart_figure = auto_chart(df, chart_type, chart_spec.get("params", {}))
            except Exception as exc:  # noqa: BLE001
                chart_error = str(exc)

        return {
            "answer": answer,
            "result_text": result_text,
            "chart_figure": chart_figure,
            "chart_error": chart_error,
            "insights": insights if isinstance(insights, list) else [],
            "raw_response": parsed,
        }

    def generate_dataset_summary(
        self,
        df: pd.DataFrame,
        profile: dict[str, Any],
    ) -> str:
        """Generate a natural-language dataset summary using Gemini."""
        if not self.is_configured:
            return profile_to_text(profile)

        llm = self._get_llm()
        prompt = f"""Summarize this dataset for a business stakeholder in 3-5 sentences.
Be specific about size, key columns, data quality, and potential analyses.

{profile_to_text(profile)}

Sample data:
{df.head(5).to_string()}"""

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content if hasattr(response, "content") else str(response)
        except Exception as exc:  # noqa: BLE001
            return f"{profile_to_text(profile)}\n\n(AI summary unavailable: {exc})"
