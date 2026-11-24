import pytest


from base.render import Render


@pytest.fixture
def mock_values():
    return {
        "ix_context": {
            "app_name": "My Test App",
            "app_metadata": {
                "name": "test_app",
                "title": "Test App",
                "train": "enterprise",
            },
        },
        "images": {
            "test_image": {
                "repository": "nginx",
                "tag": "latest",
            }
        },
    }


def test_notes(render, c1):
    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

## Security

**Read the following security precautions to ensure that you wish to continue using this application.**

---

### Container: [test_container]

#### Running user/group(s)

- User: unknown
- Group: unknown
- Supplementary Groups: apps

---

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://ixsystems.atlassian.net
"""
    )


def test_notes_on_non_enterprise_train(mock_values):
    mock_values["ix_context"]["app_metadata"]["train"] = "community"
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.set_user(568, 568)
    c1.healthcheck.disable()
    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

## Security

**Read the following security precautions to ensure that you wish to continue using this application.**

---

### Container: [test_container]

#### Running user/group(s)

- User: 568
- Group: 568
- Supplementary Groups: apps

---

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://github.com/truenas/apps
"""
    )


def test_notes_with_warnings(render, c1):
    render.notes.add_warning("this is not properly configured. fix it now!")
    render.notes.add_warning("that is not properly configured. fix it later!")
    c1.set_user(568, 568)
    output = render.render()
    assert output["x-action-required"] is True
    assert (
        output["x-notes"]
        == """# Test App ⚠️

## Warnings ⚠️

- this is not properly configured. fix it now!
- that is not properly configured. fix it later!

## Security

**Read the following security precautions to ensure that you wish to continue using this application.**

---

### Container: [test_container]

#### Running user/group(s)

- User: 568
- Group: 568
- Supplementary Groups: apps

---

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://ixsystems.atlassian.net
"""
    )


def test_notes_with_risks(render, c1):
    render.notes.add_warning("this is not properly configured. fix it now!")
    render.notes.declare_risk("truenas_api_access", True)
    # Declaring the same risk again is a no-op
    render.notes.declare_risk("truenas_api_access", True)
    render.notes.declare_risk("mdns", True)
    c1.set_user(568, 568)
    output = render.render()
    assert "x-readme" not in output
    assert (
        output["x-notes"]
        == """# Test App ⚠️

## Risks ⚠️

---

**!!! WARNING !!!**

This application requires additional elevated permissions beyond standard containerization protections. Use at your own risk.

The following additional privileges are enabled for this application:

- TrueNAS API Key

The following additional privileges may be enabled by this application:

- mDNS Announcements

---

## Warnings ⚠️

- this is not properly configured. fix it now!

## Security

**Read the following security precautions to ensure that you wish to continue using this application.**

---

### Container: [test_container]

#### Running user/group(s)

- User: 568
- Group: 568
- Supplementary Groups: apps

---

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://ixsystems.atlassian.net
"""  # noqa: E501
    )


def readme_risk_keys(output: dict) -> list[str]:
    return [item["key"] for item in output["x-readme"]["risks"]["items"]]


def enabled_risks_section(labels: list[str]) -> str:
    items = "".join(f"- {label}\n" for label in labels)
    return f"The following additional privileges are enabled for this application:\n\n{items}\n"


