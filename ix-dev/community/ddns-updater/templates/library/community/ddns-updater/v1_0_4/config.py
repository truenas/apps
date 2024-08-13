from base_v1_0_0 import utils
import json

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
                    utils.throw_error(
                        f"Expected [custom] to be set when public ip provider is [custom] for [{category}]"
                    )
                if not item["custom"].startswith("url:"):
                    utils.throw_error(
                        f"Expected [custom] to start with [url:] for [{category}]"
                    )
        if item["provider"] == "all":
            if len(items) > 1:
                utils.throw_error(
                    f"Expected only 1 item in [{category}] with [provider] set to [all], got [{len(items)}]"
                )
        if item["provider"] not in valid:
            utils.throw_error(
                f"Expected [provider] to be one of [{', '.join(valid)}], got [{item['provider']}] for [{category}]"
            )


def get_public_ip_providers(category: str, items=[]):
    result = []

    if category == "PUBLICIP_DNS_PROVIDERS":
        validate_public_ip_providers(
            items,
            valid=valid_ip_dns_providers,
            category="Public IP DNS Providers",
            allow_custom=True,
        )
    elif category == "PUBLICIP_HTTP_PROVIDERS":
        validate_public_ip_providers(
            items,
            valid=valid_ip_http_providers,
            category="Public IP HTTP Providers",
            allow_custom=True,
        )
    elif category == "PUBLICIPV4_HTTP_PROVIDERS":
        validate_public_ip_providers(
            items,
            valid=valid_ipv4_http_providers,
            category="Public IPv4 HTTP Providers",
            allow_custom=True,
        )
    elif category == "PUBLICIPV6_HTTP_PROVIDERS":
        validate_public_ip_providers(
            items,
            valid=valid_ipv6_http_providers,
            category="Public IPv6 HTTP Providers",
            allow_custom=True,
        )
    elif category == "PUBLICIP_FETCHERS":
        validate_public_ip_providers(
            items,
            valid=valid_ip_fetchers,
            category="Public IP Fetchers",
            allow_custom=True,
        )

    for item in items:
        if item["provider"] == "custom":
            result.append(item["custom"])
        else:
            result.append(item["provider"])

    return ",".join(result)


def get_providers_config(items=[]):
    result = []

    for item in items:
        if item["provider"] not in providers_schema.keys():
            utils.throw_error(
                f"Expected [provider] to be one of [{', '.join(providers_schema.keys())}], got [{item['provider']}]"
            )
        if not item.get("host", ""):
            utils.throw_error(
                f"Expected [host] to be set for provider [{item['provider']}]"
            )
        if not item.get("domain", ""):
            utils.throw_error(
                f"Expected [domain] to be set for provider [{item['provider']}]"
            )
        if not item.get("ip_version", "") in valid_ip_versions:
            utils.throw_error(
                f"Expected [ip_version] to be one of [{', '.join(valid_ip_versions)}], got [{item['ip_version']}]"
            )

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


