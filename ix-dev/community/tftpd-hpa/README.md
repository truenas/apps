# TFTP

[TFTP](https://manpages.debian.org/testing/tftpd-hpa/tftpd.8.en.html) is a server for the Trivial File Transfer Protocol.

The app runs as **root** user and drops privileges to **tftp** (9069) user for the TFTP service.

<!-- x-readme:warnings:start -->

**!!! WARNING !!!**

This application requires additional elevated permissions beyond standard containerization protections. Use at your own risk.

The following additional privileges may be enabled from installing this application:

• Host Networking

<!-- x-readme:warnings:end -->
