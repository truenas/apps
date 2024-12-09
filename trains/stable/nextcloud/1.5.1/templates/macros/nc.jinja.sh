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
set -e
config_file="/var/www/html/config/config.php"
{# Reason for sed: https://github.com/nextcloud/server/issues/44924 #}
echo "Updating database and redis host in config.php"
sed -i "s/\('dbhost' => '\)[^']*postgres:5432',/\1{{ values.consts.postgres_container_name }}:5432',/" "$config_file"
occ config:system:set redis host --value="{{ values.consts.redis_container_name }}"
{%- endmacro -%}
