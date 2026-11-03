{% macro entrypoint(values, disable_lapi, disable_metrics) -%}
#!/bin/bash

cfg="${CONFIG_FILE:-/etc/crowdsec/config.yaml}"

# Copy default files on first start so the pins apply
if [ ! -e /etc/crowdsec/local_api_credentials.yaml ] && [ ! -e /etc/crowdsec/config.yaml ]; then
  echo "Populating configuration directory..."
  rsync -av --ignore-existing /staging/etc/crowdsec/* /etc/crowdsec
fi

# Stop on invalid YAML
for f in "$cfg" "$cfg.local"; do
  if [ -f "$f" ] && ! yq e '.' "$f" >/dev/null; then
    echo "$f is not valid YAML, fix it and restart the app"
    exit 1
  fi
done

# pin <key> <value>: keep <key> at <value> in the config file and stop .local from overriding it
pin() {
  local key="$1"
  local value="$(value="$2" yq -n -o=json 'env(value)')"

  if [ -f "$cfg" ]; then
    if [ "$(yq e -o=json "$key" "$cfg")" != "$value" ]; then
      value="$value" yq e -i "$key = env(value)" "$cfg"
      if [ "$(yq e -o=json "$key" "$cfg")" != "$value" ]; then
        echo "Unable to set $key in $cfg, check that its parent keys are maps"
        exit 1
      fi
      echo "Overrode $key in $cfg with $value, it is managed by the app"
    fi
  fi

  if [ -f "$cfg.local" ]; then
    # Drop the key or a parent that isn't a map
    local drop="del($key)"
    local parent="${key%.*}"

    while [ -n "$parent" ]; do
      drop="del($parent | select(tag != \"!!map\")) | $drop"
      parent="${parent%.*}"
    done

    if [ "$(yq e -o=json "$drop" "$cfg.local")" != "$(yq e -o=json '.' "$cfg.local")" ]; then
      if ! yq e -i "$drop" "$cfg.local"; then
        echo "Unable to remove $key, or a parent that isn't a map, from $cfg.local"
        exit 1
      fi
      echo "Removed $key, or a parent that isn't a map, from $cfg.local, it is managed by the app"
    fi
  fi
}

pin .api.server.enable "{{ "false" if disable_lapi else "true" }}"
pin .api.server.listen_uri "0.0.0.0:{{ values.consts.internal_lapi_port }}"
pin .prometheus.enabled "{{ "false" if disable_metrics else "true" }}"
pin .prometheus.listen_addr "0.0.0.0"
pin .prometheus.listen_port "{{ values.consts.internal_metrics_port }}"
pin .db_config.type "sqlite"
pin .db_config.db_path "/var/lib/crowdsec/data/crowdsec.db"
pin .config_paths.data_dir "/var/lib/crowdsec/data/"

exec /bin/bash /docker_start.sh "$@"
{%- endmacro %}
