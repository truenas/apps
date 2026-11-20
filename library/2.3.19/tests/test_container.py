import pytest


from base.error import RenderError
from base.render import Render


@pytest.mark.parametrize(
    "name, image, match",
    [
        pytest.param("  ", "test_image", r"Container name cannot be empty", id="empty_container_name"),
        pytest.param(
            "test_container",
            "non_existing_image",
            r"Image \[non_existing_image\] not found in values",
            id="non_existing_image",
        ),
    ],
)
def test_add_container_invalid(render, name, image, match):
    with pytest.raises(RenderError, match=match):
        render.add_container(name, image)


def test_resolve_image(render, c1):
    output = render.render()
    assert output["services"]["test_container"]["image"] == "nginx:latest"


@pytest.mark.parametrize(
    "key, match",
    [
        pytest.param("repository", r"Repository not found for image \[test_image\]", id="missing_repo"),
        pytest.param("tag", r"Tag not found for image \[test_image\]", id="missing_tag"),
    ],
)
def test_image_missing_field(mock_values, key, match):
    mock_values["images"]["test_image"][key] = ""
    render = Render(mock_values)
    with pytest.raises(RenderError, match=match):
        render.add_container("test_container", "test_image")


def test_pull_policy(render, c1):
    c1.set_pull_policy("always")
    output = render.render()
    assert output["services"]["test_container"]["pull_policy"] == "always"


def test_invalid_pull_policy(c1):
    with pytest.raises(RenderError, match=r"Pull policy \[invalid_policy\] is not valid"):
        c1.set_pull_policy("invalid_policy")


def test_clear_caps(render, c1):
    c1.add_caps(["NET_ADMIN"])
    c1.clear_caps()
    output = render.render()
    assert "cap_drop" not in output["services"]["test_container"]
    assert "cap_add" not in output["services"]["test_container"]


@pytest.mark.parametrize(
    "setter, key",
    [
        pytest.param("set_privileged", "privileged", id="privileged"),
        pytest.param("set_tty", "tty", id="tty"),
        pytest.param("set_init", "init", id="init"),
        pytest.param("set_read_only", "read_only", id="read_only"),
        pytest.param("set_stdin", "stdin_open", id="stdin"),
    ],
)
def test_boolean_flag(render, c1, setter, key):
    getattr(c1, setter)(True)
    output = render.render()
    assert output["services"]["test_container"][key] is True


def test_hostname(render, c1):
    c1.set_hostname("test_hostname")
    output = render.render()
    assert output["services"]["test_container"]["hostname"] == "test_hostname"


def test_grace_period(render, c1):
    c1.set_grace_period(10)
    output = render.render()
    assert output["services"]["test_container"]["stop_grace_period"] == "10s"


def test_user(render, c1):
    c1.set_user(1000, 1000)
    output = render.render()
    assert output["services"]["test_container"]["user"] == "1000:1000"


def test_invalid_user(c1):
    with pytest.raises(RenderError, match=r"User/Group \[-100\] is not valid"):
        c1.set_user(-100, 1000)


def test_add_group(render, c1):
    c1.add_group(1000)
    c1.add_group("video")
    output = render.render()
    assert output["services"]["test_container"]["group_add"] == [568, 1000, "video"]


def test_add_duplicate_group(c1):
    c1.add_group(1000)
    with pytest.raises(RenderError, match=r"Group \[1000\] already added"):
        c1.add_group(1000)


def test_add_group_as_string(c1):
    with pytest.raises(RenderError, match=r"Group is a number \[1000\] but passed as a string"):
        c1.add_group("1000")


def test_add_docker_socket(render, c1):
    c1.add_docker_socket()
    output = render.render()
    assert output["services"]["test_container"]["group_add"] == [568, 999]
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "bind",
            "source": "/var/run/docker.sock",
            "target": "/var/run/docker.sock",
            "read_only": True,
            "bind": {
                "propagation": "rprivate",
                "create_host_path": False,
            },
        }
    ]


def test_snd_device(render, c1):
    c1.add_snd_device()
    output = render.render()
    assert output["services"]["test_container"]["devices"] == ["/dev/snd:/dev/snd"]
    assert output["services"]["test_container"]["group_add"] == [29, 568]


def test_shm_size(render, c1):
    c1.set_shm_size_mb(10)
    output = render.render()
    assert output["services"]["test_container"]["shm_size"] == "10M"


