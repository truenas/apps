# Psono

[Psono](https://psono.com/) is a self-hosted, open source password manager for teams.

This app deploys the `psono-combo` image, which bundles three things behind nginx:

| Path      | Component                            |
| --------- | ------------------------------------ |
| `/`       | Web client                           |
| `/server` | REST API (Django + daphne)           |
| `/portal` | Admin portal                         |

Database migrations run automatically on every start.

## Before installing

Psono needs six server keys. Generate them all at once:

```
docker run --rm psono/psono-combo:latest python3 ./psono/generateserverkeys.py
```

Copy the six values into the *Server Keys* section and **back them up**. They
cannot be changed after the first user has registered without losing access to
every stored secret.

You also need to set *Base URL* to the exact URL browsers will use, without a
trailing slash (for example `http://192.168.1.100:30475` or
`https://psono.example.com`). The web client is a static bundle that is built
with this value, so it has to match how users actually connect. If you later
move Psono behind a reverse proxy, update *Base URL* too.

## After installing

Register the first account from the Web UI. The username must end with one of
the domains listed in *Allowed Domains*.

Without SMTP configured, no activation email is sent. Activate the account from
the TrueNAS shell instead:

```
docker exec ix-<app-name>-psono-1 \
  python3 /root/psono/manage.py verifyuseremail <username>
```

To reach the admin portal under `/portal`, promote that account:

```
docker exec ix-<app-name>-psono-1 \
  python3 /root/psono/manage.py promoteuser <username> superuser
```

## Enterprise Edition

Selecting *Psono Enterprise Edition* switches to `psono/psono-combo-enterprise`,
which requires a valid Psono license. LDAP, SAML and OIDC providers are
configured from the admin portal once the matching entry is enabled under
*Authentication Methods*.

## Notes

- The container health check uses `/server/info/` rather than
  `/server/healthcheck/`. The latter performs an outbound NTP request on every
  call and is rate limited to 61 requests per hour, so it is unsuitable as a
  Docker health check.
- Any setting not exposed in the UI can be set through *Additional Environment
  Variables* using the `PSONO_` prefix, for example `PSONO_TIME_SERVER`. See the
  [Psono environment variable reference](https://doc.psono.com/admin/other/environment-variables.html).
