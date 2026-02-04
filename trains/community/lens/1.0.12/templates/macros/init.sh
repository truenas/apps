{% macro init_script(values) -%}
#!/bin/sh
set -e

echo "Checking if directory [{{ values.consts.init_uploads_path }}] is empty (Mounted at [{{ values.consts.lens_uploads_path }}] when app is running)"
if [ -z "$(ls -A {{ values.consts.init_uploads_path }})" ]; then
  echo "Directory [{{ values.consts.init_uploads_path }}] is empty, copying from defaults located at [{{ values.consts.lens_uploads_path }}] in the container"
  cp -r {{ values.consts.lens_uploads_path }}/* {{ values.consts.init_uploads_path }}
  exit 0
fi
echo "Directory [{{ values.consts.init_uploads_path }}] is not empty, skipping copy"
{%- endmacro %}
