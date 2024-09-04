import os
import re
import sys
import math
import yaml
import psutil


TOTAL_MEM = psutil.virtual_memory().total
SINGLE_SUFFIX_REGEX = re.compile(r"^[1-9][0-9]*([EPTGMK])$")
DOUBLE_SUFFIX_REGEX = re.compile(r"^[1-9][0-9]*([EPTGMK])i$")
BYTES_INTEGER_REGEX = re.compile(r"^[1-9][0-9]*$")
EXPONENT_REGEX = re.compile(r"^[1-9][0-9]*e[0-9]+$")
SUFFIX_MULTIPLIERS = {
    "K": 10**3,
    "M": 10**6,
    "G": 10**9,
    "T": 10**12,
    "P": 10**15,
    "E": 10**18,
}
DOUBLE_SUFFIX_MULTIPLIERS = {
    "Ki": 2**10,
    "Mi": 2**20,
    "Gi": 2**30,
    "Ti": 2**40,
    "Pi": 2**50,
    "Ei": 2**60,
}


def transform_memory(memory):
    result = 4096  # Default to 4GB

    if re.match(SINGLE_SUFFIX_REGEX, memory):
        suffix = memory[-1]
        result = int(memory[:-1]) * SUFFIX_MULTIPLIERS[suffix]
    elif re.match(DOUBLE_SUFFIX_REGEX, memory):
        suffix = memory[-2:]
        result = int(memory[:-2]) * DOUBLE_SUFFIX_MULTIPLIERS[suffix]
    elif re.match(BYTES_INTEGER_REGEX, memory):
        result = int(memory)
    elif re.match(EXPONENT_REGEX, memory):
        result = int(float(memory))

    result = math.ceil(result)
    result = min(result, TOTAL_MEM)
    # Convert to Megabytes
    result = result / 1024 / 1024
    return int(result)


CPU_COUNT = os.cpu_count()
NUMBER_REGEX = re.compile(r"^[1-9][0-9]$")
FLOAT_REGEX = re.compile(r"^[0-9]+\.[0-9]+$")
MILI_CPU_REGEX = re.compile(r"^[0-9]+m$")


def transform_cpu(cpu) -> int:
    result = 2
    if NUMBER_REGEX.match(cpu):
        result = int(cpu)
    elif FLOAT_REGEX.match(cpu):
        result = int(math.ceil(float(cpu)))
    elif MILI_CPU_REGEX.match(cpu):
        num = int(cpu[:-1])
        num = num / 1000
        result = int(math.ceil(num))

    if CPU_COUNT is not None:
        # Do not exceed the actual CPU count
        result = min(result, CPU_COUNT)

    return result


def get_image(image):
    if image.get("tag"):
        return f"{image['repository']}:{image['tag']}"
    return image["repository"]


def get_image_pull_policy(image):
    pp = image.get("pullPolicy", "IfNotPresent")
    if pp == "IfNotPresent":
        return "missing"
    if pp == "Always":
        return "always"
    if pp == "Never":
        return "never"


def get_envs(environment_variables):
    envs = {}
    for env in environment_variables:
        envs.update({env["name"]: env["value"]})
    return envs


def get_ports(ports_list):
    ports = []
    for p in ports_list:
        item = f"{p['nodePort']}:{p['containerPort']}"
        item += "tcp" if p.get("protocol", "TCP") == "TCP" else "udp"
        ports.append(item)
    return ports


def get_host_ports(ports_list):
    ports = []
    for port in ports_list:
        ports.append(
            {
                "target": port["containerPort"],
                "published": port["hostPort"],
                "mode": "host",
            }
        )

    return ports


def get_host_path_volumes(host_path_volumes):
    volumes = []

    for hpv in host_path_volumes:
        vol = f"{hpv['hostPath']}:{hpv['mountPath']}"
        if hpv.get("readOnly", False):
            vol += ":ro"
        volumes.append(vol)

    return volumes


