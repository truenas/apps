# qBittorrent with WireGuard VPN

[qBittorrent](https://www.qbittorrent.org/) is an open-source BitTorrent client that aims to provide a free software alternative to uTorrent.

This version includes a built-in [WireGuard](https://www.wireguard.com/) VPN connection with automatic killswitch. All torrent traffic is routed through the VPN, and if the VPN connection drops, qBittorrent is automatically shut down to prevent any leaks.

## Features

- Built-in WireGuard VPN - No separate VPN container needed
- Automatic Killswitch - Stops all traffic if VPN disconnects
- Port Forwarding Support - Configure forwarded ports from your VPN provider
- Local Network Access - WebUI accessible from your local network
- VPN Bypass for LAN - Local network traffic doesn't go through VPN

## Prerequisites

Before deploying this app, you need:

1. A WireGuard VPN configuration file from your VPN provider (e.g., AirVPN, Mullvad, ProtonVPN, etc.)
2. The configuration file must be named `wg0.conf`

## Setup Instructions

1. Deploy the app through the TrueNAS UI
2. Configure your storage paths
3. After deployment, place your WireGuard configuration file (`wg0.conf`) in the config storage directory
4. Restart the app for the VPN to activate

## Configuration

The app supports optional VPN port forwarding. If your VPN provider supports port forwarding, you can configure this in the WireGuard Configuration section.

For more information, see the [upstream documentation](https://github.com/serversathome/qbittorrent-wireguard).
