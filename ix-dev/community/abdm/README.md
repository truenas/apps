# AB Download Manager

AB Download Manager is a self-hosted download manager with a web interface and a built-in browser. This TrueNAS community catalog package configures the existing `ghcr.io/sweenyxsky-oss/abdm-truenas` container image.

The catalog installer provides configurable network port, timezone, user/group, and persistent storage for configuration, downloads, and temporary download data. The container includes the browser display stack and needs 1 GiB shared memory.

## Keep using the YAML deployment

This catalog package does **not** replace or remove the existing `docker-compose.truenas.yml` in the [ABDM TrueNAS repository](https://github.com/sweenyxsky-oss/abdm-truenas). That file remains available for users who prefer to install or manage ABDM with a direct Compose YAML deployment. The catalog definition is an additional install path.

## Image and application version

The image is pinned by digest in `ix_values.yaml` for reproducible installs. The application reports upstream version 1.10.4; the container image also packages the TrueNAS web integration and built-in browser. The pinned image tag is the TrueNAS-specific `v0.4-browser-multiconnection` build. Catalog image updates should update the pinned digest and bump the catalog package version after testing.

## Security

Keep the service on a trusted network or place it behind HTTPS before exposing it outside the LAN. Configure API-key authentication in ABDM if you need to restrict access.
