import pytest

from base.error import RenderError


@pytest.fixture
def mock_values():
    return {
        "ix_context": {
            "app_name": "My Other App",
            "app_metadata": {
                "title": "App Title",
            },
        },
        "images": {
            "test_image": {
                "repository": "nginx",
                "tag": "latest",
            }
        },
    }


def test_add_internal_network(render, c1):
    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()
    net1 = render.networks.create_internal("test_network1")
    net2 = render.networks.create_internal("test_network2")
    c1.add_network(net1)
    c1.add_network(net2)
    c2.add_network(net1)
    output = render.render()
    assert output["networks"] == {
        "ix-internal-my-other-app-test_network1": {
            "name": "ix-internal-my-other-app-test_network1",
            "external": False,
            # "enable_ipv4": True,
            "enable_ipv6": False,
            "labels": {"tn.network.internal": "true"},
        },
        "ix-internal-my-other-app-test_network2": {
            "name": "ix-internal-my-other-app-test_network2",
            "external": False,
            # "enable_ipv4": True,
            "enable_ipv6": False,
            "labels": {"tn.network.internal": "true"},
        },
    }
    assert output["services"]["test_container"]["networks"] == {
        "ix-internal-my-other-app-test_network1": {},
        "ix-internal-my-other-app-test_network2": {},
    }
    assert output["services"]["test_container2"]["networks"] == {
        "ix-internal-my-other-app-test_network1": {},
    }


def test_add_external_network(render, c1):
    # Mock the network names (No Docker client in tests)
    render.docker._network_names = set(["test_network1", "test_network2"])

    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()
    render.networks.register("test_network1")
    render.networks.register("test_network2")
    c1.add_network("test_network1")
    c1.add_network("test_network2")
    c2.add_network("test_network1")
    output = render.render()
    assert output["networks"] == {
        "test_network1": {"external": True},
        "test_network2": {"external": True},
    }
    assert output["services"]["test_container"]["networks"] == {
        "test_network1": {},
        "test_network2": {},
    }
    assert output["services"]["test_container2"]["networks"] == {
        "test_network1": {},
    }


def test_add_both_internal_and_external_network(render, c1):
    # Mock the network names (No Docker client in tests)
    render.docker._network_names = set(["test_network2"])

    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()
    net1 = render.networks.create_internal("test_network1")
    render.networks.register("test_network2")
    c1.add_network(net1)
    c1.add_network("test_network2")
    c2.add_network(net1)
    output = render.render()
    assert output["networks"] == {
        "ix-internal-my-other-app-test_network1": {
            "name": "ix-internal-my-other-app-test_network1",
            "external": False,
            # "enable_ipv4": True,
            "enable_ipv6": False,
            "labels": {"tn.network.internal": "true"},
        },
        "test_network2": {"external": True},
    }
    assert output["services"]["test_container"]["networks"] == {
        "ix-internal-my-other-app-test_network1": {},
        "test_network2": {},
    }
    assert output["services"]["test_container2"]["networks"] == {
        "ix-internal-my-other-app-test_network1": {},
    }


def test_add_network_with_config(render, c1):
    # Mock the network names (No Docker client in tests)
    render.docker._network_names = set(["test_network1"])
    net = render.networks.create_internal("test_network1")
    c1.add_network(
        net,
        {
            "interface_name": "eth0",
            "ipv4_address": "192.168.1.10",
            "mac_address": "00:11:22:33:44:55",
            "gw_priority": 1,
            "priority": 2,
        },
    )

    render.networks.register("test_network1")
    c1.add_network(
        "test_network1",
        {
            "interface_name": "eth1",
            "ipv4_address": "192.168.1.11",
            "mac_address": "00:11:22:33:44:56",
            "gw_priority": 3,
            "priority": 4,
        },
    )

    output = render.render()
    assert output["services"]["test_container"]["networks"] == {
        "ix-internal-my-other-app-test_network1": {
            "interface_name": "eth0",
            "ipv4_address": "192.168.1.10",
            "mac_address": "00:11:22:33:44:55",
            "gw_priority": 1,
            "priority": 2,
        },
        "test_network1": {
            "interface_name": "eth1",
            "ipv4_address": "192.168.1.11",
            "mac_address": "00:11:22:33:44:56",
            "gw_priority": 3,
            "priority": 4,
        },
    }


