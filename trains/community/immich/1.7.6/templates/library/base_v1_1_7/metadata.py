from . import utils


def get_header(app_name: str):
    return f"""# Welcome to TrueNAS SCALE

Thank you for installing {app_name}!
"""


def get_footer(app_name: str):
    return f"""## Documentation

Documentation for {app_name} can be found at https://www.truenas.com/docs.

## Bug reports

If you find a bug in this app, please file an issue at
https://ixsystems.atlassian.net or https://github.com/truenas/apps

## Feature requests or improvements

If you find a feature request for this app, please file an issue at
https://ixsystems.atlassian.net or https://github.com/truenas/apps
"""


def get_notes(app_name: str, body: str = ""):
    if not app_name:
        utils.throw_error("Expected [app_name] to be set")

    return f"{get_header(app_name)}\n\n{body}\n\n{get_footer(app_name)}"


def get_portals(portals: list):
    valid_schemes = ["http", "https"]
    result = []
    for portal in portals:
        # Most apps have a single portal, lets default to a standard name
        name = portal.get("name", "Web UI")
        scheme = portal.get("scheme", "http")
        path = portal.get("path", "/")

        if not name:
            utils.throw_error("Expected [portal.name] to be set")
        if name in [p["name"] for p in result]:
            utils.throw_error(
                f"Expected [portal.name] to be unique, got [{', '.join([p['name'] for p in result]+[name])}]"
            )
        if scheme not in valid_schemes:
            utils.throw_error(
                f"Expected [portal.scheme] to be one of [{', '.join(valid_schemes)}], got [{portal['scheme']}]"
            )
        if not portal.get("port"):
            utils.throw_error("Expected [portal.port] to be set")
        if not path.startswith("/"):
            utils.throw_error(
                f"Expected [portal.path] to start with /, got [{portal['path']}]"
            )

        result.append(
            {
                "name": name,
                "scheme": scheme,
                "host": portal.get("host", "0.0.0.0"),
                "port": portal["port"],
                "path": path,
            }
        )

    return result
