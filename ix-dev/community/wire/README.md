# Wire Private Server for TrueNAS

This package installs a private Wire username directory, encrypted packet relay,
backups, and the Wire status web UI. By default it only becomes reachable on
networks that can already reach the TrueNAS host; it does not configure a router,
UPnP, or public DNS. An optional authenticated TURN relay can be enabled in the
install form when the owner supplies its public hostname plus the NAS public and
private IPv4 addresses.

Every GitHub server release publishes a new container and updates this catalog
definition to its immutable verified digest. TrueNAS then reports an available
app upgrade. Applying it replaces only the containers; the account database,
server identity, messages awaiting delivery, and backups remain in `/data`.
Wire deliberately does not mount the Docker socket or silently replace a running
server, because either approach can compromise the NAS or corrupt state.

After installation, every client that should share this private community runs:

```text
/private 192.168.1.50
```

Replace the example with the TrueNAS LAN address. Tailscale users enter the
TrueNAS Tailscale IP or MagicDNS name instead. `/public` returns a client to the
normal public Wire directory. A server identity is pinned separately for every
host and port, so a changed server key is refused rather than silently trusted.

Only TCP port `47666` is required for private chat, discovery, groups, encrypted
file relay, and screen-share signaling. The web UI defaults to port `30097` and
appears as a clickable portal on the installed app. Calls and screen sharing can
connect directly on a LAN or Tailscale network. Difficult public NAT setups can
use the built-in optional Coturn service. Wire generates and shares its secret
only inside the rendered server and Coturn containers. Public TURN also requires
router forwards for TCP/UDP `3478` and UDP `49160-49200`.

This directory is a separate account namespace. Existing local Wire identities
can register on it, but encrypted cross-device recovery exists only after that
identity has connected and uploaded its backup to this server.
