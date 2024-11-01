from . import utils


def dns_opts(dns_options=None):
    dns_options = dns_options or []
    if not dns_options:
        return []

    tracked = {}
    disallowed_opts = []
    for opt in dns_options:
        key = opt.split(":")[0]
        if key in tracked:
            utils.throw_error(
                f"Expected [dns_opts] to be unique, got [{', '.join([d.split(':')[0] for d in tracked])}]"
            )
        if key in disallowed_opts:
            utils.throw_error(f"Expected [dns_opts] to not contain [{key}] key.")
        tracked[key] = opt

    return dns_options
