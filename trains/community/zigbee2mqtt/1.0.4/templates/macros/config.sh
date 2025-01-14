{% macro config_macro(values) -%}
#!/bin/sh
{%- set cfg_path = "%s/configuration.yaml"|format(values.consts.data_path) %}
if [ ! -f "{{ cfg_path }}" ]; then
  echo "File [{{ cfg_path }}] does not exist."
  exit 0
else
  echo "File [{{ cfg_path }}] exists!"
fi

frontend_value=$(yq '.frontend' {{ cfg_path }})
# Frontend variables will fail to set if the frontend key is set as boolean.
# It expects to be an object, so we set it as an empty object and let variables apply.
if [ "$frontend_value" = "true" ] || [ "$frontend_value" = "false" ]; then
  echo "Frontend value is set as boolean [$frontend_value]."
  echo "Setting as empty object."
  yq -i '.frontend = {}' {{ cfg_path }}
fi
{% endmacro %}
