# Time Machine Samba

[Time Machine Samba](https://github.com/mbentley/docker-timemachine) provides a Samba-based Time Machine backup destination for macOS.

Backup data is stored persistently under /opt/timemachine.

The application supports configurable Time Machine credentials, user and group IDs, share name, backup size limit, SMB workgroup, and Samba listening port.

Port 445 may conflict with the TrueNAS host SMB service if that service is enabled.

For upstream documentation, see the [docker-timemachine GitHub repository](https://github.com/mbentley/docker-timemachine).
