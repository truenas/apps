#!/bin/bash

app_path=$1
update_type=$2
log_path="./renovate.log"

if [[ -z "$app_path" ]]; then
  echo "Missing app_path"
  exit 1
fi

if [[ -z "$update_type" ]]; then
  echo "Missing update_type"
  exit 1
fi

if grep "{{{packageFileDir}}}" "$log_path"; then
  exit 0
fi

docker run --quiet --rm \
  --platform linux/amd64 \
  -v ./:/workspace \
  ghcr.io/truenas/apps_validation:latest app_bump_version \
  --path /workspace/"$app_path" \
  --bump "$update_type"

echo "$app_path" >>"$log_path"
