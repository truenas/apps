import pytest

from base.error import RenderError


# The conftest c1 has its healthcheck disabled, the tests here need to set it themselves
@pytest.fixture
def c1(render):
    return render.add_container("test_container", "test_image")


def test_disable_healthcheck(render, c1):
    c1.healthcheck.disable()
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"] == {"disable": True}


def test_use_built_in_healthcheck(render, c1):
    c1.healthcheck.use_built_in()
    output = render.render()
    assert "healthcheck" not in output["services"]["test_container"]


def test_set_custom_test(render, c1):
    c1.healthcheck.set_custom_test("echo $1")
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"] == {
        "test": "echo $$1",
        "interval": "30s",
        "timeout": "5s",
        "retries": 5,
        "start_period": "15s",
        "start_interval": "2s",
    }


def test_set_custom_test_array(render, c1):
    c1.healthcheck.set_custom_test(["CMD", "echo", "1"])
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"] == {
        "test": ["CMD", "echo", "1"],
        "interval": "30s",
        "timeout": "5s",
        "retries": 5,
        "start_period": "15s",
        "start_interval": "2s",
    }


def test_CMD_with_var_should_fail(c1):
    with pytest.raises(RenderError, match=r"Healthcheck with 'CMD' cannot contain shell variables"):
        c1.healthcheck.set_custom_test(["CMD", "echo", "$1"])


def test_set_options(render, c1):
    c1.healthcheck.set_custom_test(["CMD", "echo", "123$567"])
    c1.healthcheck.set_interval(9)
    c1.healthcheck.set_timeout(8)
    c1.healthcheck.set_retries(7)
    c1.healthcheck.set_start_period(6)
    c1.healthcheck.set_start_interval(5)
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"] == {
        "test": ["CMD", "echo", "123$$567"],
        "interval": "9s",
        "timeout": "8s",
        "retries": 7,
        "start_period": "6s",
        "start_interval": "5s",
    }


def test_adding_test_when_disabled(c1):
    c1.healthcheck.disable()
    with pytest.raises(RenderError, match=r"Cannot set custom test when healthcheck is disabled"):
        c1.healthcheck.set_custom_test("echo $1")


def test_not_adding_test(render, c1):
    with pytest.raises(RenderError, match=r"Healthcheck test is not set"):
        render.render()


