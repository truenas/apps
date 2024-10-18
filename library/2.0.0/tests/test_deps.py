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


def test_add_postgres_missing_config(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        render.deps.postgres(
            "test_container",
            "test_image",
            {"user": "test_user", "password": "test_password", "database": "test_database"},  # type: ignore
        )


def test_add_postgres(mock_values):
    mock_values["images"]["pg_image"] = {"repository": "postgres", "tag": "latest"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    render.deps.postgres(
        "pg_container",
        "pg_image",
        {
            "user": "test_user",
            "password": "test_password",
            "database": "test_database",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume"}},
        },
    )
    output = render.render()
    assert "devices" not in output["services"]["pg_container"]
    assert "reservations" not in output["services"]["pg_container"]["deploy"]["resources"]
    assert output["services"]["pg_container"]["image"] == "postgres:latest"
    assert output["services"]["pg_container"]["user"] == "999:999"
    assert output["services"]["pg_container"]["deploy"]["resources"]["limits"]["cpus"] == "2.0"
    assert output["services"]["pg_container"]["deploy"]["resources"]["limits"]["memory"] == "4096M"
    assert output["services"]["pg_container"]["healthcheck"] == {
        "test": "pg_isready -h 127.0.0.1 -p 5432 -U $$POSTGRES_USERNAME -d $$POSTGRES_DATABASE",
        "interval": "10s",
        "timeout": "5s",
        "retries": 30,
        "start_period": "10s",
    }
    assert output["services"]["pg_container"]["volumes"] == [
        {
            "type": "volume",
            "source": "test_volume",
            "target": "/var/lib/postgresql/data",
            "read_only": False,
            "volume": {"nocopy": False},
        }
    ]
    assert output["services"]["pg_container"]["environment"] == {
        "TZ": "Etc/UTC",
        "NVIDIA_VISIBLE_DEVICES": "void",
        "POSTGRES_USER": "test_user",
        "POSTGRES_PASSWORD": "test_password",
        "POSTGRES_DB": "test_database",
        "POSTGRES_PORT": "5432",
    }


def test_add_redis_missing_config(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        render.deps.redis(
            "test_container",
            "test_image",
            {"password": "test_password", "volume": {}},  # type: ignore
        )


def test_add_redis(mock_values):
    mock_values["images"]["redis_image"] = {"repository": "redis", "tag": "latest"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    render.deps.redis(
        "redis_container",
        "redis_image",
        {
            "password": "test_password",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume"}},
        },
    )
    output = render.render()
    assert "devices" not in output["services"]["redis_container"]
    assert "reservations" not in output["services"]["redis_container"]["deploy"]["resources"]
    assert output["services"]["redis_container"]["image"] == "redis:latest"
    assert output["services"]["redis_container"]["user"] == "1001:0"
    assert output["services"]["redis_container"]["deploy"]["resources"]["limits"]["cpus"] == "2.0"
    assert output["services"]["redis_container"]["deploy"]["resources"]["limits"]["memory"] == "4096M"
    assert output["services"]["redis_container"]["healthcheck"] == {
        "test": "redis-cli -h 127.0.0.1 -p 6379 -a $$REDIS_PASSWORD ping | grep -q PONG",
        "interval": "10s",
        "timeout": "5s",
        "retries": 30,
        "start_period": "10s",
    }
    assert output["services"]["redis_container"]["volumes"] == [
        {
            "type": "volume",
            "source": "test_volume",
            "target": "/bitnami/redis/data",
            "read_only": False,
            "volume": {"nocopy": False},
        }
    ]
    assert output["services"]["redis_container"]["environment"] == {
        "TZ": "Etc/UTC",
        "NVIDIA_VISIBLE_DEVICES": "void",
        "ALLOW_EMPTY_PASSWORD": "no",
        "REDIS_PASSWORD": "test_password",
        "REDIS_PORT_NUMBER": "6379",
    }


def test_add_mariadb_missing_config(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        render.deps.mariadb(
            "test_container",
            "test_image",
            {"user": "test_user", "password": "test_password", "database": "test_database"},  # type: ignore
        )


def test_add_mariadb(mock_values):
    mock_values["images"]["mariadb_image"] = {"repository": "mariadb", "tag": "latest"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    render.deps.mariadb(
        "mariadb_container",
        "mariadb_image",
        {
            "user": "test_user",
            "password": "test_password",
            "database": "test_database",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume"}},
        },
    )
    output = render.render()
    assert "devices" not in output["services"]["mariadb_container"]
    assert "reservations" not in output["services"]["mariadb_container"]["deploy"]["resources"]
    assert output["services"]["mariadb_container"]["image"] == "mariadb:latest"
    assert output["services"]["mariadb_container"]["user"] == "999:999"
    assert output["services"]["mariadb_container"]["deploy"]["resources"]["limits"]["cpus"] == "2.0"
    assert output["services"]["mariadb_container"]["deploy"]["resources"]["limits"]["memory"] == "4096M"
    assert output["services"]["mariadb_container"]["healthcheck"] == {
        "test": "mariadb-admin --user=root --host=127.0.0.1 --port=3306 --password=$$MARIADB_ROOT_PASSWORD ping",
        "interval": "10s",
        "timeout": "5s",
        "retries": 30,
        "start_period": "10s",
    }
    assert output["services"]["mariadb_container"]["volumes"] == [
        {
            "type": "volume",
            "source": "test_volume",
            "target": "/var/lib/mysql",
            "read_only": False,
            "volume": {"nocopy": False},
        }
    ]
    assert output["services"]["mariadb_container"]["environment"] == {
        "TZ": "Etc/UTC",
        "NVIDIA_VISIBLE_DEVICES": "void",
        "MARIADB_USER": "test_user",
        "MARIADB_PASSWORD": "test_password",
        "MARIADB_ROOT_PASSWORD": "test_password",
        "MARIADB_DATABASE": "test_database",
        "MARIADB_AUTO_UPGRADE": "true",
    }
