{% macro fix_nginx() -%}
#!/bin/bash
# Old installations had the "default" without extension,
# and after a version the extension was added. Lets cover both cases.
function check_file() {
  if [ ! -f $1 ]; then return; fi
  if grep -q "root /app/www/public" $1; then
      echo "Fixing nginx [$1] file"
      sed -i 's/root \/app\/www\/public/root \/app\/diskover-web\/public/g' $1 || { echo "Failed to fix nginx [$1] file"; exit 1; }
  fi
}

check_file "/config/nginx/site-confs/default.conf"
check_file "/config/nginx/site-confs/default"
{%- endmacro %}
