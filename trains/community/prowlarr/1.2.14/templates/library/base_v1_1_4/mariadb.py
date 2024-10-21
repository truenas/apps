from . import utils
from .security import get_caps, get_sec_opts
from .network import dns_opts
from .healthchecks import mariadb_test, check_health
from .resources import resources


def mariadb_env(user, password, root_password, dbname):
    if not user:
        utils.throw_error("Expected [user] to be set for mariadb")
    if not password:
        utils.throw_error("Expected [password] to be set for mariadb")
    if not root_password:
        utils.throw_error("Expected [root_password] to be set for mariadb")
    if not dbname:
        utils.throw_error("Expected [dbname] to be set for mariadb")
    return {
        "MARIADB_USER": user,
        "MARIADB_PASSWORD": utils.escape_dollar(password),
        "MARIADB_ROOT_PASSWORD": utils.escape_dollar(root_password),
        "MARIADB_DATABASE": dbname,
        "MARIADB_AUTO_UPGRADE": "true",
    }


def mariadb_container(data={}):
    req_keys = [
        "db_user",
        "db_password",
        "db_root_password",
        "db_name",
        "volumes",
        "resources",
    ]
    for key in req_keys:
        if not data.get(key):
            utils.throw_error(f"Expected [{key}] to be set for mariadb")

    db_user = data["db_user"]
    db_password = data["db_password"]
    db_root_password = data["db_root_password"]
    db_name = data["db_name"]
    db_port = data.get("port", 3306)
    depends = data.get("depends_on", {})
    depends_on = {}
    for key in depends:
        depends_on[key] = {
            "condition": depends[key].get("condition", "service_completed_successfully")
        }

    return {
        "image": f"{data.get('image', 'mariadb:10.6')}",
        "user": f"{data.get('user', '999')}:{data.get('group', '999')}",
        "restart": "unless-stopped",
        "cap_drop": get_caps()["drop"],
        "security_opt": get_sec_opts(),
        **({"dns_opts": dns_opts(data["dns_opts"])} if data.get("dns_opts") else {}),
        "healthcheck": check_health(mariadb_test(db=db_name, config={"port": db_port})),
        "command": [
            "--port",
            str(db_port),
        ],
        "environment": mariadb_env(
            user=db_user,
            password=db_password,
            root_password=db_root_password,
            dbname=db_name,
        ),
        "volumes": data["volumes"],
        "depends_on": depends_on,
        "deploy": {"resources": resources(data["resources"])},
    }
