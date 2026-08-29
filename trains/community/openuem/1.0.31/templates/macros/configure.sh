{% macro configure() -%}
#!/bin/sh
set -e

{# Run the actual entrypoint #}
/bin/configure.sh

{# Console #}
cp /certificates/console/console.key /console-certs/console.key
cp /certificates/console/console.cer /console-certs/console.cer
cp /certificates/console/sftp.key /console-certs/sftp.key
cp /certificates/ca/ca.cer /console-certs/ca.cer

{# OCSP #}
cp /certificates/ocsp/ocsp.cer /ocsp-certs/ocsp.cer
cp /certificates/ocsp/ocsp.key /ocsp-certs/ocsp.key
cp /certificates/ca/ca.cer /ocsp-certs/ca.cer

{# Notification Worker #}
cp /certificates/notification-worker/worker.cer /notification-worker-certs/worker.cer
cp /certificates/notification-worker/worker.key /notification-worker-certs/worker.key
cp /certificates/ca/ca.cer /notification-worker-certs/ca.cer

{# Cert Manager Worker #}
cp /certificates/cert-manager-worker/worker.cer /cert-manager-worker-certs/worker.cer
cp /certificates/cert-manager-worker/worker.key /cert-manager-worker-certs/worker.key
cp /certificates/ca/ca.cer /cert-manager-worker-certs/ca.cer
cp /certificates/ca/ca.key /cert-manager-worker-certs/ca.key

{# Agents Worker #}
cp /certificates/agents-worker/worker.cer /agents-worker-certs/worker.cer
cp /certificates/agents-worker/worker.key /agents-worker-certs/worker.key
cp /certificates/ca/ca.cer /agents-worker-certs/ca.cer

{# NATS Server #}
cp /certificates/nats/nats.cer /nats-certs/nats.cer
cp /certificates/nats/nats.key /nats-certs/nats.key
cp /certificates/ca/ca.cer /nats-certs/ca.cer
{%- endmacro %}