providers_schema = {
    "aliyun": {
        "required": [
            {"provider_key": "access_key_id", "ui_key": "aliyun_access_key"},
            {"provider_key": "access_secret", "ui_key": "aliyun_secret_key"},
        ],
        "optional": [],
    },
    "allinkl": {
        "required": [
            {"provider_key": "username", "ui_key": "allinkl_username"},
            {"provider_key": "password", "ui_key": "allinkl_password"},
        ],
        "optional": [],
    },
    "cloudflare": {
        "required": [
            {"provider_key": "zone_identifier", "ui_key": "cloudflare_zone_id"},
            {"provider_key": "ttl", "ui_key": "cloudflare_ttl"},
        ],
        "optional": [{"provider_key": "proxied", "ui_key": "cloudflare_proxied"}],
        "combos": [
            {
                "required": [{"provider_key": "token", "ui_key": "cloudflare_token"}],
                "optional": [],
            },
            {
                "required": [
                    {
                        "provider_key": "user_service_key",
                        "ui_key": "cloudflare_user_service_key",
                    }
                ],
                "optional": [],
            },
            {
                "required": [
                    {"provider_key": "email", "ui_key": "cloudflare_email"},
                    {"provider_key": "key", "ui_key": "cloudflare_api_key"},
                ],
                "optional": [],
            },
        ],
    },
    "dd24": {
        "required": [{"provider_key": "password", "ui_key": "dd24_password"}],
        "optional": [],
        "combos": [],
    },
    "ddnss": {
        "required": [
            {"provider_key": "username", "ui_key": "ddnss_username"},
            {"provider_key": "password", "ui_key": "ddnss_password"},
        ],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "ddnss_provider_ip",
                "default": False,
            },
            {
                "provider_key": "dual_stack",
                "ui_key": "ddnss_dual_stack",
                "default": False,
            },
        ],
    },
    "desec": {
        "required": [{"provider_key": "token", "ui_key": "desec_token"}],
        "optional": [],
        "combos": [],
    },
    "digitalocean": {
        "required": [{"provider_key": "token", "ui_key": "digital_ocean_token"}],
        "optional": [],
        "combos": [],
    },
    "dnsomatic": {
        "required": [
            {"provider_key": "username", "ui_key": "dnsomatic_username"},
            {"provider_key": "password", "ui_key": "dnsomatic_password"},
        ],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "dnsomatic_provider_ip",
                "default": False,
            }
        ],
    },
    "dnspod": {
        "required": [{"provider_key": "token", "ui_key": "dnspod_token"}],
        "optional": [],
        "combos": [],
    },
    "dondominio": {
        "required": [
            {"provider_key": "username", "ui_key": "dondominio_username"},
            {"provider_key": "password", "ui_key": "dondominio_password"},
            {"provider_key": "name", "ui_key": "dondominio_name"},
        ],
        "optional": [],
        "combos": [],
    },
    "dreamhost": {
        "required": [{"provider_key": "key", "ui_key": "dreamhost_key"}],
        "optional": [],
        "combos": [],
    },
    "duckdns": {
        "required": [{"provider_key": "token", "ui_key": "duckdns_token"}],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "duckdns_provider_ip",
                "default": False,
            }
        ],
        "combos": [],
    },
    "dyn": {
        "required": [
            {"provider_key": "client_key", "ui_key": "dyn_client_key"},
            {"provider_key": "username", "ui_key": "dyn_username"},
        ],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "dyn_provider_ip",
                "default": False,
            }
        ],
        "combos": [],
    },
    "dynu": {
        "required": [
            {"provider_key": "username", "ui_key": "dynu_username"},
            {"provider_key": "password", "ui_key": "dynu_password"},
        ],
        "optional": [
            {"provider_key": "group", "ui_key": "dynu_group"},
            {
                "provider_key": "provider_ip",
                "ui_key": "dynu_provider_ip",
                "default": False,
            },
        ],
    },
    "dynv6": {
        "required": [{"provider_key": "token", "ui_key": "dynv6_token"}],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "dynv6_provider_ip",
                "default": False,
            }
        ],
        "combos": [],
    },
    "easydns": {
        "required": [
            {"provider_key": "username", "ui_key": "easydns_username"},
            {"provider_key": "token", "ui_key": "easydns_token"},
        ],
        "optional": [],
    },
    "freedns": {
        "required": [{"provider_key": "token", "ui_key": "freedns_token"}],
        "optional": [],
    },
    "gandi": {
        "required": [
            {"provider_key": "key", "ui_key": "gandi_key"},
            {"provider_key": "ttl", "ui_key": "gandi_ttl"},
        ],
        "optional": [],
        "combos": [],
    },
    "gcp": {
        "required": [
            {"provider_key": "project", "ui_key": "gcp_project"},
            {"provider_key": "zone", "ui_key": "gcp_zone"},
            {
                "provider_key": "credentials",
                "ui_key": "gcp_credentials",
                "func": lambda x: json.loads(x),
            },
        ],
        "optional": [],
    },
    "godaddy": {
        "required": [
            {"provider_key": "key", "ui_key": "godaddy_key"},
            {"provider_key": "secret", "ui_key": "godaddy_secret"},
        ],
        "optional": [],
        "combos": [],
    },
    "goip": {
        "required": [
            {"provider_key": "username", "ui_key": "goip_username"},
            {"provider_key": "password", "ui_key": "goip_password"},
        ],
        "optional": [],
        "combos": [],
    },
    "he": {
        "required": [{"provider_key": "password", "ui_key": "he_password"}],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "he_provider_ip",
                "default": False,
            }
        ],
    },
    "hetzner": {
        "required": [
            {"provider_key": "token", "ui_key": "hetzner_token"},
            {"provider_key": "zone_identifier", "ui_key": "hetzner_zone_identifier"},
        ],
        "optional": [{"provider_key": "ttl", "ui_key": "hetzner_ttl"}],
    },
    "infomaniak": {
        "required": [
            {"provider_key": "username", "ui_key": "infomaniak_username"},
            {"provider_key": "password", "ui_key": "infomaniak_password"},
        ],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "infomaniak_provider_ip",
                "default": False,
            }
        ],
    },
    "inwx": {
        "required": [
            {"provider_key": "username", "ui_key": "inwx_username"},
            {"provider_key": "password", "ui_key": "inwx_password"},
        ],
        "optional": [],
    },
    "ionos": {
        "required": [{"provider_key": "api_key", "ui_key": "ionos_api_key"}],
        "optional": [],
    },
    "linode": {
        "required": [{"provider_key": "token", "ui_key": "linode_token"}],
        "optional": [],
    },
    "luadns": {
        "required": [
            {"provider_key": "token", "ui_key": "luadns_token"},
            {"provider_key": "email", "ui_key": "luadns_email"},
        ],
        "optional": [],
    },
    "namecheap": {
        "required": [{"provider_key": "password", "ui_key": "namecheap_password"}],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "namecheap_provider_ip",
                "default": False,
            }
        ],
    },
    "name.com": {
        "required": [
            {"provider_key": "token", "ui_key": "namecom_token"},
            {"provider_key": "username", "ui_key": "namecom_username"},
            {"provider_key": "ttl", "ui_key": "namecom_ttl"},
        ],
        "optional": [],
    },
    "netcup": {
        "required": [
            {"provider_key": "api_key", "ui_key": "netcup_api_key"},
            {"provider_key": "password", "ui_key": "netcup_password"},
            {"provider_key": "customer_number", "ui_key": "netcup_customer_number"},
        ],
        "optional": [],
    },
    "njalla": {
        "required": [{"provider_key": "key", "ui_key": "njalla_key"}],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "njalla_provider_ip",
                "default": False,
            }
        ],
    },
    "noip": {
        "required": [
            {"provider_key": "username", "ui_key": "noip_username"},
            {"provider_key": "password", "ui_key": "noip_password"},
        ],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "noip_provider_ip",
                "default": False,
            }
        ],
    },
    "nowdns": {
        "required": [
            {"provider_key": "username", "ui_key": "nowdns_username"},
            {"provider_key": "password", "ui_key": "nowdns_password"},
        ],
        "optional": [],
    },
    "opendns": {
        "required": [
            {"provider_key": "username", "ui_key": "opendns_username"},
            {"provider_key": "password", "ui_key": "opendns_password"},
        ],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "opendns_provider_ip",
                "default": False,
            }
        ],
    },
    "ovh": {
        "required": [{"provider_key": "mode", "ui_key": "ovh_mode"}],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "ovh_provider_ip",
                "default": False,
            }
        ],
        "combos": [
            {
                "required": [
                    {"provider_key": "username", "ui_key": "ovh_username"},
                    {"provider_key": "password", "ui_key": "ovh_password"},
                ],
                "optional": [],
            },
            {
                "required": [
                    {"provider_key": "api_endpoint", "ui_key": "ovh_api_endpoint"},
                    {"provider_key": "app_key", "ui_key": "ovh_app_key"},
                    {"provider_key": "app_secret", "ui_key": "ovh_app_secret"},
                    {"provider_key": "consumer_key", "ui_key": "ovh_consumer_key"},
                ],
                "optional": [],
            },
        ],
    },
    "porkbun": {
        "required": [
            {"provider_key": "api_key", "ui_key": "porkbun_api_key"},
            {"provider_key": "secret_api_key", "ui_key": "porkbun_secret_api_key"},
        ],
        "optional": [{"provider_key": "ttl", "ui_key": "porkbun_ttl"}],
    },
    "route53": {
        "required": [
            {"provider_key": "access_key", "ui_key": "route53_access_key"},
            {"provider_key": "secret_key", "ui_key": "route53_secret_key"},
            {"provider_key": "zone_id", "ui_key": "route53_zone_id"},
        ],
        "optional": [
            {"provider_key": "ttl", "ui_key": "route53_ttl"},
        ],
    },
    "selfhost.de": {
        "required": [
            {"provider_key": "username", "ui_key": "selfhostde_username"},
            {"provider_key": "password", "ui_key": "selfhostde_password"},
        ],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "selfhostde_provider_ip",
                "default": False,
            }
        ],
    },
    "servercow": {
        "required": [
            {"provider_key": "username", "ui_key": "servercow_username"},
            {"provider_key": "password", "ui_key": "servercow_password"},
            {"provider_key": "ttl", "ui_key": "servercow_ttl"},
        ],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "servercow_provider_ip",
                "default": False,
            }
        ],
    },
    "spdyn": {
        "required": [],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "spdyn_provider_ip",
                "default": False,
            }
        ],
        "combos": [
            {
                "required": [{"provider_key": "token", "ui_key": "spdyn_token"}],
                "optional": [],
            },
            {
                "required": [
                    {"provider_key": "user", "ui_key": "spdyn_username"},
                    {"provider_key": "password", "ui_key": "spdyn_password"},
                ],
                "optional": [],
            },
        ],
    },
    "strato": {
        "required": [{"provider_key": "password", "ui_key": "strato_password"}],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "strato_provider_ip",
                "default": False,
            }
        ],
    },
    "variomedia": {
        "required": [
            {"provider_key": "password", "ui_key": "variomedia_password"},
            {"provider_key": "email", "ui_key": "variomedia_email"},
        ],
        "optional": [
            {
                "provider_key": "provider_ip",
                "ui_key": "variomedia_provider_ip",
                "default": False,
            }
        ],
    },
    "zoneedit": {
        "required": [
            {"provider_key": "username", "ui_key": "zoneedit_username"},
            {"provider_key": "token", "ui_key": "zoneedit_token"},
        ],
        "optional": [],
    },
}


