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


def test_add_portal_with_host_ips(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    port = {"port_number": 8080, "host_ips": ["1.2.3.4", "5.6.7.8"]}
    port2 = {"port_number": 8081, "host_ips": ["::", "0.0.0.0"]}
    port3 = {"port_number": 8081, "host_ips": ["1.2.3.4"]}
    render.portals.add(port)
    render.portals.add(port, {"name": "test", "host": "my-host.com"})
    render.portals.add(port2, {"name": "test2"})
    render.portals.add(port3, {"name": "test3"})
    output = render.render()
    assert output["x-portals"] == [
        {"name": "Web UI", "scheme": "http", "host": "1.2.3.4", "port": 8080, "path": "/"},
        {"name": "test", "scheme": "http", "host": "my-host.com", "port": 8080, "path": "/"},
        {"name": "test2", "scheme": "http", "host": "0.0.0.0", "port": 8081, "path": "/"},
        {"name": "test3", "scheme": "http", "host": "1.2.3.4", "port": 8081, "path": "/"},
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
