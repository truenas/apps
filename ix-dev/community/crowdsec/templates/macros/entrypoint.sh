{% macro entrypoint(cfg) -%}
#!/bin/bash

# Stop on the first failure
set -e

config_file=/etc/crowdsec/config.yaml

if [ ! -e /etc/crowdsec/local_api_credentials.yaml ] && [ ! -e "$config_file" ]; then
  # Copy default files on first start
  echo "Populating configuration directory..."
  rsync -av --ignore-existing /staging/etc/crowdsec/* /etc/crowdsec
else
  # Only restore a missing config or credentials file, other files may have been removed on purpose
  rsync -a --ignore-existing --out-format="Restored missing /etc/crowdsec/%n from the defaults" \
    /staging/etc/crowdsec/{config,local_api_credentials}.yaml /etc/crowdsec
fi

echo "Updating [$config_file] file..."
{%- for key, value in cfg.items() %}
echo 'Setting [{{ key }}] to [{{ value|tojson }}]...'
yq -i '.{{ key }} = {{ value|tojson }}' "$config_file"
{%- endfor %}

# CrowdSec merges config.yaml.local over config.yaml, so it must not override these keys
if [ -f "$config_file.local" ]; then
  echo "Removing app managed keys from [$config_file.local] file..."
{%- for key in cfg %}
  yq -i 'del(.{{ key }})' "$config_file.local"
{%- endfor %}
fi

exec /bin/bash /docker_start.sh "$@"
{%- endmacro %}
