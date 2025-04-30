{% macro gen_keys(values) -%}
#!/bin/sh

set -e

{% set base_cmd = "/usr/local/concourse/bin/concourse generate-key -t" %}
{% set signing_key = "%s/session_signing_key" | format(values.consts.keys_path) %}
{% set tsa_host_key = "%s/tsa_host_key" | format(values.consts.keys_path) %}
{% set worker_key = "%s/worker_key" | format(values.consts.keys_path) %}
{% set authorized_keys = "%s/authorized_keys.pub" | format(values.consts.keys_path) %}

if [ ! -f "{{ signing_key }}" ]; then
  echo "Generating session signing key..."; {{ base_cmd }} rsa -f {{ signing_key }}
else
  echo "Session signing key already exists."
fi

if [ ! -f "{{ tsa_host_key }}" ]; then
  echo "Generating TSA host key..."; {{ base_cmd }} ssh -f {{ tsa_host_key }}
else
  echo "TSA host key already exists."
fi

if [ ! -f "{{ worker_key }}" ]; then
  echo "Generating worker key..."; {{ base_cmd }} ssh -f {{ worker_key }}
else
  echo "Worker key already exists."
fi

if [ ! -f "{{ authorized_keys }}" ]; then
  echo "Creating authorized keys file..."
  touch {{ authorized_keys }}
fi

worker_key=$(cat {{ values.consts.keys_path }}/worker_key.pub)
if grep -q "$worker_key" {{ authorized_keys }}; then
  echo "Worker key already exists in authorized keys."
else
  echo "Adding worker key to authorized keys..."
  echo "$worker_key" >> {{ authorized_keys }}
fi

echo "Done."
{% endmacro %}
