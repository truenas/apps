{% macro entrypoint() -%}
#!/bin/sh
set -e

echo "Copying IPC config..."
cp /config/IPC.config /app/config/IPC.config

echo "Starting ArchiSteamFarm..."
exec ArchiSteamFarm --no-restart --system-required
{%- endmacro %}
