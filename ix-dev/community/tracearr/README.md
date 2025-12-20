# Tracearr

Tracearr is a streaming access manager for Plex and Jellyfin servers that detects account sharing through geolocation analysis, impossible travel detection, and session monitoring.

## Features

- **Session Monitoring**: Track active streams across Plex and Jellyfin servers
- **Geolocation Analysis**: Identify streaming locations using IP-based geolocation
- **Impossible Travel Detection**: Flag suspicious access patterns when users stream from distant locations in short timeframes
- **Multi-Server Support**: Monitor multiple Plex and Jellyfin servers from a single dashboard

## Configuration

The app runs as a supervised container that includes all required services:
- TimescaleDB (PostgreSQL with time-series extensions)
- Redis (caching and session management)
- Tracearr web application

### Security Secrets

The following secrets are auto-generated on first run if not provided:
- **JWT Secret**: Used for signing authentication tokens
- **Cookie Secret**: Used for securing session cookies

### Storage

Three persistent storage volumes are required:
- **PostgreSQL Data**: TimescaleDB database files
- **Redis Data**: Cache persistence
- **App Data**: Application secrets and GeoIP database

## Documentation

For full documentation, visit: https://github.com/connorgallopo/tracearr
