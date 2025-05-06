def get_value_from_secret(secrets=None, secret_name=None, key=None):
    secrets = secrets if secrets else dict()
    secret_name = secret_name if secret_name else ""
    key = key if key else ""

    if not secrets or not secret_name or not key:
        raise ValueError("Expected [secrets], [secret_name] and [key] to be set")
    for curr_secret_name, curr_data in secrets.items():
        if curr_secret_name.endswith(secret_name):
            if not curr_data.get(key, None):
                raise ValueError(
                    f"Expected [{key}] to be set in secret [{curr_secret_name}]"
                )
            return curr_data[key]

    raise ValueError(f"Secret [{secret_name}] not found")
