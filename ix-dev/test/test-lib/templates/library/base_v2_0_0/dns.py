try:
    from .error import RenderError
    from .validations import must_not_be_disallowed_dns_opt
except ImportError:
    from error import RenderError
    from validations import must_not_be_disallowed_dns_opt


class Dns:
    def __init__(self, render_instance):
        self.render_instance = render_instance
        self.dns_options: set[str] = set()
        self.dns_searches: set[str] = set()
        self.dns_nameservers: set[str] = set()

        self._dns_opt_keys: set[str] = set()

        self.auto_add_dns_opts()
        self.auto_add_dns_searches()
        self.auto_add_dns_nameservers()

    def auto_add_dns_opts(self):
        values = self.render_instance.values
        for dns_opt in values.get("network", {}).get("dns_opts", []):
            self.add_dns_opt(dns_opt)

    def auto_add_dns_searches(self):
        values = self.render_instance.values
        for dns_search in values.get("network", {}).get("dns_searches", []):
            self.add_dns_search(dns_search)

    def auto_add_dns_nameservers(self):
        values = self.render_instance.values
        for dns_nameserver in values.get("network", {}).get("dns_nameservers", []):
            self.add_dns_nameserver(dns_nameserver)

    def add_dns_search(self, dns_search):
        if dns_search in self.dns_searches:
            raise RenderError(f"DNS Search [{dns_search}] already added")
        self.dns_searches.add(dns_search)

    def add_dns_nameserver(self, dns_nameserver):
        if dns_nameserver in self.dns_nameservers:
            raise RenderError(f"DNS Nameserver [{dns_nameserver}] already added")
        self.dns_nameservers.add(dns_nameserver)

    def add_dns_opt(self, dns_opt):
        # eg attempts:3
        key = dns_opt.split(":")[0]
        must_not_be_disallowed_dns_opt(key)
        if key in self._dns_opt_keys:
            raise RenderError(f"DNS Option [{key}] already added")
        self.dns_options.add(dns_opt)
        self._dns_opt_keys.add(key)

    def has_dns_opts(self):
        return len(self.dns_options) > 0

    def has_dns_searches(self):
        return len(self.dns_searches) > 0

    def has_dns_nameservers(self):
        return len(self.dns_nameservers) > 0

    def render_dns_searches(self):
        return sorted(self.dns_searches)

    def render_dns_opts(self):
        return sorted(self.dns_options)

    def render_dns_nameservers(self):
        return sorted(self.dns_nameservers)
