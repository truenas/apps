# Matter.js Server

[Matter.js Server](https://github.com/matter-js/matterjs-server) is a Matter Controller WebSocket server built on the JavaScript Matter SDK. It is a drop-in replacement for the [Python Matter Server](https://github.com/home-assistant-libs/python-matter-server) used by Home Assistant's Matter integration, and exposes the same WebSocket API at `/ws` plus a browser dashboard at `/`.

## Highlights

- Compatible with Home Assistant's Matter integration (point HA at `ws://<truenas-ip>:5580/ws`).
- Exposes an optional BLE proxy endpoint at `/ws/ble` for commissioning Matter devices over Bluetooth (works with ESPHome BT-proxy ESP32s via Home Assistant).
- Bundled web dashboard for inspecting fabrics, nodes, and Thread Border Routers.
- Supports OTA, custom DCL, and the test-net DCL for developer devices.

## Before you install

Matter device discovery needs **mDNS on UDP 5353**. The app defaults to host networking for that reason. **TrueNAS's `avahi-daemon` blocks 5353 by default** — the *Host Network* field help in this app's install form contains the one-line fix (or use the macvlan path if you'd rather not touch the host's Avahi). The Install Notes shown after install have the full walkthrough.

Upstream docs: <https://github.com/matter-js/matterjs-server/blob/main/docs/docker.md>
