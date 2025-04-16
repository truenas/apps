{% macro entrypoint(values) -%}
#!/bin/sh

ELECTRS_DIR_PATH="{{ values.consts.electrs_dir_path }}"
CONFIG_FILE_PATH="$ELECTRS_DIR_PATH/config.toml"

mkdir -p $ELECTRS_DIR_PATH
touch $CONFIG_FILE_PATH

sed -i "/auth=/d" $CONFIG_FILE_PATH
echo 'auth="{{ values.electrs.bitcoind_rpc_user }}:{{ values.electrs.bitcoind_rpc_password }}"' >> $CONFIG_FILE_PATH

electrs "$@"
{%- endmacro %}