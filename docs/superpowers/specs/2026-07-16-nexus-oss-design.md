# Nexus Repository Manager 3 (OSS / Community Edition) — TrueNAS App Design

Status: Phase 1 (HTTP-only) — design approved
Implements: truenas/apps#4502 (with `sonatype/nexus3` — the modern, supported image; the issue links to the EOL `sonatype/nexus` Nexus 2 image, see Rationale below).
Train: `community`
Library: `2.3.8` (hash `cd75c897a1e8fef54b5bd00d0d8849f240bc50db2ef650eccc0ee74f3b2b2dc1`)
Image: `sonatype/nexus3:3.94.0` (Alpine, Java 21, multi-arch amd64+arm64, published 2026-07-09)

## 1. Rationale

Issue #4502 requests "Nexus OSS" as a Package Repository app and links to
`hub.docker.com/r/sonatype/nexus/` — that is **Nexus Repository Manager 2**,
which is EOL since ~2021 and unmaintained. The supported successor is
**Nexus Repository 3** (`sonatype/nexus3`), renamed "Community Edition" since
3.77.0. Packaging Nexus 2 in 2026 has no value. This app packages Nexus 3 and
the PR description explicitly notes that it realises #4502 using the current
image.

Nexus 3 OSS uses an **embedded OrientDB** database in `/nexus-data` — no
external database is required. Single-container app.

## 2. Scope — phased

**Phase 1 (this design, this PR):** HTTP-only, single `nexus` container +
conditional `permissions` container. WebUI + all package formats (maven, npm,
nuget, pypi, helm, apt, go, conan, rubygems, raw, …) served through port 8081,
plus configurable extra published ports for **Docker registry connectors** so
`docker push/pull` works without `host_network`.

**Phase 2 (follow-up PR, outlined in §9):** native HTTPS via `certificate_id`
using a `certs` init-container that builds a JKS keystore and patches
`nexus.properties` + `jetty-https.xml`. Deliberately deferred — Nexus HTTPS is
materially more complex than Jenkins' single-flag HTTPS and would add risky
code to a first PR. Phase 2 is an additive schema migration (no existing field
changes).

## 3. Architecture

Two containers, both using image key `image` (`sonatype/nexus3`) for `nexus`
and `container_utils_image` (`ixsystems/container-utils:1.0.2`) for the
permissions helper.

### 3.1 `nexus` container
- Process runs as **UID/GID 200** (the `nexus` user baked into the image by
  `Dockerfile.alpine.java21`: `groupadd --gid 200 -r nexus` /
  `useradd --uid 200 -r nexus`). `set_user(200, 200)` in template. The image's
  `uid_entrypoint.sh` also expects 200 — consistent.
- UID/GID is **hardcoded**, not exposed to the user (precedent: `jenkins`,
  `cloudbeaver` hardcode; `prowlarr` exposes it for apps where the image allows
  arbitrary UIDs — Nexus does not).
- Data: `/nexus-data` (OrientDB, blobs, config). Mounted from
  `storage.nexus_data`.
- WebUI port: container listens on **8081** (fixed). Host port is
  `network.web_port.port_number`. The default **must be unique catalog-wide**
  (`.github/scripts/port_validation.py` flags duplicate port defaults across
  all apps in the 30000-40000 range). As of 2026-07-16 the next free default is
  **30451** — use that (re-run `port_validation.py` at impl time to confirm).
- Docker registry connector ports: extra published ports from
  `network.docker_ports`, each maps host `port_number` → internal
  `container_port` (user sets the matching connector port in the Nexus UI).
- Port mapping is **not** 1:1 like Jenkins (Jenkins sets `--httpPort` to the
  host port so container == host). Nexus listens on 8081 fixed, so `add_port`
  uses the idiomatic two-arg form `add_port(port_config, {"container_port": 8081})`
  — same pattern as `adguard-home`/`ae-netscope`. The portal points at the host
  port (`port_number`) per catalog convention; in `host_network` mode the
  container is reachable on 8081 directly and the portal port may not match —
  this is the accepted behaviour across fixed-container-port apps in the catalog.
- JVM: `INSTALL4J_ADD_VM_PARAMS` built from `nexus.java_heap`
  (`-Xms{h}M -Xmx{h}M -XX:MaxDirectMemorySize={h}M`) plus user
  `additional_java_opts` (raw JVM flags, heap flags reserved/blocked).

