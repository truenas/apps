import yaml
import os


# def main():
#     output_file = "versions.yaml"
#     versions = {}
#     with open(output_file, "r") as f:
#         versions = yaml.safe_load(f.read())
#     if not versions:
#         print(f"No versions found in {output_file}")
#         return

#     for train in os.listdir("ix-dev"):
#         for app in os.listdir(f"ix-dev/{train}"):
#             key = f"{train}/{app}"
#             if key not in versions:
#                 print(f"No version found for {key} in {output_file}")
#                 continue
#             app_file = f"ix-dev/{train}/{app}/app.yaml"
#             migrations_file = f"ix-dev/{train}/{app}/app_migrations.yaml"
#             if not os.path.exists(app_file):
#                 print(f"No values file for {app_file}")
#                 continue
#             if not os.path.exists(migrations_file):
#                 print(f"No migrations file for {migrations_file}")
#                 continue
#             with open(app_file, "r") as f:
#                 data = yaml.safe_load(f.read())
#                 version = data["version"]
#                 parts = version.split(".")
#                 old_version_parts = versions[key].split(".")

#                 if int(parts[1]) != int(old_version_parts[1]) + 1:
#                     raise ValueError(f"Version mismatch for {key}: {version} vs {versions[key]}")

#                 data["annotations"] = {"min_scale_version": "24.10.2.2"}
#             with open(app_file, "w") as f:
#                 f.write(yaml.dump(data))
#             print(f"Updated {app_file} with min_scale_version {data['annotations']['min_scale_version']}")
#             with open(migrations_file, "r") as f:
#                 mig_data = yaml.safe_load(f.read())
#                 migrations = mig_data["migrations"]
#                 for mig in migrations:
#                     mig["from"] = {}
#                     mig["from"]["max_version"] = versions[key]
#                     mig["target"]["min_version"] = version
#             mig_data["migrations"] = migrations
#             with open(migrations_file, "w") as f:
#                 f.write(yaml.dump(mig_data))
#             print(f"Updated {migrations_file} with min_version {version}")
#             print("--------------------------------------------------")


# def main():
#     output_file = "versions.yaml"
#     versions = {}

#     for train in os.listdir("ix-dev"):
#         for app in os.listdir(f"ix-dev/{train}"):
#             key = f"{train}/{app}"
#             app_file = f"ix-dev/{train}/{app}/app.yaml"
#             if not os.path.exists(app_file):
#                 print(f"No app file for {app_file}")
#                 continue
#             with open(app_file, "r") as f:
#                 data = yaml.safe_load(f.read())
#                 version = data["version"]
#             versions[key] = version
#     with open(output_file, "w") as f:
#         f.write(yaml.dump(versions, default_flow_style=False, sort_keys=False))
#     print(f"Versions written to {output_file}")
#     print("--------------------------------------------------")

