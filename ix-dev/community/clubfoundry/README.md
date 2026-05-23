# ClubFoundry — iSCSI LUN manager for shared-PC infrastructures

**ClubFoundry** is a Web UI for managing per-PC iSCSI LUNs on TrueNAS SCALE.
Designed for shared-use computers in gaming clubs, computer labs, schools,
universities, internet cafes, QA test farms, and corporate training centers.

## What it does

- **One-LUN-per-PC matrix.** Rows = workstations, columns = OS images. Create
  a fresh LUN from a golden image with one click; the clone is sparse so 50
  workstations share storage for 1× the source size.
- **Built-in lifecycle.** Switch a PC to a different OS image. Roll back to
  yesterday's snapshot. Wipe-and-restore for "boot from clean image" workflows.
- **Production-ready guardrails.** Multiple safety layers prevent the operator
  from accidentally destroying the golden image source ZVOL or pool, with
  enforced cleanup of legacy datasets + atomic LUN ID assignment that's
  multi-initiator-safe.
- **Recovery procedures.** Live console + step-by-step playbooks for the
  common failure modes (SCST stale extents, target ID drift, snapshot
  cascade conflicts).

## How updates work in TrueNAS Apps

This catalog build of ClubFoundry runs with `CLM_UPDATE_MODE=truenas_apps`,
which **disables the in-container auto-updater**. New versions are delivered
through the standard TrueNAS Apps update flow:

1. iX moderators merge our promotion PR upstream when we cut a new stable.
2. TrueNAS shows "Update Available" on the ClubFoundry tile in the Apps UI.
3. You click **Update**; TrueNAS runs `docker compose pull && up -d`.

You can roll back from the same Apps UI if a release misbehaves.

For users running ClubFoundry outside the TrueNAS Apps catalog (the
`install.sh` standalone path), the in-container sidecar updater stays
active and follows our normal alpha → beta → stable channel flow.

## Documentation

- Homepage: https://clubfoundry.net
- Standalone install: `curl -fsSL https://clubfoundry.net/install.sh | bash`
