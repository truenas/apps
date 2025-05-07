{% macro fix_nginx() -%}
#!/bin/bash
# Old installations had the "default" without extension,
# and after a version the extension was added. Lets cover both cases.
{% for file in ["/config/nginx/site-confs/default.conf", "/config/nginx/site-confs/default"] %}
if [ -f {{ file }} ]; then
  if grep -q "root /app/www/public" {{ file }}; then
      echo "Fixing nginx [{{ file }}] file"
      sed -i 's/root \/app\/www\/public/root \/app\/diskover-web\/public/g' {{ file }} || { echo "Failed to fix nginx [{{ file }}] file"; exit 1; }
  fi
fi
{% endfor %}
{%- endmacro %}
