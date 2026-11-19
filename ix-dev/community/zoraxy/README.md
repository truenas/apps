# Zoraxy

[Zoraxy](https://zoraxy.aroz.org/) A general purpose HTTP reverse proxy and forwarding tool.

<!-- x-readme:warnings:start -->

⚠️ **WARNING:** This app announces itself over mDNS (Bonjour) on the host network (when enabled), which can conflict with the system's own mDNS and disrupt discovery of TrueNAS and its services (such as its .local name, SMB and Time Machine).

⚠️ **WARNING:** This app has access to the Docker socket, which gives it full control over all containers and effectively root access to the system.

Misconfiguration or a malicious update can compromise data integrity, security, or system stability. Install at your own risk.

<!-- x-readme:warnings:end -->
