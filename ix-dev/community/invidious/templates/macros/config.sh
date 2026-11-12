{% macro config(values, cfg=[]) -%}
#!/bin/sh
{%- set cfg_path = "%s/config.yaml"|format(values.consts.config_path) %}
if [ ! -f "{{ cfg_path }}" ]; then
  echo "File [{{ cfg_path }}] does not exist. Creating it..."
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

{% set remove_keys = ["signature_server", "po_token", "visitor_data"] %}
# if signature server values exist from inv-sig-helper, remove them
if $(yq '. | has("signature_server")' "{{ cfg_path }}") = "true"; then
  echo "Found signature server values from old inv-sig-helper installation. Cleaning up..."
  {%- for key in remove_keys %}
    echo "Removing [{{ key }}] key..."
    yq -i 'del(.{{ key }})' "{{ cfg_path }}"
  {%- endfor %}
fi

echo "Done!"
{% endmacro %}
