{% macro script(values, cfg=[]) -%}
#!/bin/sh
{% set cfg_path = values.consts.config_file_path %}

if [ ! -f "{{ cfg_path }}" ]; then
  echo "File [{{ cfg_path }}] does not exist."
  touch "{{ cfg_path }}"
fi

echo "Updating [{{ cfg_path }}] file..."
yq -i '.server.port = {{ values.network.web_port.port_number }}' "{{ cfg_path }}"
yq -i '.server.database = "{{ values.consts.db_file_path }}"' "{{ cfg_path }}"
yq -i '.server.cacheDir = "{{ values.consts.cache_dir_path }}"' "{{ cfg_path }}"

{%- for store in values.storage.additional_storage %}
# Check if server.sources has the mount path, if not, add it
if [ "$(yq '.server.sources[] | select(.path == "{{ store.mount_path }}")' "{{ cfg_path }}")" = "" ]; then
  echo "Adding source [{{ store.mount_path }}] to server.sources..."
  yq -i '.server.sources += [{"path": "{{ store.mount_path }}"}]' "{{ cfg_path }}"
else
  echo "Source [{{ store.mount_path }}] already exists in server.sources. Skipping..."
fi

{%- endfor %}

echo "Done!"
{%- endmacro %}
