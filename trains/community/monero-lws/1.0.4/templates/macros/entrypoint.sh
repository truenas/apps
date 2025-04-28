{% macro entrypoint(values) -%}
#!/bin/sh

set -e

LWS_DIR_PATH="{{ values.consts.monero_lws_path }}/light_wallet_server"
ACCOUNTS_FILE_PATH="{{ values.consts.monero_lws_path }}/.accounts.txt"

mkdir -p "$LWS_DIR_PATH"
touch "$ACCOUNTS_FILE_PATH"

{% for account in values.lws.accounts %}
address="{{ account.address }}"
view_key="{{ account.view_key }}"
restore_height={{ account.restore_height or 0 }}
account_id="$address:$restore_height"

if grep -q "$address" "$ACCOUNTS_FILE_PATH"; then
  if ! grep -q "$account_id" "$ACCOUNTS_FILE_PATH"; then
    echo "Rescanning account $address from block $restore_height"
    monero-lws-admin rescan "$restore_height" "$address"
    sed -i "/$address/d" "$ACCOUNTS_FILE_PATH"
    echo "$account_id" >> "$ACCOUNTS_FILE_PATH"
  fi
else
  echo "Adding account $address"
  monero-lws-admin add_account "$address" "$view_key"
  monero-lws-admin rescan "$restore_height" "$address"
  sed -i '/{{ account.address }}/d' "$ACCOUNTS_FILE_PATH"
  echo "$account_id" >> "$ACCOUNTS_FILE_PATH"
fi
{% endfor %}

echo "Starting monero-lws-daemon"
monero-lws-daemon \
  --db-path "{{ values.consts.monero_lws_path }}/light_wallet_server" \
  "$@"
{%- endmacro %}
