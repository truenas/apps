{% macro setup(values) -%}
#!/bin/sh
node /wiki/server/ix-config.js || { echo "Failed to setup"; exit 1; }
node server
{% endmacro %}
