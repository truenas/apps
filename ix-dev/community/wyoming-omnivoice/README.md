# Wyoming OmniVoice

Local OmniVoice text-to-speech over Wyoming for Home Assistant. Supports normal
and streamed text requests, a configured reference voice, and CPU or NVIDIA GPU
inference. The CUDA 12.6 image retains support for Pascal GPUs such as Tesla P40.

The first startup downloads model weights to /data/cache. See the
[setup guide](https://github.com/ValentineAlan/wyoming-omnivoice#truenas) for storage,
GPU and Home Assistant configuration. This app provides a TCP service, not a web UI.
