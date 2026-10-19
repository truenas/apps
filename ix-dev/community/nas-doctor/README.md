# NAS Doctor

[NAS Doctor](https://github.com/mcdays94/nas-doctor) is a local diagnostic and monitoring tool for your NAS.
It runs periodic health checks — analyzing SMART data, disk usage, Docker containers,
GPU, process CPU usage, network speed, ZFS pools, UPS power, tunnels, and more — then
surfaces findings with actionable recommendations backed by Backblaze failure rate data.

## Features

- 20+ diagnostic rules with automatic root-cause correlation
- SMART health with Backblaze failure-rate thresholds (337k+ drives)
- Top Processes with Docker container attribution (cgroup v1 and v2)
- GPU monitoring (NVIDIA, Intel, AMD)
- Network speed test scheduling (Ookla CLI)
- Service checks (HTTP, TCP, DNS, Ping/ICMP, SMB, NFS, Speed)
- ZFS pool health, UPS/power monitoring
- Webhook alerts (Discord, Slack, Gotify, Ntfy)
- Prometheus metrics endpoint
- Multi-server fleet monitoring

## Notes

- Requires privileged access (`SYS_RAWIO` capability) for SMART health monitoring
- Host PID namespace sharing is enabled so Top Processes can see all host processes
  and match them to Docker containers via cgroup data
- `/dev` and `/sys` are mounted read-only for device access and GPU telemetry
