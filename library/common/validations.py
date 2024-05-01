import library.common.utils as utils
import re

def filter_is_email(email: str) -> bool:
  return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def filter_must_be_email(email: str) -> str:
  if not filter_is_email(email):
    utils.throw_error("Value must be an email address")

  return email

def filter_must_be_length(value: str, length: int) -> str:
  if len(value) < length:
    utils.throw_error(f"Value must be {length} characters long")

  return value

def filter_is_password_secure(password: str) -> bool:
  checks=[
    lambda p: len(p) >= 8,
    lambda p: re.search("[a-z]", p),
    lambda p: re.search("[A-Z]", p),
    lambda p: re.search("[0-9]", p),
    lambda p: re.search("[!@#$%^&*(),.?\":{}|<>]", p)
  ]

  return all(c(password) for c in checks)

def filter_must_be_password_secure(password: str) -> str:
    if not filter_is_password_secure(password):
        utils.throw_error("Password must contain at least 8 characters, 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character")

    return password
