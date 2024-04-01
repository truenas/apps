import secrets

def secure_string(length):
  return secrets.token_urlsafe(length)
