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


def test_add_disallowed_label(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        c1.labels.add_label("com.docker.compose.service", "test_service")


def test_add_duplicate_label(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.labels.add_label("my.custom.label", "test_value")
    with pytest.raises(Exception):
        c1.labels.add_label("my.custom.label", "test_value1")


def test_add_label(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.labels.add_label("my.custom.label1", "test_value1")
    c1.labels.add_label("my.custom.label2", "test_value2")
    output = render.render()
    assert output["services"]["test_container"]["labels"] == {
        "my.custom.label1": "test_value1",
        "my.custom.label2": "test_value2",
    }
