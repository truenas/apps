{% macro init(values) -%}
if [ ! -f "{{ values.consts.config_path }}/prometheus.yml" ]; then
  touch "{{ values.consts.config_path }}/prometheus.yml"
fi
{%- endmacro %}
