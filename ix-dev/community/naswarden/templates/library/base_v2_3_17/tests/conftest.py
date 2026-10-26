import importlib.util
import sys
from pathlib import Path

import pytest

# The library dir is named after its version (e.g. "2.3.17"), which is not a valid package name.
# Register it as the "base" package, so its modules import each other relatively, the same way they do when rendered.
# This lives in tests/ and not the library root, the renderer imports every top level .py file of the library.
_lib_dir = Path(__file__).parent.parent
_spec = importlib.util.spec_from_file_location(
    "base", _lib_dir / "__init__.py", submodule_search_locations=[str(_lib_dir)]
)
_base = importlib.util.module_from_spec(_spec)
sys.modules["base"] = _base
_spec.loader.exec_module(_base)

from base.render import Render  # noqa: E402 - needs the "base" package registered above


# Shared by the test modules, a module defining its own mock_values overrides this one
@pytest.fixture
def mock_values():
    return {
        "images": {"test_image": {"repository": "nginx", "tag": "latest"}},
    }


# Built from mock_values before the test body runs,
# tests that change mock_values first have to create their own Render
@pytest.fixture
def render(mock_values):
    return Render(mock_values)


# The usual "test_container" on "test_image", with the healthcheck disabled
@pytest.fixture
def c1(render):
    container = render.add_container("test_container", "test_image")
    container.healthcheck.disable()
    return container
