# Spoolman

[Spoolman](https://github.com/Donkie/Spoolman) is a self-hosted web service designed to help you efficiently manage your 3D printer filament spools and monitor their weights.

**Storage and Permissions:** The application runs as UID/GID 1000. Ensure your storage dataset has appropriate ownership or ACL permissions configured for UID 1000.

**Security:** Spoolman does not include built-in authentication. Do not expose this application directly to the public internet without placing it behind a reverse proxy with authentication.
