HFS is an HTTP file server with uploads, downloads, user accounts, permissions, a virtual file system and plugins.

Choose a shared folder and an admin password during installation. Open the Admin portal and sign in as `admin`. Configuration is stored separately from shared files. The password initializes the admin account only when no configuration file exists. Change it inside HFS afterwards; restarts and app updates preserve the current password. Editing the installation password in TrueNAS does not reset an existing account.

HFS runs as user/group 568 by default. The shared folder must grant this user the required read/write access; use the storage ACL options under Advanced settings if needed. HFS upload permissions are configured separately in its Admin interface.
