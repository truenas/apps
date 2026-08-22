# ActuallyFreeCD Server

ActuallyFreeCD Server is a free, server-based audio CD ripping application with a web browser interface, designed for TrueNAS and other Docker hosts.

CDs are read, ripped, verified and encoded directly on the server. The browser provides the interface for controlling and monitoring the process, so the client device does not need to remain connected while a rip is in progress.

## Features

- FLAC and MP3 output
- Fast, Automatic and Secure ripping modes
- AccurateRip verification
- Automatic AccurateRip drive-offset lookup
- MusicBrainz metadata lookup
- CD-Text metadata support
- Manual metadata editing
- Album artwork support
- Configurable artist, album and track naming
- Persistent rip logs
- Browser reconnection to an active server-side rip
- Rip cancellation
- Manual eject and eject-after-successful-rip
- Continues to support CD ripping when Internet metadata or AccurateRip services are unavailable

## Optical Drive Requirements

ActuallyFreeCD requires direct access to both Linux device nodes associated with the optical drive:

- The optical block device, normally `/dev/sr0`
- The matching SCSI generic device, for example `/dev/sg8`

The exact device numbers vary between TrueNAS systems.

From the TrueNAS shell, the matching devices can normally be identified with:

    lsscsi -g

Locate the optical drive in the output. The same line should show both its `/dev/srX` and `/dev/sgX` device names.

For example:

    /dev/sr0    /dev/sg8

Enter these two paths in the ActuallyFreeCD application configuration.

If multiple optical drives are installed, select the matching pair for the drive that should be made available to ActuallyFreeCD.

## Storage

The selected music storage is mounted inside the ActuallyFreeCD container as:

    /music

Using a TrueNAS Host Path is recommended when the ripped music should also be available to SMB, Plex or other applications.

ActuallyFreeCD can create artist, album, disc and track folders beneath this location according to the selected naming preset.

## File Permissions

ActuallyFreeCD can assign a group ID (GID) to newly created music files and directories.

For installations where the music library is shared with SMB, Plex or other TrueNAS applications, using a common media group is recommended.

File and directory permissions can also be configured during installation.

## Internet Access

Internet access is used for online services including MusicBrainz metadata lookup, album artwork and AccurateRip verification.

An Internet connection is not required to rip an audio CD.

If MusicBrainz, AccurateRip or another online service is unavailable, ActuallyFreeCD will continue to allow the CD to be ripped without that service.

## Using ActuallyFreeCD

Once installed, open the ActuallyFreeCD web browser interface using the Web UI link provided by TrueNAS.

Insert an audio CD into the configured optical drive. ActuallyFreeCD will detect the disc and read its table of contents.

Metadata can then be obtained from MusicBrainz or CD-Text, or entered manually.

Select the required tracks, output format, ripping mode and destination, then start the rip.

The ripping process runs on the server. Closing the browser, allowing a mobile device to sleep, or reconnecting from another device does not stop an active rip. Reopening the interface reconnects to the current server-side ripping session.

## Project

ActuallyFreeCD is intended to provide a genuinely free CD ripping solution without subscriptions, feature paywalls or paid upgrades.

Source code, bug reports and development information:

https://github.com/D69wookie/ActuallyFreeCD-Server
