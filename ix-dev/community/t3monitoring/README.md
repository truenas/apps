# t3monitoring

A TYPO3 CMS instance running the [t3monitoring](https://github.com/georgringer/t3monitoring)
extension, used to monitor the health/version status of other TYPO3 sites.

This app packages the TYPO3 image + a MariaDB database + a scheduler sidecar
(t3monitoring's checks run as TYPO3 scheduler tasks, so nothing gets monitored
without it).

TLS is not terminated here — put a reverse proxy in front and it'll be trusted via
`X-Forwarded-Proto`.
