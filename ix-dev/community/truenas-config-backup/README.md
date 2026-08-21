# TrueNAS Config Backup

[TrueNAS Config Backup](https://github.com/CampAsAChamp/truenas-config-backup) schedules
and manages downloads of your TrueNAS system configuration backup (via the `config.save`
API), with retention pruning, a run-history log, and a simple web dashboard.

## First-time setup

1. **Create an API key** on the TrueNAS system you want to back up
   (**My API Keys** in the TrueNAS UI). Paste it into the **API Key** field during install.
   See the upstream [least-privilege API key guide](https://github.com/CampAsAChamp/truenas-config-backup/blob/main/docs/installation.md#creating-a-least-privilege-api-key).
2. **Set TrueNAS URL** to the target system's base URL. Use `https://127.0.0.1` when the
   app runs on the same box, or the host's LAN IP (e.g. `https://192.168.1.50`) if the
   container cannot reach loopback.
3. **Leave Verify SSL Certificate disabled** for self-signed certificates (typical home-lab
   setups). The connection is still encrypted; only certificate verification is skipped.
4. **Optional:** choose a backup schedule preset (Daily / Weekly / Monthly) or a custom
   cron expression. Leave schedule mode on Manual for on-demand backups only.
5. **Set a Dashboard Password** for the web dashboard login page.
6. Open the **WebUI** portal after install to view, download, or delete backups and see
   run history.

## Important notes

- **HTTPS is required.** TrueNAS revokes API keys used over plain `http://`. If a key was
  revoked, create a new one in **My API Keys** and update the app configuration.
- **Include Secret Seed** should stay enabled if you may restore encrypted passwords from
  this backup onto a new system.
- **Include Pool Keys** and **Include Root Authorized Keys** are off by default; enable
  them only when you need those secrets preserved for hardware migration.
- **Restoring:** see the upstream [restore guide](https://github.com/CampAsAChamp/truenas-config-backup/blob/main/docs/restore.md) or the dashboard **How to restore** link.
- **Retention Count** controls how many past backup files are kept; older files are pruned
  automatically after each successful run.

For full documentation, see the [upstream repository](https://github.com/CampAsAChamp/truenas-config-backup).
