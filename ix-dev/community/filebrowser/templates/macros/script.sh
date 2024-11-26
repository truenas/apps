{% macro script(values) -%}
#!/bin/bash
if [ ! -f {{ values.consts.config_path }}/filebrowser.json ]; then
  echo "Filebrowser config file not found at [{{ values.consts.config_path }}/filebrowser.json]. Creating..."
  echo "{}" > {{ values.consts.config_path }}/filebrowser.json
fi
{%- endmacro %}
