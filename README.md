# TrueNAS Apps Catalog

This repository contains the Docker-Compose based App catalog used by TrueNAS systems to render and update the Apps catalog.

![image](https://github.com/user-attachments/assets/2f00c325-9d6a-46ff-8162-a080fd8a156a)

## Deprecating Apps, Features, Configuration or Functionality

When an `App`, `Feature`, `Configuration` or `Functionality` is deprecated, it will be marked as such.

On an already installed app, you will see a deprecation notice in the `Notes` card in the TrueNAS UI.

In the scenario that a whole app is deprecated (not just a configuration option).
The deprecation notice will also be visible in the `Discover` tab of the TrueNAS UI, next to the app's title.

**The deprecation period is 3 months.**

After the deprecation period, the app, feature, configuration or functionality will be removed.

## Contributing Applications

The Apps catalog is open for contributions! We provide instructions on how to locally develop and test new applications in our [contributors guide](CONTRIBUTIONS.md).

Questions on the development of applications? Please head over to our [discussions](https://github.com/truenas/apps/discussions) page to ask questions and collaborate with other App Developers.

## Parity Status with Legacy K3's truenas/charts (100% 🚀)

<details>
<summary>Show Apps List</summary>

| App                  | Train      | Added | Migrated                                                             |
| -------------------- | ---------- | ----- | -------------------------------------------------------------------- |
| collabora            | charts     | ✅    | ✅                                                                   |
| diskoverdata         | charts     | ✅    | ✅                                                                   |
| elastic-search       | charts     | ✅    | ✅                                                                   |
| emby                 | charts     | ✅    | ✅                                                                   |
| home-assistant       | charts     | ✅    | ✅ - [Manual steps needed](https://github.com/truenas/apps/pull/492) |
| ix-chart             | charts     | ✅    | ✅                                                                   |
| minio                | charts     | ✅    | ✅                                                                   |
| netdata              | charts     | ✅    | ✅                                                                   |
| nextcloud            | charts     | ✅    | ✅                                                                   |
| photoprism           | charts     | ✅    | ✅                                                                   |
| plex                 | charts     | ✅    | ✅                                                                   |
| pihole               | charts     | ✅    | ✅                                                                   |
| prometheus           | charts     | ✅    | ✅                                                                   |
| storj                | charts     | ✅    | ✅                                                                   |
| syncthing            | charts     | ✅    | ✅                                                                   |
| wg-easy              | charts     | ✅    | ✅                                                                   |
| actual-budget        | community  | ✅    | ✅                                                                   |
| adguard-home         | community  | ✅    | ✅                                                                   |
| audiobookshelf       | community  | ✅    | ✅                                                                   |
| autobrr              | community  | ✅    | ✅                                                                   |
| bazarr               | community  | ✅    | ✅                                                                   |
| briefkasten          | community  | ✅    | ✅                                                                   |
| castopod             | community  | ✅    | ✅                                                                   |
| chia                 | community  | ✅    | ✅                                                                   |
| clamav               | community  | ✅    | ✅                                                                   |
| cloudflared          | community  | ✅    | ✅                                                                   |
| dashy                | community  | ✅    | ✅                                                                   |
| deluge               | community  | ✅    | ✅                                                                   |
| ddns-updater         | community  | ✅    | ✅                                                                   |
| distribution         | community  | ✅    | ✅                                                                   |
| drawio               | community  | ✅    | ✅                                                                   |
| filebrowser          | community  | ✅    | ✅                                                                   |
| firefly-iii          | community  | ✅    | ✅                                                                   |
| flame                | community  | ✅    | ✅                                                                   |
| freshrss             | community  | ✅    | ✅                                                                   |
| frigate              | community  | ✅    | ✅                                                                   |
| fscrawler            | community  | ✅    | ✅                                                                   |
| gitea                | community  | ✅    | ✅                                                                   |
| handbrake            | community  | ✅    | ✅                                                                   |
| grafana              | community  | ✅    | ✅                                                                   |
| homarr               | community  | ✅    | ✅                                                                   |
| homer                | community  | ✅    | ✅                                                                   |
| homepage             | community  | ✅    | ✅                                                                   |
| immich               | community  | ✅    | ✅                                                                   |
| invidious            | community  | ✅    | ✅                                                                   |
| ipfs                 | community  | ✅    | ✅                                                                   |
| jellyfin             | community  | ✅    | ✅                                                                   |
| jellyseerr           | community  | ✅    | ✅                                                                   |
| jenkins              | community  | ✅    | ✅                                                                   |
| joplin               | community  | ✅    | ✅                                                                   |
| kapowarr             | community  | ✅    | ✅                                                                   |
| kavita               | community  | ✅    | ✅                                                                   |
| komga                | community  | ✅    | ✅                                                                   |
| lidarr               | community  | ✅    | ✅                                                                   |
| linkding             | community  | ✅    | ✅                                                                   |
| listmonk             | community  | ✅    | ✅                                                                   |
| logseq               | community  | ✅    | ✅                                                                   |
| mealie               | community  | ✅    | ✅                                                                   |
| metube               | community  | ✅    | ✅                                                                   |
| minecraft            | community  | ✅    | ✅                                                                   |
| mineos               | community  | ✅    | ✅                                                                   |
| mumble               | community  | ✅    | ✅                                                                   |
| n8n                  | community  | ✅    | ✅                                                                   |
| navidrome            | community  | ✅    | ✅                                                                   |
| nginx-proxy-manager  | community  | ✅    | ✅                                                                   |
| netbootxyz           | community  | ✅    | ✅                                                                   |
| node-red             | community  | ✅    | ✅                                                                   |
| odoo                 | community  | ✅    | ✅                                                                   |
| omada-controller     | community  | ✅    | ✅                                                                   |
| organizr             | community  | ✅    | ✅                                                                   |
| overseerr            | community  | ✅    | ✅                                                                   |
| palworld             | community  | ✅    | ✅                                                                   |
| paperless-ngx        | community  | ✅    | ✅                                                                   |
| passbolt             | community  | ✅    | ✅                                                                   |
| pgadmin              | community  | ✅    | ✅                                                                   |
| pigallery2           | community  | ✅    | ✅                                                                   |
| piwigo               | community  | ✅    | ✅                                                                   |
| planka               | community  | ✅    | ✅                                                                   |
| plex-auto-languages  | community  | ✅    | ✅                                                                   |
| prowlarr             | community  | ✅    | ✅                                                                   |
| radarr               | community  | ✅    | ✅                                                                   |
| qbittorrent          | community  | ✅    | ✅                                                                   |
| readarr              | community  | ✅    | ✅                                                                   |
| recyclarr            | community  | ✅    | ✅                                                                   |
| redis                | community  | ✅    | ✅                                                                   |
| roundcube            | community  | ✅    | ✅                                                                   |
| rsyncd               | community  | ✅    | ✅                                                                   |
| rust-desk            | community  | ✅    | ✅                                                                   |
| sabnzbd              | community  | ✅    | ✅                                                                   |
| searxng              | community  | ✅    | ✅                                                                   |
| sftpgo               | community  | ✅    | ✅                                                                   |
| sonarr               | community  | ✅    | ✅                                                                   |
| tailscale            | community  | ✅    | ✅ - [Manual steps needed](https://github.com/truenas/apps/pull/641) |
| tautulli             | community  | ✅    | ✅                                                                   |
| tdarr                | community  | ✅    | ✅                                                                   |
| terraria             | community  | ✅    | ✅                                                                   |
| tftpd-hpa            | community  | ✅    | ✅                                                                   |
| tiny-media-manager   | community  | ✅    | ✅                                                                   |
| transmission         | community  | ✅    | ✅                                                                   |
| twofactor-auth       | community  | ✅    | ✅                                                                   |
| unifi-controller     | community  | ✅    | ✅                                                                   |
| unifi-protect-backup | community  | ✅    | ✅                                                                   |
| vaultwarden          | community  | ✅    | ✅                                                                   |
| vikunja              | community  | ✅    | ✅                                                                   |
| webdav               | community  | ✅    | ✅                                                                   |
| whoogle              | community  | ✅    | ✅                                                                   |
| wordpress            | community  | ✅    | ✅                                                                   |
| zerotier             | community  | ✅    | ✅                                                                   |
| minio                | enterprise | ✅    | ✅                                                                   |
| syncthing            | enterprise | ✅    | ✅                                                                   |

</details>
