{% macro init(values) -%}

{%- set url = "https://github.com/storj/storj/releases/latest/download/identity_linux_amd64.zip" %}
{%- set id_path = values.consts.identity_dir %}
{%- set id_tool_dir = "/tmp/identity-tool" %}
{%- set id_tool_dir_files = values.consts.identity_tool_dir_files %}
{%- set flags = "--identity-dir %s"|format(id_path) %}

[ ! -w {{ values.consts.config_dir }} ] && { echo "Config directory is not writable."; exit 1; }
[ ! -r {{ id_path }} ] && { echo "Identity directory is not readable."; exit 1; }

echo "Checking for identity certificate..."
if ! [ -f "{{ id_path }}/ca.cert" ] && ! [ -f "{{ id_path }}/identity.cert" ]; then
  echo "Downloading identity generator tool..."; mkdir -p {{ id_tool_dir }}
  mkdir -p {{ id_tool_dir_files }}
  [ -w {{ id_tool_dir_files }} ] || { echo "Identity tool files directory is not writable."; exit 1; }
  [ -w {{ id_path }} ] || { echo "Identity directory is not writable."; exit 1; }
  wget -q -O {{ id_tool_dir }}/identity_linux_amd64.zip {{ url }} || { echo "Failed to download identity generator tool."; exit 1; }
  unzip -o {{ id_tool_dir }}/identity_linux_amd64.zip -d {{ id_tool_dir }} || { echo "Failed to unzip identity generator tool."; exit 1; }
  chmod +x {{ id_tool_dir }}/identity || { echo "Failed to make identity generator tool executable."; exit 1; }

  echo "Generating identity certificate..."
  {{ id_tool_dir }}/identity create storagenode {{ flags }}
  if [ ! -f "{{ id_path }}/storagenode/ca.cert" ] && [ ! -f "{{ id_path }}/storagenode/identity.cert" ]; then
    echo "Failed to generate identity certificate."
    exit 1
  fi
  echo "Identity generated successfully at {{ id_path }}"
  ls -lhR {{ id_path }}

  mv {{ id_path }}/storagenode/identity.key {{ id_path }}/identity.key || { echo "Failed to move identity key."; exit 1; }
  mv {{ id_path }}/storagenode/identity.cert {{ id_path }}/identity.cert || { echo "Failed to move identity certificate."; exit 1; }
else
  echo "Identity certificate already exists. Skipping..."
fi

echo "Checking if Storj is already setup..."
if ! [ -f {{ values.consts.config_dir }}/config.yaml ]; then
  echo "Setting up Storj"
  export SETUP="true"
  /entrypoint
else
  echo "Storj is already setup. Skipping..."
fi

# Mark setup as done so the main container can start
touch {{ values.consts.config_dir }}/setup.done || { echo "Failed to create setup.done file."; exit 1; }
{% endmacro %}
