import secrets
import yaml
import sys
import os

YAML_OPTS = {
  'default_flow_style': False,
  'sort_keys': False,
  'indent': 2,
}

class TemplateException(Exception):
  pass

def throw_error(message: str) -> None:
  # When throwing a known error, hide the traceback
  # This is because the error is also shown in the UI
  # and having a traceback makes it hard for user to read
  sys.tracebacklimit = 0
  raise TemplateException(message)


def filter_to_yaml(data: dict) -> str:
  return yaml.dump(data, **YAML_OPTS)

def func_secure_string(length: int) -> str:
  return secrets.token_urlsafe(length)

import secrets
import yaml
import sys
import os

YAML_OPTS = {
  'default_flow_style': False,
  'sort_keys': False,
  'indent': 2,
}

class TemplateException(Exception):
  pass

def throw_error(message: str) -> None:
  # When throwing a known error, hide the traceback
  # This is because the error is also shown in the UI
  # and having a traceback makes it hard for user to read
  sys.tracebacklimit = 0
  raise TemplateException(message)


def filter_to_yaml(data: dict) -> str:
  return yaml.dump(data, **YAML_OPTS)

def func_secure_string(length: int) -> str:
  return secrets.token_urlsafe(length)

# TODO: maybe extend this with ACLs API?!
def func_host_path_with_perms(data: dict, root: dict, perms: dict) -> str:
  if not data.get('type', ''):
    throw_error("Host Path Configuration: Type must be set")

  path = ''
  if data['type'] == 'host_path':
    if not data.get('host_path_config', {}):
      throw_error("Host Path Configuration: [host_path_config] must be set")
    if not data['host_path_config'].get('path', ''):
      throw_error("Host Path Configuration: [host_path_config.path] must be set")
    path = data['host_path_config']['path']
  elif data['type'] == 'ix_volume':
    if not data.get('ix_volume_config', {}):
      throw_error("IX Volume Configuration: [ix_volume_config] must be set")
    if not data['ix_volume_config'].get('dataset_name', ''):
      throw_error("IX Volume Configuration: [ix_volume_config.dataset_name] must be set")
    print(data)
    if not root.get('ixVolumes', []):
      throw_error("IX Volume Configuration: [ixVolumes] must be set")
    for item in root['ixVolumes']:
      if not item.get('hostPath', ''):
        throw_error("IX Volume Configuration: [ixVolumes] item must contain [hostPath]")
      if item['hostPath'].split('/')[-1] == data['ix_volume_config']['dataset_name']:
        path = item['hostPath']
        break
    if not path:
      throw_error(f"IX Volume Configuration: [ixVolumes] does not contain dataset with name [{data['ix_volume_config']['dataset_name']}]")
  else:
    throw_error(f"Type [{data['type']}] is not supported")


  os.makedirs(path, exist_ok=True)

  # FIXME: only do such things if user agreed or if its ixVolumes
  if perms.get('user') and perms.get('group'):
    # Set permissions
    os.chown(path, int(perms['user']), int(perms['group']))

  return path
