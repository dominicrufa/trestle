import os
import time

import pytest

from trestle.api.nih_reporter import build_payload, call_reporter

pytestmark = pytest.mark.skipif(
    os.getenv("NIH_REPORTER_LIVE") != "1",
    reason="Set NIH_REPORTER_LIVE=1 to run live NIH RePORTER integration tests.",
)

_LAST_REQUEST_TS = 0.0


def _rate_limited_call(payload: dict, timeout_s: int = 60) -> dict:
    """Call NIH RePORTER while enforcing >=1 second between requests."""
    global _LAST_REQUEST_TS
    now = time.monotonic()
    wait_s = 1.0 - (now - _LAST_REQUEST_TS)
    if wait_s > 0:
        time.sleep(wait_s)
    data = call_reporter(payload, timeout_s=timeout_s)
    _LAST_REQUEST_TS = time.monotonic()
    return data


def test_live_reporter_smoke_smith() -> None:
    payload = build_payload(fiscal_years=[2025], pi_names=["Smith"], limit=1)
    first = _rate_limited_call(payload, timeout_s=60)
    second = _rate_limited_call(payload, timeout_s=60)

    assert "results" in first
    assert isinstance(first["results"], list)
    assert "results" in second
