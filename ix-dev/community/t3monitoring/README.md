# T3 Monitoring

[t3monitoring](https://github.com/georgringer/t3monitoring) is a TYPO3 extension that
tracks the health of other TYPO3 installations — their core and extension versions,
and whether any of them are affected by a known security advisory. This app runs it
as a self-hosted TYPO3 instance you point your sites at.

Three containers: TYPO3 itself, a MariaDB database, and a scheduler. The monitoring
checks run as TYPO3 scheduler tasks, so nothing is collected without the scheduler
container.

## First start

The database is created automatically the first time the app starts — schema,
extensions, and the backend administrator you configure during installation. This
takes a minute or two, and the Web UI does not respond until it finishes.

The Web UI button opens `/typo3/`. The public frontend stays empty until you create
a page tree, which is not needed to use the monitoring backend.

## Maintenance

This app and its container image are maintained by
[undkonsorten](https://undkonsorten.com). The t3monitoring extension itself is
developed by [Georg Ringer](https://github.com/georgringer/t3monitoring).

## TLS

The container serves plain HTTP only. Put a reverse proxy in front to terminate TLS;
it is trusted via `X-Forwarded-Proto`. Enable **Force HTTPS for the TYPO3 backend**
only once every route reaches the app through that proxy — it redirects to a URL
without the published port, which breaks direct access.
