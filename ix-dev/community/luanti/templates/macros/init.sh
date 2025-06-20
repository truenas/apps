{% macro init(values) -%}
#!/bin/sh
{% set config_file = "%s/minetest.conf"|format(values.consts.config_dir) %}
{% set games_dir = "%s/.minetest/games"|format(values.consts.data_dir) %}
{% set base_url = "https://content.luanti.org/packages/%s/%s" | format(values.luanti.author, values.luanti.map_name) %}
{% set download_url = namespace(x="") %}
{% if values.luanti.release %}
  {% set download_url.x = "%s/releases/%s/download/" | format(base_url, values.luanti.release) %}
{% else %}
  {% set download_url.x = "%s/download/" | format(base_url) %}
{% endif %}

if [ ! -f "{{ config_file }}" ]; then
    echo "Minetest configuration file not found, touching it to create default settings."
    touch "{{ config_file }}"
fi

mkdir -p "{{ games_dir }}/{{ values.luanti.map_name }}"
if [ -z "$(ls -A '{{ games_dir }}/{{ values.luanti.map_name }}')" ]; then
    echo "Downloading {{ values.luanti.author }}/{{ values.luanti.map_name }} from {{ download_url.x }}"
    wget -O "/tmp/{{ values.luanti.map_name }}.zip" "{{ download_url.x }}" || {
        echo "Failed to download {{ values.luanti.map_name }} from {{ download_url.x }}"; exit 1
    }
    echo "Unzipping {{ values.luanti.map_name }} to {{ games_dir }}"
    unzip -q "/tmp/{{ values.luanti.map_name }}.zip" -d "{{ games_dir }}" || {
        echo "Downloaded file is not a valid zip archive."; exit 1
    }
else
    echo "Directory {{ games_dir }}/{{ values.luanti.map_name }} is not empty, assuming game is already installed."
fi
{% endmacro %}
