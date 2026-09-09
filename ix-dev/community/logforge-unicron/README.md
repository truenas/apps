# LogForge Unicron

[LogForge Unicron](https://www.logforge.dev/) is an all-in-one Docker UI for real-time logs, interactive terminals, custom alerts, notifications, automations, and file-system access.

LogForge requires writable access to `/var/run/docker.sock`. This grants the application host-level Docker control and is required for its interactive operations features.

Set **LogForge Hostname or IP Address** to the NAS address that browsers and remote agents will use, without a scheme or port. If using a hostname, configure DNS to resolve it to the NAS. LogForge includes this address in its HTTPS routing and certificate configuration; the Web UI portal uses the same address. The appliance creates its own certificate authority, so its certificates require client trust configuration.

The Web UI and agent mTLS listeners use the configured ports inside and outside the container. Their defaults are 30488 and 30489. Agents use the separate mTLS listener for authenticated communication. The ports must differ and cannot overlap the appliance's bundled database, telemetry, certificate authority, and internal API services; invalid choices are rejected when rendering.

The application creates a bridge network scoped to the installed app name. Generated local-agent installation commands join this network and reach `unicron.central` through its Docker DNS alias. The appliance's loopback host entries connect its bundled Central and certificate authority services. Host networking is not offered because those services require their own network namespace.

Persist `/var/lib/unicron` to retain databases, telemetry, configuration, credentials, and certificates. Additional storage can mount other datasets or shares at separate paths. The appliance runs as root to supervise its bundled services, and self-updates are disabled so TrueNAS manages container updates.
