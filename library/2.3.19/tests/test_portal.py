import pytest

from base.error import RenderError


def test_no_portals(render, c1):
    output = render.render()
    assert output["x-portals"] == []


def test_add_portal_with_host_ips(render, c1):
    port1 = {"bind_mode": "published", "port_number": 8080, "host_ips": ["1.2.3.4", "5.6.7.8"]}
    port2 = {"bind_mode": "published", "port_number": 8081, "host_ips": ["::", "0.0.0.0"]}
    port3 = {"bind_mode": "published", "port_number": 8081, "host_ips": ["1.2.3.4"]}
    port4 = {"bind_mode": "exposed", "port_number": 1234, "host_ips": ["1.2.3.4"]}
    render.portals.add(port1)
    render.portals.add(port1, {"name": "test1", "host": "my-host.com"})
    render.portals.add(port2, {"name": "test2"})
    render.portals.add(port3, {"name": "test3", "port": None})
    render.portals.add(port3, {"name": "test4", "port": 1234})
    render.portals.add(port4, {"name": "test5", "port": 1234})
    output = render.render()
    assert output["x-portals"] == [
        {"name": "Web UI", "scheme": "http", "host": "1.2.3.4", "port": 8080, "path": "/"},
        {"name": "test1", "scheme": "http", "host": "my-host.com", "port": 8080, "path": "/"},
        {"name": "test2", "scheme": "http", "host": "0.0.0.0", "port": 8081, "path": "/"},
        {"name": "test3", "scheme": "http", "host": "1.2.3.4", "port": 8081, "path": "/"},
        {"name": "test4", "scheme": "http", "host": "1.2.3.4", "port": 1234, "path": "/"},
    ]


def test_add_duplicate_portal(render):
    port = {"bind_mode": "published", "port_number": 8080, "host_ips": ["1.2.3.4", "5.6.7.8"]}
    render.portals.add(port)
    with pytest.raises(RenderError, match=r"Portal \[Web UI\] already added"):
        render.portals.add(port)


def test_add_duplicate_portal_with_explicit_name(render):
    port = {"bind_mode": "published", "port_number": 8080, "host_ips": ["1.2.3.4", "5.6.7.8"]}
    render.portals.add(port, {"name": "Some Portal"})
    with pytest.raises(RenderError, match=r"Portal \[Some Portal\] already added"):
        render.portals.add(port, {"name": "Some Portal"})


@pytest.mark.parametrize(
    "config, match",
    [
        pytest.param(
            {"scheme": "invalid_scheme"},
            r"Portal Scheme \[invalid_scheme\] is not valid",
            id="add_portal_with_invalid_scheme",
        ),
        pytest.param(
            {"path": "invalid_path"},
            r"Path \[invalid_path\] must start with /",
            id="add_portal_with_invalid_path",
        ),
        pytest.param(
            {"path": "/some//path"},
            r"Path \[/some//path\] cannot contain \[//\]",
            id="add_portal_with_invalid_path_double_slash",
        ),
        pytest.param({"port": -1}, r"Invalid port \[-1\]", id="add_portal_with_invalid_port"),
    ],
)
def test_add_portal_with_invalid_config(render, config, match):
    port = {"bind_mode": "published", "port_number": 8080, "host_ips": ["1.2.3.4", "5.6.7.8"]}
    with pytest.raises(RenderError, match=match):
        render.portals.add(port, config)
