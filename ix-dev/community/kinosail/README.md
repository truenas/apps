# Kinosail

Kinosail Player streams media from your own storage. Kinosail Subtitles finds and saves subtitle files next to media.

Choose **Player**, **Subtitles**, or **Both**. Select an existing media dataset. Player mounts it read only. Subtitles needs write access to save files. Both services run as UID/GID 10001, so grant this user access to the dataset. The installer creates separate app state volumes for each service.

Open Player at HTTPS port 38127 and Subtitles at HTTPS port 38128, unless you change the ports. Your browser may show a certificate warning on first use. [Kinosail setup guide](https://kinosail.com/getting-started/platforms/) explains the local network setup.

Kinosail is source available under the [PolyForm Perimeter License 1.0.1](https://github.com/Kinosail/kinosail/blob/main/LICENSING.md). The current container channel is `latest`; numbered releases have not been published.
