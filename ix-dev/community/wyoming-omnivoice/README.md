# Wyoming OmniVoice

Local OmniVoice text-to-speech over Wyoming for Home Assistant. Supports normal
and streamed text requests, a configured reference voice, and CPU or NVIDIA GPU
inference. GPU mode requires a supported Turing-or-newer NVIDIA GPU and a
CUDA 13.0-compatible driver (R580 or newer).

Example is the initial voice. The app seeds a bundled synthetic WAV/TXT pair into
/data/voices without overwriting existing files. To add a voice, put paired files
such as david_reference.wav and david_reference.txt in that folder, select Custom
voice name, and enter david. Restart after changing the selection or transcript.
TrueNAS cannot dynamically scan the voices folder to populate the installation form.

Settings use fixed labels, dropdown presets, help text and validated custom values.
Cache paths are fixed under /data/cache; choose the backing dataset under Storage.
The app does not expose a generic editable environment-variable-name list.

The first startup downloads model weights to /data/cache. See the
[setup guide](https://github.com/ValentineAlan/wyoming-omnivoice#install) for storage,
GPU and Home Assistant configuration. This app provides a TCP service, not a web UI.
