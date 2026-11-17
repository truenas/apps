# NAS Doctor

[NAS Doctor](https://github.com/mcdays94/nas-doctor) is a local diagnostic and monitoring tool for your NAS.

It runs periodic health checks on SMART data, disk usage, Docker containers, GPU, process CPU usage,
network speed, ZFS pools, UPS power and tunnels, then reports findings with recommendations
backed by Backblaze drive failure rates.

The container shares the host PID namespace so Top Processes can see every host process
and match it to its Docker container.

To monitor the disk space of a pool or dataset, add it under Additional Storage as a read only
Host Path with a mount path under /host/mnt (for example /host/mnt/tank).

<!-- x-readme:warnings:start -->

⚠️ **WARNING:** This app has access to the Docker socket, which gives it full control over all containers and effectively root access to the system.

Misconfiguration or a malicious update can compromise data integrity, security, or system stability. Install at your own risk.

<!-- x-readme:warnings:end -->
