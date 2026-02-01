# Jellyfin AI Upscaler

AI-powered video upscaling service for Jellyfin Media Server.

## Description

This application provides a REST API and web dashboard for AI-based video upscaling.
It uses neural networks (Real-ESRGAN, FSRCNN, ESPCN) to enhance video quality in real-time.

## Features

- **Real-ESRGAN x4** - Best quality upscaling for photos and anime (4x)
- **FSRCNN x2/x3** - Fast real-time upscaling (2x/3x)
- **ESPCN x2/x3** - Ultra-fast lightweight upscaling (2x/3x)
- **NVIDIA GPU Acceleration** - Full TensorRT support for maximum performance
- **Intel GPU Support** - OpenVINO acceleration for Intel Arc/iGPU
- **Web Dashboard** - Monitor status, run benchmarks, test upscaling at localhost:5000

## Requirements

- NVIDIA GPU with CUDA support (recommended)
- 4GB+ VRAM for Real-ESRGAN models
- Jellyfin AI Upscaler Plugin installed in Jellyfin

## Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| Enable GPU Acceleration | Use GPU for AI inference | true |
| Max Concurrent Requests | Parallel processing limit | 4 |
| Default Model | Auto-load model on startup | none |
| Web UI Port | Dashboard and API port | 5000 |

## Links

- [Project Website](https://jellyfin-upscale-ai.base44.app)
- [GitHub Repository](https://github.com/Kuschel-code/JellyfinUpscalerPlugin)
- [Docker Hub](https://hub.docker.com/r/kuscheltier/jellyfin-ai-upscaler)
