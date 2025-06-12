{% macro setup(tpl, config) %}
#!/bin/bash
set -e

{%- set cfg_path = "/config/settings.json" %}
{%- set tmp_path = "/tmp/settings.json" %}
{%- set redir_cmd = '%s && mv %s "%s" && echo -n " Done!" || { echo -n " Failed."; exit 1; }' | format(tmp_path, tmp_path, cfg_path) %}
if [ ! -f {{ cfg_path }} ]; then
  echo "No settings.json found, exiting"
  exit 1
fi

if [ ! -w {{ cfg_path }} ]; then
  echo "Settings.json is not writable, exiting"
  exit 1
fi

echo -e "\nStarting setup..."

{%- for key, val in config.items() %}
echo -n -e "\t - Setting [{{ key }}] to [{{ tpl.funcs.auto_cast(val) | tojson }}]..."
jq '."{{ key }}" = {{ tpl.funcs.auto_cast(val) | tojson }}' "{{ cfg_path }}" > {{ redir_cmd }}
echo " New value is [$(jq '."{{ key }}"' {{ cfg_path }})]";
{%- endfor %}

echo -e "Finished setup.\n"
{% endmacro %}
