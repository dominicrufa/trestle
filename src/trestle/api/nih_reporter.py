#!/usr/bin/env python3
"""Minimal NIH RePORTER API (v2 projects/search) client helpers."""

from __future__ import annotations

import csv
import json
import re
from typing import Any

API_URL = "https://api.reporter.nih.gov/v2/projects/search"

DEFAULT_INCLUDE_FIELDS = [
    "ApplId",
    "ProjectTitle",
    "ProjectNum",
    "FiscalYear",
    "AwardAmount",
    "Organization",
    "PrincipalInvestigators",
    "AgencyIcFundings",
    "ProjectStartDate",
    "ProjectEndDate",
]


def build_payload(
    fiscal_years: list[int] | None = None,
    keywords: list[str] | None = None,
    activity_codes: list[str] | None = None,
    org_names: list[str] | None = None,
    pi_names: list[str] | None = None,
    include_fields: list[str] | None = None,
    offset: int = 0,
    limit: int = 10,
) -> dict[str, Any]:
    """Build the NIH RePORTER `projects/search` request payload.

    This composes the criteria filters and request paging fields used by
    the v2 endpoint. If `include_fields` is not provided, the module default
    field list is used to keep responses compact.
    """
    criteria: dict[str, Any] = {}

    if fiscal_years:
        criteria["fiscal_years"] = fiscal_years
    if keywords:
        criteria["keywords"] = keywords
    if activity_codes:
        criteria["activity_codes"] = activity_codes
    if org_names:
        criteria["org_names"] = org_names
    if pi_names:
        criteria["pi_names"] = [
            {"first_name": "", "last_name": "", "any_name": name} for name in pi_names
        ]

    payload: dict[str, Any] = {
        "criteria": criteria,
        "offset": offset,
        "limit": limit,
    }
    payload["include_fields"] = include_fields or DEFAULT_INCLUDE_FIELDS
    return payload


def call_reporter(payload: dict[str, Any], timeout_s: int = 60) -> dict[str, Any]:
    """Send a POST request to NIH RePORTER and return parsed JSON.

    Raises:
        RuntimeError: If `requests` is not installed or the API returns a
            non-2xx response.
    """
    try:
        import requests
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: requests. Install with `python -m pip install requests`."
        ) from exc

    response = requests.post(API_URL, json=payload, timeout=timeout_s)
    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text}")
    return response.json()


def safe_get(d: dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = d
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _normalize_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


def _get_value(d: dict[str, Any], *aliases: str, default: Any = None) -> Any:
    for alias in aliases:
        if alias in d:
            return d[alias]

    normalized = {_normalize_key(k): k for k in d}
    for alias in aliases:
        resolved = normalized.get(_normalize_key(alias))
        if resolved is not None:
            return d[resolved]
    return default


def flatten_project_for_csv(project: dict[str, Any]) -> dict[str, Any]:
    org = _get_value(project, "Organization", "organization", default={}) or {}
    pis = _get_value(
        project, "PrincipalInvestigators", "principal_investigators", default=[]
    ) or []

    pi_names: list[str] = []
    for pi in pis:
        if not isinstance(pi, dict):
            continue
        name = pi.get("FullName") or pi.get("full_name") or pi.get("Name") or pi.get("name")
        if name:
            pi_names.append(str(name))

    return {
        "ApplId": _get_value(project, "ApplId", "appl_id"),
        "ProjectNum": _get_value(project, "ProjectNum", "project_num"),
        "ProjectTitle": _get_value(project, "ProjectTitle", "project_title"),
        "FiscalYear": _get_value(project, "FiscalYear", "fiscal_year"),
        "AwardAmount": _get_value(project, "AwardAmount", "award_amount"),
        "OrgName": _get_value(org, "OrgName", "org_name"),
        "OrgCity": _get_value(org, "OrgCity", "org_city"),
        "OrgState": _get_value(org, "OrgState", "org_state"),
        "PI_Names": "; ".join(pi_names) if pi_names else None,
        "ProjectStartDate": _get_value(project, "ProjectStartDate", "project_start_date"),
        "ProjectEndDate": _get_value(project, "ProjectEndDate", "project_end_date"),
    }


def print_summary(data: dict[str, Any]) -> None:
    meta = data.get("meta") or {}
    results = data.get("results") or []
    total = meta.get("total")
    offset = meta.get("offset")
    limit = meta.get("limit")

    print("=== NIH RePORTER: projects/search ===")
    print(f"Returned: {len(results)}")
    if total is not None:
        print(f"Total matching: {total}")
    if offset is not None and limit is not None:
        print(f"Offset/Limit: {offset}/{limit}")
    print()


def print_projects(results: list[dict[str, Any]], max_rows: int = 10) -> None:
    n_rows = min(len(results), max_rows)
    for i in range(n_rows):
        project = results[i]
        title = _get_value(project, "ProjectTitle", "project_title")
        year = _get_value(project, "FiscalYear", "fiscal_year")
        amount = _get_value(project, "AwardAmount", "award_amount")
        org = _get_value(project, "Organization", "organization", default={}) or {}
        org_name = _get_value(org, "OrgName", "org_name")

        pis = _get_value(project, "PrincipalInvestigators", "principal_investigators", default=[]) or []
        pi_display = None
        if pis and isinstance(pis, list) and isinstance(pis[0], dict):
            pi_display = (
                _get_value(pis[0], "FullName", "full_name", "Name", "name")
            )

        if isinstance(amount, int):
            print(f"[{i + 1}] FY{year}  ${amount:,}")
        else:
            print(f"[{i + 1}] FY{year}  ${amount}")
        if title:
            print(f"     Title: {title}")
        if org_name:
            print(f"     Org:   {org_name}")
        if pi_display:
            print(f"     PI:    {pi_display}")
        appl_id = _get_value(project, "ApplId", "appl_id")
        project_num = _get_value(project, "ProjectNum", "project_num")
        if appl_id or project_num:
            print(f"     IDs:   ApplId={appl_id}  ProjectNum={project_num}")
        print()


def write_json(path: str, data: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as file_handle:
        json.dump(data, file_handle, indent=2)
    print(f"Wrote JSON: {path}")


def write_csv(path: str, results: list[dict[str, Any]]) -> None:
    rows = [flatten_project_for_csv(project) for project in results]
    if not rows:
        print("No rows to write to CSV.")
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote CSV: {path}")
