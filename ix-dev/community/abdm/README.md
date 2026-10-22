# AB Download Manager

AB Download Manager is a modern open-source download manager featuring a responsive web interface and a built-in browser session for TrueNAS SCALE. This community catalog package deploys the `ghcr.io/sweenyxsky-oss/abdm-truenas` container image.

The catalog installer provides configurable network port, timezone, user/group IDs, and persistent storage mounts for configuration, downloads, and temporary download files. The container includes the browser display stack and is configured with 1 GiB shared memory.

## Credits & Authors

- **TrueNAS SCALE Edition & Containerization**: Abdul-Rahman B ([@sweenyxsky-oss](https://github.com/sweenyxsky-oss)) — Headless daemon adaptation, TrueNAS web interface, browser session integration, and catalog packaging.
- **Upstream AB Download Manager**: Amir Hossein Bayat ([@amir1376](https://github.com/amir1376)) and the [AB Download Manager contributors](https://github.com/amir1376/ab-download-manager).
- **Browser Extension & uBlock Origin**: Developed by upstream maintainers and Raymond Hill (gorhill).

## Dual Deployment Modes

This catalog package exists alongside the standalone Compose setup:
- **TrueNAS Apps Catalog**: One-click install from the TrueNAS SCALE UI with interactive dataset and port configuration.
- **Docker Compose (Custom App)**: The original `docker-compose.truenas.yml` remains maintained in [sweenyxsky-oss/abdm-truenas](https://github.com/sweenyxsky-oss/abdm-truenas) for users who prefer direct Compose management.

## Image & Verification

The image is pinned by immutable digest in `ix_values.yaml` (`v0.4-browser-multiconnection@sha256:0e72114de44e...`). The base application reports upstream version 1.10.4.

## Security

Keep the service on a trusted local network or place it behind a reverse proxy with HTTPS. You can enable API-key authentication within the ABDM web interface.
