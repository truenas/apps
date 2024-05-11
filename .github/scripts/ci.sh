#!/bin/bash

train_dir="$1"
app_name="$2"
test_file="$3"

echo "Parameters:"
echo "  - train_dir: [$train_dir]"
echo "  - app_name: [$app_name]"
echo "  - test_file: [$test_file]"

# TODO: container_image="ghcr.io/truenas/apps_validation:latest"
container_image="sonicaj/a_v:latest"
# render_cmd="catalog_templating render"
render_cmd="python3 /app/catalog_templating/scripts/render_compose.py render"
test_values_dir="templates/test_values"

check_required_params() {
  required_params=("train_dir" "app_name" "test_file")
  for param in "${required_params[@]}"; do
    if [ -z "${!param}" ]; then
      echo "Error: parameter [$param] is empty"
      exit 1
    fi
  done
}

separator() {
  echo -e "\n================================================\n"
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

cleanup() {
  local base_cmd="$1"
  $base_cmd down --remove-orphans --volumes
  $base_cmd rm --force --stop --volumes
}

run_docker() {
  local project_name="$(openssl rand -hex 12)"
  local rendered_path="ix-dev/${train_dir}/${app_name}/templates/rendered"
  local base_cmd="docker compose -p $project_name -f $rendered_path/docker-compose.yaml"

  # TODO: make it better later
  ./copy_lib.sh $train_dir $app_name || echo "Failed to copy lib"

  echo -n "Rendering docker-compose file..."
  # Render the docker-compose file
  docker run --quiet --rm -v "$(pwd)":/workspace $container_image \
    $render_cmd --path /workspace/ix-dev/${train_dir}/${app_name} \
    --values /workspace/ix-dev/${train_dir}/${app_name}/${test_values_dir}/${test_file}

  if [ $? -ne 0 ]; then
    echo " Failed."
    exit 1
  fi
  echo " Done!"

  echo -e "\nPrinting docker compose config (parsed compose)"
  separator
  $base_cmd config
  separator

  # FIXME:
  mkdir -p /mnt/test
  chown -R nobody:nogroup /mnt/test
  chmod 777 /mnt/test

  $base_cmd up --detach --quiet-pull --wait --wait-timeout 600
  local exit_code=$?

  separator
  # Print logs (for debugging)
  $base_cmd logs
  separator
  echo ''
  # Print docker compose processes (for debugging)
  $base_cmd ps --all
  separator

  if [ $exit_code -ne 0 ]; then
    echo "Failed to start container(s)"
    local failed="$($base_cmd ps --status exited --all --format json)"
    # if failed starts with { put it inside []
    if [[ $failed == "{"* ]]; then
      failed="[$failed]"
    fi

    for container in $(echo ${failed} | jq -r '.[].ID'); do
      echo "Container [$container] exited. Printing Inspect Data"
      docker container inspect $container | jq
    done

    cleanup $base_cmd
    exit 1
  fi

  cleanup $base_cmd
}

check_required_params
check_required_commands
run_docker
