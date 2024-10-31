from base_v1_1_5 import utils


def get_args(data):
    args = []

    if data.get("advertise_exit_node"):
        args.append("--advertise-exit-node")
    if data.get("webclient"):
        args.append("--webclient=true")

    reserved_keys = ["--advertise-exit-node", "--hostname", "--authkey", "--webclient"]
    for arg in data.get("extra_args", []):
        for key in reserved_keys:
            if arg.startswith(key):
                utils.throw_error(f"Please use the dedicated field for {key}")
        args.append(arg)
    return " ".join(args)
