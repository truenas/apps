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


def test_add_ports(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.ports.add_port(8081, 8080)
    c1.ports.add_port(8082, 8080, {"protocol": "udp"})
    output = render.render()
    assert output["services"]["test_container"]["ports"] == [
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress"},
        {"published": 8082, "target": 8080, "protocol": "udp", "mode": "ingress"},
    ]


def test_add_duplicate_ports(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.ports.add_port(8081, 8080)
    c1.ports.add_port(8081, 8080, {"protocol": "udp"})  # This should not raise
    with pytest.raises(Exception):
        c1.ports.add_port(8081, 8080)


def test_add_duplicate_ports_with_different_family(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.ports.add_port(8081, 8080, {"host_ip": "192.168.1.10"})
    c1.ports.add_port(8081, 8080, {"host_ip": "::"})
    output = render.render()
    assert output["services"]["test_container"]["ports"] == [
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "192.168.1.10"},
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "::"},
    ]


def test_add_duplicate_ports_to_specific_v6_host_ip_binds_to_0_0_0_0(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.ports.add_port(8081, 8080, {"host_ip": "0.0.0.0"})
    c1.ports.add_port(8081, 8080, {"host_ip": "::1"})
    output = render.render()
    assert output["services"]["test_container"]["ports"] == [
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "0.0.0.0"},
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "::1"},
    ]


def test_add_duplicate_ports_to_both_wildcard_host_ip(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.ports.add_port(8081, 8080, {"host_ip": "::"})
    c1.ports.add_port(8081, 8080, {"host_ip": "0.0.0.0"})
    output = render.render()
    assert output["services"]["test_container"]["ports"] == [
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress"},
    ]


def test_add_duplicate_ports_to_multiple_v4_and_v6_host_ip(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.ports.add_port(8081, 8080, {"host_ip": "192.168.1.10"})
    c1.ports.add_port(8081, 8080, {"host_ip": "192.168.1.11"})
    c1.ports.add_port(8081, 8080, {"host_ip": "::1"})
    c1.ports.add_port(8081, 8080, {"host_ip": "::2"})
    output = render.render()
    assert output["services"]["test_container"]["ports"] == [
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "192.168.1.10"},
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "192.168.1.11"},
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "::1"},
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "::2"},
    ]


def test_add_duplicate_port_to_specific_host_ip_binds_to_v6_wildcard(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.ports.add_port(8081, 8080, {"host_ip": "::"})
    with pytest.raises(Exception):
        c1.ports.add_port(8081, 8080, {"host_ip": "::1"})


def test_add_duplicate_ports_with_different_host_ip(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.ports.add_port(8081, 8080, {"host_ip": "192.168.1.10"})
    c1.ports.add_port(8081, 8080, {"host_ip": "192.168.1.11"})
    output = render.render()
    assert output["services"]["test_container"]["ports"] == [
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "192.168.1.10"},
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "192.168.1.11"},
    ]


def test_add_duplicate_ports_to_specific_host_ip_binds_to_0_0_0_0(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.ports.add_port(8081, 8080, {"host_ip": "192.168.1.10"})
    with pytest.raises(Exception):
        c1.ports.add_port(8081, 8080, {"host_ip": "0.0.0.0"})


def test_add_duplicate_ports_to_0_0_0_0_binds_to_specific_host_ip(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.ports.add_port(8081, 8080, {"host_ip": "0.0.0.0"})
    with pytest.raises(Exception):
        c1.ports.add_port(8081, 8080, {"host_ip": "192.168.1.10"})


def test_add_ports_with_invalid_protocol(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        c1.ports.add_port(8081, 8080, {"protocol": "invalid_protocol"})


def test_add_ports_with_invalid_mode(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        c1.ports.add_port(8081, 8080, {"mode": "invalid_mode"})


def test_add_ports_with_invalid_ip(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        c1.ports.add_port(8081, 8080, {"host_ip": "invalid_ip"})


def test_add_ports_with_invalid_host_port(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        c1.ports.add_port(-1, 8080)


def test_add_ports_with_invalid_container_port(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        c1.ports.add_port(8081, -1)
