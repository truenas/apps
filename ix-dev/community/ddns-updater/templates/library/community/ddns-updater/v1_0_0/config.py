from base_v1_0_0 import utils


def validate_public_ip_dns_providers(items=[]):
    valid_providers = [
        "cloudflare",
        "opendns",
    ]

    for item in items:
        if not item.get("provider"):
            utils.throw_error("Expected [provider] to be set for public ip provider")
        if item["provider"] == "custom":
            utils.throw_error("Custom provider is not supported for public ip dns providers")
        if item["provider"] not in valid_providers:
            utils.throw_error(f"Expected [provider] to be one of [{', '.join(valid_providers)}], got [{item['provider']}]")


def validate_public_ip_http_providers(items=[]):
    valid_providers = [
        "custom",
        "ipify",
        "ifconfig",
        "ipinfo",
        "google",
        "spdyn",
        "ipleak",
        "icanhazip",
        "ident",
        "nnev",
        "wtfismyip",
        "seeip",
        "changeip",
    ]

    for item in items:
        if not item.get("provider"):
            utils.throw_error("Expected [provider] to be set for public ip provider")
        if item["provider"] == "custom":
            if not item.get("custom"):
                utils.throw_error("Expected [custom] to be set when public ip provider is [custom]")
            if not item["custom"].startswith("url:"):
                utils.throw_error("Expected [custom] to start with [url:]")
        if item["provider"] not in valid_providers:
            utils.throw_error(f"Expected [provider] to be one of [{', '.join(valid_providers)}], got [{item['provider']}]")


def get_public_ip_providers(category: str, items=[]):
    result = []

    if category == "PUBLICIP_DNS_PROVIDERS":
        validate_public_ip_dns_providers(items)
    elif category == "PUBLICIP_HTTP_PROVIDERS":
        validate_public_ip_http_providers(items)
    # elif category == "PUBLICIPV4_HTTP_PROVIDERS":
    #     validate_public_ipv4_http_providers(items)
    # elif category == "PUBLICIPV6_HTTP_PROVIDERS":
    #     validate_public_ipv6_http_providers(items)
    # elif category == "PUBLICIP_FETCHERS":
    #     validate_public_ip_fetchers(items)

    for item in items:
        if item["provider"] == "custom":
            result.append(item["custom"])
        else:
            result.append(item["provider"])

    return ",".join(result)
