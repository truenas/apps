{% macro setup(values) -%}
#!/bin/bash
set -e

# The /config volume hides the folder that the image creates.
# The app creates the database file, but not its folder.
# Root has no DAC_OVERRIDE here, so mkdir runs as the app user.
echo "Making sure [{{ values.consts.database_dir }}] exists"
s6-setuidgid abc mkdir -p "{{ values.consts.database_dir }}"
{% endmacro %}