@pytest.mark.parametrize(
    "test_type, config, expected",
    [
        pytest.param(
            "http",
            {"port": 8080},
            [
                "CMD-SHELL",
                f"""/bin/bash -c '{{ printf "GET / HTTP/1.1\\r\\nHost: 127.0.0.1\\r\\nConnection: close\\r\\n\\r\\n" >&0; grep "HTTP" | grep -q "200"; }} 0<>/dev/tcp/127.0.0.1/8080'""",  # noqa
            ],
            id="http_healthcheck",
        ),
        pytest.param(
            "curl",
            {"port": 8080, "path": "/health", "data": {"test": "val"}, "exec_type": "CMD"},
            [
                "CMD",
                "curl",
                "--request",
                "GET",
                "--silent",
                "--output",
                "/dev/null",
                "--show-error",
                "--fail",
                "--data",
                '{"test": "val"}',
                "http://127.0.0.1:8080/health",
            ],
            id="curl_healthcheck_as_CMD",
        ),
        pytest.param(
            "curl",
            {"port": 8080, "path": "/health", "data": {"test": "val"}},
            [
                "CMD",
                "curl",
                "--request",
                "GET",
                "--silent",
                "--output",
                "/dev/null",
                "--show-error",
                "--fail",
                "--data",
                '{"test": "val"}',
                "http://127.0.0.1:8080/health",
            ],
            id="curl_healthcheck",
        ),
        pytest.param(
            "curl",
            {"port": 8080, "path": "/health", "method": "POST", "headers": [("X-Test", "some-value")], "data": {}},
            [
                "CMD",
                "curl",
                "--request",
                "POST",
                "--silent",
                "--output",
                "/dev/null",
                "--show-error",
                "--fail",
                "--header",
                "X-Test: some-value",
                "--data",
                "{}",
                "http://127.0.0.1:8080/health",
            ],
            id="curl_healthcheck_with_headers_and_method_and_data",
        ),
        pytest.param(
            "wget",
            {"port": 8080, "path": "/health"},
            ["CMD", "wget", "--quiet", "--spider", "http://127.0.0.1:8080/health"],
            id="wget_healthcheck",
        ),
        pytest.param(
            "wget",
            {"port": 8080, "path": "/health", "spider": False},
            ["CMD", "wget", "--quiet", "-O", "/dev/null", "http://127.0.0.1:8080/health"],
            id="wget_healthcheck_no_spider",
        ),
        pytest.param(
            "wget",
            {"port": 8080, "path": "/health", "spider": False, "data": {"test": "val"}, "method": "POST"},
            [
                "CMD",
                "wget",
                "--quiet",
                "--method",
                "POST",
                "-O",
                "/dev/null",
                "--body-data",
                '{"test": "val"}',
                "http://127.0.0.1:8080/health",
            ],
            id="wget_healthcheck_data",
        ),
        pytest.param(
            "wget",
            {"port": 8080, "path": "/health", "spider": False, "data": {"test": "val"}, "busybox": True},
            [
                "CMD",
                "wget",
                "--quiet",
                "-O",
                "/dev/null",
                "--post-data",
                '{"test": "val"}',
                "http://127.0.0.1:8080/health",
            ],
            id="wget_healthcheck_data_busybox",
        ),
        pytest.param(
            "netcat",
            {"port": 8080},
            ["CMD", "nc", "-z", "-w", "1", "127.0.0.1", "8080"],
            id="netcat_healthcheck",
        ),
        pytest.param(
            "netcat",
            {"port": 8080, "udp": True},
            ["CMD", "nc", "-z", "-w", "1", "-u", "127.0.0.1", "8080"],
            id="netcat_udp_healthcheck",
        ),
        pytest.param(
            "tcp",
            {"port": 8080},
            ["CMD", "timeout", "1", "bash", "-c", "cat < /dev/null > /dev/tcp/127.0.0.1/8080"],
            id="tcp_healthcheck",
        ),
        pytest.param(
            "redis",
            {"port": 6380},
            ["CMD", "redis-cli", "-h", "127.0.0.1", "-p", "6380", "ping"],
            id="redis_healthcheck",
        ),
        pytest.param(
            "postgres",
            {"user": "test-user", "db": "test-db"},
            ["CMD", "pg_isready", "-h", "127.0.0.1", "-p", "5432", "-U", "test-user", "-d", "test-db"],
            id="postgres_healthcheck",
        ),
        pytest.param(
            "mariadb",
            {"password": "test-pass"},
            ["CMD", "mariadb-admin", "--user=root", "--host=127.0.0.1", "--port=3306", "--password=test-pass", "ping"],
            id="mariadb_healthcheck",
        ),
        pytest.param(
            "mongodb",
            {"db": "test-db"},
            [
                "CMD",
                "mongosh",
                "--host",
                "127.0.0.1",
                "--port",
                "27017",
                "test-db",
                "--eval",
                'db.adminCommand("ping")',
                "--quiet",
            ],
            id="mongodb_healthcheck",
        ),
        pytest.param(
            "pidof",
            {"process": "some-process"},
            ["CMD", "pidof", "-s", "some-process"],
            id="pidof",
        ),
        pytest.param(
            "pgrep",
            {"process": "some-process"},
            ["CMD", "pgrep", "-f", "some-process"],
            id="pgrep",
        ),
        pytest.param(
            "node",
            {"port": 8080},
            [
                "CMD",
                "node",
                "-e",
                'require(\'http\').get({"host": "127.0.0.1", "port": 8080, "path": "/"}, '
                "r => process.exit(r.statusCode === 200 ? 0 : 1))"
                ".on('error', () => process.exit(1));",
            ],
            id="node_healthcheck",
        ),
        pytest.param(
            "node",
            {"port": 8443, "path": "/health", "scheme": "https"},
            [
                "CMD",
                "node",
                "-e",
                'require(\'https\').get({"host": "127.0.0.1", "port": 8443, "path": "/health", "rejectUnauthorized": false}, '  # noqa
                "r => process.exit(r.statusCode === 200 ? 0 : 1))"
                ".on('error', () => process.exit(1));",
            ],
            id="node_healthcheck_https",
        ),
        pytest.param(
            "node",
            {"port": 3000, "path": "/status", "host": "0.0.0.0", "binary": "/usr/local/bin/node"},
            [
                "CMD",
                "/usr/local/bin/node",
                "-e",
                'require(\'http\').get({"host": "0.0.0.0", "port": 3000, "path": "/status"}, '
                "r => process.exit(r.statusCode === 200 ? 0 : 1))"
                ".on('error', () => process.exit(1));",
            ],
            id="node_healthcheck_custom_binary_and_host",
        ),
        pytest.param(
            "node_tcp",
            {"port": 8080},
            [
                "CMD",
                "node",
                "-e",
                (
                    "require('net').connect(8080, \"127.0.0.1\", () => process.exit(0))"
                    ".on('error', () => process.exit(1));"
                ),
            ],
            id="node_tcp_healthcheck",
        ),
        pytest.param(
            "node_tcp",
            {"port": 3000, "host": "0.0.0.0", "binary": "/usr/local/bin/node"},
            [
                "CMD",
                "/usr/local/bin/node",
                "-e",
                "require('net').connect(3000, \"0.0.0.0\", () => process.exit(0)).on('error', () => process.exit(1));",
            ],
            id="node_tcp_healthcheck_custom_binary_and_host",
        ),
    ],
)
def test_set_test(render, c1, test_type, config, expected):
    c1.healthcheck.set_test(test_type, config)
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == expected


def test_postgres_healthcheck_custom_binary(render, c1):
    c1.healthcheck.set_test(
        "postgres",
        {"user": "test-user", "db": "test-db", "binary": "/usr/lib/postgresql/17/bin/pg_isready"},
    )
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"][1] == "/usr/lib/postgresql/17/bin/pg_isready"


@pytest.mark.parametrize(
    "test_type, config, match",
    [
        pytest.param(
            "http",
            {"port": 8080, "path": "invalid"},
            r"Path \[invalid\] must start with /",
            id="invalid_path",
        ),
        pytest.param("node", {}, r"Expected \[port\] to be set", id="node_healthcheck_missing_port"),
        pytest.param(
            "node",
            {"port": 8080, "scheme": "ftp"},
            r"Healthcheck Scheme \[ftp\] is not valid",
            id="node_healthcheck_invalid_scheme",
        ),
        pytest.param(
            "node",
            {"port": 8080, "path": "no-leading-slash"},
            r"Path \[no-leading-slash\] must start with /",
            id="node_healthcheck_invalid_path",
        ),
        pytest.param("node_tcp", {}, r"Expected \[port\] to be set", id="node_tcp_healthcheck_missing_port"),
    ],
)
def test_set_test_invalid(c1, test_type, config, match):
    with pytest.raises(RenderError, match=match):
        c1.healthcheck.set_test(test_type, config)
