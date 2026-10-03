# CloudGate

[CloudGate](https://github.com/Elias02345/CloudGate) is a self-hosted web UI
that manages Cloudflare Tunnels for you — publish homelab services from
behind CGNAT without port forwarding.

No configuration is required: an admin account and every secret are
generated on first boot. The optional local nginx reverse-proxy mode (an
alternative to Cloudflare Tunnel routing, picked per host) needs ports
80/443, which this package does not publish by default — add them under
Network Configuration → Additional Ports if you use that mode.
