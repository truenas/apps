from base_v1_1_4 import utils


def get_args(data):
    args = []

    if data.get("advertise_exit_node"):
        args.append("--advertise-exit-node")

    reserved_keys = ["--advertise-exit-node", "--hostname", "--authkey"]
    for arg in data.get("extra_args", []):
        for key in reserved_keys:
            if arg.startswith(key):
                utils.throw_error(f"Please use the dedicated field for {key}")
        args.append(arg)
    return " ".join(args)
