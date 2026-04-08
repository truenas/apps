{% macro entrypoint(values) %}
if [ ! -f /data/config.yaml ]; then
  echo "Generating default config"
  forgejo-runner generate-config > /data/config.yaml
fi

if [ ! -f /data/.runner ]; then
  echo "Registering the runner"
  forgejo-runner register \
    --config /data/config.yaml \
    --no-interactive \
    --name {{ values.forgejo_runner.runner_name }} \
    --instance {{ values.forgejo_runner.instance_url }} \
    {%- if values.forgejo_runner.runner_labels %}
    --labels {{ values.forgejo_runner.runner_labels | join(",") }} \
    {%- endif %}
    --token {{ values.forgejo_runner.runner_registration_token }} || { echo "Runner failed to register"; exit 1; }
  echo "Runner registered successfully"
else
  echo "Runner register file [/data/.runner] already exists"
  echo "Skipping registration"
  echo "If you want to re-register the runner, please delete the file /data/.runner"
fi
echo -e "\n\n"

echo "Starting the runner"
forgejo-runner daemon --config /data/config.yaml
exit 0
{% endmacro %}
