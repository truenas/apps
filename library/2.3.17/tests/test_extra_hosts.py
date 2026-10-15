import pytest

from base.error import RenderError


def test_add_extra_host(render, c1):
    c1.add_extra_host("test_host", "127.0.0.1")
    c1.add_extra_host("test_host2", "127.0.0.2")
    c1.add_extra_host("host.docker.internal", "host-gateway")
    output = render.render()
    assert output["services"]["test_container"]["extra_hosts"] == {
        "host.docker.internal": "host-gateway",
        "test_host": "127.0.0.1",
        "test_host2": "127.0.0.2",
    }


def test_add_duplicate_extra_host(c1):
    c1.add_extra_host("test_host", "127.0.0.1")
    with pytest.raises(RenderError, match=r"Host \[test_host\] already added with \[127.0.0.1\]"):
        c1.add_extra_host("test_host", "127.0.0.2")


def test_add_extra_host_with_ipv6(render, c1):
    c1.add_extra_host("test_host", "::1")
    output = render.render()
    assert output["services"]["test_container"]["extra_hosts"] == {"test_host": "::1"}


def test_add_extra_host_with_invalid_ip(c1):
    with pytest.raises(RenderError, match=r"Invalid IP address \[invalid_ip\] for host \[test_host\]"):
        c1.add_extra_host("test_host", "invalid_ip")
