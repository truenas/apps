import re


def filter_is_email(email):
  import re
  return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def filter_must_be_email(email):
  if not is_email(email):
    raise ValueError("must be an email address")
  return email

def filter_must_be_length(value, length):
  if len(value) < length:
    raise ValueError("must be %d characters long" % length)
  return value

def filter_is_password_secure(password):
  checks=[
    lambda p: len(p) >= 8,
    lambda p: re.search("[a-z]", p),
    lambda p: re.search("[A-Z]", p),
    lambda p: re.search("[0-9]", p),
    lambda p: re.search("[!@#$%^&*(),.?\":{}|<>]", p)
  ]
  return all(c(password) for c in checks)

def filter_must_be_password_secure(password):
    if not is_password_secure(password):
        raise ValueError("password must contain at least 8 characters, 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character")
    return password
