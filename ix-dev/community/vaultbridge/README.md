# VaultBridge

[VaultBridge](https://github.com/mrtrollex/VaultBridge) is a self-hosted REST and semantic search
bridge for Obsidian Markdown vaults. It is licensed under the MIT License. Project documentation is
available in the [repository README](https://github.com/mrtrollex/VaultBridge#readme) and the
[TrueNAS deployment guide](https://github.com/mrtrollex/VaultBridge/blob/main/README_TRUENAS.md).

This package definition deploys the normal published VaultBridge image as a TrueNAS Community App.
It does not fork VaultBridge runtime behavior. Catalog availability is claimed only after upstream
review, merge, and delivery through TrueNAS.

## Production image contract

The package consumes the published VaultBridge `1.1.0` image through the current upstream
repository-plus-tag convention:

```text
ghcr.io/mrtrollex/vaultbridge:1.1.0
```

The verified release evidence records OCI index
`sha256:753e613617d221c3dac311600a36cab3f2727b09f630321664eaa7b7ad6eb48c`; the current TrueNAS image
values schema has no dedicated digest field, so the digest remains a validation/evidence invariant.
Fixtures inherit the production image map from `ix_values.yaml` and retain only synthetic API keys
and disposable paths.

`app_version` is `1.1.0`. Catalog package `version` is the required initial `1.0.0`. Library `2.3.11`,
its generated hash, `item.yaml`, and the generated library copy are included. The current source icon
is attached or linked for review; a TrueNAS reviewer supplies the final CDN URL during the upstream
review process. No CDN URL is fabricated here.

## Storage and permissions

The selected Obsidian vault is mounted read/write at `/vault` by default and remains authoritative.
VaultBridge does not create, copy, recursively change, or automatically repair ownership or ACLs on
that path. The selected non-root UID/GID must already have traverse and read/write access, unless the
operator deliberately enables and configures the TrueNAS ACL form. A read-only mount is supported
for retrieval-only use; note create and append operations then fail normally.

Persistent derived semantic data and model caches are mounted at `/data`. The default is a
TrueNAS-managed ixVolume; an existing host path is also supported. The standard permissions helper
may prepare app-owned `/data`, but it is never applied to `/vault`.

If the application cannot access `/vault`, grant the configured UID/GID the minimum necessary access
using the dataset's existing POSIX or ACL model, then restart the application. Do not use broad
world-writable permissions or recursively replace an existing vault ACL.

The Web Portal opens `/ui/` on the configured Web Port. It never includes an API key. API keys are
masked in the install form, but this is UI masking rather than an encrypted secret-store guarantee;
a privileged TrueNAS or Docker administrator can inspect deployed container configuration.
