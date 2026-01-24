# Deltabadger

[Deltabadger](https://github.com/deltabadger/deltabadger) is a self-hosted crypto DCA (Dollar Cost Averaging) bot.

## Features

- **Web UI**: Full-featured web interface for configuration and monitoring
- **Self-Hosted**: Keep your API keys and data private on your own server
- **Multi-Exchange Support**: Connect to various crypto exchanges via API
- **Automated DCA**: Set up dollar-cost averaging strategies for crypto purchases
- **Secure**: Auto-generates encryption secrets, stores data in SQLite database

## Post-Installation Setup

> **IMPORTANT**: After installation, you must configure your exchange API keys through the web interface.

1. Access the Web UI at the configured port (default: 30737)
2. Complete the initial setup wizard
3. Configure your exchange API credentials
4. Set up your DCA strategies

> **WARNING**: Keep your exchange API keys secure. Use read-only or trading-only API keys with appropriate permissions.

## Storage

The app stores all data in `/app/storage` including:
- SQLite databases (accounts, orders, configurations)
- Auto-generated encryption secrets
- Application logs

Data persists across container restarts and updates.
