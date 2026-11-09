import pytest

from base.error import RenderError
from base.render import Render


def test_add_expose_ports(render, c1):
    c1.expose.add_port(8081)
    c1.expose.add_port(8081, "udp")
    c1.expose.add_port(8082, "udp")
    output = render.render()
    assert output["services"]["test_container"]["expose"] == ["8081/tcp", "8081/udp", "8082/udp"]


def test_add_duplicate_expose_ports(c1):
    c1.expose.add_port(8081)
    with pytest.raises(RenderError, match=r"Exposed port \[8081/tcp\] already added"):
        c1.expose.add_port(8081)


def test_add_expose_ports_with_host_network(mock_values):
    mock_values["network"] = {"host_network": True}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.expose.add_port(8081)
    output = render.render()
    assert "expose" not in output["services"]["test_container"]
