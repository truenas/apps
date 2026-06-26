# AE NetScope

AE NetScope is an open source LAN inventory and sysadmin network documentation web app.

It helps keep track of devices, IP and MAC records, subnets, VLANs, services, hardware notes, backups, users, audit history and operational health from a single web interface.

This TrueNAS app package runs AE NetScope with PostgreSQL and Valkey. Valkey is used as the Redis-compatible backend for session and rate-limit support.

## Install Notes

The installer exposes normal app settings instead of requiring manual environment variables.

Required values:

- Database Password: internal PostgreSQL password.
- Redis Password: internal Redis password.
- Session Secret: random value of at least 32 characters used to sign sessions.

Optional values:

- Public App URL must match the URL used to access AE NetScope.
- HTTPS Mode should stay disabled for plain HTTP access. Enable it only when AE NetScope is served through HTTPS, such as behind a reverse proxy.
- Additional Environment Variables can be used for AE NetScope options that are not exposed directly by the app form.

## Early Preview Notice

This app package targets AE NetScope `v0.1.4-alpha`. It is an early public preview and should be tested carefully before use with important production data.
