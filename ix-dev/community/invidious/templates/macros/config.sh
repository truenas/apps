{% macro config(values, cfg=[]) -%}
#!/bin/sh
{%- set cfg_path = "%s/config.yaml"|format(values.consts.config_path) %}
if [ ! -f "{{ cfg_path }}" ]; then
  echo "File [{{ cfg_path }}] does not exist. Exiting..."
  exit 1
fi

echo "Updating [{{ cfg_path }}] file..."
{%- for c in cfg %}
{%- for key, value in c.items() %}
echo "Updating [{{ key }}] key..."
yq -i '.{{ key }} = {{ value }}' "{{ cfg_path }}"
echo "New value for [{{ key }}]: $$(yq '.{{ key }}' "{{ cfg_path }}")"
{%- endfor %}
{%- endfor %}
echo "Done!"

{% endmacro %}
