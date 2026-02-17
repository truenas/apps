{% macro entrypoint(values) -%}
#!/bin/sh

set -e

# Creates configuration file if it doesn't exist.
# The XMRig image already ships with a configuration file at this path, but the bind mount wipes it.
CONFIG_FILE_PATH="$HOME/.config/xmrig.json"

if [ ! -e "$CONFIG_FILE_PATH" ]; then
  mkdir -p "$(dirname "$CONFIG_FILE_PATH")"
  cp $HOME/xmrig-config.json $CONFIG_FILE_PATH
fi

xmrig "$@"
{%- endmacro %}