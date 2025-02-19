{% macro config_script() -%}
#!/bin/sh

if [ ! -f /home/agent/data/config/config.json ]; then
  echo "Fetching default config..."
  curl -s -o /home/agent/data/config/config.json https://raw.githubusercontent.com/kerberos-io/agent/master/machinery/data/config/config.json
else
  echo "Config already exists. Skipping..."
  exit 0
fi
{%- endmacro %}
