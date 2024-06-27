from base_v1_0_0 import utils


def get_public_ip_providers(items=[]):
    result = []

    for item in items:
        if not item.get("provider"):
            utils.throw_error("Expected [provider] to be set for public ip provider")
        if item["provider"] == "custom":
            if not item.get("custom"):
                utils.throw_error("Expected [custom] to be set when public ip provider is [custom]")
            result.append(item["custom"])
        else:
            result.append(item["provider"])

    return ",".join(result)
