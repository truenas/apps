from base_v1_0_0 import utils

valid_providers = [
    "aliyun",
    "allinkl",
    "cloudflare",
    "dd24",
    "ddnss",
    "desec",
    "digitalocean",
    "dnsomatic",
    "dnspod",
    # "dondominio",
    # "dreamhost",
    # "duckdns",
    # "dyn",
    # "dynu",
    # "dynv6",
    # "easydns",
    # "freedns",
    # "gandi",
    # "gcp",
    # "godaddy",
    # "goip",
    # "google",
    # "he",
    # "hetzner",
    # "infomaniak",
    # "inwx",
    # "ionos",
    # "linode",
    # "luadns",
    # "name.com",
    # "namecheap",
    # "netcup",
    # "njalla",
    # "noip",
    # "nowdns",
    # "opendns",
    # "ovh",
    # "porkbun",
    # "selfhost.de",
    # "servercow",
    # "spdyn",
    # "strato",
    # "variomedia",
    # "zoneedit",
]
valid_ip_dns_providers = [
    "all",
    "cloudflare",
    "opendns",
]
valid_ip_http_providers = [
    "all",
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
valid_ipv4_http_providers = [
    "all",
    "ipleak",
    "ipify",
    "icanhazip",
    "ident",
    "nnev",
    "wtfismyip",
    "seeip",
]
valid_ipv6_http_providers = [
    "all",
    "ipleak",
    "ipify",
    "icanhazip",
    "ident",
    "nnev",
    "wtfismyip",
    "seeip",
]
valid_ip_fetchers = [
    "all",
    "http",
    "dns",
]
valid_ip_versions = ["", "ipv4", "ipv6"]


def validate_public_ip_providers(items=[], valid=[], category="", allow_custom=False):

    for item in items:
        if not item.get("provider"):
            utils.throw_error(f"Expected [provider] to be set for [{category}]")
        if item["provider"] == "custom":
            if not allow_custom:
                utils.throw_error(f"Custom provider is not supported for [{category}]")
            else:
                if not item.get("custom"):
                    utils.throw_error(f"Expected [custom] to be set when public ip provider is [custom] for [{category}]")
                if not item["custom"].startswith("url:"):
                    utils.throw_error(f"Expected [custom] to start with [url:] for [{category}]")
        if item["provider"] == "all":
            if len(items) > 1:
                utils.throw_error(f"Expected only 1 item in [{category}] with [provider] set to [all], got [{len(items)}]")
        if item["provider"] not in valid:
            utils.throw_error(f"Expected [provider] to be one of [{', '.join(valid)}], got [{item['provider']}] for [{category}]")


def get_public_ip_providers(category: str, items=[]):
    result = []

    if category == "PUBLICIP_DNS_PROVIDERS":
        validate_public_ip_providers(items, valid=valid_ip_dns_providers, category="Public IP DNS Providers", allow_custom=True)
    elif category == "PUBLICIP_HTTP_PROVIDERS":
        validate_public_ip_providers(items, valid=valid_ip_http_providers, category="Public IP HTTP Providers", allow_custom=True)
    elif category == "PUBLICIPV4_HTTP_PROVIDERS":
        validate_public_ip_providers(items, valid=valid_ipv4_http_providers, category="Public IPv4 HTTP Providers", allow_custom=True)
    elif category == "PUBLICIPV6_HTTP_PROVIDERS":
        validate_public_ip_providers(items, valid=valid_ipv6_http_providers, category="Public IPv6 HTTP Providers", allow_custom=True)
    elif category == "PUBLICIP_FETCHERS":
        validate_public_ip_providers(items, valid=valid_ip_fetchers, category="Public IP Fetchers", allow_custom=True)

    for item in items:
        if item["provider"] == "custom":
            result.append(item["custom"])
        else:
            result.append(item["provider"])

    return ",".join(result)


def get_providers_config(items=[]):
    result = []

    for item in items:
        if item["provider"] not in valid_providers:
            utils.throw_error(f"Expected [provider] to be one of [{', '.join(valid_providers)}], got [{item['provider']}]")
        if not item.get("host", ""):
            utils.throw_error(f"Expected [host] to be set for provider [{item['provider']}]")
        if not item.get("domain", ""):
            utils.throw_error(f"Expected [domain] to be set for provider [{item['provider']}]")
        if not item.get("ip_version", "") in valid_ip_versions:
            utils.throw_error(f"Expected [ip_version] to be one of [{', '.join(valid_ip_versions)}], got [{item['ip_version']}]")

        result.append(
            {
                "provider": item["provider"],
                "host": item["host"],
                "domain": item["domain"],
                "ip_version": item.get("ip_version", ""),
                **get_provider_config(item),
            }
        )

    return {"settings": result}


def required_key(item={}, key=""):
    if not item.get(key):
        utils.throw_error(f"Expected [{key}] to be set for [{item['provider']}]")
    return item[key]


data = {
    "aliyun": {
        "required": [{"provider_key": "access_key_id", "user_key": "aliyun_access_key"}, {"provider_key": "secret_key", "user_key": "aliyun_secret_key"}],
        "optional": [],
    },
    "allinkl": {
        "required": [{"provider_key": "username", "user_key": "allinkl_username"}, {"provider_key": "password", "user_key": "allinkl_password"}],
        "optional": [],
    },
    "cloudflare": {
        "required": [{"provider_key": "zone_identifier", "user_key": "cloudflare_zone_id"}, {"provider_key": "ttl", "user_key": "cloudflare_ttl"}],
        "optional": [{"provider_key": "proxied", "user_key": "cloudflare_proxied"}],
        "combos": [
            {"required": [{"provider_key": "token", "user_key": "cloudflare_token"}], "optional": []},
            {"required": [{"provider_key": "user_service_key", "user_key": "cloudflare_user_service_key"}], "optional": []},
            {"required": [{"provider_key": "email", "user_key": "cloudflare_email"}, {"provider_key": "key", "user_key": "cloudflare_api_key"}], "optional": []},
        ],
    },
    "dd24": {"required": [{"provider_key": "password", "user_key": "dd24_password"}], "optional": [], "combos": []},
    "ddnss": {
        "required": [{"provider_key": "username", "user_key": "ddnss_username"}, {"provider_key": "password", "user_key": "ddnss_password"}],
        "optional": [{"provider_key": "provider_ip", "user_key": "ddnss_provider_ip", "default": False}, {"provider_key": "dual_stack", "user_key": "ddnss_dual_stack", "default": False}],
        "combos": [],
    },
    "desec": {"required": [{"provider_key": "token", "user_key": "desec_token"}], "optional": [], "combos": []},
    "digitalocean": {"required": [{"provider_key": "token", "user_key": "digital_ocean_token"}], "optional": [], "combos": []},
    "dnsomatic": {
        "required": [{"provider_key": "username", "user_key": "dnsomatic_username"}, {"provider_key": "password", "user_key": "dnsomatic_password"}],
        "optional": [{"provider_key": "provider_ip", "user_key": "dnsomatic_provider_ip", "default": False}],
        "combos": [],
    },
    "dnspod": {"required": [{"provider_key": "token", "user_key": "dnspod_token"}], "optional": [], "combos": []},
}


def get_provider_config(item={}):
    if item["provider"] not in data:
        utils.throw_error(f"Expected [provider] to be one of [{', '.join(data.keys())}], got [{item['provider']}]")

    result = {}
    provider_data = data[item["provider"]]

    for required in provider_data["required"]:
        result[required["provider_key"]] = required_key(item, required["user_key"])
    result.update(get_optional_data(item, provider_data))

    combo_data = {}
    for combo in provider_data["combos"]:
        if combo_data:
            break

        combo_data = get_combo_data(item, combo)
        # Go to next combo
        if not combo_data:
            continue

        result.update(combo_data)
        result.update(get_optional_data(item, combo))

    if not combo_data:
        utils.throw_error(f"Expected provider [{item['provider']}] to have at least one of the following combinations: {', '.join(get_combos_printout(provider_data['combos']))}")

    return result


def get_combo_data(item={}, combo={}):
    result = {}
    for required in combo["required"]:
        if required["user_key"] not in item:
            return {}
        result[required["provider_key"]] = required_key(item, required["user_key"])
    return result


def get_optional_data(item={}, data={}):
    result = {}
    for optional in data["optional"]:
        if optional["user_key"] in item:
            result[optional["provider_key"]] = item[optional["user_key"]]
        elif optional.get("default") is not None:
            result[optional["provider_key"]] = optional["default"]
    return result


def get_combos_printout(combos=[]):
    result = []
    for combo in combos:
        result.append(f"[{', '.join([r['key'] for r in combo['required']])}]")


# - provider: aliyun                                    - Required
#   domain: "example.com"                               - Required
#   host: "@"                                           - Required - Valid value ("@" or subdomain)
#   ip_version: ""                                      - Required - Valid values (ipv4/ipv6/"")
#   aliyun_access_key: key                              - Required
#   aliyun_secret_key: secret                           - Required

# - provider: allinkl                                   - Required
#   domain: "example.com"                               - Required
#   host: "@"                                           - Required - Valid value ("@" or subdomain)
#   ip_version: ""                                      - Required - Valid values (ipv4/ipv6/"")
#   allinkl_username: user                              - Required
#   allinkl_password: password                          - Required

# - provider: cloudflare                                - Required
#   domain: "example.com"                               - Required
#   host: "@"                                           - Required - Valid value ("@")
#   ip_version: ""                                      - Required - Valid values (ipv4/ipv6/"")
#   cloudflare_zone_id: id                              - Required
#   cloudflare_ttl: 1                                   - Required - Valid values (>=1)
#   cloudflare_proxied: false                           - Required - Valid values (true/false)
#   # One of the following is required
#   1. Token
#   cloudflare_token: token                             - Required
#   2. User service key
#   cloudflare_user_service_key: user_service_key       - Required
#   3. Email and API key
#   cloudflare_email: email                             - Required
#   cloudflare_api_key: api_key                         - Required

# - provider: dd24                                      - Required
#   domain: "example.com"                               - Required
#   host: "@"                                           - Required - Valid value ("@" or subdomain)
#   ip_version: ""                                      - Required - Valid values (ipv4/ipv6/"")
#   dd24_password: pass                                 - Required

# - provider: ddnss                                     - Required
#   domain: "example.com"                               - Required
#   host: "@"                                           - Required - Valid value ("@" or subdomain)
#   ip_version: ""                                      - Required - Valid values (ipv4/ipv6/"")
#   ddnss_username: user                                - Required
#   ddnss_password: password                            - Required
#   ddnss_provider_ip: true                             - Required - Valid values (true/false)
#   ddnss_dual_stack: false                             - Optional - Valid values (true/false)

# - provider: desec                                     - Required
#   domain: "example.com"                               - Required
#   host: "@"                                           - Required - Valid value ("@" or subdomain)
#   ip_version: ""                                      - Required - Valid values (ipv4/ipv6/"")
#   desec_token: pass                                   - Required

# - provider: digitalocean                              - Required
#   domain: "example.com"                               - Required
#   host: "@"                                           - Required - Valid value ("@" or subdomain)
#   ip_version: ""                                      - Required - Valid values (ipv4/ipv6/"")
#   digital_ocean_token: token                          - Required

# - provider: dnspod                                    - Required
#   domain: "example.com"                               - Required
#   host: "@"                                           - Required - Valid value ("@" or subdomain)
#   ip_version: ""                                      - Required - Valid values (ipv4/ipv6/"")
#   dnspod_token: token                                 - Required

# - provider: dnsomatic                                 - Required
#   domain: "example.com"                               - Required
#   host: "@"                                           - Required - Valid value ("@" or subdomain)
#   ip_version: ""                                      - Required - Valid values (ipv4/ipv6/"")
#   dnsomatic_username: user                            - Required
#   dnsomatic_password: pass                            - Required
#   dnsomatic_provider_ip: true                         - Required - Valid values (true/false)