def map_ix_volumes_to_host_path(volumes, ix_volumes):
    volumes = []
    for vol in volumes:
        ds = vol.get("datasetName")
        host_path = ix_volumes.get(ds)
        if not host_path:
            raise Exception(f"Could not find host path for dataset [{ds}]")

        volumes.append(f"{host_path}:{vol['mountPath']}")
    return volumes


def get_dns_opt(dns_options):
    if not dns_options:
        return []

    dns_opts = []
    for opt in dns_options.get("options", []):
        dns_opts.append(f"{opt['name']}:{opt['value']}")

    return dns_opts


def get_portal(portal_details):
    node_ip = "0.0.0.0"

    return {
        "name": portal_details.get("portalName", "Web Portal"),
        "scheme": portal_details.get("protocol", "http"),
        "host": (
            node_ip
            if portal_details.get("useNodeIP")
            else portal_details.get("host", node_ip)
        ),
        "port": portal_details.get("port", 80),
        "path": "/",
    }


def get_gpus_and_devices(gpus, system_gpus):
    gpus = gpus or {}
    system_gpus = system_gpus or []

    result = {}
    nvidia_ids = []
    for gpu in gpus.items() if gpus else []:
        kind = gpu[0].lower()  # Kind of gpu (amd, nvidia, intel)
        count = gpu[1]  # Number of gpus user requested

        if count == 0:
            continue

        if "amd" in kind or "intel" in kind:
            result.update({"devices": ["/dev/dri:/dev/dri"]})
        elif "nvidia" in kind:
            sys_gpus = [
                gpu_item
                for gpu_item in system_gpus
                if gpu_item.get("error") is None
                and gpu_item.get("vendor", None) is not None
                and gpu_item.get("vendor", "").upper() == "NVIDIA"
            ]
            for sys_gpu in sys_gpus:
                if count == 0:  # We passed # of gpus that user previously requested
                    break
                guid = sys_gpu.get("vendor_specific_config", {}).get("uuid", "")
                pci_slot = sys_gpu.get("pci_slot", "")
                if not guid or not pci_slot:
                    continue

                nvidia_ids.append(guid)
                count -= 1

    if nvidia_ids:
        nvidia_device = {
            "capabilities": ["gpu"],
            "driver": "nvidia",
            "device_ids": nvidia_ids,
        }
        result.update({"reservations": {"devices": [nvidia_device]}})

    return result


