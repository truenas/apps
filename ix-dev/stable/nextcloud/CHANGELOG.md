# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## 1.6.0

### Added

- Get real client IP from proxies
    - Cloudflare IPs are pre-configured and toggleable
    - Proxies can be added following the [ngx_http_realip_module `set_real_ip_from`](https://nginx.org/en/docs/http/ngx_http_realip_module.html) format
    - The `real_ip_header` is configurable
- Show X-Real-IP in Nextcloud logs