### 3.2 `permissions` container
- `tpl.deps.perms(values.consts.perms_container_name)` with
  `perm_config = {"uid": 200, "gid": 200, "mode": "check"}`.
- `add_or_skip_action()` for `/nexus-data` and each `additional_storage`.
- Activated only when it has actions; `nexus` depends on it
  `service_completed_successfully`. Guarantees `/nexus-data` is owned by 200
  before Nexus starts (complements the image's own entrypoint, which also wants
  200).

### 3.3 Healthcheck
`curl` variant (curl is present in the alpine image —
`apk add openjdk21 tar procps gzip curl shadow`, curl not removed) against the
**container** port 8081, no-auth status endpoint:

| field | value |
|---|---|
| test | `curl` `http://127.0.0.1:8081/service/rest/v1/status` |
| start_period | 120s (Nexus cold-starts in 2–3 min) |
| interval | 30s |
| timeout | 10s |
| retries | 5 |

Portal: `web_port` (host port), scheme `http`.

## 4. `ix_values.yaml`

```yaml
images:
  image:
    repository: sonatype/nexus3
    tag: "3.94.0"
  container_utils_image:
    repository: ixsystems/container-utils
    tag: 1.0.2

consts:
  nexus_container_name: nexus
  perms_container_name: permissions
  run_as_user: 200
  run_as_group: 200
  nexus_data_path: /nexus-data
  web_container_port: 8081
  notes_body: |
    The initial admin password is generated on first start.
    Retrieve it from the app logs or read /nexus-data/admin.password
    inside the container. Username: admin. Change it on first login.
```

## 5. `questions.yaml`

Groups (no "User and Group" group — UID hardcoded):

1. **Nexus Configuration**
   - `TZ` (string, default `Etc/UTC`, `$ref definitions/timezone`)
   - `nexus` (dict):
     - `java_heap` (int, MB, default 2048, required) — heap size; feeds
       `-Xms`/`-Xmx`/`-XX:MaxDirectMemorySize`.
     - `additional_java_opts` (list of string, default `[]`) — raw JVM flags
       appended to `INSTALL4J_ADD_VM_PARAMS`. Template `fail()`s if any entry
       matches `-Xmx` / `-Xms` / `-XX:MaxDirectMemorySize` (reserved, set from
       `java_heap`). Duplicate-key check is not applicable (raw strings).
       - Note: Jenkins' `additional_java_opts` is a list of `property`/`value`
         dicts (it auto-prefixes `-D` for Jenkins system properties). Nexus has
         no such convention — raw flags (`-D...`, `-Xss`, etc.) are appropriate,
         matching Jenkins' *other* field `additional_opts` which is itself a
         list of strings.
     - `additional_envs` (list of dict `name`/`value`, default `[]`)

2. **Network Configuration**
   - `web_port` (dict): `bind_mode` (published/exposed/"", default published),
     `port_number` (int 1–65535, default **30451** — must be unique
     catalog-wide, see `port_validation.py`; re-check at impl time),
     `host_ips` (list, show_if published).
   - `docker_ports` (list, default `[]`) — extra ports for Nexus Docker
     repository connectors. Each item (dict): `bind_mode` (default published),
     `port_number` (int, **required, no default**), `container_port` (int,
     **required, no default** — the internal Nexus connector port the user sets
     in the Nexus UI), `host_ips` (list, show_if published).
     - **Why no defaults:** `port_validation.py` recurses into list items and
       treats every int with `min=1,max=65535,default` as a catalog-wide host
       port that must be unique. A list that's empty by default must not
       reserve a slot; `item_looks_like_port` skips fields with no default
       (`if not schema.get("default"): return False`). Making both port fields
       default-less keeps them out of the uniqueness map.
     - **Precedent:** `eclipse-mosquitto` `additional_ports` uses this exact
       pattern — list of dicts with `bind_mode` (default `published`),
       `port_number` (int, required, no default), `container_port` (int,
       required, no default), `protocol`. Confirmed valid against
       `port_validation.py` (no catalog port slot consumed by an empty list).
   - `networks` (list, show_if `host_network == false`) — same shape as Jenkins.
   - `host_network` (bool, default false).

