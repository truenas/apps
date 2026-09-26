# Corsfix

[Corsfix](https://corsfix.com) is an open-source CORS proxy. The dashboard manages applications, allowed target domains, API keys, encrypted secrets, and request analytics. This TrueNAS app installs the dashboard, proxy, MongoDB, and Redis.

Put the two published TrueNAS ports behind an HTTPS reverse proxy first: route `https://app.example.com` to the dashboard host port (default `30120`) and `https://proxy.example.com` to the proxy host port (default `30121`). Set **Dashboard URL** and **Proxy URL** to those public addresses. The URLs need distinct origins and must match what your browser uses. You can bind the host ports to a private interface when the reverse proxy runs on the same machine or network.

Before installing, create separate MongoDB and Redis passwords, an authentication secret, and a 32-byte encryption key encoded as Base64 (`openssl rand -base64 32`). Keep these values in your password manager. Both the dashboard and proxy receive the same encryption key. Losing it makes previously stored encrypted secrets unreadable.

After deployment, open the **Dashboard** portal, register the first account, then edit the app and enable **Disable signup**. The **Proxy** portal opens `/up` and should return `Corsfix: OK.`. To use Corsfix, register your application's origin and allowed API targets in the dashboard, then send requests to the proxy URL.

MongoDB and Redis have no published ports. Their data is stored in TrueNAS-managed datasets by default. Back up the MongoDB dataset and all four secret values together. Redis uses append-only persistence. TrueNAS does not provide TLS for the two published ports automatically. The Corsfix dashboard builds proxy request URLs with HTTPS, so the reverse proxy is needed for a working public deployment. Plain HTTP URLs are allowed only for localhost startup testing.

The dashboard image is available for AMD64 hosts. [Self-hosting documentation](https://corsfix.com/docs/open-source/self-hosting) and [source code](https://github.com/corsfix/corsfix) are maintained by Corsfix.
