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

{%- for store in values.storage.additional_storage if store.index_data %}
check_path "{{ store.mount_path }}"
{%- endfor %}

echo "Deduplicating individual crontab files for abc and root users"
cat /etc/crontabs/abc | sort | uniq > /tmp/crontab-abc
cat {{ values.consts.cron_file_path }} | sort | uniq > /tmp/crontab-root

echo "Setting up crontabs for abc and root users"
crontab -u abc /tmp/crontab-abc || { echo "Failed to setup abc crontab"; exit 1; }
crontab -u root /tmp/crontab-root || { echo "Failed to setup root crontab"; exit 1; }
echo "Crontabs setup complete"
{%- endmacro %}
