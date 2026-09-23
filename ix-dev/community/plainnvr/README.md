# PlainNVR

[PlainNVR](https://github.com/endless1233214/plainnvr) is a lightweight self-hosted network video recorder for RTSP cameras.

PlainNVR records camera streams to local storage, provides go2rtc-backed live viewing, and includes optional Home Assistant bridge endpoints for snapshots and playback.

Version 0.1.3 keeps the go2rtc RTSP relay on localhost by default. Native and
browser clients use the WebUI port for authenticated signaling and the WebRTC
port for media. Publish the WebRTC port for both TCP and UDP, and configure a
reachable TrueNAS address and that published port in WebRTC Candidates when
Docker advertises only an internal container address.

Publishing the RTSP port does not enable external RTSP access by itself. Only
for trusted-network integrations, add `NVR_GO2RTC_RTSP_HOST=0.0.0.0` under
Additional Environment Variables. That RTSP relay is unauthenticated and must
be restricted by your network firewall. Keep the go2rtc API on localhost.
