# Ghost

Ghost is a powerful app for professional publishers to create, share, and grow a business around their content.

## Features

- Modern publishing platform
- Built-in membership and subscription management
- Email newsletters
- SEO optimized
- Custom themes and integrations
- Content API

## Configuration

### Site URL

The Site URL must include the protocol (http:// or https://) and should match the actual URL where Ghost will be accessible.

Examples:
- `http://192.168.1.100:2368`
- `http://ghost.example.com`
- `https://myblog.com`

**Important**: If you change the URL later, you must update it in the Ghost configuration and restart the app.

### Database

Ghost uses MariaDB for data storage. The database is automatically configured with the credentials you provide during setup.

- Database passwords are required and should be strong
- The database is stored in a separate volume for persistence
- Backups should include both the content and database volumes

### Storage

Ghost requires persistent storage for:

- **Content Storage**: Themes, images, uploaded files, and application data
- **Database Storage**: MariaDB data files

Both storage volumes are essential for Ghost operation and should be backed up regularly.

### Additional Environment Variables

You can configure additional environment variables for advanced Ghost features such as:

- Mail/SMTP configuration
- Custom integrations
- Advanced settings

Refer to [Ghost Configuration Documentation](https://ghost.org/docs/config/) for available options.

## Initial Setup

1. Install the app with your desired configuration
2. Access Ghost via the Web Portal
3. Navigate to `/ghost` to access the admin panel
4. Create your admin account (first user becomes the owner)
5. Complete the initial setup wizard

## Portals

- **Web Portal**: Main Ghost site (/)
- **Admin Portal**: Ghost admin panel (/ghost)

## Notes

- Ghost runs as non-root user (UID 1000)
- MariaDB runs as non-root user (UID 999)
- Initial setup requires web UI access
- URL changes require app restart
- Content uploads are stored in the content volume

## Links

- [Ghost Documentation](https://ghost.org/docs/)
- [Ghost API Documentation](https://ghost.org/docs/api/)
- [Ghost Themes](https://ghost.org/themes/)
- [GitHub Repository](https://github.com/TryGhost/Ghost)