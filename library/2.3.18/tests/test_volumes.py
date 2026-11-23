import pytest
from pathlib import Path


from base.error import RenderError
from base.render import Render
from base.formatter import get_hashed_name_for_volume


def test_add_volume_invalid_type(c1):
    with pytest.raises(RenderError, match=r"Storage type \[invalid_type\] is not supported for volume mounts"):
        c1.add_storage("/some/path", {"type": "invalid_type"})


def test_add_volume_empty_mount_path(c1):
    with pytest.raises(RenderError, match=r"Path \[\] cannot be empty"):
        c1.add_storage("", {"type": "tmpfs"})


def test_add_volume_duplicate_mount_path(c1):
    c1.add_storage("/some/path", {"type": "tmpfs"})
    with pytest.raises(RenderError, match=r"Tmpfs mount path \[/some/path\] already added"):
        c1.add_storage("/some/path", {"type": "tmpfs"})


@pytest.mark.parametrize(
    "host_path_config, match",
    [
        pytest.param(
            {"type": "host_path", "host_path_config": {"path": "/mnt/test", "propagation": "invalid_propagation"}},
            r"Expected \[propagation\] to be one of \[.*\], got \[invalid_propagation\]",
            id="add_volume_host_path_invalid_propagation",
        ),
        pytest.param(
            {"type": "host_path"},
            r"Expected \[host_path_config\] to be set for \[host_path\] type",
            id="add_host_path_volume_no_host_path_config",
        ),
        pytest.param(
            {"type": "host_path", "host_path_config": {"path": ""}},
            r"Path \[\] cannot be empty",
            id="add_host_path_volume_no_path",
        ),
        pytest.param(
            {"type": "host_path", "host_path_config": {"acl_enable": True, "acl": {"path": ""}}},
            r"Expected \[host_path_config\.acl\.path\] to be set for \[host_path\] type",
            id="add_host_path_with_acl_no_path",
        ),
        pytest.param(
            {"type": "host_path", "host_path_config": {"path": "/mnt"}},
            r"Path \[/mnt\] is not allowed to be mounted",
            id="host_path_with_disallowed_path",
        ),
        pytest.param(
            {"type": "host_path", "host_path_config": {"path": "/dev/zfs"}},
            r"Path \[/dev/zfs\] is not allowed to be mounted",
            id="host_path_with_zfs_device",
        ),
    ],
)
def test_add_host_path_volume_invalid(c1, host_path_config, match):
    with pytest.raises(RenderError, match=match):
        c1.add_storage("/some/path", host_path_config)


@pytest.mark.parametrize(
    "host_path_config, source, read_only, bind",
    [
        pytest.param(
            {"type": "host_path", "host_path_config": {"path": "/mnt/test"}},
            "/mnt/test",
            False,
            {"create_host_path": False, "propagation": "rprivate"},
            id="add_host_path_volume_mount",
        ),
        pytest.param(
            {
                "type": "host_path",
                "host_path_config": {"path": "/mnt/test", "acl_enable": True, "acl": {"path": "/mnt/test/acl"}},
            },
            "/mnt/test/acl",
            False,
            {"create_host_path": False, "propagation": "rprivate"},
            id="add_host_path_volume_mount_with_acl",
        ),
        pytest.param(
            {"type": "host_path", "host_path_config": {"path": "/mnt/test", "propagation": "slave"}},
            "/mnt/test",
            False,
            {"create_host_path": False, "propagation": "slave"},
            id="add_host_path_volume_mount_with_propagation",
        ),
        pytest.param(
            {"type": "host_path", "host_path_config": {"path": "/mnt/test", "create_host_path": True}},
            "/mnt/test",
            False,
            {"create_host_path": True, "propagation": "rprivate"},
            id="add_host_path_volume_mount_with_create_host_path",
        ),
        pytest.param(
            {"type": "host_path", "read_only": True, "host_path_config": {"path": "/mnt/test"}},
            "/mnt/test",
            True,
            {"create_host_path": False, "propagation": "rprivate"},
            id="add_host_path_volume_mount_with_read_only",
        ),
    ],
)
def test_add_host_path_volume_mount(render, c1, host_path_config, source, read_only, bind):
    c1.add_storage("/some/path", host_path_config)
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {"type": "bind", "source": source, "target": "/some/path", "read_only": read_only, "bind": bind}
    ]


