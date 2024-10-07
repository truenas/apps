import pytest


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


def test_values_cannot_be_modified(mock_values):
    render = Render(mock_values)
    render.values["test"] = "test"
    with pytest.raises(Exception):
        render.render()
