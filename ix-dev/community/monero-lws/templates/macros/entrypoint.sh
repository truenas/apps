{% macro entrypoint(values) -%}
#!/bin/sh

{% for account in values.lws.accounts %}
echo "Adding account {{ account.address }}"
monero-lws-admin add_account "{{ account.address }}" "{{ account.view_key }}"
{% endfor %}

echo "Starting monero-lws-daemon"
monero-lws-daemon \
  --db-path "{{ values.consts.monero_lws_path }}/light_wallet_server" \
  "$@"
{%- endmacro %}
