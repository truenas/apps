# Wealthfolio

[Wealthfolio](https://wealthfolio.app) is an open-source, private portfolio tracker for investments, net worth, spending, and simulations. All data is stored locally with no cloud dependencies.

For more information and configuration options, see the [Wealthfolio documentation](https://github.com/wealthfolio/wealthfolio).

## Configuration

- `WF_SECRET_KEY` — Required. A 32-byte key used for secrets encryption and JWT signing. Generate with: `openssl rand -base64 32`
- `WF_AUTH_PASSWORD_HASH` — Optional. Argon2id PHC string to enable password authentication. Generate with: `printf 'your-password' | argon2 yoursalt16chars! -id -e`
- `WF_CORS_ALLOW_ORIGINS` — Optional. Comma-separated list of allowed CORS origins. Required when auth is enabled.
- `WF_AUTH_REQUIRED` — Optional. Set to `false` to skip authentication (only use behind a trusted reverse proxy).

Note: `WF_LISTEN_ADDR` and `WF_DB_PATH` are managed automatically by this app and cannot be overridden via additional environment variables.
