import pytest

from base.error import RenderError


def test_add_sysctl(render, c1):
    c1.sysctls.add("net.ipv4.ip_forward", 1)
    c1.sysctls.add("fs.mqueue.msg_max", 100)
    output = render.render()
    assert output["services"]["test_container"]["sysctls"] == {"net.ipv4.ip_forward": "1", "fs.mqueue.msg_max": "100"}


def test_add_net_sysctl_with_host_network(render, c1):
    c1.set_network_mode("host")
    c1.sysctls.add("net.ipv4.ip_forward", 1)
    with pytest.raises(
        RenderError, match=r"Sysctl \[net.ipv4.ip_forward\] cannot start with \[net.\] when host network is enabled"
    ):
        render.render()


def test_add_duplicate_sysctl(c1):
    c1.sysctls.add("net.ipv4.ip_forward", 1)
    with pytest.raises(RenderError, match=r"Sysctl \[net.ipv4.ip_forward\] already added"):
        c1.sysctls.add("net.ipv4.ip_forward", 0)


def test_add_empty_sysctl(c1):
    with pytest.raises(RenderError, match=r"Sysctls key cannot be empty"):
        c1.sysctls.add("", 1)


def test_add_sysctl_with_invalid_key(render, c1):
    c1.sysctls.add("invalid.sysctl", 1)
    with pytest.raises(RenderError, match=r"Sysctl \[invalid.sysctl\] is not valid"):
        render.render()
