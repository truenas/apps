# Fodaris

[Fodaris](https://fodaris.co.uk) - Self-hosted monitoring and observability for servers, containers, websites, network devices and databases. One container with PostgreSQL bundled in.

## What it monitors

- **Endpoints**: CPU, memory, disk, network, GPU and temperature across Linux, Windows and macOS via lightweight native agents
- **Containers**: per-container resource usage for Docker and Podman
- **Websites and APIs**: HTTP/HTTPS availability, response time, status codes, SSL expiry
- **Databases**: PostgreSQL, MySQL, MariaDB, Redis, MongoDB, MSSQL, Oracle, SQLite
- **Applications**: Nginx, Apache, HAProxy, Caddy, IIS, Tomcat
- **Network devices**: SNMP v1/v2c/v3 for switches, routers, firewalls and NAS
- **Logs**: centralised log shipping with search and redaction
- **IPAM**: IP address allocation tracking and subnet scanning

## Key features

- Built-in PostgreSQL database - no external DB required
- Encryption at rest for credentials and sensitive labels (key auto-generated on first boot)
- Real-time dashboards with per-endpoint customisation
- Alerts via email, Slack, Discord, Microsoft Teams, PagerDuty, ntfy and webhooks
- Backup schedules (local and S3-compatible)
- Multi-factor authentication and role-based access control
- Native agents for Linux, macOS, Windows and Docker

## First-time setup

After the app starts, open the Web UI (default port 8443) and sign in with:

- Username: `admin`
- Password: `Fodaris2026`

You will be required to change the password on first sign-in.

## Licensing

The free tier includes 5 endpoints, 5 websites, 5 databases and 5 applications. Paid tiers available at [fodaris.co.uk/pricing](https://fodaris.co.uk/pricing.html).

## Sources

- Website: [fodaris.co.uk](https://fodaris.co.uk)
- Documentation: [docs.fodaris.co.uk](https://docs.fodaris.co.uk)
- Live demo: [demo.fodaris.co.uk](https://demo.fodaris.co.uk)
- Docker Hub: [goodhallsolutions/fodaris](https://hub.docker.com/r/goodhallsolutions/fodaris)
- Community Discord: [discord.gg/9HN47kBFgm](https://discord.gg/9HN47kBFgm)
