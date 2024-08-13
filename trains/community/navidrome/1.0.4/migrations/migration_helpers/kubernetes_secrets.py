def get_value_from_secret(secrets={}, secret_name="", key=""):
    if not secrets or not secret_name or not key:
        raise ValueError("Expected [secrets], [secret_name] and [key] to be set")
    for secret in secrets.items():
        curr_secret_name = secret[0]
        curr_data = secret[1]

        if curr_secret_name.endswith(secret_name):
            if not curr_data.get(key, None):
                raise ValueError(
                    f"Expected [{key}] to be set in secret [{curr_secret_name}]"
                )
            return curr_data[key]

    raise ValueError(f"Secret [{secret_name}] not found")
