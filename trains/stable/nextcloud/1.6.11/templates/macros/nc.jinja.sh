{% macro occ(values) -%}
#!/bin/bash
uid="$(id -u)"
gid="$(id -g)"
if [ "$uid" = "0" ]; then
  user='www-data'
  group='www-data'
else
  user="$uid"
  group="$gid"
fi
run_as() {
  if [ "$(id -u)" = "0" ]; then
    su -p "$user" -s /bin/bash -c "php /var/www/html/occ $(printf '%q ' "$@")"
  else
    /bin/bash -c "php /var/www/html/occ $(printf '%q ' "$@")"
  fi
}
run_as "$@"
{%- endmacro -%}

{% macro hosts_update(values) -%}
#!/bin/bash
config_file="/var/www/html/config/config.php"
{# Reason for sed: https://github.com/nextcloud/server/issues/44924 #}
echo "Updating database and redis host in config.php"
sed -i "s/\('dbhost' => '\)[^']*postgres:5432',/\1{{ values.consts.postgres_container_name }}:5432',/" "$config_file" || { echo "Failed to update database host. Exiting..."; exit 1; }
occ config:system:set redis host --value="{{ values.consts.redis_container_name }}" || { echo "Failed to update redis host. Continuing..."; exit 0; }
{%- endmacro -%}

{% macro trusted_domains_update() -%}
#!/bin/bash
set_list() {
  list_name="${1:?"list_name is unset"}"
  space_delimited_values="${2:?"space_delimited_values is unset"}"

  # Get current list
  current_list="$(occ config:system:get "$list_name")"
  # Convert newline separated values to space separated
  current_list="$(echo "$current_list" | tr '\n' ' ')"
  # Merge current list with new values
  merged_list="$(echo "$current_list $space_delimited_values" | tr ' ' '\n' | xargs -I{} echo {})"
  # Remove duplicate values
  merged_list="$(echo "$merged_list" | tr ' ' '\n' | sort -u | tr '\n' ' ')"

  if [ -n "${merged_list}" ]; then
    # Remove current list, so we can replace it with the new one
    occ config:system:delete "$list_name" || return

    IDX=0
    # Replace spaces with newlines so the input can have
    # mixed entries of space or new line separated values
    echo "$merged_list" | tr ' ' '\n' | while IFS= read -r value; do
        # Skip empty values
        if [ -z "$value" ]; then
          continue
        fi

        occ config:system:set "$list_name" $IDX --value="$value"

        IDX=$((IDX+1))
    done
  fi
}

echo "Updating trusted domains. It will append new domains to the existing list."
echo "If you see a domain that is not longer valid, you need to manually remove it from the list in the config.php file."

set_list "trusted_domains" "${NEXTCLOUD_TRUSTED_DOMAINS}" || { echo "Failed to update trusted domains. Continuing..."; exit 0; }

{%- endmacro -%}

{% macro imaginary_url(host, port) -%}
#!/bin/bash
echo '## Configuring Imaginary...'
occ config:system:set preview_imaginary_url --value={{ "http://%s:%d"|format(host, port) }}
{%- endmacro -%}
