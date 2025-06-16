{% macro setup(values) -%}
#!/bin/bash

{%- set cfg_file = "%s/garage.toml" | format(values.consts.config_path) %}
if [ ! -f {{ cfg_file }} ]; then
    echo "Creating a new configuration file at {{ cfg_file }}"
    touch {{ cfg_file }}
fi

echo "Updating configuration file at {{ cfg_file }}"

{%- set base_cmd = "dasel put --file %s --type" |format(cfg_file) %}
{%- for item in values.garage.additional_options %}
{{ base_cmd }} {{ item.type }} "{{ item.path }}" --value "{{ item.value }}"
{%- endfor %}

{{ base_cmd }} int ".replication_factor" --value 1
{{ base_cmd }} string ".metadata_dir" --value "{{ values.consts.metadata_path }}"
{{ base_cmd }} string ".data_dir" --value "{{ values.consts.data_path }}"
{{ base_cmd }} string ".metadata_snapshots_dir" --value "{{ values.consts.metadata_snapshots_path }}"

{{ base_cmd }} string ".rpc_bind_addr" --value "0.0.0.0:{{ values.network.rpc_port.port_number }}"

{{ base_cmd }} string ".s3_api.api_bind_addr" --value "0.0.0.0:{{ values.network.s3_port.port_number }}"
{{ base_cmd }} string ".s3_api.s3_region" --value "{{ values.garage.region }}"

{{ base_cmd }} string ".s3_web.bind_addr" --value "0.0.0.0:{{ values.network.s3_web_port.port_number }}"
{{ base_cmd }} string ".s3_web.root_domain" --value "{{ values.garage.s3_web_root_domain }}"

{{ base_cmd }} string ".admin.api_bind_addr" --value "0.0.0.0:{{ values.network.admin_port.port_number }}"

echo "Configuration file updated successfully at {{ cfg_file }}"
{% endmacro %}
