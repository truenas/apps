from . import utils
import re

def is_email(email):
  return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def must_be_email(email):
  if not is_email(email):
    utils.throw_error("Value must be an email address")

  return email

def must_be_length(value, length):
  if len(value) < length:
    utils.throw_error(f"Value must be {length} characters long")

  return value

def is_password_secure(password):
  checks=[
    lambda p: len(p) >= 8,
    lambda p: re.search("[a-z]", p),
    lambda p: re.search("[A-Z]", p),
    lambda p: re.search("[0-9]", p),
    lambda p: re.search("[!@#$%^&*(),.?\":{}|<>]", p)
  ]

  return all(c(password) for c in checks)

def must_be_password_secure(password):
    if not is_password_secure(password):
        utils.throw_error("Password must contain at least 8 characters, 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character")

    return password

def validate_path(path):
    if not path:
        utils.throw_error("Path must be set")

    if not path.startswith("/"):
        utils.throw_error(f"Path [{path}] must start with [/]")

    return path

# MinIO Validations (TODO: Move to directory under enterprise/MinIO)
def validate(data):
  if not data['minio'].get('access_key', ''):
     utils.throw_error("MinIO: [access_key] must be set")

  if not data['minio'].get('secret_key', ''):
     utils.throw_error("MinIO: [secret_key] must be set")

  if len(data['storage'].get('data', [])) < 1:
     utils.throw_error("MinIO: At least 1 storage item must be set")

  if len(data['storage']['data']) > 1 and not data['minio'].get('multi_mode', {}).get('enabled', False):
     utils.throw_error("MinIO: [Multi Mode] must be enabled if more than 1 storage item is set")

  # make sure mount_paths in data['storage']['data'] are unique
  mount_paths = [item['mount_path'] for item in data['storage']['data']]
  if len(mount_paths) != len(set(mount_paths)):
    utils.throw_error(f"MinIO: Mount paths in MinIO storage must be unique, found duplicates: [{', '.join(mount_paths)}]")

  if data['logsearch'].get('enabled', False):
    if not data['logsearch'].get('postgres_password', ''):
      utils.throw_error("MinIO: [LogSearch] [postgres_password] must be set")
    if not data['logsearch'].get('disk_capacity_gb', ''):
      utils.throw_error("MinIO: [LogSearch] [disk_capacity_gb] must be set")

  if data['minio'].get('multi_mode', {}).get('enabled', False):
    disallowed_keys = ["server"]
    for item in data['minio']['multi_mode'].get('items', []):
      if item in disallowed_keys:
        utils.throw_error(f"MinIO: Value [{item}] is not allowed in [Multi Mode] items")

      if item.startswith("/"):
        # check if these charactes exist in item
        if any(char in item for char in ["{", "}"]) and not "..." in item:
          utils.throw_error("MinIO: [Multi Mode] items must have 3 dots when they are paths with expansion eg [/some_path{1...4}]")

  return ''
