{% macro set_option(tpl, cfg_file, item) -%}
{%- set value = item.value | string if item.type == "string" else tpl.funcs.auto_cast(item.value) %}
{%- set expr = "%s = %s" | format(item.path, value | tojson) %}
yq -i -p toml -o toml '{{ expr | replace("'", "'\\''") }}' "{{ cfg_file }}"
{%- endmacro %}

{% macro setup(tpl, values, cfg) -%}
#!/bin/bash
set -e

{%- set cfg_file = "%s/garage.toml" | format(values.consts.config_path) %}
if [ ! -f {{ cfg_file }} ]; then
    echo "Creating a new configuration file at {{ cfg_file }}"
    touch {{ cfg_file }}
fi

{% set keys = cfg | map(attribute="path") | list %}

echo "Updating configuration file at {{ cfg_file }}"

{% for item in cfg %}
echo "Setting option [{{ item.path }}] to [{{ item.value }}]"
{{ set_option(tpl, cfg_file, item) }}
{% endfor %}

{%- for item in values.garage.additional_options %}
{% if item.path in keys %}
  {% do tpl.funcs.fail("Option [%s] cannot be overridden" |format(item.path)) %}
{% endif %}
echo "Setting additional option [{{ item.path }}] to [{{ item.value }}]"
{{ set_option(tpl, cfg_file, item) }}
{%- endfor %}

echo "Configuration file updated successfully at {{ cfg_file }}"
{% endmacro %}
