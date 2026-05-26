# TrueNAS Apps Repository

## What This Repo Is

Community-contributed app definitions for the TrueNAS app catalog. Each app is a self-contained directory under `ix-dev/community/{app-name}/` that generates a Docker Compose file via a Jinja2 template and a Python rendering library.

## Repository Layout

```
ix-dev/
  community/        ← All new contributions go here
  stable/           ← iXsystems-managed, do not edit
  enterprise/       ← iXsystems-managed, do not edit
library/
  2.3.5/            ← Current rendering library (use this version)
  hashes.yaml       ← SHA256 integrity hashes per version
trains/             ← Auto-generated catalog, do NOT edit
catalog.json        ← Auto-generated, do NOT edit
CONTRIBUTIONS.md    ← Full contributor guide
```

## App Directory Structure (Required)

```
ix-dev/community/{name}/
├── app.yaml                          # App metadata
├── ix_values.yaml                    # Static images + constants
├── questions.yaml                    # User configuration schema (UI form)
├── item.yaml                         # Auto-generated catalog entry (do not hand-edit)
├── README.md                         # One-liner description + upstream link
├── app_migrations.yaml               # Optional: version migration definitions
├── migrations/                       # Optional: Python migration scripts
└── templates/
    ├── docker-compose.yaml           # Jinja2 template — the main render logic
    ├── library/base_v2_3_5/          # Auto-copied from /library/2.3.5/ (do not edit)
    ├── rendered/                     # Gitignored: output of render run
    └── test_values/
        └── basic-values.yaml         # CI test configuration (required)
```

## Rendering Library Pattern

Every `docker-compose.yaml` template follows this pattern:

```jinja2
{% set tpl = ix_lib.base.render.Render(values) %}

{# Create internal network #}
{% set app_net = tpl.networks.create_internal("app-net") %}

{# Set up permission init container #}
{% set perm_container = tpl.deps.perms(values.consts.perms_container_name) %}
{% set perms_config = {"uid": values.run_as.user, "gid": values.run_as.group, "mode": "check"} %}

{# Set up PostgreSQL #}
{% set pg_config = {"user": values.consts.db_user, "password": values.app.db_password, "database": values.consts.db_name, "volume": values.storage.postgres_data} %}
{% set postgres = tpl.deps.postgres(values.consts.postgres_container_name, values.app.postgres_image_selector, pg_config, perm_container) %}
{% do postgres.container.add_network(app_net) %}

{# Set up Redis #}
{% set redis_config = {"password": values.app.redis_password, "volume": {"type": "temporary", "volume_config": {"volume_name": "redis-data"}}} %}
{% set redis = tpl.deps.redis(values.consts.redis_container_name, "redis_image", redis_config, perm_container) %}
{% do redis.container.add_network(app_net) %}

{# Main app container #}
{% set app = tpl.add_container(values.consts.app_container_name, "image") %}
{% do app.add_network(app_net) %}
{% do app.set_user(values.run_as.user, values.run_as.group) %}
{% do app.depends.add_dependency(values.consts.postgres_container_name, "service_healthy") %}
{% do app.depends.add_dependency(values.consts.redis_container_name, "service_healthy") %}
{% do app.healthcheck.set_test("http", {"port": 9000, "path": "/api/v1/ping"}) %}
{% do app.add_port(values.network.web_port) %}
{% do app.add_storage("/data", values.storage.data) %}
{% do perm_container.add_or_skip_action("data", values.storage.data, perms_config) %}

{# Activate perms container if needed #}
{% if perm_container.has_actions() %}
  {% do perm_container.activate() %}
  {% do postgres.add_dependency(values.consts.perms_container_name, "service_completed_successfully") %}
{% endif %}

{% do tpl.portals.add(values.network.web_port) %}
{{ tpl.render() | tojson }}
```

## Key Conventions

- **lib_version** in `app.yaml` must be `2.3.5` (current latest)
- **`lib_version_hash`** in `app.yaml` must match `library/hashes.yaml` for version 2.3.5: `c0d042e3de6350fae9aee546d3c79bc0accf1f2011da89cc1ebff29421aa7fc9`
- Image keys in `ix_values.yaml` must end with `_image`
- Variables in `questions.yaml` use `snake_case`
- Sensitive fields need `private: true` in schema
- Mark immutable fields (set-once) with `immutable: true`
- Use `show_if` for conditional fields
- PostgreSQL image selector pattern: support both `postgres_17_image` and `postgres_18_image`
- `run_as_context` in `app.yaml`: document each container's UID/GID
- Non-root preferred: uid/gid 999 for app containers, 999 for postgres, 0 for containers that need root
- Storage types: `ix_volume` (default), `host_path`, `nfs`, `cifs`, `temporary`
- Increment `version` in `app.yaml` on every change (start at `1.0.0`)
- Only modify files under `ix-dev/` or `library/`. Everything else is auto-generated.

## Testing an App

```bash
# Render-only validation (no deployment)
./.github/scripts/ci.py --app peertube --train community --render-only=true

# Full test with deployment
./.github/scripts/ci.py --app peertube --train community --wait=true
```

## PeerTube App

Located at `ix-dev/community/peertube/`. The develop branch has an initial copy of the
adventurelog app that needs to be fully rewritten for PeerTube.

### PeerTube Architecture

| Service    | Image                              | Role                      |
|------------|------------------------------------|---------------------------|
| peertube   | chocobozzz/peertube:production-bookworm | Main application     |
| postgres   | postgres:17-alpine / 18-alpine     | Database (standard, no PostGIS) |
| redis      | redis:7-alpine                     | Cache / job queue         |

- No nginx/certbot needed — TrueNAS handles TLS via its built-in reverse proxy
- No Postfix container — configure external SMTP via environment variables

### Key PeerTube Environment Variables

```
PEERTUBE_DB_HOSTNAME, PEERTUBE_DB_USERNAME, PEERTUBE_DB_PASSWORD, PEERTUBE_DB_NAME
PEERTUBE_REDIS_HOSTNAME, PEERTUBE_REDIS_AUTH
PEERTUBE_WEBSERVER_HOSTNAME, PEERTUBE_WEBSERVER_PORT, PEERTUBE_WEBSERVER_HTTPS
PEERTUBE_SECRET
PEERTUBE_ADMIN_EMAIL
PT_INITIAL_ROOT_PASSWORD
PEERTUBE_SMTP_HOSTNAME, PEERTUBE_SMTP_PORT, PEERTUBE_SMTP_USERNAME, PEERTUBE_SMTP_PASSWORD
PEERTUBE_SMTP_TLS, PEERTUBE_SMTP_FROM_ADDRESS
```

### PeerTube Storage

| Mount path | Purpose                              |
|------------|--------------------------------------|
| `/data`    | Videos, thumbnails, previews, uploads |
| `/config`  | `production.yaml` config file        |

### PeerTube Ports

| Port | Protocol | Purpose          | Required |
|------|----------|------------------|----------|
| 9000 | HTTP     | Web UI           | Yes      |
| 1935 | TCP      | RTMP live stream | Optional |

### PeerTube UID/GID

The official PeerTube Docker image uses user `peertube` with UID 999, GID 999.
The permissions init container must chown data/config volumes to 999:999.
