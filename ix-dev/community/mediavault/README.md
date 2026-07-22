# MediaVault

MediaVault is a self-hosted movie and series server with a built-in web interface and clients for Android phones, tablets, Android TV, Google TV, and NVIDIA Shield.

Official binaries are free for personal, non-commercial use without a purchase or subscription. See the public [MediaVault Free Personal Use Terms](https://github.com/ScorpionZK89/MediaVault-Releases/blob/main/PERSONAL-USE-TERMS.md) and [environment-variable reference](https://github.com/ScorpionZK89/MediaVault-Releases/blob/main/ENVIRONMENT.md).

The image includes the .NET runtime, SQLite provider, FFmpeg, and ffprobe. Media mounts are read-only; configuration, data, cache, transcodes, downloads, and backups use separate writable storage locations.

For a new installation, TrueNAS automatically creates separate managed ixVolume datasets for configuration, data, cache, transcodes, downloads, backups, and media. No datasets need to be prepared manually.

For an existing Custom App installation, select the same host paths during the one-time catalog migration. Never point the media storage field at writable app-data paths.
