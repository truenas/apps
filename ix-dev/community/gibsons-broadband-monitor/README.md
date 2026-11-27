# Gibson's Broadband Monitor

Scheduled broadband speed and latency tests, availability checks, outage history, historical charts, CSV exports, optional ntfy alerts and 16 interface languages. Measurements and settings stay in a local SQLite database.

Set a dashboard password and a long session secret during installation. Full speed tests run hourly by default and consume internet data.

Optional Server Network Usage exposes the host /proc/1/net directory read-only. It measures one host interface including LAN transfers, not whole-household traffic or ISP billing usage. Allow two samples about a minute apart for usage totals. The container starts as root to prepare its dedicated data directory, then runs the application as UID/GID 10001.
