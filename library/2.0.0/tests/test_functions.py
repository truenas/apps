import re
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


def test_funcs(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()

    tests = [
        {"func": "auto_cast", "values": ["1"], "expected": 1},
        {"func": "basic_auth_header", "values": ["my_user", "my_pass"], "expected": "Basic bXlfdXNlcjpteV9wYXNz"},
        {"func": "basic_auth", "values": ["my_user", "my_pass"], "expected": "bXlfdXNlcjpteV9wYXNz"},
        {
            "func": "bcrypt_hash",
            "values": ["my_pass"],
            "expect_regex": r"^\$2b\$12\$[a-zA-Z0-9-_\.\/]+$",
        },
        {"func": "camel_case", "values": ["my_user"], "expected": "My_User"},
        {"func": "copy_dict", "values": [{"a": 1}], "expected": {"a": 1}},
        {"func": "fail", "values": ["my_message"], "expect_raise": True},
        {
            "func": "htpasswd",
            "values": ["my_user", "my_pass"],
            "expect_regex": r"^my_user:\$2b\$12\$[a-zA-Z0-9-_\.\/]+$",
        },
        {"func": "is_boolean", "values": ["true"], "expected": True},
        {"func": "is_boolean", "values": ["false"], "expected": True},
        {"func": "is_number", "values": ["1"], "expected": True},
        {"func": "is_number", "values": ["1.1"], "expected": True},
        {"func": "match_regex", "values": ["value", "^[a-zA-Z0-9]+$"], "expected": True},
        {"func": "match_regex", "values": ["value", "^[0-9]+$"], "expected": False},
        {"func": "merge_dicts", "values": [{"a": 1}, {"b": 2}], "expected": {"a": 1, "b": 2}},
        {"func": "must_match_regex", "values": ["my_user", "^[0-9]$"], "expect_raise": True},
        {"func": "must_match_regex", "values": ["1", "^[0-9]$"], "expected": "1"},
        {"func": "secure_string", "values": [10], "expect_regex": r"^[a-zA-Z0-9-_]+$"},
    ]

    for test in tests:
        print(test["func"], test)
        func = render.funcs[test["func"]]
        if test.get("expect_raise", False):
            with pytest.raises(Exception):
                func(*test["values"])
        elif test.get("expect_regex"):
            r = func(*test["values"])
            assert re.match(test["expect_regex"], r) is not None
        else:
            r = func(*test["values"])
            assert r == test["expected"]
