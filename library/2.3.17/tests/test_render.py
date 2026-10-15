import pytest


from base.render import Render


def test_values_cannot_be_modified(mock_values):
    render = Render(mock_values)
    render.values["test"] = "test"
    with pytest.raises(Exception):
        render.render()


def test_duplicate_containers(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        render.add_container("test_container", "test_image")


def test_no_containers(mock_values):
    render = Render(mock_values)
    with pytest.raises(Exception):
        render.render()
