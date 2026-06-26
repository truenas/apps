# Restic Manager

The [Restic Manager](https://codeberg.org/echocat/truenas-restic-manager) is a web-based TrueNAS backup manager that discovers datasets, creates ZFS snapshots, runs scheduled restic backups, and keeps persistent run history.

The configured web port accepts plain HTTP, but it also serves HTTPS on the same port using the TrueNAS UI certificate by default.

If you run it behind a reverse proxy, configure `TRM_UPSTREAM_TRUSTED_ADDRESS` so forwarded client IPs and optional `X-Forwarded-Prefix` values are honored.
