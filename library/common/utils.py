import secrets
import yaml


YAML_OPTS = {
  'default_flow_style': False,
  'sort_keys': False,
  'indent': 2,
}

def filter_to_yaml(data):
  return yaml.dump(data, **YAML_OPTS)

def func_secure_string(length):
  return secrets.token_urlsafe(length)
