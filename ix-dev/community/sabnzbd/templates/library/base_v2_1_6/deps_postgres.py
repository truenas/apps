import urllib.parse
from typing import TYPE_CHECKING, TypedDict, NotRequired


if TYPE_CHECKING:
    from render import Render
    from storage import IxStorage


try:
    from .error import RenderError
    from .deps_perms import PermsContainer
    from .validations import valid_port_or_raise
except ImportError:
    from error import RenderError
    from deps_perms import PermsContainer
    from validations import valid_port_or_raise


class PostgresConfig(TypedDict):
    user: str
    password: str
    database: str
    port: NotRequired[int]
    volume: "IxStorage"


MAX_POSTGRES_VERSION = 17


class PostgresContainer:
    def __init__(
        self, render_instance: "Render", name: str, image: str, config: PostgresConfig, perms_instance: PermsContainer
    ):
        self._render_instance = render_instance
        self._name = name
        self._config = config
        self._data_dir = "/var/lib/postgresql/data"
        self._upgrade_name = f"{self._name}_upgrade"
        self._upgrade_container = None

        for key in ("user", "password", "database", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for postgres")

        port = valid_port_or_raise(self._get_port())

        c = self._render_instance.add_container(name, image)

        c.set_user(999, 999)
        c.healthcheck.set_test("postgres")
        c.remove_devices()
        c.add_storage(self._data_dir, config["volume"])

        common_variables = {
            "POSTGRES_USER": config["user"],
            "POSTGRES_PASSWORD": config["password"],
            "POSTGRES_DB": config["database"],
            "POSTGRES_PORT": port,
        }

        for k, v in common_variables.items():
            c.environment.add_env(k, v)

        perms_instance.add_or_skip_action(
            f"{self._name}_postgres_data", config["volume"], {"uid": 999, "gid": 999, "mode": "check"}
        )

        repo = self._get_repo(image)
        # eg we don't want to handle upgrades of pg_vector at the moment
        if repo == "postgres":
            target_major_version = self._get_target_version(image)
            upg = self._render_instance.add_container(self._upgrade_name, image)
            upg.build_image(get_build_manifest())
            upg.set_entrypoint(["/bin/bash", "-c", "/upgrade.sh"])
            upg.configs.add("pg_container_upgrade.sh", get_upgrade_script(), "/upgrade.sh", "0755")
            upg.restart.set_policy("on-failure", 1)
            upg.set_user(999, 999)
            upg.healthcheck.disable()
            upg.remove_devices()
            upg.add_storage(self._data_dir, config["volume"])
            for k, v in common_variables.items():
                upg.environment.add_env(k, v)

            upg.environment.add_env("TARGET_VERSION", target_major_version)
            upg.environment.add_env("DATA_DIR", self._data_dir)

            self._upgrade_container = upg

            c.depends.add_dependency(self._upgrade_name, "service_completed_successfully")

        # Store container for further configuration
        # For example: c.depends.add_dependency("other_container", "service_started")
        self._container = c

    @property
    def container(self):
        return self._container

    def add_dependency(self, container_name: str, condition: str):
        self._container.depends.add_dependency(container_name, condition)
        if self._upgrade_container:
            self._upgrade_container.depends.add_dependency(container_name, condition)

    def _get_port(self):
        return self._config.get("port") or 5432

    def _get_repo(self, image):
        images = self._render_instance.values["images"]
        if image not in images:
            raise RenderError(f"Image [{image}] not found in values. Available images: [{', '.join(images.keys())}]")
        repo = images[image].get("repository", "")
        if not repo:
            raise RenderError("Could not determine repo")
        return repo

    def _get_target_version(self, image):
        images = self._render_instance.values["images"]
        if image not in images:
            raise RenderError(f"Image [{image}] not found in values. Available images: [{', '.join(images.keys())}]")
        tag = images[image].get("tag", "")
        tag = str(tag)  # Account for tags like 16.6
        target_major_version = tag.split(".")[0]

        try:
            target_major_version = int(target_major_version)
        except ValueError:
            raise RenderError(f"Could not determine target major version from tag [{tag}]")

        if target_major_version > MAX_POSTGRES_VERSION:
            raise RenderError(f"Postgres version [{target_major_version}] is not supported")

        return target_major_version

    def get_url(self, variant: str):
        user = urllib.parse.quote_plus(self._config["user"])
        password = urllib.parse.quote_plus(self._config["password"])
        creds = f"{user}:{password}"
        addr = f"{self._name}:{self._get_port()}"
        db = self._config["database"]

        match variant:
            case "postgres":
                return f"postgres://{creds}@{addr}/{db}?sslmode=disable"
            case "postgresql":
                return f"postgresql://{creds}@{addr}/{db}?sslmode=disable"
            case "postgresql_no_creds":
                return f"postgresql://{addr}/{db}?sslmode=disable"
            case "host_port":
                return addr
            case _:
                raise RenderError(f"Expected [variant] to be one of [postgres, postgresql], got [{variant}]")


def get_build_manifest() -> list[str | None]:
    return [
        f"RUN apt-get update && apt-get install -y {' '.join(get_upgrade_packages())}",
        "WORKDIR /tmp",
    ]


def get_upgrade_packages():
    return [
        "rsync",
        "postgresql-13",
        "postgresql-14",
        "postgresql-15",
        "postgresql-16",
    ]


def get_upgrade_script():
    return """
#!/bin/bash
set -euo pipefail

get_bin_path() {
  local version=$1
  echo "/usr/lib/postgresql/$version/bin"
}

log() {
  echo "[ix-postgres-upgrade] - [$(date +'%Y-%m-%d %H:%M:%S')] - $1"
}

check_writable() {
  local path=$1
  if [ ! -w "$path" ]; then
    log "$path is not writable"
    exit 1
  fi
}

check_writable "$DATA_DIR"

# Don't do anything if its a fresh install.
if [ ! -f "$DATA_DIR/PG_VERSION" ]; then
  log "File $DATA_DIR/PG_VERSION does not exist. Assuming this is a fresh install."
  exit 0
fi

# Don't do anything if we're already at the target version.
OLD_VERSION=$(cat "$DATA_DIR/PG_VERSION")
log "Current version: $OLD_VERSION"
log "Target version: $TARGET_VERSION"
if [ "$OLD_VERSION" -eq "$TARGET_VERSION" ]; then
  log "Already at target version $TARGET_VERSION"
  exit 0
fi

# Fail if we're downgrading.
if [ "$OLD_VERSION" -gt "$TARGET_VERSION" ]; then
  log "Cannot downgrade from $OLD_VERSION to $TARGET_VERSION"
  exit 1
fi

export OLD_PG_BINARY=$(get_bin_path "$OLD_VERSION")
if [ ! -f "$OLD_PG_BINARY/pg_upgrade" ]; then
  log "File $OLD_PG_BINARY/pg_upgrade does not exist."
  exit 1
fi

export NEW_PG_BINARY=$(get_bin_path "$TARGET_VERSION")
if [ ! -f "$NEW_PG_BINARY/pg_upgrade" ]; then
  log "File $NEW_PG_BINARY/pg_upgrade does not exist."
  exit 1
fi

export NEW_DATA_DIR="/tmp/new-data-dir"
if [ -d "$NEW_DATA_DIR" ]; then
  log "Directory $NEW_DATA_DIR already exists."
  exit 1
fi

export PGUSER="$POSTGRES_USER"
log "Creating new data dir and initializing..."
PGDATA="$NEW_DATA_DIR" eval "initdb --username=$POSTGRES_USER --pwfile=<(echo $POSTGRES_PASSWORD)"

timestamp=$(date +%Y%m%d%H%M%S)
backup_name="backup-$timestamp-$OLD_VERSION-$TARGET_VERSION.tar.gz"
log "Backing up $DATA_DIR to $NEW_DATA_DIR/$backup_name"
tar -czf "$NEW_DATA_DIR/$backup_name" "$DATA_DIR"

log "Using old pg_upgrade [$OLD_PG_BINARY/pg_upgrade]"
log "Using new pg_upgrade [$NEW_PG_BINARY/pg_upgrade]"
log "Checking upgrade compatibility of $OLD_VERSION to $TARGET_VERSION..."

"$NEW_PG_BINARY"/pg_upgrade \
  --old-bindir="$OLD_PG_BINARY" \
  --new-bindir="$NEW_PG_BINARY" \
  --old-datadir="$DATA_DIR" \
  --new-datadir="$NEW_DATA_DIR" \
  --socketdir /var/run/postgresql \
  --check

log "Compatibility check passed."

log "Upgrading from $OLD_VERSION to $TARGET_VERSION..."
"$NEW_PG_BINARY"/pg_upgrade \
  --old-bindir="$OLD_PG_BINARY" \
  --new-bindir="$NEW_PG_BINARY" \
  --old-datadir="$DATA_DIR" \
  --new-datadir="$NEW_DATA_DIR" \
  --socketdir /var/run/postgresql

log "Upgrade complete."

log "Copying old pg_hba.conf to new pg_hba.conf"
# We need to carry this over otherwise
cp "$DATA_DIR/pg_hba.conf" "$NEW_DATA_DIR/pg_hba.conf"

log "Replacing contents of $DATA_DIR with contents of $NEW_DATA_DIR (including the backup)."
rsync --archive --delete "$NEW_DATA_DIR/" "$DATA_DIR/"

log "Removing $NEW_DATA_DIR."
rm -rf "$NEW_DATA_DIR"

log "Done."
"""
