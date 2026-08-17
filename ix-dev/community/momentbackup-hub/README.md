# MomentBackup Hub

[MomentBackup Hub](https://momentbackup.com/hub/) is a private overview of
MomentBackup protection. It shows whether each computer is protected, warns when
backups stop, and relays signed hub commands. It stores no backup data.

It starts in heartbeat mode. To scan backup storage too, turn on **Scan backup
storage** and add one or more read-only additional-storage mounts under
`/repos`.

Set **Hub HTTPS address** to the exact origin every computer can resolve before
the first start. The Hub writes that host into its durable certificate, so
changing it later requires enrolling every computer again. Every additional
backup mount is forced read-only by the template.

The container image is proprietary software from Watari Labs Pty Ltd.
Setup guide: <https://momentbackup.com/hub/>.
Support: <https://momentbackup.com/support/>.
