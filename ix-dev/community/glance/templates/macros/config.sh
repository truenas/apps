{% macro config(values, cfg=[]) -%}
#!/bin/sh
{%- set cfg_path = "%s/glance.yml"|format(values.consts.config_path) %}
if [ ! -f "{{ cfg_path }}" ]; then
  echo "File [{{ cfg_path }}] does not exist. Creating a default config..."
  cp /default.yml "{{ cfg_path }}"
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

result=$(yq '. | has("pages")' "{{ cfg_path }}")
if [ "$result" != "true" ]; then
  echo "No pages key found. Adding an empty one..."
  yq -i '.pages = []' "{{ cfg_path }}"
else
  echo "Pages key already exists."
fi

echo "Done!"
{% endmacro %}
