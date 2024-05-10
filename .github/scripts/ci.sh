#!/bin/bash

train_dir="$1"
app_name="$2"
test_file="$3"

container_image="ghcr.io/truenas/apps_validation:latest"

check_required_params() {
  required_params=("train_dir" "app_name" "test_file")
  for param in "${required_params[@]}"; do
    if [ -z "${!param}" ]; then
      echo "Error: parameter [$param] is empty"
      exit 1
    fi
  done
}

check_required_commands() {
  required_commands=("docker" "jq" "openssl")
  for command in "${required_commands[@]}"; do
    if ! command -v "$command" &>/dev/null; then
      echo "Error: command [$command] is not installed"
      exit 1
    fi
  done
}

run_docker() {
  local project_name="$(openssl rand -hex 12)"
  local rendered_path="/workspace/ix-dev/${train_dir}/${app_name}/templates/rendered"
  local base_cmd="docker compose -p $project_name -f $rendered_path/docker-compose.yaml"

  # Render the docker-compose file
  docker run --rm -v "$(pwd)":/workspace $container_image \
    /usr/bin/catalog_templating render --path /workspace/ix-dev/${train_dir}/${app_name} \
    --values /workspace/ix-dev/${train_dir}/${app_name}/test_values/${test_file}

  if [ $? -ne 0 ]; then
    echo "Failed to render docker-compose file"
    exit 1
  fi

  echo "Printing docker compose config (parsed compose)"
  $base_cmd config

  $base_cmd up -d --wait --wait-timeout 600
  local exit_code=$?

  # Print logs (for debugging)
  $base_cmd logs
  # Print docker compose processes (for debugging)
  $base_cmd ps --all

  if [ $exit_code -ne 0 ]; then
    echo "Failed to start container(s)"
    local failed=$($base_cmd ps --status exited --all --format json)
    for container in $(echo $failed | jq -r '.[].ID'); do
      echo "Container [$container] exited. Printing Inspect Data"
      docker container inspect $container | jq
    done

    exit 1
  fi

  $base_cmd down --remove-orphans --volumes
  $base_cmd rm --force --stop --volumes
}

check_required_params
check_required_commands
run_docker
