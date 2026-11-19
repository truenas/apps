# Nextcloud 34

[Nextcloud](https://nextcloud.com/) is a file sharing server that puts the control and security of your own data back into your hands.

This Community package is an independently versioned Nextcloud 34 line. It is
intended for installations that deliberately remain on major version 34 and
must not be confused with the separate nextcloud package that tracks newer
major releases. Installing this app does not migrate an existing nextcloud
application automatically; preserve and reconcile the database, application
configuration, data directory, and secrets before a manual migration.

<!-- x-readme:warnings:start -->

⚠️ **WARNING:** This app has access to the Docker socket, which gives it full control over all containers and effectively root access to the system.

Misconfiguration or a malicious update can compromise data integrity, security, or system stability. Install at your own risk.

<!-- x-readme:warnings:end -->
