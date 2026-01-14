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


def test_disable_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"] == {"disable": True}


def test_use_built_in_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.use_built_in()
    output = render.render()
    assert "healthcheck" not in output["services"]["test_container"]


def test_set_custom_test(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
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


def test_set_custom_test_array(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
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


def test_CMD_with_var_should_fail(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.healthcheck.set_custom_test(["CMD", "echo", "$1"])


def test_set_options(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
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


def test_adding_test_when_disabled(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        c1.healthcheck.set_custom_test("echo $1")


def test_not_adding_test(mock_values):
    render = Render(mock_values)
    render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        render.render()


def test_invalid_path(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.healthcheck.set_test("http", {"port": 8080, "path": "invalid"})


def test_http_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("http", {"port": 8080})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
        "CMD-SHELL",
        f"""/bin/bash -c '{{ printf "GET / HTTP/1.1\\r\\nHost: 127.0.0.1\\r\\nConnection: close\\r\\n\\r\\n" >&0; grep "HTTP" | grep -q "200"; }} 0<>/dev/tcp/127.0.0.1/8080'""",  # noqa
    ]


def test_curl_healthcheck_as_CMD(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("curl", {"port": 8080, "path": "/health", "data": {"test": "val"}, "exec_type": "CMD"})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
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
    ]


def test_curl_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("curl", {"port": 8080, "path": "/health", "data": {"test": "val"}})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
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
    ]


def test_curl_healthcheck_with_headers_and_method_and_data(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test(
        "curl", {"port": 8080, "path": "/health", "method": "POST", "headers": [("X-Test", "some-value")], "data": {}}
    )
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
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
    ]


def test_wget_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("wget", {"port": 8080, "path": "/health"})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
        "CMD",
        "wget",
        "--quiet",
        "--spider",
        "http://127.0.0.1:8080/health",
    ]


def test_wget_healthcheck_no_spider(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("wget", {"port": 8080, "path": "/health", "spider": False})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
        "CMD",
        "wget",
        "--quiet",
        "-O",
        "/dev/null",
        "http://127.0.0.1:8080/health",
    ]


def test_wget_healthcheck_data(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test(
        "wget", {"port": 8080, "path": "/health", "spider": False, "data": {"test": "val"}, "method": "POST"}
    )
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
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
    ]


def test_wget_healthcheck_data_busybox(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test(
        "wget", {"port": 8080, "path": "/health", "spider": False, "data": {"test": "val"}, "busybox": True}
    )
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
        "CMD",
        "wget",
        "--quiet",
        "-O",
        "/dev/null",
        "--post-data",
        '{"test": "val"}',
        "http://127.0.0.1:8080/health",
    ]


def test_netcat_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("netcat", {"port": 8080})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
        "CMD",
        "nc",
        "-z",
        "-w",
        "1",
        "127.0.0.1",
        "8080",
    ]


def test_netcat_udp_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("netcat", {"port": 8080, "udp": True})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
        "CMD",
        "nc",
        "-z",
        "-w",
        "1",
        "-u",
        "127.0.0.1",
        "8080",
    ]


def test_tcp_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("tcp", {"port": 8080})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
        "CMD",
        "timeout",
        "1",
        "bash",
        "-c",
        "cat < /dev/null > /dev/tcp/127.0.0.1/8080",
    ]


def test_redis_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("redis", {"password": "test"})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
        "CMD",
        "redis-cli",
        "-h",
        "127.0.0.1",
        "-p",
        "6379",
        "-a",
        "test",
        "ping",
    ]


def test_redis_healthcheck_no_password(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("redis", {"password": ""})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
        "CMD",
        "redis-cli",
        "-h",
        "127.0.0.1",
        "-p",
        "6379",
        "ping",
    ]


def test_postgres_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("postgres", {"user": "test-user", "db": "test-db"})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
        "CMD",
        "pg_isready",
        "-h",
        "127.0.0.1",
        "-p",
        "5432",
        "-U",
        "test-user",
        "-d",
        "test-db",
    ]


def test_mariadb_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("mariadb", {"password": "test-pass"})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
        "CMD",
        "mariadb-admin",
        "--user=root",
        "--host=127.0.0.1",
        "--port=3306",
        "--password=test-pass",
        "ping",
    ]


def test_mongodb_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("mongodb", {"db": "test-db"})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == [
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
    ]
