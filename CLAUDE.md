# CLAUDE.md

This file is specific to this fork (`https://github.com/blastik/truenas-apps`) and should **not** be submitted upstream via PR.

## Project Overview

TrueNAS Apps is a Docker Compose-based application catalog. Apps are defined using:
- `app.yaml` — metadata
- `ix_values.yaml` — static defaults (images, consts)
- `questions.yaml` — user configuration schema (UI form)
- `templates/docker-compose.yaml` — Jinja2 template rendered by the library

**Only modify files under `/ix-dev/` or `/library/`. All other files are auto-generated.**

All new community apps go in `/ix-dev/community/`.

## Environment Setup

### Python via asdf

This project uses Python 3.11. Manage it with [asdf](https://asdf-vm.com/):

```bash
asdf plugin add python
asdf install python 3.11.11
asdf local python 3.11.11   # writes .tool-versions (globally gitignored)
```

### Virtual environment via uv

Use [uv](https://github.com/astral-sh/uv) to create and manage the virtualenv:

```bash
# Install uv if not already available
brew install uv   # or: pip install uv

# Create virtualenv and install test dependencies
uv venv
uv pip install -e ".[test]"

# Activate the virtualenv
source .venv/bin/activate
```

Dependencies (from `pyproject.toml` `[project.optional-dependencies] test`):
- `pyyaml`, `psutil`, `pytest`, `pytest-cov`, `bcrypt`, `pydantic`

## Key Commands

### Render a compose file (no Docker needed)

```bash
./.github/scripts/ci.py --app <app> --train community --test-file basic-values.yaml --render-only=true
```

### Deploy and test an app locally

```bash
./.github/scripts/ci.py --app <app> --train community --test-file basic-values.yaml --wait=true
```

### Run library unit tests

```bash
pytest library/ -vvv
```

### Validate port uniqueness

```bash
./.github/scripts/port_validation.py
```

### Generate app metadata (capabilities, etc.)

```bash
./.github/scripts/generate_metadata.py --train community --app <app>
```

### Validate catalog (requires Docker)

```bash
docker run --platform linux/amd64 --quiet --rm -e FAKE_ENV=1 -v $PWD:/workspace \
  ghcr.io/truenas/apps_validation:latest apps_dev_charts_validate validate --path /workspace
```

### Copy/update library files into an app (requires Docker)

```bash
docker run --platform linux/amd64 --quiet --rm -e FAKE_ENV=1 -v $PWD:/workspace \
  ghcr.io/truenas/apps_validation:latest apps_catalog_hash_generate --path /workspace
```

## Project Structure

```
ix-dev/
  community/         <- All new apps go here
  stable/            <- Managed by iXsystems
  enterprise/        <- Managed by iXsystems
library/
  2.2.8/             <- Latest library version (use this)
  0.0.1/             <- Legacy (do not use)
.github/scripts/
  ci.py              <- Local/CI test runner
  generate_metadata.py
  port_validation.py
trains/              <- Auto-generated, DO NOT EDIT
```

## App Directory Structure

```
ix-dev/community/<app>/
├── app.yaml                   # metadata (name, version, lib_version, run_as_context)
├── ix_values.yaml             # images + consts
├── questions.yaml             # user config schema
├── README.md                  # short description
├── templates/
│   ├── docker-compose.yaml    # Jinja2 template
│   └── test_values/
│       └── basic-values.yaml  # required; use port 30000+ and /opt/tests/ paths
```

## Library Version

Always use the latest library version: **`2.2.8`**

Set in `app.yaml`:
```yaml
lib_version: 2.2.8
lib_version_hash: ""   # auto-filled by ci.py
```

## Conventions

- App `name` must match its directory name exactly
- `train` field must match the parent directory
- Start app `version` at `1.0.0`; increment on every change
- Use `568:568` (or user-configurable) as the run-as uid/gid
- Test storage paths use `/opt/tests/` prefix for Docker Desktop compatibility
- Prefer `ghcr.io` over `docker.io` for images
- Use `ix_volume` as default storage type

## Versioning App Changes

Every modification to an app requires bumping `version` in `app.yaml`:
- Patch (`1.0.0` → `1.0.1`): bug fixes
- Minor (`1.0.0` → `1.1.0`): new features/options
- Major (`1.0.0` → `2.0.0`): breaking config changes (requires migration)

## Git Workflow

This repo's `origin` is the personal fork (`https://github.com/blastik/truenas-apps`).

**Never work directly on `master`.** Always create a feature branch for each app or change, then open a PR from that branch:

```bash
# Start new work
git checkout master && git pull origin master
git checkout -b feat/add-myapp

# Before committing, run the unit tests
pytest library/ -vvv

# Then commit and push to fork
git add ix-dev/community/myapp/
git commit -m "feat(community): add myapp"
git push origin feat/add-myapp
```

PRs are opened from `feat/*` branches on the fork to `master` on the upstream repo.

**Do NOT include `CLAUDE.md` or any fork-specific files in upstream PRs.**

## Global Gitignore

`.tool-versions` (asdf) is excluded globally via `~/.gitignore_global`. This is already configured on this machine:

```bash
git config --global core.excludesfile ~/.gitignore_global
# ~/.gitignore_global contains: .tool-versions
```
