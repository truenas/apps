#!/bin/bash

# Copy the library to the ix-dev directory
train=$1
app_name=$2

if [ -z "$train" ]; then
  echo "Usage: $0 <train> <app_name>"
  exit 1
fi

if [ -z "$app_name" ]; then
  echo "Usage: $0 <app_name>"
  exit 1
fi

app_path="ix-dev/$train/$app_name"

if [ ! -d "$app_path" ]; then
  echo "App [$app_path] does not exist"
  exit 1
fi

# pick the latest version
lib=$(ls -d library/* | sort -V | tail -n 1)
lib_version=$(basename $lib)
rm -rf "$app_path/templates/library/base_v$(sed 's/\./_/g' <<<$lib_version)"
mkdir -p "$app_path/templates/library/$lib_version"
cp -r $lib/* "$app_path/templates/library/$lib_version"
mv "$app_path/templates/library/$lib_version" "$app_path/templates/library/base_v$(sed 's/\./_/g' <<<$lib_version)"
