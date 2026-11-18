{% macro entrypoint(values) -%}
#!/bin/sh

{% set cfg_file_path = "%s/config.toml" | format(values.consts.config_dir_path) %}

mkdir -p "{{ values.consts.config_dir_path }}"
touch "{{ cfg_file_path }}"

sed -i "/auth=/d" "{{ cfg_file_path }}"
echo 'auth="{{ values.electrs.bitcoind_rpc_user }}:{{ values.electrs.bitcoind_rpc_password }}"' >> "{{ cfg_file_path }}"

electrs "$@"
{%- endmacro %}
