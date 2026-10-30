# Scryer

[Scryer](https://www.scryer.media/scryer/) manages movies, series, and anime. This app runs its [first-party container](https://github.com/scryer-media/scryer/pkgs/container/scryer); see the [upstream documentation](https://www.scryer.media/scryer/docs/installation/docker/) for application setup.

**Before installing,** create a protected plain-text file that contains a strong, unique bootstrap administrator password. Enter the absolute host path of that file, not the password itself, as the Bootstrap Password File. The selected user and group (568 by default) must be able to read the file and traverse its parent directories, and the file must not be world-readable. A file owned by root with group 568 and mode 0640 works on a dataset with POSIX permissions; on an ACL dataset, check the effective ACLs. Keep the file outside your media dataset and leave it in place, because Scryer reads it on every start. A missing, empty, or unreadable file stops Scryer from starting.

**First sign-in:** log in as the configured administrator with the password from the file, then change the temporary password. Leaving the file configured never resets an existing password, but Scryer refuses to start if the configured administrator account is later disabled or loses full administrator rights.

**Storage:** back up the whole configuration storage, because it holds the database and the encryption key. Prefer a host path dataset for a permanent installation. Mount one dataset for downloads and media at /data and use the same /data mapping in your download client; hard links only work inside a single dataset. The app never changes the ownership of your media.

**Network:** use a trusted network or an HTTPS reverse proxy. Public URL declares the address your browser uses; it does not enable TLS.

**Updates and removal:** update through TrueNAS and take a backup first. Restore a backup only onto the Scryer version that created it. Rolling back the app in TrueNAS does not roll back host path data, so restore your backup instead. Host path data is kept when the app is removed, but **Remove iXVolumes** deletes configuration stored in an ixVolume.
