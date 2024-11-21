{% macro config(values, cfg=[]) -%}
#!/bin/sh
{%- set cfg_path = "%s/config.yaml"|format(values.consts.config_path) %}
if [ ! -f "{{ cfg_path }}" ]; then
  echo "File [{{ cfg_path }}] does not exist. Copying default config..."
  cp -v "/shared/config.example.yaml" "{{ cfg_path }}"
else
  echo "File [{{ cfg_path }}] exists!"
fi

echo "Updating [{{ cfg_path }}] file..."
{%- for c in cfg %}
{%- for key, value in c.items() %}
echo ''
echo "Updating [{{ key }}] key..."
yq -i '.{{ key }} = {{ value|tojson }}' "{{ cfg_path }}"
echo "New value for [{{ key }}]: $(yq '.{{ key }}' "{{ cfg_path }}")"
{%- endfor %}
{%- endfor %}
echo "Done!"
{% endmacro %}

{% macro fetch_db_seed(values) -%}
#!/bin/sh
{{ skip_step_or_continue(values=values, step="fetch_db_seed") }}
mkdir -p /shared/seed
cd /shared/seed

echo "Fetching seed..."
git init || { echo "Failed to initialize git repo"; exit 1; }
git remote add invidious https://github.com/iv-org/invidious.git || { echo "Failed to add remote"; exit 1; }
git fetch invidious || { echo "Failed to fetch remote"; exit 1; }
# Get the following directories: config, docker
git checkout invidious/master -- config docker || { echo "Failed to checkout"; exit 1; }
echo "Fetched seed successfully"

mv -fv config/config.example.yml /shared/config.example.yaml || { echo "Failed to move config"; exit 1; }
mv -fv config docker || { echo "Failed to move files"; exit 1; }
echo "Done!"
{% endmacro %}

{% macro apply_db_seed(values) -%}
#!/bin/sh
{{ skip_step_or_continue(values=values, step="apply_db_seed") }}
echo "Applying seed..."
cd /shared/seed/docker
./init-invidious-db.sh || { echo "Failed to apply seed"; exit 1; }
echo "Done!"
{% endmacro %}


{% macro skip_step_or_continue(values, step='') -%}
{%- set cfg_path = "%s/config.yaml"|format(values.consts.config_path) %}
touch "{{ cfg_path }}"
if [ -f "{{ cfg_path }}" ]; then
  echo "Found existing config file [{{ cfg_path }}]."
  echo "Treating it as an existing installation. Skipping step [{{ step }}]..."

  echo "If you are re-installing, please remove the file and restart the app."
  echo "After it is up and running, you can update the config file to your needs and restart the app."
  exit 0
fi
{% endmacro %}
