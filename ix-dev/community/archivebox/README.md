# ArchiveBox

[ArchiveBox](https://archivebox.io) saves websites as HTML, PDF, screenshots, WARC, and more for offline browsing.

Open the Web UI after installation to complete the setup wizard and create the first administrator. The ArchiveBox URL and replay mode can optionally be set during installation. Full JavaScript replay requires wildcard DNS and a reverse proxy for the configured domain and its subdomains.

The single ArchiveBox container includes the web server, background workers, scheduled crawls, and search. The data volume stores the database, configuration, archived content, and browser profiles. Keep this volume on local storage; additional storage can be mounted at `/data/archive` for archived content.

Use Additional Environment Variables for advanced [configuration](https://github.com/ArchiveBox/ArchiveBox/wiki/Configuration), including archive visibility and Archive.org submissions.
