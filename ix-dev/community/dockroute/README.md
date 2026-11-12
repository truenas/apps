# DockRoute

[DockRoute](https://www.dockroute.dev) is External-DNS for plain Docker hosts:
it watches running containers, reads **dockroute.\*** labels and reconciles the
matching DNS records — and Cloudflare Tunnel routes — in a pluggable provider.
TXT-based ownership means it never alters records it cannot prove it manages.

<!-- x-readme:warnings:start -->

⚠️ **WARNING:** This app has access to the Docker socket, which gives it full control over all containers and effectively root access to the system.

Misconfiguration or a malicious update can compromise data integrity, security, or system stability. Install at your own risk.

<!-- x-readme:warnings:end -->
