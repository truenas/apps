{% macro config(values, cfg=[]) -%}
#!/bin/sh
{%- set cfg_path = values.consts.config_file %}
if [ ! -f "{{ cfg_path }}" ]; then
  echo "File [{{ cfg_path }}] does not exist. Creating a new config file..."
  touch "{{ cfg_path }}"
else
  echo "File [{{ cfg_path }}] exists!"
fi

echo "Updating [{{ cfg_path }}] file..."
{%- for c in cfg %}
{%- for key, value in c.items() %}
echo ''
echo "Updating [{{ key }}] key..."
yq -i '.{{ key }} = {{ value|tojson }}' "{{ cfg_path }}"
echo "New value for [{{ key }}]: $(yq '.{{ key }}' "{{ cfg_path }}")"
{%- endfor %}
{%- endfor %}

echo "Done!"
{% endmacro %}
