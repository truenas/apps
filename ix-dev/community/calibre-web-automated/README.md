# Calibre-Web Automated

[Calibre-Web Automated](https://github.com/crocodilestick/Calibre-Web-Automated) is a web application for managing Calibre eBook libraries with automated book ingestion, conversion, metadata, and reader-sync features.

## First-time setup

1. Open the **WebUI** portal after the app starts.
2. Sign in with the default credentials:

   - Username: `admin`
   - Password: `admin123`

3. Change the default password immediately.
4. Configure CWA behavior from its settings pages.

## Storage

- **Configuration Storage** holds CWA settings, databases, and processed-book backups.
- **Calibre Library Storage** holds the managed Calibre library. Choose **Host Path** when using an existing library dataset.
- **Book Ingest Storage** is for completed eBook files awaiting import. CWA removes files from this directory after processing.

Do not download files directly into the ingest directory. Download them completely elsewhere, then move them into the ingest directory.

To use Calibre plugins, add an **Additional Storage** entry mounted at:

```text
/config/.config/calibre/plugins
