def migrate_dns_config(dns_config):
    if not dns_config:
        return []

    dns_opts = []
    for opt in dns_config.get("options", []):
        dns_opts.append(f"{opt['name']}:{opt['value']}")

    return dns_opts
