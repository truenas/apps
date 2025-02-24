{% macro patch() -%}
chmod +x /etc/cont-init.d/20-config
chmod +x /etc/cont-init.d/30-patch-nvidia
chmod +x /etc/cont-init.d/60-custom-setup-script
chmod +x /etc/services.d/unmanic/run
{%- endmacro %}
