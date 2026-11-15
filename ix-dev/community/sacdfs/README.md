# sacdfs

[sacdfs](https://github.com/aclater/sacdfs) serves SACD disc images (ISO files) as DSF and WAV
files over SMB and NFS, so music servers and players read them like ordinary albums. The images
stay untouched and are mounted read-only.

SMB is published on port 10445 and NFS on 12049 by default, because TrueNAS's own SMB and NFS
services hold 445 and 2049.
