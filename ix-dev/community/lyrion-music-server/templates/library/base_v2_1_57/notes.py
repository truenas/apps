from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

SHORT_LIVED = "short-lived"


@dataclass
class Security:
    header: str
    items: list[str]


class Notes:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._app_name: str = ""
        self._app_train: str = ""
        self._info: list[str] = []
        self._warnings: list[str] = []
        self._deprecations: list[str] = []
        self._security: dict[str, list[Security]] = {}
        self._header: str = ""
        self._body: str = ""
        self._footer: str = ""

        self._auto_set_app_name()
        self._auto_set_app_train()
        self._auto_set_header()
        self._auto_set_footer()

    def _is_enterprise_train(self):
        if self._app_train == "enterprise":
            return True

    def _auto_set_app_name(self):
        app_name = self._render_instance.values.get("ix_context", {}).get("app_metadata", {}).get("title", "")
        self._app_name = app_name or "<app_name>"

    def _auto_set_app_train(self):
        app_train = self._render_instance.values.get("ix_context", {}).get("app_metadata", {}).get("train", "")
        self._app_train = app_train or "<app_train>"

    def _auto_set_header(self):
        self._header = f"# {self._app_name}\n\n"

    def _auto_set_footer(self):
        url = "https://github.com/truenas/apps"
        if self._is_enterprise_train():
            url = "https://ixsystems.atlassian.net"
        footer = "## Bug Reports and Feature Requests\n\n"
        footer += "If you find a bug in this app or have an idea for a new feature, please file an issue at\n"
        footer += f"{url}\n"
        self._footer = footer

    def add_info(self, info: str):
        self._info.append(info)

    def add_warning(self, warning: str):
        self._warnings.append(warning)

    def _prepend_warning(self, warning: str):
        self._warnings.insert(0, warning)

    def add_deprecation(self, deprecation: str):
        self._deprecations.append(deprecation)

    def set_body(self, body: str):
        self._body = body

    def get_pretty_host_mount(self, hm: str) -> tuple[str, bool]:
        hm = hm.rstrip("/")
        mapping = {
            "/dev/bus/usb": "USB Devices",
            "/dev/net/tun": "TUN Device",
            "/dev/snd": "Sound Device",
            "/dev/fuse": "Fuse Device",
            "/dev/uinput": "UInput Device",
            "/dev/dvb": "DVB Devices",
            "/dev/dri": "DRI Device",
            "/dev/kfd": "AMD GPU Device",
            "/etc/os-release": "OS Release File",
            "/etc/group": "Group File",
            "/etc/passwd": "Password File",
            "/etc/hostname": "Hostname File",
            "/var/run/docker.sock": "Docker Socket",
            "/var/run/utmp": "UTMP",
            "/var/run/dbus": "DBus Socket",
            "/run/udev": "Udev Socket",
        }
        if hm in mapping:
            return f"{mapping[hm]} ({hm})", True

        hm = hm + "/"
        starters = ("/dev/", "/proc/", "/sys/", "/etc/", "/lib/")
        if any(hm.startswith(s) for s in starters):
            return hm.rstrip("/"), True

        return "", False

    def get_group_name_from_id(self, group_id: int | str) -> str:
        mapping = {
            0: "root",
            20: "dialout",
            24: "cdrom",
            29: "audio",
            568: "apps",
            999: "docker",
        }
        if group_id in mapping:
            return mapping[group_id]
        return str(group_id)

    def scan_containers(self):
        for name, c in self._render_instance._containers.items():
            if self._security.get(name) is None:
                self._security[name] = []

            if c.restart._policy == "on-failure":
                self._security[name].append(Security(header=SHORT_LIVED, items=[]))

            if c._privileged:
                self._security[name].append(
                    Security(
                        header="Privileged mode is enabled",
                        items=[
                            "Has the same level of control as a system administrator",
                            "Can access and modify any part of your TrueNAS system",
                        ],
                    )
                )

            run_as_sec_items = []
            user, group = c._user.split(":") if c._user else [-1, -1]
            if user in ["0", -1]:
                user = "root" if user == "0" else "unknown"
            if group in ["0", -1]:
                group = "root" if group == "0" else "unknown"
            run_as_sec_items.append(f"User: {user}")
            run_as_sec_items.append(f"Group: {group}")
            groups = [self.get_group_name_from_id(g) for g in c._group_add]
            if groups:
                groups_str = ", ".join(sorted(groups))
                run_as_sec_items.append(f"Supplementary Groups: {groups_str}")
            self._security[name].append(Security("Running user/group(s)", run_as_sec_items))

            if c._ipc_mode == "host":
                self._security[name].append(
                    Security(
                        header="Host IPC namespace is enabled",
                        items=[
                            "Container can access the inter-process communication mechanisms of the host",
                            "Allows communication with other processes on the host under particular circumstances",
                        ],
                    )
                )
            if c._pid_mode == "host":
                self._security[name].append(
                    Security(
                        header="Host PID namespace is enabled",
                        items=[
                            "Container can see and interact with all host processes",
                            "Potential for privilege escalation or process manipulation",
                        ],
                    )
                )
            if c._cgroup == "host":
                self._security[name].append(
                    Security(
                        header="Host cgroup namespace is enabled",
                        items=[
                            "Container shares control groups with the host system",
                            "Can bypass resource limits and isolation boundaries",
                        ],
                    )
                )
            if "no-new-privileges=true" not in c._security_opt.render():
                self._security[name].append(
                    Security(
                        header="Security option [no-new-privileges] is not set",
                        items=[
                            "Processes can gain additional privileges through setuid/setgid binaries",
                            "Can potentially allow privilege escalation attacks within the container",
                        ],
                    )
                )

            host_mounts = []
            for dev in c.devices._devices:
                pretty, _ = self.get_pretty_host_mount(dev.host_device)
                host_mounts.append(f"{pretty} - ({dev.cgroup_perm or 'Read/Write'})")

            for vm in c.storage._volume_mounts:
                if vm.volume_mount_spec.get("type", "") == "bind":
                    source = vm.volume_mount_spec.get("source", "")
                    read_only = vm.volume_mount_spec.get("read_only", False)
                    pretty, is_host_mount = self.get_pretty_host_mount(source)
                    if is_host_mount:
                        host_mounts.append(f"{pretty} - ({'Read Only' if read_only else 'Read/Write'})")

            if host_mounts:
                self._security[name].append(
                    Security(
                        header="Passing Host Files, Devices, or Sockets into the Container", items=sorted(host_mounts)
                    )
                )
            if c._tty:
                self._prepend_warning(
                    f"Container [{name}] is running with a TTY, "
                    "Logs do not appear correctly in the UI due to an [upstream bug]"
                    "(https://github.com/docker/docker-py/issues/1394)"
                )
        self._security = {k: v for k, v in self._security.items() if v}

    def render(self):
        self.scan_containers()

        result = self._header

        if self._warnings:
            result += "## Warnings\n\n"
            for warning in self._warnings:
                result += f"- {warning}\n"
            result += "\n"

        if self._deprecations:
            result += "## Deprecations\n\n"
            for deprecation in self._deprecations:
                result += f"- {deprecation}\n"
            result += "\n"

        if self._info:
            result += "## Info\n\n"
            for info in self._info:
                result += f"- {info}\n"
            result += "\n"

        if self._security:
            result += "## Security\n\n"
            result += "**Read the following security precautions to ensure"
            result += " that you wish to continue using this application.**\n\n"

            def render_security(container_name: str, security: list[Security]) -> str:
                output = "---\n\n"
                output += f"### Container: [{container_name}]"
                if any(sec.header == SHORT_LIVED for sec in security):
                    output += "\n\n**This container is short-lived.**"
                output += "\n\n"
                for sec in [s for s in security if s.header != SHORT_LIVED]:
                    output += f"#### {sec.header}\n\n"
                    for item in sec.items:
                        output += f"- {item}\n"
                    if sec.items:
                        output += "\n"
                return output

            sec_list = []
            sec_short_lived_list = []
            for container_name, security in self._security.items():
                if any(sec.header == SHORT_LIVED for sec in security):
                    sec_short_lived_list.append((container_name, security))
                    continue
                sec_list.append((container_name, security))

            sec_list = sorted(sec_list, key=lambda x: x[0])
            sec_short_lived_list = sorted(sec_short_lived_list, key=lambda x: x[0])

            joined_sec_list = [*sec_list, *sec_short_lived_list]
            for idx, item in enumerate(joined_sec_list):
                container, sec = item
                result += render_security(container, sec)
                # If its the last container, add a final ---
                if idx == len(joined_sec_list) - 1:
                    result += "---\n\n"

        if self._body:
            result += self._body.strip() + "\n\n"

        result += self._footer

        return result
