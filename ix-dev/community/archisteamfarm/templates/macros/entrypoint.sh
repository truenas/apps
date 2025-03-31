{% macro entrypoint() %}
#!/usr/bin/env bash
set -e

cp /config/IPC.config /app/config/IPC.config

echo "Starting ArchiSteamFarm..."
exec ArchiSteamFarm --no-restart --system-required
{% endmacro %}
