import importlib
import sys
import os

import pytest

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


@pytest.mark.unit
@pytest.mark.parametrize(
    "module_name",
    [
        "server",
        "server_enhanced",
        "db_helper",
        "db_helper_updated",
        "logging_setup",
    ],
)
def test_modules_importable(module_name: str):
    """Verify key modules import without raising exceptions."""
    importlib.import_module(module_name)
