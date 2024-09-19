{% macro setup(values, config) %}
#!/bin/bash
{%- set cfg_path = "/config/settings.json" %}
{%- set tmp_path = "/tmp/settings.json" %}
{%- set redir_cmd = '%s && mv %s "%s" && echo -n " Done!" || { echo -n " Failed."; exit 1; }' | format(tmp_path, tmp_path, cfg_path) %}
if [ ! -f {{ cfg_path }} ]; then
  echo "No settings.json found, exiting"
  exit 1
fi

{%- for key, value in config.items() %}

echo -n "Setting [{{ key }}] to [{{ value | tojson }}]..."
jq '."{{ key }}" = {{ value | tojson }}' "{{ cfg_path }}" > {{ redir_cmd }}
echo " New value is [$$(jq '."{{ key }}"' {{ cfg_path }})]";
{%- endfor %}

{% endmacro %}
