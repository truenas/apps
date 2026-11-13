import pytest

from base.error import RenderError


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
