import pytest

from base.error import RenderError


def test_add_dependency(render, c1):
    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()
    c1.depends.add_dependency("test_container2", "service_started")
    output = render.render()
    assert output["services"]["test_container"]["depends_on"]["test_container2"] == {"condition": "service_started"}


def test_add_dependency_invalid_condition(render, c1):
    render.add_container("test_container2", "test_image")
    with pytest.raises(RenderError, match=r"Depend Condition \[invalid_condition\] is not valid"):
        c1.depends.add_dependency("test_container2", "invalid_condition")


def test_add_dependency_missing_container(c1):
    with pytest.raises(RenderError, match=r"Dependency \[test_container2\] not found in defined containers"):
        c1.depends.add_dependency("test_container2", "service_started")


def test_add_dependency_duplicate(render, c1):
    render.add_container("test_container2", "test_image")
    c1.depends.add_dependency("test_container2", "service_started")
    with pytest.raises(RenderError, match=r"Dependency \[test_container2\] already added"):
        c1.depends.add_dependency("test_container2", "service_started")
