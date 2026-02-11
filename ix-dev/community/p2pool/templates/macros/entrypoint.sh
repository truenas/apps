{% macro entrypoint(values) -%} 
#!/bin/sh

set -e

# This avoids resolving host.docker.internal to ipv6.
# Monerod does not bind the zmq pub port to ipv6 for example, so we'd be unable to connect.
HOST_IP=$(getent ahostsv4 host.docker.internal | awk '{print $1}' | head -n 1)

{% if values.p2pool.use_remote_node %}
  p2pool --host {{ values.p2pool.remote_node_host }} "$@"
{% else %}
  p2pool --host $HOST_IP "$@"
{% endif %}

{%- endmacro %}