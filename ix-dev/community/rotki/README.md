# Rotki

Rotki is an open-source portfolio tracker, accounting and analytics tool that keeps
your financial data locally. Track blockchain addresses, exchanges and DeFi positions.

Create a Rotki account in the Web UI after installation. Your account password
protects the encrypted local database; the catalog Session Key protects API sessions.
Generate a random Session Key with `openssl rand -hex 32` and keep it across upgrades.

The data storage contains the encrypted user databases and global asset database.
The logs storage contains backend logs. Back up data storage before upgrading.
For host-path storage, grant the configured user/group access to both directories.

Keep the app on a trusted private network, or behind an authenticating reverse proxy
that terminates HTTPS. Enable secure cookies only when accessing the app over HTTPS.
Do not expose the app port directly to the internet.

Rotki runs without root and uses the upstream image's native health probe.
Wallet addresses and exchange connections are configured inside Rotki.

See the [upstream Docker documentation](https://docs.rotki.com/requirement-and-installation/docker).
