{% macro dockerfile(values) %}
 FROM {{ values.images.builder.repository }}:{{ values.images.builder.tag }} AS builder
RUN xcaddy build {{ values.consts.caddy_version }} --with github.com/tailscale/caddy-tailscale
 FROM {{ values.images.image.repository }}:{{ values.images.image.tag }}
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
{% endmacro %}