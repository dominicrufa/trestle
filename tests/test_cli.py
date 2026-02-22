import pytest

from trestle.api import cli


def test_parse_args_happy_path() -> None:
    args = cli.parse_args(
        ["--year", "2024", "--year", "2025", "--pi", "Smith", "--limit", "10", "--offset", "2"]
    )
    assert args.year == [2024, 2025]
    assert args.pi == ["Smith"]
    assert args.limit == 10
    assert args.offset == 2


@pytest.mark.parametrize(
    "argv",
    [
        ["--limit", "0"],
        ["--offset", "-1"],
        ["--print_n", "0"],
        ["--timeout", "0"],
    ],
)
def test_parse_args_rejects_invalid_bounds(argv: list[str]) -> None:
    with pytest.raises(SystemExit):
        cli.parse_args(argv)


def test_main_success_path(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(cli, "call_reporter", lambda payload, timeout_s: {"meta": {}, "results": []})

    written: dict[str, bool] = {"json": False, "csv": False}

    def _fake_write_json(path: str, data: dict) -> None:
        written["json"] = True

    def _fake_write_csv(path: str, data: list[dict]) -> None:
        written["csv"] = True

    monkeypatch.setattr(cli, "write_json", _fake_write_json)
    monkeypatch.setattr(cli, "write_csv", _fake_write_csv)

    rc = cli.main(["--pi", "Smith", "--limit", "1", "--out_json", "a.json", "--out_csv", "a.csv"])
    out = capsys.readouterr().out

    assert rc == 0
    assert "Request payload:" in out
    assert written["json"] is True
    assert written["csv"] is True


def test_main_failure_path(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def _boom(payload: dict, timeout_s: int) -> dict:
        raise RuntimeError("HTTP 400: bad payload")

    monkeypatch.setattr(cli, "call_reporter", _boom)
    rc = cli.main(["--pi", "Smith", "--limit", "1"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "Request failed:" in captured.err
