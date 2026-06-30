# Changelog

## [1.0.0] - 2026-06-29

### Added
- Initial release of LTO-6 Tape Manager for TrueNAS community catalog
- Orchestrated LTFS mount/eject via host DBus socket (no `pid: host`)
- Auto-mount on tape insertion (SCSI medium detection via sg_turs)
- Auto-eject on physical button press (SCSI Unit Attention ASC=5a/01)
- Mandatory pre-tape buffer with configurable gate (80%) and kill (88%) thresholds
- Prometheus exporter on port 9125 (buffer usage, mount state, drive temp)
- Orchestrator REST API on port 9877 (mount, unmount, eject, deep-recovery)
- Optional Telegram notifications (token stored as private secret)
- Support for dual drives: lto6 (sg4/nst1) and lto6b (sg2/nst0)
