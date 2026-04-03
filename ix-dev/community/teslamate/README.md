# TeslaMate

[TeslaMate](https://docs.teslamate.org/) is a self-hosted data logger for your Tesla.

It provides detailed driving and charging statistics, MQTT integration for home automation,
and supports rich visualizations via Grafana.

## Grafana Dashboards

TeslaMate does not bundle a Grafana instance. To use the official TeslaMate dashboards,
enable the **Import TeslaMate Dashboards to External Grafana** option during installation.
When enabled, a one-time init container runs on each app start to:

1. Create or update a `TeslaMate` PostgreSQL datasource in your Grafana instance
2. Create a `TeslaMate` folder in Grafana
3. Download and import all official dashboards from the TeslaMate GitHub repository

### Required Grafana plugins

The following community plugins must be installed in your Grafana instance before dashboards
will render correctly. Install them via **Administration → Plugins** or by setting the
`GF_INSTALL_PLUGINS` environment variable on your Grafana app:

- `pr0ps-trackmap-panel`
- `natel-discrete-panel`
- `grafana-piechart-panel`
- `panodata-map-panel`

### Creating a Grafana Service Account

The importer uses the Grafana HTTP API authenticated with a Service Account token:

1. In your Grafana instance, go to **Administration → Service Accounts**
2. Click **Add service account**, give it a name (e.g. `teslamate-importer`), set Role to **Editor**, click **Create**
3. Open the new service account, click **Add service account token**, copy the generated token
4. Paste the token into the **Grafana Service Account Token** field during TeslaMate installation

### Connecting Grafana to the TeslaMate database

Grafana queries the TeslaMate PostgreSQL database directly. For this to work, your Grafana
instance must be able to reach the postgres container.

**On TrueNAS SCALE (recommended):**

1. In your Grafana app settings, go to **Network Configuration → Networks**
2. Add the TeslaMate app network (typically `ix-teslamate`) to the Grafana containers
3. Leave the **Database Host** field empty in TeslaMate settings — it defaults to the
   internal `postgres` container name, which is reachable once networks are joined

**External Grafana (different host):**

Set the **Database Host** field to the IP address or hostname of your TrueNAS system and
expose the postgres port via **Network Configuration** in the TeslaMate app.

## TeslaMateAPI

The optional [TeslaMateAPI](https://github.com/tobiasehlert/teslamateapi) container exposes
a REST API for TeslaMate data, useful for home automation integrations (e.g. Home Assistant).
Enable it under **TeslaMate Configuration → Enable TeslaMateAPI**.

An API token (minimum 32 characters) is recommended. Leave it empty to disable authentication.

## MQTT

TeslaMate publishes vehicle data to an MQTT broker. Configure the broker hostname and port
under **TeslaMate Configuration**. If you do not use MQTT, enable **Disable MQTT**.
