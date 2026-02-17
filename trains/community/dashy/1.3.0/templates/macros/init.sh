{% macro init(values) -%}
#!/bin/sh
set -e

echo "Checking if directory [{{ values.consts.init_config_path }}] is empty (Mounted at [{{ values.consts.dashy_config_path }}] when app is running)"
if [ -z "$(ls -A {{ values.consts.init_config_path }})" ]; then
  echo "Directory [{{ values.consts.init_config_path }}] is empty, copying from defaults located at [{{ values.consts.dashy_config_path }}] in the container"
  cp -r {{ values.consts.dashy_config_path }}/* {{ values.consts.init_config_path }}
  exit 0
fi
echo "Directory [{{ values.consts.init_config_path }}] is not empty, skipping copy"

{%- endmacro %}
