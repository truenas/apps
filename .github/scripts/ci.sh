#!/bin/bash

train_dir="$1"
app_name="$2"

if [ -z "$train_dir" ]; then
  echo "Usage: $0 <train> <app_name>"
  exit 1
fi

if [ -z "$app_name" ]; then
  echo "Usage: $0 <app_name>"
  exit 1
fi

files=("$train_dir/$app_name/ci/*.yaml")

required_commands=(
  "docker"
)

for command in "${required_commands[@]}"; do
  if ! command -v $command &>/dev/null; then
    echo "Error: command [$command] is not installed"
    exit 1
  fi
done

for values_file in $files; do
  echo "Testing [$values_file]"

  docker run --rm -v ${pwd}:/workspace ghcr.io/truenas/apps_validation:latest \
    /usr/bin/catalog_templating render --path /workspace/ix-dev/${train_dir}/${app_name} \
    --values /workspace/${values_file}

  PROJECT_NAME="$(openssl rand -hex 12)"
  docker_compose_project="docker compose -p $PROJECT_NAME \
    -f ix-dev/${train_dir}/${app_name}/templates/rendered/docker-compose.yaml"

  echo "Printing docker compose config (parsed compose)"
  ${docker_compose_project} config

  # Note that this will report failure if a container exits with a zero exit code too.
  # https://github.com/docker/compose/issues/10596
  ${docker_compose_project} up -d --wait --wait-timeout 600
  exit_code=$?

  # Print logs (for debugging)
  ${docker_compose_project} logs

  # Print docker compose processes (for debugging)
  ${docker_compose_project} ps --all

  if [ $exit_code -ne 0 ]; then
    echo "Failed to start container(s)"

    failed=$(${docker_compose_project} ps --status exited --all --format json)
    for container in $(echo $failed | jq -r '.[].ID'); do
      echo "Container [$container] exited. Printing Inspect Data"
      docker container inspect $container | jq
    done

    exit 1
  fi

  ${docker_compose_project} down --remove-orphans --volumes
  ${docker_compose_project} rm --force --stop --volumes

  # Clean up the test directory used by the app
  # TODO: make something with this. I dont like the hardcoded /mnt/test
  echo "Cleaning up /mnt/test directory"
  sudo rm -r /mnt/test || echo "Failed to clean up /mnt/test"
done
