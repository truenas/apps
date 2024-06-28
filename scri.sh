#!/bin/bash
set -x

function run() {
  train=$1
  app=$2
  branch=$3

  git switch $branch || exit 1
  git pull
  git pull origin library-stuff --rebase
  ./.github/scripts/ci.py --app $app --train $train --test-file basic-values.yaml --render-only true || exit 1
  sudo chown skois -R ix-dev
  git add .
  git commit -m "update lib"
  git push -f
}

function grm() {
  train=$1
  app=$2
  branch=$3

  git switch $branch || exit 1
  sudo chown skois -R ix-dev
  git reset --soft HEAD~1
  git rm scr.sh
  git reset -q HEAD -- /home/skois/projects/ix/apps/scr.sh
  rm /home/skois/projects/ix/apps/scr.sh
  git push -f
}

run community ddns-updater add-ddns-updater
# run community autobrr add-autobrr
# run community navidrome add-navidrome
# run community unifi-controller add-unifi-controller
# run community audiobookshelf add-audiobookshelf
# run community adguard-home add-adguard
# run charts pihole add-pihole
# run community actual-budget add-actualbudget
# run community drawio add-drawio
# run community tautulli add-tautulli
# run community tailscale add-tailscale
# run community qbittorrent add-qbit
# run community komga add-komga
# run community overseerr add-overseerr
# run community bazarr add-bazarr
# run community portainer add-portainer
# run community readarr readarr
# run community dockge add-dockge
# run community jellyseerr add-jellyseer
# run community lidarr add-libarr
# run community prowlarr add-prowlarr
# run community radarr add-radarr
# run community sonarr add-sonarr
# run charts plex add-plex
# run enterprise minio add-minio-enterprise
