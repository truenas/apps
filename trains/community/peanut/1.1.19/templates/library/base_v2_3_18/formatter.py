import json
import hashlib


def escape_dollar(text: str) -> str:
    return text.replace("$", "$$")


def get_hashed_name_for_volume(prefix: str, config: dict):
    config_hash = hashlib.sha256(json.dumps(config).encode("utf-8")).hexdigest()
    return f"{prefix}_{config_hash}"


def get_hash_with_prefix(prefix: str, data: str):
    return f"{prefix}_{hashlib.sha256(data.encode('utf-8')).hexdigest()}"


def merge_dicts_no_overwrite(dict1, dict2):
    overlapping_keys = dict1.keys() & dict2.keys()
    if overlapping_keys:
        raise ValueError(f"Merging of dicts failed. Overlapping keys: {overlapping_keys}")
    return {**dict1, **dict2}


def get_image_with_hashed_data(image: str, data: str):
    # Drop the digest pin (repo:tag@sha256:...), it is not valid in the generated tag.
    # The digest is still part of the hashed data (FROM line), so a digest change results in a new tag.
    image = image.split("@")[0]
    return get_hash_with_prefix(f"ix-{image}", data)
