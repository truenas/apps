{% macro config(values, cfg=[]) -%}
#!/bin/sh
{%- set cfg_path = "%s/config.yaml"|format(values.consts.config_path) %}
echo "Updating [{{ cfg_path }}] file..."

{%- for c in cfg %}
echo "Updating [{{c.key}}] key..."
yq -i '.{{ c.key }} = {{ c.value }}' "{{ cfg_path }}"
echo "New value for [{{c.key}}]: $$(yq '.{{ c.key }}' "{{ cfg_path }}")"
{%- endfor %}
echo "Done!"

{% endmacro %}