3. **Storage Configuration**
   - `nexus_data` (dict): `type` (host_path/ix_volume, default ix_volume),
     `ix_volume_config` (`acl_enable`/`dataset_name` default `nexus-data`/
     `acl_entries`), `host_path_config` (`acl_enable`/`acl`/`path`).
   - `additional_storage` (list, default `[]`): full set
     (host_path/ix_volume/cifs/nfs), `read_only`, `mount_path`, per-type config
     — identical to Jenkins.

4. **Labels Configuration** — list of `key`/`value`/`containers` with
   `containers` enum `["nexus"]`.

5. **Resources Configuration** — `limits.cpus` (default 2), `limits.memory`
   (default 4096 MB).

## 6. `templates/docker-compose.yaml`

```jinja2
{% set tpl = ix_lib.base.render.Render(values) %}
{% set c1 = tpl.add_container(values.consts.nexus_container_name, "image") %}

{% set vm_params = namespace(items=[]) %}
{% do vm_params.items.extend([
  "-Xms%dM"|format(values.nexus.java_heap),
  "-Xmx%dM"|format(values.nexus.java_heap),
  "-XX:MaxDirectMemorySize=%dM"|format(values.nexus.java_heap),
]) %}
{% for opt in values.nexus.additional_java_opts %}
  {% if opt.startswith("-Xms") or opt.startswith("-Xmx") or "-XX:MaxDirectMemorySize" in opt %}
    {% do tpl.funcs.fail(
      "Expected [nexus.additional_java_opts] to not contain reserved heap options "
      "[-Xms/-Xmx/-XX:MaxDirectMemorySize]. Set heap via [nexus.java_heap]."
    ) %}
  {% endif %}
  {% do vm_params.items.append(opt) %}
{% endfor %}

{% set perm_container = tpl.deps.perms(values.consts.perms_container_name) %}
{% set perm_config = {"uid": values.consts.run_as_user, "gid": values.consts.run_as_group, "mode": "check"} %}

{% do c1.set_user(values.consts.run_as_user, values.consts.run_as_group) %}
{% do c1.environment.add_env("INSTALL4J_ADD_VM_PARAMS", vm_params.items|join(" ")) %}
{% do c1.environment.add_user_envs(values.nexus.additional_envs) %}

{% do c1.healthcheck.set_test("curl", {"port": values.consts.web_container_port, "path": "/service/rest/v1/status"}) %}
{% do c1.healthcheck.set_start_period(120) %}
{% do c1.healthcheck.set_interval(30) %}
{% do c1.healthcheck.set_timeout(10) %}
{% do c1.healthcheck.set_retries(5) %}

{% do c1.add_port(values.network.web_port, {"container_port": values.consts.web_container_port}) %}

{% for dp in values.network.docker_ports %}
  {% do c1.add_port(dp) %}
{% endfor %}

{% do c1.add_storage(values.consts.nexus_data_path, values.storage.nexus_data) %}
{% do perm_container.add_or_skip_action(values.consts.nexus_data_path, values.storage.nexus_data, perm_config) %}

{% for store in values.storage.additional_storage %}
  {% do c1.add_storage(store.mount_path, store) %}
  {% do perm_container.add_or_skip_action(store.mount_path, store, perm_config) %}
{% endfor %}

{% if perm_container.has_actions() %}
  {% do perm_container.activate() %}
  {% do c1.depends.add_dependency(values.consts.perms_container_name, "service_completed_successfully") %}
{% endif %}

{% do tpl.portals.add(values.network.web_port) %}
{% do tpl.notes.set_body(values.consts.notes_body) %}

{{ tpl.render() | tojson }}
```

## 7. `app.yaml` metadata

```yaml
annotations:
  min_scale_version: 24.10.2.2   # match a recent community app; confirm against latest at impl time
app_version: 3.94.0
capabilities: []
categories:
- development
changelog_url: https://help.sonatype.com/en/release-notes/2024-2025.html
date_added: '2026-07-16'
description: Nexus Repository Manager — open source package/repository manager (maven, npm, nuget, pypi, docker, helm, …).
home: https://www.sonatype.com/products/sonatype-nexus-repository
host_mounts: []
icon: https://media.sys.truenas.net/apps/nexus/icons/icon.svg
keywords:
- repository
- maven
- npm
- docker-registry
- packages
lib_version: 2.3.8
lib_version_hash: cd75c897a1e8fef54b5bd00d0d8849f240bc50db2ef650eccc0ee74f3b2b2dc1
maintainers:
- name: blka
  url: https://github.com/blka
name: nexus
run_as_context:
- description: Container [nexus] runs as the non-root user/group nexus (200).
  gid: 200
  group_name: nexus
  uid: 200
  user_name: nexus
sources:
- https://hub.docker.com/r/sonatype/nexus3
- https://github.com/sonatype/docker-nexus3
- https://help.sonatype.com/en/nexus-repository.html
title: Nexus Repository
train: community
version: 1.0.0
```

