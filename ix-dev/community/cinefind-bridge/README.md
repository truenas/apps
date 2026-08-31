# CineFind Bridge

CineFind Bridge sends movies and series found by CineFind to private Seerr,
Radarr and Sonarr instances. Use Seerr as before, connect Radarr/Sonarr
directly, or configure all three and choose a destination in CineFind.

The app makes an outbound connection to CineFind; no public IP, incoming port,
Cloudflare Tunnel or router configuration is needed. Your service URLs, API
keys and full root-folder paths stay in the TrueNAS app and are never stored
by CineFind.

Create a one-time pairing code in **CineFind Account → CineFind Bridge**, then
paste the code and at least one complete URL/API-key pair into the installation
form. Seerr supports movies and series; Radarr handles movies and Sonarr
handles series.
