# Legejo

[Legejo](https://github.com/jularboolean/legejo) is a self-hosted EPUB library: a catalog with shelves and search, a reader in the browser, OPDS for reading apps, and sync with Kobo e-readers and KOReader.

The administrator account set in the app's configuration is created on the first start, when the database is empty. Everything Legejo keeps, books included, lives in the data storage.

To have Legejo pick up books from a folder, mount it with additional storage and set `LEGEJO_IMPORT_DIR` to its mount path in the additional environment variables.
