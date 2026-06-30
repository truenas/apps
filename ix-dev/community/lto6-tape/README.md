# LTO-6 Tape Manager

Manages LTO-6 tape drives (LTFS) on TrueNAS SCALE — orchestrated mount/eject, auto-mount on tape insertion, auto-eject on physical button press, with a mandatory pre-tape buffer and Prometheus monitoring.

## Prerequisites

### 1. Host LTFS service (required)

The container controls tape operations by sending `systemctl` commands to the host via the DBus socket (`/var/run/dbus`). The corresponding host systemd service must be installed **before** deploying this app.

Follow the installation guide at: https://github.com/eddiejdi/truenas-lto6-app

Quick install (run as root on TrueNAS host):

```bash
# Download and run the host asset installer
curl -fsSL https://raw.githubusercontent.com/eddiejdi/truenas-lto6-app/main/host-assets/install.sh | bash
```

This installs:
- `ltfs-lto6.service` — LTFS FUSE mount for the primary drive
- `ltfs-lto6b.service` — LTFS FUSE mount for the secondary drive (optional)
- Supporting scripts: `ltfs_recovery.py`, `ltfs-fc-stable-start`, `lto6-resolve-device`

### 2. Pre-tape buffer dataset (required)

Create a dedicated ZFS dataset for the staging area before deploying:

```bash
zfs create tank/pretape/lto6-cache
```

This path must be set in the **Pre-Tape Buffer** section of the app configuration.

### 3. Device names

Find your tape device names on the TrueNAS host:

```bash
lsscsi -g
```

Look for entries of type `tape` and `mediumx`. Typical values:
- SCSI generic: `/dev/sg4` (for `lsscsi` type `tape`)
- No-rewind tape: `/dev/nst1`

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| SCSI Generic Device | `/dev/sg4` | Host device for the tape drive |
| No-rewind Tape Device | `/dev/nst1` | Host no-rewind device |
| Pre-tape buffer path | _(required)_ | ZFS dataset for staging |
| Buffer min free (GiB) | 30 | Mount blocked below this |
| Buffer gate (%) | 80 | New drain jobs blocked above this |
| Buffer kill (%) | 88 | Active writes aborted above this |
| LTFS mount point | `/mnt/tape/lto6` | Where LTFS is mounted on the host |
| Auto-mount on insert | `true` | Mount tape when inserted |
| Auto-eject on button | `true` | Safe unmount + eject on button press |
| Orchestrator port | `9877` | REST API port |
| Exporter port | `9125` | Prometheus metrics port |

## Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 9877 | HTTP | Orchestrator REST API |
| 9125 | HTTP | Prometheus metrics exporter |

## Prometheus Metrics

The exporter publishes the following metrics on `:9125/metrics`:

| Metric | Description |
|--------|-------------|
| `lto6_app_buffer_bytes_free` | Buffer free space in bytes |
| `lto6_app_buffer_pct_used` | Buffer used percentage |
| `lto6_app_buffer_gate_ok` | 1 if buffer gate is open (usage < gate_pct) |
| `lto6_app_mount_up` | 1 if LTFS is currently mounted |
| `lto6_app_service_up` | 1 if host ltfs service is active |
| `lto6_app_button_watch_up` | 1 if button-watch thread is running |
| `lto6_app_drive_temp_celsius` | Tape drive temperature |

## Orchestrator API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health |
| `/status` | GET | Current mount and buffer state |
| `/mount` | POST | Mount tape (blocked if buffer gate exceeded) |
| `/unmount` | POST | Unmount tape cleanly |
| `/eject` | POST | Unmount and physically eject tape |
| `/deep-recovery` | POST | Run deep recovery on a damaged tape |

## Architecture

```
┌─────────────────────────────────────────────┐
│  TrueNAS Host                               │
│                                             │
│  ltfs-lto6.service (FUSE mount, systemd)    │
│  /dev/sg4, /dev/nst1, /dev/fuse            │
│  /var/run/dbus ──────────────────────┐     │
└──────────────────────────────────────│──────┘
                                       │ DBus
┌──────────────────────────────────────│──────┐
│  LTO-6 Tape Manager (Docker)         │     │
│                                       ▼     │
│  button_watch ──► dbus-send systemctl       │
│  orchestrator_api :9877                     │
│  exporter :9125                             │
└─────────────────────────────────────────────┘
```

The LTFS FUSE stack runs on the **host** as a systemd service. The container uses the DBus socket to start/stop/restart it — the same approach used by [Steam Headless](https://github.com/Steam-Headless/docker-steam-headless) in this catalog.

## Source

- App source: https://github.com/eddiejdi/truenas-lto6-app
- LTFS upstream: https://github.com/LinearTapeFileSystem/ltfs
