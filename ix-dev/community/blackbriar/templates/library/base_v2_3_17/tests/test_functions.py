import re
from collections import Counter

import pytest

from base.error import RenderError


@pytest.fixture
def mock_values():
    return {
        "images": {"test_image": {"repository": "nginx", "tag": "latest"}},
        "ix_volumes": {"test": "/mnt/test123"},
        "resources": {
            "gpus": {
                "use_all_gpus": True,
                "kfd_device_exists": True,
                "nvidia_gpu_selection": {
                    "pci_slot_0": {"uuid": "uuid_0", "use_gpu": True},
                },
            }
        },
    }


def _with_ids(cases):
    """Give each (func, args, expectation) case an id of <func>-<n>, numbered per func."""
    seen = Counter()
    params = []
    for func, args, expectation in cases:
        seen[func] += 1
        params.append(pytest.param(func, args, expectation, id=f"{func}-{seen[func]}"))
    return params


@pytest.mark.parametrize(
    "func, args, expected",
    _with_ids(
        [
            ("auto_cast", ["1"], 1),
            ("auto_cast", ["TrUe"], True),
            ("auto_cast", ["FaLsE"], False),
            ("auto_cast", ["0.2"], 0.2),
            ("auto_cast", [True], True),
            ("basic_auth_header", ["my_user", "my_pass"], "Basic bXlfdXNlcjpteV9wYXNz"),
            ("basic_auth", ["my_user", "my_pass"], "bXlfdXNlcjpteV9wYXNz"),
            ("camel_case", ["my_user"], "My_User"),
            ("copy_dict", [{"a": 1}], {"a": 1}),
            ("is_boolean", ["true"], True),
            ("is_boolean", ["false"], True),
            ("is_number", ["1"], True),
            ("is_number", ["1.1"], True),
            ("match_regex", ["value", "^[a-zA-Z0-9]+$"], True),
            ("match_regex", ["value", "^[0-9]+$"], False),
            ("deep_merge", [{"a": 1, "b": {"b1": 2}}, {"b": {"b2": 3}}], {"a": 1, "b": {"b1": 2, "b2": 3}}),
            ("must_match_regex", ["1", "^[0-9]$"], "1"),
            ("disallow_chars", ["my_user", ["$", "@"], "my_key"], "my_user"),
            ("get_host_path", [{"type": "host_path", "host_path_config": {"path": "/mnt/test"}}], "/mnt/test"),
            ("get_host_path", [{"type": "ix_volume", "ix_volume_config": {"dataset_name": "test"}}], "/mnt/test123"),
            ("or_default", [None, 1], 1),
            ("or_default", [1, None], 1),
            ("or_default", [False, 1], 1),
            ("or_default", [True, 1], True),
            ("temp_config", ["test"], {"type": "temporary", "volume_config": {"volume_name": "test"}}),
            ("require_unique", [["a=1", "b=2", "c"], "values.key", "="], None),
            ("require_no_reserved", [["a=1", "b=2", "c"], "values.key", ["d"], "="], None),
            ("url_encode", ["7V!@@%%63r@a5#e!2X9!68g4b"], "7V%21%40%40%25%2563r%40a5%23e%212X9%2168g4b"),
            (
                "url_to_dict",
                ["192.168.1.1:8080"],
                {"host": "192.168.1.1", "port": 8080, "scheme": "http", "netloc": "192.168.1.1:8080", "path": ""},
            ),
            (
                "url_to_dict",
                ["[::]:8080"],
                {"host": "::", "port": 8080, "scheme": "http", "netloc": "[::]:8080", "path": ""},
            ),
            (
                "url_to_dict",
                ["[::]:8080/abc/", True],
                {
                    "host": "[::]",
                    "port": 8080,
                    "host_no_brackets": "::",
                    "scheme": "http",
                    "netloc": "[::]:8080",
                    "path": "/abc/",
                },
            ),
            ("to_yaml", [{"a": 1, "b": 2}], "a: 1\nb: 2\n"),
            ("has_amd_gpu", [], True),
            ("has_nvidia_gpu", [], True),
            ("has_intel_gpu", [], True),
            ("has_any_gpu", [], True),
        ]
    ),
)
def test_func_returns(render, func, args, expected):
    assert render.funcs[func](*args) == expected


@pytest.mark.parametrize(
    "func, args, regex",
    _with_ids(
        [
            ("bcrypt_hash", ["my_pass"], r"^\$2b\$12\$[a-zA-Z0-9-_\.\/]+$"),
            ("bcrypt_hash", ["a" * 72], r"^\$2b\$12\$[a-zA-Z0-9-_\.\/]+$"),
            ("htpasswd", ["my_user", "my_pass"], r"^my_user:\$2b\$12\$[a-zA-Z0-9-_\.\/]+$"),
            ("htpasswd", ["my_user", "my_pass", 10], r"^my_user:\$2b\$10\$[a-zA-Z0-9-_\.\/]+$"),
            ("secure_string", [10], r"^[a-zA-Z0-9-_]+$"),
        ]
    ),
)
def test_func_matches(render, func, args, regex):
    assert re.match(regex, render.funcs[func](*args)) is not None


@pytest.mark.parametrize(
    "func, args, match",
    _with_ids(
        [
            ("bcrypt_hash", ["a" * 73], r"Expected bcrypt password to be at most 72 bytes\. Got 73 bytes"),
            ("fail", ["my_message"], r"^my_message$"),
            ("htpasswd", ["my_user", "a" * 73], r"Expected bcrypt password to be at most 72 bytes\. Got 73 bytes"),
            ("htpasswd", ["my_user", "my_pass", 32], r"bcrypt rounds must be between 4 and 31"),
            ("must_match_regex", ["my_user", "^[0-9]$"], r"Expected \[my_user\] to match \[\^\[0-9\]\$\]"),
            ("disallow_chars", ["my_user$", ["$", "@"], "my_key"], r"Disallowed character \[\$\] in \[my_key\]"),
            ("temp_config", [""], r"Expected \[name\] to be set when calling \[temp_config\]"),
            (
                "require_unique",
                [["a=1", "b=2", "b=3"], "values.key", "="],
                r"Expected values in \[values\.key\] to be unique",
            ),
            (
                "require_no_reserved",
                [["a=1", "b=2", "c"], "values.key", ["a"], "="],
                r"Value \[a\] is reserved and cannot be set in \[values\.key\]",
            ),
            (
                "require_no_reserved",
                [["a=1", "b=2", "c"], "values.key", ["b"], "=", True],
                r"Value \[b\] is reserved and cannot be set in \[values\.key\]",
            ),
        ]
    ),
)
def test_func_raises(render, func, args, match):
    with pytest.raises(RenderError, match=match):
        render.funcs[func](*args)
