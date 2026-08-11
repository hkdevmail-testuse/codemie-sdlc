import os
import time
from contextlib import contextmanager

import pytest


DEFAULT_BASE_URL = "http://127.0.0.1:5000"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--base-url",
        action="store",
        default=os.environ.get("BASE_URL", DEFAULT_BASE_URL),
        help="Base URL for the running Expense Tracker app (default: http://127.0.0.1:5000)",
    )


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    return str(request.config.getoption("--base-url")).rstrip("/")


@contextmanager
def _soft_timeout(seconds: float):
    start = time.time()
    yield
    elapsed = time.time() - start
    if elapsed > seconds:
        raise TimeoutError(f"Operation exceeded soft timeout: {elapsed:.2f}s > {seconds:.2f}s")


@pytest.fixture(scope="session")
def http_timeout_seconds() -> float:
    return float(os.environ.get("HTTP_TIMEOUT", "10"))


@pytest.fixture(scope="session")
def api_wait_timeout_seconds() -> float:
    return float(os.environ.get("API_WAIT_TIMEOUT", "20"))


@pytest.fixture(scope="session")
def api_is_up(base_url: str, api_wait_timeout_seconds: float, http_timeout_seconds: float):
    """Wait until the API is reachable.

    NOTE: We do not start the Flask server here; tests are designed to run against a running app.
    """
    import requests

    deadline = time.time() + api_wait_timeout_seconds
    last_exc: Exception | None = None

    while time.time() < deadline:
        try:
            r = requests.get(f"{base_url}/", timeout=http_timeout_seconds)
            if r.status_code in (200, 302):
                return True
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
        time.sleep(0.5)

    raise AssertionError(
        f"Expense Tracker app not reachable at {base_url} within {api_wait_timeout_seconds}s. Last error: {last_exc}"
    )
