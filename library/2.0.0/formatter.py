import re
import json
import hashlib


# Replaces all single dollar signs with double dollar signs
# Docker tries to expand shell variables, so we need to
# escape them in multiple places
# It will not replace dollar signs that are already escaped
def escape_dollar(text):
    # https://regex101.com/r/tdbI7y/1
    return re.sub(r"(?<!\$)\$(?!\$)", r"$$", text)


def get_hashed_name_for_volume(prefix: str, config: dict):
    config_hash = hashlib.sha256(json.dumps(config).encode("utf-8")).hexdigest()
    return f"{prefix}_{config_hash}"
