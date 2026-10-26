# PhValheim Server

PhValheim hosts multiple vanilla and modded Valheim worlds in one container. Manage worlds, mods, shared configuration, access lists, backups, restores, updates and logs in your browser. Choose mods from Thunderstore, Hexium or a local catalogue; the PhValheim client syncs each world's mods and shared settings before launching the game. Optional Hugin assistance and Vibes tools help build and package your own mods.

PhValheim is free and will always be free. Its creator makes no profit from PhValheim users or operators.

## Installation

Select a specific trusted host IP for the private admin interface. After installation, open **Admin UI** and complete the setup wizard with your Steam Web API key, public website hostname, game DNS and world base port. Set **Base Port** to the **Game UDP Base Port** chosen in the app configuration, which defaults to `25000`.

Each world reserves two consecutive UDP ports. The default of ten world slots publishes `25000–25019/udp`, with identical host and container ports. Keep every world's port pair inside the configured range, including when restoring existing data. Increase the range when you need additional worlds; resource needs depend on worlds, players and mods.

The **Player Website** portal serves players separately. Keep **Admin UI** restricted to a trusted network, VPN or SSH tunnel. Configure public website HTTPS with a reverse proxy and forward the required game UDP ports separately. The app uses bridge networking and does not publish its internal database or Supervisor listener.

## Storage

The data mount at `/opt/stateful` contains the database, worlds, games, mods, configuration, local catalogue and Vibes projects/toolchain. Preserve the whole mount through upgrades. A separate backup dataset at `/opt/stateful/backups` is enabled by default; it can be disabled to keep world backups under the main data mount.

World backup archives do not replace a consistent backup of the full application dataset. Stop the app for a consistent full-data backup or restoration. Existing host-path datasets must allow the image's root startup and service accounts to manage their files.

## Optional features

AI providers are optional. Players need their own copy of Valheim. Modded worlds use the PhValheim client on Windows, Linux or macOS; vanilla worlds use ordinary Valheim. Consoles cannot load PC mods.

Original PhValheim code owned by Brian Miller is licensed under MIT. Third-party components and media retain their own terms.

[Website](https://phvalheim.com) · [Documentation](https://brianmiller.github.io/phvalheim-server/) · [Product tour](https://brianmiller.github.io/phvalheim-server/start/tour/) · [Support](https://github.com/brianmiller/phvalheim-server/issues)
