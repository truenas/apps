{% macro init(values) -%}
#!/bin/sh
set -e

if [ ! -f {{ values.consts.key_file_path }} ]; then
    echo "Generating key file..."
    /chia-blockchain/venv/bin/python3 -c \
        "from chia.util.keychain import generate_mnemonic;print(generate_mnemonic())" > {{ values.consts.key_file_path }}

    if [ ! -f {{ values.consts.key_file_path }} ]; then
        echo "Failed to generate key file"
        exit 1
    fi

    echo "Key file generated successfully"
fi
{%- endmacro %}
