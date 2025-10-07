# Nevu for Plex

Nevu for Plex is an alternative UI for your personal Plex server, providing modern and immersive interfaces for Web, Desktop, Android and AndroidTV.

**Important Note**: Nevu still requires you to have a Plex server that it can connect to - it's just a different interface running on a separate web server.

## Features

- Modern, immersive UI
- Seamless Plex integration
- Play media
- Automatic track matching (Keep the same audio and subtitle language across episodes)
- Browse libraries
- Search for media
- Watch Together (Nevu Sync)
- Get Recommendations
- Fully integrated Watchlist
- Simple and easy to use
- Pro-User features (like special shortcuts etc.)

## Configuration

### Required Settings

- **Plex Server URL**: The URL of your Plex server (e.g., `http://your-plex-server:32400`)

### Optional Settings

- **Disable TLS Verification**: If enabled, the proxy will not check HTTPS SSL certificates
- **Disable Nevu Sync**: If enabled, Nevu sync (watch together) will be disabled
- **Disable Request Logging**: If enabled, the server will not log any requests
- **Disable Global Reviews**: If enabled, Nevu global reviews will be disabled

### Network Configuration

- **Host Network**: Recommended for discovery to work properly
- **WebUI Port**: The port where Nevu will be accessible (default: 30015)
- **Discovery Port**: UDP port 44201 is always published for discovery functionality

## Links

- [GitHub Repository](https://github.com/Ipmake/Nevu)
- [Docker Hub](https://hub.docker.com/r/ipmake/nevu)
- [Android & AndroidTV Apps](https://github.com/Ipmake/Nevu/discussions/43)
