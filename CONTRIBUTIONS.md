# Contributing to TrueNAS Apps Catalog

This guide will walk you through everything you need to know about
contributing a new application to the catalog, from understanding the
project architecture to submitting your first pull request.

## Table of Contents

- [Welcome & Project Overview](#welcome--project-overview)
- [Getting Started](#getting-started)
- [Project Architecture](#project-architecture)
- [Contributing a New Application](#contributing-a-new-application)
- [Configuration System Deep Dive](#configuration-system-deep-dive)
- [Templates and Rendering](#templates-and-rendering)
- [Local Testing](#local-testing)
- [Updates and Migrations](#updates-and-migrations)
- [Best Practices](#best-practices)
- [Submission Guidelines](#submission-guidelines)
- [Getting Help](#getting-help)

---

## Welcome & Project Overview

### What is TrueNAS Apps?

TrueNAS Apps is a Docker Compose-based application catalog that makes it
easy to deploy and manage containerized applications on TrueNAS systems.
Think of it as an app store for your TrueNAS server.

Users can browse, install, configure, and manage applications through a
friendly web interface without needing to write Docker Compose files manually.

### How It Works

The system uses a templating approach:

1. **App developers** (that's you!) define applications using a combination of metadata files (`app.yaml`),
   configuration schemas (`questions.yaml`), and Jinja2 templates (`docker-compose.yaml`)
2. **TrueNAS users** select an app from the catalog and fill out a form based on the questions you define
3. **The rendering system** processes your templates with the user's values and generates a standard Docker Compose file
4. **Docker Compose** deploys and manages the containers

### Our Mission

We aim to:

- Make self-hosting applications accessible to everyone, regardless of technical expertise
- Provide a curated, well-tested catalog of applications
- Enable easy application management with sensible defaults
- Support the open-source community by promoting and simplifying deployment of great applications

### Why Contribute?

By contributing an app to this catalog, you:

- Help TrueNAS users easily deploy applications they love
- Give back to the open-source community
- Gain experience with Docker, templating systems, and Python
- Connect with other app developers and the TrueNAS community

---

## Getting Started

### Prerequisites

Before you begin, make sure you have the following installed on your local machine:

#### Required Software

- **Git** - For cloning the repository
- **Docker** - To run containers locally
- **Docker Compose** - For orchestrating multi-container apps
- **Python 3.x** - The templating and testing system is written in Python
- **jq** - JSON processor used by the CI scripts

To avoid installing python (and its dependencies) on your system, you can install [**devbox**](https://www.jetify.com/devbox)
and use the provided `devbox.json` file to set up your environment:

```bash
devbox shell
```

#### Required Python Packages

> You can skip this if using devbox as described above.

Install these Python packages:

```bash
pip install pyyaml psutil pytest pytest-cov bcrypt pydantic
```

**Alternative using nix-shell** (if you have Nix installed):

```bash
nix-shell -p 'python3.withPackages (ps: with ps; [ pyyaml psutil pytest pytest-cov bcrypt pydantic ])'
```

### Cloning the Repository

```bash
git clone https://github.com/truenas/apps.git
cd apps
```

### Avoid Duplicate Work

Before starting work on an app:

1. **Check existing issues**: Someone might already be working on it
2. **Check existing PRs**: The app might already be in review
3. **Open an issue or comment**: Let others know you're working on it before starting work
4. **Open a draft PR**: This allows maintainers to catch any wrong directions early

### Repository Structure

Once cloned, you'll see this structure:

```txt
.
├── ix-dev/                   # App definitions
│   ├── community/            # Community-contributed apps (this is where you work!)
│   ├── stable/               # TrueNAS curated apps
│   ├── enterprise/           # Apps for enterprise users
│   ├── dev/                  # Development/testing
│   └── test/                 # Test apps
├── library/                  # Rendering library (Python modules)
│   └── 2.x.x/                # Library versions
├── trains/                   # Auto-generated catalog files (DO NOT EDIT)
├── docs/                     # Documentation
├── .github/                  # CI/CD scripts and workflows
│   └── scripts/
│       └── ci.py             # Local/CI testing script
└── README.md
```

**Important:** ⚠️ You should only modify files under `/ix-dev/` or `/library/` directories. All other files are auto-generated. ⚠️

### Understanding Trains

Apps are organized into "trains" (categories):

- **community**: Community-contributed apps - all new contributions go here
- **stable**: TrueNAS applications that are curated and maintained by TrueNAS team
- **enterprise**: Enterprise-grade applications maintained by iXsystems

All new contributions should target the `community` train. Other trains are managed by iXsystems maintainers.

---

## Project Architecture

### High-Level Overview

The TrueNAS Apps system follows this flow:

```txt
┌─────────────────┐
│  App Developer  │ ← You define the app structure
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  App Definition Files                           │
│  • app.yaml (metadata)                          │
│  • ix_values.yaml (static defaults)             │
│  • questions.yaml (user configuration schema)   │
│  • templates/docker-compose.yaml (Jinja2)       │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  TrueNAS User   │ ← User fills out configuration form
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  Rendering System                               │
│  • Merges ix_values.yaml + user values          │
│  • Processes Jinja2 template                    │
│  • Uses library functions (ports, storage, etc) │
│  • Validates configuration                      │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  Docker Compose File                            │
│  • Standard docker-compose.yaml                 │
│  • Contains all services, volumes, networks     │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Docker Engine  │ ← Deploys and manages containers
└─────────────────┘
```

### Component Architecture (Top-Down)

#### 1. App Directory Structure

Each app lives in `/ix-dev/{train}/{app}/` and has this structure:

```txt
/ix-dev/{train}/{app}/
├── app.yaml                    # App metadata (required)
├── item.yaml                   # Auto-generated catalog entry
├── ix_values.yaml              # Static default values (required)
├── questions.yaml              # User configuration schema (required)
├── README.md                   # Short app description (required)
├── app_migrations.yaml         # Migration definitions (optional)
├── migrations/                 # Migration scripts (optional)
│   └── migration_script        # Python migration script
└── templates/
    ├── docker-compose.yaml     # Jinja2 template (required)
    ├── library/                # Auto-copied library files (auto-generated)
    │   └── base_v2_x_xx/       # Library version (auto-generated)
    ├── rendered/               # Temporary (gitignored)
    │   └── docker-compose.yaml # Rendered compose file (auto-generated)
    └── test_values/            # CI test configurations (required)
        └── basic-values.yaml   # Basic test scenario (required)
```

#### 2. The Library System

The library (`/library/{version}/`) is a collection of Python modules that handle common tasks:

- **render.py**: Main orchestration—coordinates the entire rendering process
- **container.py**: Container configuration (image, command, environment, etc.)
- **storage.py**: Volume and mount management
- **ports.py**: Port mapping configuration
- **environment.py**: Environment variable handling
- **healthcheck.py**: Health check configuration
- **deps_*.py**: Pre-built common dependencies:
  - `deps_postgres.py`: PostgreSQL database
  - `deps_redis.py`: Redis cache
  - `deps_mariadb.py`: MariaDB database
  - `deps_perms.py`: Permission initialization container
  - And more...

The library provides a Python API that you use in your Jinja2 templates to generate Docker Compose configuration.

#### 3. The Rendering Process

When a user deploys an app:

1. **Value Collection**: User input from the UI form (based on `questions.yaml`) is collected
2. **Validation**: Middleware validates user input against the schema
3. **Value Merging**: User values are merged with `ix_values.yaml` defaults
4. **Template Processing**:
   - Jinja2 processes `templates/docker-compose.yaml`
   - Your template calls library functions to build configuration
   - Library returns structured data representing Docker Compose services
5. **Rendering**: The final Docker Compose YAML is generated
6. **Validation**: The compose file is validated against docker engine for spec correctness
7. **Deployment**: Docker Compose creates and starts the containers
8. **Monitoring**: Health checks ensure containers are running properly
9. **Portal Generation**: Web UI links are made available to the user

#### 4. The CI/CD Pipeline

The GitHub Actions CI/CD system:

- Validates all app definitions
- Runs tests against test values
- Publishes to the catalog (after PR is merged)

---

## Contributing a New Application

### Step-by-Step Process

#### Step 1: Find a Similar App

The easiest way to create a new app is to copy an existing one that's similar. Browse `/ix-dev/community/` to find an app with similar requirements:

- Similar number of containers (single app vs. app + database)
- Similar storage needs
- Similar networking requirements

```bash
# Example: Creating a new app based on qbittorrent
cd ix-dev/community
cp -r qbittorrent myapp
cd myapp
```

#### Step 2: Modify app.yaml

Update the app metadata in `app.yaml`:

```yaml
app_version: 2.1.0            # Upstream application version (ie the container image tag)
capabilities: []              # List any Linux capabilities needed (autogenerated using the generate metadata script)
categories:                   # Single category that best fits the app
- productivity
date_added: '2025-01-01'      # Date the app was added to TrueNAS
description: A brief description of what the app does
home: https://myapp.com       # Upstream homepage
host_mounts: []               # List any host mounts needed (usually for devices like /var/run/docker.sock)
icon: https://media.sys.truenas.net/apps/myapp/icons/icon.png
keywords:
- productivity
- tools
lib_version: 2.1.60           # Use the latest library version (check /library/)
lib_version_hash: ""          # Leave empty, will be auto-generated
maintainers:                  # TrueNAS is the only maintainer for now
- email: dev@ixsystems.com
  name: truenas
  url: https://www.ixsystems.com
name: myapp                   # Must match directory name
run_as_context:               # Metadata for user/group the app runs as (use 568 if it can run as any non-root user)
- description: MyApp runs as any non-root user
  gid: 568
  group_name: myapp
  uid: 568
  user_name: myapp
screenshots: []               # URLs to screenshots (hosted on TrueNAS CDN)
sources: []                   # Upstream source code repositories
title: My Awesome Application # Human-friendly app title
train: community              # Must match parent directory
version: 1.0.0                # App version (start at 1.0.0)
```

**Key fields:**

- `name`: Must exactly match your directory name
- `train`: Must match the parent directory (`community`, `stable`, etc.)
- `version`: Increment this whenever you make changes to the app
- `app_version`: The version of the upstream application
- `lib_version`: Use the latest non-v1 library version (check `/library/` directory)
- `run_as_context`: Metadata for user/group the app runs as (security best practice)

**About icons and screenshots:**

For icons and screenshots that will be hosted on the TrueNAS CDN,
include the URLs or attach the images in your PR description.
The PR reviewer will upload them to the CDN and provide you with the correct URLs.

#### Step 3: Define Static Values (ix_values.yaml)

This file contains values that are always used, not exposed to users:

Keys for the images must always end with `image`.

If the versioning of an image is not SemVer, a custom versioning regex must
be added in the renovate-config.js file to ensure proper updates.

Prefer `ghcr` over `docker.io` for images.

```yaml
images:
  image:
    repository: myorg/myapp
    tag: 2.1.0
  worker_image:
    repository: myorg/myapp-worker
    tag: 2.1.0

consts:
  app_container_name: myapp
  perms_container_name: myapp-perms
```

**Common patterns:**

- `images`: Define all container images and their tags
- `consts`: Constants used throughout your templates

#### Step 4: Create User Configuration Schema (questions.yaml)

This defines the form users see when configuring your app.

Most groups should exist across all apps. For example:

- My App Configuration (App-specific settings)
- User and Group Configuration (Can be skipped if the app can ONLY run as a specific uid/gid and users can't choose)
- Network Configuration
- Storage Configuration
- Labels Configuration
- Resources Configuration

Also keep in mind that most groups and their fields structure is "fixed" and cannot be changed.
Rendering library does lots of automated things based on this structure.

It uses a schema-based approach:

> This is a simplified example - with only few of the above mentioned groups.

```yaml
groups:
  - name: My App Configuration
    description: Configure MyApp Settings
  - name: Network
    description: Network Configuration
  - name: Storage
    description: Storage Configuration

questions:
  - variable: myapp
    label: ""
    group: My App Configuration
    schema:
      type: dict
      attrs:
        - variable: admin_email
          label: Administrator Email
          description: Email address for the administrator
          schema:
            type: string
            required: true
            default: "admin@example.com"
        - variable: enable_feature
          label: Enable Advanced Feature
          schema:
            type: boolean
            default: false
        - variable: additional_envs
          label: Additional Environment Variables
          schema:
            type: list
            default: []
            items:
              - variable: env
                label: Environment Variable
                schema:
                  type: dict
                  attrs:
                    - variable: name
                      label: Name
                      schema:
                        type: string
                        required: true
                    - variable: value
                      label: Value
                      schema:
                        type: string
  # Network Configuration
  - variable: network
    label: ""
    group: Network
    schema:
      type: dict
      attrs:
        # Also simplified, a port must have whole lot more attributes.
        # See other apps for full example.
        - variable: web_port
          label: Web Port
          description: Port for the web interface
          schema:
            type: dict
            attrs:
              - variable: port
                label: Port Number
                schema:
                  type: int
                  default: 8080
                  min: 1024
                  max: 65535
                  required: true

  # Storage Configuration
  - variable: storage
    label: ""
    group: Storage
    schema:
      type: dict
      attrs:
        # Also simplified, a storage must have whole lot more attributes.
        # See other apps for full example.
        - variable: config
          label: App Configuration Storage
          description: Stores application configuration
          schema:
            type: dict
            attrs:
              - variable: type
                label: Type
                schema:
                  type: string
                  default: "ix_volume"
                  enum:
                    - value: "host_path"
                      description: "Host Path"
                    - value: "ix_volume"
                      description: "TrueNAS Dataset"
              - variable: ix_volume_config
                label: Dataset Configuration
                schema:
                  type: dict
                  show_if: [["type", "=", "ix_volume"]]
                  attrs:
                    - variable: acl_enable
                      label: Enable ACL
                      schema:
                        type: boolean
                        default: false
              - variable: host_path_config
                label: Host Path Configuration
                schema:
                  type: dict
                  show_if: [["type", "=", "host_path"]]
                  attrs:
                    - variable: path
                      label: Host Path
                      schema:
                        type: hostpath
                        required: true
```

**Schema types available:**

- `string`: Text input
- `int`: Number input
- `boolean`: Checkbox
- `dict`: Nested configuration (object)
- `list`: Array of items
- `uri`: URL input
- `path`: File/directory path on the system
- `hostpath`: Path that must exist on the host

> And more...

**Important attributes:**

- `required`: Whether the field is mandatory
- `default`: Default value
- `min`/`max`: For numeric fields
- `min_length`/`max_length`: For string fields
- `enum`: List of allowed values
- `show_if`: Conditional display based on other field values
- `private`: Hides the value (for passwords)
- `hidden`: Completely hides the field but includes it in config

> And more...

#### Step 5: Create the Docker Compose Template

The `templates/docker-compose.yaml` file is a Jinja2 template that uses the library to generate configuration:

```yaml
{# First, initialize the rendering system #}
{% set tpl = ix_lib.base.render.Render(values) %}

{# Define the main application container #}
{% set app = tpl.add_container(values.consts.app_container_name, "image") %}
{% do app.set_user(values.run_as.user, values.run_as.group) %}
{% do app.healthcheck.set_test("curl", {"port": 8080, "path": "/health"}) %}

{# Configure environment variables #}
{% do app.environment.add_env("APP_PORT", values.network.web_port.port) %}
{% do app.environment.add_env("ADMIN_EMAIL", values.myapp.admin_email) %}

{# Add port mappings #}
{% do app.add_port(values.network.web_port) %}

{# Configure storage #}
{% do app.add_storage("/config", values.storage.config) %}

{# Setup permissions container for storage initialization #}
{% set perms = tpl.deps.perms(values.consts.perms_container_name) %}
{% do perms.add_or_skip_action("config", values.storage.config, {"uid": 568, "gid": 568, "mode": "check"}) %}

{% if perms.has_actions() %}
  {% do perms.activate() %}
  {% do app.depends.add_dependency(values.consts.perms_container_name, "service_completed_successfully") %}
{% endif %}

{# Add portal for UI access #}
{% do tpl.portals.add(values.network.web_port, scheme="http", path="/") %}

{# Render the final configuration #}
{{ tpl.render() | tojson }}
```

Explore other apps for more examples.

**Key library components:**

- `tpl.add_container(name, image_key)`: Creates a new container
- `app.set_user(uid, gid)`: Sets the user the container runs as
- `app.healthcheck.set_test()`: Configures health checks
- `app.environment.add_env()`: Adds environment variables
- `app.add_port()`: Maps ports to the host
- `app.add_storage()`: Mounts volumes
- `tpl.deps.perms()`: Creates a permissions init container
- `tpl.portals.add()`: Adds a web UI portal link

**Adding dependencies (database example):**

```yaml
{# Add PostgreSQL database #}
{% set pg_config = {
  "user": values.consts.db_user,
  "password": values.myapp.db_password,
  "database": values.consts.db_name,
  "volume": values.storage.postgres_data,
} %}
{% set postgres = tpl.deps.postgres("postgres", "postgres_image", pg_config, perms) %}
{% do app.depends.add_dependency("postgres", "service_healthy") %}
{# Use postgres.get_url() to generate the connection string #}
{% do app.environment.add_env("DATABASE_URL", postgres.get_url("postgresql")) %}
```

#### Step 6: Create Test Files

Create test value files in `templates/test_values/` to test different configurations:

**basic-values.yaml:**

```yaml
resources:
  limits:
    cpus: 2.0
    memory: 4096

# Should contain all options that are exposed in the questions.yaml
myapp:
  admin_email: test@example.com
  enable_feature: false
  additional_envs: []

network:
  web_port:
    bind_mode: published
    port_number: 30080 # Use a non-default port for testing, catches issues early

ix_volumes:
  test_myapp_config: /opt/tests/mnt/myapp/config

storage:
  config:
    type: ix_volume
    ix_volume_config:
      dataset_name: test_myapp_config
      create_host_path: true
```

**Note on test storage paths:**

Most apps use directories like `/opt/tests/**` for storage in test files. This is because:

- macOS whitelists `/opt/` by default for Docker
- Linux doesn't have this restriction
- It prevents accidentally mounting sensitive directories

Make sure your test files won't mount any directories you don't want them to!

#### Step 7: Create README.md

Keep the README brief - just a title and short description. Link to upstream documentation for details:

```markdown
# My Awesome Application

[My Awesome Application](https://myapp.com) is a tool for doing awesome things.
```

---

## Configuration System Deep Dive

### Understanding Values Hierarchy

When your template is rendered, values come from multiple sources merged in this order:

1. `ix_values.yaml` - Your static defaults
2. User input from `questions.yaml` (or test values during testing)

Access values in templates using: `values.path.to.variable`

---

## Templates and Rendering

### Template Structure

Every template follows this basic structure:

```yaml
{# 1. Initialize the rendering system #}
{% set tpl = ix_lib.base.render.Render(values) %}

{# 2. Add containers #}
{# 3. Configure containers #}
{# 4. Add dependencies #}
{# 5. Setup permissions #}
{# 6. Add portals #}

{# Final: Render the configuration #}
{{ tpl.render() | tojson }}
```

### Library API Reference

#### Adding a Container

```python
{% set app = tpl.add_container("container_name", "image_key") %}
```

- First argument: Container name (use value from `consts`)
- Second argument: Key in `ix_values.yaml` images section

#### Container Configuration

```python
{# Set user and group - usually picked automatically from run_as_context in app.yaml #}
{# Only set manually if you need to override the default #}
{% do app.set_user(568, 568) %}

{# Set entrypoint and command #}
{% do app.set_entrypoint(["myapp"]) %}
{% do app.set_command(["--config", "/config/app.conf"]) %}

{# Add environment variables #}
{% do app.environment.add_env("KEY", "value") %}
{% do app.environment.add_env("PORT", 8080) %}

{# Add port mappings #}
{% do app.add_port(values.network.web_port) %}

{# Add storage mounts #}
{% do app.add_storage("/config", values.storage.config) %}
{% do app.add_storage("/data", values.storage.data) %}

{# Set capabilities #}
{% do app.add_caps(["NET_ADMIN", "SYS_ADMIN"]) %}
```

#### Health Checks

```python
{# HTTP health check #}
{% do app.healthcheck.set_test("curl", {"port": 8080, "path": "/"}) %}

{# TCP health check #}
{% do app.healthcheck.set_test("netcat", {"port": 5432}) %}

{# Disable health check #}
{% do app.healthcheck.disable() %}
```

#### Dependencies

```python
{# Wait for service to be healthy #}
{% do app.depends.add_dependency("database", "service_healthy") %}

{# Wait for init container to complete #}
{% do app.depends.add_dependency("init", "service_completed_successfully") %}
```

#### Permissions Container

```python
{# Create permissions container #}
{% set perms = tpl.deps.perms("perms_container_name") %}
{% set perms_config = {"uid": 568, "gid": 568, "mode": "check"} %}

{# Add permission actions #}
{% do perms.add_or_skip_action("config", values.storage.config, perms_config) %}

{# Activate and add dependency #}
{% if perms.has_actions() %}
  {% do perms.activate() %}
  {% do app.depends.add_dependency("perms_container_name", "service_completed_successfully") %}
{% endif %}
```

**Permission modes:**

> Both modes will skip if the directory is not empty.

- `check`: Only fix if permissions are wrong
- `always`: Always set permissions

#### Common Dependencies

**PostgreSQL:**

```python
{% set pg_config = {
  "user": "myapp",
  "password": values.myapp.db_password,
  "database": "myapp_db",
  "volume": values.storage.postgres_data,
} %}
{% set postgres = tpl.deps.postgres("postgres", "postgres_image", pg_config, perms) %}
{% do app.depends.add_dependency("postgres", "service_healthy") %}
```

**Redis:**

```python
{% set redis_config = {
  "password": values.myapp.redis_password,
  "volume": values.storage.redis_data,
} %}
{% set redis = tpl.deps.redis("redis", "redis_image", redis_config, perms) %}
{% do app.depends.add_dependency("redis", "service_healthy") %}
```

**MariaDB:**

```python
{% set mariadb_config = {
  "user": "myapp",
  "password": values.myapp.db_password,
  "database": "myapp_db",
  "root_password": values.myapp.root_password,
  "volume": values.storage.mariadb_data,
} %}
{% set mariadb = tpl.deps.mariadb("mariadb", "mariadb_image", mariadb_config, perms) %}
{% do app.depends.add_dependency("mariadb", "service_healthy") %}
```

#### Portals

Portals create clickable links in the TrueNAS UI:

```python
{# Simple portal (HTTP, path="/") #}
{% do tpl.portals.add(values.network.web_port) %}

{# Custom portal #}
{% do tpl.portals.add(values.network.web_port, {"scheme": "https", "path": "/admin"}) %}

{# Multiple portals #}
{% do tpl.portals.add(values.network.web_port, {"scheme": "http"}) %}
{% do tpl.portals.add(values.network.api_port, {"name": "Custom Label", "path": "/api"}) %}
```

#### Notes

Add informational notes displayed to users:

```python
{% do tpl.notes.add_info("First time setup requires visiting /setup") %}
{% do tpl.notes.add_warning("This app requires GPU passthrough") %}
```

### What Gets Generated

Your template generates a standard Docker Compose file. Here's an example:

**Input (your template):**

```yaml
{% set tpl = ix_lib.base.render.Render(values) %}
{% set app = tpl.add_container(values.consts.app_container_name, "image") %}
{% do app.set_user(568, 568) %}
{% do app.add_port(values.network.web_port) %}
{% do app.healthcheck.set_test("curl", {"port": 8080, "path": "/ping"}) %}
{% do app.add_storage("/config", values.storage.config) %}
{{ tpl.render() | tojson }}
```

**Output (generated compose file):**

```yaml
services:
  myapp:
    cap_drop:
      - ALL
    deploy:
      resources:
        limits:
          cpus: 2
          memory: "4294967296"
    environment:
      GID: "568"
      GROUP_ID: "568"
      NVIDIA_VISIBLE_DEVICES: void
      PGID: "568"
      PUID: "568"
      TZ: Etc/UTC
      UID: "568"
      UMASK: "002"
      UMASK_SET: "002"
      USER_ID: "568"
    group_add:
      - "568"
    healthcheck:
      test:
        - CMD
        - curl
        - --request
        - GET
        - --silent
        - --output
        - /dev/null
        - --show-error
        - --fail
        - http://127.0.0.1:8080/ping
      timeout: 5s
      interval: 30s
      retries: 5
      start_period: 15s
      start_interval: 2s
    image: some-repo/myapp:2.1.0
    platform: linux/amd64
    ports:
      - mode: ingress
        target: 8080
        published: "8080"
        protocol: tcp
    restart: unless-stopped
    security_opt:
      - no-new-privileges=true
    user: 568:568
    volumes:
      - type: bind
        source: /opt/tests/mnt/config
        target: /config
        bind:
          propagation: rprivate
          create_host_path: true
x-notes: |
  # <app_name>

  ## Security

  **Read the following security precautions to ensure that you wish to continue using this application.**

  ---

  ### Container: [myapp]

  #### Running user/group(s)

  - User: 568
  - Group: 568
  - Supplementary Groups: apps

  ## Bug Reports and Feature Requests

  If you find a bug in this app or have an idea for a new feature, please file an issue at
  https://github.com/truenas/apps
x-portals:
  - host: 0.0.0.0
    name: Web UI
    path: /
    port: 8080
    scheme: http
```

---

## Local Testing

Before submitting your PR, thoroughly test your app locally using the CI script.

### Running Tests

The `.github/scripts/ci.py` script is your primary testing tool:

```bash
# Basic test - deploys the app and waits for it to be healthy
./.github/scripts/ci.py --app myapp --train community --test-file basic-values.yaml

# Keep the app running for manual testing
./.github/scripts/ci.py --app myapp --train community --test-file basic-values.yaml --wait=true
# or devbox run app-test community myapp <optionally basic-values.yaml>

# Just render the compose file without deploying
./.github/scripts/ci.py --app myapp --train community --test-file basic-values.yaml --render-only=true
# or devbox run app-render community myapp <optionally basic-values.yaml>
```

### Command Options

- `--app`: Your app directory name
- `--train`: The train (community, stable, etc.)
- `--test-file`: Which test file from `templates/test_values/` to use
- `--wait=true`: Keeps the app running until you stop it (Ctrl+C). Shows the web UI URL if available
- `--render-only=true`: Only renders the compose file without deploying

### What the CI Script Does

When you run the CI script, it automatically:

1. **Generates `item.yaml`**: Creates the catalog entry
2. **Updates library files**: Copies the correct library version to `templates/library/` based on `lib_version` in `app.yaml`
3. **Updates `lib_version_hash`**: Calculates and sets the hash in `app.yaml`
4. **Renders the template**: Processes your Jinja2 template with the test values
5. **Deploys with Docker Compose**: Starts the containers (unless `--render-only`)
6. **Monitors health**: Waits for containers to become healthy (times out after 10 minutes)

### Metadata Generation / Validation

```bash
# Generates some metadata (like capabilities) for your app
./.github/scripts/generate_metadata.py --app myapp --train community
# Validates ports in questions.yaml are unique
./.github/scripts/port_validation.py
```

### Testing Workflow

1. **Start with basic test:**

   ```bash
   ./.github/scripts/ci.py --app myapp --train community --test-file basic-values.yaml --wait=true
   ```

2. **Check the output:**
   - The script will show you the rendered compose file location
   - It will display the web UI URL if configured
   - Watch for any errors in container startup

3. **Verify functionality:**
   - Open the web UI in your browser
   - Test basic functionality
   - Check logs: `docker logs myapp`

4. **Test different configurations:**
   - Create additional test files if needed (e.g., `with-database-values.yaml`, `hostpath-values.yaml`)
   - Test each configuration thoroughly

5. **Clean up:**
   - Press Ctrl+C to stop (with `--wait=true`)
   - Or the script will auto-cleanup if it runs without `--wait`
   - Manual cleanup if needed: `docker compose -f /path/to/rendered/docker-compose.yaml down -v`

### Troubleshooting

**Containers won't start:**

- Check `docker logs <container_name>` for errors
- Verify image names and tags in `ix_values.yaml`
- Check port conflicts: `docker ps` to see if ports are already in use

**Permission errors:**

- Verify `set_user` in your template
- Check permissions container configuration
- Ensure storage paths are accessible

**Template errors:**

- Use `--render-only=true` to see the rendered compose file
- Check for Jinja2 syntax errors
- Verify all values paths exist in your test files

**Health checks failing:**

- Verify the health check command is correct
- Verify the application ships the binary used in the health check (ie `curl`, etc.)

### Testing on TrueNAS

Currently, there's no easy way to test directly on a TrueNAS system before your PR is merged. However:

- If it works on your local machine with Docker Compose, it should work on TrueNAS
- Exceptions include hardware-specific features (GPU, devices, etc.)
- Let the reviewer know about any special requirements in your PR

### Testing questions.yaml

The `questions.yaml` schema is validated during CI, but also needs manual review:

- To see how different values affect the rendered compose file, modify your test files
- Test all conditional fields (`show_if`)
- Verify all enum options work correctly
- Test required vs optional fields

---

## Updates and Migrations

When you update an existing app or change its configuration structure, you may need migrations to preserve user data and settings.

### When to Use Migrations

Use migrations when:

- Changing the structure of configuration values
- Renaming configuration fields

### Creating a Migration

#### Step 1: Create app_migrations.yaml

Define when your migration should run:

```yaml
migrations:
  - file: migrate_to_v2
    from:
      max_version: 1.0.10     # Applies to apps upgrading from version <= 1.0.10
    target:
      min_version: 2.0.0      # When upgrading to version >= 2.0.0
```

#### Step 2: Write the Migration Script

Create `migrations/migrate_to_v2` (Python script):

```python
#!/usr/bin/python3
import yaml
import sys
import os

def migrate(values):
    """
    Transform old configuration to new configuration.

    Old structure:
      network:
        web_port: 8080

    New structure:
      network:
        web_port:
          port: 8080
          bind_mode: "published"
    """

    # Check if old structure exists
    if isinstance(values.get("network", {}).get("web_port"), int):
        old_port = values["network"]["web_port"]

        # Transform to new structure
        values["network"]["web_port"] = {
            "port": old_port,
            "bind_mode": "published",
            "host_ips": [],
        }

    return values

if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit(1)

    if os.path.exists(sys.argv[1]):
        with open(sys.argv[1], "r") as f:
            print(yaml.dump(migrate(yaml.safe_load(f.read()))))
```

#### Step 3: Make Script Executable

```bash
chmod +x migrations/migrate_to_v2
```

#### Step 4: Update app.yaml

Increment the `version` field to trigger the migration:

```yaml
version: 2.0.0  # Incremented from 1.0.10
```

### Migration Best Practices

1. **Handle Edge Cases**: Check for missing or unexpected values
2. **Test Thoroughly**: Test migrations with various old configurations
3. **Document Changes**: Explain what changed in your PR description
4. **Preserve Data**: Never delete user data without explicit consent
5. **Validate Output**: Ensure migrated values match the new schema

---

## Best Practices

### Security

1. **Run as Non-Root**: Always define `run_as_context` with a non-root user

   > Note: this is only METADATA

   ```yaml
   run_as_context:
     - uid: 568
       gid: 568
       user_name: myapp
       group_name: myapp
   ```

2. **Use Secrets**: Mark sensitive fields as private in `questions.yaml`

   > Note: this is just UI masking.

   ```yaml
   - variable: password
     schema:
       type: string
       private: true
   ```

3. **Minimal Capabilities**: Only add capabilities if absolutely necessary

   ```python
   {% do app.set_capabilities(["NET_ADMIN"]) %}  # Only if needed
   ```

4. **Validate Input**: Use schema validation (min, max, enum) in `questions.yaml`

### Performance

1. **Use Health Checks**: Always define appropriate health checks

   ```python
   {% do app.healthcheck.set_test("curl", {"port": 8080, "path": "/health"}) %}
   ```

2. **Optimize Dependencies**: Only add dependencies when needed

   ```python
   {% do app.depends.add_dependency("postgres", "service_healthy") %}
   ```

3. **Use Latest Library**: Always use the newest non-v1 library version

### User Experience

1. **Sensible Defaults**: Provide good default values in `questions.yaml`
2. **Clear Descriptions**: Add helpful descriptions to fields (where applicable)
3. **Group Related Settings**: Use the existing groups to organize configuration
4. **Conditional Fields**: Use `show_if` to hide irrelevant options
5. **Add Portals**: Always add web UI portals when applicable

### Code Quality

1. **Start from Similar App**: Copy a similar app rather than starting from scratch
2. **Follow Naming Conventions**: Use consistent naming (snake_case for variables)
3. **Comment Complex Logic**: Add comments in templates for clarity
4. **Test Multiple Scenarios**: Create multiple test files
5. **Clean Up**: Remove unused code from copied apps

### Storage

1. **Use ix_volume by Default**: TrueNAS-managed datasets are preferred
   as defaults, as it makes it easy to spin up the app and test.

   ```yaml
   default: "ix_volume"
   ```

2. **Document Storage Needs**: Explain what each storage mount is for
3. **Test Paths**: Use `/opt/tests/` prefix in test files for compatibility

### Versioning

1. **Semantic Versioning**: Use semantic versioning for `version` field
   - Major: Breaking changes
   - Minor: New features
   - Patch: Bug fixes

2. **Track Upstream**: Keep `app_version` in sync with main container tag
3. **Increment on Every Change**: Always bump `version` when modifying the app

### Documentation

1. **Document Special Requirements**: Note GPU, devices, or network requirements
2. **Add Configuration Notes**: Include setup instructions if needed
3. **Link to Upstream Docs**: Provide links to official documentation

---

## Submission Guidelines

### Before You Submit

Checklist before opening a PR:

- [ ] App works locally with all test files
- [ ] `app.yaml` metadata is complete and accurate
- [ ] `questions.yaml` has clear labels and descriptions
- [ ] All test files pass successfully
- [ ] README.md is written
- [ ] Only files under `/ix-dev/` or `/library/` are modified
- [ ] No auto-generated files are included in the PR
- [ ] Icons/screenshots are ready (links provided in PR description)

### PR Description Template

When you create a new pull request, GitHub will automatically populate it with our PR template. This template includes sections for:

- **Description**: Brief overview of the app and what it does
- **App Information**: Links to upstream repository, documentation, license, and version
- **Testing**: Checklist of test scenarios you've verified
- **Icons and Screenshots**: Visual assets for the app
- **Special Notes**: Any important setup or usage information
- **Checklist**: Final verification before submission

The template is located at [`.github/PULL_REQUEST_TEMPLATE/new-app.md`](.github/PULL_REQUEST_TEMPLATE/new-app.md)
and will be automatically loaded when you create a PR.
Simply fill in the placeholders with your app's specific information.

### Review Process

What to expect:

1. **Automated Checks**: CI will run automatically
   - Validates your app structure
   - Runs test files
   - Checks for errors

2. **Human Review**: A maintainer will review your PR
   - Check code quality
   - Verify app works as expected
   - Suggest improvements

3. **Iteration**: You may need to make changes
   - Address review comments
   - Fix any issues found
   - Update based on feedback

4. **CDN Upload**: Reviewer will upload icons/screenshots
   - You'll receive CDN URLs
   - Update your PR with the URLs

5. **Merge**: Once approved, your PR will be merged!

### After Your PR is Merged

Congratulations! Your app is now in the catalog. 🎉

#### Notify Upstream Developers

It's a great idea to let the upstream app developers know that their app is now available on TrueNAS:

- **Contact them politely**: Via GitHub issue, email, or Discord
- **Provide a quick how-to**: Explain how to deploy their app on TrueNAS
- **Suggest adding TrueNAS**: To their supported platforms list
- **Share the catalog link**: Link to the TrueNAS Apps catalog

---

## Getting Help

### Resources

- **GitHub Discussions**: https://github.com/truenas/apps/discussions
  - Ask questions
  - Share tips and tricks
  - Collaborate with other developers

- **Library Tests**: `/library/{version}/tests/`
  - Real examples of library usage
  - See how different features work

- **Existing Apps**: `/ix-dev/community/`
  - Browse real-world examples
  - See how similar apps are structured
  - Copy patterns that work

- **TrueNAS Forums**: https://forums.truenas.com
  - Community support
  - User feedback
  - General TrueNAS questions

### Common Questions

**Q: Which library version should I use?**
A: Always use the latest non-v1 version from `/library/`. Check the directory for available versions and use the highest numbered 2.x.x version.

**Q: My app needs a GPU. How do I configure that?**
A: Check apps like `plex` or `jellyfin` that use GPU passthrough. You'll need to add device mappings and possibly capabilities.

**Q: Can I test on TrueNAS before submitting?**
A: Currently there's no easy way. Test locally with Docker Compose—if it works there, it should work on TrueNAS.

**Q: How do I handle questions.yaml migrations?**
A: Create an `app_migrations.yaml` file and a Python migration script. See the "Updates and Migrations" section above.

**Q: Can I add an app to the stable or enterprise train?**
A: You can't. This train is managed by TrueNAS maintainers only. Submit to the community train only.

**Q: How do I update an existing app?**
A: Fork the repo, make your changes, increment the version in `app.yaml`, and open a PR. Include what changed in the description.

**Q: An app is outdated. Can I update it?**
A: If it's been more than 2 days that the upstream container tag has been released, and our bot hasn't picked it up yet, please open an issue.
   A fix has to be applied so the bot can pick it up.

### Getting Involved

Want to do more than just contribute apps?

- **Review PRs**: Help review other contributors' apps
- **Improve Documentation**: Submit improvements to this guide
- **Report Issues**: Found a bug? Open an issue
- **Help Users**: Answer questions in Discussions / Issues

### Contact

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For contributions

---

## Thank You!

Thank you for contributing to the TrueNAS Apps catalog! Your work helps make self-hosting accessible to everyone. We appreciate your time and effort in making this ecosystem better.

Happy coding! 🚀
