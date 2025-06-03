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


providers_schema = {
    "aliyun": {
        "required": [
            {"provider_key": "access_key_id", "ui_key": "aliyun_access_key"},
            {"provider_key": "access_secret", "ui_key": "aliyun_secret_key"},
        ],
    },
    "allinkl": {
        "required": [
            {"provider_key": "username", "ui_key": "allinkl_username"},
            {"provider_key": "password", "ui_key": "allinkl_password"},
        ],
    },
    "cloudflare": {
        "required": [
            {"provider_key": "zone_identifier", "ui_key": "cloudflare_zone_id"},
            {"provider_key": "ttl", "ui_key": "cloudflare_ttl", "type": "int"},
        ],
        "optional": [{"provider_key": "proxied", "ui_key": "cloudflare_proxied"}],
        "combos": [
            {"required": [{"provider_key": "token", "ui_key": "cloudflare_token"}]},
            {"required": [{"provider_key": "user_service_key", "ui_key": "cloudflare_user_service_key"}]},
            {
                "required": [
                    {"provider_key": "email", "ui_key": "cloudflare_email"},
                    {"provider_key": "key", "ui_key": "cloudflare_api_key"},
                ],
            },
        ],
    },
    "dd24": {
        "required": [{"provider_key": "password", "ui_key": "dd24_password"}],
    },
    "ddnss": {
        "required": [
            {"provider_key": "username", "ui_key": "ddnss_username"},
            {"provider_key": "password", "ui_key": "ddnss_password"},
        ],
        "optional": [
            {"provider_key": "dual_stack", "ui_key": "ddnss_dual_stack", "default": False},
        ],
    },
    "desec": {
        "required": [{"provider_key": "token", "ui_key": "desec_token"}],
    },
    "digitalocean": {
        "required": [{"provider_key": "token", "ui_key": "digital_ocean_token"}],
    },
    "dnsomatic": {
        "required": [
            {"provider_key": "username", "ui_key": "dnsomatic_username"},
            {"provider_key": "password", "ui_key": "dnsomatic_password"},
        ],
    },
    "dnspod": {
        "required": [{"provider_key": "token", "ui_key": "dnspod_token"}],
    },
    "domeneshop": {
        "required": [
            {"provider_key": "token", "ui_key": "domeneshop_token"},
            {"provider_key": "secret", "ui_key": "domeneshop_secret"},
        ],
    },
    "dondominio": {
        "required": [
            {"provider_key": "username", "ui_key": "dondominio_username"},
            {"provider_key": "password", "ui_key": "dondominio_password"},
        ],
    },
    "dreamhost": {
        "required": [{"provider_key": "key", "ui_key": "dreamhost_key"}],
    },
    "duckdns": {
        "required": [{"provider_key": "token", "ui_key": "duckdns_token"}],
    },
    "dyn": {
        "required": [
            {"provider_key": "client_key", "ui_key": "dyn_client_key"},
            {"provider_key": "username", "ui_key": "dyn_username"},
        ],
    },
    "dynu": {
        "required": [
            {"provider_key": "username", "ui_key": "dynu_username"},
            {"provider_key": "password", "ui_key": "dynu_password"},
        ],
        "optional": [{"provider_key": "group", "ui_key": "dynu_group"}],
    },
    "dynv6": {
        "required": [{"provider_key": "token", "ui_key": "dynv6_token"}],
    },
    "easydns": {
        "required": [
            {"provider_key": "username", "ui_key": "easydns_username"},
            {"provider_key": "token", "ui_key": "easydns_token"},
        ],
    },
    "freedns": {
        "required": [{"provider_key": "token", "ui_key": "freedns_token"}],
    },
    "gandi": {
        "required": [
            {"provider_key": "ttl", "ui_key": "gandi_ttl", "type": "int"},
        ],
        "combos": [
            {"required": [{"provider_key": "key", "ui_key": "gandi_key"}]},
            {"required": [{"provider_key": "personal_access_token", "ui_key": "gandi_personal_access_token"}]},
        ],
    },
    "gcp": {
        "required": [
            {"provider_key": "project", "ui_key": "gcp_project"},
            {"provider_key": "zone", "ui_key": "gcp_zone"},
            {"provider_key": "credentials", "ui_key": "gcp_credentials", "func": lambda x: json.loads(x)},
        ],
    },
    "godaddy": {
        "required": [
            {"provider_key": "key", "ui_key": "godaddy_key"},
            {"provider_key": "secret", "ui_key": "godaddy_secret"},
        ],
    },
    "goip": {
        "required": [
            {"provider_key": "username", "ui_key": "goip_username"},
            {"provider_key": "password", "ui_key": "goip_password"},
        ],
    },
    "he": {
        "required": [{"provider_key": "password", "ui_key": "he_password"}],
    },
    "hetzner": {
        "required": [
            {"provider_key": "token", "ui_key": "hetzner_token"},
            {"provider_key": "zone_identifier", "ui_key": "hetzner_zone_identifier"},
        ],
        "optional": [{"provider_key": "ttl", "ui_key": "hetzner_ttl", "type": "int"}],
    },
    "infomaniak": {
        "required": [
            {"provider_key": "username", "ui_key": "infomaniak_username"},
            {"provider_key": "password", "ui_key": "infomaniak_password"},
        ],
    },
    "inwx": {
        "required": [
            {"provider_key": "username", "ui_key": "inwx_username"},
            {"provider_key": "password", "ui_key": "inwx_password"},
        ],
    },
    "ionos": {
        "required": [{"provider_key": "api_key", "ui_key": "ionos_api_key"}],
    },
    "linode": {
        "required": [{"provider_key": "token", "ui_key": "linode_token"}],
    },
    "loopia": {
        "required": [
            {"provider_key": "username", "ui_key": "loopia_username"},
            {"provider_key": "password", "ui_key": "loopia_password"},
        ],
    },
    "luadns": {
        "required": [
            {"provider_key": "token", "ui_key": "luadns_token"},
            {"provider_key": "email", "ui_key": "luadns_email"},
        ],
    },
    "myaddr": {
        "required": [{"provider_key": "key", "ui_key": "myaddr_key"}],
    },
    "namecheap": {
        "required": [{"provider_key": "password", "ui_key": "namecheap_password"}],
    },
    "name.com": {
        "required": [
            {"provider_key": "token", "ui_key": "namecom_token"},
            {"provider_key": "username", "ui_key": "namecom_username"},
            {"provider_key": "ttl", "ui_key": "namecom_ttl", "type": "int"},
        ],
    },
    "namesilo": {
        "required": [{"provider_key": "key", "ui_key": "namesilo_key"}],
        "optional": [{"provider_key": "ttl", "ui_key": "namesilo_ttl", "type": "int"}],
    },
    "netcup": {
        "required": [
            {"provider_key": "api_key", "ui_key": "netcup_api_key"},
            {"provider_key": "password", "ui_key": "netcup_password"},
            {"provider_key": "customer_number", "ui_key": "netcup_customer_number"},
        ],
    },
    "njalla": {
        "required": [{"provider_key": "key", "ui_key": "njalla_key"}],
    },
    "noip": {
        "required": [
            {"provider_key": "username", "ui_key": "noip_username"},
            {"provider_key": "password", "ui_key": "noip_password"},
        ],
    },
    "nowdns": {
        "required": [
            {"provider_key": "username", "ui_key": "nowdns_username"},
            {"provider_key": "password", "ui_key": "nowdns_password"},
        ],
    },
    "opendns": {
        "required": [
            {"provider_key": "username", "ui_key": "opendns_username"},
            {"provider_key": "password", "ui_key": "opendns_password"},
        ],
    },
    "ovh": {
        "required": [{"provider_key": "mode", "ui_key": "ovh_mode"}],
        "combos": [
            {
                "required": [
                    {"provider_key": "username", "ui_key": "ovh_username"},
                    {"provider_key": "password", "ui_key": "ovh_password"},
                ],
            },
            {
                "required": [
                    {"provider_key": "api_endpoint", "ui_key": "ovh_api_endpoint"},
                    {"provider_key": "app_key", "ui_key": "ovh_app_key"},
                    {"provider_key": "app_secret", "ui_key": "ovh_app_secret"},
                    {"provider_key": "consumer_key", "ui_key": "ovh_consumer_key"},
                ],
            },
        ],
    },
    "porkbun": {
        "required": [
            {"provider_key": "api_key", "ui_key": "porkbun_api_key"},
            {"provider_key": "secret_api_key", "ui_key": "porkbun_secret_api_key"},
        ],
        "optional": [{"provider_key": "ttl", "ui_key": "porkbun_ttl", "type": "int"}],
    },
    "route53": {
        "required": [
            {"provider_key": "access_key", "ui_key": "route53_access_key"},
            {"provider_key": "secret_key", "ui_key": "route53_secret_key"},
            {"provider_key": "zone_id", "ui_key": "route53_zone_id"},
        ],
        "optional": [{"provider_key": "ttl", "ui_key": "route53_ttl", "type": "int"}],
    },
    "selfhost.de": {
        "required": [
            {"provider_key": "username", "ui_key": "selfhostde_username"},
            {"provider_key": "password", "ui_key": "selfhostde_password"},
        ],
    },
    "servercow": {
        "required": [
            {"provider_key": "username", "ui_key": "servercow_username"},
            {"provider_key": "password", "ui_key": "servercow_password"},
            {"provider_key": "ttl", "ui_key": "servercow_ttl", "type": "int"},
        ],
    },
    "spdyn": {
        "required": [],
        "combos": [
            {"required": [{"provider_key": "token", "ui_key": "spdyn_token"}]},
            {
                "required": [
                    {"provider_key": "user", "ui_key": "spdyn_username"},
                    {"provider_key": "password", "ui_key": "spdyn_password"},
                ],
            },
        ],
    },
    "strato": {
        "required": [{"provider_key": "password", "ui_key": "strato_password"}],
    },
    "variomedia": {
        "required": [
            {"provider_key": "password", "ui_key": "variomedia_password"},
            {"provider_key": "email", "ui_key": "variomedia_email"},
        ],
    },
    "vultr": {
        "required": [
            {"provider_key": "apikey", "ui_key": "vultr_api_key"},
        ],
        "optional": [{"provider_key": "ttl", "ui_key": "vultr_ttl", "type": "int"}],
    },
    "zoneedit": {
        "required": [
            {"provider_key": "username", "ui_key": "zoneedit_username"},
            {"provider_key": "token", "ui_key": "zoneedit_token"},
        ],
    },
}


