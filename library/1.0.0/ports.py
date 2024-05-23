def port(
    host_port,
    container_port=None,
    protocol=None,
    mode=None,
    host_ip=None,
):
    port = {}
    if host_port > 65535 or host_port < 1:
        raise ValueError(f"Expected port to be between 1 and 65535, got [{host_port}]")
    port["published"] = host_port

    if container_port:
        if container_port > 65535 or container_port < 1:
            raise ValueError(f"Expected container port to be between 1 and 65535, got [{container_port}]")
        port["target"] = container_port
    else:  # If container port is not specified, use the same as host port
        port["target"] = host_port

    if protocol:
        if port not in ["tcp", "udp"]:
            raise ValueError(f"Expected protocol to be tcp or udp, got [{protocol}]")
        port["protocol"] = protocol

    if mode:
        if mode not in ["ingress", "host"]:
            raise ValueError(f"Expected mode to be ingress or host, got [{mode}]")
        port["mode"] = mode

    if host_ip:
        port["host_ip"] = host_ip

    return port
