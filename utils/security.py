"""Security utilities for safe code execution and file validation."""

from __future__ import annotations

import ast
import re
from typing import Any

# Maximum characters allowed in generated analysis code.
MAX_CODE_LENGTH = 2000

# File extensions and MIME types we accept.
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
ALLOWED_MIME_TYPES = {
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/octet-stream",
}

# Dangerous patterns that must never appear in executed code.
BLOCKED_PATTERNS = [
    r"\bimport\b",
    r"\bfrom\b",
    r"\bexec\b",
    r"\beval\b",
    r"\bcompile\b",
    r"\bopen\b",
    r"\bos\b",
    r"\bsys\b",
    r"\bsubprocess\b",
    r"\bsocket\b",
    r"\brequests\b",
    r"\burllib\b",
    r"\bshutil\b",
    r"\bpathlib\b",
    r"\bglobals\b",
    r"\blocals\b",
    r"\b__\w+__\b",
    r"\bgetattr\b",
    r"\bsetattr\b",
    r"\bdelattr\b",
    r"\bbreakpoint\b",
    r"\binput\b",
    r"\bprint\b",
]

# AST node types that are not permitted in sandboxed code.
BLOCKED_AST_NODES = (
    ast.Import,
    ast.ImportFrom,
    ast.Global,
    ast.Nonlocal,
    ast.Lambda,
    ast.ClassDef,
    ast.AsyncFunctionDef,
    ast.Await,
    ast.Yield,
    ast.YieldFrom,
)


def validate_file_extension(filename: str) -> bool:
    """Return True if the file extension is allowed."""
    if not filename:
        return False
    lower = filename.lower()
    return any(lower.endswith(ext) for ext in ALLOWED_EXTENSIONS)


def validate_file_size(file_size_bytes: int, max_mb: float = 25.0) -> bool:
    """Return True if file size is within the configured limit."""
    return file_size_bytes <= max_mb * 1024 * 1024


def validate_uploaded_file(
    filename: str,
    file_size_bytes: int,
    max_mb: float = 25.0,
) -> tuple[bool, str]:
    """
    Validate an uploaded file's name and size.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not validate_file_extension(filename):
        return False, "Only CSV and Excel (.xlsx, .xls) files are supported."

    if not validate_file_size(file_size_bytes, max_mb):
        return False, f"File exceeds the maximum size of {max_mb:.0f} MB."

    return True, ""


def validate_analysis_code(code: str) -> tuple[bool, str]:
    """
    Validate Python/Pandas analysis code before sandboxed execution.

    Checks length, blocked patterns, and AST structure.
    """
    if not code or not code.strip():
        return False, "No analysis code was provided."

    stripped = code.strip()
    if len(stripped) > MAX_CODE_LENGTH:
        return False, f"Code exceeds maximum length of {MAX_CODE_LENGTH} characters."

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, stripped, re.IGNORECASE):
            return False, "Code contains disallowed operations for security reasons."

    try:
        tree = ast.parse(stripped, mode="exec")
    except SyntaxError as exc:
        return False, f"Invalid Python syntax: {exc}"

    for node in ast.walk(tree):
        if isinstance(node, BLOCKED_AST_NODES):
            return False, f"Disallowed construct: {type(node).__name__}"

        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in {"exec", "eval", "compile", "open"}:
                return False, f"Disallowed function call: {func.id}"

    return True, ""


def safe_execute(
    code: str,
    df: Any,
    extra_globals: dict[str, Any] | None = None,
) -> tuple[Any, str | None]:
    """
    Execute validated Pandas analysis code in a restricted namespace.

    Only `df`, `pd`, `np`, and whitelisted builtins are available.

    Returns:
        Tuple of (result, error_message). error_message is None on success.
    """
    is_valid, error = validate_analysis_code(code)
    if not is_valid:
        return None, error

    import numpy as np
    import pandas as pd

    safe_builtins = {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "dict": dict,
        "enumerate": enumerate,
        "float": float,
        "int": int,
        "len": len,
        "list": list,
        "max": max,
        "min": min,
        "range": range,
        "round": round,
        "set": set,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "zip": zip,
        "True": True,
        "False": False,
        "None": None,
    }

    namespace: dict[str, Any] = {
        "__builtins__": safe_builtins,
        "df": df.copy(),
        "pd": pd,
        "np": np,
    }
    if extra_globals:
        namespace.update(extra_globals)

    try:
        exec(compile(code.strip(), "<analysis>", "exec"), namespace)  # noqa: S102
        result = namespace.get("result")
        if result is None:
            result = namespace.get("df")
        return result, None
    except Exception as exc:  # noqa: BLE001
        return None, f"Execution error: {type(exc).__name__}: {exc}"
