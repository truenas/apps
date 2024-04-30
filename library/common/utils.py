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
# TODO: once we have ixVolumes in update this func
def func_host_path_with_perms(path, perms):
  if not path:
    raise ValueError("path is required")

  os.makedirs(path, exist_ok=True)

  # FIXME: only do such things if user agreed or if its ixVolumes
  if perms.get('user') and perms.get('group'):
    # Set permissions
    os.chown(path, int(perms['user']), int(perms['group']))

  return ''
