# DockTail

[DockTail](https://docktail.org) - Label-based Tailscale Services for Docker containers.

DockTail watches the containers on this system and turns the ones with `docktail.*` labels into Tailscale Services.
It brings its own Tailscale sidecar, so the Tailscale app does not need to be installed.
Apps do not need published ports; DockTail connects to their container IPs directly.

Before installing, you need:

- A Tailscale auth key for the sidecar, allowed to apply the tags in **Advertise Tags** (default `tag:server`).
- A Tailscale OAuth client (recommended) or API key, so DockTail can create service definitions.
- `tagOwners` and `autoApprovers.services` entries in your tailnet policy.
  See [Tailscale Admin Setup](https://docktail.org/docs/tailscale-admin/).

To turn an app into a Tailscale Service, add these labels to its container
(for catalog apps, under **Labels Configuration**). Use the port the app listens on inside its container:

```text
docktail.service.enable=true
docktail.service.name=myapp
docktail.service.port=80
```

The app is then reachable at `http://myapp.<your-tailnet>.ts.net`.
The first time a service is advertised, it may need approval in the Services tab of the Tailscale admin console.

DockTail has no web interface. [DockTail Cloud](https://docktail.org/cloud/) monitoring is optional.

Documentation: https://docktail.org/docs/
License: [AGPL-3.0](https://github.com/marvinvr/docktail/blob/main/LICENSE)