@pytest.mark.parametrize(
    "ix_volume_config, match",
    [
        pytest.param(
            {"type": "ix_volume", "ix_volume_config": {"dataset_name": "invalid_dataset"}},
            r"Expected the key \[invalid_dataset\] to be set in \[ix_volumes\] for \[ix_volume\] type",
            id="add_ix_volume_invalid_dataset_name",
        ),
        pytest.param(
            {"type": "ix_volume"},
            r"Expected \[ix_volume_config\] to be set for \[ix_volume\] type",
            id="add_ix_volume_no_ix_volume_config",
        ),
    ],
)
def test_add_ix_volume_invalid(mock_values, ix_volume_config, match):
    mock_values["ix_volumes"] = {"test_dataset": "/mnt/test"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    with pytest.raises(RenderError, match=match):
        c1.add_storage("/some/path", ix_volume_config)


@pytest.mark.parametrize(
    "ix_volume_config, bind",
    [
        pytest.param(
            {"type": "ix_volume", "ix_volume_config": {"dataset_name": "test_dataset"}},
            {"create_host_path": False, "propagation": "rprivate"},
            id="add_ix_volume_volume_mount",
        ),
        pytest.param(
            {
                "type": "ix_volume",
                "ix_volume_config": {"dataset_name": "test_dataset", "propagation": "rslave", "create_host_path": True},
            },
            {"create_host_path": True, "propagation": "rslave"},
            id="add_ix_volume_volume_mount_with_options",
        ),
    ],
)
def test_add_ix_volume_volume_mount(mock_values, ix_volume_config, bind):
    mock_values["ix_volumes"] = {"test_dataset": "/mnt/test"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.add_storage("/some/path", ix_volume_config)
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {"type": "bind", "source": "/mnt/test", "target": "/some/path", "read_only": False, "bind": bind}
    ]


CIFS_CONFIG = {"server": "server", "path": "/path", "username": "user", "password": "pas$word"}


@pytest.mark.parametrize(
    "cifs_config, match",
    [
        pytest.param(
            {"type": "cifs", "cifs_config": {"path": "/path", "username": "user", "password": "password"}},
            r"Expected \[server\] to be set for \[cifs\] type",
            id="cifs_volume_missing_server",
        ),
        pytest.param(
            {"type": "cifs", "cifs_config": {"server": "server", "username": "user", "password": "password"}},
            r"Expected \[path\] to be set for \[cifs\] type",
            id="cifs_volume_missing_path",
        ),
        pytest.param(
            {"type": "cifs", "cifs_config": {"server": "server", "path": "/path", "password": "password"}},
            r"Expected \[username\] to be set for \[cifs\] type",
            id="cifs_volume_missing_username",
        ),
        pytest.param(
            {"type": "cifs", "cifs_config": {"server": "server", "path": "/path", "username": "user"}},
            r"Expected \[password\] to be set for \[cifs\] type",
            id="cifs_volume_missing_password",
        ),
        pytest.param(
            {"type": "cifs"},
            r"Expected \[cifs_config\] to be set for \[cifs\] type",
            id="cifs_volume_without_cifs_config",
        ),
        pytest.param(
            {"type": "cifs", "cifs_config": {**CIFS_CONFIG, "options": ["verbose=true", "verbose=true"]}},
            r"Option \[verbose\] already added for \[cifs\] type",
            id="cifs_volume_duplicate_option",
        ),
        pytest.param(
            {"type": "cifs", "cifs_config": {**CIFS_CONFIG, "options": ["user=username"]}},
            r"Option \[user\] is not allowed for \[cifs\] type",
            id="cifs_volume_disallowed_option",
        ),
        pytest.param(
            {"type": "cifs", "cifs_config": {**CIFS_CONFIG, "options": {"verbose": True}}},
            r"Expected \[cifs_config\.options\] to be a list for \[cifs\] type",
            id="cifs_volume_invalid_options",
        ),
        pytest.param(
            {"type": "cifs", "cifs_config": {**CIFS_CONFIG, "options": [{"verbose": True}]}},
            r"Options for \[cifs\] type must be a list of strings",
            id="cifs_volume_invalid_options2",
        ),
    ],
)
def test_cifs_volume_invalid(c1, cifs_config, match):
    with pytest.raises(RenderError, match=match):
        c1.add_storage("/some/path", cifs_config)


@pytest.mark.parametrize(
    "cifs_inner_config, options",
    [
        pytest.param(CIFS_CONFIG, "noperm,password=pas$$word,user=user", id="add_cifs_volume"),
        pytest.param(
            {**CIFS_CONFIG, "options": ["vers=3.0", "verbose=true"]},
            "noperm,password=pas$$word,user=user,verbose=true,vers=3.0",
            id="cifs_volume_with_options",
        ),
    ],
)
def test_add_cifs_volume(render, c1, cifs_inner_config, options):
    c1.add_storage("/some/path", {"type": "cifs", "cifs_config": cifs_inner_config})
    output = render.render()
    vol_name = get_hashed_name_for_volume("cifs", cifs_inner_config)
    assert output["volumes"] == {vol_name: {"driver_opts": {"type": "cifs", "device": "//server/path", "o": options}}}
    assert output["services"]["test_container"]["volumes"] == [
        {"type": "volume", "source": vol_name, "target": "/some/path", "read_only": False, "volume": {"nocopy": False}}
    ]


@pytest.mark.parametrize(
    "nfs_config, match",
    [
        pytest.param(
            {"type": "nfs", "nfs_config": {"path": "/path"}},
            r"Expected \[server\] to be set for \[nfs\] type",
            id="nfs_volume_missing_server",
        ),
        pytest.param(
            {"type": "nfs", "nfs_config": {"server": "server"}},
            r"Expected \[path\] to be set for \[nfs\] type",
            id="nfs_volume_missing_path",
        ),
        pytest.param(
            {"type": "nfs"},
            r"Expected \[nfs_config\] to be set for \[nfs\] type",
            id="nfs_volume_without_nfs_config",
        ),
        pytest.param(
            {
                "type": "nfs",
                "nfs_config": {"server": "server", "path": "/path", "options": ["verbose=true", "verbose=true"]},
            },
            r"Option \[verbose\] already added for \[nfs\] type",
            id="nfs_volume_duplicate_option",
        ),
        pytest.param(
            {"type": "nfs", "nfs_config": {"server": "server", "path": "/path", "options": ["addr=server"]}},
            r"Option \[addr\] is not allowed for \[nfs\] type",
            id="nfs_volume_disallowed_option",
        ),
        pytest.param(
            {"type": "nfs", "nfs_config": {"server": "server", "path": "/path", "options": {"verbose": True}}},
            r"Expected \[nfs_config\.options\] to be a list for \[nfs\] type",
            id="nfs_volume_invalid_options",
        ),
        pytest.param(
            {"type": "nfs", "nfs_config": {"server": "server", "path": "/path", "options": [{"verbose": True}]}},
            r"Options for \[nfs\] type must be a list of strings",
            id="nfs_volume_invalid_options2",
        ),
    ],
)
def test_nfs_volume_invalid(c1, nfs_config, match):
    with pytest.raises(RenderError, match=match):
        c1.add_storage("/some/path", nfs_config)


@pytest.mark.parametrize(
    "nfs_inner_config, options",
    [
        pytest.param({"server": "server", "path": "/path"}, "addr=server", id="add_nfs_volume"),
        pytest.param(
            {"server": "server", "path": "/path", "options": ["vers=3.0", "verbose=true"]},
            "addr=server,verbose=true,vers=3.0",
            id="nfs_volume_with_options",
        ),
    ],
)
def test_add_nfs_volume(render, c1, nfs_inner_config, options):
    c1.add_storage("/some/path", {"type": "nfs", "nfs_config": nfs_inner_config})
    output = render.render()
    vol_name = get_hashed_name_for_volume("nfs", nfs_inner_config)
    assert output["volumes"] == {vol_name: {"driver_opts": {"type": "nfs", "device": ":/path", "o": options}}}
    assert output["services"]["test_container"]["volumes"] == [
        {"type": "volume", "source": vol_name, "target": "/some/path", "read_only": False, "volume": {"nocopy": False}}
    ]


@pytest.mark.parametrize(
    "tmpfs_config, match",
    [
        pytest.param(
            {"size": "2"}, r"Expected \[size\] to be an integer for \[tmpfs\] type, got \[2\]", id="tmpfs_invalid_size"
        ),
        pytest.param(
            {"size": 0}, r"Expected \[size\] to be greater than 0 for \[tmpfs\] type, got \[0\]", id="tmpfs_zero_size"
        ),
        pytest.param(
            {"mode": "invalid"}, r"Expected \[mode\] to be a octal string, got \[invalid\]", id="tmpfs_invalid_mode"
        ),
        pytest.param(
            {"exec": "yes"},
            r"Expected \[exec\] to be a boolean for \[tmpfs\] type, got \[yes\]",
            id="tmpfs_invalid_exec",
        ),
    ],
)
def test_tmpfs_invalid(c1, tmpfs_config, match):
    with pytest.raises(RenderError, match=match):
        c1.add_storage("/some/path", {"type": "tmpfs", "tmpfs_config": tmpfs_config})


def test_tmpfs_volume(render, c1):
    c1.add_storage("/some/path", {"type": "tmpfs"})
    c1.add_storage("/some/other/path", {"type": "tmpfs", "tmpfs_config": {"size": 100}})
    c1.add_storage(
        "/some/other/path2", {"type": "tmpfs", "tmpfs_config": {"size": 100, "mode": "0777", "uid": 1000, "gid": 1000}}
    )
    output = render.render()
    assert output["services"]["test_container"]["tmpfs"] == [
        "/some/other/path2:gid=1000,mode=0777,size=104857600,uid=1000",
        "/some/other/path:size=104857600",
        "/some/path",
    ]


def test_tmpfs_exec(render, c1):
    c1.add_storage("/run", {"type": "tmpfs", "tmpfs_config": {"exec": True, "uid": 568, "gid": 568}})
    c1.add_storage("/some/path", {"type": "tmpfs", "tmpfs_config": {"exec": False}})
    output = render.render()
    assert output["services"]["test_container"]["tmpfs"] == [
        "/run:exec,gid=568,uid=568",
        "/some/path",
    ]


TMPFS = {"type": "tmpfs", "tmpfs_config": {"size": 100}}
VOLUME = {"type": "volume", "volume_config": {"volume_name": "test_volume"}}


@pytest.mark.parametrize(
    "first, second, match",
    [
        pytest.param(
            VOLUME,
            TMPFS,
            r"Tmpfs mount path \[/some/path\] already used for another volume mount",
            id="add_tmpfs_with_existing_volume",
        ),
        pytest.param(
            TMPFS,
            VOLUME,
            r"Mount path \[/some/path\] already used for another volume mount",
            id="add_volume_with_existing_tmpfs",
        ),
    ],
)
def test_add_conflicting_mount_path(c1, first, second, match):
    c1.add_storage("/some/path", first)
    with pytest.raises(RenderError, match=match):
        c1.add_storage("/some/path", second)


def test_temporary_volume(render, c1):
    vol_config = {"type": "temporary", "volume_config": {"volume_name": "test_temp_volume"}}
    c1.add_storage("/some/path", vol_config)
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "source": "test_temp_volume",
            "type": "volume",
            "target": "/some/path",
            "read_only": False,
            "volume": {"nocopy": False},
        }
    ]


