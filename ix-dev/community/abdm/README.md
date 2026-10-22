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

## TrueNAS SCALE 25.10 Reviewer Test Checklist

Run these checks on a disposable TrueNAS SCALE 25.10.x system and pool. Record the exact TrueNAS build, app revision, image digest, and outcome for each step. Do not use production data; take a dataset snapshot or backup before upgrade/rollback testing.

### Install

- [ ] Refresh the catalog and confirm AB Download Manager appears in the community train.
- [ ] Install with default ixVolumes; confirm the wizard completes and the app reaches **Running**.
- [ ] Open the app portal and verify the web interface and built-in browser session load.
- [ ] Add a small test download; confirm completed files land in the configured downloads dataset.
- [ ] Restart the app and confirm configuration, browser profile, and downloaded test file persist.
- [ ] Repeat installation using host-path storage and a non-default published port; verify port access and file ownership with the configured UID/GID.
- [ ] Confirm the UI is not exposed beyond the intended trusted network and API-key authentication can be enabled before external exposure.

### Upgrade

- [ ] Install an earlier catalog revision/image first, configure storage, and create a test download plus a recognizable app setting.
- [ ] Make a dataset snapshot/backup and record the current app revision, image, settings, and data.
- [ ] Apply the newer catalog revision/image through the 25.10 Apps UI.
- [ ] Confirm the app returns to **Running**, the portal works, the setting and files remain intact, and a new download succeeds.
- [ ] Review app events/logs for failed migrations, permission errors, or restart loops.

### Rollback

- [ ] After the successful upgrade, use the rollback option exposed by the installed-app UI (or the supported 25.10 app rollback API if the UI does not expose it) to return to the recorded prior revision.
- [ ] Confirm the prior revision/image is active and the app reaches **Running**.
- [ ] Verify the portal, saved setting, existing files, and a new test download. Record any data/schema incompatibility; restore the pre-upgrade snapshot if recovery is needed.
- [ ] If no prior revision is offered, mark rollback **not testable** for this catalog state and explain that rollback requires a prior successful app update/version. Do not claim rollback passed without exercising it.

