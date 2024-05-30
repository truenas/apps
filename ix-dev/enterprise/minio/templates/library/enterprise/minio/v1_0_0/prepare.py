from base_v1_0_0.postgres import pg_env, pg_url
from base_v1_0_0 import utils
from base_v1_0_0 import healthchecks


def prepare(values={}):
    minio_container_name = "minio"
    pg_container_name = "postgres"
    logsearch_container_name = "logsearch"

    log_auth_token = utils.secure_string(16)
    log_audit_token = utils.secure_string(16)

    pg_user = "logsearch"
    pg_database = "logsearch"

    result = {
        "containers": [],
        "volumes": [],
        "ports": [
            {"enabled": True, "target": minio_container_name, "host_port": values["app_network"]["api_port"]},
            {"enabled": True, "target": minio_container_name, "host_port": values["app_network"]["console_port"]},
        ],
    }

    minio_vols = []
    multi_mode_items = values["app_minio"].get("multi_mode").get("items")
    for idx, store in enumerate(values["app_storage"]["data_dirs"]):
        minio_vols.append(store["mount_path"])
        # TODO: transform things like host_path_config etc to the correct schema
        result["volumes"].append(
            {
                "enabled": True,
                "name": f"minio_{idx}",
                "type": store["type"],
                "targets": [{"container_name": minio_container_name, "mount_path": store["mount_path"]}],
            }
        )

    minio_container = {
        "enabled": True,
        "name": minio_container_name,
        "image": "minio/minio:RELEASE.2023-12-07T04-16-00Z",
        "user": f"{values['app_minio']['user']}:{values['app_minio']['group']}",
        "command": [
            "server",
            "--address",
            f":{values['app_network']['api_port']}",
            "--console-address",
            f":{values['app_network']['console_port']}",
        ],
        "links": [],
        "depends": [],
        "environment": {
            "MC_HOST_health": f"http://localhost:{values['app_network']['api_port']}",
            "MINIO_ROOT_USER": values["app_minio"]["access_key"],
            "MINIO_ROOT_PASSWORD": values["app_minio"]["secret_key"],
            "MINIO_VOLUMES": " ".join(multi_mode_items or minio_vols),
        },
        "healthcheck": {"test": "mc ready --insecure health"},
    }

    if values["app_minio"].get("server_url", None):
        minio_container["environment"]["MINIO_SERVER_URL"] = values["app_minio"]["server_url"]
    if values["app_minio"].get("console_url", None):
        minio_container["environment"]["MINIO_BROWSER_REDIRECT_URL"] = values["app_minio"]["console_url"]

    if values["app_minio"]["logging"]["quiet"]:
        minio_container["command"].extend(["--quiet"])
    if values["app_minio"]["logging"]["anonymous"]:
        minio_container["command"].extend(["--anonymous"])

    if values["app_network"].get("certificate_id", None):
        certs = values["ixCertificates"][values["app_network"]["certificate_id"]]
        result["configs"] = [
            {
                "enabled": True,
                "name": "private",
                "content": certs["privatekey"],
                "targets": [{"container_name": minio_container_name, "container_path": "/.minio/certs/private.key"}],
            },
            {
                "enabled": True,
                "name": "public",
                "content": certs["certificate"],
                "targets": [{"container_name": minio_container_name, "container_path": "/.minio/certs/public.crt"}],
            },
        ]
        minio_container["environment"].update({"MC_HOST_health": f"https://localhost:{values['app_network']['api_port']}"})

    if values["app_logsearch"]["enabled"]:
        minio_container["command"].extend(["--certs-dir", "/.minio/certs"])
        minio_container["links"].append(logsearch_container_name)
        minio_container["depends"].append({"container_name": logsearch_container_name, "condition": "service_healthy"})
        minio_container["environment"].update(
            {
                "MINIO_AUDIT_WEBHOOK_ENABLE_ix_logsearch": "on",
                "MINIO_AUDIT_WEBHOOK_ENDPOINT_ix_logsearch": f"http://{logsearch_container_name}:8080/api/ingest?token={log_audit_token}",
                "MINIO_LOG_QUERY_AUTH_TOKEN": log_auth_token,
                "MINIO_LOG_QUERY_URL": f"http://{logsearch_container_name}:8080",
            }
        )
        # TODO: transform things like host_path_config etc to the correct schema
        result["volumes"].append(
            {
                "enabled": True,
                "name": "pg_data",
                "type": values["app_logsearch"]["postgres_data"]["type"],
                "targets": [{"container_name": pg_container_name, "mount_path": "/var/lib/postgresql/data"}],
            }
        )

        result["containers"] = [
            {
                "enabled": True,
                "name": pg_container_name,
                "image": "postgres:15",
                "user": "999:999",
                "environment": pg_env(pg_user, values["app_logsearch"]["postgres_password"], pg_database),
                "healthcheck": {"test": healthchecks.pg_test(pg_user, values["app_logsearch"]["postgres_password"], pg_database)},
            },
            {
                "enabled": True,
                "name": logsearch_container_name,
                "image": "minio/operator:v4.5.8",
                "user": f"{values['app_minio']['user']}:{values['app_minio']['group']}",
                "entrypoint": ["/logsearch"],
                "links": [pg_container_name],
                "depends": [{"container_name": pg_container_name, "condition": "service_healthy"}],
                "environment": {
                    "LOGSEARCH_DISK_CAPACITY_GB": values["app_logsearch"]["disk_capacity_gb"],
                    "LOGSEARCH_PG_CONN_STR": pg_url("postgresql", pg_container_name, pg_user, values["app_logsearch"]["postgres_password"], pg_database),
                    "LOGSEARCH_AUDIT_AUTH_TOKEN": log_audit_token,
                    "MINIO_LOG_QUERY_AUTH_TOKEN": log_auth_token,
                },
                "healthcheck": {"test": healthchecks.curl_test("http://localhost:8080/status")},
            },
        ]

    result["containers"].append(minio_container)

    return result
