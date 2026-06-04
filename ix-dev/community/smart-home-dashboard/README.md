# Smart Home Dashboard

[Smart Home Dashboard](https://github.com/Daddelgreis74/smart-home-dashboard) is a modern smart home wall panel featuring customizable themes, Fritz!Box call monitor, Tasmota device management, weather data, waste calendar, and live radio.

## Configuration

The following environment variables are set automatically by the installation wizard:

- `PORT` - The port the dashboard listens on (configured in Network settings)
- `HOST` - Set to `0.0.0.0` (listens on all interfaces inside the container)
- `DATA_DIR` - Path to the persistent data directory

You can add custom environment variables through the **Additional Environment Variables** section during installation.

## Persistent Data

All configuration files are stored in the mounted data volume and persist across updates:

| File / Directory | Description |
| :--- | :--- |
| `tasmota.json` | Tasmota device configurations |
| `radio.json` | Web radio stations |
| `cameras.json` | Camera stream configurations |
| `fritzbox.json` | Fritz!Box connection credentials |
| `fritzbox_calls.json` | Call monitor history |
| `presence.json` | Presence detection settings |
| `uploads/` | Uploaded waste calendar files (`.ics`) |
| `ssl/` | Optional SSL certificates (`key.pem`, `cert.pem`) |

## SSL / HTTPS

To enable HTTPS, place `key.pem` and `cert.pem` files in the `ssl/` subdirectory
of your data volume. The dashboard will automatically detect and use them.
If no certificates are found, the dashboard falls back to HTTP.
