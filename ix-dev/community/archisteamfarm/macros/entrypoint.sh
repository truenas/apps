{% macro entrypoint(values) -%}
#!/bin/sh

echo "Applying IPC Configuration"
cat <<EOF > /app/config/IPC.config
{
	"Kestrel": {
		"Endpoints": {
			"HTTP": {
				"Url": "http://*:1242"
			}
		}
	}
}
EOF

echo "Starting ArchiSteamFarm"
ArchiSteamFarm \
  --no-restart \
  --system-required \
  "$@"
{%- endmacro %}
