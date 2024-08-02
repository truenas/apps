# Filebrowser

[Filebrowser](https://filebrowser.org) provides a file managing interface within a specified directory and it can be used to upload, delete, preview, rename and edit your files.

You can configure further the settings by using Environment Variables.
See [Filebrowser Documentation](https://filebrowser.org/cli/filebrowser) for more information.
Use the format `FB_OPTION_NAME` where the option name is the name of the option you want to set.

You can also edit the configuration file `/config/filebrowser.json`.

Note that the following options are already set and will always take precedence
over the environment variables and the configuration file:

- `FB_ROOT`/`--root` is set to `/data` (Any additional volume mounted will be under this directory)
- `FB_PORT`/`--port` is set to `30044` (Or the port you configured in the installation wizard)
- `FB_ADDRESS`/`--address` is set to `0.0.0.0` (It will listen on all interfaces **inside** the container)
- `FB_DATABASE`/`--database` is set to `/config/filebrowser.db`
- `FB_CONFIG`/`--config` is set to `/config/filebrowser.json`

Also when a certificate is selected

- `FB_CERT`/`--cert` is set to `/config/certs/tls.crt`
- `FB_KEY`/`--key` is set to `/config/certs/tls.key`
