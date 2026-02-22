from trestle.api.nih_reporter import build_payload, flatten_project_for_csv


def test_smoke_package_import() -> None:
    payload = build_payload(limit=5, offset=0)
    assert payload["limit"] == 5
    assert payload["offset"] == 0
    assert "include_fields" in payload


def test_build_payload_formats_pi_names_as_name_criteria() -> None:
    payload = build_payload(pi_names=["Smith"])
    assert payload["criteria"]["pi_names"] == [
        {"first_name": "", "last_name": "", "any_name": "Smith"}
    ]


def test_flatten_project_for_csv_handles_snake_case_fields() -> None:
    project = {
        "appl_id": 123,
        "project_num": "R01AB123456",
        "project_title": "Test Project",
        "fiscal_year": 2024,
        "award_amount": 100000,
        "organization": {"org_name": "Example University", "org_city": "Boston", "org_state": "MA"},
        "principal_investigators": [{"full_name": "Alice Smith"}],
        "project_start_date": "2024-01-01",
        "project_end_date": "2025-12-31",
    }
    row = flatten_project_for_csv(project)

    assert row["ApplId"] == 123
    assert row["ProjectNum"] == "R01AB123456"
    assert row["ProjectTitle"] == "Test Project"
    assert row["FiscalYear"] == 2024
    assert row["AwardAmount"] == 100000
    assert row["OrgName"] == "Example University"
    assert row["PI_Names"] == "Alice Smith"
