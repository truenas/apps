# Lens

[Lens](https://github.com/FreeCAD/Ondsel-Server) is a collaborative CAD platform for uploading, viewing, and sharing 3D models with version control, export capabilities, and real-time collaboration tools.

## Features

- Web-based 3D CAD model viewing and collaboration
- Version control for 3D models
- Real-time collaboration tools
- Export capabilities for various formats
- User authentication and access control

## Services

- **Backend API**: Node.js/Feathers backend service providing REST API
- **Frontend**: Vue.js web interface for user interaction
- **MongoDB**: Database for application data and user information
- **Redis**: Cache and task queue for background jobs
- **FC Worker API**: Background task processing API worker
- **FC Worker Celery**: Background task processing Celery worker

## Default Credentials

- **Admin Email**: admin@local.test
- **Admin Username**: admin
- **Admin Password**: admin@local.test

⚠️ **Important**: Change default credentials immediately after installation!

## Configuration

- **Backend Port**: Default 30301 (configurable)
- **Frontend Port**: Default 30300 (configurable)
- **MongoDB**: Not exposed externally by default (optional port exposure available)
- **SMTP**: Optional email server configuration for notifications

## Documentation

For more information, visit the [Lens GitHub repository](https://github.com/FreeCAD/Ondsel-Server).
