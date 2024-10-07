import pytest
import json

from render import Render


@pytest.fixture
def mock_values():
    return {
        "images": {
            "test_image": {
                "repository": "nginx",
                "tag": "latest",
            }
        },
    }


def test_add_container(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.set_stdin(True)

    output = render.render()

    assert "test_container" in output["services"]

    s1 = output["services"]["test_container"]
    assert len(output["services"]) == 1
    assert s1 == {
        "image": "nginx:latest",
        "stdin_open": True,
        "tty": False,
    }