class Config:
    def __init__(self, tpl, values):
        self.fail = tpl.funcs["fail"]
        self.warn = tpl.notes.add_warning
        self.values = values

    def validate_public_ip_providers(self, items=[], valid=[], category="", allow_custom=False):
        for item in items:
            if not item.get("provider"):
                self.fail(f"Expected [provider] to be set for [{category}]")
            if item["provider"] == "custom":
                if not allow_custom:
                    self.fail(f"Custom provider is not supported for [{category}]")
                else:
                    if not item.get("custom"):
                        self.fail(f"Expected [custom] to be set when public ip provider is [custom] for [{category}]")
                    if not item["custom"].startswith("url:"):
                        self.fail(f"Expected [custom] to start with [url:] for [{category}]")
            if item["provider"] == "all":
                if len(items) > 1:
                    self.fail(f"Expected only 1 item in [{category}] with [provider] set to [all], got [{len(items)}]")
            if item["provider"] not in valid:
                self.fail(
                    f"Expected [provider] to be one of [{', '.join(valid)}], got [{item['provider']}] for [{category}]"
                )

    def get_public_ip_providers(self, category: str, items=[]):
        result = []

        if category == "PUBLICIP_DNS_PROVIDERS":
            self.validate_public_ip_providers(
                items,
                valid=valid_ip_dns_providers,
                category="Public IP DNS Providers",
                allow_custom=True,
            )
        elif category == "PUBLICIP_HTTP_PROVIDERS":
            self.validate_public_ip_providers(
                items,
                valid=valid_ip_http_providers,
                category="Public IP HTTP Providers",
                allow_custom=True,
            )
        elif category == "PUBLICIPV4_HTTP_PROVIDERS":
            self.validate_public_ip_providers(
                items,
                valid=valid_ipv4_http_providers,
                category="Public IPv4 HTTP Providers",
                allow_custom=True,
            )
        elif category == "PUBLICIPV6_HTTP_PROVIDERS":
            self.validate_public_ip_providers(
                items,
                valid=valid_ipv6_http_providers,
                category="Public IPv6 HTTP Providers",
                allow_custom=True,
            )
        elif category == "PUBLICIP_FETCHERS":
            self.validate_public_ip_providers(
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

    def get_providers_config(self, items=[]):
        result = []

        for item in items:
            if item["provider"] not in providers_schema.keys():
                self.fail(
                    f"Expected [provider] to be one of [{', '.join(providers_schema.keys())}], got [{item['provider']}]"
                )
            if not item.get("domain", ""):
                self.fail(f"Expected [domain] to be set for provider [{item['provider']}]")
            if item.get("host", ""):
                self.warn(
                    f"Provider [{item['provider']}] has deprecated [host] field set, with value [{item['host']}]."
                )
            if not item.get("ip_version", "") in valid_ip_versions:
                self.fail(
                    f"Expected [ip_version] to be one of [{', '.join(valid_ip_versions)}], got [{item['ip_version']}]"
                )

            result.append(
                {
                    "provider": item["provider"],
                    "domain": item["domain"],
                    "ip_version": item.get("ip_version", ""),
                    **self.get_provider_config(item),
                }
            )

        return {"settings": result}

    def required_key(self, item={}, key=""):
        if not item.get(key):
            self.fail(f"Expected [{key}] to be set for [{item['provider']}]")
        return item[key]

    def get_provider_config(self, item={}):
        if item["provider"] not in providers_schema:
            self.fail(
                f"Expected [provider] to be one of [{', '.join(providers_schema.keys())}], got [{item['provider']}]"
            )

        result = {}
        provider_data = providers_schema[item["provider"]]

        for required in provider_data["required"]:
            if required.get("func"):
                result[required["provider_key"]] = required["func"](self.required_key(item, required["ui_key"]))
            else:
                match required.get("type", ""):
                    case "int":
                        result[required["provider_key"]] = int(self.required_key(item, required["ui_key"]))
                    case _:
                        result[required["provider_key"]] = str(self.required_key(item, required["ui_key"]))
        result.update(self.get_optional_data(item, provider_data))

        combo_data = {}
        for combo in provider_data.get("combos", []):
            if combo_data:
                break

            combo_data = self.get_combo_data(item, combo)
            # Go to next combo
            if not combo_data:
                continue

            result.update(combo_data)
            result.update(self.get_optional_data(item, combo))

        if not combo_data and provider_data.get("combos", []):
            self.fail(
                f"Expected provider [{item['provider']}] to have at least one of the following combinations: "
                + f"{', '.join(self.get_combos_printout(provider_data['combos']))}"
            )

        return result

    def get_combo_data(self, item={}, combo={}):
        result = {}
        for required in combo["required"]:
            if required["ui_key"] not in item or item[required["ui_key"]] == "":
                return {}
            if required.get("func"):
                result[required["provider_key"]] = required["func"](self.required_key(item, required["ui_key"]))
            else:
                result[required["provider_key"]] = self.required_key(item, required["ui_key"])
        return result

    def get_optional_data(self, item={}, data={}):
        result = {}
        for optional in data.get("optional", []):
            if optional["ui_key"] in item:
                if optional.get("func"):
                    result[optional["provider_key"]] = optional["func"](item[optional["ui_key"]])
                else:
                    result[optional["provider_key"]] = item[optional["ui_key"]]
            elif optional.get("default") is not None:
                result[optional["provider_key"]] = optional["default"]
        return result

    def get_combos_printout(self, combos=[]):
        result = []
        for combo in combos:
            result.append(f"[{', '.join([r['provider_key'] for r in combo['required']])}]")
        return result
