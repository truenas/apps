{% macro entrypoint(values) -%}
#!/bin/sh

{% for account in values.lws.accounts %}
monero-lws-admin add_account "{{ account.address }}" "{{ account.view_key }}"
{% endfor %}

monero-lws-daemon --db-path={{ values.consts.monero_lws_path }}/light_wallet_server "$@"
{%- endmacro %}
