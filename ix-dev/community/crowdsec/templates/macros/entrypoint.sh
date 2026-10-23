{% macro entrypoint(values) -%}
#!/bin/bash

cfg="${CONFIG_FILE:-/etc/crowdsec/config.yaml}"

# Copy default files on first start so the pins apply
if [ ! -e /etc/crowdsec/local_api_credentials.yaml ] && [ ! -e /etc/crowdsec/config.yaml ]; then
  echo "Populating configuration directory..."
  rsync -av --ignore-existing /staging/etc/crowdsec/* /etc/crowdsec
fi

# pin <key> <value> [env|strenv]: keep <key> at <value> in the config file and out of its .local overlay
pin() {
  local key="$1"
  local value="$2"
  local func="${3:-env}"

  if [ -f "$cfg" ]; then
    if [ "$(yq e "$key" "$cfg")" != "$value" ]; then
      echo "Overriding $key in $cfg with $value, it is managed by the app"
      value="$value" yq e -i "$key = $func(value)" "$cfg"
    fi
  fi

  if [ -f "$cfg.local" ]; then
    if [ "$(yq e "$key" "$cfg.local")" != "null" ]; then
      echo "Removing $key from $cfg.local, it is managed by the app"
      yq e -i "del($key)" "$cfg.local"
    fi
  fi
}

pin .api.server.enable "{{ (not values.network.disable_lapi) | lower }}"
pin .api.server.listen_uri "0.0.0.0:{{ values.consts.internal_lapi_port }}"
pin .prometheus.enabled "{{ values.network.enable_metrics | lower }}"
pin .prometheus.listen_addr "0.0.0.0"
pin .prometheus.listen_port "{{ values.consts.internal_metrics_port }}"
{% if not values.crowdsec.external_db %}
pin .db_config.type "sqlite"
mkdir -p "$(dirname "$DB_PATH")"
pin .db_config.db_path "$DB_PATH" strenv
{% endif %}
pin .config_paths.data_dir "/var/lib/crowdsec/data/"

exec /bin/bash /docker_start.sh "$@"
{%- endmacro %}
