{% macro config_script() -%}
#!/bin/sh

if [ ! -f /home/agent/data/config/config.json ]; then
  echo "Fetching default config..."
  curl --output /home/agent/data/config/config.json https://raw.githubusercontent.com/kerberos-io/agent/master/machinery/data/config/config.json
  exit 0
else
  echo "Config already exists. Skipping..."
  exit 0
fi
{%- endmacro %}
