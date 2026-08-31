# ScarletX

ScarletX is a self-hosted adult scene management and automation platform focused on scenes, performers, studios, TPDB metadata, monitoring, downloading, imports, and local-library playback.

This TrueNAS Community Apps definition deploys the official ScarletX container from GitHub Container Registry and exposes the ScarletX web interface.

Persistent storage is available for:

- `/config` — database, cache, generated artwork, and application state
- `/downloads` — incomplete, completed, and failed downloads
- `/media` — permanent scene library
- `/backups` — database backups

ScarletX runs as a configurable non-root user/group by default and does not require additional Linux capabilities.
