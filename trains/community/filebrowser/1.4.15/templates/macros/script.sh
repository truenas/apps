{% macro script(values) -%}
#!/bin/sh
{%- set mappings = {
  "%s/filebrowser.json"|format(values.consts.config_path): "%s/settings.json"|format(values.consts.config_path),
  "%s/database.db"|format(values.consts.config_path): "%s/filebrowser.db"|format(values.consts.config_path),
} %}

echo "Migrating FileBrowser configuration files..."

{%- for src, dest in mappings.items() %}
echo "Checking for file at [{{ src }}]..."
[ -f {{ src }} ] && { echo "File found at [{{ src }}], renaming to {{ dest }}"; mv "{{ src }}" "{{ dest }}"; } || echo "File not found at [{{ src }}], no need to migrate."
{%- endfor %}
echo "Migration complete."
{%- endmacro %}
