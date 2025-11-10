{% macro app_init(tpl, config) -%}
#!/bin/sh
set -e

{%- for v in ["target_path", "app_id", "source_path"] %}
  {%- if not config[v] %}
    {%- do tpl.funcs.fail("Missing required config value: %s"|format(v)) %}
  {%- endif %}
{%- endfor %}

{%- set app_id = config.app_id %}
{%- set source_path = config.source_path %}
{%- set target_path = config.target_path %}

{%- set app_path = "%s/%s"|format(target_path, app_id) %}
if [ -d {{ app_path }} ]; then
  echo "Removing old app files for [{{ app_id }}] from {{ app_path }}]"
  rm -rf {{ app_path }}
fi

{%- if not config.enabled %}
  echo "App [{{ app_id }}] is disabled, exiting."
  exit 0
{%- endif %}

mkdir -p {{ app_path }}

echo "Copying app files for [{{ app_id }}] to [{{ app_path }}] from [{{ source_path }}]"
cp -R {{ source_path }} {{ target_path }}

echo "Setting ownership to [{{ config.run_as.uid }}:{{ config.run_as.gid }}] for [{{ app_path }}]"
chown -R {{ config.run_as.uid }}:{{ config.run_as.gid }} {{ app_path }}

echo "Done!"
{% endmacro %}
