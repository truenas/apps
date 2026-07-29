# YunKan

[YunKan](https://yun-kan.com/) is a self-hosted NVR for RTSP and ONVIF IP cameras with
on-device AI detection (motion, person, vehicle, face, license plate, pose/fall, package,
baby cry). Video stays on the local network; no vendor cloud is involved.

Everything runs in a single container: media server, recorder, detection workers, web
admin and reverse proxy.

## Inference backend

Pick the image that matches your hardware under [Inference Backend]:

| Option | Hardware |
| --- | --- |
| CPU | Any x86_64 host, no accelerator needed |
| OpenVINO | Intel iGPU / Arc - also enables VAAPI hardware decoding (enable the GPU under Resources) |
| CUDA | NVIDIA GPU with 6 GB VRAM or more |
| TensorRT | NVIDIA GPU with 6 GB VRAM or more, builds an engine on first start |

## Notes

- Runs on the host network by default: 23406 (web interface) and 23515 TCP/UDP (WebRTC
  media) are the ports clients use; 23880 (RTSP) and 24214 (streaming) are internal and
  gated by a signed token. A bridge network works too - it publishes only the web and
  WebRTC ports, and the WebRTC port has to keep the same number on both sides.
- A free tier is available; paid tiers unlock additional features and are activated in
  the web interface.
- `/etc/machine-id` and `/sys/class/dmi/id/product_uuid` are mounted read-only to derive
  a stable hardware fingerprint for offline license binding.
- Update the app from the TrueNAS Apps page; the Docker socket is not mounted, so the
  in-app self-upgrade path is disabled.