def test_auto_add_networks(render, c1):
    render.docker._network_names = set(["test_network1", "test_network2"])
    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()

    net = render.networks.create_internal("test_network1")
    c1.add_network(net)
    c2.add_network(net)

    # Hack around the fact that docker client is not available in tests
    new_net = render.values.get("network", {})
    new_net["networks"] = [
        {
            "name": "test_network1",
            "containers": [
                {"name": "test_container", "config": {"interface_name": "eth0"}},
                {"name": "test_container2", "config": {"interface_name": "eth0"}},
            ],
        },
        {
            "name": "test_network2",
            "containers": [
                {"name": "test_container", "config": {"interface_name": "eth1", "aliases": ["alias1"]}},
            ],
        },
    ]
    render.values["network"] = new_net
    render._original_values["network"] = new_net

    render._auto_add_networks()
    for container in render._containers.values():
        container._auto_add_networks()
    # End hack

    output = render.render()
    assert output["networks"] == {
        "ix-internal-my-other-app-test_network1": {
            "name": "ix-internal-my-other-app-test_network1",
            "external": False,
            # "enable_ipv4": True,
            "enable_ipv6": False,
            "labels": {"tn.network.internal": "true"},
        },
        "test_network2": {"external": True},
        "test_network1": {"external": True},
    }
    assert output["services"]["test_container"]["networks"] == {
        "ix-internal-my-other-app-test_network1": {},
        "test_network2": {
            "interface_name": "eth1",
            "aliases": ["alias1"],
        },
        "test_network1": {
            "interface_name": "eth0",
        },
    }
    assert output["services"]["test_container2"]["networks"] == {
        "ix-internal-my-other-app-test_network1": {},
        "test_network1": {
            "interface_name": "eth0",
        },
    }


# Two different networks on the same container, sharing one config value
@pytest.mark.parametrize(
    "config, match",
    [
        pytest.param(
            {"interface_name": "eth0"},
            r"cannot have the same interface name \[eth0\]",
            id="add_network_with_duplicate_interface_name",
        ),
        pytest.param(
            {"mac_address": "00:11:22:33:44:55"},
            r"cannot have the same MAC address \[00:11:22:33:44:55\]",
            id="add_network_with_duplicate_mac_address",
        ),
        pytest.param(
            {"ipv4_address": "192.168.1.10"},
            r"cannot have the same IPv4 address \[192\.168\.1\.10\]",
            id="add_network_with_duplicate_ipv4_address",
        ),
        pytest.param(
            {"ipv6_address": "2001:db8:85a3:8d3:1319:8a2e:370:7348"},
            r"cannot have the same IPv6 address \[2001:db8:85a3:8d3:1319:8a2e:370:7348\]",
            id="add_network_with_duplicate_ipv6_address",
        ),
        pytest.param(
            {"gw_priority": 1},
            r"cannot have the same gateway priority \[1\]",
            id="add_network_with_duplicate_gateway_priority",
        ),
        pytest.param(
            {"priority": 1}, r"cannot have the same priority \[1\]", id="add_network_with_duplicate_priority"
        ),
    ],
)
def test_add_network_with_duplicate(render, c1, config, match):
    net1 = render.networks.create_internal("test_network1")
    net2 = render.networks.create_internal("test_network2")
    c1.add_network(net1, config)
    with pytest.raises(RenderError, match=match):
        c1.add_network(net2, config)


def test_add_duplicate_internal_network(render, c1):
    render.networks.create_internal("test_network1")
    with pytest.raises(RenderError, match=r"Network \[ix-internal-my-other-app-test_network1\] already exists"):
        render.networks.create_internal("test_network1")


def test_add_duplicate_external_network(render, c1):
    # Mock the network names (No Docker client in tests)
    render.docker._network_names = set(["test_network1"])
    render.networks.register("test_network1")
    with pytest.raises(RenderError, match=r"Network \[test_network1\] already exists"):
        render.networks.register("test_network1")


def test_add_duplicate_internal_external_network(render, c1):
    # Mock the network names (No Docker client in tests), so the register gets past the docker check
    render.docker._network_names = set(["ix-internal-my-other-app-test_network1"])
    render.networks.create_internal("test_network1")
    with pytest.raises(RenderError, match=r"Network \[ix-internal-my-other-app-test_network1\] already exists"):
        render.networks.register("ix-internal-my-other-app-test_network1")


def test_add_network_with_duplicate_aliases(render, c1):
    # Mock the network names (No Docker client in tests)
    render.docker._network_names = set(["test_network1", "test_network2"])
    render.networks.register("test_network1")
    render.networks.register("test_network2")
    c1.add_network("test_network1", {"aliases": ["alias1", "alias2"]})
    with pytest.raises(
        RenderError,
        match=r"Network \[test_network2\] cannot have the same aliases \[alias2\] as network \[test_network1\]",
    ):
        c1.add_network("test_network2", {"aliases": ["alias2", "alias3"]})
