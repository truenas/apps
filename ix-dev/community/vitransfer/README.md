# ViTransfer

[ViTransfer](https://www.vitransfer.com) is a professional video review and approval platform for filmmakers.

**Official Website:** https://www.vitransfer.com
**GitHub:** https://github.com/MansiVisuals/ViTransfer
**Docker Hub:** https://hub.docker.com/r/crypt010/vitransfer

## Quick Setup

1. Install ViTransfer from TrueNAS Apps catalog
2. Generate secure secrets using the commands shown in each field description
3. Configure your admin credentials
4. Access the web interface and complete setup

## Required Secrets

Generate all required secrets before installation:

```bash
# Database passwords (hex format - no special characters)
openssl rand -hex 32      # For POSTGRES_PASSWORD
openssl rand -hex 32      # For REDIS_PASSWORD

# Encryption and JWT secrets (base64 format)
openssl rand -base64 32   # For ENCRYPTION_KEY
openssl rand -base64 64   # For JWT_SECRET
openssl rand -base64 64   # For JWT_REFRESH_SECRET
openssl rand -base64 64   # For SHARE_TOKEN_SECRET
```

## Important Notes

- **Admin Name**: Optional display name (defaults to "Admin")
- **Admin Email & Password**: Required for initial setup only
- **Share Token Secret**: Required for v0.6.0+ client authentication
- Change your admin password after first login
- All secrets are required and must be unique

For full documentation, visit https://www.vitransfer.com/docs
