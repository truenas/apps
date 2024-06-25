# AdGuard Home

During the setup wizard, AdGuard Home presents an option to select on which port the web interface will be available.
(Defaults to 80. Which is a privileged port and also usually the TrueNAS SCALE UI uses that port)
Because of that, App will force the webUI to listen to port 30000 (or the port selected by user in the TrueNAS SCALE UI).

If you select a different port in the wizard, the Dashboard will not work initially but
after a couple of minutes container will automatically restart and the Dashboard will
be available on the port you selected on the TrueNAS SCALE UI.

> - AdGuard runs as `root` user.
> - AdGuard runs with host networking enabled.
