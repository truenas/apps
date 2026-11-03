# Plex DB Repair

[Plex DB Repair](https://github.com/bmartino1/plex-dbrepair-docker) is a one-shot Plex database maintenance utility using ChuckPa DBRepair.

The application discovers a running Plex Docker container through the host Docker socket, performs the selected database maintenance operation, writes persistent logs, and exits when finished.

A running Plex installation is required before starting this application.

The application may stop the Plex Media Server process during maintenance and can restart the Plex container after successful completion.

The Docker socket grants this application host-level Docker control. Verify Plex database backups before performing maintenance.

This application is intentionally configured as a one-shot job and does not automatically restart after completion.

For source code and deployment documentation, see the [plex-dbrepair-docker GitHub repository](https://github.com/bmartino1/plex-dbrepair-docker).

<!-- x-readme:warnings:start -->

⚠️ **WARNING:** This app has access to the Docker socket, which gives it full control over all containers and effectively root access to the system.

Misconfiguration or a malicious update can compromise data integrity, security, or system stability. Install at your own risk.

<!-- x-readme:warnings:end -->
