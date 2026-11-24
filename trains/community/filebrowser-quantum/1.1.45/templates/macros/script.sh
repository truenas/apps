{% macro script(values, cfg=[]) -%}
#!/bin/sh
{% set cfg_path = values.consts.config_file_path %}
{% set legacy_db_path = values.consts.legacy_db_file_path %}

if [ ! -f "{{ cfg_path }}" ]; then
  echo "File [{{ cfg_path }}] does not exist."
  touch "{{ cfg_path }}" || { echo "Failed to create [{{ cfg_path }}] file."; exit 1; }
fi

if [ ! -w "{{ cfg_path }}" ]; then
  echo "File [{{ cfg_path }}] is not writable."
  exit 1
fi

# TODO: Remove once v1 installs are no longer expected to upgrade
migrate_v1_config() {
  echo "Migrating v1 config..."
  # v2 moved the port under [http] and rejects unknown keys
  yq -i 'del(.server.port)' "{{ cfg_path }}"

  # v2 rejects the v1 string form of [server.database]
  if [ "$(yq '.server.database | tag' "{{ cfg_path }}")" = "!!str" ]; then
    echo "Removing legacy [server.database] string..."
    yq -i 'del(.server.database)' "{{ cfg_path }}"
  fi

  # Import the v1 BoltDB into SQLite on first v2 start (no-op once the SQLite db is populated)
  if [ -s "{{ legacy_db_path }}" ]; then
    echo "Found legacy database [{{ legacy_db_path }}], setting [server.database.migrateFrom]..."
    yq -i '.server.database.migrateFrom = "{{ legacy_db_path }}"' "{{ cfg_path }}"
  else
    yq -i 'del(.server.database.migrateFrom)' "{{ cfg_path }}"
  fi
}

echo "Updating [{{ cfg_path }}] file..."
migrate_v1_config
yq -i '.http.port = {{ values.network.web_port.port_number }}' "{{ cfg_path }}"
yq -i '.server.database.path = "{{ values.consts.db_file_path }}"' "{{ cfg_path }}"
yq -i '.server.cacheDir = "{{ values.consts.cache_dir_path }}"' "{{ cfg_path }}"

{%- for store in values.storage.additional_storage %}
# Check if server.sources has the mount path, if not, add it
if [ "$(yq '.server.sources[] | select(.path == "{{ store.mount_path }}")' "{{ cfg_path }}")" = "" ]; then
  echo "Adding source [{{ store.mount_path }}] to server.sources..."
  yq -i '.server.sources += [{"path": "{{ store.mount_path }}", "config": {"defaultEnabled": true}}]' "{{ cfg_path }}"
else
  echo "Source [{{ store.mount_path }}] already exists in server.sources. Skipping..."
fi

{%- endfor %}

echo "Done!"
{%- endmacro %}
