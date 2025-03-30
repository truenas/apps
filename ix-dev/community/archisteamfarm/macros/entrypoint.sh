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
		},
		"KnownNetworks": [
			"10.0.0.0/8",
			"172.16.0.0/12",
			"192.168.0.0/16"
		]
	}
}
EOF

echo "Starting ArchiSteamFarm"
ArchiSteamFarm \
  --no-restart \
  --system-required \
  "$@"
{%- endmacro %}
