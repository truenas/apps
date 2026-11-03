# ClamAV clamdscan

[ClamAV clamdscan](https://github.com/bmartino1/clamav-alpine) is a one-shot filesystem malware scanner using ClamAV and clamdscan.

When started, the container updates virus signatures, starts clamd, scans the configured filesystem path, stores persistent scan logs, and exits when the scan completes.

The scan target is mounted read-only by default.

For source code and deployment documentation, see the [clamav-alpine GitHub repository](https://github.com/bmartino1/clamav-alpine).
