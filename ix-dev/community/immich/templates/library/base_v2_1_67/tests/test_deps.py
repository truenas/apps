import json
import pytest

from render import Render


@pytest.fixture
def mock_values():
    return {
        "images": {
            "test_image": {
                "repository": "nginx",
                "tag": "latest",
            },
            "container_utils_image": {
                "repository": "ixsystems/container-utils",
                "tag": "1.0.0",
            },
            "postgres_upgrade_image": {
                "repository": "ixsystems/postgres-upgrade",
                "tag": "1.0.0",
            },
        },
    }


def test_add_postgres_missing_config(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        render.deps.postgres(
            "pg_container",
            "test_image",
            {"user": "test_user", "password": "test_password", "database": "test_database"},  # type: ignore
        )


def test_add_postgres_unsupported_repo(mock_values):
    mock_values["images"]["pg_image"] = {"repository": "unsupported_repo", "tag": "16.6-bookworm"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    with pytest.raises(Exception):
        render.deps.postgres(
            "pg_container",
            "pg_image",
            {
                "user": "test_user",
                "password": "test_@password",
                "database": "test_database",
                "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
            },
            perms_container,
        )


def test_add_postgres(mock_values):
    mock_values["images"]["pg_image"] = {"repository": "postgres", "tag": "16.6-bookworm"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    p = render.deps.postgres(
        "pg_container",
        "pg_image",
        {
            "user": "test_user",
            "password": "test_@password",
            "database": "test_database",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
        },
        perms_container,
    )
    if perms_container.has_actions():
        perms_container.activate()
        p.container.depends.add_dependency("perms_container", "service_completed_successfully")
    output = render.render()
    assert (
        p.get_url("postgres") == "postgres://test_user:test_%40password@pg_container:5432/test_database?sslmode=disable"
    )
    assert "devices" not in output["services"]["pg_container"]
    assert "reservations" not in output["services"]["pg_container"]["deploy"]["resources"]
    assert output["services"]["pg_container"]["image"] == "postgres:16.6-bookworm"
    assert output["services"]["pg_container"]["user"] == "999:999"
    assert output["services"]["pg_container"]["deploy"]["resources"]["limits"]["cpus"] == "2.0"
    assert output["services"]["pg_container"]["deploy"]["resources"]["limits"]["memory"] == "4096M"
    assert output["services"]["pg_container"]["healthcheck"] == {
        "test": [
            "CMD",
            "pg_isready",
            "-h",
            "127.0.0.1",
            "-p",
            "5432",
            "-U",
            "test_user",
            "-d",
            "test_database",
        ],
        "interval": "30s",
        "timeout": "5s",
        "retries": 5,
        "start_period": "15s",
        "start_interval": "2s",
    }
    assert output["services"]["pg_container"]["volumes"] == [
        {
            "type": "volume",
            "source": "test_volume",
            "target": "/var/lib/postgresql",
            "read_only": False,
            "volume": {"nocopy": False},
        }
    ]
    assert output["services"]["pg_container"]["environment"] == {
        "TZ": "Etc/UTC",
        "UMASK": "002",
        "UMASK_SET": "002",
        "NVIDIA_VISIBLE_DEVICES": "void",
        "POSTGRES_USER": "test_user",
        "POSTGRES_PASSWORD": "test_@password",
        "POSTGRES_DB": "test_database",
        "PGPORT": "5432",
        "PGDATA": "/var/lib/postgresql/16/docker",
    }
    assert output["services"]["pg_container"]["depends_on"] == {
        "perms_container": {"condition": "service_completed_successfully"},
        "pg_container_upgrade": {"condition": "service_completed_successfully"},
    }
    assert output["services"]["perms_container"]["restart"] == "on-failure:1"


def test_add_postgres_options(mock_values):
    mock_values["images"]["pg_image"] = {"repository": "postgres", "tag": "16.6-bookworm"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    render.deps.postgres(
        "pg_container",
        "pg_image",
        {
            "user": "test_user",
            "password": "test_@password",
            "database": "test_database",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
            "additional_options": {"maintenance_work_mem": "1024MB", "max_connections": "100"},
        },
        perms_container,
    )

    output = render.render()
    assert output["services"]["pg_container"]["command"] == [
        "-c",
        "maintenance_work_mem=1024MB",
        "-c",
        "max_connections=100",
    ]


def test_add_redis_missing_config(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        render.deps.redis(
            "redis_container",
            "test_image",
            {"password": "test_password", "volume": {}},  # type: ignore
        )


def test_add_redis_unsupported_repo(mock_values):
    mock_values["images"]["redis_image"] = {"repository": "unsupported_repo", "tag": "latest"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    with pytest.raises(Exception):
        render.deps.redis(
            "redis_container",
            "redis_image",
            {
                "password": "test&password@",
                "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
            },
            perms_container,
        )


def test_add_redis_with_password_with_spaces(mock_values):
    mock_values["images"]["redis_image"] = {"repository": "redis", "tag": "latest"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        render.deps.redis(
            "redis_container",
            "redis_image",
            {"password": "test password", "volume": {}},  # type: ignore
        )


def test_add_redis(mock_values):
    mock_values["images"]["redis_image"] = {"repository": "valkey/valkey", "tag": "latest"}
    mock_values["run_as"] = {"user": 0, "group": 0}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    r = render.deps.redis(
        "redis_container",
        "redis_image",
        {
            "password": "test&password@",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
        },
        perms_container,
    )
    c1.environment.add_env("REDIS_URL", r.get_url("redis"))
    if perms_container.has_actions():
        perms_container.activate()
        r.container.depends.add_dependency("perms_container", "service_completed_successfully")
    output = render.render()
    assert "devices" not in output["services"]["redis_container"]
    assert "reservations" not in output["services"]["redis_container"]["deploy"]["resources"]
    assert (
        output["services"]["test_container"]["environment"]["REDIS_URL"]
        == "redis://default:test%26password%40@redis_container:6379"
    )
    assert output["services"]["redis_container"]["image"] == "valkey/valkey:latest"
    assert output["services"]["redis_container"]["user"] == "568:568"
    assert output["services"]["redis_container"]["deploy"]["resources"]["limits"]["cpus"] == "2.0"
    assert output["services"]["redis_container"]["deploy"]["resources"]["limits"]["memory"] == "4096M"
    assert output["services"]["redis_container"]["healthcheck"] == {
        "test": [
            "CMD",
            "redis-cli",
            "-h",
            "127.0.0.1",
            "-p",
            "6379",
            "-a",
            "test&password@",
            "ping",
        ],
        "interval": "30s",
        "timeout": "5s",
        "retries": 5,
        "start_period": "15s",
        "start_interval": "2s",
    }
    assert output["services"]["redis_container"]["volumes"] == [
        {
            "type": "volume",
            "source": "test_volume",
            "target": "/data",
            "read_only": False,
            "volume": {"nocopy": False},
        }
    ]
    assert output["services"]["redis_container"]["environment"] == {
        "TZ": "Etc/UTC",
        "UMASK": "002",
        "UMASK_SET": "002",
        "NVIDIA_VISIBLE_DEVICES": "void",
        "REDIS_PASSWORD": "test&password@",
    }
    assert output["services"]["redis_container"]["depends_on"] == {
        "perms_container": {"condition": "service_completed_successfully"}
    }


def test_add_mariadb_missing_config(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        render.deps.mariadb(
            "mariadb_container",
            "test_image",
            {"user": "test_user", "password": "test_password", "database": "test_database"},  # type: ignore
        )


def test_add_mariadb_unsupported_repo(mock_values):
    mock_values["images"]["mariadb_image"] = {"repository": "unsupported_repo", "tag": "latest"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    with pytest.raises(Exception):
        render.deps.mariadb(
            "mariadb_container",
            "mariadb_image",
            {
                "user": "test_user",
                "password": "test_password",
                "database": "test_database",
                "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
            },
            perms_container,
        )


def test_add_mariadb(mock_values):
    mock_values["images"]["mariadb_image"] = {"repository": "mariadb", "tag": "latest"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    m = render.deps.mariadb(
        "mariadb_container",
        "mariadb_image",
        {
            "user": "test_user",
            "password": "test_password",
            "database": "test_database",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
        },
        perms_container,
    )
    if perms_container.has_actions():
        perms_container.activate()
        m.container.depends.add_dependency("perms_container", "service_completed_successfully")
    output = render.render()
    assert "devices" not in output["services"]["mariadb_container"]
    assert "reservations" not in output["services"]["mariadb_container"]["deploy"]["resources"]
    assert output["services"]["mariadb_container"]["image"] == "mariadb:latest"
    assert output["services"]["mariadb_container"]["user"] == "999:999"
    assert output["services"]["mariadb_container"]["deploy"]["resources"]["limits"]["cpus"] == "2.0"
    assert output["services"]["mariadb_container"]["deploy"]["resources"]["limits"]["memory"] == "4096M"
    assert output["services"]["mariadb_container"]["healthcheck"] == {
        "test": [
            "CMD",
            "mariadb-admin",
            "--user=root",
            "--host=127.0.0.1",
            "--port=3306",
            "--password=test_password",
            "ping",
        ],
        "interval": "30s",
        "timeout": "5s",
        "retries": 5,
        "start_period": "15s",
        "start_interval": "2s",
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
        "UMASK": "002",
        "UMASK_SET": "002",
        "NVIDIA_VISIBLE_DEVICES": "void",
        "MARIADB_USER": "test_user",
        "MARIADB_PASSWORD": "test_password",
        "MARIADB_ROOT_PASSWORD": "test_password",
        "MARIADB_DATABASE": "test_database",
        "MARIADB_AUTO_UPGRADE": "true",
    }
    assert output["services"]["mariadb_container"]["depends_on"] == {
        "perms_container": {"condition": "service_completed_successfully"}
    }


def test_add_perms_container(mock_values):
    mock_values["ix_volumes"] = {
        "test_dataset1": "/mnt/test/1",
        "test_dataset2": "/mnt/test/2",
        "test_dataset3": "/mnt/test/3",
    }
    mock_values["images"]["postgres_image"] = {"repository": "postgres", "tag": "17.7-bookworm"}
    mock_values["images"]["redis_image"] = {"repository": "valkey/valkey", "tag": "latest"}
    mock_values["images"]["mariadb_image"] = {"repository": "mariadb", "tag": "latest"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()

    # fmt: off
    volume_perms = {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}}
    volume_no_perms = {"type": "volume", "volume_config": {"volume_name": "test_volume"}}
    host_path_perms = {"type": "host_path", "host_path_config": {"path": "/mnt/test", "auto_permissions": True}}
    host_path_no_perms = {"type": "host_path", "host_path_config": {"path": "/mnt/test"}}
    host_path_acl_perms = {"type": "host_path", "host_path_config": {"acl": {"path": "/mnt/test"}, "acl_enable": True, "auto_permissions": True}} # noqa
    ix_volume_no_perms = {"type": "ix_volume", "ix_volume_config": {"dataset_name": "test_dataset1"}}
    ix_volume_perms = {"type": "ix_volume", "ix_volume_config": {"dataset_name": "test_dataset2", "auto_permissions": True}} # noqa
    ix_volume_acl_perms = {"type": "ix_volume", "ix_volume_config": {"dataset_name": "test_dataset3", "acl_enable": True, "auto_permissions": True}} # noqa
    temp_volume = {"type": "temporary", "volume_config": {"volume_name": "test_temp_volume"}}
    read_only_volume = {"type": "volume", "read_only": True, "volume_config": {"volume_name": "test_read_only_volume", "auto_permissions": True}} # noqa
    # fmt: on

    c1.add_storage("/some/path1", volume_perms)
    c1.add_storage("/some/path2", volume_no_perms)
    c1.add_storage("/some/path3", host_path_perms)
    c1.add_storage("/some/path4", host_path_no_perms)
    c1.add_storage("/some/path5", host_path_acl_perms)
    c1.add_storage("/some/path6", ix_volume_no_perms)
    c1.add_storage("/some/path7", ix_volume_perms)
    c1.add_storage("/some/path8", ix_volume_acl_perms)
    c1.add_storage("/some/path9", temp_volume)
    c1.add_storage("/some/path10", read_only_volume)

    perms_container = render.deps.perms("test_perms_container")
    perms_container.add_or_skip_action("data", volume_perms, {"uid": 1000, "gid": 1000, "mode": "check"})
    perms_container.add_or_skip_action("data2", volume_no_perms, {"uid": 1000, "gid": 1000, "mode": "check"})
    perms_container.add_or_skip_action("data3", host_path_perms, {"uid": 1000, "gid": 1000, "mode": "check"})
    perms_container.add_or_skip_action("data4", host_path_no_perms, {"uid": 1000, "gid": 1000, "mode": "check"})
    perms_container.add_or_skip_action("data5", host_path_acl_perms, {"uid": 1000, "gid": 1000, "mode": "check"})
    perms_container.add_or_skip_action("data6", ix_volume_no_perms, {"uid": 1000, "gid": 1000, "mode": "check"})
    perms_container.add_or_skip_action("data7", ix_volume_perms, {"uid": 1000, "gid": 1000, "mode": "check"})
    perms_container.add_or_skip_action("data8", ix_volume_acl_perms, {"uid": 1000, "gid": 1000, "mode": "check"})
    perms_container.add_or_skip_action("data9", temp_volume, {"uid": 1000, "gid": 1000, "mode": "check"})
    perms_container.add_or_skip_action("data10", read_only_volume, {"uid": 1000, "gid": 1000, "mode": "check"})
    postgres = render.deps.postgres(
        "postgres_container",
        "postgres_image",
        {
            "user": "test_user",
            "password": "test_password",
            "database": "test_database",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
        },
        perms_container,
    )
    redis = render.deps.redis(
        "redis_container",
        "redis_image",
        {
            "password": "test_password",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
        },
        perms_container,
    )
    mariadb = render.deps.mariadb(
        "mariadb_container",
        "mariadb_image",
        {
            "user": "test_user",
            "password": "test_password",
            "database": "test_database",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
        },
        perms_container,
    )

    if perms_container.has_actions():
        perms_container.activate()
        c1.depends.add_dependency("test_perms_container", "service_completed_successfully")
        postgres.container.depends.add_dependency("test_perms_container", "service_completed_successfully")
        redis.container.depends.add_dependency("test_perms_container", "service_completed_successfully")
        mariadb.container.depends.add_dependency("test_perms_container", "service_completed_successfully")
    output = render.render()
    assert output["services"]["test_perms_container"]["network_mode"] == "none"
    assert output["services"]["test_container"]["depends_on"] == {
        "test_perms_container": {"condition": "service_completed_successfully"}
    }
    # fmt: off
    content = [
        {"read_only": False, "mount_path": "/mnt/permission/data", "is_temporary": False, "identifier": "data", "recursive": False, "mode": "check", "uid": 1000, "gid": 1000, "chmod": None}, # noqa
        {"read_only": False, "mount_path": "/mnt/permission/data3", "is_temporary": False, "identifier": "data3", "recursive": False, "mode": "check", "uid": 1000, "gid": 1000, "chmod": None}, # noqa
        {"read_only": False, "mount_path": "/mnt/permission/data6", "is_temporary": False, "identifier": "data6", "recursive": False, "mode": "check", "uid": 1000, "gid": 1000, "chmod": None}, # noqa
        {"read_only": False, "mount_path": "/mnt/permission/data7", "is_temporary": False, "identifier": "data7", "recursive": False, "mode": "check", "uid": 1000, "gid": 1000, "chmod": None}, # noqa
        {"read_only": False, "mount_path": "/mnt/permission/data9", "is_temporary": True, "identifier": "data9", "recursive": True, "mode": "check", "uid": 1000, "gid": 1000, "chmod": None}, # noqa
        {"read_only": True, "mount_path": "/mnt/permission/data10", "is_temporary": False, "identifier": "data10", "recursive": False, "mode": "check", "uid": 1000, "gid": 1000, "chmod": None}, # noqa
        {"read_only": False, "mount_path": "/mnt/permission/postgres_container_postgres_data", "is_temporary": False, "identifier": "postgres_container_postgres_data", "recursive": False, "mode": "check", "uid": 999, "gid": 999, "chmod": None}, # noqa
        {"read_only": False, "mount_path": "/mnt/permission/redis_container_redis_data", "is_temporary": False, "identifier": "redis_container_redis_data", "recursive": False, "mode": "check", "uid": 568, "gid": 568, "chmod": None}, # noqa
        {"read_only": False, "mount_path": "/mnt/permission/mariadb_container_mariadb_data", "is_temporary": False, "identifier": "mariadb_container_mariadb_data", "recursive": False, "mode": "check", "uid": 999, "gid": 999, "chmod": None}, # noqa
    ]
    # fmt: on
    assert output["configs"]["permissions_actions_data"]["content"] == json.dumps(content)
    assert output["services"]["test_perms_container"]["entrypoint"] == ["python3", "/script/permissions.py"]


def test_add_duplicate_perms_action(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    vol_config = {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}}
    c1.add_storage("/some/path", vol_config)
    perms_container = render.deps.perms("test_perms_container")
    perms_container.add_or_skip_action("data", vol_config, {"uid": 1000, "gid": 1000, "mode": "check"})
    with pytest.raises(Exception):
        perms_container.add_or_skip_action("data", vol_config, {"uid": 1000, "gid": 1000, "mode": "check"})


def test_add_perm_action_without_auto_perms_enabled(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    vol_config = {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": False}}
    c1.add_storage("/some/path", vol_config)
    perms_container = render.deps.perms("test_perms_container")
    perms_container.add_or_skip_action("data", vol_config, {"uid": 1000, "gid": 1000, "mode": "check"})
    if perms_container.has_actions():
        perms_container.activate()
        c1.depends.add_dependency("test_perms_container", "service_completed_successfully")
    output = render.render()
    assert "configs" not in output
    assert "ix-test_perms_container" not in output["services"]
    assert "depends_on" not in output["services"]["test_container"]


def test_add_unsupported_postgres_version(mock_values):
    mock_values["images"]["pg_image"] = {"repository": "postgres", "tag": "99"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        render.deps.postgres(
            "test_container",
            "test_image",
            {"user": "test_user", "password": "test_password", "database": "test_database"},  # type: ignore
        )


def test_add_postgres_with_invalid_tag(mock_values):
    mock_values["images"]["pg_image"] = {"repository": "postgres", "tag": "latest"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        render.deps.postgres(
            "pg_container",
            "pg_image",
            {"user": "test_user", "password": "test_password", "database": "test_database"},  # type: ignore
        )


def test_postgres_with_upgrade_container(mock_values):
    mock_values["images"]["pg_image"] = {"repository": "postgres", "tag": "16.6-bookworm"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("test_perms_container")
    pg = render.deps.postgres(
        "postgres_container",
        "pg_image",
        {
            "user": "test_user",
            "password": "test_password",
            "database": "test_database",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
        },
        perms_container,
    )
    if perms_container.has_actions():
        perms_container.activate()
        pg.add_dependency("test_perms_container", "service_completed_successfully")
    output = render.render()
    pg = output["services"]["postgres_container"]
    pgup = output["services"]["postgres_container_upgrade"]
    assert pg["volumes"] == pgup["volumes"]
    assert pg["user"] == pgup["user"]
    assert pgup["environment"]["TARGET_VERSION"] == "16"
    assert pgup["environment"]["PGDATA"] == "/var/lib/postgresql/16/docker"
    pgup_env = pgup["environment"]
    pgup_env.pop("TARGET_VERSION")
    assert pg["environment"] == pgup_env
    assert pg["depends_on"] == {
        "test_perms_container": {"condition": "service_completed_successfully"},
        "postgres_container_upgrade": {"condition": "service_completed_successfully"},
    }
    assert pgup["depends_on"] == {"test_perms_container": {"condition": "service_completed_successfully"}}
    assert pgup["restart"] == "on-failure:1"
    assert pgup["healthcheck"] == {"disable": True}
    assert pgup["image"] == "ixsystems/postgres-upgrade:1.0.0"
    assert pgup["entrypoint"] == ["/bin/bash", "-c", "/upgrade.sh"]


def test_add_mongodb(mock_values):
    mock_values["images"]["mongodb_image"] = {"repository": "mongo", "tag": "latest"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    m = render.deps.mongodb(
        "mongodb_container",
        "mongodb_image",
        {
            "user": "test_user",
            "password": "test_password",
            "database": "test_database",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
        },
        perms_container,
    )
    if perms_container.has_actions():
        perms_container.activate()
        m.container.depends.add_dependency("perms_container", "service_completed_successfully")
    output = render.render()
    assert "devices" not in output["services"]["mongodb_container"]
    assert "reservations" not in output["services"]["mongodb_container"]["deploy"]["resources"]
    assert output["services"]["mongodb_container"]["image"] == "mongo:latest"
    assert output["services"]["mongodb_container"]["user"] == "568:568"
    assert output["services"]["mongodb_container"]["deploy"]["resources"]["limits"]["cpus"] == "2.0"
    assert output["services"]["mongodb_container"]["deploy"]["resources"]["limits"]["memory"] == "4096M"
    assert output["services"]["mongodb_container"]["healthcheck"] == {
        "test": [
            "CMD",
            "mongosh",
            "--host",
            "127.0.0.1",
            "--port",
            "27017",
            "test_database",
            "--eval",
            'db.adminCommand("ping")',
            "--quiet",
        ],
        "interval": "30s",
        "timeout": "5s",
        "retries": 5,
        "start_period": "15s",
        "start_interval": "2s",
    }
    assert output["services"]["mongodb_container"]["volumes"] == [
        {
            "type": "volume",
            "source": "test_volume",
            "target": "/data/db",
            "read_only": False,
            "volume": {"nocopy": False},
        }
    ]
    assert output["services"]["mongodb_container"]["environment"] == {
        "TZ": "Etc/UTC",
        "UMASK": "002",
        "UMASK_SET": "002",
        "NVIDIA_VISIBLE_DEVICES": "void",
        "MONGO_INITDB_ROOT_USERNAME": "test_user",
        "MONGO_INITDB_ROOT_PASSWORD": "test_password",
        "MONGO_INITDB_DATABASE": "test_database",
    }
    assert output["services"]["mongodb_container"]["depends_on"] == {
        "perms_container": {"condition": "service_completed_successfully"}
    }


def test_add_mongodb_unsupported_repo(mock_values):
    mock_values["images"]["mongo_image"] = {"repository": "unsupported_repo", "tag": "7"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    with pytest.raises(Exception):
        render.deps.mongodb(
            "mongo_container",
            "mongo_image",
            {
                "user": "test_user",
                "password": "test_@password",
                "database": "test_database",
                "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
            },
            perms_container,
        )


def test_add_meilisearch(mock_values):
    mock_values["images"]["meili_image"] = {"repository": "getmeili/meilisearch", "tag": "v1.17.0"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    m = render.deps.meilisearch(
        "meili_container",
        "meili_image",
        {
            "master_key": "test_master_key",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
        },
        perms_container,
    )
    if perms_container.has_actions():
        perms_container.activate()
        m.container.depends.add_dependency("perms_container", "service_completed_successfully")
    output = render.render()
    assert "devices" not in output["services"]["meili_container"]
    assert "reservations" not in output["services"]["meili_container"]["deploy"]["resources"]
    assert output["services"]["meili_container"]["image"] == "getmeili/meilisearch:v1.17.0"
    assert output["services"]["meili_container"]["user"] == "568:568"
    assert output["services"]["meili_container"]["deploy"]["resources"]["limits"]["cpus"] == "2.0"
    assert output["services"]["meili_container"]["deploy"]["resources"]["limits"]["memory"] == "4096M"
    assert output["services"]["meili_container"]["healthcheck"] == {
        "test": [
            "CMD",
            "curl",
            "--request",
            "GET",
            "--silent",
            "--output",
            "/dev/null",
            "--show-error",
            "--fail",
            "http://127.0.0.1:7700/health",
        ],
        "interval": "30s",
        "timeout": "5s",
        "retries": 5,
        "start_period": "15s",
        "start_interval": "2s",
    }
    assert output["services"]["meili_container"]["volumes"] == [
        {
            "type": "volume",
            "source": "test_volume",
            "target": "/meili_data",
            "read_only": False,
            "volume": {"nocopy": False},
        }
    ]
    assert output["services"]["meili_container"]["environment"] == {
        "TZ": "Etc/UTC",
        "UMASK": "002",
        "UMASK_SET": "002",
        "NVIDIA_VISIBLE_DEVICES": "void",
        "MEILI_MASTER_KEY": "test_master_key",
        "MEILI_HTTP_ADDR": "0.0.0.0:7700",
        "MEILI_NO_ANALYTICS": "true",
        "MEILI_EXPERIMENTAL_DUMPLESS_UPGRADE": "true",
    }
    assert output["services"]["meili_container"]["depends_on"] == {
        "perms_container": {"condition": "service_completed_successfully"}
    }


def test_add_meilisearch_unsupported_repo(mock_values):
    mock_values["images"]["meili_image"] = {"repository": "unsupported_repo", "tag": "7"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    with pytest.raises(Exception):
        render.deps.meilisearch(
            "meili_container",
            "meili_image",
            {
                "master_key": "test_master_key",
                "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
            },
            perms_container,
        )


def test_add_elasticsearch(mock_values):
    mock_values["images"]["elastic_image"] = {
        "repository": "elasticsearch",
        "tag": "9.1.2",
    }
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    m = render.deps.elasticsearch(
        "elastic_container",
        "elastic_image",
        {
            "password": "test_password",
            "node_name": "some_test_node",
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
        },
        perms_container,
    )
    if perms_container.has_actions():
        perms_container.activate()
        m.container.depends.add_dependency("perms_container", "service_completed_successfully")
    output = render.render()
    assert "devices" not in output["services"]["elastic_container"]
    assert "reservations" not in output["services"]["elastic_container"]["deploy"]["resources"]
    assert output["services"]["elastic_container"]["image"] == "elasticsearch:9.1.2"
    assert output["services"]["elastic_container"]["user"] == "1000:1000"
    assert output["services"]["elastic_container"]["deploy"]["resources"]["limits"]["cpus"] == "2.0"
    assert output["services"]["elastic_container"]["deploy"]["resources"]["limits"]["memory"] == "4096M"
    assert output["services"]["elastic_container"]["healthcheck"] == {
        "test": [
            "CMD",
            "curl",
            "--request",
            "GET",
            "--silent",
            "--output",
            "/dev/null",
            "--show-error",
            "--fail",
            "--header",
            "Authorization: Basic ZWxhc3RpYzp0ZXN0X3Bhc3N3b3Jk",
            "http://127.0.0.1:9200/_cluster/health?local=true",
        ],  # noqa
        "interval": "30s",
        "timeout": "5s",
        "retries": 5,
        "start_period": "15s",
        "start_interval": "2s",
    }
    assert output["services"]["elastic_container"]["volumes"] == [
        {
            "type": "volume",
            "source": "test_volume",
            "target": "/usr/share/elasticsearch/data",
            "read_only": False,
            "volume": {"nocopy": False},
        }
    ]
    assert output["services"]["elastic_container"]["environment"] == {
        "TZ": "Etc/UTC",
        "UMASK": "002",
        "UMASK_SET": "002",
        "NVIDIA_VISIBLE_DEVICES": "void",
        "ELASTIC_PASSWORD": "test_password",
        "http.port": "9200",
        "path.data": "/usr/share/elasticsearch/data",
        "path.repo": "/usr/share/elasticsearch/data/snapshots",
        "node.name": "some_test_node",
        "discovery.type": "single-node",
        "xpack.security.enabled": "true",
        "xpack.security.transport.ssl.enabled": "false",
    }
    assert output["services"]["elastic_container"]["depends_on"] == {
        "perms_container": {"condition": "service_completed_successfully"}
    }


def test_add_elasticsearch_unsupported_repo(mock_values):
    mock_values["images"]["elastic_image"] = {"repository": "unsupported_repo", "tag": "7"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    with pytest.raises(Exception):
        render.deps.elasticsearch(
            "elastic_container",
            "elastic_image",
            {
                "password": "test_password",
                "node_name": "some_test_node",
                "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
            },
            perms_container,
        )


def test_add_solr(mock_values):
    mock_values["images"]["solr_image"] = {"repository": "solr", "tag": "9.9.0"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    m = render.deps.solr(
        "solr_container",
        "solr_image",
        {
            "core": "test_core",
            "modules": ["analysis-extras", "some-other-module"],
            "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
        },
        perms_container,
    )
    if perms_container.has_actions():
        perms_container.activate()
        m.container.depends.add_dependency("perms_container", "service_completed_successfully")
    output = render.render()
    assert "devices" not in output["services"]["solr_container"]
    assert "reservations" not in output["services"]["solr_container"]["deploy"]["resources"]
    assert output["services"]["solr_container"]["image"] == "solr:9.9.0"
    assert output["services"]["solr_container"]["user"] == "568:568"
    assert output["services"]["solr_container"]["deploy"]["resources"]["limits"]["cpus"] == "2.0"
    assert output["services"]["solr_container"]["deploy"]["resources"]["limits"]["memory"] == "4096M"
    assert output["services"]["solr_container"]["healthcheck"] == {
        "test": [
            "CMD",
            "curl",
            "--request",
            "GET",
            "--silent",
            "--output",
            "/dev/null",
            "--show-error",
            "--fail",
            "http://127.0.0.1:8983/solr/test_core/admin/ping",
        ],
        "interval": "30s",
        "timeout": "5s",
        "retries": 5,
        "start_period": "15s",
        "start_interval": "2s",
    }
    assert output["services"]["solr_container"]["volumes"] == [
        {
            "type": "volume",
            "source": "test_volume",
            "target": "/var/solr",
            "read_only": False,
            "volume": {"nocopy": False},
        }
    ]
    assert output["services"]["solr_container"]["environment"] == {
        "TZ": "Etc/UTC",
        "UMASK": "002",
        "UMASK_SET": "002",
        "NVIDIA_VISIBLE_DEVICES": "void",
        "SOLR_PORT": "8983",
        "SOLR_MODULES": "analysis-extras,some-other-module",
    }
    assert output["services"]["solr_container"]["command"] == ["solr-precreate", "test_core"]
    assert output["services"]["solr_container"]["depends_on"] == {
        "perms_container": {"condition": "service_completed_successfully"}
    }


def test_add_solr_unsupported_repo(mock_values):
    mock_values["images"]["solr_image"] = {"repository": "unsupported_repo", "tag": "7"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    perms_container = render.deps.perms("perms_container")
    with pytest.raises(Exception):
        render.deps.solr(
            "solr_container",
            "solr_image",
            {
                "core": "test_core",
                "volume": {"type": "volume", "volume_config": {"volume_name": "test_volume", "auto_permissions": True}},
            },
            perms_container,
        )


def test_add_tika(mock_values):
    mock_values["images"]["tika_image"] = {"repository": "apache/tika", "tag": "3.2.3.0-full"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    render.deps.tika(
        "tika_container",
        "tika_image",
        {
            "port": 10999,
        },
    )
    output = render.render()
    assert "devices" not in output["services"]["tika_container"]
    assert "reservations" not in output["services"]["tika_container"]["deploy"]["resources"]
    assert output["services"]["tika_container"]["image"] == "apache/tika:3.2.3.0-full"
    assert output["services"]["tika_container"]["user"] == "568:568"
    assert output["services"]["tika_container"]["deploy"]["resources"]["limits"]["cpus"] == "2.0"
    assert output["services"]["tika_container"]["deploy"]["resources"]["limits"]["memory"] == "4096M"
    assert output["services"]["tika_container"]["healthcheck"] == {
        "test": [
            "CMD",
            "wget",
            "--quiet",
            "-O",
            "/dev/null",
            "http://127.0.0.1:10999/tika",
        ],
        "interval": "30s",
        "timeout": "5s",
        "retries": 5,
        "start_period": "15s",
        "start_interval": "2s",
    }
    assert output["services"]["tika_container"]["environment"] == {
        "TZ": "Etc/UTC",
        "UMASK": "002",
        "UMASK_SET": "002",
        "NVIDIA_VISIBLE_DEVICES": "void",
    }
    assert output["services"]["tika_container"]["command"] == ["--port", "10999"]


def test_add_tika_unsupported_repo(mock_values):
    mock_values["images"]["tika_image"] = {"repository": "unsupported_repo", "tag": "7"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(Exception):
        render.deps.tika(
            "tika_container",
            "tika_image",
            {},
        )
