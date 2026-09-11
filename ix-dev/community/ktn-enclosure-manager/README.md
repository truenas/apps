# KTN Enclosure Manager

[KTN Enclosure Manager](https://github.com/MechanicalCoderX/ktn-enclosure-manager) is a
drive-bay map, chassis telemetry and IDENT LED control panel for SES disk shelves attached
to TrueNAS SCALE. TrueNAS gates its built-in enclosure UI behind iX hardware, so a
third-party shelf reports "Enclosure Unavailable"; this fills that gap without patching
middleware. Telemetry uses read-only device opens, and the only write it can perform is
lighting a drive bay's Identify LED.