def test_notes_risks_do_not_require_action(render, c1, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    # Every risk at once, enabled and may, none of them asks the user for an action
    for risk in ("docker_access", "host_capabilities", "host_network", "host_pid", "privileged"):
        render.notes.declare_risk(risk)
    render.notes.declare_risk("truenas_api_access", True)
    render.notes.declare_risk("mdns", True)
    c1.set_privileged(True)
    c1.set_network_mode("host")
    c1.set_pid_mode("host")
    c1.add_docker_socket()
    # A separate container, privileged mode skips the capabilities risk
    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()
    c2.add_caps(["SYS_ADMIN"])
    output = render.render()
    assert readme_risk_keys(output) == [
        "docker_access",
        "host_capabilities",
        "host_network",
        "host_pid",
        "mdns",
        "privileged",
        "truenas_api_access",
    ]
    assert enabled_risks_section(
        [
            "Docker Socket Access",
            "Extended System Capabilities",
            "Host Networking",
            "Host Process Namespace",
            "Privileged Mode",
            "TrueNAS API Key",
        ]
    ) in output["x-notes"]
    assert "may be enabled by this application:\n\n- mDNS Announcements\n" in output["x-notes"]
    assert output["x-action-required"] is False
    # Risks don't mark the title, only warnings and deprecations do
    assert output["x-notes"].startswith("# Test App\n\n## Risks ⚠️\n\n---\n\n**!!! WARNING !!!**")
    assert "## Warnings" not in output["x-notes"]


def test_notes_invalid_risk(render):
    with pytest.raises(Exception, match=r"Risk \[invalid\] is not valid"):
        render.notes.declare_risk("invalid")


@pytest.mark.parametrize("risk", ["truenas_api_access", "mdns"])
def test_undetectable_risk_needs_applies(render, risk):
    with pytest.raises(Exception, match=rf"Risk \[{risk}\] can't be detected"):
        render.notes.declare_risk(risk)


@pytest.mark.parametrize("risk", ["docker_access", "host_capabilities", "host_network", "host_pid", "privileged"])
def test_detected_risk_takes_no_applies(render, risk):
    with pytest.raises(Exception, match=rf"Risk \[{risk}\] is detected from the containers"):
        render.notes.declare_risk(risk, True)


def test_readme_risks(render, c1, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    render.notes.declare_risk("truenas_api_access", True)
    render.notes.declare_risk("mdns", False)
    # Declared risks the render doesn't have are still possible before install
    render.notes.declare_risk("host_network")
    output = render.render()
    assert output["x-readme"] == {
        "risks": {
            "header": "!!! WARNING !!!",
            "intro": (
                "This application requires additional elevated permissions beyond standard containerization "
                "protections. Use at your own risk."
            ),
            "list_header": "The following additional privileges may be enabled from installing this application:",
            "footer": "",
            "items": [
                {"key": "host_network", "label": "Host Networking"},
                {"key": "mdns", "label": "mDNS Announcements"},
                {"key": "truenas_api_access", "label": "TrueNAS API Key"},
            ],
        }
    }
    # After install, only what applies
    assert enabled_risks_section(["TrueNAS API Key"]) in output["x-notes"]
    assert "Host Networking" not in output["x-notes"]
    assert "mDNS Announcements" not in output["x-notes"]


def test_risks_footer(render, c1, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    monkeypatch.setattr("base.notes.RISKS_FOOTER", "See the apps security page.")
    render.notes.declare_risk("truenas_api_access", True)
    output = render.render()
    assert output["x-readme"]["risks"]["footer"] == "See the apps security page."
    assert "- TrueNAS API Key\n\nSee the apps security page.\n\n---\n\n" in output["x-notes"]


def test_risks_that_do_not_apply_are_not_in_notes(render, c1):
    render.notes.declare_risk("truenas_api_access", False)
    render.notes.declare_risk("mdns", False)
    render.notes.declare_risk("host_network")
    output = render.render()
    assert output["x-notes"].startswith("# Test App\n\n")
    assert "## Risks" not in output["x-notes"]


def test_mdns_only_may_be_enabled(render, c1):
    render.notes.declare_risk("mdns", True)
    output = render.render()
    assert "are enabled for this application" not in output["x-notes"]
    assert (
        "The following additional privileges may be enabled by this application:\n\n- mDNS Announcements\n\n"
        in output["x-notes"]
    )


def test_readme_no_risks(render, c1, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    output = render.render()
    assert output["x-readme"]["risks"]["items"] == []


def test_readme_undeclared_risk_fails(render, c1, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    c1.set_privileged(True)
    c1.add_docker_socket()
    with pytest.raises(Exception, match=r"Risks \[docker_access, privileged\] were detected but not declared"):
        render.render()


def test_undeclared_risk_does_not_fail_install(render, c1):
    # Users can add the socket through additional storage, the notes still list it
    c1.add_docker_socket()
    output = render.render()
    assert enabled_risks_section(["Docker Socket Access"]) in output["x-notes"]


@pytest.mark.parametrize("socket", ["/var/run/docker.sock", "/run/docker.sock"])
def test_risk_docker_socket(render, c1, monkeypatch, socket):
    monkeypatch.setenv("IX_RENDER_README", "1")
    render.notes.declare_risk("docker_access")
    c1.add_storage(socket, {"type": "host_path", "host_path_config": {"path": socket}, "read_only": True})
    output = render.render()
    assert output["x-action-required"] is False
    assert enabled_risks_section(["Docker Socket Access"]) in output["x-notes"]
    assert readme_risk_keys(output) == ["docker_access"]


def test_risk_privileged(render, c1, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    render.notes.declare_risk("privileged")
    c1.set_privileged(True)
    output = render.render()
    assert enabled_risks_section(["Privileged Mode"]) in output["x-notes"]
    assert readme_risk_keys(output) == ["privileged"]


def test_risk_host_network(render, c1, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    render.notes.declare_risk("host_network")
    c1.set_network_mode("host")
    output = render.render()
    assert enabled_risks_section(["Host Networking"]) in output["x-notes"]
    assert readme_risk_keys(output) == ["host_network"]


def test_risk_host_pid(render, c1, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    render.notes.declare_risk("host_pid")
    c1.set_pid_mode("host")
    output = render.render()
    assert output["x-action-required"] is False
    assert enabled_risks_section(["Host Process Namespace"]) in output["x-notes"]
    assert readme_risk_keys(output) == ["host_pid"]


@pytest.mark.parametrize("cap", ["SYS_ADMIN", "SYS_MODULE", "SYS_RAWIO", "DAC_READ_SEARCH"])
def test_risk_host_capabilities(render, c1, monkeypatch, cap):
    monkeypatch.setenv("IX_RENDER_README", "1")
    render.notes.declare_risk("host_capabilities")
    c1.add_caps([cap])
    output = render.render()
    assert output["x-action-required"] is False
    assert enabled_risks_section(["Extended System Capabilities"]) in output["x-notes"]
    assert readme_risk_keys(output) == ["host_capabilities"]


@pytest.mark.parametrize("cap", ["NET_ADMIN", "SYS_PTRACE", "CHOWN"])
def test_no_risk_namespaced_capabilities(render, c1, monkeypatch, cap):
    monkeypatch.setenv("IX_RENDER_README", "1")
    c1.add_caps([cap])
    output = render.render()
    assert readme_risk_keys(output) == []
    assert "## Risks" not in output["x-notes"]


def test_privileged_skips_host_capabilities_risk(render, c1, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    render.notes.declare_risk("privileged")
    c1.set_privileged(True)
    c1.add_caps(["SYS_ADMIN"])
    output = render.render()
    assert enabled_risks_section(["Privileged Mode"]) in output["x-notes"]
    assert readme_risk_keys(output) == ["privileged"]


def test_risk_detected_once_for_many_containers(render, c1, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    render.notes.declare_risk("privileged")
    c1.set_privileged(True)
    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()
    c2.set_privileged(True)
    output = render.render()
    assert enabled_risks_section(["Privileged Mode"]) in output["x-notes"]
    assert readme_risk_keys(output) == ["privileged"]


def test_host_mounts_not_rendered_by_default(render, c1):
    output = render.render()
    assert "x-host-mounts" not in output


def test_host_mounts(render, c1, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    render.notes.declare_risk("docker_access")
    c1.add_docker_socket()
    c1.add_storage("/host/os-release", {"type": "host_path", "host_path_config": {"path": "/etc/os-release"}})
    c1.add_storage("/data", {"type": "host_path", "host_path_config": {"path": "/mnt/pool/data"}})
    c1.devices.add_device("/dev/fuse", "/dev/fuse")
    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()
    c2.add_docker_socket()
    output = render.render()
    assert output["x-host-mounts"] == ["/dev/fuse", "/etc/os-release", "/var/run/docker.sock"]


def test_host_mounts_skip_user_picked_devices(render, c1, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    c1.devices.add_device("/dev/ttyUSB0", "/dev/ttyUSB0")
    output = render.render()
    assert output["x-host-mounts"] == []
    assert "/dev/ttyUSB0 - (Read/Write)" in output["x-notes"]


def test_host_mounts_skip_auto_added_gpus(mock_values, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    mock_values["resources"] = {"gpus": {"use_all_gpus": True, "kfd_device_exists": True}}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.devices.add_dri_device()
    output = render.render()
    assert output["x-host-mounts"] == []


def test_host_mounts_dri_from_template(render, c1, monkeypatch):
    monkeypatch.setenv("IX_RENDER_README", "1")
    c1.devices.add_dri_device()
    output = render.render()
    assert output["x-host-mounts"] == ["/dev/dri"]


def test_notes_with_deprecations(render, c1):
    render.notes.add_deprecation("this is will be removed later. fix it now!")
    render.notes.add_deprecation("that is will be removed later. fix it later!")
    c1.set_user(568, 568)
    output = render.render()
    assert output["x-action-required"] is True
    assert (
        output["x-notes"]
        == """# Test App ⚠️

## Deprecations ⚠️

- this is will be removed later. fix it now!
- that is will be removed later. fix it later!

## Security

**Read the following security precautions to ensure that you wish to continue using this application.**

---

### Container: [test_container]

#### Running user/group(s)

- User: 568
- Group: 568
- Supplementary Groups: apps

---

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://ixsystems.atlassian.net
"""
    )


def test_notes_with_body(render, c1):
    render.notes.set_body(
        """## Additional info

Some info
some other info.
"""
    )
    c1.set_user(568, 568)
    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

## Security

**Read the following security precautions to ensure that you wish to continue using this application.**

---

### Container: [test_container]

#### Running user/group(s)

- User: 568
- Group: 568
- Supplementary Groups: apps

---

## Additional info

Some info
some other info.

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://ixsystems.atlassian.net
"""
    )


def test_notes_all(render, c1):
    render.notes.add_warning("this is not properly configured. fix it now!")
    render.notes.add_warning("that is not properly configured. fix it later!")
    render.notes.add_deprecation("this is will be removed later. fix it now!")
    render.notes.add_deprecation("that is will be removed later. fix it later!")
    render.notes.add_info("some info")
    render.notes.add_info("some other info")
    render.notes.declare_risk("truenas_api_access", True)
    render.notes.set_body(
        """## Additional info

Some info
some other info.
"""
    )
    net1 = render.networks.create_internal("test_network1")
    net2 = render.networks.create_internal("test_network2")

    c1.add_network(net1)
    c1.add_network(net2)
    c1.set_privileged(True)
    c1.set_user(0, 0)
    c1.add_group(0)
    c1.set_ipc_mode("host")
    c1.set_pid_mode("host")
    c1.set_cgroup("host")
    c1.set_tty(True)
    c1.set_grace_period(61)
    c1.remove_security_opt("no-new-privileges")
    c1.add_docker_socket()
    c1.add_udev()
    c1.add_udev(subpath="data")
    c1.add_utmp()
    c1.add_dbus()
    c1.add_tun_device()
    c1.add_usb_bus()
    c1.add_snd_device()
    c1.devices.add_device("/dev/null", "/dev/null", "rwm")
    c1.add_storage("/etc/os-release", {"type": "host_path", "host_path_config": {"path": "/etc/os-release"}})
    c1.restart.set_policy("on-failure", 1)

    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()
    c2.set_user(568, 568)

    c3 = render.add_container("test_container3", "test_image")
    c3.healthcheck.disable()
    c3.restart.set_policy("on-failure", 1)
    c3.set_user(568, 568)

    output = render.render()
    assert output["x-action-required"] is True
    assert (
        output["x-notes"]
        == """# Test App ⚠️

## Risks ⚠️

---

**!!! WARNING !!!**

This application requires additional elevated permissions beyond standard containerization protections. Use at your own risk.

The following additional privileges are enabled for this application:

- Docker Socket Access
- Host Process Namespace
- Privileged Mode
- TrueNAS API Key

---

## Warnings ⚠️

- Container [test_container] is running with a TTY, Logs do not appear correctly in the UI due to an [upstream bug](https://github.com/docker/docker-py/issues/1394)
- this is not properly configured. fix it now!
- that is not properly configured. fix it later!
- Container [test_container] has a grace period of [61] seconds. TrueNAS waits a maximum of 60 seconds for docker engine to stop during system reboot/shutdown. If the container needs the full configured grace period, manually stop it before reboot/shutdown to ensure the full wait time is honored.

## Deprecations ⚠️

- this is will be removed later. fix it now!
- that is will be removed later. fix it later!

## Info

- some info
- some other info

## Security

**Read the following security precautions to ensure that you wish to continue using this application.**

---

### Container: [test_container2]

#### Running user/group(s)

- User: 568
- Group: 568
- Supplementary Groups: apps

---

### Container: [test_container]

**This container is short-lived.**

#### Privileged mode is enabled

- Has the same level of control as a system administrator
- Can access and modify any part of your TrueNAS system

#### Joined networks

- ix-internal-my-test-app-test_network1
- ix-internal-my-test-app-test_network2

#### Running user/group(s)

- User: root
- Group: root
- Supplementary Groups: apps, audio, docker, root

#### Host IPC namespace is enabled

- Container can access the inter-process communication mechanisms of the host
- Allows communication with other processes on the host under particular circumstances

#### Host PID namespace is enabled

- Container can see and interact with all host processes
- Potential for privilege escalation or process manipulation

#### Host cgroup namespace is enabled

- Container shares control groups with the host system
- Can bypass resource limits and isolation boundaries

#### Security option [no-new-privileges] is not set

- Processes can gain additional privileges through setuid/setgid binaries
- Can potentially allow privilege escalation attacks within the container

#### Passing Host Files, Devices, or Sockets into the Container

- /dev/null - (rwm)
- /run/udev/data - (Read Only)
- DBus Socket (/run/dbus) - (Read Only)
- Docker Socket (/var/run/docker.sock) - (Read Only)
- OS Release File (/etc/os-release) - (Read/Write)
- Sound Device (/dev/snd) - (Read/Write)
- TUN Device (/dev/net/tun) - (Read/Write)
- USB Devices (/dev/bus/usb) - (Read/Write)
- UTMP (/var/run/utmp) - (Read Only)
- Udev Socket (/run/udev) - (Read Only)

---

### Container: [test_container3]

**This container is short-lived.**

#### Running user/group(s)

- User: 568
- Group: 568
- Supplementary Groups: apps

---

## Additional info

Some info
some other info.

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://ixsystems.atlassian.net
"""  # noqa
    )
