{% macro setup_py(values) -%}
from deluge.config import Config
import os
import shutil
if not os.path.exists('/config/core.conf'):
  print('Copying default config')
  shutil.copyfile('/defaults/core.conf', '/config/core.conf')
print('Loading config')
config = Config('/config/core.conf')
print('Setting listen ports to [{{ values.network.torrent_port }}]')
config['listen_ports'] = [{{ values.network.torrent_port }}, {{ values.network.torrent_port }}]
print('Saving config')
Config.save(config)
print('Done')
{%- endmacro %}
