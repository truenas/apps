# LLDAP

LLDAP is a lightweight LDAP directory server with a built-in web interface for managing users, groups, and application credentials.

## Endpoints

- Web UI: `http://<host>:17170`
- LDAP: `ldap://<host>:3890`
- LDAPS (optional): `ldaps://<host>:6360`

## Default Access

- Admin username: `admin`
- Admin password: generated during install (displayed in install dialog)

## Required Configuration

- LDAP domain (e.g. `example.com`)
- Data directory (`/data` is persisted to the host)

## Optional Configuration

- Custom ports / bind addresses
- External PostgreSQL / MySQL database URL
- SMTP settings for email-based password reset
- LDAPS certificate/key paths

## Reference

- Project: https://github.com/lldap/lldap
- Documentation: https://github.com/lldap/lldap/tree/main/docs
- Docker image: https://hub.docker.com/r/lldap/lldap
