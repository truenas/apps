{% macro gen_keys(values) -%}
#!/bin/sh

set -e

{%- set base_cmd = "/usr/local/concourse/bin/concourse generate-key -t" %}
{%- set signing_key = "%s/session_signing_key" | format(values.consts.keys_path) %}
{%- set tsa_host_key = "%s/tsa_host_key" | format(values.consts.keys_path) %}
{%- set worker_key = "%s/worker_key" | format(values.consts.keys_path) %}
{%- set authorized_keys = "%s/authorized_keys.pub" | format(values.consts.keys_path) %}

[ ! -f "{{ signing_key }}" ] \
  && { echo "Generating session signing key..."; {{ base_cmd }} rsa -f {{ signing_key }}; } \
  || echo "Session signing key already exists."

[ ! -f "{{ tsa_host_key }}" ] \
  && { echo "Generating TSA host key..."; {{ base_cmd }} ssh -f {{ tsa_host_key }}; } \
  || echo "TSA host key already exists."

[ ! -f "{{ worker_key }}" ] \
  && { echo "Generating worker key..."; {{ base_cmd }} ssh -f {{ worker_key }}; } \
  || echo "Worker key already exists."

[ ! -f "{{ authorized_keys }}" ] \
  && { echo "Creating authorized keys file..."; touch {{ authorized_keys }}; } \
  || echo "Authorized keys file already exists."

worker_key=$(cat {{ worker_key }}.pub)
grep -q "$worker_key" {{ authorized_keys }} \
  && echo "Worker key already exists in authorized keys." \
  || { echo "Adding worker key to authorized keys..."; echo "$worker_key" >> {{ authorized_keys }}; }

echo "Done."
{% endmacro %}
