# DockRoute

[DockRoute](https://www.dockroute.dev) is External-DNS for plain Docker hosts:
it watches running containers, reads **dockroute.\*** labels and reconciles the
matching DNS records — and Cloudflare Tunnel routes — in a pluggable provider.
TXT-based ownership means it never alters records it cannot prove it manages.

<!-- x-readme:warnings:start -->

**!!! WARNING !!!**

This application requires additional elevated permissions beyond standard containerization protections. Use at your own risk.

The following additional privileges may be enabled from installing this application:

• Docker Socket Access

• Host Networking

<!-- x-readme:warnings:end -->
