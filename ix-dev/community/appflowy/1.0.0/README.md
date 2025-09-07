# AppFlowy

AppFlowy is an open-source alternative to Notion. You are in charge of your data and customizations.

AppFlowy is a privacy-first, flexible, and extensible workspace for you to achieve more.

## Features

- **Open Source & Privacy First**: Your data belongs to you. AppFlowy ensures your data privacy by keeping everything local.
- **Block-based Editor**: Create rich content with blocks that can be easily rearranged and styled.
- **Collaborative Workspace**: Work together with your team in real-time.
- **AI-powered**: Enhanced with AI capabilities for smart content creation and assistance.
- **Cross-platform**: Available on desktop and web.
- **Self-hosted**: Full control over your data with self-hosted deployment.

## Configuration

### Initial Setup

1. **Web Host**: Configure the base URL where AppFlowy will be accessible (e.g., `appflowy.example.com`)
2. **Admin Credentials**: Set up the initial admin email and password
3. **JWT Secret**: Configure a secure JWT secret for authentication
4. **Database Password**: Set a secure password for PostgreSQL

### Authentication

- **Admin Email**: Initial administrator email address
- **Admin Password**: Initial administrator password
- **JWT Secret**: Secret key for JWT token signing (must be at least 32 characters)
- **JWT Expiration**: Token expiration time in seconds (default: 3600)
- **Disable Signup**: Optionally prevent public user registration

### Email Configuration (Optional)

Configure SMTP settings to enable email notifications:
- **SMTP Host**: Your SMTP server hostname
- **SMTP Port**: SMTP server port (default: 587)
- **SMTP Username**: Authentication username
- **SMTP Password**: Authentication password
- **From Email**: Email address to send from

### AI Features (Optional)

- **Enable AI**: Toggle AI-powered features
- **OpenAI API Key**: Required for AI functionality

### Storage

AppFlowy uses:
- **PostgreSQL**: For application data storage
- **MinIO**: For S3-compatible file storage (documents, images, etc.)

### Network

- **Web Port**: Default port is 30800
- **HTTPS**: Optional SSL certificate can be configured

## Default Credentials

After installation, you can access AppFlowy using the admin credentials you configured during setup.

## Ports

- **80/443**: Web interface (via nginx reverse proxy)

## Accessing AppFlowy

After deployment, AppFlowy will be available at:
- Web interface: `http://your-truenas-ip:configured-port` or `https://your-domain` if HTTPS is configured
- Admin console: `http://your-truenas-ip:configured-port/console`
- MinIO console: `http://your-truenas-ip:configured-port/minio` (for file storage management)

## Architecture

This AppFlowy deployment includes:
- **nginx**: Reverse proxy and web server
- **appflowy_cloud**: Main application backend
- **gotrue**: Authentication service
- **postgres**: Database server
- **redis**: Caching and session storage
- **minio**: S3-compatible object storage
- **admin_frontend**: Administrative interface
- **appflowy_worker**: Background job processor
- **appflowy_web**: Web frontend
- **appflowy_ai**: AI services (optional)

## Security Considerations

1. **Change Default Passwords**: Always change default passwords before exposing to the internet
2. **Use HTTPS**: Configure SSL certificates for production use
3. **Firewall**: Only expose necessary ports
4. **JWT Secret**: Use a strong, randomly generated JWT secret
5. **Database Security**: Use a strong PostgreSQL password

## Backup

Important data to backup:
- PostgreSQL database (application data)
- MinIO storage (user files and documents)

## Support

For support and documentation:
- [AppFlowy GitHub](https://github.com/AppFlowy-IO/AppFlowy)
- [AppFlowy Documentation](https://docs.appflowy.io/)
- [AppFlowy Community](https://discord.gg/9Q2xaN37tV)

## License

AppFlowy is released under the AGPL-3.0 license.
