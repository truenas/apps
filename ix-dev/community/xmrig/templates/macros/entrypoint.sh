{% macro entrypoint(values) -%}
#!/bin/sh

set -e

EXAMPLE_CONFIG_FILE_PATH="$HOME/xmrig-config.json"
QUESTIONS_CONFIG_FILE_PATH="$HOME/xmrig-questions.json"
USER_CONFIG_FILE_PATH="$HOME/.config/xmrig.json"

if [ ! -e "$USER_CONFIG_FILE_PATH" ]; then
  mkdir -p "$(dirname "$USER_CONFIG_FILE_PATH")"
  cp $EXAMPLE_CONFIG_FILE_PATH $USER_CONFIG_FILE_PATH
fi

if [ ! -e "$QUESTIONS_CONFIG_FILE_PATH" ]; then
  echo '{}' > "$QUESTIONS_CONFIG_FILE_PATH"
fi

jq_write() {
  jq "$1" "$QUESTIONS_CONFIG_FILE_PATH" > "$QUESTIONS_CONFIG_FILE_PATH.tmp" && mv "$QUESTIONS_CONFIG_FILE_PATH.tmp" "$QUESTIONS_CONFIG_FILE_PATH"
}

if [ "{{ values.xmrig.use_custom_config_file }}" = "False" ]; then
  if [ "{{ values.xmrig.remote_pool_address }}" != '' ]; then
    jq_write '.pools[0].url = "{{ values.xmrig.remote_pool_address }}"'
  else
    jq_write '.pools[0].url = "host.docker.internal:{{ values.xmrig.local_xmrig_port }}"'
  fi

  if [ "{{ values.xmrig.pool_username }}" != '' ]; then
    jq_write '.pools[0].user = "{{ values.xmrig.pool_username }}"'
  fi

  if [ "{{ values.xmrig.pool_password }}" != '' ]; then
    jq_write '.pools[0].pass = "{{ values.xmrig.pool_password }}"'
  fi

  if [ "{{ values.xmrig.algorithm }}" != '' ]; then
    jq_write '.pools[0].algo = "{{ values.xmrig.algorithm }}"'
  fi

  if [ "{{ values.xmrig.coin }}" != '' ]; then
    jq_write '.pools[0].coin = "{{ values.xmrig.coin }}"'
  fi

  jq_write '.cpu.enabled = true'
  jq_write '.cpu.priority = {{ values.xmrig.cpu_priority }}'
  jq_write '.cpu["*"].threads = {{ values.xmrig.cpu_threads }}'
  jq_write '.randomx["1gb-pages"] = {{ values.xmrig.use_1gb_huge_pages | lower }}'
  jq_write '.randomx.rdmsr = {{ values.xmrig.use_msr_mod | lower }}'

  if [ "{{ values.xmrig.use_proxy }}" = "True" ]; then
    if [ "{{ values.xmrig.use_arti_app_proxy }}" = "True" ]; then
      jq_write '.pools[0].socks5 = "host.docker.internal:{{ values.xmrig.arti_app_proxy_port }}"'
    else
      jq_write '.pools[0].socks5 = "{{ values.xmrig.proxy_host }}:{{ values.xmrig.proxy_port }}"'
    fi
  fi

  jq_write '.["donate-level"] = {{ values.xmrig.donate_percentage }}'

  cat $QUESTIONS_CONFIG_FILE_PATH
  xmrig -c $QUESTIONS_CONFIG_FILE_PATH "$@"
else
  xmrig "$@"
fi

{%- endmacro %}