@pytest.mark.parametrize(
    "volume_config, match",
    [
        pytest.param(
            {}, r"Expected \[volume_config\] to be set for \[volume\] type", id="docker_volume_missing_config"
        ),
        pytest.param(
            {"volume_name": ""},
            r"Expected \[volume_config\.volume_name\] to be set for \[volume\] type",
            id="docker_volume_missing_volume_name",
        ),
    ],
)
def test_docker_volume_invalid(c1, volume_config, match):
    with pytest.raises(RenderError, match=match):
        c1.add_storage("/some/path", {"type": "volume", "volume_config": volume_config})


def test_docker_volume(render, c1):
    vol_config = {"type": "volume", "volume_config": {"volume_name": "test_volume"}}
    c1.add_storage("/some/path", vol_config)
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "volume",
            "source": "test_volume",
            "target": "/some/path",
            "read_only": False,
            "volume": {"nocopy": False},
        }
    ]
    assert output["volumes"] == {"test_volume": {}}


def test_anonymous_volume(render, c1):
    vol_config = {"type": "anonymous", "volume_config": {"nocopy": True}}
    c1.add_storage("/some/path", vol_config)
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {"type": "volume", "target": "/some/path", "read_only": False, "volume": {"nocopy": True}}
    ]
    assert "volumes" not in output


