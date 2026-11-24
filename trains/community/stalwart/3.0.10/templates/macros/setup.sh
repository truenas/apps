{% macro fetch_cli(values) -%}
{%- set ver = values.consts.cli_version %}
{%- set asset = "stalwart-cli-x86_64-unknown-linux-musl" %}
{%- set base = "https://github.com/stalwartlabs/cli/releases/download/%s"|format(ver) %}
{%- set bin = "%s/stalwart-cli"|format(values.consts.cli_dir) -%}
#!/bin/sh
set -eu

if [ -x "{{ bin }}" ] && "{{ bin }}" --version 2>/dev/null | grep -qF "{{ ver[1:] }}"; then
    echo "stalwart-cli {{ ver }} already present at {{ bin }}"
    exit 0
fi

echo "Downloading stalwart-cli {{ ver }}..."
cd /tmp
curl -fsSLo "{{ asset }}.tar.xz" "{{ base }}/{{ asset }}.tar.xz"
curl -fsSLo "{{ asset }}.tar.xz.sha256" "{{ base }}/{{ asset }}.tar.xz.sha256"
grep -F "{{ asset }}.tar.xz" "{{ asset }}.tar.xz.sha256" | sha256sum -c -

echo "Extracting stalwart-cli to {{ values.consts.cli_dir }}..."
tar -xJf "{{ asset }}.tar.xz" -C "{{ values.consts.cli_dir }}" --strip-components=1 "{{ asset }}/stalwart-cli"
chmod 0755 "{{ bin }}"

echo "stalwart-cli installed:"
"{{ bin }}" --version
{%- endmacro %}

{% macro seed(values, listeners) -%}
{%- set cli = "%s/stalwart-cli"|format(values.consts.cli_dir) -%}
#!/bin/bash
set -euo pipefail

# stalwart-cli stores session state under $HOME; give it a writable one (the
# run-as user has no home directory in the image).
export HOME=/tmp

recovery_pass="$(head -c 18 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 24)"
export STALWART_RECOVERY_MODE=1
export STALWART_RECOVERY_ADMIN="admin:${recovery_pass}"

echo "Starting Stalwart in recovery mode to seed configuration..."
/usr/local/bin/stalwart --config "{{ values.consts.config_file }}" &
server_pid=$!

echo "Waiting for the recovery listener on port 8080..."
for _ in $(seq 1 60); do
    if curl -fsS -o /dev/null "http://127.0.0.1:8080/healthz/live"; then
        break
    fi
    sleep 1
done

export STALWART_URL="http://127.0.0.1:8080"
export STALWART_USER="admin"
export STALWART_PASSWORD="${recovery_pass}"

# Create listeners that don't exist yet (with their default TLS mode), and only
# update name/bind/protocol on existing ones so WebUI changes are preserved.
echo "Checking existing listeners..."
existing="$("{{ cli }}" query NetworkListener --fields name --json)"
plan="/tmp/plan.ndjson"
cp "{{ values.consts.plan_file }}" "${plan}"

add_listener() {
    if grep -qF "\"name\":\"$1\"" <<< "${existing}"; then
        echo "Listener $1 exists, updating"
        printf '\n%s' "$3" >> "${plan}"
    else
        echo "Listener $1 is missing, creating"
        printf '\n%s' "$2" >> "${plan}"
    fi
}
{% for l in listeners %}
add_listener '{{ l.name }}' '{{ l.create }}' '{{ l.upsert }}'
{%- endfor %}

echo "Applying configuration plan..."
"{{ cli }}" apply --file "${plan}"

echo "Configuration applied. Stopping recovery server..."
kill "${server_pid}"
wait "${server_pid}" 2>/dev/null || true
echo "Seed phase complete."
{%- endmacro %}
