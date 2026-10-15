import pytest

from base.error import RenderError
from base.render import Render


@pytest.mark.parametrize(
    "network, key, expected",
    [
        pytest.param(
            {"dns_opts": ["attempts:3", "opt1", "opt2"]},
            "dns_opt",
            ["attempts:3", "opt1", "opt2"],
            id="auto_add_dns_opts",
        ),
        pytest.param(
            {"dns_searches": ["search1", "search2"]},
            "dns_search",
            ["search1", "search2"],
            id="auto_add_dns_searches",
        ),
        pytest.param(
            {"dns_nameservers": ["nameserver1", "nameserver2"]},
            "dns",
            ["nameserver1", "nameserver2"],
            id="auto_add_dns_nameservers",
        ),
    ],
)
def test_auto_add_dns(mock_values, network, key, expected):
    mock_values["network"] = network
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    output = render.render()
    assert output["services"]["test_container"][key] == expected


@pytest.mark.parametrize(
    "network, match",
    [
        pytest.param(
            {"dns_nameservers": ["nameserver1", "nameserver1"]},
            r"DNS Nameserver \[nameserver1\] already added",
            id="add_duplicate_dns_nameservers",
        ),
        pytest.param(
            {"dns_searches": ["search1", "search1"]},
            r"DNS Search \[search1\] already added",
            id="add_duplicate_dns_searches",
        ),
        pytest.param(
            {"dns_opts": ["attempts:3", "attempts:5"]},
            r"DNS Option \[attempts\] already added",
            id="add_duplicate_dns_opts",
        ),
    ],
)
def test_add_duplicate_dns(mock_values, network, match):
    mock_values["network"] = network
    render = Render(mock_values)
    with pytest.raises(RenderError, match=match):
        render.add_container("test_container", "test_image")
