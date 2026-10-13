# SignalDB

SignalDB stores metrics, logs, and traces with OTLP ingestion and an Explore UI.
The app includes PostgreSQL for metadata and an optional MCP server.

## Configure a tenant

Create `signaldb.toml` in the Data storage directory before starting the app.
The container reads this file as `/data/signaldb.toml`. Keep it readable by the
configured SignalDB user and restrict access because it contains API keys.

Use this example with your own randomly generated API key:

```toml
[[auth.tenants]]
id = "default"
slug = "default"
name = "Default Tenant"
default_dataset = "default"

[[auth.tenants.api_keys]]
key = "REPLACE_WITH_A_LONG_RANDOM_API_KEY"
name = "Default Key"

[[auth.tenants.datasets]]
id = "default"
slug = "default"
is_default = true
```

Send OTLP requests with `Authorization: Bearer <api key>` and
`X-Tenant-ID: default`. Use the same key to sign in to the Explore UI.

The app manages database, storage, memory budgets, public URLs, and the optional
admin API key through environment variables. These override matching TOML
settings. The app does not create or overwrite `signaldb.toml`.

For additional settings, see the [SignalDB documentation](https://github.com/cedricziel/signaldb/tree/main/docs).
