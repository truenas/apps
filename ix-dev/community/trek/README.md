# TREK

[TREK](https://github.com/liketrek/TREK) is a self-hosted, collaborative travel planner with interactive maps, itineraries, bookings, budgets, packing lists, and a mobile-friendly PWA.

The app stores its database and configuration in `/app/data` and uploaded files in `/app/uploads`; both locations are persisted separately. TREK creates and persists its encryption key in the data directory unless an `ENCRYPTION_KEY` is supplied. Keep that key unchanged when restoring or moving an instance.

Set the initial admin email and password in the TrueNAS install form. TREK uses them to create the first administrator on startup; changing these app settings later does not change the existing account. Secure Cookies is disabled by default for direct HTTP access from the TrueNAS UI. If you expose TREK through HTTPS, enable Secure Cookies in the app settings and set `TRUST_PROXY=1` in Additional Environment Variables; the reverse proxy must support WebSocket upgrades for `/ws`.
