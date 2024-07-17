from . import utils


def dns_opts(dns_opts=[]):
    if not dns_opts:
        return []

    tracked = {}
    disallowed_opts = []
    for opt in dns_opts:
        key = opt.split(":")[0]
        if key in tracked:
            utils.throw_error(
                f"Expected [dns_opts] to be unique, got [{', '.join([d.split(':')[0] for d in tracked])}]"
            )
        if key in disallowed_opts:
            utils.throw_error(f"Expected [dns_opts] to not contain [{key}] key.")
        tracked[key] = opt

    return dns_opts
