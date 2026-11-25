import pytest

from base.error import RenderError


def test_device_cgroup_rule(render, c1):
    c1.add_device_cgroup_rule("c 13:* rwm")
    c1.add_device_cgroup_rule("b 10:20 rwm")
    output = render.render()
    assert output["services"]["test_container"]["device_cgroup_rules"] == [
        "b 10:20 rwm",
        "c 13:* rwm",
    ]


@pytest.mark.parametrize(
    "rule",
    [
        pytest.param("c 13:* rwm", id="device_cgroup_rule_duplicate"),
        pytest.param("c 13:* rm", id="device_cgroup_rule_duplicate_group"),
    ],
)
def test_device_cgroup_rule_duplicate(c1, rule):
    c1.add_device_cgroup_rule("c 13:* rwm")
    with pytest.raises(RenderError, match=r"has already been added for this device group"):
        c1.add_device_cgroup_rule(rule)


@pytest.mark.parametrize(
    "rule, match",
    [
        pytest.param(
            "d 10:20 rwm",
            r"Expected type to be one of \[a, b, c\] but got \[d\]",
            id="device_cgroup_rule_invalid_device",
        ),
        pytest.param("a 10:20 rwd", r"Cgroup Permission \[rwd\] is not valid", id="device_cgroup_rule_invalid_perm"),
        pytest.param(
            "a 10 20 rwd",
            r"Expected format is \[<type> <major>:<minor> <permission>\]",
            id="device_cgroup_rule_invalid_format",
        ),
        pytest.param(
            "a 10 rwd",
            r"Expected format is \[<type> <major>:<minor> <permission>\]",
            id="device_cgroup_rule_invalid_format_missing_major",
        ),
        pytest.param(
            "a 10:20:30 rwm",
            r"Expected format is \[<type> <major>:<minor> <permission>\]",
            id="device_cgroup_rule_invalid_format_extra_colon",
        ),
    ],
)
def test_device_cgroup_rule_invalid(c1, rule, match):
    with pytest.raises(RenderError, match=match):
        c1.add_device_cgroup_rule(rule)
