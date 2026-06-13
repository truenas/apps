# kestrel

kestrel is a self-hosted purchase planner that calendarizes e-commerce purchases based on your paydays and budget.

Paste a link from any supported store (Amazon, MercadoLibre, Aliexpress, IKEA, Walmart) and kestrel automatically extracts the price and schedules the purchase on an upcoming payday.

## Installation

Install via **Apps > Install From YAML** in the TrueNAS UI. Paste the contents of `app.yaml` or use the catalog entry if published.

### Required Configuration

| Setting | Value |
|---------|-------|
| App Name | `kestrel` |
| Version | See `app.yaml` |
| Timezone | Your local timezone |

### Storage

Mount a persistent volume at `/home/kestrel/data` for the SQLite database. The app runs as UID **568** (TrueNAS apps convention). If permissions errors occur, run a one-time init container:

```yaml
image: busybox:latest
command: ["chown", "-R", "568:568", "/home/kestrel/data"]
securityContext:
  runAsUser: 0
volumeMounts:
  - name: data
    mountPath: /home/kestrel/data
```

### Networking

| Port | Protocol | Description |
|------|----------|-------------|
| 8000 | TCP | Web UI |

The default portal configuration points to port 8000 with HTTP scheme.

## Containers

The app consists of up to two containers:

- **kestrel** — Main application (Go binary, ~15 MB image)
- **kestrel-scraper** — Optional Playwright sidecar for JavaScript-heavy sites (~300 MB image, runs on port 8001)

The scraper is only needed if you frequently scrape sites that rely on client-side rendering. Most stores (Amazon, IKEA, etc.) work with the built-in HTTP extractor.

## Updating

1. Stop the app in the TrueNAS UI
2. Update the image tag to the new version
3. Start the app

Database migrations run automatically on startup.

## Screenshots

Screenshots will be available in the official catalog listing.

## Source

- GitHub: [CaptDany/kestrel](https://github.com/CaptDany/kestrel)
- Docker Hub: [capndany/kestrel](https://hub.docker.com/r/capndany/kestrel)
