# DockTail

[DockTail](https://docktail.org) - Label-based Tailscale Services for Docker containers.

DockTail watches the containers on this system and turns the ones with `docktail.*` labels into Tailscale Services.
Apps do not need published ports; DockTail connects to their container IPs directly.

DockTail needs a Tailscale node to put the services on. Pick one under **Tailscale Mode**:

- **TrueNAS Tailscale App** (default): reuse the Tailscale app you already run.
  In the Tailscale app, set **Tailscale Socket Storage** to **Host Path** (an empty directory),
  enter the same directory as DockTail's **Tailscale Socket Directory**, and give the node a tag,
  for example **Extra Arguments** `--advertise-tags=tag:server`. Keep the Tailscale app on host networking (its default).
- **Sidecar**: DockTail runs its own Tailscale container, for systems without the Tailscale app.
  It needs an auth key allowed to apply the tags in **Advertise Tags** (default `tag:server`).
  **Host Network** (on by default) lets the sidecar reach every app; turn it off to join only the networks you list.

Before installing, you need:

- Optionally, a Tailscale OAuth client (recommended) or API key, so DockTail can create service definitions.
  Without one, you create each service in the Tailscale admin console yourself.
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
