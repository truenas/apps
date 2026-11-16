# TAK Server

[TAK Server](https://tak.gov/) is the server component of the Tactical Assault Kit ecosystem, supporting ATAK, iTAK and WinTAK clients.

This app uses the official TAK Product Center hardened container images. On first start it creates a private certificate authority, server certificate, admin client certificate and user client certificates. Certificates are stored in the certs storage volume and can be retrieved with docker cp from the running ix-takserver-1 container.

**Required ports:** 8089 for CoT streaming (mTLS), 8443 for the WebTAK admin console and API (mTLS), and 8446 for the certificate enrollment API. PostgreSQL port 5432 is never published.

**Important notes:** The first start can take several minutes while the CA, database schema and JVMs initialize. The certs dataset contains the CA private key and all private keys, so keep it private and back it up. TAK Server is subject to the TAK Product Center terms of use; deploying this app confirms you have the right to use the upstream images.
