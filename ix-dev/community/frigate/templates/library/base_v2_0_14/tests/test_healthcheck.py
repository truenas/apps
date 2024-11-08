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


def test_set_custom_test(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_custom_test("echo $1")
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"] == {
        "test": "echo $$1",
        "interval": "10s",
        "timeout": "5s",
        "retries": 30,
        "start_period": "10s",
    }


def test_set_custom_test_array(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_custom_test(["CMD", "echo", "$1"])
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"] == {
        "test": ["CMD", "echo", "$$1"],
        "interval": "10s",
        "timeout": "5s",
        "retries": 30,
        "start_period": "10s",
    }


def test_set_options(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_custom_test(["CMD", "echo", "$1"])
    c1.healthcheck.set_interval(9)
    c1.healthcheck.set_timeout(8)
    c1.healthcheck.set_retries(7)
    c1.healthcheck.set_start_period(6)
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"] == {
        "test": ["CMD", "echo", "$$1"],
        "interval": "9s",
        "timeout": "8s",
        "retries": 7,
        "start_period": "6s",
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
    assert (
        output["services"]["test_container"]["healthcheck"]["test"]
        == """/bin/bash -c 'exec {hc_fd}<>/dev/tcp/127.0.0.1/8080 && echo -e "GET / HTTP/1.1\\r\\nHost: 127.0.0.1\\r\\nConnection: close\\r\\n\\r\\n" >&$${hc_fd} && cat <&$${hc_fd} | grep -q "200 OK"'"""  # noqa
    )


def test_curl_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("curl", {"port": 8080, "path": "/health"})
    output = render.render()
    assert (
        output["services"]["test_container"]["healthcheck"]["test"]
        == "curl --silent --output /dev/null --show-error --fail http://127.0.0.1:8080/health"
    )


def test_curl_healthcheck_with_headers(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("curl", {"port": 8080, "path": "/health", "headers": [("X-Test", "$test")]})
    output = render.render()
    assert (
        output["services"]["test_container"]["healthcheck"]["test"]
        == 'curl --silent --output /dev/null --show-error --fail --header "X-Test: $$test" http://127.0.0.1:8080/health'
    )


def test_wget_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("wget", {"port": 8080, "path": "/health"})
    output = render.render()
    assert (
        output["services"]["test_container"]["healthcheck"]["test"]
        == "wget --spider --quiet http://127.0.0.1:8080/health"
    )


def test_netcat_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("netcat", {"port": 8080})
    output = render.render()
    assert output["services"]["test_container"]["healthcheck"]["test"] == "nc -z -w 1 127.0.0.1 8080"


def test_tcp_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("tcp", {"port": 8080})
    output = render.render()
    assert (
        output["services"]["test_container"]["healthcheck"]["test"]
        == "timeout 1 bash -c 'cat < /dev/null > /dev/tcp/127.0.0.1/8080'"
    )


def test_redis_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("redis")
    output = render.render()
    assert (
        output["services"]["test_container"]["healthcheck"]["test"]
        == "redis-cli -h 127.0.0.1 -p 6379 -a $$REDIS_PASSWORD ping | grep -q PONG"
    )


def test_postgres_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("postgres")
    output = render.render()
    assert (
        output["services"]["test_container"]["healthcheck"]["test"]
        == "pg_isready -h 127.0.0.1 -p 5432 -U $$POSTGRES_USER -d $$POSTGRES_DB"
    )


def test_mariadb_healthcheck(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.set_test("mariadb")
    output = render.render()
    assert (
        output["services"]["test_container"]["healthcheck"]["test"]
        == "mariadb-admin --user=root --host=127.0.0.1 --port=3306 --password=$$MARIADB_ROOT_PASSWORD ping"
    )
