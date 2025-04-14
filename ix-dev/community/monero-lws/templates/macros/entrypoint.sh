{% macro entrypoint(values) -%}
#!/bin/sh

set -e

LWS_DIR_PATH="{{ values.consts.monero_lws_path }}/light_wallet_server"
ACCOUNTS_FILE_PATH="{{ values.consts.monero_lws_path }}/.accounts.txt"

mkdir -p $LWS_DIR_PATH
touch $ACCOUNTS_FILE_PATH

{% for account in values.lws.accounts %}
account_id="{{ account.address }}:{{ account.restore_height }}"

if grep -q "{{ account.address }}" $ACCOUNTS_FILE_PATH; then
  if ! grep -q "$account_id" $ACCOUNTS_FILE_PATH; then
    echo "Rescanning account {{ account.address }} from block {{ account.restore_height }}"
    monero-lws-admin rescan {{ account.restore_height }} {{ account.address }}
    sed -i '/{{ account.address }}/d' $ACCOUNTS_FILE_PATH
    echo "$account_id" >> $ACCOUNTS_FILE_PATH    
  fi
else
  echo "Adding account {{ account.address }}"
  monero-lws-admin add_account {{ account.address }} {{ account.view_key }}
  monero-lws-admin rescan {{ account.restore_height }} {{ account.address }}
  sed -i '/{{ account.address }}/d' $ACCOUNTS_FILE_PATH
  echo "$account_id" >> $ACCOUNTS_FILE_PATH
fi
{% endfor %}

echo "Starting monero-lws-daemon"
monero-lws-daemon \
  --db-path "{{ values.consts.monero_lws_path }}/light_wallet_server" \
  "$@"
{%- endmacro %}