def test_valid_caps(render, c1):
    c1.add_caps(["ALL", "NET_ADMIN"])
    output = render.render()
    assert output["services"]["test_container"]["cap_add"] == ["ALL", "NET_ADMIN"]
    assert output["services"]["test_container"]["cap_drop"] == ["ALL"]


@pytest.mark.parametrize(
    "caps, match",
    [
        pytest.param(
            ["ALL", "NET_ADMIN", "NET_ADMIN"], r"Capability \[NET_ADMIN\] already added", id="add_duplicate_caps"
        ),
        pytest.param(["invalid_cap"], r"Capability \[invalid_cap\] is not valid", id="invalid_caps"),
    ],
)
def test_add_caps_invalid(c1, caps, match):
    with pytest.raises(RenderError, match=match):
        c1.add_caps(caps)


@pytest.mark.parametrize(
    "mode",
    [
        pytest.param("host", id="network_mode"),
        pytest.param("service:test_container", id="network_mode_with_container"),
    ],
)
def test_network_mode(render, c1, mode):
    c1.set_network_mode(mode)
    output = render.render()
    assert output["services"]["test_container"]["network_mode"] == mode


def test_auto_network_mode_with_host_network(mock_values):
    mock_values["network"] = {"host_network": True}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    output = render.render()
    assert output["services"]["test_container"]["network_mode"] == "host"


@pytest.mark.parametrize(
    "mode, match",
    [
        pytest.param(
            "service:missing_container",
            r"Service \[missing_container\] not found",
            id="network_mode_with_container_missing",
        ),
        pytest.param("invalid_mode", r"Invalid network mode \[invalid_mode\]", id="invalid_network_mode"),
    ],
)
def test_network_mode_invalid(c1, mode, match):
    with pytest.raises(RenderError, match=match):
        c1.set_network_mode(mode)


def test_entrypoint(render, c1):
    c1.set_entrypoint(["/bin/bash", "-c", "echo hello $MY_ENV"])
    output = render.render()
    assert output["services"]["test_container"]["entrypoint"] == ["/bin/bash", "-c", "echo hello $$MY_ENV"]


def test_command(render, c1):
    c1.set_command(["echo", "hello $MY_ENV"])
    output = render.render()
    assert output["services"]["test_container"]["command"] == ["echo", "hello $$MY_ENV"]


def test_add_ports(render, c1):
    c1.add_port({"port_number": 8081, "container_port": 8080, "bind_mode": "published"})
    c1.add_port({"port_number": 8082, "container_port": 8080, "bind_mode": "published", "protocol": "udp"})
    c1.add_port({"port_number": 8083, "container_port": 8080, "bind_mode": "exposed"})
    c1.add_port({"port_number": 8084, "container_port": 8080, "bind_mode": ""})
    c1.add_port(
        {"port_number": 9091, "container_port": 9091, "bind_mode": "published"},
        {"container_port": 9092, "protocol": "udp"},
    )
    output = render.render()
    assert output["services"]["test_container"]["ports"] == [
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress"},
        {"published": 8082, "target": 8080, "protocol": "udp", "mode": "ingress"},
        {"published": 9091, "target": 9092, "protocol": "udp", "mode": "ingress"},
    ]
    assert output["services"]["test_container"]["expose"] == ["8080/tcp"]


def test_add_ports_with_invalid_host_ips(c1):
    with pytest.raises(RenderError, match=r"Expected \[host_ips\] to be a list, got \[invalid\]"):
        c1.add_port({"port_number": 8081, "container_port": 8080, "bind_mode": "published", "host_ips": "invalid"})


def test_add_ports_with_empty_host_ips(render, c1):
    c1.add_port({"port_number": 8081, "container_port": 8080, "bind_mode": "published", "host_ips": []})
    output = render.render()
    assert output["services"]["test_container"]["ports"] == [
        {"published": 8081, "target": 8080, "protocol": "tcp", "mode": "ingress"}
    ]


@pytest.mark.parametrize(
    "mode",
    [
        pytest.param("host", id="set_ipc_mode"),
        pytest.param("", id="set_ipc_empty_mode"),
    ],
)
def test_set_ipc_mode(render, c1, mode):
    c1.set_ipc_mode(mode)
    output = render.render()
    assert output["services"]["test_container"]["ipc"] == mode


