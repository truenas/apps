from . import utils
from .security import get_caps, get_sec_opts
from .network import dns_opts
from .healthchecks import redis_test, check_health
from .resources import resources


def redis_container(data={}):
    req_keys = ["password", "volumes", "resources"]
    for key in req_keys:
        if not data.get(key):
            utils.throw_error(f"Expected [{key}] to be set for postgres")

    redis_password = data["password"]
    redis_port = data.get("port", 6379)
    depends = data.get("depends_on", {})
    depends_on = {}
    for key in depends:
        depends_on[key] = {
            "condition": depends[key].get("condition", "service_completed_successfully")
        }

    return {
        "image": f"{data.get('image', 'bitnami/redis:7.0.11')}",
        "user": f"{data.get('user', '1001')}:{data.get('group', '0')}",
        "restart": "unless-stopped",
        "cap_drop": get_caps()["drop"],
        "security_opt": get_sec_opts(),
        **({"dns_opts": dns_opts(data["dns_opts"])} if data.get("dns_opts") else {}),
        "healthcheck": check_health(redis_test(config={"port": redis_port})),
        "environment": redis_env(
            password=redis_password,
            port=redis_port,
        ),
        "volumes": data["volumes"],
        "depends_on": depends_on,
        "deploy": {"resources": resources(data["resources"])},
    }


def redis_env(password, port=6379):
    if not password:
        utils.throw_error("Expected [password] to be set for redis")

    return {
        "ALLOW_EMPTY_PASSWORD": "no",
        "REDIS_PASSWORD": utils.escape_dollar(password),
        "REDIS_PORT_NUMBER": port,
    }
