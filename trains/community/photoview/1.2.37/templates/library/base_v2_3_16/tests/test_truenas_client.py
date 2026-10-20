import pytest
from unittest.mock import MagicMock

from truenas_client import TNClient, PortCombo, ValidationErrors, RenderError


@pytest.fixture
def mock_render():
    """Create a minimal mock Render instance for testing."""
    render = MagicMock()
    render.values = {
        "ix_context": {
            "app_name": "test-app",
        },
    }
    return render


# Test data: each combo has its own conflict and should_raise flag
tests = [
    {
        "name": "no_conflicts",
        "combo_data": [
            {"combo": PortCombo(bindip="192.168.1.10", port=8080), "conflict": None, "should_raise": False},
            {"combo": PortCombo(bindip="192.168.1.11", port=9090), "conflict": None, "should_raise": False},
        ],
        "should_raise": False,
    },
    {
        "name": "single_combo_no_conflict",
        "combo_data": [
            {"combo": PortCombo(bindip="0.0.0.0", port=3000), "conflict": None, "should_raise": False},
        ],
        "should_raise": False,
    },
    {
        "name": "conflict_with_current_app_only",
        "combo_data": [
            {
                "combo": PortCombo(bindip="192.168.1.10", port=8080),
                "conflict": [
                    "render.test-app.schema",
                    "The port is being used by following services:\n"
                    "1) \"192.168.1.10:8080\" used by Applications ('test-app' application)",
                    22,
                ],
                "should_raise": False,  # Current app is filtered out
            },
        ],
        "should_raise": False,
    },
    {
        "name": "conflict_with_webui",
        "combo_data": [
            {
                "combo": PortCombo(bindip="192.168.1.10", port=8080),
                "conflict": [
                    "render.test-app.schema",
                    "The port is being used by following services:\n"
                    '1) "192.168.1.10:8080" used by WebUI Service',
                    22,
                ],
                "should_raise": True,
            },
        ],
        "should_raise": True,
    },
    {
        "name": "multiple_combos_one_conflicts_with_current_app_one_with_webui",
        "combo_data": [
            {
                "combo": PortCombo(bindip="192.168.1.10", port=8080),
                "conflict": [
                    "render.test-app.schema",
                    "The port is being used by following services:\n"
                    "1) \"192.168.1.10:8080\" used by Applications ('test-app' application)",
                    22,
                ],
                "should_raise": False,  # Current app is filtered out
            },
            {
                "combo": PortCombo(bindip="192.168.1.11", port=9090),
                "conflict": [
                    "render.test-app.schema",
                    "The port is being used by following services:\n"
                    '1) "192.168.1.11:9090" used by WebUI Service',
                    22,
                ],
                "should_raise": True,
            },
        ],
        "should_raise": True,  # One combo has non-current-app conflict
    },
    {
        "name": "conflict_with_other_app",
        "combo_data": [
            {
                "combo": PortCombo(bindip="192.168.1.10", port=8080),
                "conflict": [
                    "render.test-app.schema",
                    "The port is being used by following services:\n"
                    "1) \"192.168.1.10:8080\" used by Applications ('other-app' application)",
                    22,
                ],
                "should_raise": True,
            },
        ],
        "should_raise": True,
    },
    {
        "name": "multiple_combos_with_conflicts",
        "combo_data": [
            {
                "combo": PortCombo(bindip="192.168.1.10", port=8080),
                "conflict": [
                    "render.test-app.schema",
                    "The port is being used by following services:\n"
                    '1) "192.168.1.10:8080" used by WebUI Service',
                    22,
                ],
                "should_raise": True,
            },
            {
                "combo": PortCombo(bindip="192.168.1.11", port=9090),
                "conflict": [
                    "render.test-app.schema",
                    "The port is being used by following services:\n"
                    "1) \"192.168.1.11:9090\" used by Applications ('another-app' application)",
                    22,
                ],
                "should_raise": True,
            },
        ],
        "should_raise": True,
    },
    {
        "name": "ipv6_wildcard_no_conflict",
        "combo_data": [
            {"combo": PortCombo(bindip="::", port=8080), "conflict": None, "should_raise": False},
        ],
        "should_raise": False,
    },
    {
        "name": "mixed_ipv4_ipv6_combos",
        "combo_data": [
            {"combo": PortCombo(bindip="192.168.1.10", port=8080), "conflict": None, "should_raise": False},
            {"combo": PortCombo(bindip="fd00:1234:5678:abcd::10", port=9090), "conflict": None, "should_raise": False},
            {"combo": PortCombo(bindip="0.0.0.0", port=3000), "conflict": None, "should_raise": False},
        ],
        "should_raise": False,
    },
]


@pytest.mark.parametrize("test", tests)
def test_validate_ip_port_combos_with_new_endpoint(mock_render, test):
    """Test validate_ip_port_combos using the new port.validate_ports endpoint.

    When the new endpoint is available, it returns conflicts which are then filtered.
    """
    tn_client = TNClient(mock_render)

    # Collect all conflicts from combo_data
    all_conflicts = [data["conflict"] for data in test["combo_data"] if data["conflict"] is not None]

    # Mock to return the conflicts from the test case
    tn_client.client.call = MagicMock(return_value=all_conflicts)

    combos = [data["combo"] for data in test["combo_data"]]

    if test["should_raise"]:
        with pytest.raises(RenderError):
            tn_client.validate_ip_port_combos(combos)
    else:
        # Should not raise
        tn_client.validate_ip_port_combos(combos)


@pytest.mark.parametrize("test", tests)
def test_validate_ip_port_combos_with_fallback(mock_render, test):
    """Test validate_ip_port_combos using the fallback path (old port.validate_port endpoint).

    When port.validate_ports doesn't exist, fall back to individual port.validate_port calls.
    This path should produce the same results as the new endpoint.
    """
    tn_client = TNClient(mock_render)

    # Mock the client.call to simulate the new endpoint not existing
    def call_side_effect(method, schema, *args):
        if method == "port.validate_ports":
            # Simulate the new endpoint not existing
            raise Exception("Method does not exist")
        elif method == "port.validate_port":
            # args are: (port, ip, None, True)
            port = args[0]
            ip = args[1]

            # Find the combo_data that matches this IP:port
            for data in test["combo_data"]:
                combo = data["combo"]
                if combo.bindip == ip and combo.port == port:
                    # Found the matching combo, check if it should raise
                    if data["should_raise"]:
                        # Raise ValidationErrors for this combo
                        exc = ValidationErrors([data["conflict"]])
                        exc.args = (data["conflict"][1],)
                        raise exc
                    break
        return []

    tn_client.client.call = MagicMock(side_effect=call_side_effect)

    combos = [data["combo"] for data in test["combo_data"]]

    if test["should_raise"]:
        with pytest.raises(RenderError):
            tn_client.validate_ip_port_combos(combos)
    else:
        # Should not raise
        tn_client.validate_ip_port_combos(combos)