def get_provider_config(item={}):
    if item["provider"] not in providers_schema:
        utils.throw_error(
            f"Expected [provider] to be one of [{', '.join(providers_schema.keys())}], got [{item['provider']}]"
        )

    result = {}
    provider_data = providers_schema[item["provider"]]

    for required in provider_data["required"]:
        if required.get("func"):
            result[required["provider_key"]] = required["func"](
                required_key(item, required["ui_key"])
            )
        else:
            result[required["provider_key"]] = required_key(item, required["ui_key"])
    result.update(get_optional_data(item, provider_data))

    combo_data = {}
    for combo in provider_data.get("combos", []):
        if combo_data:
            break

        combo_data = get_combo_data(item, combo)
        # Go to next combo
        if not combo_data:
            continue

        result.update(combo_data)
        result.update(get_optional_data(item, combo))

    if not combo_data and provider_data.get("combos", []):
        utils.throw_error(
            f"Expected provider [{item['provider']}] to have at least one of the following combinations: "
            + f"{', '.join(get_combos_printout(provider_data['combos']))}"
        )

    return result


def get_combo_data(item={}, combo={}):
    result = {}
    for required in combo["required"]:
        if required["ui_key"] not in item:
            return {}
        if required.get("func"):
            result[required["provider_key"]] = required["func"](
                required_key(item, required["ui_key"])
            )
        else:
            result[required["provider_key"]] = required_key(item, required["ui_key"])
    return result


def get_optional_data(item={}, data={}):
    result = {}
    for optional in data["optional"]:
        if optional["ui_key"] in item:
            if optional.get("func"):
                result[optional["provider_key"]] = optional["func"](
                    item[optional["ui_key"]]
                )
            else:
                result[optional["provider_key"]] = item[optional["ui_key"]]
        elif optional.get("default") is not None:
            result[optional["provider_key"]] = optional["default"]
    return result


def get_combos_printout(combos=[]):
    result = []
    for combo in combos:
        result.append(f"[{', '.join([r['provider_key'] for r in combo['required']])}]")
    return result
