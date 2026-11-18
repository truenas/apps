# SignalDB

[SignalDB](https://github.com/cedricziel/signaldb) stores metrics, logs, and traces with native OTLP ingestion and an Explore UI.
The app includes PostgreSQL for metadata and an optional MCP server.

Before the first start, create **signaldb.toml** in the Data storage directory with at least one tenant and API key.
The app does not create or overwrite this file. Keep it readable by the configured user and restrict access, because it contains API keys.
See [Getting an API key](https://github.com/cedricziel/signaldb/blob/main/docs/users/authentication.md#getting-an-api-key)
and the annotated [signaldb.dist.toml](https://github.com/cedricziel/signaldb/blob/main/signaldb.dist.toml) for the format.

Send OTLP requests with an **Authorization: Bearer** header carrying the API key and an **X-Tenant-ID** header naming the tenant.
Use the same key to sign in to the Explore UI.
