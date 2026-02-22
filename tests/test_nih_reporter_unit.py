import json
import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

from trestle.api.nih_reporter import (
    DEFAULT_INCLUDE_FIELDS,
    build_payload,
    call_reporter,
    flatten_project_for_csv,
    safe_get,
    write_csv,
    write_json,
)


def test_build_payload_defaults() -> None:
    payload = build_payload()
    assert payload["criteria"] == {}
    assert payload["offset"] == 0
    assert payload["limit"] == 10
    assert payload["include_fields"] == DEFAULT_INCLUDE_FIELDS


def test_build_payload_with_all_filters() -> None:
    payload = build_payload(
        fiscal_years=[2024, 2025],
        keywords=["cancer"],
        activity_codes=["R01"],
        org_names=["STANFORD UNIVERSITY"],
        pi_names=["Smith"],
        include_fields=["ProjectTitle"],
        offset=5,
        limit=25,
    )
    assert payload["criteria"]["fiscal_years"] == [2024, 2025]
    assert payload["criteria"]["keywords"] == ["cancer"]
    assert payload["criteria"]["activity_codes"] == ["R01"]
    assert payload["criteria"]["org_names"] == ["STANFORD UNIVERSITY"]
    assert payload["criteria"]["pi_names"] == [
        {"first_name": "", "last_name": "", "any_name": "Smith"}
    ]
    assert payload["include_fields"] == ["ProjectTitle"]
    assert payload["offset"] == 5
    assert payload["limit"] == 25


def test_call_reporter_success(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = {"meta": {"total": 1}, "results": [{"appl_id": 1}]}

    class _Response:
        ok = True
        status_code = 200
        text = ""

        @staticmethod
        def json() -> dict[str, object]:
            return expected

    def _fake_post(url: str, json: dict[str, object], timeout: int) -> _Response:
        assert "reporter.nih.gov" in url
        assert "criteria" in json
        assert timeout == 5
        return _Response()

    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(post=_fake_post))
    out = call_reporter({"criteria": {}}, timeout_s=5)
    assert out == expected


def test_call_reporter_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Response:
        ok = False
        status_code = 400
        text = "bad payload"

    def _fake_post(url: str, json: dict[str, object], timeout: int) -> _Response:
        return _Response()

    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(post=_fake_post))
    with pytest.raises(RuntimeError, match="HTTP 400"):
        call_reporter({"criteria": {}}, timeout_s=5)


def test_safe_get_nested_and_default() -> None:
    data = {"a": {"b": {"c": 3}}}
    assert safe_get(data, "a", "b", "c") == 3
    assert safe_get(data, "a", "x", default="missing") == "missing"


def test_flatten_project_for_csv_handles_mixed_field_styles() -> None:
    project = {
        "ApplId": 123,
        "project_num": "R01AB123456",
        "ProjectTitle": "Test Project",
        "fiscal_year": 2024,
        "AwardAmount": 100000,
        "organization": {"OrgName": "Example University", "org_city": "Boston", "org_state": "MA"},
        "PrincipalInvestigators": [{"full_name": "Alice Smith"}],
        "project_start_date": "2024-01-01",
        "ProjectEndDate": "2025-12-31",
    }
    row = flatten_project_for_csv(project)
    assert row["ApplId"] == 123
    assert row["ProjectNum"] == "R01AB123456"
    assert row["ProjectTitle"] == "Test Project"
    assert row["FiscalYear"] == 2024
    assert row["AwardAmount"] == 100000
    assert row["OrgName"] == "Example University"
    assert row["PI_Names"] == "Alice Smith"


def test_write_json_and_csv(tmp_path: Path) -> None:
    json_path = tmp_path / "out.json"
    csv_path = tmp_path / "out.csv"

    data = {"meta": {"total": 1}, "results": []}
    write_json(str(json_path), data)
    with open(json_path, encoding="utf-8") as file_handle:
        parsed = json.load(file_handle)
    assert parsed == data

    rows = [
        {
            "ApplId": 1,
            "ProjectNum": "R01AA000001",
            "ProjectTitle": "Title",
            "FiscalYear": 2025,
            "AwardAmount": 42,
            "Organization": {"OrgName": "Org"},
            "PrincipalInvestigators": [{"FullName": "A Smith"}],
            "ProjectStartDate": "2025-01-01",
            "ProjectEndDate": "2026-01-01",
        }
    ]
    write_csv(str(csv_path), rows)
    with open(csv_path, encoding="utf-8") as file_handle:
        content = file_handle.read()
    assert "ProjectTitle" in content
    assert "Title" in content
