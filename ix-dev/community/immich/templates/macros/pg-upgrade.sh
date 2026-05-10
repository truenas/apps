{% macro precheck(values) %}
#!/usr/bin/env bash
# Pre-upgrade safety checks. Runs before any dump containers.
# Exits 0 if safe to proceed (including no-op fresh-install / same-version cases).
# Exits non-zero with a message if the cluster on disk is in a state we cannot upgrade.
set -euo pipefail

base=/var/lib/postgresql
target="{{ values.consts.target_pg_major }}"
# Space-separated list of old majors we have a dump path for.
supported_old_versions="{% for v in values.consts.dump_source_versions %}{{ v }} {% endfor %}"

# Detect on-disk PG version, if any.
on_disk=""
for v in 18 17 16 15 14 13; do
  if [ -f "${base}/${v}/docker/PG_VERSION" ]; then
    on_disk="${v}"
    break
  fi
done

if [ -z "${on_disk}" ]; then
  echo "Precheck: no existing Postgres cluster on disk (fresh install or empty volume). OK."
  exit 0
fi

if [ "${on_disk}" = "${target}" ]; then
  echo "Precheck: on-disk Postgres version (${on_disk}) matches target (${target}). No upgrade needed."
  exit 0
fi

if [ "${on_disk}" -gt "${target}" ]; then
  echo "Precheck FAILED: on-disk Postgres version is ${on_disk}, target is ${target}." >&2
  echo "Downgrades are not supported. Restore from backup or roll back the application version." >&2
  exit 2
fi

# Refuse if we have no dump path for the on-disk version.
match=0
for v in ${supported_old_versions}; do
  if [ "${v}" = "${on_disk}" ]; then
    match=1
    break
  fi
done
if [ "${match}" -ne 1 ]; then
  echo "Precheck FAILED: no automated upgrade path from PG${on_disk} to PG${target}." >&2
  echo "Supported source versions: ${supported_old_versions}" >&2
  echo "Restore from backup, or upgrade in stages via an Immich version that bridges to a supported source." >&2
  exit 2
fi

# Marker file check: refuse to dump+restore if the data volume does not look like an Immich install.
if [ ! -e /data/.immich ]; then
  echo "Precheck FAILED: /data/.immich marker file is missing." >&2
  echo "Either this volume does not contain an Immich install, or the marker was removed." >&2
  echo "Refusing to run an automated upgrade against unrecognised data." >&2
  exit 2
fi

# Disk-space check: dump+restore needs at least 2x the size of the source cluster on the same dataset.
src=$(du -sb "${base}/${on_disk}/docker" | awk '{print $1}')
avail=$(df -B1 --output=avail "${base}" | tail -1)
need=$(( src * 2 ))
if [ "${need}" -gt "${avail}" ]; then
  src_gib=$(( src / 1024 / 1024 / 1024 ))
  avail_gib=$(( avail / 1024 / 1024 / 1024 ))
  need_gib=$(( need / 1024 / 1024 / 1024 ))
  echo "Precheck FAILED: insufficient free space for dump+restore." >&2
  echo "Source cluster size: ${src_gib} GiB; need at least ${need_gib} GiB free; available: ${avail_gib} GiB." >&2
  echo "Free up space on the postgres_data dataset and retry." >&2
  exit 2
fi

# Ownership check: the postgres dirs must be owned by the in-container postgres user (999:999).
own=$(stat -c '%u:%g' "${base}/${on_disk}/docker")
if [ "${own}" != "999:999" ]; then
  echo "Precheck FAILED: ${base}/${on_disk}/docker is owned by ${own}; expected 999:999 (netdata)." >&2
  echo "Fix ownership on the host (chown -R 999:999 …/pgData) and retry." >&2
  exit 2
fi

src_gib=$(( src / 1024 / 1024 / 1024 ))
avail_gib=$(( avail / 1024 / 1024 / 1024 ))
echo "Precheck OK: PG${on_disk} → PG${target}; src=${src_gib} GiB, free=${avail_gib} GiB."
{% endmacro %}


{% macro dump_script(values) %}
#!/usr/bin/env bash
# Runs inside a temporary PG${OLD_VERSION} container alongside the legacy data dir.
# Only the dump container whose `OLD_VERSION` matches what's on disk does any work;
# the others exit 0 cleanly. The first to run a successful dump writes the marker
# `_upgrade_workdir/dump.complete`, which subsequent containers in the chain honour.
set -euo pipefail

base=/var/lib/postgresql
work="${base}/_upgrade_workdir"
old="${OLD_VERSION:?OLD_VERSION must be set}"
target="${TARGET_VERSION:?TARGET_VERSION must be set}"

mkdir -p "${work}"
chmod 0700 "${work}"

if [ -f "${work}/dump.complete" ]; then
  echo "Dump-${old}: marker present at ${work}/dump.complete — skipping."
  exit 0
fi

if [ "${old}" = "${target}" ]; then
  echo "Dump-${old}: skipping — old equals target." >&2
  exit 0
fi

if [ ! -f "${base}/${old}/docker/PG_VERSION" ]; then
  echo "Dump-${old}: no PG${old} cluster on disk; skipping."
  exit 0
fi

old_dir="${base}/${old}/docker"
sock=/tmp/pg-dump-sock
mkdir -p "${sock}"
chown 999:999 "${sock}"
chmod 0700 "${sock}"

# pg_hba in an Immich-initialised cluster may require a password even on the local
# socket; export PGPASSWORD so psql/pg_dump can authenticate either way.
export PGPASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}"

