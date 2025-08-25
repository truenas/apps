import json
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Union


# Keep the original constants but with better organization
class PublicIPProviders:
    """Centralized definition of all public IP provider configurations"""

    DNS = ["all", "cloudflare", "opendns"]
    IPV4_HTTP = ["all", "ipleak", "ipify", "icanhazip", "ident", "nnev", "wtfismyip", "seeip"]
    IPV6_HTTP = ["all", "ipleak", "ipify", "icanhazip", "ident", "nnev", "wtfismyip", "seeip"]
    FETCHERS = ["all", "http", "dns"]
    HTTP = [
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


class IPVersions:
    """Valid IP version specifications"""

    UNSPECIFIED = ""
    IPV4 = "ipv4"
    IPV6 = "ipv6"

    ALL = [UNSPECIFIED, IPV4, IPV6]


class FieldType:
    """Field type constants"""

    STRING = "str"
    INTEGER = "int"
    BOOLEAN = "bool"


@dataclass
class ProviderField:
    """Represents a configuration field for a provider"""

    provider_key: str
    ui_key: str
    field_type: str = FieldType.STRING
    default: Optional[Any] = None
    func: Optional[Callable] = None


@dataclass
class ProviderCombo:
    """Represents an authentication combination"""

    required: List[ProviderField]
    optional: List[ProviderField] = field(default_factory=list)


@dataclass
class ProviderSchema:
    """Schema definition for a DNS provider"""

    required: List[ProviderField] = field(default_factory=list)
    optional: List[ProviderField] = field(default_factory=list)
    combos: List[ProviderCombo] = field(default_factory=list)


# Convert the old dictionary schema to use dataclasses
providers_schema: Dict[str, ProviderSchema] = {
    "aliyun": ProviderSchema(
        required=[
            ProviderField("access_key_id", "aliyun_access_key"),
            ProviderField("access_secret", "aliyun_secret_key"),
        ],
    ),
    "allinkl": ProviderSchema(
        required=[
            ProviderField("username", "allinkl_username"),
            ProviderField("password", "allinkl_password"),
        ],
    ),
    "changeip": ProviderSchema(
        required=[
            ProviderField("username", "changeip_username"),
            ProviderField("password", "changeip_password"),
        ],
    ),
    "cloudflare": ProviderSchema(
        required=[
            ProviderField("zone_identifier", "cloudflare_zone_id"),
            ProviderField("ttl", "cloudflare_ttl", FieldType.INTEGER),
        ],
        optional=[ProviderField("proxied", "cloudflare_proxied", FieldType.BOOLEAN)],
        combos=[
            ProviderCombo([ProviderField("token", "cloudflare_token")]),
            ProviderCombo([ProviderField("user_service_key", "cloudflare_user_service_key")]),
            ProviderCombo(
                [
                    ProviderField("email", "cloudflare_email"),
                    ProviderField("key", "cloudflare_api_key"),
                ]
            ),
        ],
    ),
    "dd24": ProviderSchema(
        required=[ProviderField("password", "dd24_password")],
    ),
    "ddnss": ProviderSchema(
        required=[
            ProviderField("username", "ddnss_username"),
            ProviderField("password", "ddnss_password"),
        ],
        optional=[
            ProviderField("dual_stack", "ddnss_dual_stack", FieldType.BOOLEAN, default=False),
        ],
    ),
    "desec": ProviderSchema(
        required=[ProviderField("token", "desec_token")],
    ),
    "digitalocean": ProviderSchema(
        required=[ProviderField("token", "digital_ocean_token")],
    ),
    "dnsomatic": ProviderSchema(
        required=[
            ProviderField("username", "dnsomatic_username"),
            ProviderField("password", "dnsomatic_password"),
        ],
    ),
    "dnspod": ProviderSchema(
        required=[ProviderField("token", "dnspod_token")],
    ),
    "domeneshop": ProviderSchema(
        required=[
            ProviderField("token", "domeneshop_token"),
            ProviderField("secret", "domeneshop_secret"),
        ],
    ),
    "dondominio": ProviderSchema(
        required=[
            ProviderField("username", "dondominio_username"),
            ProviderField("password", "dondominio_password"),
        ],
    ),
    "dreamhost": ProviderSchema(
        required=[ProviderField("key", "dreamhost_key")],
    ),
    "duckdns": ProviderSchema(
        required=[ProviderField("token", "duckdns_token")],
    ),
    "dyn": ProviderSchema(
        required=[
            ProviderField("client_key", "dyn_client_key"),
            ProviderField("username", "dyn_username"),
        ],
    ),
    "dynu": ProviderSchema(
        required=[
            ProviderField("username", "dynu_username"),
            ProviderField("password", "dynu_password"),
        ],
        optional=[ProviderField("group", "dynu_group")],
    ),
    "dynv6": ProviderSchema(
        required=[ProviderField("token", "dynv6_token")],
    ),
    "easydns": ProviderSchema(
        required=[
            ProviderField("username", "easydns_username"),
            ProviderField("token", "easydns_token"),
        ],
    ),
    "freedns": ProviderSchema(
        required=[ProviderField("token", "freedns_token")],
    ),
    "gandi": ProviderSchema(
        required=[
            ProviderField("ttl", "gandi_ttl", FieldType.INTEGER),
        ],
        combos=[
            ProviderCombo([ProviderField("key", "gandi_key")]),
            ProviderCombo([ProviderField("personal_access_token", "gandi_personal_access_token")]),
        ],
    ),
    "gcp": ProviderSchema(
        required=[
            ProviderField("project", "gcp_project"),
            ProviderField("zone", "gcp_zone"),
            ProviderField("credentials", "gcp_credentials", func=json.loads),
        ],
    ),
    "godaddy": ProviderSchema(
        required=[
            ProviderField("key", "godaddy_key"),
            ProviderField("secret", "godaddy_secret"),
        ],
    ),
    "goip": ProviderSchema(
        required=[
            ProviderField("username", "goip_username"),
            ProviderField("password", "goip_password"),
        ],
    ),
    "he": ProviderSchema(
        required=[ProviderField("password", "he_password")],
    ),
    "hetzner": ProviderSchema(
        required=[
            ProviderField("token", "hetzner_token"),
            ProviderField("zone_identifier", "hetzner_zone_identifier"),
        ],
        optional=[ProviderField("ttl", "hetzner_ttl", FieldType.INTEGER)],
    ),
    "infomaniak": ProviderSchema(
        required=[
            ProviderField("username", "infomaniak_username"),
            ProviderField("password", "infomaniak_password"),
        ],
    ),
    "inwx": ProviderSchema(
        required=[
            ProviderField("username", "inwx_username"),
            ProviderField("password", "inwx_password"),
        ],
    ),
    "ionos": ProviderSchema(
        required=[ProviderField("api_key", "ionos_api_key")],
    ),
    "linode": ProviderSchema(
        required=[ProviderField("token", "linode_token")],
    ),
    "loopia": ProviderSchema(
        required=[
            ProviderField("username", "loopia_username"),
            ProviderField("password", "loopia_password"),
        ],
    ),
    "luadns": ProviderSchema(
        required=[
            ProviderField("token", "luadns_token"),
            ProviderField("email", "luadns_email"),
        ],
    ),
    "myaddr": ProviderSchema(
        required=[ProviderField("key", "myaddr_key")],
    ),
    "namecheap": ProviderSchema(
        required=[ProviderField("password", "namecheap_password")],
    ),
    "name.com": ProviderSchema(
        required=[
            ProviderField("token", "namecom_token"),
            ProviderField("username", "namecom_username"),
            ProviderField("ttl", "namecom_ttl", FieldType.INTEGER),
        ],
    ),
    "namesilo": ProviderSchema(
        required=[ProviderField("key", "namesilo_key")],
        optional=[ProviderField("ttl", "namesilo_ttl", FieldType.INTEGER)],
    ),
    "netcup": ProviderSchema(
        required=[
            ProviderField("api_key", "netcup_api_key"),
            ProviderField("password", "netcup_password"),
            ProviderField("customer_number", "netcup_customer_number"),
        ],
    ),
    "njalla": ProviderSchema(
        required=[ProviderField("key", "njalla_key")],
    ),
    "noip": ProviderSchema(
        required=[
            ProviderField("username", "noip_username"),
            ProviderField("password", "noip_password"),
        ],
    ),
    "nowdns": ProviderSchema(
        required=[
            ProviderField("username", "nowdns_username"),
            ProviderField("password", "nowdns_password"),
        ],
    ),
    "opendns": ProviderSchema(
        required=[
            ProviderField("username", "opendns_username"),
            ProviderField("password", "opendns_password"),
        ],
    ),
    "ovh": ProviderSchema(
        required=[ProviderField("mode", "ovh_mode")],
        combos=[
            ProviderCombo(
                [
                    ProviderField("username", "ovh_username"),
                    ProviderField("password", "ovh_password"),
                ]
            ),
            ProviderCombo(
                [
                    ProviderField("api_endpoint", "ovh_api_endpoint"),
                    ProviderField("app_key", "ovh_app_key"),
                    ProviderField("app_secret", "ovh_app_secret"),
                    ProviderField("consumer_key", "ovh_consumer_key"),
                ]
            ),
        ],
    ),
    "porkbun": ProviderSchema(
        required=[
            ProviderField("api_key", "porkbun_api_key"),
            ProviderField("secret_api_key", "porkbun_secret_api_key"),
        ],
        optional=[ProviderField("ttl", "porkbun_ttl", FieldType.INTEGER)],
    ),
    "route53": ProviderSchema(
        required=[
            ProviderField("access_key", "route53_access_key"),
            ProviderField("secret_key", "route53_secret_key"),
            ProviderField("zone_id", "route53_zone_id"),
        ],
        optional=[ProviderField("ttl", "route53_ttl", FieldType.INTEGER)],
    ),
    "selfhost.de": ProviderSchema(
        required=[
            ProviderField("username", "selfhostde_username"),
            ProviderField("password", "selfhostde_password"),
        ],
    ),
    "servercow": ProviderSchema(
        required=[
            ProviderField("username", "servercow_username"),
            ProviderField("password", "servercow_password"),
            ProviderField("ttl", "servercow_ttl", FieldType.INTEGER),
        ],
    ),
    "spdyn": ProviderSchema(
        combos=[
            ProviderCombo([ProviderField("token", "spdyn_token")]),
            ProviderCombo(
                [
                    ProviderField("user", "spdyn_username"),
                    ProviderField("password", "spdyn_password"),
                ]
            ),
        ],
    ),
    "strato": ProviderSchema(
        required=[ProviderField("password", "strato_password")],
    ),
    "variomedia": ProviderSchema(
        required=[
            ProviderField("password", "variomedia_password"),
            ProviderField("email", "variomedia_email"),
        ],
    ),
    "vultr": ProviderSchema(
        required=[ProviderField("apikey", "vultr_api_key")],
        optional=[ProviderField("ttl", "vultr_ttl", FieldType.INTEGER)],
    ),
    "zoneedit": ProviderSchema(
        required=[
            ProviderField("username", "zoneedit_username"),
            ProviderField("token", "zoneedit_token"),
        ],
    ),
}


class Config:
    def __init__(self, tpl, values):
        self.fail = tpl.funcs["fail"]
        self.warn = tpl.notes.add_warning
        self.values = values

    def validate_public_ip_providers(
        self, items: List[Dict[str, Any]], valid: List[str], category: str = "", allow_custom: bool = False
    ) -> None:

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

    def get_public_ip_providers(self, category: str, items: List[Dict[str, Any]]) -> str:
        items = items or []
        result = []

        if category == "PUBLICIP_DNS_PROVIDERS":
            self.validate_public_ip_providers(
                items, PublicIPProviders.DNS, "Public IP DNS Providers", allow_custom=True
            )
        elif category == "PUBLICIP_HTTP_PROVIDERS":
            self.validate_public_ip_providers(
                items, PublicIPProviders.HTTP, "Public IP HTTP Providers", allow_custom=True
            )
        elif category == "PUBLICIPV4_HTTP_PROVIDERS":
            self.validate_public_ip_providers(
                items, PublicIPProviders.IPV4_HTTP, "Public IPv4 HTTP Providers", allow_custom=True
            )
        elif category == "PUBLICIPV6_HTTP_PROVIDERS":
            self.validate_public_ip_providers(
                items, PublicIPProviders.IPV6_HTTP, "Public IPv6 HTTP Providers", allow_custom=True
            )
        elif category == "PUBLICIP_FETCHERS":
            self.validate_public_ip_providers(
                items, PublicIPProviders.FETCHERS, "Public IP Fetchers", allow_custom=True
            )

        for item in items:
            if item["provider"] == "custom":
                result.append(item["custom"])
            else:
                result.append(item["provider"])

        return ",".join(result)

    def get_providers_config(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        items = items or []
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

            if not item.get("ip_version", "") in IPVersions.ALL:
                self.fail(
                    f"Expected [ip_version] to be one of [{', '.join(IPVersions.ALL)}], got [{item['ip_version']}]"
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

    def required_key(self, item: Dict[str, Any], key: str) -> Any:
        if not item.get(key):
            self.fail(f"Expected [{key}] to be set for [{item['provider']}]")
        return item[key]

    def get_provider_config(self, item: Dict[str, Any]) -> Dict[str, Any]:
        if item["provider"] not in providers_schema:
            self.fail(
                f"Expected [provider] to be one of [{', '.join(providers_schema.keys())}], got [{item['provider']}]"
            )

        result = {}
        provider_data = providers_schema[item["provider"]]

        # Process required fields
        for required_field in provider_data.required:
            value = self.required_key(item, required_field.ui_key)
            result[required_field.provider_key] = self._convert_field_value(value, required_field)

        # Process optional fields
        result.update(self.get_optional_data(item, provider_data))

        combo_data = {}
        for combo in provider_data.combos:
            if combo_data:
                break

            combo_data = self.get_combo_data(item, combo)
            # Go to next combo
            if not combo_data:
                continue

            result.update(combo_data)
            result.update(self.get_optional_data(item, combo))

        if not combo_data and provider_data.combos:
            self.fail(
                f"Expected provider [{item['provider']}] to have at least one of the following combinations: "
                + f"{', '.join(self.get_combos_printout(provider_data.combos))}"
            )

        return result

    def get_combo_data(self, item: Dict[str, Any], combo: ProviderCombo) -> Dict[str, Any]:
        """Get combo authentication data"""
        result = {}
        for required_field in combo.required:
            if required_field.ui_key not in item or item[required_field.ui_key] == "":
                return {}
            result[required_field.provider_key] = self._convert_field_value(
                self.required_key(item, required_field.ui_key), required_field
            )
        return result

    def get_optional_data(self, item: Dict[str, Any], data: Union[ProviderSchema, ProviderCombo]) -> Dict[str, Any]:
        result = {}
        for optional_field in data.optional:
            if optional_field.ui_key in item:
                result[optional_field.provider_key] = self._convert_field_value(
                    item[optional_field.ui_key], optional_field
                )
            elif optional_field.default is not None:
                result[optional_field.provider_key] = optional_field.default
        return result

    def get_combos_printout(self, combos: List[ProviderCombo]) -> List[str]:
        result = []
        for combo in combos:
            result.append(f"[{', '.join([field.provider_key for field in combo.required])}]")
        return result

    def _convert_field_value(self, value: Any, field: ProviderField) -> Any:
        """Convert field value to appropriate type"""
        if field.func:
            return field.func(value)

        if field.field_type == FieldType.INTEGER:
            return int(value)
        elif field.field_type == FieldType.BOOLEAN:
            return bool(value)
        else:
            return str(value)
