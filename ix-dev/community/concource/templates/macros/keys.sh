{% macro gen_keys(values) -%}
#!/bin/sh

set -e

{% set base_cmd = "/usr/local/concourse/bin/concourse generate-key -t" %}

if [ ! -f "{{ values.consts.keys_path }}/session_signing_key" ]; then
  echo "Generating session signing key..."; {{ base_cmd }} rsa -f {{ values.consts.keys_path }}/session_signing_key
else
  echo "Session signing key already exists."
fi

if [ ! -f "{{ values.consts.keys_path }}/tsa_host_key" ]; then
  echo "Generating TSA host key..."; {{ base_cmd }} ssh -f {{ values.consts.keys_path }}/tsa_host_key
else
  echo "TSA host key already exists."
fi

if [ ! -f "{{ values.consts.keys_path }}/worker_key" ]; then
  echo "Generating worker key..."; {{ base_cmd }} ssh -f {{ values.consts.keys_path }}/worker_key
else
  echo "Worker key already exists."
fi

if [ ! -f "{{ values.consts.keys_path }}/authorized_keys.pub" ]; then
  echo "Creating authorized keys file..."
  touch {{ values.consts.keys_path }}/authorized_keys
fi

worker_key=$(cat {{ values.consts.keys_path }}/worker_key.pub)
if grep -q "$worker_key" {{ values.consts.keys_path }}/authorized_keys.pub; then
  echo "Worker key already exists in authorized keys."
else
  echo "Adding worker key to authorized keys..."
  echo "$worker_key" >> {{ values.consts.keys_path }}/authorized_keys.pub
fi

echo "Done."
{% endmacro %}
