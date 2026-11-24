# sacdfs

[sacdfs](https://github.com/dsd-toolbox/sacdfs) serves SACD disc images (ISO files) as DSF and WAV
files over SMB and NFS, so music servers and players read them like ordinary albums. The images
stay untouched and are mounted read-only.

SMB is published on port 10445 and NFS on 12049 by default, because TrueNAS's own SMB and NFS
services hold 445 and 2049.

For clients that only use port 445 (Windows drive mapping, Roon, other apps' SMB storage), set
Mount Folder to an empty dataset that TrueNAS shares over SMB: sacdfs's files appear in its folder
sacd. Create the SMB share before the app starts; TrueNAS refuses to save it while the mount is
there.

<!-- x-readme:warnings:start -->

**!!! WARNING !!!**

This application requires additional elevated permissions beyond standard containerization protections. Use at your own risk.

The following additional privileges may be enabled from installing this application:

• Extended System Capabilities

<!-- x-readme:warnings:end -->
