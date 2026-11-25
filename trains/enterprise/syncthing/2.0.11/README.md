# Syncthing

[Syncthing](https://syncthing.net/) is a file synchronization program.

At each startup of the application, the following settings are applied:

Disable automatic upgrades.

Disable anonymous usage reporting.

Disable NAT traversal.

Disable global discovery.

Disable local discovery.

Disable relaying.

Disable announcing LAN addresses.

Additionally, the following defaults are set for new syncthing "folders":

Max total size of **xattr**: 10 MiB.

Max size per **xattr**: 2 MiB.

Enable **send** and **sync** of **xattr**.

Enable **send** and **sync** of **ownership**.

Ignore permissions.

No default folder path.

<!-- x-readme:warnings:start -->

**!!! WARNING !!!**

This application requires additional elevated permissions beyond standard containerization protections. Use at your own risk.

The following additional privileges may be enabled from installing this application:

• Extended System Capabilities

• Host Networking

<!-- x-readme:warnings:end -->
