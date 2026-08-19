import importlib

import pytest


@pytest.mark.unit
@pytest.mark.parametrize(
    "module_name",
    [
        "codemie-sdlc.backend.server",
        "codemie-sdlc.backend.server_enhanced",
        "codemie-sdlc.backend.db_helper",
        "codemie-sdlc.backend.db_helper_updated",
        "codemie-sdlc.backend.logging_setup",
    ],
)
def test_modules_importable(module_name: str):
    """Verify key modules import without raising exceptions."""
    importlib.import_module(module_name)