@pytest.mark.parametrize(
    "kwargs, source, target",
    [
        pytest.param({}, "/run/udev", "/run/udev", id="add_udev"),
        pytest.param({"subpath": "data"}, "/run/udev/data", "/run/udev/data", id="add_udev_subpath"),
        pytest.param(
            {"mount_path": "/some/path", "subpath": "data"},
            "/run/udev/data",
            "/some/path",
            id="add_udev_subpath_with_mount_path",
        ),
    ],
)
def test_add_udev(render, c1, kwargs, source, target):
    c1.add_udev(**kwargs)
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "bind",
            "source": source,
            "target": target,
            "read_only": True,
            "bind": {"create_host_path": False, "propagation": "rprivate"},
        }
    ]


@pytest.mark.parametrize(
    "method",
    [
        pytest.param("add_udev", id="add_udev_cannot_be_read_write"),
        pytest.param("add_dbus", id="add_dbus_cannot_be_read_write"),
        pytest.param("add_utmp", id="add_utmp_cannot_be_read_write"),
        pytest.param("add_docker_socket", id="add_docker_socket_cannot_be_read_write"),
    ],
)
def test_cannot_be_read_write(c1, method):
    with pytest.raises(TypeError):
        getattr(c1, method)(read_only=False)


@pytest.mark.parametrize(
    "subpath, match",
    [
        pytest.param(
            "/data",
            r"Expected \[subpath\] to be a relative path without \[\.\.\], got \[/data\]",
            id="/data",
        ),
        pytest.param(
            "../../etc",
            r"Expected \[subpath\] to be a relative path without \[\.\.\], got \[\.\./\.\./etc\]",
            id="../../etc",
        ),
        pytest.param(
            "data/../..",
            r"Expected \[subpath\] to be a relative path without \[\.\.\], got \[data/\.\./\.\.\]",
            id="data/../..",
        ),
        pytest.param("a//b", r"Path \[/run/udev/a//b\] cannot contain \[//\]", id="a//b"),
    ],
)
def test_add_udev_invalid_subpath(c1, subpath, match):
    with pytest.raises(RenderError, match=match):
        c1.add_udev(subpath=subpath)


