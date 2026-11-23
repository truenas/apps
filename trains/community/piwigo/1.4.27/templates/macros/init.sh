{% macro init(values) -%}
{%- set pw_url = "http://%s:%d" | format(values.consts.piwigo_container_name, values.consts.internal_web_port) %}
{%- set args = [
  "language=%s"|format(values.piwigo.language),
  "dbhost=%s"|format(values.consts.mariadb_container_name),
  "dbuser=%s"|format(values.consts.db_user),
  "dbpasswd=%s"|format(values.piwigo.db_password),
  "dbname=%s"|format(values.consts.db_name),
  "prefix=piwigo_",
  "admin_name=%s"|format(values.piwigo.admin_name),
  "admin_pass1=%s"|format(values.piwigo.admin_password),
  "admin_pass2=%s"|format(values.piwigo.admin_password),
  "admin_mail=%s"|format(values.piwigo.admin_email),
  "install=Start+installation",
] %}
#!/bin/sh

until curl --silent --fail --output /dev/null {{ pw_url }}; do
  echo "Waiting for Piwigo to start..."
  sleep 1
done

if curl --silent --fail {{ pw_url }}/install.php | grep "Piwigo is already installed"; then
  echo "Piwigo is already installed, skipping installation"
  exit 0
fi

echo "Installing Piwigo..."

curl -X POST -d "{{ args | join("&") }}" {{ pw_url }}/install.php || { echo "Failed to install Piwigo"; exit 1; }
if curl --silent --fail {{ pw_url }}/install.php | grep "Piwigo is already installed"; then
  echo "Piwigo is already installed, skipping installation"
  exit 0
fi

exit 1
{% endmacro %}
