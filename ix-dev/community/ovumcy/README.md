# Ovumcy

Ovumcy is a menstrual cycle tracker you run yourself. Your data stays on your server: there is no
cloud account, no analytics and no third party in the loop.

Ovumcy's predictions are estimates, never fact. They are not medical advice and not a method of
contraception.

## Storage

- **Data** (`/app/data`) holds the SQLite database.
- **Fence** (`/app/fence`) holds the calendar-feed restore fence. Ovumcy refuses to start unless it is
  a real, separate mount, and it must stay out of your database backups.

## Secret key

`SECRET_KEY` is required. Generate one with `openssl rand -hex 32` and keep it outside the
dataset backup of the database.

## Backups and password reset

Stop the app before taking a backup. For the backup and restore contract and for
`ovumcy reset-password`, see the
[self-hosted guide](https://github.com/ovumcy/ovumcy-web/blob/main/docs/self-hosted.md).
