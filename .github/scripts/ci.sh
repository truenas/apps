#!/bin/bash

train_dir="$1"
app_name="$2"
test_file="$3"

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
  local docker_compose_project="docker compose -p $project_name -f $rendered_path/docker-compose.yaml"

  # Render the docker-compose file
  docker run --rm -v "$(pwd)":/workspace ghcr.io/truenas/apps_validation:latest \
    /usr/bin/catalog_templating render --path /workspace/ix-dev/${train_dir}/${app_name} \
    --values /workspace/ix-dev/${train_dir}/${app_name}/test_values/${test_file}

  echo "Printing docker compose config (parsed compose)"
  $docker_compose_project config

  $docker_compose_project up -d --wait --wait-timeout 600
  local exit_code=$?

  # Print logs (for debugging)
  $docker_compose_project logs
  # Print docker compose processes (for debugging)
  $docker_compose_project ps --all

  if [ $exit_code -ne 0 ]; then
    echo "Failed to start container(s)"
    local failed=$($docker_compose_project ps --status exited --all --format json)
    for container in $(echo $failed | jq -r '.[].ID'); do
      echo "Container [$container] exited. Printing Inspect Data"
      docker container inspect $container | jq
    done

    exit 1
  fi

  $docker_compose_project down --remove-orphans --volumes
  $docker_compose_project rm --force --stop --volumes
}

cleanup() {
  echo "Cleaning up /mnt/test directory"
  # TODO: make something with this. I dont like the hardcoded /mnt/test
  sudo rm -r /mnt/test || echo "Failed to clean up /mnt/test"
}

# Run the cleanup function on exit
trap cleanup EXIT

check_required_params
check_required_commands
run_docker