# Start the old PG with no TCP listener; only a private unix socket.
PGDATA="${old_dir}" pg_ctl -D "${old_dir}" \
  -o "-c listen_addresses='' -c unix_socket_directories=${sock} -c unix_socket_permissions=0700" \
  -w -t 60 start

trap 'PGDATA="${old_dir}" pg_ctl -D "${old_dir}" -m fast stop || true' EXIT

# Sanitise legacy state that breaks downstream restore on PG${target}.
# - The legacy pgvecto.rs `vectors` extension/schema is unavailable in the new image (#3882).
# - The reserved-prefix GUC `vchordrq.prewarm_dim` produces warnings on the new server (#4667).
psql -h "${sock}" -U "{{ values.consts.db_user }}" -d "{{ values.consts.db_name }}" \
  -v ON_ERROR_STOP=1 \
  -c "DROP EXTENSION IF EXISTS vectors CASCADE;" \
  -c "DROP SCHEMA IF EXISTS vectors CASCADE;" \
  -c "ALTER DATABASE \"{{ values.consts.db_name }}\" RESET vchordrq.prewarm_dim;"

# Custom-format dump of the application database. Streams to disk; doesn't buffer in memory.
pg_dump -h "${sock}" -U "{{ values.consts.db_user }}" -d "{{ values.consts.db_name }}" \
  -Fc -f "${work}/dump.partial"

mv "${work}/dump.partial" "${work}/dump.dat"
chmod 0600 "${work}/dump.dat"

# Stop cleanly so the data dir can be moved.
PGDATA="${old_dir}" pg_ctl -D "${old_dir}" -m fast stop
trap - EXIT

# Mark the dump complete BEFORE moving the legacy data dir aside. Order matters: if
# the subsequent `mv` fails (or the container is killed between the two steps) we err
# on the side of "dump exists; trust the dump" rather than "dump never completed; re-dump
# from the legacy dir" — because once we're past this point a re-dump may no longer be
# possible (the source could be gone or the new PG cluster could already have started initdb).
touch "${work}/dump.complete"

# Move the legacy data dir to a non-numeric sibling so the main PG container's entrypoint
# initialises a fresh cluster at /var/lib/postgresql/${target}/docker. A non-numeric prefix
# also avoids any future re-introduction of the upstream upgrade.sh from misidentifying it
# as a candidate cluster (it walks ${base}/*/docker).
ts=$(date +%s)
mv "${base}/${old}" "${base}/_legacy_pg${old}_${ts}"

size=$(du -h "${work}/dump.dat" | awk '{print $1}')
echo "Dump-${old} complete: ${work}/dump.dat (${size}); legacy data moved to ${base}/_legacy_pg${old}_${ts}."
{% endmacro %}


{% macro restore_script(values) %}
#!/usr/bin/env bash
# Runs after the main Postgres container is healthy. Restores the dump produced by
# whichever dump container matched the on-disk version (if any), then runs
# post-restore sanitisation.
# Idempotent: if no dump is present, or restore already completed, exits 0.
set -euo pipefail

base=/var/lib/postgresql
work="${base}/_upgrade_workdir"

if [ ! -f "${work}/dump.complete" ]; then
  echo "Restore: no dump present (fresh install or no upgrade needed). Nothing to restore."
  exit 0
fi
if [ -f "${work}/restore.complete" ]; then
  echo "Restore: marker present at ${work}/restore.complete — already restored."
  exit 0
fi
if [ ! -f "${work}/dump.dat" ]; then
  echo "Restore FAILED: dump.complete marker present but ${work}/dump.dat is missing." >&2
  echo "Either the dump file was removed or restore already moved it aside without writing restore.complete." >&2
  echo "Inspect ${work} and ${base}/_legacy_pg* manually." >&2
  exit 2
fi

host="{{ values.consts.pgvecto_container_name }}"
db="{{ values.consts.db_name }}"
user="{{ values.consts.db_user }}"

export PGPASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}"

# pg_restore --clean --if-exists drops and recreates each object so we don't conflict with
# the empty schema that initdb / docker-entrypoint leaves behind.
pg_restore -h "${host}" -U "${user}" -d "${db}" \
  --clean --if-exists --no-owner --no-acl \
  --exit-on-error \
  "${work}/dump.dat"

# Clear reserved-prefix GUC that some installs carry over (#4667). Idempotent.
psql -h "${host}" -U "${user}" -d "${db}" -v ON_ERROR_STOP=1 \
  -c "ALTER DATABASE \"${db}\" RESET vchordrq.prewarm_dim;"

# Sanity check: at least one immich row visible. Table is `asset` (singular) on Immich.
# Only runs when dump.complete was set, so the table must exist.
count=$(psql -h "${host}" -U "${user}" -d "${db}" -At -v ON_ERROR_STOP=1 \
  -c "SELECT count(*) FROM asset;")
echo "Restore: post-restore asset row count = ${count}."

# Mark restore complete and rename the dump so a subsequent compose-up does not retrigger.
ts=$(date +%s)
mv "${work}/dump.dat" "${work}/dump.restored.${ts}.dat"
touch "${work}/restore.complete"
echo "Restore complete. Dump archived as ${work}/dump.restored.${ts}.dat."
echo "Legacy PG data dir is preserved at /var/lib/postgresql/_legacy_pg* — remove manually once you have verified Immich is working."
{% endmacro %}
