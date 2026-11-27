#!/bin/bash
set -euo pipefail

# Renovate 45 images no longer ship the docker CLI, but renovate_bump.sh
# needs it to run app_bump_version through the mounted docker socket.
# https://github.com/renovatebot/renovate/releases/tag/45.0.0
install-tool docker

exec renovate