def migrate(values):
    app_name = ""  # FIXME: (The user defined name)
    app_config = values["app_config"]  # FIXME: (The values from questions)
    ix_volumes = values.get("ix_volumes")  # FIXME: (The ix_volumes in the new format)
    system_gpus = values.get("gpu_choices")  # FIXME: (The system gpus)

    # Raise for some stuff that are not implemented yet
    if app_config.get("externalInterfaces", []):
        raise Exception("External interfaces are not supported yet")

    if app_config.get("emptyDirVolumes", []):
        raise Exception("EmptyDir volumes are not supported yet")

    if app_config["workloadType"] in ["Job", "CronJob"]:
        print("Jobs/CronJobs are not supported. Was never exposed", file=sys.stderr)

    if app_config.get("cronSchedule", None):
        print("cronSchedule is not supported. Was never exposed", file=sys.stderr)

    if app_config.get("jobRestartPolicy", None):
        print("jobRestartPolicy is not supported. Was never exposed", file=sys.stderr)

    if app_config["dnsPolicy"]:
        print(
            "DNS Policy cannot be migrated to docker-compose as there is no need for it"
            "Safely ignoring the DNS Policy",
            file=sys.stderr,
        )

    manifest = {"services": {app_name: {}}}
    app_manifest = manifest["services"][app_name]

    app_manifest.update(
        {
            "image": get_image(app_config["image"]),
            "pull_policy": get_image_pull_policy(app_config["image"]),
        }
    )

    if app_config.get("containerCommand", []):
        app_manifest["entrypoint"] = app_config["containerCommand"]

    if app_config.get("containerArgs", []):
        app_manifest["command"] = app_config["containerArgs"]

    if app_config.get("containerEnvironmentVariables", []):
        app_manifest["environment"] = get_envs(
            app_config["containerEnvironmentVariables"]
        )

    if app_config.get("hostNetwork", False):
        app_manifest.update({"network_mode": "host"})

    if app_config.get("portForwardingList", []):
        app_manifest.update({"ports": get_ports(app_config["portForwardingList"])})

    if app_config.get("hostPortsList", []):
        app_manifest.update({"ports": get_host_ports(app_config["hostPortsList"])})

    if app_config.get("securityContext", {}):
        sc = app_config["securityContext"]
        if sc.get("capabilities", []):
            app_manifest.update({"cap_add": sc["capabilities"]})

        if sc.get("enableRunAsUser", False):
            user = sc.get("runAsUser", 568)
            group = sc.get("runAsGroup", 568)
            app_manifest.update({"user": f"{user}:{group}"})

        if sc.get("privileged", False):
            app_manifest.update({"privileged": True})

    if app_config.get("tty", False):
        app_manifest.update({"tty": True})

    if app_config.get("stdin", False):
        app_manifest.update({"stdin": True})

    if app_config.get("livenessProbe", {}).get("command", []):
        hc = {"test": ["CMD", *app_config["livenessProbe"]["command"]]}
        if app_config["livenessProbe"].get("initialDelaySeconds", 0) > 0:
            hc.update(
                {"start_period": app_config["livenessProbe"]["initialDelaySeconds"]}
            )
        if app_config["livenessProbe"].get("periodSeconds", 0) > 0:
            hc.update({"interval": app_config["livenessProbe"]["periodSeconds"]})
        app_manifest.update({"healthcheck": hc})

    if app_config.get("dnsConfig", {}):
        dns_c = app_config["dnsConfig"]
        if dns_c.get("options", []):
            app_manifest.update(
                {"dns_opt": get_dns_opt(app_config["dnsConfig"]["options"])}
            )
        if dns_c.get("searches", []):
            app_manifest.update({"dns_search": dns_c["searches"]})
        if dns_c.get("nameservers", []):
            app_manifest.update({"dns": dns_c["nameservers"]})

    volumes = []
    if app_config.get("hostPathVolumes", []):
        volumes.extend(get_host_path_volumes(app_config["hostPathVolumes"]))

    if app_config.get("volumes", []):
        app_manifest.update(
            {"volumes": map_ix_volumes_to_host_path(app_config["volumes"], ix_volumes)}
        )

    if volumes:
        app_manifest.update({"volumes": volumes})

    limits = {}
    if app_config.get("enableResourceLimits", False):
        if app_config.get("cpuLimit", None):
            limits.update({"cpus": transform_cpu(app_config["cpuLimit"])})
        if app_config.get("memLimit", None):
            limits.update({"memory": transform_memory(app_config["memLimit"])})

    if limits:
        app_manifest.update({"deploy": {"resources": {"limits": limits}}})

    if app_config.get("gpuConfiguration", {}):
        gpus_and_devices = get_gpus_and_devices(
            app_config["gpuConfiguration"].get("gpus"), system_gpus
        )
        if gpus_and_devices.get("devices", []):
            app_manifest.update({"devices": gpus_and_devices["devices"]})
        if gpus_and_devices.get("reservations", {}):
            app_manifest["deploy"]["resources"]["reservations"] = gpus_and_devices[
                "reservations"
            ]

    if app_config.get("enableUIPortal", False):
        app_manifest.update({"x-portals": [get_portal(app_config["portalDetails"])]})

    return manifest


