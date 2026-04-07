# TeslaMate

[TeslaMate](https://docs.teslamate.org/) is a self-hosted data logger for your Tesla.

It provides detailed driving and charging statistics, MQTT integration for home automation,
and supports rich visualizations via Grafana.

## Grafana Dashboards

TeslaMate does not bundle a Grafana instance. To use the official TeslaMate dashboards you need
to install Grafana separately (e.g. the Grafana app from the TrueNAS app catalog) and set it up
manually.

### 1. Install required Grafana plugins

The following community plugins must be installed in your Grafana instance before dashboards
will render correctly. Install them via **Administration → Plugins** or by setting the
`GF_INSTALL_PLUGINS` environment variable on your Grafana app:

- `pr0ps-trackmap-panel`
- `natel-discrete-panel`
- `grafana-piechart-panel`
- `panodata-map-panel`

### 2. Connect Grafana to the TeslaMate database

Grafana queries the TeslaMate PostgreSQL database directly. For this to work, your Grafana
instance must be able to reach the `postgres` container.

**On TrueNAS SCALE (recommended):**

1. In your Grafana app settings, go to **Network Configuration → Networks**
2. Add the TeslaMate app network (typically `ix-teslamate`) to the Grafana containers
3. In Grafana, create a new **PostgreSQL** datasource with:
   - **Host**: `postgres:5432` (the internal container name, reachable once networks are joined)
   - **Database**: `teslamate`
   - **User**: `teslamate`
   - **Password**: the database password you set in TeslaMate
   - **SSL Mode**: `disable`

**External Grafana (different host):**

Expose the PostgreSQL port via **Network Configuration** in the TeslaMate app, then configure
the datasource using your TrueNAS host IP and the exposed port.

### 3. Import the dashboards

1. Download the official TeslaMate dashboards from the
   [TeslaMate GitHub repository](https://github.com/teslamate-org/teslamate/tree/master/grafana/dashboards)
2. In Grafana, go to **Dashboards → Import** and upload each dashboard JSON file
3. Select the `TeslaMate` PostgreSQL datasource when prompted

## TeslaMateAPI

The optional [TeslaMateAPI](https://github.com/tobiasehlert/teslamateapi) container exposes
a REST API for TeslaMate data, useful for home automation integrations (e.g. Home Assistant).
Enable it under **TeslaMate Configuration → Enable TeslaMateAPI**.

An API token (minimum 32 characters) is recommended. Leave it empty to disable authentication.

## MQTT

TeslaMate publishes vehicle data to an MQTT broker. Configure the broker hostname and port
under **TeslaMate Configuration**. If you do not use MQTT, enable **Disable MQTT**.
