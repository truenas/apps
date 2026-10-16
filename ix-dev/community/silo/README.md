# Silo

[Silo](https://siloserver.org/) is a self-hosted media server for films, series, audiobooks, ebooks, podcasts, and manga, with a web client and Jellyfin-compatible APIs.

The app deploys Silo in integrated mode with PostgreSQL 18 (pgvector) and Valkey (a Redis-compatible cache). Set an encryption secret generated with `openssl rand -base64 48`, and back it up separately from the database. The database password can be generated with `openssl rand -hex 24`.

Add your media under Additional Storage, for example mounted read-only at `/mnt/media`. Catalog seeds can optionally be mounted read-only at `/catalog-seeds`.

Silo listens on container ports `8080` (web), `8096` (Jellyfin-compatible API), and `13378` (Audiobookshelf-compatible API). Silo does not expose an HTTPS listener; terminate TLS at a reverse proxy if needed.

When search is enabled, Meilisearch is reachable from Silo at `http://meilisearch:7700`.

Jellyfin Web UI assets are installed separately from Silo's Compatibility settings. The installation needs a memory limit of at least 6144 MB.

The PostgreSQL tuning profile defaults to `auto`; set `POSTGRES_TUNE` in Additional Environment Variables to use another profile supported by Silo.

Upstream compose sources:

- [Silo](https://raw.githubusercontent.com/Silo-Server/silo-server/main/docker-compose.yml)
- [Silo NVIDIA settings](https://raw.githubusercontent.com/Silo-Server/silo-server/main/docker-compose.nvidia.yml)
- [Silo VA-API settings](https://raw.githubusercontent.com/Silo-Server/silo-server/main/docker-compose.vaapi.yml)
