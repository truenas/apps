{% macro script(values) -%}
#!/bin/sh
{% set mappings = {
  "%s/filebrowser.json"|format(values.consts.config_path): "%s/settings.json"|format(values.consts.config_path),
  "%s/database.db"|format(values.consts.config_path): "%s/filebrowser.db"|format(values.consts.config_path)
} %}

{% for src, dest in mappings.items() %}
[ -f {{ src }} ] && {echo "File found at [{{ src }}], renaming to {{ dest }}"; mv {{ src }} {{ dest }}; }
{% endfor %}
{%- endmacro %}
