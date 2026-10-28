# TREK

[TREK](https://github.com/liketrek/TREK) is a self-hosted, collaborative travel planner with interactive maps, itineraries, bookings, budgets, packing lists, and a mobile-friendly PWA.

The app stores its database and configuration in `/app/data` and uploaded files in `/app/uploads`; both locations are persisted separately. TREK creates and persists its encryption key in the data directory unless an `ENCRYPTION_KEY` is supplied. Keep that key unchanged when restoring or moving an instance.

The initial admin credentials are generated on first startup and printed in the app logs unless both `ADMIN_EMAIL` and `ADMIN_PASSWORD` are configured before the first launch. The default cookie setting supports direct HTTP access from the TrueNAS UI. If you expose TREK through HTTPS, configure `COOKIE_SECURE=true` and `TRUST_PROXY=1` in Additional Environment Variables; the reverse proxy must support WebSocket upgrades for `/ws`.
