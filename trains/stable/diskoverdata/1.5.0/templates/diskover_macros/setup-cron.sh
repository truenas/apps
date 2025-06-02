{% macro setup_cron(values) -%}
#!/bin/bash
function check_path() {
    [ ! $(ls -A $1) ] && echo "Empty directory found, writing a dummy file at [$1] to trigger indexing" | tee $1/diskover_test.txt
    if [ ! -f "/config/crontab" ]; then return; fi
    if grep -q "/app/diskover/diskover.py $1" /config/crontab; then
        echo "------------------------------------WARNING-----------------------------------"
        echo "A crontab entry for [$1] has been found in /config/crontab".
        echo "This is no longer needed as it is now handled in the /etc/crontabs/abc file."
        echo "Please remove the entry from /config/crontab"
        echo "------------------------------------------------------------------------------"
    fi
}

check_path /data
{%- for store in values.storage.additional_storage if store.index_data %}
check_path "{{ store.mount_path }}"
{%- endfor %}

echo "Merging {{ values.consts.cron_file_path }} with /etc/crontabs/abc"
cat {{ values.consts.cron_file_path }} /etc/crontabs/abc | sort | uniq > /tmp/crontab-abc
crontab -u abc /tmp/crontab-abc || { echo "Failed to setup crontab"; exit 1; }
echo "Finished merging {{ values.consts.cron_file_path }} with /etc/crontabs/abc"
{%- endmacro %}
