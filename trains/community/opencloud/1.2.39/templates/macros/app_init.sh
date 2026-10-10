{% macro app_init(values) -%}
#!/bin/sh
set -e

[ -z "$TARGET_PATH" ] && echo "Missing required environment variable: TARGET_PATH" && exit 1
[ -z "$APP_ID" ] && echo "Missing required environment variable: APP_ID" && exit 1
[ -z "$SOURCE_PATH" ] && echo "Missing required environment variable: SOURCE_PATH" && exit 1
[ -z "$ENABLED" ] && echo "Missing required environment variable: ENABLED" && exit 1

app_path="$TARGET_PATH/$APP_ID"
if [ -d "$app_path" ]; then
  echo "Removing old app files for [$APP_ID] from [$app_path]"
  rm -rf "$app_path"
fi

if [ "$ENABLED" != "true" ]; then
  echo "App [$APP_ID] is disabled, exiting."
  exit 0
fi

mkdir -p "$TARGET_PATH"

echo "Copying app files for [$APP_ID] to [$app_path] from [$SOURCE_PATH]"
cp -R "$SOURCE_PATH" "$app_path"

echo "Setting ownership to [{{ values.run_as.user }}:{{ values.run_as.group }}] for [$app_path]"
chown -R {{ values.run_as.user }}:{{ values.run_as.group }} "$app_path"

echo "Done!"
{% endmacro %}
