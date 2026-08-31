# ScarletX

ScarletX is a self-hosted adult scene management and automation platform focused on scenes, performers, studios, TPDB metadata, monitoring, downloading, imports, and local-library playback.

This TrueNAS Community Apps definition deploys the official ScarletX 0.3.8 backend and Nginx web containers from GitHub Container Registry. Nginx is the only public HTTP entrypoint; the FastAPI backend remains private on the app network.

Persistent storage is attached to the backend for:

- `/config` — database, cache, generated artwork, and application state
- `/downloads` — incomplete, completed, and failed downloads
- `/media` — permanent scene library
- `/backups` — database backups

Additional ixVolume, host-path, SMB/CIFS, and NFS mounts remain available for the backend. ScarletX containers run as a configurable non-root user/group by default and do not require additional Linux capabilities.
