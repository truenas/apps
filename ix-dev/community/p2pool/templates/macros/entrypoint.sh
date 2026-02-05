{% macro entrypoint(values) -%}
#!/bin/sh

set -e

rm -f params.conf
echo "--host {{ values.p2pool.remote_node_host if values.p2pool.use_remote_node else 'host.docker.internal' }}" >> params.conf
echo "--rpc-port {{ values.p2pool.monerod_rpc_port }}" >> params.conf
echo "--zmq-port {{ values.p2pool.monerod_zmq_pub_port }}" >> params.conf
echo "--wallet {{ values.p2pool.wallet_address }}" >> params.conf

# check if the peers array is not empty
{% set peers = namespace(x=[]) %}
{% for peer in values.p2pool.peers %}
  {% do peers.x.append("%s:%s"|format(peer.host, peer.port)) %}
{% endfor %}
{% if peers.x %}
  echo "--addpeers {{ peers.x | join(',') }}" >> params.conf
{% endif %}

{% if values.network.stratum_port.bind_mode %}
  echo "--stratum 0.0.0.0:{{ values.network.stratum_port.port_number }}" >> params.conf
{% endif %}
{% if values.network.p2p_port.bind_mode %}
  echo "--p2p 0.0.0.0:{{ values.network.p2p_port.port_number }}" >> params.conf
{% endif %}

{% for flag in values.p2pool.additional_flags %}
  echo "{{ flag }}" >> params.conf
{% endfor %}

cat params.conf

echo "Starting p2pool"
p2pool --params-file params.conf
{%- endmacro %}
