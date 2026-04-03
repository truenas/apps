{% macro grafana_import(values) -%}
#!/bin/sh
set -e

GRAFANA_URL="{{ values.grafana.url | trim('/') }}"
GRAFANA_API_TOKEN="{{ values.grafana.api_token }}"
DB_HOST="{{ values.grafana.db_host if values.grafana.db_host else values.consts.postgres_container_name }}"
DB_PORT="{{ values.grafana.db_port }}"
DB_SSL="{{ values.grafana.db_ssl_mode }}"
TESLAMATE_VERSION="{{ values.images.image.tag }}"

# Wait for Grafana to be reachable
echo "Waiting for Grafana at ${GRAFANA_URL}..."
until curl -sf -o /dev/null "${GRAFANA_URL}/api/health"; do
  echo "Grafana not ready, retrying in 5s..."
  sleep 5
done
echo "Grafana is ready."

# Create or update the TeslaMate PostgreSQL datasource.
# Try POST first (create); if it fails (already exists), fall back to PUT (update).
echo "Configuring TeslaMate datasource..."
DATASOURCE_PAYLOAD="{\"name\":\"TeslaMate\",\"type\":\"postgres\",\"access\":\"proxy\",\"url\":\"${DB_HOST}:${DB_PORT}\",\"user\":\"{{ values.consts.db_user }}\",\"database\":\"{{ values.consts.db_name }}\",\"secureJsonData\":{\"password\":\"{{ values.teslamate.db_password }}\"},\"jsonData\":{\"sslmode\":\"${DB_SSL}\",\"postgresVersion\":1500,\"timescaledb\":false},\"isDefault\":true}"

curl -sf -X POST \
  -H "Authorization: Bearer ${GRAFANA_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "${DATASOURCE_PAYLOAD}" \
  "${GRAFANA_URL}/api/datasources" \
  || curl -sf -X PUT \
  -H "Authorization: Bearer ${GRAFANA_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "${DATASOURCE_PAYLOAD}" \
  "${GRAFANA_URL}/api/datasources/name/TeslaMate"
echo "Datasource configured."

# Create TeslaMate folder with a fixed UID for idempotent re-runs.
echo "Creating TeslaMate folder..."
curl -sf -X POST \
  -H "Authorization: Bearer ${GRAFANA_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"uid\":\"teslamate\",\"title\":\"TeslaMate\"}" \
  "${GRAFANA_URL}/api/folders" \
  || echo "Folder already exists, continuing..."

# Fetch dashboard list from GitHub and import each one.
BASE_RAW="https://raw.githubusercontent.com/teslamate-org/teslamate/v${TESLAMATE_VERSION}/grafana/dashboards"
API_CONTENTS="https://api.github.com/repos/teslamate-org/teslamate/contents/grafana/dashboards?ref=v${TESLAMATE_VERSION}"

echo "Fetching dashboard list for TeslaMate v${TESLAMATE_VERSION}..."
DASHBOARDS=$(curl -sf "${API_CONTENTS}" \
  | grep '"name"' \
  | grep '\.json"' \
  | sed 's/.*"name": "\([^"]*\.json\)".*/\1/')

if [ -z "${DASHBOARDS}" ]; then
  echo "ERROR: Could not fetch dashboard list from GitHub. Check internet access and the TeslaMate version."
  exit 1
fi

for DASHBOARD in ${DASHBOARDS}; do
  echo "Importing dashboard: ${DASHBOARD}..."
  DASHBOARD_JSON=$(curl -sf "${BASE_RAW}/${DASHBOARD}") \
    || { echo "WARNING: Could not fetch ${DASHBOARD}, skipping."; continue; }

  curl -sf -X POST \
    -H "Authorization: Bearer ${GRAFANA_API_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"dashboard\":${DASHBOARD_JSON},\"folderUid\":\"teslamate\",\"overwrite\":true}" \
    "${GRAFANA_URL}/api/dashboards/import" \
    || echo "WARNING: Failed to import ${DASHBOARD}"
done

echo "All TeslaMate dashboards imported successfully."
{%- endmacro %}
