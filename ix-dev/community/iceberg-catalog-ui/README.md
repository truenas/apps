# Iceberg Catalog UI (for AIStor)

[Iceberg Catalog UI](https://github.com/arturborycki/aistore-ui) is a multi-user web UI for the
Apache Iceberg catalog of MinIO AIStor Tables. Browse and manage warehouses, namespaces, tables,
views, snapshots and column statistics, and describe data with Apache Ossie semantic models.

Users sign in with their AIStor access keys. Each user works with their own temporary
credentials and AIStor policies; the app holds no shared credentials.

This is a community project, not a MinIO product.

## Setup

- **Public URL**: the address people open, with the port, e.g. `https://truenas.local:30553`.
  Sign-in is only accepted from it and from the additional origins.
- **AIStor Endpoint**: the AIStor S3 API (not the console), e.g. `http://192.0.2.20:9000`.
- **Certificate**: select a TrueNAS certificate, or leave it empty and the app creates a
  self-signed certificate and keeps it in its storage.
- **Semantic models** need a bucket on AIStor with versioning enabled.
