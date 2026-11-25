# DockTail

[DockTail](https://docktail.org) turns Docker containers with docktail labels into Tailscale Services.

DockTail uses the node of the TrueNAS Tailscale app. In the Tailscale app, set **Tailscale Socket Storage**
to a Host Path, and use the same path as DockTail's **Tailscale Socket Storage**.

Your tailnet policy needs tagOwners and autoApprovers.services entries for the node's tag.
See the [Tailscale admin setup](https://docktail.org/docs/tailscale-admin/).

<!-- x-readme:warnings:start -->

**!!! WARNING !!!**

This application requires additional elevated permissions beyond standard containerization protections. Use at your own risk.

The following additional privileges may be enabled from installing this application:

• Docker Socket Access

• Host Networking

<!-- x-readme:warnings:end -->
