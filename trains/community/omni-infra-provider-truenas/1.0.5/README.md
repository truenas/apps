# Omni TrueNAS Provider

[Omni TrueNAS Provider](https://github.com/bearbinary/omni-infra-provider-truenas) is a Sidero Omni infrastructure provider that provisions and manages Talos Linux VMs on TrueNAS SCALE.

## Prerequisites

- A running [Sidero Omni](https://omni.siderolabs.com/) instance
- An Omni InfraProvider service account key
- TrueNAS SCALE 25.10 (Goldeye) or newer
- A TrueNAS API key for a **dedicated non-root user** in the `builtin_administrators` group, with the password disabled. Do not use the root key. See the upstream [TrueNAS setup guide](https://github.com/bearbinary/omni-infra-provider-truenas/blob/main/docs/truenas-setup.md) for the exact steps. A dedicated user gives you a separate audit trail, independent revocation, and no password attack surface.