@pytest.mark.parametrize(
    "mode, match",
    [
        pytest.param("invalid", r"IPC mode \[invalid\] is not valid", id="set_ipc_mode_with_invalid_ipc_mode"),
        pytest.param(
            "container:invalid",
            r"IPC mode \[container:invalid\] is not valid\. Container \[invalid\] does not exist",
            id="set_ipc_mode_with_container_ipc_mode_and_invalid_container",
        ),
    ],
)
def test_set_ipc_mode_invalid(c1, mode, match):
    with pytest.raises(RenderError, match=match):
        c1.set_ipc_mode(mode)


def test_set_ipc_mode_with_container_ipc_mode(render, c1):
    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()
    c1.set_ipc_mode("container:test_container2")
    output = render.render()
    assert output["services"]["test_container"]["ipc"] == "container:test_container2"


@pytest.mark.parametrize(
    "mode",
    [
        pytest.param("host", id="set_pid_mode"),
        pytest.param("", id="set_pid_empty_mode"),
    ],
)
def test_set_pid_mode(render, c1, mode):
    c1.set_pid_mode(mode)
    output = render.render()
    assert output["services"]["test_container"]["pid"] == mode


@pytest.mark.parametrize(
    "mode, match",
    [
        pytest.param("invalid", r"PID mode \[invalid\] is not valid", id="set_pid_mode_with_invalid_pid_mode"),
        pytest.param(
            "container:invalid",
            r"PID mode \[container:invalid\] is not valid\. Container \[invalid\] does not exist",
            id="set_pid_mode_with_container_pid_mode_and_invalid_container",
        ),
    ],
)
def test_set_pid_mode_invalid(c1, mode, match):
    with pytest.raises(RenderError, match=match):
        c1.set_pid_mode(mode)


def test_set_pid_mode_with_container_pid_mode(render, c1):
    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()
    c1.set_pid_mode("container:test_container2")
    output = render.render()
    assert output["services"]["test_container"]["pid"] == "container:test_container2"


def test_set_cgroup(render, c1):
    c1.set_cgroup("host")
    output = render.render()
    assert output["services"]["test_container"]["cgroup"] == "host"


def test_set_cgroup_invalid(c1):
    with pytest.raises(RenderError, match=r"Cgroup \[invalid\] is not valid"):
        c1.set_cgroup("invalid")


def test_set_mac_invalid(c1):
    with pytest.raises(RenderError, match=r"Invalid MAC Address \[invalid_mac\]"):
        c1.set_mac("invalid_mac")


def test_set_mac_valid(render, c1):
    c1.set_mac("00:00:00:00:00:00")
    output = render.render()
    assert output["services"]["test_container"]["mac_address"] == "00:00:00:00:00:00"


@pytest.mark.parametrize(
    "kwargs, cpus, memory",
    [
        pytest.param({}, "1", "512M", id="setup_as_helper"),
        pytest.param({"profile": "medium"}, "2", "1024M", id="setup_as_helper_med_profile"),
        pytest.param({"profile": ""}, "2.0", "4096M", id="setup_as_helper_no_profile"),
    ],
)
def test_setup_as_helper(mock_values, kwargs, cpus, memory):
    mock_values["resources"] = {"gpus": {"use_all_gpus": True}}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.setup_as_helper(**kwargs)
    output = render.render()
    assert output["services"]["test_container"]["restart"] == "on-failure:1"
    assert output["services"]["test_container"]["network_mode"] == "none"
    assert output["services"]["test_container"]["healthcheck"]["disable"] is True
    assert output["services"]["test_container"]["deploy"]["resources"]["limits"]["cpus"] == cpus
    assert output["services"]["test_container"]["deploy"]["resources"]["limits"]["memory"] == memory
    assert "devices" not in output["services"]["test_container"]


def test_setup_as_helper_with_net(mock_values):
    mock_values["resources"] = {"gpus": {"use_all_gpus": True}}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.setup_as_helper(disable_network=False)
    output = render.render()
    assert output["services"]["test_container"]["restart"] == "on-failure:1"
    assert output["services"]["test_container"]["healthcheck"]["disable"] is True
    assert output["services"]["test_container"]["deploy"]["resources"]["limits"]["cpus"] == "1"
    assert output["services"]["test_container"]["deploy"]["resources"]["limits"]["memory"] == "512M"
    assert "devices" not in output["services"]["test_container"]


def test_container_name(c1):
    assert c1.name() == "test_container"
