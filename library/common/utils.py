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

def throw_error(message):
  # When throwing a known error, hide the traceback
  # This is because the error is also shown in the UI
  # and having a traceback makes it hard for user to read
  sys.tracebacklimit = 0
  raise TemplateException(message)


def filter_to_yaml(data):
  return yaml.dump(data, **YAML_OPTS)

def func_secure_string(length):
  return secrets.token_urlsafe(length)

# TODO: maybe extend this with ACLs API?!
# TODO: once we have ixVolumes in update this func
def func_host_path_with_perms(data, perms):
  if not data['type']:
    throw_error("Host Path Configuration: Type must be set")
  if data['type'] == 'host_path':
    if not data['host_path_config']:
      throw_error("Host Path Configuration: Host Path Config must be set")
    path = data['host_path_config']['path']

  if not path:
      throw_error("Host Path Configuration: Path must be set")

  os.makedirs(path, exist_ok=True)

  # FIXME: only do such things if user agreed or if its ixVolumes
  if perms.get('user') and perms.get('group'):
    # Set permissions
    os.chown(path, int(perms['user']), int(perms['group']))

  return ''
