# Vaultwarden

[Vaultwarden](https://github.com/dani-garcia/vaultwarden) Alternative implementation of the `Bitwarden` server API written in Rust and compatible with upstream Bitwarden clients

While the option to use `Rocket` for TLS is there, it is not
[recommended](https://github.com/dani-garcia/vaultwarden/wiki/Enabling-HTTPS#via-rocket).
Instead, use a reverse proxy to handle TLS termination.

Using `HTTPS` is **required** for the most of the features to work (correctly).
