{% macro run(values) -%}
{%- set user_db = "%s/users.db" | format(values.consts.config_path) -%}
{%- set flags = namespace(x=[
  "--port=%d"|format(values.network.web_port),
  "--enable-local-write",
  "--disable-use-bonjour",
  "--trusted-ips=192.168.0.0/16,172.16.0.0/12,10.0.0.0/8",
]) -%}

# export XDG_RUNTIME_DIR=/tmp/runtime-root
if [ ! -f {{ values.consts.books_path }}/metadata.db ]; then
  echo 'Creating an empty calibre metadata database at [{{ values.consts.books_path }}/metadata.db]'
  touch {{ values.consts.books_path }}/metadata.db
fi

{%- if values.calibre.enable_auth -%}
  {%- do flags.x.append("--enable-auth") -%}
  {%- do flags.x.append("--userdb=%s"|format(user_db)) %}

if [ ! -f {{ user_db }} ]; then
  echo 'Creating calibre user database at [{{ user_db }}] and adding admin user'
  /usr/bin/calibre-server \
    --userdb {{ user_db }} \
    --manage-users add admin '{{ values.consts.default_admin_pass }}'
fi
{%- endif %}

/usr/bin/calibre-server {{ flags.x | join(" ") }} {{ values.consts.books_path }}
{% endmacro %}
