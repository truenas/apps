import pytest


from base.error import RenderError


tests = [
    {
        "name": "add_ports_should_work",
        "inputs": [
            {
                "values": ({"bind_mode": "published", "port_number": 8081}, {"container_port": 8080}),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8082},
                    {"container_port": 8080, "protocol": "udp"},
                ),
                "expect_error": False,
            },
        ],
        "expected": [
            {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress"},
            {"published": 8082, "target": 8080, "protocol": "udp", "mode": "ingress"},
        ],
    },
    {
        "name": "add_duplicate_ports_should_fail",
        "inputs": [
            {
                "values": ({"bind_mode": "published", "port_number": 8081}, {"container_port": 8080}),
                "expect_error": False,
            },
            {
                "values": ({"bind_mode": "published", "port_number": 8081}, {"container_port": 8080}),
                "expect_error": r"Port \[8081/tcp/ipv4\] already added for \[0\.0\.0\.0\]",
            },
        ],
    },
    {
        "name": "adding_duplicate_port_different_protocol_should_work",
        "inputs": [
            {
                "values": ({"bind_mode": "published", "port_number": 8081}, {"container_port": 8080}),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "protocol": "udp"},
                ),
                "expect_error": False,
            },
        ],
        "expected": [
            {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress"},
            {"published": 8081, "target": 8080, "protocol": "udp", "mode": "ingress"},
        ],
    },
    {
        "name": "adding_same_port_for_both_wildcard_families_should_work",
        "inputs": [
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["0.0.0.0"]},
                ),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["::"]},
                ),
                "expect_error": False,
            },
        ],
        "expected": [
            {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress"},
        ],
    },
    {
        "name": "adding_duplicate_port_for_v4_ip_and_v4_wildcard_should_fail",
        "inputs": [
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["192.168.1.10"]},
                ),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["0.0.0.0"]},
                ),
                "expect_error": (
                    r"Cannot bind port \[8081/tcp/ipv4\] to \[0\.0\.0\.0\], already bound to \[192\.168\.1\.10\]"
                ),
            },
        ],
    },
    {
        "name": "adding_duplicate_port_for_v4_wildcard_and_v4_ip_should_fail",
        "inputs": [
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["0.0.0.0"]},
                ),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["192.168.1.10"]},
                ),
                "expect_error": (
                    r"Cannot bind port \[8081/tcp/ipv4\] to \[192\.168\.1\.10\], already bound to \[0\.0\.0\.0\]"
                ),
            },
        ],
    },
    {
        "name": "adding_duplicate_port_for_v4_wildcard_and_v6_ip_should_work",
        "inputs": [
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["192.168.1.10"]},
                ),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["fd00:1234:5678:abcd::10"]},
                ),
                "expect_error": False,
            },
        ],
        "expected": [
            {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "192.168.1.10"},
            {
                "published": 8081,
                "target": 8080,
                "protocol": "tcp",
                "mode": "ingress",
                "host_ip": "fd00:1234:5678:abcd::10",
            },
        ],
    },
    {
        "name": "adding_duplicate_port_for_v6_wildcard_and_v4_ip_should_work",
        "inputs": [
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["::"]},
                ),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["192.168.1.10"]},
                ),
                "expect_error": False,
            },
        ],
        "expected": [
            {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "192.168.1.10"},
            {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "::"},
        ],
    },
    {
        "name": "adding_duplicate_port_for_v6_wildcard_and_v6_ip_should_fail",
        "inputs": [
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["::"]},
                ),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["fd00:1234:5678:abcd::10"]},
                ),
                "expect_error": (
                    r"Cannot bind port \[8081/tcp/ipv6\] to \[fd00:1234:5678:abcd::10\], already bound to \[::\]"
                ),
            },
        ],
    },
    {
        "name": "adding_duplicate_port_for_v6_ip_and_v6_wildcard_should_fail",
        "inputs": [
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["fd00:1234:5678:abcd::10"]},
                ),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["::"]},
                ),
                "expect_error": (
                    r"Cannot bind port \[8081/tcp/ipv6\] to \[::\], already bound to \[fd00:1234:5678:abcd::10\]"
                ),
            },
        ],
    },
    {
        "name": "adding_duplicate_port_with_different_v4_ip_should_work",
        "inputs": [
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["192.168.1.10"]},
                ),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["192.168.1.11"]},
                ),
                "expect_error": False,
            },
        ],
        "expected": [
            {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "192.168.1.10"},
            {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "192.168.1.11"},
        ],
    },
    {
        "name": "adding_port_with_invalid_protocol_should_fail",
        "inputs": [
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "protocol": "invalid_protocol"},
                ),
                "expect_error": r"Port Protocol \[invalid_protocol\] is not valid",
            },
        ],
    },
    {
        "name": "adding_port_with_invalid_mode_should_fail",
        "inputs": [
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "mode": "invalid_mode"},
                ),
                "expect_error": r"Port Mode \[invalid_mode\] is not valid",
            },
        ],
    },
    {
        "name": "adding_port_with_invalid_ip_should_fail",
        "inputs": [
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["invalid_ip"]},
                ),
                "expect_error": r"Invalid IP address \[invalid_ip\]",
            },
        ],
    },
    {
        "name": "adding_port_with_invalid_port_number_should_fail",
        "inputs": [
            {
                "values": ({"bind_mode": "published", "port_number": -1}, {"container_port": 8080}),
                "expect_error": r"Invalid port \[-1\]\. Valid ports are between 1 and 65535",
            },
        ],
    },
    {
        "name": "adding_port_with_invalid_container_port_should_fail",
        "inputs": [
            {
                "values": ({"bind_mode": "published", "port_number": 8081}, {"container_port": -1}),
                "expect_error": r"Invalid port \[-1\]\. Valid ports are between 1 and 65535",
            },
        ],
    },
    {
        "name": "adding_duplicate_ports_with_different_host_ip_should_work",
        "inputs": [
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["192.168.1.10"]},
                ),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["192.168.1.10"], "protocol": "udp"},
                ),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["192.168.1.11"]},
                ),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["192.168.1.11"], "protocol": "udp"},
                ),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["fd00:1234:5678:abcd::10"]},
                ),
                "expect_error": False,
            },
            {
                "values": (
                    {"bind_mode": "published", "port_number": 8081},
                    {"container_port": 8080, "host_ips": ["fd00:1234:5678:abcd::11"]},
                ),
                "expect_error": False,
            },
        ],
        # fmt: off
        "expected": [
            {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "192.168.1.10"},
            {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "192.168.1.11"},
            {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "fd00:1234:5678:abcd::10"}, # noqa
            {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress", "host_ip": "fd00:1234:5678:abcd::11"}, # noqa
            {"published": 8081, "target": 8080, "protocol": "udp", "mode": "ingress", "host_ip": "192.168.1.10"},
            {"published": 8081, "target": 8080, "protocol": "udp", "mode": "ingress", "host_ip": "192.168.1.11"},
        ],
        # fmt: on
    },
]


# expect_error is either False or the regex the raised RenderError has to match
@pytest.mark.parametrize("test", tests, ids=[t["name"] for t in tests])
def test_ports(test, render, c1):
    for input in test["inputs"]:
        if input["expect_error"]:
            with pytest.raises(RenderError, match=input["expect_error"]):
                c1.add_port(*input["values"])
        else:
            c1.add_port(*input["values"])

    if any(i["expect_error"] for i in test["inputs"]):
        return

    output = render.render()
    assert output["services"]["test_container"]["ports"] == test["expected"]
