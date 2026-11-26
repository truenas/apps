import json
from typing import TYPE_CHECKING, Any

from .config import Config

if TYPE_CHECKING:
    from ix_lib.base import Lib
    from ix_lib.values import Values

DATA_PATH = "/updater/data"
PERMS_CONTAINER_NAME = "permissions"
DDNS_CONTAINER_NAME = "ddns"


def render(lib: "Lib", values: "Values") -> dict[str, Any]:
    tpl = lib.Render(values)
    fn = Config(tpl, values)
    ddns = values["ddns"]
    run_as = values["run_as"]
    web_port = values["network"]["web_port"]

    providers_config = fn.get_providers_config(ddns["config"])

    c1 = tpl.add_container(DDNS_CONTAINER_NAME, "image")
    perm_container = tpl.deps.perms(PERMS_CONTAINER_NAME)
    perms_config = {"uid": run_as["user"], "gid": run_as["group"], "mode": "check"}

    c1.set_user(run_as["user"], run_as["group"])
    if values.get("ci"):
        c1.healthcheck.disable()
    else:
        c1.healthcheck.set_custom_test(["CMD", "/updater/ddns-updater", "healthcheck"])
        c1.healthcheck.set_interval(60)

    c1.environment.add_env("LISTENING_ADDRESS", f":{web_port['port_number']}")
    c1.environment.add_env("DATADIR", DATA_PATH)
    c1.environment.add_env("BACKUP_DIRECTORY", DATA_PATH)
    c1.environment.add_env("PERIOD", ddns["period"])
    c1.environment.add_env("BACKUP_PERIOD", ddns["backup_period"])
    c1.environment.add_env("HTTP_TIMEOUT", ddns["http_timeout"])
    c1.environment.add_env("UPDATE_COOLDOWN_PERIOD", ddns["update_cooldown_period"])
    c1.environment.add_env("SHOUTRRR_ADDRESSES", ",".join(ddns["shoutrrr_addresses"]))
    c1.environment.add_env("PUBLICIP_DNS_TIMEOUT", ddns["public_dns_timeout"])
    for env, category, key in (
        ("PUBLICIP_DNS_PROVIDERS", "PUBLICIP_DNS_PROVIDERS", "public_ip_dns_providers"),
        ("PUBLICIP_HTTP_PROVIDERS", "PUBLICIP_HTTP_PROVIDERS", "public_ip_http_providers"),
        ("PUBLICIPV4_HTTP_PROVIDERS", "PUBLICIPV4_HTTP_PROVIDERS", "public_ipv4_http_providers"),
        ("PUBLICIPV6_HTTP_PROVIDERS", "PUBLICIPV6_HTTP_PROVIDERS", "public_ipv6_http_providers"),
        ("PUBLICIP_FETCHERS", "PUBLICIP_FETCHERS", "public_ip_fetchers"),
    ):
        c1.environment.add_env(env, fn.get_public_ip_providers(category=category, items=ddns[key]))
    c1.environment.add_env("CONFIG", json.dumps(providers_config, sort_keys=True))
    c1.environment.add_user_envs(ddns["additional_envs"])

    c1.add_port(web_port)

    c1.add_storage(DATA_PATH, values["storage"]["data"])
    perm_container.add_or_skip_action("data", values["storage"]["data"], perms_config)

    for store in values["storage"]["additional_storage"]:
        c1.add_storage(store["mount_path"], store)
        perm_container.add_or_skip_action(store["mount_path"], store, perms_config)

    if perm_container.has_actions():
        perm_container.activate()
        c1.depends.add_dependency(PERMS_CONTAINER_NAME, "service_completed_successfully")

    tpl.portals.add(web_port)

    tpl.notes.declare_risk("host_network")

    return tpl.render()
