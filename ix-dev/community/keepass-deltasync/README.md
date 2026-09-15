# KeePass DeltaSync

[KeePass DeltaSync](https://gitlab.com/Star95/keepass-deltasync) is a self-hosted
sync server for KeePass `kdbx` databases. Entries are synced as end-to-end
encrypted deltas — the server only ever stores ciphertext and never sees your
master password or keys.

Clients are available for desktop (CLI and GUI), Android and as a browser
extension.

## First start

Open `/admin.html` on the app's address and sign in with the **Admin Username**
and **Admin Password** you set during installation. From there you create users
and issue enrollment tokens for your devices — each one is shown as a QR code
the Android app can scan.

Forgot them? They are in the app's configuration, under **Edit → KeePass
DeltaSync Configuration**.

The server speaks plain HTTP. Put an HTTPS-terminating reverse proxy in front of
it before exposing it to the internet.
