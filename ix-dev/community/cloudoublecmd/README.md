# ClouDouble Commander

ClouDouble Commander provides a web file manager for a TrueNAS path selected during installation. The image is pinned to the verified Linux/amd64 manifest digest for `ghcr.io/sweenyxsky-oss/cloudoublecmd-app`.

## Access and data safety

The installer mounts the selected host path read-write at `/data/pool`. To follow the whole-pool setup, select the pool root, not a child dataset or folder. This gives the app broad read/write access to everything under that mounted root, including the ability to permanently delete files. Only install it on a trusted LAN or behind a VPN/HTTPS reverse proxy, take regular ZFS snapshots/backups, and do not expose the web port directly to the internet. The app does not recursively change ownership or permissions; make sure UID/GID 1000 can access the selected path using your existing ACL/permissions.

Provide a private service access token of at least 32 bytes and a private UI password of at least 12 characters in the installer. The catalog marks both fields private for UI masking; TrueNAS documents that `private: true` masks a value in the form and is not a secrets-vault guarantee. Treat credentials in app configuration and rendered Compose data as sensitive, and use a unique token/password. The service token is for API authentication; the UI password protects browser sign-in.

## Test status and limitations

The source service's automated test suite and the GitHub Actions image build passed for the source revision used to create this package. The rendered catalog template and deployment have not been run through the TrueNAS catalog CI or tested on a TrueNAS host in this preparation. Linux/amd64 is the only verified image architecture; TrueNAS version compatibility and pool-path/ACL behavior still require catalog CI and reviewer/runtime validation.
