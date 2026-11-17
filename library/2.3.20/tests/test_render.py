import os
import sys

import pytest

from base.error import RenderError
from base.render import Render


def test_values_cannot_be_modified(render):
    render.values["test"] = "test"
    with pytest.raises(RenderError, match=r"Values have been modified since the renderer was created"):
        render.render()


def test_duplicate_containers(render, c1):
    with pytest.raises(RenderError, match=r"Container test_container already exists"):
        render.add_container("test_container", "test_image")


def test_no_containers(render):
    with pytest.raises(RenderError, match=r"No containers added"):
        render.render()


def test_excepthook_exits_on_render_error(monkeypatch, capsys, mock_values):
    # Restored after the test, so the hook installed by Render does not leak into other tests
    monkeypatch.setattr(sys, "excepthook", lambda *_: pytest.fail("previous hook must not be called"))
    Render(mock_values)
    with pytest.raises(SystemExit) as exc_info:
        sys.excepthook(RenderError, RenderError("Invalid port"), None)
    assert exc_info.value.code == os.EX_CONFIG
    assert capsys.readouterr().err == "Invalid port\n"


def test_excepthook_passes_other_errors(monkeypatch, mock_values):
    calls = []
    monkeypatch.setattr(sys, "excepthook", lambda *args: calls.append(args))
    Render(mock_values)
    error = ValueError("boom")
    sys.excepthook(ValueError, error, None)
    assert calls == [(ValueError, error, None)]
