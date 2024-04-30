import secrets
import yaml
import os

YAML_OPTS = {
  'default_flow_style': False,
  'sort_keys': False,
  'indent': 2,
}

def filter_to_yaml(data):
  return yaml.dump(data, **YAML_OPTS)

def func_secure_string(length):
  return secrets.token_urlsafe(length)

# TODO: maybe extend this with ACLs API?!
def func_host_path_with_perms(path, perms):
  if not path:
    raise ValueError("path is required")

  if not perms.get('user') or not perms.get('group'):
    raise ValueError("user and group are required")

  os.makedirs(path, exist_ok=True)

  # Set permissions
  os.chown(path, int(perms['user']), int(perms['group']))

  return ''
