# KTN Enclosure Manager

[KTN Enclosure Manager](https://github.com/MechanicalCoderX/ktn-enclosure-manager) is a
drive-bay map, chassis telemetry and IDENT LED control panel for SES disk shelves attached
to TrueNAS SCALE. TrueNAS gates its built-in enclosure UI behind iX hardware, so a
third-party shelf reports "Enclosure Unavailable"; this fills that gap without patching
middleware. Telemetry uses read-only device opens, and the only write it can perform is
lighting a drive bay's Identify LED.

<!-- x-readme:warnings:start -->

⚠️ **WARNING:** This app requires a TrueNAS API key, which gives it administrative control over the system.

Misconfiguration or a malicious update can compromise data integrity, security, or system stability. Install at your own risk.

<!-- x-readme:warnings:end -->
