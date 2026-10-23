# UniHub

[UniHub](https://github.com/mrksrus/selfhost-unihub) combines mail, contacts, calendars,
tasks, notes and recordings in a self-hosted web app.

Private noncommercial self-hosting is free. Business use requires a separate
licence. See the [licensing terms](https://github.com/mrksrus/selfhost-unihub/blob/main/LICENSING.md).
UniHub is developed and maintained with AI assistance.

Configure an external HTTPS reverse proxy before signing in. Keep MariaDB,
uploads and encryption keys across updates. This installer supports fresh
installations and does not automatically import existing custom-app data.
See the [installation guide](https://github.com/mrksrus/selfhost-unihub/blob/main/docs/INSTALLATION.md).

To change the stored-data encryption key, back up first and put its old value in
Previous Encryption Key before setting a new one. Keep the previous key while
old encrypted values remain; UniHub does not rewrite them automatically. If
Separate Backup Master Key was empty, set it to the old encryption key before
the change so existing backups remain unlockable. See
[changing the encryption key](https://github.com/mrksrus/selfhost-unihub/blob/v0.23.0/docs/INSTALLATION.md#changing-the-encryption-key).

Version 0.23.0 upgrades the database and the stored-secret format. Take a database
and uploads backup before updating. To roll back, restore that backup and its
keys instead of only switching to an older image. See the
[upgrade notes](https://github.com/mrksrus/selfhost-unihub/blob/v0.23.0/docs/UPGRADING.md#0230-hardening).

Account backup, import and restore are experimental. Keep an independent backup
of the database, uploads, configuration and keys.
