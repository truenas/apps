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
