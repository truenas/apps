{%- macro entrypoint(values) -%}
#!/bin/sh

set -e

EXAMPLE_CONFIG_FILE_PATH="$HOME/xmrig-config.json"
USER_CONFIG_FILE_PATH="$HOME/.config/xmrig.json"

if [ ! -e "$USER_CONFIG_FILE_PATH" ]; then
  mkdir -p "$(dirname "$USER_CONFIG_FILE_PATH")"
  cp $EXAMPLE_CONFIG_FILE_PATH $USER_CONFIG_FILE_PATH
fi

jq_write() {
  jq "$1" "$USER_CONFIG_FILE_PATH" > "$USER_CONFIG_FILE_PATH.tmp" && mv "$USER_CONFIG_FILE_PATH.tmp" "$USER_CONFIG_FILE_PATH"
}

{%- set pool_addr =
  values.xmrig.remote_pool_address
  if values.xmrig.remote_pool_address
  else "host.docker.internal:%s" | format(values.xmrig.local_xmrig_port)
%}

jq_write '.pools[0].url = "{{ pool_addr }}"'

{%- if values.xmrig.pool_username %}
jq_write '.pools[0].user = "{{ values.xmrig.pool_username }}"'
{%- endif %}

{%- if values.xmrig.pool_password %}
jq_write '.pools[0].pass = "{{ values.xmrig.pool_password }}"'
{%- endif %}

{%- if values.xmrig.algorithm %}
jq_write '.pools[0].algo = "{{ values.xmrig.algorithm }}"'
{%- endif %}

{%- if values.xmrig.coin %}
jq_write '.pools[0].coin = "{{ values.xmrig.coin }}"'
{%- endif %}

jq_write '.cpu.enabled = true'
jq_write '.cpu.priority = {{ values.xmrig.cpu_priority }}'
jq_write '.cpu["*"].threads = {{ values.xmrig.cpu_threads }}'
jq_write '.randomx["1gb-pages"] = {{ values.xmrig.use_1gb_huge_pages | lower }}'
jq_write '.randomx.rdmsr = {{ values.xmrig.use_msr_mod | lower }}'

{%- if values.xmrig.use_proxy %}
  {%- set proxy_addr =
    "host.docker.internal:%s" | format(values.xmrig.arti_app_proxy_port)
    if values.xmrig.use_arti_app_proxy
    else "%s:%s" | format(values.xmrig.proxy_host, values.xmrig.proxy_port)
  %}
  jq_write '.pools[0].socks5 = "{{ proxy_addr }}"'
{%- endif %}

jq_write '.["donate-level"] = {{ values.xmrig.donate_percentage }}'

cat $USER_CONFIG_FILE_PATH
xmrig -c $USER_CONFIG_FILE_PATH "$@"

{%- endmacro %}
