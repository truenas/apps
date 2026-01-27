{% macro setup(values) %}
const cfg_path = "/wiki/config.yml";
const fs = require('fs-extra');
const yaml = require('js-yaml');

console.log(`Updating [${cfg_path}] file...`);

if (!fs.existsSync(cfg_path)) {
  console.log(`File [${cfg_path}] does not exist.`);
  process.exit(1);
}

console.log(`File [${cfg_path}] exists!`);
const data = yaml.safeLoad(fs.readFileSync(cfg_path, 'utf8'));

data["bindIP"] = "0.0.0.0";
data["port"] = {{ values.network.http_port.port_number }};
if (!data["db"]) data["db"] = {};
data["db"]["type"] = "postgres";
data["db"]["host"] = "{{ values.consts.postgres_container_name }}";
data["db"]["port"] = 5432;
data["db"]["user"] = "{{ values.consts.db_user }}";
data["db"]["pass"] = "{{ values.wiki_js.db_password }}";
data["db"]["db"] = "{{ values.consts.db_name }}";

if (!data["ssl"]) data["ssl"] = {};
data["ssl"]["enabled"] = {{ "true" if values.network.certificate_id else "false" }};

{% if values.network.certificate_id %}
data["ssl"]["provider"] = "custom";
data["ssl"]["format"] = "pem";
data["ssl"]["port"] = {{ values.network.https_port.port_number }};
data["ssl"]["key"] = "{{ values.consts.ssl_key_path }}";
data["ssl"]["cert"] = "{{ values.consts.ssl_cert_path }}";
{% endif %}

fs.writeFileSync(cfg_path, yaml.safeDump(data));
console.log("Done!\n\n");
{% endmacro %}
