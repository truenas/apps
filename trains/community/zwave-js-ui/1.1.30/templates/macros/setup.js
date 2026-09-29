{% macro setup(values) %}
const fs = require('fs');
const cfgPath = "{{ values.consts.data_path }}/settings.json";

if (!fs.existsSync(cfgPath)) {
  fs.writeFileSync(cfgPath, '{}', 'utf8');
  console.log(`Settings file [${cfgPath}] created`);
}

const data = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
data.zwave = data.zwave || {};
data.zwave.serverPort = {{ values.network.ws_port.port_number }};
data.zwave.port = "{{ values.consts.zwave_serial_path }}";

fs.writeFileSync(cfgPath, JSON.stringify(data, null, 2), 'utf8');

console.log(`Settings updated in [${cfgPath}]`);
{% endmacro %}
