{% macro setup(tpl, values, cfg) -%}
#!/bin/bash

{%- set cfg_file = "%s/garage.toml" | format(values.consts.config_path) %}
if [ ! -f {{ cfg_file }} ]; then
    echo "Creating a new configuration file at {{ cfg_file }}"
    touch {{ cfg_file }}
fi

{%- set base_cmd = "dasel put --file %s --type" |format(cfg_file) %}
{% set keys = cfg | map(attribute="path") | list %}

echo "Updating configuration file at {{ cfg_file }}"

{% for item in cfg %}
echo "Setting option [{{ item.path }}] to [{{ item.value }}]"
{{ base_cmd }} {{ item.type }} "{{ item.path }}" --value "{{ item.value }}"
{% endfor %}

{%- for item in values.garage.additional_options %}
{% if item.path in keys %}
  {% do tpl.funcs.fail("Option [%s] cannot be overridden" |format(item.path)) %}
{% endif %}
echo "Setting additional option [{{ item.path }}] to [{{ item.value }}]"
{{ base_cmd }} {{ item.type }} "{{ item.path }}" --value "{{ item.value }}"
{%- endfor %}

echo "Configuration file updated successfully at {{ cfg_file }}"
{% endmacro %}
