{#
  We do this instead of using the "depends_on" because docker does not stop
  waiting until all containers have started and without all containers started,
  we hit the upper limit of mw timeout. This only happens on initial install,
  when the identity is not generated yet.
#}
{% macro entrypoint(values) -%}
until [ -f "{{ values.consts.config_dir }}/setup.done" ]; do
  echo "Waiting for Storj to be setup..."; sleep 5;
done

{%- if values.storj.wallets %}
/entrypoint --operator.wallet-features={{ values.storj.wallets | join(",") }}
{%- else %}
/entrypoint
{%- endif %}
{%- endmacro %}
