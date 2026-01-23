{% macro script(values, cfg=[]) -%}
#!/bin/sh
{% set cfg_path = values.consts.config_file_path %}

if [ ! -f "{{ cfg_path }}" ]; then
  echo "File [{{ cfg_path }}] does not exist."
  touch "{{ cfg_path }}"
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

{%- endmacro %}
