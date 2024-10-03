#!/bin/bash

app_path=$1
update_type=$2
dep_name=$3
dep_version=$4
log_path="/tmp/renovate.log"

if [ ! -f "$log_path" ]; then
  touch "$log_path"
fi

if [[ -z "$app_path" ]]; then
  echo "Missing app_path"
  exit 1
fi

if [[ -z "$update_type" ]]; then
  echo "Missing update_type"
  exit 1
fi

if grep "$app_path" "$log_path"; then
  update_type=""
fi

docker run --quiet --rm \
  --platform linux/amd64 \
  -v ./:/workspace \
  ghcr.io/truenas/apps_validation:latest app_bump_version \
  --path /workspace/"$app_path" \
  --bump "$update_type" \
  --dep-name "$dep_name" \
  --dep-version "$dep_version"

echo "$app_path" >>"$log_path"
