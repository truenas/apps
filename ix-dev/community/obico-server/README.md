# Obico Server

Self-hosted 3D printer monitoring platform with AI-powered failure detection.

## Features

- **Multi-Printer Support** - Monitor unlimited OctoPrint and Klipper printers
- **AI Failure Detection** - Detect print failures automatically using deep learning
- **Email Alerts** - Get notified of print failures via email
- **Data Privacy** - All data stays local, no cloud dependency
- **Web Dashboard** - Real-time printer status and monitoring
- **REST API** - Integrate with other systems

## Quick Start

1. Install app from TrueNAS Apps
2. Configure database password and Django secret key
3. Access at `http://your-truenas-ip:3334`
4. Login with `root@example.com` / `supersecret` (change immediately!)
5. Connect your OctoPrint/Klipper printers

## Configuration

All settings are configured through TrueNAS UI during installation:
- Database credentials
- Django secret key
- Optional SMTP for email notifications
- Web UI port (default: 3334)

## Resources

- **Website:** https://obico.io
- **Docs:** https://www.obico.io/docs/server-guides/
- **GitHub:** https://github.com/TheSpaghettiDetective/obico-server

## Support

For issues and questions:
1. Check official Obico documentation
2. Review TrueNAS app logs
3. Visit GitHub issues: https://github.com/TheSpaghettiDetective/obico-server/issues
