# Midnight Commander

[Midnight Commander](https://midnight-commander.org) is a powerful visual file manager accessible directly in your web browser, powered by [ttyd](https://github.com/topheman/ttyd).

It provides a full-featured two-panel text interface for browsing, copying, moving, and managing files on your TrueNAS system — no SSH client needed.

## Features

- Two-panel file manager interface
- Accessible via any web browser on port `7681`
- Automatically opens in the first mounted dataset on startup
- Supports keyboard shortcuts for fast navigation

## Storage

Mount one or more TrueNAS datasets as **Additional Storage**. The first mounted path will be automatically detected and opened in Midnight Commander when the container starts.

Example mount path: `/mnt/mypool/mydataset` → mount inside container as `/mydataset`

## Access

Open your browser and navigate to:

```
http://<truenas-ip>:7681
```

## Source

- Docker Hub: https://hub.docker.com/r/leonekwolfik/midnight-commander
- GitHub: https://github.com/leonekwolfik/mc