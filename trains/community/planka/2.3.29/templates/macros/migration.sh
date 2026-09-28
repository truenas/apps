{%- macro migration(values) %}
set -e

function echo() {
  /bin/echo "[migration.sh] $@"
}

function mark_completed() {
  echo "Marking migration as completed by creating /app/data/.migration_completed"
  echo "DO NOT REMOVE THIS FILE\n" > /app/data/.migration_completed
  echo "Keep this file to prevent the migration from running again.\n" >> /app/data/.migration_completed
  echo "It is only safe to remove this file once migration handling code is removed" >> /app/data/.migration_completed
  echo "from the TrueNAS app and you have upgraded to a newer version of the TrueNAS app." >> /app/data/.migration_completed
}

{% set is_install = values.get("ix_context", {}).get("is_install", true) %}
{% if is_install %}
mark_completed
{% endif %}

if [ -f /app/data/.migration_completed ]; then
  echo "Migration already completed, skipping."
  exit 0
fi

echo "Copying project-background-images to background-images"
cp -av /app/public/project-background-images/. /app/public/background-images

echo "Running db:upgrade"
npm run db:upgrade || { echo "db:upgrade failed"; exit 1; }

mkdir /app/data/protected /app/data/private || { echo "Failed to create data directories"; exit 1; }

echo "Copying user avatars"
cp -av /app/public/user-avatars /app/data/protected || { echo "Failed to copy user avatars"; exit 1; }

echo "Copying background images"
cp -av /app/public/background-images /app/data/protected || { echo "Failed to copy background images"; exit 1; }

echo "Copying attachments"
cp -av /app/private/attachments /app/data/private || { echo "Failed to copy attachments"; exit 1; }

mark_completed

echo "Migration completed successfully"
{%- endmacro %}
