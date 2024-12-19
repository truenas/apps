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


def test_no_portals(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    output = render.render()
    assert output["x-portals"] == []


def test_add_portal(mock_values):
    render = Render(mock_values)
    render.portals.add_portal({"scheme": "http", "path": "/", "port": 8080})
    render.portals.add_portal({"name": "Other Portal", "scheme": "https", "path": "/", "port": 8443})
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    output = render.render()
    assert output["x-portals"] == [
        {"name": "Other Portal", "scheme": "https", "host": "0.0.0.0", "port": 8443, "path": "/"},
        {"name": "Web UI", "scheme": "http", "host": "0.0.0.0", "port": 8080, "path": "/"},
    ]


def test_add_duplicate_portal(mock_values):
    render = Render(mock_values)
    render.portals.add_portal({"scheme": "http", "path": "/", "port": 8080})
    with pytest.raises(Exception):
        render.portals.add_portal({"scheme": "http", "path": "/", "port": 8080})


def test_add_duplicate_portal_with_explicit_name(mock_values):
    render = Render(mock_values)
    render.portals.add_portal({"name": "Some Portal", "scheme": "http", "path": "/", "port": 8080})
    with pytest.raises(Exception):
        render.portals.add_portal({"name": "Some Portal", "scheme": "http", "path": "/", "port": 8080})


def test_add_portal_with_invalid_scheme(mock_values):
    render = Render(mock_values)
    with pytest.raises(Exception):
        render.portals.add_portal({"scheme": "invalid_scheme", "path": "/", "port": 8080})


def test_add_portal_with_invalid_path(mock_values):
    render = Render(mock_values)
    with pytest.raises(Exception):
        render.portals.add_portal({"scheme": "http", "path": "invalid_path", "port": 8080})


def test_add_portal_with_invalid_path_double_slash(mock_values):
    render = Render(mock_values)
    with pytest.raises(Exception):
        render.portals.add_portal({"scheme": "http", "path": "/some//path", "port": 8080})


def test_add_portal_with_invalid_port(mock_values):
    render = Render(mock_values)
    with pytest.raises(Exception):
        render.portals.add_portal({"scheme": "http", "path": "/", "port": -1})