allow = [
    "ix-dev/community/actual-budget/app.yaml",
    "ix-dev/community/adguard-home/app.yaml",
    "ix-dev/community/affine/app.yaml",
    "ix-dev/community/archisteamfarm/app.yaml",
    "ix-dev/community/arti/app.yaml",
    "ix-dev/community/audiobookshelf/app.yaml",
    "ix-dev/community/authelia/app.yaml",
    "ix-dev/community/authentik/app.yaml",
    "ix-dev/community/autobrr/app.yaml",
    "ix-dev/community/automatic-ripping-machine/app.yaml",
    "ix-dev/community/baserow/app.yaml",
    "ix-dev/community/bazarr/app.yaml",
    "ix-dev/community/bitcoind/app.yaml",
    "ix-dev/community/bitmagnet/app.yaml",
    "ix-dev/community/briefkasten/app.yaml",
    "ix-dev/community/calibre-web/app.yaml",
    "ix-dev/community/calibre/app.yaml",
    "ix-dev/community/castopod/app.yaml",
    "ix-dev/community/change-detection/app.yaml",
    "ix-dev/community/channels-dvr/app.yaml",
    "ix-dev/community/chia/app.yaml",
    "ix-dev/community/clamav/app.yaml",
    "ix-dev/community/cloudflared/app.yaml",
    "ix-dev/community/cockpit-ws/app.yaml",
    "ix-dev/community/code-server/app.yaml",
    "ix-dev/community/codegate/app.yaml",
    "ix-dev/community/concourse/app.yaml",
    "ix-dev/community/convertx/app.yaml",
    "ix-dev/community/crafty-4/app.yaml",
    "ix-dev/community/dashy/app.yaml",
    "ix-dev/community/dawarich/app.yaml",
    "ix-dev/community/ddns-updater/app.yaml",
    "ix-dev/community/deluge/app.yaml",
    "ix-dev/community/distribution/app.yaml",
    "ix-dev/community/dockge/app.yaml",
    "ix-dev/community/dozzle/app.yaml",
    "ix-dev/community/drawio/app.yaml",
    "ix-dev/community/duplicati/app.yaml",
    "ix-dev/community/eclipse-mosquitto/app.yaml",
    "ix-dev/community/electrs/app.yaml",
    "ix-dev/community/esphome/app.yaml",
    "ix-dev/community/filebrowser/app.yaml",
    "ix-dev/community/filestash/app.yaml",
    "ix-dev/community/firefly-iii/app.yaml",
    "ix-dev/community/fireshare/app.yaml",
    "ix-dev/community/flame/app.yaml",
    "ix-dev/community/flaresolverr/app.yaml",
    "ix-dev/community/flood/app.yaml",
    "ix-dev/community/forgejo/app.yaml",
    "ix-dev/community/freshrss/app.yaml",
    "ix-dev/community/frigate/app.yaml",
    "ix-dev/community/fscrawler/app.yaml",
    "ix-dev/community/gaseous-server/app.yaml",
    "ix-dev/community/gitea-act-runner/app.yaml",
    "ix-dev/community/gitea/app.yaml",
    "ix-dev/community/glances/app.yaml",
    "ix-dev/community/grafana/app.yaml",
    "ix-dev/community/gramps-web/app.yaml",
    "ix-dev/community/handbrake-web/app.yaml",
    "ix-dev/community/handbrake/app.yaml",
    "ix-dev/community/heimdall/app.yaml",
    "ix-dev/community/homarr/app.yaml",
    "ix-dev/community/homebox/app.yaml",
    "ix-dev/community/homepage/app.yaml",
    "ix-dev/community/homer/app.yaml",
    "ix-dev/community/i2p/app.yaml",
    "ix-dev/community/iconik-storage-gateway/app.yaml",
    "ix-dev/community/immich/app.yaml",
    "ix-dev/community/influxdb/app.yaml",
    "ix-dev/community/invidious/app.yaml",
    "ix-dev/community/invoice-ninja/app.yaml",
    "ix-dev/community/ipfs/app.yaml",
    "ix-dev/community/it-tools/app.yaml",
    "ix-dev/community/jackett/app.yaml",
    "ix-dev/community/jdownloader2/app.yaml",
    "ix-dev/community/jellyfin/app.yaml",
    "ix-dev/community/jellyseerr/app.yaml",
    "ix-dev/community/jellystat/app.yaml",
    "ix-dev/community/jelu/app.yaml",
    "ix-dev/community/jenkins/app.yaml",
    "ix-dev/community/joplin/app.yaml",
    "ix-dev/community/kapowarr/app.yaml",
    "ix-dev/community/karakeep/app.yaml",
    "ix-dev/community/kasm-workspaces/app.yaml",
    "ix-dev/community/kavita/app.yaml",
    "ix-dev/community/kerberos-agent/app.yaml",
    "ix-dev/community/komga/app.yaml",
    "ix-dev/community/komodo/app.yaml",
    "ix-dev/community/lancache-monolithic/app.yaml",
    "ix-dev/community/lazylibrarian/app.yaml",
    "ix-dev/community/lidarr/app.yaml",
    "ix-dev/community/linkding/app.yaml",
    "ix-dev/community/listmonk/app.yaml",
    "ix-dev/community/logseq/app.yaml",
    "ix-dev/community/lyrion-music-server/app.yaml",
    "ix-dev/community/maintainerr/app.yaml",
    "ix-dev/community/mariadb/app.yaml",
    "ix-dev/community/mealie/app.yaml",
    "ix-dev/community/mempool/app.yaml",
    "ix-dev/community/metube/app.yaml",
    "ix-dev/community/minecraft-bedrock/app.yaml",
    "ix-dev/community/minecraft/app.yaml",
    "ix-dev/community/mineos/app.yaml",
    "ix-dev/community/mitmproxy/app.yaml",
    "ix-dev/community/monero-lws/app.yaml",
    "ix-dev/community/monero-wallet-rpc/app.yaml",
    "ix-dev/community/monerod/app.yaml",
    "ix-dev/community/mongodb/app.yaml",
    "ix-dev/community/monitee-agent/app.yaml",
    "ix-dev/community/mumble/app.yaml",
    "ix-dev/community/n8n/app.yaml",
    "ix-dev/community/navidrome/app.yaml",
    "ix-dev/community/netbootxyz/app.yaml",
    "ix-dev/community/newt/app.yaml",
    "ix-dev/community/nextpvr/app.yaml",
    "ix-dev/community/nginx-proxy-manager/app.yaml",
    "ix-dev/community/node-red/app.yaml",
    "ix-dev/community/notifiarr/app.yaml",
    "ix-dev/community/nzbget/app.yaml",
    "ix-dev/community/octoprint/app.yaml",
    "ix-dev/community/odoo/app.yaml",
    "ix-dev/community/ollama/app.yaml",
    "ix-dev/community/omada-controller/app.yaml",
    "ix-dev/community/onlyoffice-document-server/app.yaml",
    "ix-dev/community/open-speed-test/app.yaml",
    "ix-dev/community/open-webui/app.yaml",
    "ix-dev/community/organizr/app.yaml",
    "ix-dev/community/outline/app.yaml",
    "ix-dev/community/overseerr/app.yaml",
    "ix-dev/community/palworld/app.yaml",
    "ix-dev/community/paperless-ngx/app.yaml",
    "ix-dev/community/passbolt/app.yaml",
    "ix-dev/community/penpot/app.yaml",
    "ix-dev/community/pgadmin/app.yaml",
    "ix-dev/community/pigallery2/app.yaml",
    "ix-dev/community/piwigo/app.yaml",
    "ix-dev/community/planka/app.yaml",
    "ix-dev/community/playwright/app.yaml",
    "ix-dev/community/plex-auto-languages/app.yaml",
    "ix-dev/community/portainer/app.yaml",
    "ix-dev/community/postgres/app.yaml",
    "ix-dev/community/prowlarr/app.yaml",
    "ix-dev/community/pterodactyl-panel/app.yaml",
    "ix-dev/community/qbittorrent/app.yaml",
    "ix-dev/community/radarr/app.yaml",
    "ix-dev/community/readarr/app.yaml",
    "ix-dev/community/recyclarr/app.yaml",
    "ix-dev/community/redis/app.yaml",
    "ix-dev/community/romm/app.yaml",
    "ix-dev/community/roundcube/app.yaml",
    "ix-dev/community/rsyncd/app.yaml",
    "ix-dev/community/rust-desk/app.yaml",
    "ix-dev/community/sabnzbd/app.yaml",
    "ix-dev/community/satisfactory-server/app.yaml",
    "ix-dev/community/scrutiny/app.yaml",
    "ix-dev/community/scrypted/app.yaml",
    "ix-dev/community/searxng/app.yaml",
    "ix-dev/community/seaweedfs/app.yaml",
    "ix-dev/community/sftpgo/app.yaml",
    "ix-dev/community/sonarr/app.yaml",
    "ix-dev/community/spottarr/app.yaml",
    "ix-dev/community/steam-headless/app.yaml",
    "ix-dev/community/stirling-pdf/app.yaml",
    "ix-dev/community/tailscale/app.yaml",
    "ix-dev/community/tautulli/app.yaml",
    "ix-dev/community/tdarr/app.yaml",
    "ix-dev/community/teamspeak/app.yaml",
    "ix-dev/community/terraria/app.yaml",
    "ix-dev/community/tftpd-hpa/app.yaml",
    "ix-dev/community/tianji/app.yaml",
    "ix-dev/community/tiny-media-manager/app.yaml",
    "ix-dev/community/transmission/app.yaml",
    "ix-dev/community/tvheadend/app.yaml",
    "ix-dev/community/twofactor-auth/app.yaml",
    "ix-dev/community/umami/app.yaml",
    "ix-dev/community/unifi-controller/app.yaml",
    "ix-dev/community/unifi-protect-backup/app.yaml",
    "ix-dev/community/unmanic/app.yaml",
    "ix-dev/community/uptime-kuma/app.yaml",
    "ix-dev/community/urbackup/app.yaml",
    "ix-dev/community/vaultwarden/app.yaml",
    "ix-dev/community/versitygw/app.yaml",
    "ix-dev/community/vikunja/app.yaml",
    "ix-dev/community/warracker/app.yaml",
    "ix-dev/community/webdav/app.yaml",
    "ix-dev/community/wger/app.yaml",
    "ix-dev/community/whoogle/app.yaml",
    "ix-dev/community/windmill/app.yaml",
    "ix-dev/community/woodpecker-ci/app.yaml",
    "ix-dev/community/wordpress/app.yaml",
    "ix-dev/community/wyze-bridge/app.yaml",
    "ix-dev/community/zerotier/app.yaml",
    "ix-dev/community/zigbee2mqtt/app.yaml",
    "ix-dev/community/zipline/app.yaml",
    "ix-dev/dev/truenas-webui/app.yaml",
    "ix-dev/enterprise/asigra-ds-system/app.yaml",
    "ix-dev/enterprise/ix-remote-assist/app.yaml",
    "ix-dev/enterprise/minio/app.yaml",
    "ix-dev/enterprise/syncthing/app.yaml",
    "ix-dev/stable/collabora/app.yaml",
    "ix-dev/stable/diskoverdata/app.yaml",
    "ix-dev/stable/elastic-search/app.yaml",
    "ix-dev/stable/emby/app.yaml",
    "ix-dev/stable/home-assistant/app.yaml",
    "ix-dev/stable/ix-app/app.yaml",
    "ix-dev/stable/minio/app.yaml",
    "ix-dev/stable/netdata/app.yaml",
    "ix-dev/stable/nextcloud/app.yaml",
    "ix-dev/stable/photoprism/app.yaml",
    "ix-dev/stable/pihole/app.yaml",
    "ix-dev/stable/plex/app.yaml",
    "ix-dev/stable/prometheus/app.yaml",
    "ix-dev/stable/storj/app.yaml",
    "ix-dev/stable/syncthing/app.yaml",
    "ix-dev/test/nextcloud/app.yaml",
]


def main():
    for train in os.listdir("ix-dev"):
        for app in os.listdir(f"ix-dev/{train}"):
            app_file = f"ix-dev/{train}/{app}/app.yaml"
            if app_file not in allow:
                print(f"Skipping {app_file} as it is not in the allow list")
                continue
            if not os.path.exists(app_file):
                print(f"No app file for {app_file}")
                raise FileNotFoundError(f"App file {app_file} does not exist")
            with open(app_file, "r") as f:
                data = yaml.safe_load(f.read())
                version = data["version"]
                parts = version.split(".")
                parts[2] = str(int(parts[2]) + 1)
                new_version = ".".join(parts)
            data["version"] = new_version
            with open(app_file, "w") as f:
                f.write(yaml.dump(data))
            print(f"Updated {app_file} to version {new_version}")
            print("--------------------------------------------------")


if __name__ == "__main__":
    main()