if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit(1)

    if os.path.exists(sys.argv[1]):
        with open(sys.argv[1], "r") as f:
            print(yaml.dump(migrate(yaml.safe_load(f.read()))))


# questions:
#   # Cronjob schedule
#   - variable: cronSchedule
#     label: "Cron Schedule"
#     group: "Workload Details"
#     schema:
#       hidden: true
#       type: cron
#       show_if: [["workloadType", "=", "CronJob"]]
#       default:
#         minute: "5"

#   # Restart Policy
#   - variable: jobRestartPolicy
#     description: "Restart Policy for Job"
#     label: "Restart Policy"
#     group: "Restart Policy"
#     schema:
#       hidden: true
#       type: string
#       default: "OnFailure"
#       show_if: [["workloadType", "!=", "Deployment"]]
#       enum:
#         - value: "OnFailure"
#           description: "Only restart job if it fails"
#         - value: "Never"
#           description: "Never restart job even if it fails"

#   # Networking options
#   - variable: externalInterfaces
#     description: "Add External Interfaces"
#     label: "Add external Interfaces"
#     group: "Networking"
#     schema:
#       type: list
#       items:
#         - variable: interfaceConfiguration
#           description: "Interface Configuration"
#           label: "Interface Configuration"
#           schema:
#             type: dict
#             $ref:
#               - "normalize/interfaceConfiguration"
#             attrs:
#               - variable: hostInterface
#                 description: "Please specify host interface"
#                 label: "Host Interface"
#                 schema:
#                   type: string
#                   required: true
#                   $ref:
#                     - "definitions/interface"
#               - variable: ipam
#                 description: "Define how IP Address will be managed"
#                 label: "IP Address Management"
#                 schema:
#                   type: dict
#                   required: true
#                   attrs:
#                     - variable: type
#                       description: "Specify type for IPAM"
#                       label: "IPAM Type"
#                       schema:
#                         type: string
#                         required: true
#                         enum:
#                           - value: "dhcp"
#                             description: "Use DHCP"
#                           - value: "static"
#                             description: "Use static IP"
#                         show_subquestions_if: "static"
#                         subquestions:
#                           - variable: staticIPConfigurations
#                             label: "Static IP Addresses"
#                             schema:
#                               type: list
#                               items:
#                                 - variable: staticIP
#                                   label: "Static IP"
#                                   schema:
#                                     type: ipaddr
#                                     cidr: true
#                           - variable: staticRoutes
#                             label: "Static Routes"
#                             schema:
#                               type: list
#                               items:
#                                 - variable: staticRouteConfiguration
#                                   label: "Static Route Configuration"
#                                   schema:
#                                     type: dict
#                                     attrs:
#                                       - variable: destination
#                                         label: "Destination"
#                                         schema:
#                                           type: ipaddr
#                                           cidr: true
#                                           required: true
#                                       - variable: gateway
#                                         label: "Gateway"
#                                         schema:
#                                           type: ipaddr
#                                           cidr: false
#                                           required: true

#   - variable: emptyDirVolumes
#     label: "Memory Backed Volumes"
#     description: "Mount memory based temporary volumes for fast access i.e consuming /dev/shm"
#     group: "Storage"
#     schema:
#       type: list
#       items:
#         - variable: emptyDirVolume
#           label: "Memory Backed Volume"
#           schema:
#             type: dict
#             attrs:
#               - variable: mountPath
#                 label: "Mount Path"
#                 description: "Path where temporary path will be mounted inside the pod"
#                 schema:
#                   type: path
#                   required: true
#               - variable: sizeLimit
#                 label: "Size Limit"
#                 description: |
#                   Optional - Size of the memory backed volume.</br>
#                   Format: 100Mi, 1Gi, 2Gi etc
#                 schema:
#                   type: string
#                   valid_chars: "^([+-]?[0-9.]+)([eEinumkKMGTP]*[-+]?[0-9]*)$"
#                   default: "512Mi"
