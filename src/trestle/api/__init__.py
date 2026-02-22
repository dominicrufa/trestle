"""API clients and CLI utilities for Trestle."""

from .nih_reporter import (
    API_URL,
    DEFAULT_INCLUDE_FIELDS,
    build_payload,
    call_reporter,
    flatten_project_for_csv,
    print_projects,
    print_summary,
    safe_get,
    write_csv,
    write_json,
)

__all__ = [
    "API_URL",
    "DEFAULT_INCLUDE_FIELDS",
    "build_payload",
    "call_reporter",
    "flatten_project_for_csv",
    "print_projects",
    "print_summary",
    "safe_get",
    "write_csv",
    "write_json",
]
