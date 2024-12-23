{% macro setup_cron(values) -%}
#!/bin/bash
# Old installations had the "default" without extension,
# and after a version the extension was added. Lets cover both cases.
{% for file in ["/config/nginx/site-confs/default.conf", "/config/nginx/site-confs/default"] %}
if grep -q "root /app/www/public" {{ file }}; then
    echo "Fixing nginx [{{ file }}] file"
    sed -i 's/root \/app\/www\/public/root \/app\/diskover-web\/public/g' {{ file }} || { echo "Failed to fix nginx [{{ file }}] file"; exit 1; }
fi
{% endfor %}

{{ check_path("/data") }}
[ ! "$(ls -A /data)" ] && {{ create_dummy_file("/data") }}

{%- for store in values.storage.additional_storage if store.index_data %}
{{ check_path(store.mount_path) }}
[ ! "$(ls -A {{ store.mount_path }})" ] && {{ create_dummy_file(store.mount_path) }}
{%- endfor %}

echo "Merging {{ values.consts.cron_file_path }} with /etc/crontabs/abc"
cat {{ values.consts.cron_file_path }} /etc/crontabs/abc | sort | uniq > /tmp/crontab-abc
crontab -u abc /tmp/crontab-abc || { echo "Failed to setup crontab"; exit 1; }
echo "Finished merging {{ values.consts.cron_file_path }} with /etc/crontabs/abc"
{%- endmacro %}

{% macro create_dummy_file(path) -%}
echo "Empty directory found, writing a dummy file at [{{ path }}] to trigger indexing" | tee {{ path }}/diskover_test.txt
{%- endmacro %}

{% macro check_path(path) -%}
if grep -q "/app/diskover/diskover.py {{ path }}" /config/crontab; then
    echo "------------------------------------WARNING-----------------------------------"
    echo "A crontab entry for [{{ path }}] has been found in /config/crontab".
    echo "This is no longer needed as it is now handled in the /etc/crontabs/abc file."
    echo "Please remove the entry from /config/crontab"
    echo "------------------------------------------------------------------------------"
fi
{%- endmacro %}