@pytest.mark.parametrize(
    "kwargs, target",
    [
        pytest.param({}, "/run/dbus", id="add_dbus"),
        pytest.param({"mount_path": "/some/path"}, "/some/path", id="add_dbus_mount_path"),
    ],
)
def test_add_dbus(render, c1, kwargs, target):
    c1.add_dbus(**kwargs)
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "bind",
            "source": "/run/dbus",
            "target": target,
            "read_only": True,
            "bind": {"create_host_path": False, "propagation": "rprivate"},
        }
    ]


@pytest.mark.parametrize(
    "kwargs, target",
    [
        pytest.param({}, "/var/run/utmp", id="add_utmp"),
        pytest.param({"mount_path": "/some/path"}, "/some/path", id="add_utmp_mount_path"),
    ],
)
def test_add_utmp(render, c1, kwargs, target):
    c1.add_utmp(**kwargs)
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "bind",
            "source": "/var/run/utmp",
            "target": target,
            "read_only": True,
            "bind": {"create_host_path": False, "propagation": "rprivate"},
        }
    ]


@pytest.mark.parametrize(
    "mount_path",
    [
        pytest.param("/var/run/docker.sock", id="add_docker_socket"),
        pytest.param("/some/path", id="add_docker_socket_mount_path"),
    ],
)
def test_add_docker_socket(render, c1, mount_path):
    c1.storage._add_docker_socket(mount_path=mount_path)
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "bind",
            "source": "/var/run/docker.sock",
            "target": mount_path,
            "read_only": True,
            "bind": {"create_host_path": False, "propagation": "rprivate"},
        }
    ]


