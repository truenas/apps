# HAMAL

[HAMAL](https://github.com/i1k3r/HAMAL-TRUENAS) is a fast, private, temporary point-to-point local file transfer application.

## Features

- **Ephemeral Transfer Rooms**: Create temporary rooms with customizable lifespan (TTL).
- **Direct P2P Local Transfers**: High-speed point-to-point transfers directly across your local network without third-party cloud routing.
- **PIN Authentication & QR Connect**: Secure participant access with optional 8-digit PINs and mobile-friendly QR codes.
- **Automatic Lifecycle & Cleanup**: Automated countdown and secure purge of all files and SQLite metadata upon room closure or expiry.
- **Hardened Security**: Runs unprivileged (`10001:10001`) with read-only root filesystem, `no-new-privileges`, and in-memory `/tmp` buffer.

## Configuration & Storage

- **WebUI Port**: Default port `7700`.
- **Persistent Data**: Stores database and active room files in `/data`. The application runs as UID/GID `10001:10001`.
