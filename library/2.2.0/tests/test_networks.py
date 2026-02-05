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


def test_add_internal_network(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()
    net1 = render.networks.create_internal("test_network1")
    net2 = render.networks.create_internal("test_network2")
    c1.add_network(net1)
    c1.add_network(net2)
    c2.add_network(net1)
    output = render.render()
    assert output["networks"] == {
        "ix-internal-test_network1": {
            "external": False,
            "enable_ipv4": True,
            "enable_ipv6": False,
            "labels": {"ix.internal": "true"},
        },
        "ix-internal-test_network2": {
            "external": False,
            "enable_ipv4": True,
            "enable_ipv6": False,
            "labels": {"ix.internal": "true"},
        },
    }
    assert output["services"]["test_container"]["networks"] == {
        "ix-internal-test_network1": {},
        "ix-internal-test_network2": {},
    }
    assert output["services"]["test_container2"]["networks"] == {
        "ix-internal-test_network1": {},
    }


def test_add_external_network(mock_values):
    render = Render(mock_values)
    # Mock the network names (No Docker client in tests)
    render.docker._network_names = set(["test_network1", "test_network2"])

    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
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


def test_add_both_internal_and_external_network(mock_values):
    render = Render(mock_values)
    # Mock the network names (No Docker client in tests)
    render.docker._network_names = set(["test_network2"])

    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()
    net1 = render.networks.create_internal("test_network1")
    render.networks.register("test_network2")
    c1.add_network(net1)
    c1.add_network("test_network2")
    c2.add_network(net1)
    output = render.render()
    assert output["networks"] == {
        "ix-internal-test_network1": {
            "external": False,
            "enable_ipv4": True,
            "enable_ipv6": False,
            "labels": {"ix.internal": "true"},
        },
        "test_network2": {"external": True},
    }
    assert output["services"]["test_container"]["networks"] == {
        "ix-internal-test_network1": {},
        "test_network2": {},
    }
    assert output["services"]["test_container2"]["networks"] == {
        "ix-internal-test_network1": {},
    }


def test_add_network_with_config(mock_values):
    render = Render(mock_values)
    # Mock the network names (No Docker client in tests)
    render.docker._network_names = set(["test_network1"])
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
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
        "ix-internal-test_network1": {
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


def test_add_network_with_duplicate_interface_name(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    net = render.networks.create_internal("test_network1")
    c1.add_network(net, {"interface_name": "eth0"})
    with pytest.raises(Exception):
        c1.add_network(net, {"interface_name": "eth0"})


def test_add_network_with_duplicate_mac_address(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    net = render.networks.create_internal("test_network1")
    c1.add_network(net, {"mac_address": "00:11:22:33:44:55"})
    with pytest.raises(Exception):
        c1.add_network(net, {"mac_address": "00:11:22:33:44:55"})


def test_add_network_with_duplicate_ipv4_address(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    net = render.networks.create_internal("test_network1")
    c1.add_network(net, {"ipv4_address": "192.168.1.10"})
    with pytest.raises(Exception):
        c1.add_network(net, {"ipv4_address": "192.168.1.10"})


def test_add_network_with_duplicate_ipv6_address(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    net = render.networks.create_internal("test_network1")
    c1.add_network(net, {"ipv6_address": "2001:db8:85a3:8d3:1319:8a2e:370:7348"})
    with pytest.raises(Exception):
        c1.add_network(net, {"ipv6_address": "2001:db8:85a3:8d3:1319:8a2e:370:7348"})


def test_add_network_with_duplicate_gateway_priority(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    net = render.networks.create_internal("test_network1")
    c1.add_network(net, {"gw_priority": 1})
    with pytest.raises(Exception):
        c1.add_network(net, {"gw_priority": 1})


def test_add_network_with_duplicate_priority(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    net = render.networks.create_internal("test_network1")
    c1.add_network(net, {"priority": 1})
    with pytest.raises(Exception):
        c1.add_network(net, {"priority": 1})


def test_add_duplicate_internal_network(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    render.networks.create_internal("test_network1")
    with pytest.raises(Exception):
        render.networks.create_internal("test_network1")


def test_add_duplicate_external_network(mock_values):
    render = Render(mock_values)
    # Mock the network names (No Docker client in tests)
    render.docker._network_names = set(["test_network1"])
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    render.networks.register("test_network1")
    with pytest.raises(Exception):
        render.networks.register("test_network1")


def test_add_duplicate_internal_external_network(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    render.networks.create_internal("test_network1")
    with pytest.raises(Exception):
        render.networks.register("ix-internal-test_network1")
