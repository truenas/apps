# DockTail

[DockTail](https://docktail.org) — Label-based Tailscale Services for Docker containers.

License: [AGPL-3.0](https://github.com/marvinvr/docktail/blob/main/LICENSE).
Documentation: https://docktail.org/docs/.

Requires TrueNAS SCALE 24.10 or later, a Tailscale auth key, and OAuth or API credentials.
Includes a Tailscale sidecar using host networking, `/dev/net/tun`, persistent state,
and a shared socket volume. DockTail mounts the Docker socket read-only.
DockTail Cloud monitoring is optional. No local web UI.
