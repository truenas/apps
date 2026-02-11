{%- macro migration() %}
{# /app/data is expected to be mounted #}
set -e

if [ -f /app/data/.migration_completed ]; then
  echo "Migration already completed, skipping."
  exit 0
fi

mkdir /app/data/protected /app/data/private || { echo "Failed to create data directories"; exit 1; }

# Private
echo "Copying attachments"
cp -av /app/private/attachments /app/data/private || { echo "Failed to copy attachments"; exit 1; }

# Protected
echo "Copying public assets"
cp -av /app/public/favicons /app/data/protected || { echo "Failed to copy favicons"; exit 1; }
echo "Copying user avatars"
cp -av /app/public/user-avatars /app/data/protected || { echo "Failed to copy user avatars"; exit 1; }
echo "Copying project background images"
cp -av /app/public/project-background-images /app/data/protected || { echo "Failed to copy project background images"; exit 1; }
# Rename to match new paths
mv /app/data/protected/project-background-images /app/data/protected/background-images || { echo "Failed to rename project background images"; exit 1; }

echo "Running db:upgrade"
npm run db:upgrade || { echo "db:upgrade failed"; exit 1; }

echo "DO NOT REMOVE THIS FILE, until migration handling is removed from the TrueNAS app and you have upgraded to a newer version of the TrueNAS app." > /app/data/.migration_completed

echo "Migration completed successfully"
{%- endmacro %}
