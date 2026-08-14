# Gluetun VPN Client

Initial TrueNAS Community catalog implementation for [Gluetun](https://github.com/passteque/gluetun), a lightweight VPN client with built-in proxy services.

The container image runs as root by default, requires `NET_ADMIN` and `/dev/net/tun`, and persists state under `/gluetun`.

Upstream documentation:

- https://github.com/passteque/gluetun
- https://github.com/qdm12/gluetun-wiki

Catalog notes:

- Fixed internal service ports follow the image defaults.
- Host port publication remains configurable through the TrueNAS network questions.
- Additional provider-specific settings can be supplied through Additional Environment Variables.
