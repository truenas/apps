{% macro banlist_setup(values) -%}
#!/bin/sh

set -eu

apk add --no-cache curl git gnupg

GPG_KEY_URL="https://github.com/Cuprate/cuprate/raw/7b8756fa80e386fb04173d8220c15c86bf9f9888/misc/gpg_keys/boog900.asc"
REPO_URL="https://github.com/Boog900/monero-ban-list"
REPO_DIR="/tmp/monero-ban-list"

rm -rf "$REPO_DIR"
git clone --depth 1 "$REPO_URL" "$REPO_DIR"
cd "$REPO_DIR"

curl -fsSL "$GPG_KEY_URL" | gpg --batch --import
gpg --batch --verify ./sigs/boog900.sig ban_list.txt

cp ban_list.txt /banlist/ban_list.txt
chmod 644 /banlist/ban_list.txt
{%- endmacro %}
