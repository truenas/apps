# Donetick

Donetick is a self-hosted task and habit tracker that exposes its web UI on port 2021. The app stores configuration under `/config` and data under `/donetick-data`, both mapped to the host path you provide (defaults to `/mnt/tank/apps/donetick`, with `config` and `data` subdirectories). On first start, a default `selfhosted.yaml` is written to `/config` and a strong JWT secret is auto-generated unless you supply `DT_JWT_SECRET` via Additional Environment Variables (or other DT_* overrides) in the app form.