def test_host_path_without_disallowed_path(render, c1):
    host_path_config = {"type": "host_path", "host_path_config": {"path": "/mnt/test"}}
    c1.add_storage("/mnt", host_path_config)
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "bind",
            "source": "/mnt/test",
            "target": "/mnt",
            "read_only": False,
            "bind": {"create_host_path": False, "propagation": "rprivate"},
        }
    ]


# Symlinks resolve on the machine that renders, so they are faked
SYMLINKS = {"/mnt/pool/link": "/mnt/pool/target", "/mnt/pool/sock": "/run/docker.sock", "/mnt/pool/data": "/data"}


def mock_resolve(self):
    return Path(SYMLINKS.get(str(self), str(self)))


def test_host_path_resolved_source(render, c1, monkeypatch):
    monkeypatch.setattr(Path, "resolve", mock_resolve)
    c1.add_storage("/data", {"type": "host_path", "host_path_config": {"path": "/mnt/pool/link"}})
    (vm,) = c1.storage._volume_mounts
    assert vm.resolved_source == "/mnt/pool/target"
    # The rendered source is the path as given
    output = render.render()
    assert output["services"]["test_container"]["volumes"][0]["source"] == "/mnt/pool/link"


def test_host_path_symlink_to_restricted_path(c1, monkeypatch):
    monkeypatch.setattr(Path, "resolve", mock_resolve)
    with pytest.raises(RenderError, match=r"Path \[/mnt/pool/data\] is not allowed to be mounted"):
        c1.add_storage("/data", {"type": "host_path", "host_path_config": {"path": "/mnt/pool/data"}})


def test_ix_volume_resolved_source(mock_values, monkeypatch):
    monkeypatch.setattr(Path, "resolve", mock_resolve)
    mock_values["ix_volumes"] = {"test_dataset": "/mnt/pool/link"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.add_storage("/data", {"type": "ix_volume", "ix_volume_config": {"dataset_name": "test_dataset"}})
    (vm,) = c1.storage._volume_mounts
    assert vm.resolved_source == "/mnt/pool/target"


def test_volume_has_no_resolved_source(c1):
    c1.add_storage("/data", {"type": "volume", "volume_config": {"volume_name": "test_volume"}})
    (vm,) = c1.storage._volume_mounts
    assert vm.resolved_source == ""


def test_docker_socket_symlink_risk_warning(render, c1, monkeypatch):
    monkeypatch.setattr(Path, "resolve", mock_resolve)
    c1.add_storage("/var/run/docker.sock", {"type": "host_path", "host_path_config": {"path": "/mnt/pool/sock"}})
    output = render.render()
    assert "This app has access to the Docker socket" in output["x-notes"]
