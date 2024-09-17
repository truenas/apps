from . import utils
from .security import get_caps, get_sec_opts
from .network import dns_opts
from .healthchecks import pg_test, check_health
from .resources import resources


def pg_url(variant, host, user, password, dbname, port=5432):
    if not host:
        utils.throw_error("Expected [host] to be set")
    if not user:
        utils.throw_error("Expected [user] to be set")
    if not password:
        utils.throw_error("Expected [password] to be set")
    if not dbname:
        utils.throw_error("Expected [dbname] to be set")

    if variant == "postgresql":
        return f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=disable"
    elif variant == "postgres":
        return f"postgres://{user}:{password}@{host}:{port}/{dbname}?sslmode=disable"
    else:
        utils.throw_error(
            f"Expected [variant] to be one of [postgresql, postgres], got [{variant}]"
        )


def pg_env(user, password, dbname, port=5432):
    if not user:
        utils.throw_error("Expected [user] to be set for postgres")
    if not password:
        utils.throw_error("Expected [password] to be set for postgres")
    if not dbname:
        utils.throw_error("Expected [dbname] to be set for postgres")
    return {
        "POSTGRES_USER": user,
        "POSTGRES_PASSWORD": utils.escape_dollar(password),
        "POSTGRES_DB": dbname,
        "POSTGRES_PORT": port,
    }


def pg_container(data={}):
    req_keys = ["db_user", "db_password", "db_name", "volumes", "resources"]
    for key in req_keys:
        if not data.get(key):
            utils.throw_error(f"Expected [{key}] to be set for postgres")

    pg_user = data["db_user"]
    pg_password = data["db_password"]
    pg_dbname = data["db_name"]
    pg_port = data.get("port", 5432)
    depends = data.get("depends_on", {})
    depends_on = {}
    for key in depends:
        depends_on[key] = {
            "condition": depends[key].get("condition", "service_completed_successfully")
        }

    return {
        "image": f"{data.get('image', 'postgres:15')}",
        "user": f"{data.get('user', '999')}:{data.get('group', '999')}",
        "restart": "unless-stopped",
        "cap_drop": get_caps()["drop"],
        "security_opt": get_sec_opts(),
        **({"dns_opts": dns_opts(data["dns_opts"])} if data.get("dns_opts") else {}),
        "healthcheck": check_health(pg_test(user=pg_user, db=pg_dbname)),
        "environment": pg_env(
            user=pg_user,
            password=pg_password,
            dbname=pg_dbname,
            port=pg_port,
        ),
        "volumes": data["volumes"],
        "depends_on": depends_on,
        "deploy": {"resources": resources(data["resources"])},
    }
