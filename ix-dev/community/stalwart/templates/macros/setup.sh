{% macro init(values) -%}
#!/bin/bash

{% set cfg_file = values.consts.config_file_path %}
if [ ! -f {{ cfg_file }} ]; then
    echo "Creating a new configuration file at {{ cfg_file }}"
    /usr/local/bin/stalwart --init /opt/stalwart
fi
{%- endmacro %}

{% macro setup(values, cfg) -%}
#!/bin/bash
{%- set cfg_file = values.consts.config_file_path %}
if [ ! -f {{ cfg_file }} ]; then
    echo "Stalwart configuration file not found at {{ cfg_file }}"
    exit 1
fi

{%- set base_cmd = "dasel put --file %s --type" |format(cfg_file) %}
{% set keys = cfg | map(attribute="path") | list %}

echo "Updating configuration file at {{ cfg_file }}"

{% for item in cfg %}
echo "Setting option [{{ item.path }}] to [{{ item.value }}]"
{{ base_cmd }} {{ item.type }} "{{ item.path }}" --value "{{ item.value }}"
{% endfor %}

echo "Configuration file updated successfully at {{ cfg_file }}"
{% endmacro %}
