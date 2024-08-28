{% macro setup_cron(values) -%}
#!/bin/bash
{% set text = "'Empty directory found, writing a dummy file at [%s] to trigger indexing' | tee %s/diskover_test.txt" %}
[ ! "$$(ls -A /data)" ] && echo {{ text | format("/data", "/data") }}
{%- for store in values.storage.additional_storage if store.index_data %}
[ ! "$$(ls -A {{ store.mount_path }})" ] && echo {{ text | format(store.mount_path, store.mount_path) }}
{%- endfor %}
echo "Merging {{ values.consts.cron_file_path }} with /etc/crontabs/abc"
cat {{ values.consts.cron_file_path }} /etc/crontabs/abc | sort | uniq > /tmp/crontab-abc
crontab -u abc /tmp/crontab-abc || { echo "Failed to setup crontab"; exit 1; }
echo "Finished merging {{ values.consts.cron_file_path }} with /etc/crontabs/abc"
{%- endmacro %}
