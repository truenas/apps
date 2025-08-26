{% macro healthcheck(values) -%}
#!/bin/sh
{% set base_path = "/var/syncthing/config" %}
{# If the db is migrated, use the normal healthcheck #}
if [ -d "{{base_path}}/index-v2" ]; then
    wget --quiet --spider http://127.0.0.1:{{values.network.web_port.port_number}}/rest/noauth/health || exit 1
    exit 0
fi

{#
  Let syncthing migrate the db, in the meantime, report healthy,
  so docker compose up command does not timeout.
#}
if [ -d "{{base_path}}/index-v0.14.0.db" ]; then
    echo "Migrating database, reporting healthy"
    exit 0
fi

{# Something went wrong, report unhealthy #}
echo "Something went wrong, reporting unhealthy"
exit 1
{% endmacro %}
