# Plex DB Repair

One-shot Plex database repair and backup job; expected to exit after completion.

Source: [Apps/plex-dbrepair](https://github.com/bmartino1/bmartino1TrueNasCharts/tree/main/Apps/plex-dbrepair).

WARNING: This one-shot utility requires Docker socket access and may stop or restart Plex. A completed exit is expected; don't treat it as a long-running service.

Experimental and unsupported TrueNAS SCALE 25.10 test VM application. Validate installation and runtime before production use.

<!-- x-readme:warnings:start -->

⚠️ **WARNING:** This app has access to the Docker socket, which gives it full control over all containers and effectively root access to the system.

Misconfiguration or a malicious update can compromise data integrity, security, or system stability. Install at your own risk.

<!-- x-readme:warnings:end -->
