from base_v1_0_4 import utils


def get_args(data):
    args = []

    if data.get("advertise_exit_node"):
        args.append("--advertise-exit-node")

    reserved_keys = ["--advertise-exit-node", "--hostname"]
    for arg in data.get("extra_args", []):
        for key in reserved_keys:
            if arg.startswith(key):
                utils.throw_error(f"Please use the dedicated field for {key}")
        args.append(arg)
    return " ".join(args)


def validate(values):
    key = values.get("tailscale", {}).get("auth_key") or ""
    if not key.startswith("tskey-"):
        utils.throw_error(
            f"The auth key must start with 'tskey-', but starts with '{key[:8]}'"
        )
