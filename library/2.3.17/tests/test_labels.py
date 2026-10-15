import pytest

from base.error import RenderError
from base.render import Render


def test_add_disallowed_label(c1):
    with pytest.raises(
        RenderError,
        match=r"Label \[com.docker.compose.service\] cannot start with \[com.docker.compose\]",
    ):
        c1.labels.add_label("com.docker.compose.service", "test_service")


def test_add_duplicate_label(c1):
    c1.labels.add_label("my.custom.label", "test_value")
    with pytest.raises(RenderError, match=r"Label \[my.custom.label\] already added"):
        c1.labels.add_label("my.custom.label", "test_value1")


def test_add_label_on_non_existing_container(mock_values):
    mock_values["labels"] = [
        {
            "key": "my.custom.label1",
            "value": "test_value1",
            "containers": ["test_container", "test_container2"],
        },
    ]
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(
        RenderError, match=r"Label \[my.custom.label1\] references container \[test_container2\] which does not exist"
    ):
        render.render()


def test_add_label(render, c1):
    c1.labels.add_label("my.custom.label1", "test_value1")
    c1.labels.add_label("my.custom.label2", "test_value2")
    output = render.render()
    assert output["services"]["test_container"]["labels"] == {
        "my.custom.label1": "test_value1",
        "my.custom.label2": "test_value2",
    }


def test_auto_add_labels(mock_values):
    mock_values["labels"] = [
        {
            "key": "my.custom.label1",
            "value": "test_value1",
            "containers": ["test_container", "test_container2"],
        },
        {
            "key": "my.custom.label2",
            "value": "test_value2",
            "containers": ["test_container"],
        },
    ]
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c2 = render.add_container("test_container2", "test_image")
    c1.healthcheck.disable()
    c2.healthcheck.disable()
    output = render.render()
    assert output["services"]["test_container"]["labels"] == {
        "my.custom.label1": "test_value1",
        "my.custom.label2": "test_value2",
    }
    assert output["services"]["test_container2"]["labels"] == {
        "my.custom.label1": "test_value1",
    }
