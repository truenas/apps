import pytest

from base.formatter import escape_dollar


@pytest.mark.parametrize(
    "value, expected",
    [
        ("test", "test"),
        ("$test", "$$test"),
        ("$$test", "$$$$test"),
        ("$$$test", "$$$$$$test"),
        ("$test$", "$$test$$"),
    ],
)
def test_escape_dollar(value, expected):
    assert escape_dollar(value) == expected