`item.yaml` mirrors `app.yaml` `categories`/`icon_url`/`screenshots`/`tags`.
Screenshots left empty (no TrueNAS-hosted assets yet) or omitted if the catalog
allows; icon path follows convention `media.sys.truenas.net/apps/nexus/icons/icon.svg`
— the asset itself is hosted by TrueNAS maintainers outside this repo.

## 8. Test values & CI

`templates/test_values/basic-values.yaml` — non-default values to catch issues
(CI publishes these host ports directly on the runner; they need only be free
on the runner, not catalog-unique — uniqueness is enforced only on
`questions.yaml` defaults):
- `network.web_port.port_number: 30452`, `bind_mode: published` (host 30452 →
  container 8081 — exercises the host≠container mapping).
- `network.docker_ports`: one entry — `bind_mode: published`,
  `port_number: 30453`, `container_port: 8082` (host 30453 → container 8082).
- `nexus.java_heap: 1024`
- `nexus.additional_java_opts: ["-Djava.net.preferIPv4Stack=true"]`
- `storage.nexus_data`: `type: host_path`, `host_path_config.path: /opt/tests/mnt/nexus-data`
- `resources.limits.cpus: 2`, `limits.memory: 2048`

CI / local render: `python .github/scripts/ci.py --app nexus --validate-templates`.
On macOS arm64 use the `apps_validation` openat2/ENOSYS workaround from prior
sessions to render templates locally. Also run
`python3 .github/scripts/port_validation.py` to confirm no duplicate default
ports were introduced.

No `app_migrations.yaml` / `migrations/` in Phase 1 (new app, v1.0.0).

## 9. Phase 2 outline (HTTPS, follow-up PR)

Additive only — no changes to existing fields:

1. Add `network.certificate_id` (int, nullable, `$ref definitions/certificate`).
2. `certs` init-container (image `image`, has `keytool` since it's the nexus
   image with JDK) runs before `nexus`:
   - Convert `certificate_id` (private key + cert) → PKCS12 via `openssl` →
     JKS keystore via `keytool -importkeystore`, placed at
     `/nexus-data/etc/ssl/keystore.jks`, password = `tpl.funcs.secure_string(32)`.
   - Generate/patch `/nexus-data/etc/nexus.properties`: add
     `application-port-ssl=8443`, `nexus-args=...jetty-https.xml...`,
     `ssl.etc=${karaf.data}/etc/ssl`.
   - Patch `/opt/sonatype/nexus/etc/jetty/jetty-https.xml` (install dir —
     regenerated every start by the init container, so survives image upgrade)
     to set `KeyStorePath`/`KeyStorePassword`/`KeyManagerPassword`/
     `TrustStorePassword` (all = the secure string).
3. When `certificate_id` set: disable HTTP (`application-port=-1` /
   remove `jetty-http.xml` from `nexus-args`), serve HTTPS on `web_port`
   mapped to container 8443, healthcheck `curl --insecure` scheme https, portal
   scheme https.
4. New `cert-setup.sh.jinja` macro (mirror Jenkins), `certs` container
   `setup_as_helper()`, perms on a `/tmp` temp volume.

## 10. Open questions to confirm at implementation time

- `min_scale_version`: pick the value a recent community app uses at impl time
  (don't trust the placeholder above blindly).
- `changelog_url`: exact Sonatype release-notes URL — verify it resolves.
- Icon asset hosting: confirm whether a PR must ship the SVG in-repo or whether
  `media.sys.truenas.net` is provisioned by maintainers post-merge (Jenkins
  convention implies the latter).
- Reserved-heap flag check uses plain Jinja string methods (`startswith`,
  `in`) — verified available: library 2.3.8 has no `regex_search` filter, and
  Jenkins relies on the same `.startswith()` / `in` pattern.