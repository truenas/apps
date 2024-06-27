from base_v1_0_0 import utils

valid_providers = [
    "aliyun",
    "allinkl",
    "cloudflare",
    "dd24",
    "ddnss",
    "digitalocean",
    "dnsomatic",
    "dnspod",
    "dondominio",
    "dreamhost",
    "duckdns",
    "dyn",
    "dynu",
    "dynv6",
    "freedns",
    "gandi",
    "gcp",
    "godaddy",
    "google",
    "he",
    "infomaniak",
    "inwx",
    "linode",
    "luadns",
    "namecheap",
    "njalla",
    "noip",
    "opendns",
    "ovh",
    "porkbun",
    "selfhost.de",
    "servercow",
    "spdyn",
    "strato",
    "variomedia",
    "ionos",
    "desec",
    "easydns",
    "goip",
    "hetzner",
    "name.com",
    "netcup",
    "nowdns",
    "zoneedit",
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


def get_provider_config(item={}):
    if item["provider"] == "aliyun":
        return {"access_key_id": required_key(item, "aliyun_access_key"), "access_secret": required_key(item, "aliyun_secret_key")}
    elif item["provider"] == "allinkl":
        return {"username": required_key(item, "allinkl_username"), "password": required_key(item, "allinkl_password")}
    elif item["provider"] == "cloudflare":
        cf = {"zone_identifier": required_key(item, "cloudflare_zone_id"), "ttl": required_key(item, "cloudflare_ttl"), "proxied": item.get("cloudflare_proxied", False)}
        if item.get("cloudflare_token"):
            return {**cf, "token": required_key(item, "cloudflare_token")}
        elif item.get("cloudflare_user_service_key"):
            return {**cf, "user_service_key": required_key(item, "cloudflare_user_service_key")}
        elif item.get("cloudflare_email") and item.get("cloudflare_api_key"):
            return {**cf, "email": required_key(item, "cloudflare_email"), "key": required_key(item, "cloudflare_api_key")}
        else:
            utils.throw_error("Expected either [cloudflare_token], [cloudflare_user_service_key] or [cloudflare_email, cloudflare_api_key] to be set for [cloudflare]")
    elif item["provider"] == "dd24":
        return {"password": required_key(item, "dd24_password")}
    elif item["provider"] == "ddnss":
        return {"username": required_key(item, "ddnss_username"), "password": required_key(item, "ddnss_password"), "provider_ip": item.get("ddnss_provider_ip", False), "dual_stack": item.get("ddnss_dual_stack", False)}
    elif item["provider"] == "desec":
        return {"token": required_key(item, "desec_token")}
    elif item["provider"] == "digitalocean":
        return {"token": required_key(item, "digital_ocean_token")}


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
