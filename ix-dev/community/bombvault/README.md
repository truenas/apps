# BombVault

[BombVault](https://github.com/junkerderprovinz/bombvault) backs up Docker containers and KVM/libvirt VMs with [restic](https://restic.net), and restores them by recreating the container or VM rather than only copying its files back. Incremental, deduplicated and encrypted, with off-site replication, retention, file-level restore and scheduling, all from a web UI.

Two things to know before installing. It needs the Docker socket, which is root-equivalent access, because it stops and recreates containers around backup and restore. And it needs a real host path holding the data you want backed up: TrueNAS does not allow mounting `/mnt` itself, and apps left on the default ixVolume storage keep their data under `/mnt/.ix-apps`, which cannot be mounted either, so those apps' data is out of reach while apps configured with host-path storage are fully covered.

VM backup is optional and talks to libvirt over SSH. On TrueNAS it needs `LIBVIRT_URI` to name the socket at `/run/truenas_libvirt/libvirt-sock`, since the default URI does not work there. See [the VM backup setup guide](https://github.com/junkerderprovinz/bombvault/blob/main/docs/vm-backup-ssh-setup.md).

Support: [GitHub issues](https://github.com/junkerderprovinz/bombvault/issues).
