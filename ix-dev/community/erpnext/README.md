# ERPNext

[ERPNext](https://erpnext.com) is an open-source business management system for accounting, inventory, sales and support.

This package creates one new managed site with MariaDB, Redis, workers and a web
portal. Use dedicated storage for sites/attachments, logs, database and queue data.
Choose the site name and database password once. Changing the initial
Administrator password field later does not reset an existing account.

Images are pinned. The reviewed lifecycle supports fresh installation and only
the exact ERPNext 16.51.0 to 16.51.1 patch transition. Other ERPNext image/version changes
and importing an unmanaged existing site are blocked. Background jobs must be
drained or reviewed before a new upgrade can proceed.

The upgrade preserves a database/files/config backup before migration. Backups
contain private data and credentials: preserve them outside the app's storage
before relying on recovery. Interrupted migrations block startup and require
explicit recovery to separate storage; there is no automatic rollback. The
disposable test recovery helper is not a general restore feature in this app.
