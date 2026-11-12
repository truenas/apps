import pytest

from base.error import RenderError


def test_invalid_restart_policy(c1):
    with pytest.raises(RenderError, match=r"Restart policy \[invalid_policy\] is not valid"):
        c1.restart.set_policy("invalid_policy")


@pytest.mark.parametrize(
    "args, expected",
    [
        pytest.param(("on-failure",), "on-failure", id="valid_restart_policy"),
        pytest.param(("on-failure", 10), "on-failure:10", id="valid_restart_policy_with_maximum_retry_count"),
    ],
)
def test_valid_restart_policy(render, c1, args, expected):
    c1.restart.set_policy(*args)
    output = render.render()
    assert output["services"]["test_container"]["restart"] == expected


@pytest.mark.parametrize(
    "policy, maximum_retry_count, match",
    [
        pytest.param(
            "on-failure",
            -1,
            r"Maximum retry count must be a positive integer",
            id="invalid_restart_policy_with_maximum_retry_count",
        ),
        pytest.param(
            "always",
            10,
            r"Maximum retry count can only be set for \[on-failure\] restart policy",
            id="invalid_restart_policy_with_maximum_retry_count_and_policy",
        ),
    ],
)
def test_invalid_restart_policy_with_maximum_retry_count(c1, policy, maximum_retry_count, match):
    with pytest.raises(RenderError, match=match):
        c1.restart.set_policy(policy, maximum_retry_count=maximum_retry_count)
